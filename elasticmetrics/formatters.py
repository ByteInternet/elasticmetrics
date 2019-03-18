def flatten_metrics(metrics, path_separator='.', prefix=''):
    """Format the metrics into a dictionary that maps unique paths to
    metric values. paths are separated by the path_separator character, default
    is ".".
    Only dictionary containers are supported, as metrics are a hierarchy of names mapped
    to numeric values.

    :param dict metrics: dictionary of metrics.
    :param str path_separator: separate paths in flattened path from the hierarchy
    :param str prefix: prefix for the metrics paths
    :return dict: flattened unique paths mapped to metric values
    """
    flattened = {}
    for name in metrics:
        value = metrics[name]
        current_path = prefix + path_separator + name if prefix else name
        if isinstance(value, dict):
            sub_paths = flatten_metrics(value, path_separator, prefix=current_path)
            for (subpath, value) in sub_paths.items():
                flattened[subpath] = value
        else:
            flattened[current_path] = value

    return flattened
