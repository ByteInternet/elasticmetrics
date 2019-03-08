import json
from contextlib import closing
from logging import getLogger
from .common import HttpClient
from .exceptions import ElasticMetricsRequestError


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

    def _request_get(self, path):
        """Send a GET request to the URL path and return the decoded response
        :param str path: the URL path to request for
        :raise ElasticMetricsRequestError
        """
        request = self._create_request(path)
        url = request.get_full_url()
        try:
            logger.debug('requesting URL "{}"'.format(url))
            with closing(self._urlopen(request)) as response:
                logger.debug('URL "{}" response code "{}"'.format(response.getcode()))
                return json.load(response)
        except IOError as err:
            logger.error('failed to request URL "{}": {}'.format(url, err))
            raise ElasticMetricsRequestError('request error to URL "{}": {}'.format(url, err))
        except ValueError as err:
            logger.error('invalid JSON response from "{}": {}'.format(url, err))
            raise ElasticMetricsRequestError(
                      'invalid JSON response from "{}": {}'.format(url, err)
                  )

    def cluster_health(self):
        """Collect cluster health status

        :rtype: dict
        """
        return self._request_get(PATH_CLUSTER_HEALTH)

    def cluster_stats(self):
        """Collect statistics from a cluster point of view, includes
        basic index metrics and node information.

        :rtype: dict
        """
        return self._request_get(PATH_CLUSTER_STATS)

    def cluster_pending_tasks(self):
        """Collect information about pending cluster-level changes

        :rtype: dict
        """
        return self._request_get(PATH_CLUSTER_PENDING_TASKS)

    def node_stats(self):
        """Collect statistics from local node.

        :rtype: dict
        """
        return self._request_get(PATH_NODE_STATS)
