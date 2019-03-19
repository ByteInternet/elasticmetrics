import os
import json
from collections import OrderedDict
from mock import call
from elasticmetrics.formatters import flatten_metrics, sort_flatten_metrics_iter
from . import BaseTestCase, FIXTURES_PATH


FIXTURE_NODEMETRICS = os.path.join(FIXTURES_PATH, 'node_metrics.json')

with open(FIXTURE_NODEMETRICS, 'rt') as fh:
    MOCK_NODE_METRICS = json.load(fh)


class TestFlattenMetrics(BaseTestCase):
    def test_flatten_metrics_returns_a_dict_of_dot_separated_paths_from_metrics(self):
        expected_metrics = {
            'http.total_opened': 10,
            'http.current_open': 1,
            'process.cpu.percent': 0,
            'process.cpu.total_in_millis': 251710,
            'process.mem.total_virtual_in_bytes': 7133585408,
            'jvm.gc.collectors.young.collection_count': 335,
            'jvm.threads.count': 46,
            'jvm.threads.peak_count': 46,
            'fs.total.total_in_bytes': 57866743808,
            'fs.total.free_in_bytes': 15557791744,
            'fs.total.available_in_bytes': 12594728960,
            'transport.server_open': 0,
        }
        flattened = flatten_metrics(MOCK_NODE_METRICS)

        for key, value in expected_metrics.items():
            self.assertIn(key, flattened)
            self.assertEqual(flattened[key], value)

    def test_flatten_metrics_applies_path_separator_if_specified(self):
        expected_metrics = {
            'http->current_open': 1,
            'process->cpu->percent': 0,
            'process->cpu->total_in_millis': 251710,
            'jvm->gc->collectors->young->collection_count': 335,
            'jvm->threads->count': 46,
            'fs->total->total_in_bytes': 57866743808,
            'fs->total->available_in_bytes': 12594728960,
        }
        flattened = flatten_metrics(MOCK_NODE_METRICS, path_separator='->')

        for key, value in expected_metrics.items():
            self.assertIn(key, flattened)
            self.assertEqual(flattened[key], value)

    def test_flatten_metrics_prefixes_the_paths_with_the_specified_prefix(self):
        expected_metrics = {
            'mynode.http.total_opened': 10,
            'mynode.http.current_open': 1,
            'mynode.process.cpu.percent': 0,
        }
        flattened = flatten_metrics(MOCK_NODE_METRICS, prefix='mynode')

        for key, value in expected_metrics.items():
            self.assertIn(key, flattened)
            self.assertEqual(flattened[key], value)


class TestSortFlattenMetricsIter(BaseTestCase):
    def test_sort_flatten_metrics_iter_calls_flatten_metrics_on_all_metrics(self):
        mock_flatten = self.set_up_patch('elasticmetrics.formatters.flatten_metrics')
        mock_flatten.return_value = {
            'http.total_opened': 10,
            'http.current_open': 1,
        }

        sort_flatten_metrics_iter([MOCK_NODE_METRICS, MOCK_NODE_METRICS])
        mock_flatten.assert_has_calls([
            call(MOCK_NODE_METRICS, '.', ''),
            call(MOCK_NODE_METRICS, '.', '')
        ])

    def test_sort_flatten_metrics_iter_calls_flatten_metrics_on_metrics_with_separator_and_prefix(self):
        mock_flatten = self.set_up_patch('elasticmetrics.formatters.flatten_metrics')
        mock_flatten.return_value = {
            'http.total_opened': 10,
            'http.current_open': 1,
        }

        sort_flatten_metrics_iter([MOCK_NODE_METRICS], '->', 'mynode')
        mock_flatten.assert_called_once_with(MOCK_NODE_METRICS, '->', 'mynode')

    def test_sort_flatten_metrics_iter_returns_sorted_ordered_dict(self):
        metrics1 = {
            'fs': {'total': 200},
            'process': {'cpu': {'percent': 2}},
        }
        metrics2 = {
            'threads': {'count': 3},
            'http': {'total_opened': 70},
            'buffer_pools': {'direct': {'count': 41}},
        }
        expected = OrderedDict()
        expected['buffer_pools.direct.count'] = 41
        expected['fs.total'] = 200
        expected['http.total_opened'] = 70
        expected['process.cpu.percent'] = 2
        expected['threads.count'] = 3

        result = sort_flatten_metrics_iter((metrics1, metrics2))
        self.assertIsInstance(result, OrderedDict)
        self.assertEqual(result, expected)
