import sys
import os
import json
from logging import getLogger, DEBUG, INFO, ERROR, Formatter, StreamHandler, NullHandler
from argparse import ArgumentParser
from elasticmetrics import __version__
from elasticmetrics.collectors import ElasticSearchCollector
from elasticmetrics.metrics import cluster_health_metrics, node_performance_metrics
from elasticmetrics.formatters import sort_flatten_metrics_iter

EX_OK = getattr(os, 'EX_OK', 0)
EX_DATAERR = getattr(os, 'EX_DATAERR', 65)
EX_SOFTWARE = getattr(os, 'EX_SOFTWARE', 70)
EX_TEMPFAIL = getattr(os, 'EX_TEMPFAIL', 75)

PROG_NAME = 'elasticmetrics.tool'
COLLECT_TARGETS = ['cluster_health', 'node_stats']

logger = getLogger(PROG_NAME)


def parse_args(args=None):
    parser = ArgumentParser(
        prog=PROG_NAME,
        description='collect and report metrics from Elastic stack')
    parser.add_argument(
        '--host', default='localhost', help='ElasticSearch server hostname')
    parser.add_argument(
        '--port', default=9200, type=int, help='ElasticSearch server port')
    parser.add_argument(
        '--user',
        '-u',
        default=os.environ.get('ELASTICSEARCH_USER'),
        help='ElasticSearch username')
    parser.add_argument(
        '--password',
        '-p',
        default=os.environ.get('ELASTICSEARCH_PASSWORD'),
        help='ElasticSearch password')
    parser.add_argument(
        '--ssl', action='store_true', help='use SSL (when applicable)')
    parser.add_argument(
        '--insecure',
        action='store_true',
        help='perform insecure SSL connections, skip certificate verification')
    parser.add_argument('--verbose', action='store_true', help='more output'),
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='less output (overrides verbose)'),
    parser.add_argument(
        '--collect',
        default='cluster_health,node_stats',
        help='comma separated list of targets '
        'to collect: {}. Default is cluster_health,node_stats'.format(
            ','.join(COLLECT_TARGETS))),
    parser.add_argument('--version', action='version', version=__version__)
    formatter_group = parser.add_mutually_exclusive_group()
    formatter_group.add_argument(
        '--raw-stats',
        action='store_true',
        help='output raw stats as returned from Elastic APIs'),
    formatter_group.add_argument(
        '--dotted-paths',
        action='store_true',
        help='output metrics named as dotted paths mapped to values'),
    parser.add_argument(
        '--node-alias',
        help='alias for the node. Used as prefix for metrics paths')
    return parser.parse_args(args)


def _ensure_logging_handler(logger, handler=None):
    if logger.handlers:
        return
    logger.addHandler(handler or NullHandler())


def config_loggers(quiet=False, verbose=False):
    log_level = ERROR if quiet else DEBUG
    logger.setLevel(log_level)
    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(
        Formatter('[%(levelname)s] %(name)s: %(message)s'))
    stream_handler.setLevel(DEBUG if verbose else INFO)
    logger.addHandler(stream_handler)

    # silent warnings like "No handlers could be found for logger ..." for loggers
    # from other modules
    sublogger_handler = stream_handler if verbose else None
    subloggers = [
        getLogger('elasticmetrics.collectors'),
        getLogger('elasticmetrics.http')
    ]
    for sublogger in subloggers:
        sublogger.setLevel(log_level)
        _ensure_logging_handler(sublogger, sublogger_handler)


def create_es_collector(opts):
    """Create an ElasticSearchCollector configured by options provided by
    parsing arguments
    """
    ssl_context = {}
    if opts.insecure:
        ssl_context['no_cert_verify'] = True
        logger.warning(
            'disabled SSL certificate verification. requests are insecure')

    return ElasticSearchCollector(
        opts.host,
        port=opts.port,
        user=opts.user,
        password=opts.password,
        scheme='https' if opts.ssl else 'http',
        ssl_context=ssl_context)


def main(args=None):
    try:
        opts = parse_args(args)
        config_loggers(opts.quiet, opts.verbose)
        targets = set(
            [word.strip().lower() for word in opts.collect.split(',')])
        for target in targets:
            if target not in COLLECT_TARGETS:
                logger.error("invalid argument to collect: {}".format(target))
                return EX_DATAERR

        output = {}

        collector = create_es_collector(opts)
        logger.debug('collecting ElasticSearch metrics')
        path_prefix = opts.node_alias or ''
        if 'cluster_health' in targets:
            output['cluster_health'] = collector.cluster_health(
            ) if opts.raw_stats else cluster_health_metrics(
                collector.cluster_health())
        if 'node_stats' in targets:
            output['node_stats'] = collector.node_stats(
            ) if opts.raw_stats else node_performance_metrics(
                collector.node_stats())

        if opts.dotted_paths:
            cluster_output = sort_flatten_metrics_iter(
                [output.get('cluster_health', {})
                 ],  # open to add other cluster related metrics
                prefix='cluster')
            node_output = sort_flatten_metrics_iter(
                [output.get('node_stats', {})
                 ],  # open to add other node related metrics
                prefix=path_prefix)
            output = cluster_output
            output.update(node_output)
            for metric_path, value in output.items():
                print('{} {}'.format(metric_path, value))
        else:
            print(json.dumps(output, indent=4))

        return EX_OK
    except KeyboardInterrupt:
        return EX_TEMPFAIL
    except Exception as err:
        logger.error(err)
        return EX_SOFTWARE


sys.exit(main())
