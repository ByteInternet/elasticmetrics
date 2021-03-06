import os
import json
from elasticmetrics.metrics import node_performance_metrics, cluster_health_metrics
from . import BaseTestCase, FIXTURES_PATH


FIXTURE_NODESTATS = os.path.join(FIXTURES_PATH, 'node_stats.json')

with open(FIXTURE_NODESTATS, 'rt') as fh:
    MOCK_NODE_STATS = json.load(fh)


MOCK_CLUSTER_HEALTH = {
    "active_primary_shards": 3962,
    "active_shards": 7927,
    "active_shards_percent_as_number": 100.0,
    "cluster_name": "es",
    "delayed_unassigned_shards": 0,
    "initializing_shards": 0,
    "number_of_data_nodes": 8,
    "number_of_in_flight_fetch": 0,
    "number_of_nodes": 10,
    "number_of_pending_tasks": 1,
    "relocating_shards": 0,
    "status": "green",
    "task_max_waiting_in_queue_millis": 10,
    "timed_out": False,
    "unassigned_shards": 1
}


class TestClusterHealthMetrics(BaseTestCase):
    def test_cluster_health_metrics_returns_integer_metrics(self):
        metrics = cluster_health_metrics(MOCK_CLUSTER_HEALTH)
        self.assertIsInstance(metrics, dict)
        self.assertEqual(metrics['active_primary_shards'], 3962)
        self.assertEqual(metrics['active_shards'], 7927)
        self.assertEqual(metrics['active_shards_percent_as_number'], 100)
        self.assertEqual(metrics['delayed_unassigned_shards'], 0)
        self.assertEqual(metrics['initializing_shards'], 0)
        self.assertEqual(metrics['number_of_in_flight_fetch'], 0)
        self.assertEqual(metrics['number_of_pending_tasks'], 1)
        self.assertEqual(metrics['relocating_shards'], 0)
        self.assertEqual(metrics['task_max_waiting_in_queue_millis'], 10)
        self.assertEqual(metrics['status'], 2)

    def test_cluster_health_metrics_normalizes_status_value(self):
        metrics = cluster_health_metrics({'status': 'GrEEn '})
        self.assertEqual(metrics['status'], 2)

    def test_cluster_health_metrics_returns_status_yellow(self):
        metrics = cluster_health_metrics({'status': 'yellow'})
        self.assertEqual(metrics['status'], 4)

    def test_cluster_health_metrics_returns_status_red(self):
        metrics = cluster_health_metrics({'status': 'red'})
        self.assertEqual(metrics['status'], 6)

    def test_cluster_health_metrics_normalizes_returns_status_0_if_missing(self):
        metrics = cluster_health_metrics({})
        self.assertEqual(metrics['status'], 0)


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
        # aggregated metrics
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
        # aggregated metrics
        self.assertEqual(buf_metrics['total']['count'], 86 + 1)
        self.assertEqual(buf_metrics['total']['used_in_bytes'], 540041224 + 5403)

    def test_node_performance_metrics_returns_transport_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['transport'], dict)
        self.assertEqual(metrics['transport']['rx_count'], 3351172)
        self.assertEqual(metrics['transport']['rx_size_in_bytes'], 76369739396)
        self.assertEqual(metrics['transport']['tx_count'], 3351172)
        self.assertEqual(metrics['transport']['tx_size_in_bytes'], 14846089376)

    def test_node_performance_metrics_returns_thread_pool_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertEqual(metrics['thread_pool'], MOCK_NODE_STATS['nodes']['abcd12345node']['thread_pool'])

    def test_node_performance_metrics_returns_indices_docs_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['indices']['docs'], dict)
        sub_metrics = metrics['indices']['docs']
        self.assertEqual(sub_metrics['count'], 0)
        self.assertEqual(sub_metrics['deleted'], 0)

    def test_node_performance_metrics_returns_indices_fielddata_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['indices']['fielddata'], dict)
        sub_metrics = metrics['indices']['fielddata']
        self.assertEqual(sub_metrics['evictions'], 0)
        self.assertEqual(sub_metrics['memory_size_in_bytes'], 0)

    def test_node_performance_metrics_returns_indices_query_cache_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['indices']['query_cache'], dict)
        sub_metrics = metrics['indices']['query_cache']
        self.assertEqual(sub_metrics['evictions'], 0)
        self.assertEqual(sub_metrics['hit_count'], 0)
        self.assertEqual(sub_metrics['miss_count'], 0)
        self.assertEqual(sub_metrics['memory_size_in_bytes'], 0)

    def test_node_performance_metrics_returns_indices_request_cache_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['indices']['request_cache'], dict)
        sub_metrics = metrics['indices']['request_cache']
        self.assertEqual(sub_metrics['evictions'], 0)
        self.assertEqual(sub_metrics['hit_count'], 0)
        self.assertEqual(sub_metrics['miss_count'], 0)
        self.assertEqual(sub_metrics['memory_size_in_bytes'], 0)

    def test_node_performance_metrics_returns_indices_search_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['indices']['search'], dict)
        sub_metrics = metrics['indices']['search']
        self.assertEqual(sub_metrics['fetch_current'], 0)
        self.assertEqual(sub_metrics['query_current'], 0)
        self.assertEqual(sub_metrics['scroll_current'], 0)
        self.assertEqual(sub_metrics['suggest_current'], 0)

    def test_node_performance_metrics_returns_indices_segments_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['indices']['segments'], dict)
        sub_metrics = metrics['indices']['segments']
        self.assertEqual(sub_metrics['count'], 0)
        self.assertEqual(sub_metrics['doc_values_memory_in_bytes'], 0)
        self.assertEqual(sub_metrics['fixed_bit_set_memory_in_bytes'], 0)
        self.assertEqual(sub_metrics['index_writer_memory_in_bytes'], 0)
        self.assertEqual(sub_metrics['memory_in_bytes'], 0)
        self.assertEqual(sub_metrics['version_map_memory_in_bytes'], 0)

    def test_node_performance_metrics_returns_indices_store_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['indices']['store'], dict)
        sub_metrics = metrics['indices']['store']
        self.assertEqual(sub_metrics['size_in_bytes'], 0)

    def test_node_performance_metrics_returns_indices_translog_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['indices']['translog'], dict)
        sub_metrics = metrics['indices']['translog']
        self.assertEqual(sub_metrics['operations'], 0)
        self.assertEqual(sub_metrics['size_in_bytes'], 0)
        self.assertEqual(sub_metrics['uncommitted_operations'], 0)
        self.assertEqual(sub_metrics['uncommitted_size_in_bytes'], 0)

    def test_node_performance_metrics_returns_indices_warmer_metrics(self):
        metrics = node_performance_metrics(MOCK_NODE_STATS)
        self.assertIsInstance(metrics['indices']['warmer'], dict)
        sub_metrics = metrics['indices']['warmer']
        self.assertEqual(sub_metrics['current'], 0)
        self.assertEqual(sub_metrics['total'], 0)
