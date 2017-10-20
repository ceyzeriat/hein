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

The native TPC/IP sockets implement a N-to-1 communication scheme: many clients (e.g. browsers) talk to a unique server (e.g. internet provider server) and engage a 1-to-1 communication (e.g. url request) with the server from which they will all get their own individual answers (e.g. web page). In this particular case, the server is passive: the only thing it does is answer the clients in a 1-to-1 communication.
If there is no client, the server does nothing. If there is no server, the client returns an error.

Now let's imagine the reverse case where one would like to broadcast a same message to N listeners, where N is subject to changing, whether some of the listening services are launched or not. This is a typical case where one would like a client to talk to many listening servers... and where the listening-servers did the "connection step" towards the broadcasting client... and the client is broadcasting its message even if no server is actually listening.

Well, my friend, you are stuck.

Actually not, because this is exactly what hein does: 1-Publisher to N-Subscriber socket communication.

Exemple
=======

Straight to the point: launch 3 terminals in which you should start an interactive python interpreter.

In the first terminal (listener 1), type:

.. code-block:: python

    from hein import SocReceiver
    r = SocReceiver(port=50007, name="Captain")
    
in the second one (transmitter), type:

.. code-block:: python

    from hein import SocTransmitter
    t = SocTransmitter(port=50007, nreceivermax=2)
    
You will instantly see the transmitter terminal wishing a hearful welcome to its first listener.

In in the third one (listener 2), type:

.. code-block:: python

    from hein import SocReceiver
    r = SocReceiver(port=50007, name="Kirk")
    
Here again, the transmitter terminal acknoledges the connection of the second listener. Now type in the transmitter terminal:

.. code-block:: python

    t.tell_raw('hello!')
    
And you will see the message appear in both listening terminals.

This in no magic, this is smart socket communication.

Obviously, the behavior at connection and reception is driven my callback functions, which by default only print the listener's names or the message transmitted.
All you will need now is write your own functions to replace these default callbacks.
That's it.


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
