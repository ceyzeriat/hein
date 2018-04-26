.. hein

.. image:: http://img.shields.io/badge/license-GPLv3-blue.svg?style=flat

    :target: https://github.com/ceyzeriat/hein/blob/master/LICENSE

:Name: hein
:Website: https://github.com/ceyzeriat/hein
:Author: Guillaume Schworer
:Version: 0.1

Hein: Advanced Subscriber-Publisher Socket Communication. Fully compatible python2 and 3.

The native TPC/IP sockets implement a N-to-1 communication scheme: many clients (e.g. browsers) talk to a unique server (e.g. internet provider server) and engage a 1-to-1 communication (e.g. url request) with the server from which they will all get their own individual answers (e.g. web page). In this particular case, the server is passive: the only thing it does is answer the clients in a 1-to-1 communication.
If there is no client, the server does nothing. If there is no server, the client returns an error.

Now let's imagine the reverse case where one wants to broadcast the same message to N listeners (each of them in a perfectly separate and independent environment/process/namespace), where N is subject to changing with time, and no matter if some of the listeners are launched, not launched (yet), or dropped.

This is a typical case where one needs a unique client to talk to several listening servers... and where the servers did themselves the "connection step" towards the broadcasting client... and where the client is broadcasting its messages even if no server is actually listening.

Well, my friend, you are stuck.

Actually not, because this is exactly what `hein` does: 1-Publisher to N-Subscriber ashynchronous socket communication, turn-key - check the example below.

NB: ``PyDispatcher``, ``Dispatch``, ``PyPubSub``, ``smokesignal`` or other similar libraries will get you to the point where several threads can talk to each other - that is great for some applications, but threads are not processes and you will be required to share the publisher object among subscribers: this is not an option when subscribers run in separate processes, possibly on different machines. ``ZeroMQ`` will get you to the point where you can talk between processes. However, all of the asynchronous heavy logistics is left for you to implement, and the socket connections will crash when a subscriber drops (unless you cover this case in your own implementation as well). Both of these tweaks are natively covered in ``hein``: minimal effort. Also, hein requires no deamon to be run.


Example
=======

Straight to the point: launch 3 terminals in which you should start an interactive python interpreter (not an IDE).

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

Now close one listener and type:

.. code-block:: python
    
    t.ping()

Only one listener is listed with the True (is connected) flag. Now let's try another one that keeps the type of the inputs:

.. code-block:: python

    from datetime import datetime
    import pytz
    
    t.tell_json({'string': 'hello', 'integer': 34, 'float': 13.4, 'd': datetime(2017, 12, 3, tzinfo=pytz.UTC)})

The receiver will get exactly the same thing:

.. code-block:: python

    {'integer': 34, 'float': 13.4, 'string': 'hello', 'd': datetime.datetime(2017, 12, 3, 0, 0, tzinfo=<UTC>)}


Obviously, the behavior at connection and reception is driven by callback functions, which by default only print the listener's names or the message transmitted.
All you will need now is write your own functions to replace these default callbacks.
That's it.

Note that, as you probably have seen when running the example/teaser, that the communication are natively non-blocking and asynchronous: no need to do the ennoying threading work yourself, `hein` library is turnkey solution (unlike ZeroMQ).

The best typical example of the use of hein is having several applications talking to each other: they are all busy doing their own things but still get messages from each other at the time their are sent (i.e. async, not at the time they are not busy anymore to process them).

Documentation
=============

Refer to this page for detailed API documentation, http://pythonhosted.org/hein/hein.html


Requirements
============

Hein requires the following Python packages:

* socket: Really?
* threading, select: for threading and port-reading
* time, os: for basic stuff
* byt: to handle chains of bytes identically no matter the python version
* pytz: optional, for handling datetime-timezones


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
