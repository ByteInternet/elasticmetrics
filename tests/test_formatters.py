import os
import json
from elasticmetrics.formatters import flatten_metrics
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
