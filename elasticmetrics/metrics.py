from copy import copy


def node_performance_metrics(node_stats):
    """From node stats structure, returns a dictionary of node performance metrics.

    :param dict node_stats: dict of node stats, as returned by _nodes/*/stats API
    :return dict: selection of node performance metrics
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
    return _available_keys(
                proc_stats,
                ('cpu', 'mem', 'max_file_descriptors', 'open_file_descriptors')
            )


def _get_node_jvm_metrics(jvm_stats):
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
        if 'count' not in jvm_metrics['buffer_pools']:
            jvm_metrics['buffer_pools']['count'] = buf_total_count
        if 'used_in_bytes' not in jvm_metrics['buffer_pools']:
            jvm_metrics['buffer_pools']['used_in_bytes'] = buf_total_used
        if 'total_capacity_in_bytes' not in jvm_metrics['buffer_pools']:
            jvm_metrics['buffer_pools']['total_capacity_in_bytes'] = buf_total_cap

    return jvm_metrics


def _available_keys(dict_, keys):
    """Return a sub dictionary of the argument, with the specified keys, only if they exit.

    :param dict dict_: the source dictionary
    :pram iterable keys: desired keys
    :return: dict
    """
    return {k: dict_[k] for k in set(keys).intersection(dict_.keys())}
