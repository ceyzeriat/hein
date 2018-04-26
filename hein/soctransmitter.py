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
from multiprocessing import Manager
import json


from . import core


__all__ = ['SocTransmitter']


class SocTransmitter(object):
    def __init__(self, port, nreceivermax, start=True, portname="",
                 timeoutACK=1.):
        """Creates a transmitting socket to which receiving socket
        can listen.

        Args:
          * port (int): the communication socket-port
          * nreceivermax (int): the maximum amount of receivers that can
            listen. From 1 to 5.
          * start (bool): whether to start the broadcasting at
            initialization or not. If not, use ``start`` method
          * portname (str[15]): the name of the communicating port, for
            display purposes only
          * timeoutACK (float or None): the timeout duration in seconds
            to wait for the acknowledgement receipt, or ``None`` to
            disable it
        """
        self._running = False
        self.timeoutACK = None if timeoutACK is None else float(timeoutACK)
        self.port = int(port)
        self.portname = str(portname)[:15]
        self._nreceivermax = max(1, min(5, int(nreceivermax)))
        self.receivers = {}
        self._ping = Manager().Queue(maxsize=0)
        self.sending_buffer = []
        self.last_sent = 0.
        if start:
            self.start()

    def __str__(self):
        return "Socket transmitter on port {:d} name '{}' ({})"\
            .format(
                self.port,
                self.portname,
                'on' if self.running else 'off')

    __repr__ = __str__
    
    def start(self):
        """Initializes and starts the broadcasting on the communication
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
        """The number of receivers currently listening to the port.
        Note that the active receivers are updated at each communication
        and some receivers may have dropped since then
        """
        return len(self.receivers)

    @nreceivers.setter
    def nreceivers(self, value):
        return

    def _tell_receiver(self, name, txt, ping=False):
        self.receivers[name].sendall(txt)
        # no ACK mode
        if self.timeoutACK is None:
            if ping:
                # requested a ping, so give a bool anyway
                return core.getAR(self.receivers[name])
            else:
                return None
        elif not core.getAR(self.receivers[name], timeout=self.timeoutACK):
            return self._dropped(name=name)
        return True
   
    def _dropped(self, name):
        """Called-back function when a receiver did not send the
        acknowledgement within the timeout period.
        Default behavior is drop the receiver and return False (used to
        populate the answer of a ping call)
        
        Can be overriden, although ``name`` parameter is mandatory
        """
        del self.receivers[name]
        return False

    def _tell(self, txt, key, tag=None, unpack=True):
        """Does the real preparation and sending of the message
        """
        if not self.running:
            return False
        tag = core._EMPTY if tag is None\
            else Byt(core.clean_name(str(tag)[:core.TAGLEN]))
        extra = tag + core.DICTMAPPER\
                + (core._ONE if unpack else core._ZERO) + core.DICTMAPPER
        self.sending_buffer.append((key + extra + core.package_message(txt),
                                    key == core.PINGKEY))
        return True

    def tell_raw(self, txt, tag=None):
        """Broadcasts a raw message

        Args:
          * txt (Byt or str): the message
          * tag (str[15] or None): a key to indicate the kind of
            message transmitted
        """
        if not isinstance(txt, core.STRINGTYPES):
            return False
        if not len(txt) > 0:
            return False
        txt = core.base_type2bytes(txt, keep_typ=False, json=False)
        return self._tell(txt=txt, key=core.RAWKEY, tag=tag, unpack=False)

    def tell(self, v, tag=None, unpack=True):
        """Broadcasts an extended-json variable, cross-compatible
        between python 2 and 3

        Supported types:
          * structure: list, dict
          * numerical: int, float
          * base: bool, None
          * time: datetime, date, time (with timezones if pytz is
            available),
          * string: Byt, unicode, str, bytes
    
        Args:
          * v: the variable to send
          * tag (str[15] or None): a key to indicate the kind of
            message transmitted
          * unpack (bool): whether the message will be automatically
            decoded upon reception
        """
        v = core.json_dumps(v)
        return self._tell(txt=v, key=core.JSONKEY, tag=tag, unpack=unpack)

    def tell_dict(self, *args, **kwargs):
        """DEPRECATED, use tell instead
        Broadcasts a dictionary-type message

        Kwargs:
          * the keys-values to merge into a socket-compatible string
        """
        print("tell_dict is deprecated, use tell instead")
        return False

    def tell_dict_type(self, *args, **kwargs):
        """DEPRECATED, use tell instead
        """
        print("tell_dict_type is deprecated, use tell instead")
        return False

    def tell_json(self, *args, **kwargs):
        """DEPRECATED, use tell instead
        """
        print("tell_json is deprecated, use tell instead")
        return False

    def tell_list(self, *args, **kwargs):
        """DEPRECATED, use tell instead
        """
        print("tell_list is deprecated, use tell instead")
        return False

    def tell_list_type(self, *args, **kwargs):
        """DEPRECATED, use tell instead
        """
        print("tell_list_type is deprecated, use tell instead")
        return False

    def tell_json_ext(self, *args, **kwargs):
        """DEPRECATED, use tell instead
        """
        print("tell_json_ext is deprecated, use tell instead")
        return False

    def tell_key(self, *args, **kwargs):
        """DEPRECATED, use tell instead
        """
        print("tell_key is deprecated, use tell instead")
        return False

    def tell_report(self, *args, **kwargs):
        """DEPRECATED, use tell instead
        """
        print("tell_report is deprecated, use tell instead")
        return False

    def ping(self):
        """Pings all receivers to check their health, updates the
        receivers list and returns the result
        """
        self._tell(txt=core._EMPTY, key=core.PINGKEY)
        ping_res = self._ping.get()
        self._ping.task_done()
        return ping_res

    def close_receivers(self):
        """Forces all receivers to drop listening
        """
        self._tell(txt=core._EMPTY, key=core.DIEKEY)
        for k, v in list(self.receivers.items()):
            core.killSock(v)
            del self.receivers[k]

    def close(self):
        """Shuts the broadcasting down, and forces all receivers to
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
        """Whether the broadcasting is active or not
        """
        return self._running

    @running.setter
    def running(self, value):
        pass

    def _newconnection(self, name):
        """Call-back function when a new connection
        is extablished

        Can be overriden, although ``name`` parameter is mandatory
        """
        print('hello: {}'.format(name))


