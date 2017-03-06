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
from byt import Byt


# acknowledgement character
ACK = Byt('\xaa')


SOCKETDICTSEPARATOR = Byt('\xac\xbd')
SOCKETDICTESCAPE = Byt('\xee')
SOCKETDICTMAPPER = Byt(':')  # must a char that cannot be in a dict key
SOCKETDICTESCAPEDSEPARATOR = SOCKETDICTSEPARATOR + SOCKETDICTESCAPE
REPORTKEY = Byt('__report__')
DIEKEY = Byt('__die__')
PINGKEY = Byt('__ping__')
RAWKEY = Byt('__raw__')


def receive(sock, l=16, timeout=1.):
    """
    Listens to a socket and returns a chain of bytes, or ``None``

    Args:
    * sock (socket): the sock to listen to
    * l (int): the length of the message to read
    * timeout (float): the timetout
    """
    ready = select.select([sock], [], [], timeout)
    if ready[0]:
        return Byt(sock.recv(int(l)))
    else:
        return None

def getAR(sock, timeout=0.1):
    """
    Checks for the acknowledgement on a socket

    Args:
    * sock (socket): the sock to listen to
    * timeout (float): the timeout in seconds
    """
    return receive(sock, l=len(core.ACK), timeout=timeout) == core.ACK

def killSock(sock):
    """
    Shuts down and closes a socket

    Args:
    * sock (socket): the sock to kill
    """
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

def merge_socket_info(**kwargs):
    """
    Merges the data using the socket separator and returns a string

    Kwargs:
    * the keys to merge into a socket-compatible string
    """
    ret = Byt()
    for k, v in kwargs.items():
        if not isStr(v):
            v = str(v)
        abit = Byt(k) + SOCKETMAPPER + Byt(v)
        ret += abit.replace(SOCKETSEPARATOR, SOCKETSEPARATOR+SOCKETESCAPE)
        ret += SOCKETSEPARATOR*2
    return ret
