from elasticmetrics.collectors import ElasticSearchCollector
from elasticmetrics.http import HttpClient
from . import BaseTestCase


class TestElasticSearchCollector(BaseTestCase):
    def test_elasitcsearch_collector_is_an_http_client_instance(self):
        es_collector = ElasticSearchCollector('localhost')
        self.assertIsInstance(es_collector, HttpClient)

    def test_elasticsearch_collector_init_uses_es_port_by_default(self):
        es_collector = ElasticSearchCollector('localhost')
        self.assertEqual(es_collector.port, 9200)

    def test_elasticsearch_collector_init_uses_es_port_by_default_for_https(self):
        es_collector = ElasticSearchCollector('localhost', scheme='https')
        self.assertEqual(es_collector.port, 9200)
