from logging import getLogger
from .http import HttpClient


PATH_CLUSTER_HEALTH = '_cluster/health'
PATH_CLUSTER_STATS = '_cluster/stats'
PATH_CLUSTER_PENDING_TASKS = '_cluster/pending_tasks'
PATH_NODE_STATS = '_nodes/_local/stats'


logger = getLogger(__name__)


class ElasticSearchCollector(HttpClient):
    """Collect ElasticSearch metrics

    :param str host: ES server hostname/address
    :param int port: ES server port number
    :param str user: HTTP basic auth user
    :param str password: HTTP basic auth password
    :param str scheme: URL scheme, http/https
    :param dict headers: dictionary of additional headers
    """

    default_port_http = 9200
    default_port_https = 9200

    def cluster_health(self):
        """Collect cluster health status

        :rtype: dict
        """
        logger.debug('getting cluster health info')
        return self._get_json(PATH_CLUSTER_HEALTH)

    def cluster_stats(self):
        """Collect statistics from a cluster point of view, includes
        basic index metrics and node information.

        :rtype: dict
        """
        logger.debug('getting cluster statistics')
        return self._get_json(PATH_CLUSTER_STATS)

    def cluster_pending_tasks(self):
        """Collect information about pending cluster-level changes

        :rtype: dict
        """
        logger.debug('getting cluster pending tasks')
        return self._get_json(PATH_CLUSTER_PENDING_TASKS)

    def node_stats(self):
        """Collect statistics from local node.

        :rtype: dict
        """
        logger.debug('getting node statistics')
        return self._get_json(PATH_NODE_STATS)
