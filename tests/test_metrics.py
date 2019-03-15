import os
import json
from elasticmetrics.metrics import node_performance_metrics
from . import BaseTestCase, FIXTURES_PATH


FIXTURE_NODESTATS = os.path.join(FIXTURES_PATH, 'node_stats.json')

with open(FIXTURE_NODESTATS, 'rt') as fh:
    MOCK_NODE_STATS = json.load(fh)


class TestNodePerformanceMetrics(BaseTestCase):

    def test_node_performance_metrics_returns_fs_total_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['fs']['total'], dict)
        self.assertEqual(metrics['fs']['total']['total_in_bytes'], 1203896320)
        self.assertEqual(metrics['fs']['total']['available_in_bytes'], 1121034240)
        self.assertEqual(metrics['fs']['total']['free_in_bytes'], 1200672768)

    def test_node_performance_metrics_returns_fs_iostats_total_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['fs']['io_stats']['total'], dict)
        self.assertEqual(metrics['fs']['io_stats']['total']['operations'], 18)
        self.assertEqual(metrics['fs']['io_stats']['total']['read_kilobytes'], 32)
        self.assertEqual(metrics['fs']['io_stats']['total']['read_operations'], 2)
        self.assertEqual(metrics['fs']['io_stats']['total']['write_kilobytes'], 72)
        self.assertEqual(metrics['fs']['io_stats']['total']['write_operations'], 16)

    def test_node_performance_metrics_returns_http_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['http'], dict)
        self.assertEqual(metrics['http']['current_open'], 13)
        self.assertEqual(metrics['http']['total_opened'], 1396355)

    def test_node_performance_metrics_returns_process_information_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['process'], dict)
        self.assertEqual(metrics['process']['cpu']['percent'], 13)
        self.assertEqual(metrics['process']['cpu']['total_in_millis'], 76362600)
        self.assertEqual(metrics['process']['max_file_descriptors'], 65536)
        self.assertEqual(metrics['process']['open_file_descriptors'], 763)
        self.assertEqual(metrics['process']['mem']['total_virtual_in_bytes'], 19547267072)

    def test_node_performance_metrics_returns_jvm_memory_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['jvm'], dict)
        self.assertIsInstance(metrics['jvm']['mem'], dict)
        mem_metrics = metrics['jvm']['mem']
        self.assertEqual(mem_metrics['heap_committed_in_bytes'], 12815171584)
        self.assertEqual(mem_metrics['heap_max_in_bytes'], 12815171584)
        self.assertEqual(mem_metrics['heap_used_in_bytes'], 2645643024)
        self.assertEqual(mem_metrics['heap_used_percent'], 20)
        self.assertEqual(mem_metrics['non_heap_used_in_bytes'], 119877816)
        self.assertEqual(mem_metrics['non_heap_committed_in_bytes'], 127721472)

    def test_node_performance_metrics_returns_jvm_gc_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['jvm'], dict)
        self.assertIsInstance(metrics['jvm']['gc'], dict)
        gc_metrics = metrics['jvm']['gc']
        self.assertEqual(gc_metrics['collectors']['old']['collection_count'], 2)
        self.assertEqual(gc_metrics['collectors']['old']['collection_time_in_millis'], 108)
        self.assertEqual(gc_metrics['collectors']['young']['collection_count'], 3266)
        self.assertEqual(gc_metrics['collectors']['young']['collection_time_in_millis'], 114463)
        # accumulated metrics
        self.assertEqual(gc_metrics['collection_count'], 3266 + 2)
        self.assertEqual(gc_metrics['collection_time_in_millis'], 114463 + 108)

    def test_node_performance_metrics_returns_jvm_threads_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['jvm'], dict)
        self.assertIsInstance(metrics['jvm']['threads'], dict)
        threads_metrics = metrics['jvm']['threads']
        self.assertEqual(threads_metrics['count'], 89)
        self.assertEqual(threads_metrics['peak_count'], 91)

    def test_node_performance_metrics_returns_jvm_buffer_pool_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['jvm'], dict)
        self.assertIsInstance(metrics['jvm']['buffer_pools'], dict)
        buf_metrics = metrics['jvm']['buffer_pools']
        self.assertEqual(buf_metrics['direct']['count'], 86)
        self.assertEqual(buf_metrics['direct']['used_in_bytes'], 540041224)
        self.assertEqual(buf_metrics['mapped']['count'], 1)
        self.assertEqual(buf_metrics['mapped']['used_in_bytes'], 5403)
        # accumulated metrics
        self.assertEqual(buf_metrics['count'], 86 + 1)
        self.assertEqual(buf_metrics['used_in_bytes'], 540041224 + 5403)
