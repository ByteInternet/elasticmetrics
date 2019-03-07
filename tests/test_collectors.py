# -*- coding: utf-8 -*-
from elasticmetrics.collectors import ElasticSearchCollector
from elasticmetrics.exceptions import ElasticMetricsError
from . import BaseTestCase


class TestElasticSearchCollector(BaseTestCase):
    def test_elasticsearch_collector_init_has_default_params(self):
        es_collector = ElasticSearchCollector('localhost')
        self.assertEqual(es_collector.host, 'localhost')
        self.assertEqual(es_collector.port, 9200)
        self.assertEqual(es_collector.scheme, 'http')
        self.assertIsNone(es_collector.user)
        self.assertIsNone(es_collector.password)
        self.assertEqual(es_collector.headers, {})

    def test_elasticsearch_collector_init_sets_attrs_from_params(self):
        es_collector = ElasticSearchCollector(
            host='es.example.org',
            port=9222,
            user='testuser',
            password='testpassword',
            scheme='https',
            headers={'CustomHeader': 'header_value'}
        )
        self.assertEqual(es_collector.host, 'es.example.org')
        self.assertEqual(es_collector.port, 9222)
        self.assertEqual(es_collector.user, 'testuser')
        self.assertEqual(es_collector.password, 'testpassword')
        self.assertEqual(es_collector.scheme, 'https')
        self.assertIsInstance(es_collector.headers, dict)
        self.assertIn(es_collector.headers['CustomHeader'], 'header_value')

    def test_elasticsearch_collector_init_sets_authorization_header_from_user_password(self):
        es_collector = ElasticSearchCollector(
            'localhost',
            user='testuser',
            password='testpassword',
        )
        self.assertEqual(
            es_collector.headers['Authorization'],
            'Basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk',
        )

    def test_elasticsearch_collector_init_raises_on_invalid_scheme(self):
        with self.assertRaises(ElasticMetricsError):
            es_collector = ElasticSearchCollector(
                'es.example.org',
                scheme='nothttp',
            )

    def test_elasticsearch_collector_supports_utf8_credentials(self):
        es_collector = ElasticSearchCollector(
            host='es.example.org',
            user=u't€stuser',
            password=u't€stpássword',
        )
        self.assertEqual(es_collector.user, u't€stuser')
        self.assertEqual(es_collector.password, u't€stpássword')
        self.assertEqual(
            es_collector.headers['Authorization'],
            'Basic dOKCrHN0dXNlcjp04oKsc3Rww6Fzc3dvcmQ=',
        )
