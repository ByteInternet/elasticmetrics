from copy import copy


STATUS_CODES = {
    'green': 2,
    'yellow': 4,
    'red': 6,
}


def cluster_health_metrics(health_stats):
    """From cluster health stats structure, returns a dictionary of cluster metrics.

    :param dict health_stats: dict of cluster info as returned from _cluster/health API
    :return dict: selection of cluster metrics (numeric values)
    """
    metrics = _dict_map(
               int,
               _available_keys(
                   health_stats,
                   ('active_primary_shards', 'active_shards', 'active_shards_percent_as_number',
                    'delayed_unassigned_shards', 'initializing_shards', 'number_of_in_flight_fetch',
                    'number_of_pending_tasks', 'relocating_shards', 'task_max_waiting_in_queue_millis')
                )
           )

    metrics['status'] = STATUS_CODES.get(health_stats.get('status', '').lower().strip(), 0)
    return metrics


def node_performance_metrics(node_stats):
    """From node stats structure, returns a dictionary of node performance metrics.

    :param dict node_stats: dict of node stats, as returned by _nodes/*/stats API
    :return dict: selection of node performance metrics (numeric values)
    """
    metrics = {}
    node_id = list(node_stats['nodes'].keys()).pop()
    node_data = node_stats['nodes'][node_id]

    # file system metrics
    fs_stats = node_data.get('fs')
    if fs_stats:
        metrics['fs'] = _get_node_fs_metrics(fs_stats)

    metrics['http'] = node_data['http']  # HTTP connections info

    # process resource usage
    proc_stats = node_data.get('process')
    if proc_stats:
        metrics['process'] = _get_node_process_metrics(proc_stats)

    # jvm metrics
    jvm_stats = node_data.get('jvm')
    if jvm_stats:
        metrics['jvm'] = _get_node_jvm_metrics(jvm_stats)

    # transport metrics: inter node send/reads
    if 'transport' in node_data:
        metrics['transport'] = node_data['transport']

    # thread_pool metrics
    if 'thread_pool' in node_data:
        metrics['thread_pool'] = node_data['thread_pool']

    # indices metrics
    indices_stats = node_data.get('indices')
    if indices_stats:
        metrics['indices'] = _get_node_indices_metrics(indices_stats)

    return metrics


def _get_node_fs_metrics(fs_stats):
    fs_metrics = {}
    if 'total' in fs_stats:
        fs_metrics['total'] = _available_keys(
                                fs_stats['total'],
                                ('available_in_bytes', 'free_in_bytes', 'total_in_bytes')
                              )

    # io_stats is not available on all platforms
    if 'io_stats' in fs_stats and 'total' in fs_stats['io_stats']:
        fs_metrics['io_stats'] = {}
        io_stats_total = fs_stats['io_stats']['total']
        fs_metrics['io_stats']['total'] = _available_keys(
                                            io_stats_total,
                                            ('operations', 'read_kilobytes', 'read_operations',
                                             'write_kilobytes', 'write_operations')
                                          )
    return fs_metrics


def _get_node_process_metrics(proc_stats):
    """Return process metrics from the process stats dict, which
    is the "process" key in the response from the node stats API.

    :param dict proc_stats: the "process" key from node stats API response
    :return: dict
    """
    return _available_keys(
                proc_stats,
                ('cpu', 'mem', 'max_file_descriptors', 'open_file_descriptors')
            )


def _get_node_jvm_metrics(jvm_stats):
    """Return JVM related metrics from the JVM stats dict, which
    is the "jvm" key in the response from the node stats API
    Some keys may be added to the returning dict (for example aggregated metrics):
     - buffer_pool.total: aggregate buffer pool metrics for different pools
     - gc.collection_*: aggregate metrics from different gc subsections

    :param dict jvm_stats: the "jvm" key from node stats API response
    :return: dict
    """
    jvm_metrics = {}
    metric_section_keys = {
        'mem': ('heap_committed_in_bytes', 'heap_used_in_bytes', 'heap_used_percent',
                'heap_max_in_bytes', 'non_heap_committed_in_bytes', 'non_heap_used_in_bytes'),
        'threads': ('count', 'peak_count'),
    }

    for section, section_keys in metric_section_keys.items():
        if section in jvm_stats:
            jvm_metrics[section] = _available_keys(jvm_stats[section], section_keys)

    jvm_metrics['gc'] = copy(jvm_stats['gc'])
    gc_total_collection_count, gc_total_collection_time = 0, 0
    for collection_stats in jvm_metrics['gc']['collectors'].values():
        gc_total_collection_count += collection_stats['collection_count']
        gc_total_collection_time += collection_stats['collection_time_in_millis']
    if 'collection_count' not in jvm_metrics['gc']:
        jvm_metrics['gc']['collection_count'] = gc_total_collection_count
    if 'collection_time_in_millis' not in jvm_metrics['gc']:
        jvm_metrics['gc']['collection_time_in_millis'] = gc_total_collection_time

    if 'buffer_pools' in jvm_stats:
        jvm_metrics['buffer_pools'] = copy(jvm_stats['buffer_pools'])
        buf_total_count, buf_total_used, buf_total_cap = 0, 0, 0
        for buffer_stats in jvm_stats['buffer_pools'].values():
            buf_total_count += buffer_stats['count']
            buf_total_used += buffer_stats['used_in_bytes']
            buf_total_cap += buffer_stats['total_capacity_in_bytes']
        jvm_metrics['buffer_pools']['total'] = {
            'count': buf_total_count,
            'used_in_bytes': buf_total_used,
            'total_capacity_in_bytes': buf_total_cap,
        }

    return jvm_metrics


def _get_node_indices_metrics(indices_stats):
    """Return metrics from indices stats from the node, which is the "indices" key
    in the response from the node stats API.

    :param dict indics_stats: the "indices" key from node stats API response
    :return: dict
    """
    indices_metrics = {}
    metric_section_keys = {
        'docs': ('count', 'deleted'),
        'fielddata': ('evictions', 'memory_size_in_bytes'),
        'query_cache': ('evictions', 'hit_count', 'miss_count', 'memory_size_in_bytes'),
        'request_cache': ('evictions', 'hit_count', 'miss_count', 'memory_size_in_bytes'),
        'search': ('fetch_current', 'query_current', 'scroll_current', 'suggest_current'),
        'segments': ('count', 'memory_in_bytes', 'index_writer_memory_in_bytes',
                     'fixed_bit_set_memory_in_bytes', 'doc_values_memory_in_bytes', 'version_map_memory_in_bytes'),
        'store': ('size_in_bytes',),
        'translog': ('operations', 'size_in_bytes', 'uncommitted_operations', 'uncommitted_size_in_bytes'),
        'warmer': ('current', 'total'),
    }

    for section, section_keys in metric_section_keys.items():
        if section in indices_stats:
            indices_metrics[section] = _available_keys(indices_stats[section], section_keys)

    return indices_metrics


def _available_keys(dict_, keys):
    """Return a sub dictionary of the argument, with the specified keys, only if they exit.

    :param dict dict_: the source dictionary
    :pram iterable keys: desired keys
    :return: dict
    """
    return {k: dict_[k] for k in set(keys).intersection(dict_.keys())}


def _dict_map(func, dict_):
    """Return a dictionary of the results of applying the function
    to the values of the provided dictionary, preserving the keys.
    """
    return {k: func(dict_[k]) for k in dict_}
