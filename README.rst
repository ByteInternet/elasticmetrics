***************
Elastic Metrics
***************

Collect performance metrics from ElasticSearch.


Installation
------------

.. code-block:: bash

    $ pip install elasticmetrics


The only dependencies are Python 2.7+ and setuptools.

However on development (and test) environment
`pytest <https://pypi.org/project/pytest/>`_ and `mock <https://pypi.org/project/mock>`_ are required.

.. code-block:: bash

    # on dev/test env
    $ pip install -r requirements/dev.txt


Development
-----------

* Code is on `GitHub <https://github.com/ByteInternet/elasticmetrics>`_


Tests
^^^^^

`Tox <https://pypi.org/project/tox/>`_ is most convenient to run tests with, since it handles creation of virtualenvs

.. code-block:: bash

    $ tox

When development dependencies are installed (preferably with a virtual environment),
tests can be run by calling `pytest`.

.. code-block:: bash

    $ pytest


License
-------

elasticmetrics is released under the terms of the `MIT license <http://opensource.org/licenses/MIT>`_.

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
