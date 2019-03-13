from elasticmetrics.collectors import ElasticSearchCollector
from elasticmetrics.http import HttpClient
from elasticmetrics.pystdlib.urllib_request import Request
from . import BaseTestCase


class TestElasticSearchCollector(BaseTestCase):
    def setUp(self):
        self.mock_urlopen = self.set_up_patch('elasticmetrics.http.urlopen')
        self.mock_urlopen.return_value = self._mock_urlopen_response('{"_nodes": []}')

    def test_elasitcsearch_collector_is_an_http_client_instance(self):
        es_collector = ElasticSearchCollector('localhost')
        self.assertIsInstance(es_collector, HttpClient)

    def test_elasticsearch_collector_init_uses_es_port_by_default(self):
        es_collector = ElasticSearchCollector('localhost')
        self.assertEqual(es_collector.port, 9200)

    def test_elasticsearch_collector_init_uses_es_port_by_default_for_https(self):
        es_collector = ElasticSearchCollector('localhost', scheme='https')
        self.assertEqual(es_collector.port, 9200)

    def test_elasticsearch_collector_cluster_health_queries_api_and_returns_parsed_json(self):
        es_collector = ElasticSearchCollector('localhost')
        resp = es_collector.cluster_health()

        self.assertEqual(resp, {"_nodes": []})
        self.assertTrue(self.mock_urlopen.called)
        urlopen_arg = self.mock_urlopen.call_args[0][0]
        self.assertIsInstance(urlopen_arg, Request)
        self.assertEqual(
            urlopen_arg.get_full_url(),
            'http://localhost:9200/_cluster/health'
        )

    def test_elasticsearch_collector_cluster_stats_queries_api_and_returns_parsed_json(self):
        es_collector = ElasticSearchCollector('es.example.org', port=9300, scheme='https')
        resp = es_collector.cluster_stats()

        self.assertEqual(resp, {"_nodes": []})
        self.assertTrue(self.mock_urlopen.called)
        urlopen_arg = self.mock_urlopen.call_args[0][0]
        self.assertIsInstance(urlopen_arg, Request)
        self.assertEqual(
            urlopen_arg.get_full_url(),
            'https://es.example.org:9300/_cluster/stats'
        )

    def test_elasticsearch_collector_node_stats_queries_api_and_returns_parsed_json(self):
        es_collector = ElasticSearchCollector('127.0.1.1', port=9200, scheme='https')
        resp = es_collector.node_stats()

        self.assertEqual(resp, {"_nodes": []})
        self.assertTrue(self.mock_urlopen.called)
        urlopen_arg = self.mock_urlopen.call_args[0][0]
        self.assertIsInstance(urlopen_arg, Request)
        self.assertEqual(
            urlopen_arg.get_full_url(),
            'https://127.0.1.1:9200/_nodes/_local/stats'
        )

    def test_elasticsearch_collector_cluster_pending_tasks_queries_api_and_returns_parsed_json(self):
        es_collector = ElasticSearchCollector('localhost', port=9300)
        resp = es_collector.cluster_pending_tasks()

        self.assertEqual(resp, {"_nodes": []})
        self.assertTrue(self.mock_urlopen.called)
        urlopen_arg = self.mock_urlopen.call_args[0][0]
        self.assertIsInstance(urlopen_arg, Request)
        self.assertEqual(
            urlopen_arg.get_full_url(),
            'http://localhost:9300/_cluster/pending_tasks'
        )
