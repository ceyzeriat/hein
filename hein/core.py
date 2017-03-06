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


ESCAPE = Byt('\xee')
DICTSEPARATOR = Byt('\xac\xbd')
ESCAPEDDICTSEPARATOR = DICTSEPARATOR + ESCAPE
MESSAGEEND = Byt('\xac\x96')
ESCAPEDMESSAGEEND = MESSAGEEND + ESCAPE
DICTMAPPER = Byt(':')  # must a char that cannot be in a dict key

KEYLENGTH = 7
DIEKEY = Byt('__die__')
PINGKEY = Byt('__png__')
REPORTKEY = Byt('__rpt__')
RAWKEY = Byt('__raw__')
DICTKEY = Byt('__dic__')


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
    * the keys-values to merge into a socket-compatible string
    """
    ret = Byt()
    for k, v in kwargs.items():
        if not isinstance(v, (str, Byt)):
            v = str(v)
        abit = Byt(k) + DICTMAPPER + Byt(v)
        ret += abit.replace(DICTSEPARATOR, ESCAPEDDICTSEPARATOR)
        ret += DICTSEPARATOR*2
    return ret


def package_message(txt):
    """
    Escapes the message end flag in txt and adds it at the end
    """
    return txt.replace(MESSAGEEND, ESCAPEDMESSAGEEND) + MESSAGEEND*2


def split_flow(data, n=-1):
    """
    Splits messages from flow

    Args:
    * data (Byt): the data flow to split
    * n (int): how many packets should be splited, at maximum,
        set to -1 for all
    """
    res = data.split(MESSAGEEND*2, int(n))
    if len(res) <= 1:  # no split found
        return res
    # apply recovery of escaped chars to all splits found except last one
    return [item.replace(ESCAPEDMESSAGEEND, MESSAGEEND)\
                for item in res[:-1]]\
            + res[-1:]


def split_socket_info(data, asStr=False):
    """
    Splits the data using the socket separator and returns a dictionary
    of the different pieces in bytes format

    Args:
    * data (Byt): the data to split
    * asStr (bool): whether the dictionary-value should be returned as
        string, or Byt.
    """
    dic = {}
    for item in data.split(DICTSEPARATOR*2):
        k, v = item.replace(ESCAPEDDICTSEPARATOR, DICTSEPARATOR)\
                   .split(DICTMAPPER, 1)
        dic[str(k)] = str(v) if asStr else v
    return dic


def is_reporting(data):
    """
    Tells if the data is of reporting format

    Args:
    * data (Byt): the text to evaluate
    """
    socksep = DICTSEPARATOR * 2
    lsep = len(socksep)
    PROOF = Byt(REPORTKEY) + DICTMAPPER + Byt(1)
    # only and just reporting flag
    if data == PROOF:
        return True
    # start with report flag
    elif data[:len(PROOF)+lsep] == PROOF + socksep:
        return True
    return False






def merge_reporting(**kwargs):
    """
    Merges the data using the socket separator and returns a string
    """
    # remove the reporting key in case it is in the dictionary to merge
    del kwargs[REPORTKEY]
    res = merge_socket_info(**kwargs)
    # prepend the reporting key
    return Byt(REPORTKEY) + DICTMAPPER + Byt(1) + DICTSEPARATOR*2 + res