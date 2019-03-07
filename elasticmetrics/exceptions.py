"""
elasticmetrics.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~
Exception classes for the package
"""


class ElasticMetricsError(Exception):
    """Base exception class for all exceptions thrown by this package"""
    pass


class ElasticMetricsRequestError(ElasticMetricsError):
    """Errors on failure to query ElasticSearch"""
    pass
