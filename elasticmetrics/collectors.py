import json
from contextlib import closing
from logging import getLogger
from base64 import b64encode
from .pystdlib.urllib_request import urlopen, Request
from .exceptions import ElasticMetricsError, ElasticMetricsRequestError


PATH_CLUSTER_HEALTH = '_cluster/health'
PATH_CLUSTER_STATS = '_cluster/stats'
PATH_CLUSTER_PENDING_TASKS = '_cluster/pending_tasks'
PATH_NODE_STATS = '_nodes/_local/stats'

logger = getLogger(__name__)


class ElasticSearchCollector(object):
    def __init__(self, host, port=9200, user=None, password=None, scheme='http', headers=None):
        """Collect ElasticSearch metrics

        :param str host: ES server hostname/address
        :param int port: ES server port number
        :param str user: HTTP basic auth user
        :param str password: HTTP basic auth password
        :param str scheme: URL scheme, http/https
        :param dict headers: dictionary of additional headers
        """
        if scheme not in ('http', 'https'):
            raise ElasticMetricsError('invalid scheme "{}"'.format(scheme))

        self._host = host
        self._port = port
        self._user = user
        self._scheme = scheme
        self._password = password
        self._headers = headers or {}
        if user and password:
            # b64encode wants/returns bytes, we encode input and decode results
            basic_auth = b64encode(
                            u'{}:{}'.format(user, password).encode('utf-8')
                        ).decode('utf-8').strip()
            self._headers['Authorization'] = 'Basic {}'.format(basic_auth)

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def scheme(self):
        return self._scheme

    @property
    def headers(self):
        return self._headers.copy()

    def _request_get(self, path):
        """Send a GET request to the URL path and return the decoded response
        :param str path: the URL path to request for
        :raise ElasticMetricsRequestError
        """
        url = '{}://{}:{}/{}'.format(self._scheme, self._host, self._port, path)
        request = Request(url, headers=self._headers)
        try:
            logger.debug('requesting URL "{}"'.format(url))
            with closing(urlopen(request)) as response:
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
