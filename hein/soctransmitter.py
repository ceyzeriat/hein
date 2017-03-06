#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  
#  HEIN - Advanced Subscriber-Publisher Socket Communication
#  Copyright (C) 2017  Guillaume Schworer
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  
#  For any information, bug report, idea, donation, hug, beer, please contact
#    guillaume.schworer@gmail.com
#
###############################################################################


import socket
from threading import Thread
import select
import time
from byt import Byt

from . import core


__all__ = ['SocTransmitter']


class SocTransmitter(object):
    def __init__(self, port, nreceivermax, start=True, portname=""):
        """
        Creates a transmitting socket to which receiving socket
        can listen.

        Args:
        * port (int): the communication port
        * nreceivermax (int): the maximum amount of receivers that can
          listen. From 1 to 5.
        * start (bool): whether to start the broadcasting at
          initialization or not. If not, use ``start`` method
        * portname (str[15]): the name of the communicating port, for
          identification purposes
        """
        self._running = False
        self.port = int(port)
        self.portname = str(portname)[:15]
        self._nreceivermax = max(1, min(5, int(nreceivermax)))
        self.receivers = {}
        self.sending_buffer = []
        if start:
            self.start()

    def __str__(self):
        return "Socket transmitter on port {:d} ({})".format(
            self.port,
            'on' if self.running else 'off')

    __repr__ = __str__
    
    def start(self):
        """
        Initializes and starts the broadcasting on the communication
        port, if not already started.
        """
        if self.running:
            return
        self._soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._soc.setblocking(0)
        self._soc.bind(('', self.port))
        self._soc.listen(self._nreceivermax)
        self._running = True
        loopy = Thread(target=accept_receivers, args=(self,))
        loopy.daemon = True
        loopy.start()
        loopy = Thread(target=send_buffer, args=(self,))
        loopy.daemon = True
        loopy.start()

    @property
    def nreceivers(self):
        """
        The number of receivers currently listening to the port.
        Note that the active receivers are updated at each communication
        and some receivers may have dropped since then
        """
        return len(self.receivers)

    @nreceivers.setter
    def nreceivers(self, value):
        return

    def _tell_receiver(self, name, receiver, txt):
        try:
            receiver.getpeername()
        except:
            return
        receiver.sendall(txt)
        if not core.getAR(receiver):
            del self.receivers[name]

    def _tell(self, txt, key):
        """
        Does the real preparation and sending of the message
        """
        if not self.running:
            return False
        self.sending_buffer.append(key + core.package_message(txt))
        return True

    def tell_raw(self, txt):
        """
        Broadcasts a raw-type message

        Args:
        * txt (Byt or str): the message
        """
        if not len(txt) > 0:
            return False
        return self._tell(Byt(txt), core.RAWKEY)

    def tell_dict(self, **kwargs):
        """
        Broadcasts a dictionary-type message

        Kwargs:
        * the keys-values to merge into a socket-compatible string
        """
        if not len(kwargs) > 0:
            return False
        return self._tell(core.merge_socket_info(**kwargs), core.DICTKEY)

    def tell_report(self, **kwargs):
        """
        Broadcasts a dictionary-type message

        Kwargs:
        * the keys-values to merge into a socket-compatible string
        """
        if not len(kwargs) > 0:
            return False
        return self._tell(core.merge_socket_info(**kwargs), core.REPORTKEY)

    def close_receivers(self):
        """
        Forces all receivers to drop listening
        """
        self._tell('', DIEKEY)
        for idx, item in enumerate(list(self.receivers)):
            core.killSock(item)
            del self.receivers[idx]

    def close(self):
        """
        Shuts the broadcasting down, and forces all receivers to
        drop listening. The broadcasting can be restarted using
        ``start``.
        """
        if not self.running:
            return
        self._running = False
        self.sending_buffer = []
        self.close_receivers()
        core.killSock(self._soc)

    @property
    def running(self):
        """
        Whether the broadcasting is active or not
        """
        return self._running

    @running.setter
    def running(self, value):
        pass

    def _newconnection(self, name):
        """
        Call-back function when a new connection
        is extablished

        Can be overriden, although ``name`` parameter is mandatory
        """
        print('hello: {}'.format(name))


def send_buffer(self):
    """
    Infinite loop sending messages
    """
    while self.running:
        # make a list-copy
        for line in list(self.sending_buffer):
            # make a list-copy
            for name, receiver in list(self.receivers.items()):
                self._tell_receiver(name, receiver, line)
            del self.sending_buffer[0]
            time.sleep(0.03)
            # process might have died in between
            if time is None:
                break
        time.sleep(0.001)
        # process might have died in between
        if time is None:
            break


def accept_receivers(self):
    """
    Infinite loop registering all new receivers
    """
    while self.running:
        receiver = None
        # blocking with 1 sec timeout
        ready = select.select([self._soc], [], [], 1)
        if ready[0]:
            # should be a new connection here, but just in case...
            try:
                receiver, addr = self._soc.accept()
            except:
                continue
        else:
            continue
        # maybe _soc broke while select
        if not self.running:
            core.killSock(receiver)
            break
        upToLimit = False
        if self.nreceivers >= self._nreceivermax:
            # maybe replace old droped connection with new one
            upToLimit = True
        receiver.send(core.ACK)
        name = core.receive(receiver, l=15, timeout=5.)
        if name is not None:
            if name in self.receivers:  # replace old connection
                # close broken socket
                core.killSock(self.receivers[name])
                receiver.send(core.ACK)
                self.receivers[name] = receiver
                self._newconnection(name)
            else:  # name does not exist already
                if not upToLimit:
                    receiver.send(core.ACK)
                    self.receivers[name] = receiver
                    self._newconnection(name)
                else:
                    core.killSock(receiver)
        else:
            core.killSock(receiver)
