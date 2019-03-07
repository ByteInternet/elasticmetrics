# -*- coding: utf-8 -*-
from ssl import SSLContext
from elasticmetrics.common import HttpClient
from elasticmetrics.exceptions import ElasticMetricsError
from . import BaseTestCase


class TestHttpClient(BaseTestCase):
    def test_http_client_init_has_default_params(self):
        http_client = HttpClient('localhost')
        self.assertEqual(http_client.host, 'localhost')
        self.assertEqual(http_client.port, 80)
        self.assertEqual(http_client.scheme, 'http')
        self.assertIsNone(http_client.user)
        self.assertIsNone(http_client.password)
        self.assertEqual(http_client.headers, {})
        self.assertIsNone(http_client.ssl_context)

    def test_http_client_init_sets_attrs_from_params(self):
        http_client = HttpClient(
            host='www.example.org',
            port=443,
            user='testuser',
            password='testpassword',
            scheme='https',
            headers={'CustomHeader': 'header_value'}
        )
        self.assertEqual(http_client.host, 'www.example.org')
        self.assertEqual(http_client.port, 443)
        self.assertEqual(http_client.user, 'testuser')
        self.assertEqual(http_client.password, 'testpassword')
        self.assertEqual(http_client.scheme, 'https')
        self.assertIsInstance(http_client.headers, dict)
        self.assertIn(http_client.headers['CustomHeader'], 'header_value')
        self.assertIsInstance(http_client.ssl_context, SSLContext)

    def test_http_client_init_sets_authorization_header_from_user_password(self):
        http_client = HttpClient(
            'localhost',
            user='testuser',
            password='testpassword',
        )
        self.assertEqual(
            http_client.headers['Authorization'],
            'Basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk',
        )

    def test_elasticsearch_collector_supports_utf8_credentials(self):
        http_client = HttpClient(
            host='www.example.org',
            user=u't€stuser',
            password=u't€stpássword',
        )
        self.assertEqual(http_client.user, u't€stuser')
        self.assertEqual(http_client.password, u't€stpássword')
        self.assertEqual(
            http_client.headers['Authorization'],
            'Basic dOKCrHN0dXNlcjp04oKsc3Rww6Fzc3dvcmQ=',
        )

    def test_elasticsearch_collector_init_raises_on_invalid_scheme(self):
        with self.assertRaises(ElasticMetricsError):
            http_client = HttpClient(
                'www.example.org',
                scheme='nothttp',
            )

    def test_http_client_headers_are_immutable(self):
        http_client = HttpClient('www.example.org')
        headers = http_client.headers
        headers['NewHeader'] = 'new value'
        self.assertEqual(http_client.headers, {})