def send_buffer(self):
    """Infinite loop sending messages
    """
    ALMOST = 0.85
    while self.running:
        # make a list-copy
        lines_to_send = list(self.sending_buffer)
        if len(lines_to_send) == 0:
            time.sleep(0.0001)
            # process might have died in between
            if time is None:
                break
            continue
        # too many lines to send.. gotta merge some to keep up
        elif len(lines_to_send) >= ALMOST*core.SENDBUFFERFREQ:
            # average amount of lines to be merged
            avg_join = int(len(lines_to_send) / (ALMOST * core.SENDBUFFERFREQ))
            # make init copy
            new_lines_to_send = [[lines_to_send[0][0], lines_to_send[0][1], 1]]
            # loop to merge
            for line, ping in lines_to_send[1:]:
                # if not ping and not previously ping and below average merge
                if not (ping or new_lines_to_send[-1][1]\
                        or new_lines_to_send[-1][2] > avg_join):
                    new_lines_to_send[-1][0] += line
                    new_lines_to_send[-1][2] += 1
                else:  # just add new line
                    new_lines_to_send.append([line, ping, 1])
            # copy it back
            lines_to_send = new_lines_to_send
        # iterate on lines
        for item in lines_to_send:
            # merged lines have a thrid argument, default 1
            line, ping = item[:2]
            cnt = item[2] if len(item) > 2 else 1
            t = time.time()
            # in case of ping, init
            ping_res = {}
            # make a list-copy
            for name, receiver in list(self.receivers.items()):
                ping_res[name] = self._tell_receiver(name, line, ping)
            if ping:
                self._ping.put(ping_res)
            # remove lines, possibly several if merged
            for i in range(cnt):
                del self.sending_buffer[0]
            # wait for the right time to go on
            while time.time()-t < 0.99 / core.SENDBUFFERFREQ:
                time.sleep(0.1/core.SENDBUFFERFREQ)
                # process might have died in between
                if time is None:
                    break
        else:
            self.last_sent = time.time()
            continue


def accept_receivers(self):
    """Infinite loop registering all new receivers
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
            name = str(name)
            if name in self.receivers:  # reciever already has such name
                if self.ping().get(name, False):  # still active
                    # refuse new connection
                    core.killSock(receiver)
                else:  # not active anymore.. replace old connection
                    # close broken socket
                    core.killSock(self.receivers.get(name))
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
