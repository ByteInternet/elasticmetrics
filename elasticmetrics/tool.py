import sys
import os
from logging import getLogger, DEBUG, INFO, ERROR, Formatter, StreamHandler, NullHandler
from argparse import ArgumentParser
from elasticmetrics import __version__
from elasticmetrics.collectors import ElasticSearchCollector


EX_OK = getattr(os, 'EX_OK', 0)
EX_SOFTWARE = getattr(os, 'EX_SOFTWARE', 70)
EX_TEMPFAIL = getattr(os, 'EX_TEMPFAIL', 75)

logger = getLogger(__name__)


def parse_args(args=None):
    parser = ArgumentParser(
                description='collect and report metrics from Elastic stack'
            )
    parser.add_argument('--host', default='localhost', help='ElasticSearch server hostname')
    parser.add_argument('--port', default=9200, type=int, help='ElasticSearch server port')
    parser.add_argument('--user', '-u', default=os.environ.get('ELASTICSEARCH_USER'),
                        help='ElasticSearch username')
    parser.add_argument('--password', '-p', default=os.environ.get('ELASTICSEARCH_PASSWORD'),
                        help='ElasticSearch password')
    parser.add_argument('--ssl', action='store_true',
                        help='use SSL (when applicable)')
    parser.add_argument('--insecure', action='store_true',
                        help='perform insecure SSL connections, skip certificate verification')
    parser.add_argument('--verbose', action='store_true', help='more output'),
    parser.add_argument('--quiet', action='store_true', help='less output (overrides verbose)'),
    parser.add_argument('--version', action='version', version=__version__)
    return parser.parse_args(args)


def _ensure_logging_handler(logger):
    if not logger.handlers:
        logger.addHandler(NullHandler())


def config_loggers(quiet=False, verbose=False):
    logger.setLevel(ERROR if quiet else DEBUG)
    stdout_handler = StreamHandler(sys.stdout)
    stdout_handler.setFormatter(Formatter('%(levelname)s: %(message)s'))
    stdout_handler.setLevel(DEBUG if verbose else INFO)
    logger.addHandler(stdout_handler)
    # silent warnings like "No handlers could be found for logger ..."
    _ensure_logging_handler(getLogger('elasticmetrics.collectors'))
    _ensure_logging_handler(getLogger('elasticmetrics.common'))


def create_es_collector(opts):
    """Create an ElasticSearchCollector configured by options provided by
    parsing arguments
    """
    ssl_context = {}
    if opts.insecure:
        ssl_context['no_cert_verify'] = True
        logger.warning('disabled SSL certificate verification. requests are insecure')

    return ElasticSearchCollector(
            opts.host, port=opts.port,
            user=opts.user, password=opts.password,
            scheme='https' if opts.ssl else 'http',
            ssl_context=ssl_context
            )


def main(args=None):
    try:
        opts = parse_args(args)
        config_loggers(opts.quiet, opts.verbose)
        es_collector = create_es_collector(opts)
        logger.debug('collecting cluster health info')
        print(es_collector.cluster_health())
        return EX_OK
    except KeyboardInterrupt:
        return EX_TEMPFAIL
    except Exception as err:
        logger.error(err)
        return EX_SOFTWARE


sys.exit(main())
