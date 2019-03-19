***************
Elastic Metrics
***************

Collect performance metrics from ElasticSearch.

`elasticmetrics` is a Python library, designed to be used in different contexts and easy
to integrate with other tools. Each step of data collection, transformation and
reporting is defined in a separate reusable module:

* `collectors`: abstract logic of collecting data.
* `metrics`: abstract selecting and/or aggregating measurments (metrics)
* `formatters`: transform metrics into other formats.
* `tool`: combine the functionality of other modules to form a CLI application

Collectors
----------

`collectors.ElasticSearchCollector` collects cluster and node stats by calling ElasticSearch APIs.


.. code-block:: python

    from elasticmetrics.collectors import ElasticSearchCollector

    collector = ElasticSearchCollector('es.example.org')
    collector.cluster_health()  # call _cluster/health, get ES cluster high level stats
    collector.cluster_stats()  # call _cluster/stats, get ES cluster detailed stats
    collector.node_stats()  # call _node/_local/stats, get ES node detailed stats


    # collector supports detailed configurations like
    # SSL, basic HTTP auth with UTF-8 credentials, and control over SSL context
    insecure_ssl_collector = ElasticSearchCollector(
                                'localhost',
                                port=9200,
                                scheme='https',
                                user=u't€stuser',
                                password=u't€stpássword',
                                ssl_context={'no_cert_verify': True}
                             )


The returned values are exactly what's returned from the Elasitc APIs.


Composing Features
------------------

Features from different modules can be composed together to achieve expected behavior.


.. code-block:: python

    from elasticmetrics.collectors import ElasticSearchCollector
    from elasticmetrics.metrics import flatten_metrics

    collector = ElasticSearchCollector(
                    'es.example.org',
                    scheme='https',
                    user='testuser',
                    password='testpassword'
                )
    metrics_as_dotted_paths = flatten_metrics(
        collect.node_stats()
        prefix='example_es_server'
    )
    # metrics_as_dotted_paths can be pushed to a time series backend, like Graphite



Installation
============

.. code-block:: bash

    $ pip install elasticmetrics


The only dependencies are Python 2.7+ and setuptools.

However on development (and test) environment
`pytest <https://pypi.org/project/pytest/>`_, `mock <https://pypi.org/project/mock>`_
and `pycodestyle <https://pypi.org/project/pycodestyle/>`_ are required.


.. code-block:: bash

    # on dev/test env
    $ pip install -r requirements/dev.txt


CLI Tool
========

`elasticmetrics.tool` is a CLI program that exposes some of the functionlaty of the library. It'll execute when imported:


.. code-block:: bash

    $ python -m elasticmetrics.tool --help


Elastic credentials can be passed as arguments, or set as environment variables.
The example below will connect to ElasticSearch listening on the default port on localhost
over HTTPS, and only collect node stats, and reads access credentials from environment variables.


.. code-block:: bash

    $ export ELASTICSEARCH_USER="someuser"
    $ export ELASTICSEARCH_PASSWORD="somepassword"
    $ python -m elasticmetrics.tool --ssl --quiet --collect node_stats



Development
===========

* Code is on `GitHub <https://github.com/ByteInternet/elasticmetrics>`_


Tests
-----

`Tox <https://pypi.org/project/tox/>`_ is most convenient to run tests with, since it handles creation of virtualenvs

.. code-block:: bash

    $ tox

Or when development dependencies are installed (preferably with a virtual environment),
tests can be run by directly calling `pytest`.

.. code-block:: bash

    $ pytest


License
=======

elasticmetrics is released under the terms of the MIT license.

The MIT License (MIT)

Copyright (c) 2019 Byte B.V.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
