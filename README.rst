.. hein

.. image:: http://img.shields.io/travis/ceyzeriat/hein/master.svg?style=flat
    :target: https://travis-ci.org/ceyzeriat/hein
.. image:: https://coveralls.io/repos/github/ceyzeriat/hein/badge.svg?branch=master
    :target: https://coveralls.io/github/ceyzeriat/hein?branch=master
.. image:: http://img.shields.io/badge/license-GPLv3-blue.svg?style=flat
    :target: https://github.com/ceyzeriat/hein/blob/master/LICENSE

:Name: hein
:Website: https://github.com/ceyzeriat/hein
:Author: Guillaume Schworer
:Version: 0.1

Hein: Advanced Subscriber-Publisher Socket Communication.

The native TPC/IP sockets implement a N-to-1 communication scheme: many clients (e.g. browsers) talk to a unique server (e.g. internet provider server) and engage a 1-to-1 communication (e.g. url request) with it for which they will all get their own individual answers (e.g. web page). In this particular case, the server is passive: the only thing it does is answer the clients in a 1-to-1 communication.
If there is no client, the server does nothing. If there is no server, the client returns an error.

Now let's imagine the reverse case where one would like to broadcast a same message to N listeners, where N is subject to changing, whether the listening service is launched or not. This is a typical case where one would like a client to talk to many listening servers... where the listening-servers did the "connection step" towards the broadcasting client... and the client is broadcasting its message even if no server is actually listening.

Well, my friend, you are stuck.

Actually not, because this is exactly what hein does: 1-Publisher to N-Subscriber socket communication.


Documentation
=============

Refer to this page for detailed API documentation, http://pythonhosted.org/hein/hein.html


Requirements
============

Hein requires the following Python packages:

* socket: Obviously
* threading, select: for threading and port-reading
* time, os: for basic stuff
* byt: to handle chains of bytes identically no matter the python version


Installation
============

The easiest and fastest way for you to get the package and run is to install hein through pip::

  $ pip install hein

You can also download Hein source from GitHub and type::

  $ python setup.py install

Dependency on byt will be installed automatically. Refer to the requirements section. If you have a standard install of python (or any fancier distribution like anaconda), you should be good to go.

Contributing
============

Code writing
------------

Code contributions are welcome! Just send a pull request on GitHub and we will discuss it. In the `issue tracker`_ you may find pending tasks.

Bug reporting
-------------

If you think you've found one please refer to the `issue tracker`_ on GitHub.

.. _`issue tracker`: https://github.com/ceyzeriat/hein/issues

Additional options
------------------

You can either send me an e-mail or add it to the issues/wishes list on GitHub.

Citing
======

If you use Hein on your project, please
`drop me a line <mailto:{my first name}.{my family name}@gmail.com>`, you will get fixes and additional options earlier.

License
=======

Hein is released under the GNU General Public License v3 or later (GPLv3+). Please refer to the LICENSE file.
