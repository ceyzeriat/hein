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
import select
from byt import Byt


# acknowledgement character
ACK = Byt('\xaa')


# escape character
ESCAPE = Byt('\xee')
# split character for dictionaries between items
DICTSEPARATOR = Byt('\xac\xbd')
ESCAPEDDICTSEPARATOR = DICTSEPARATOR + ESCAPE
# end character of a communication
MESSAGEEND = Byt('\xac\x96')
ESCAPEDMESSAGEEND = MESSAGEEND + ESCAPE
# split character between key and value of a dictionary item
# must a character that cannot be in a dict key
DICTMAPPER = Byt(':')

# length of pre-pending keys - all must have the same length
KEYLENGTH = 7
# send this to kill a receiver
DIEKEY = Byt('__die__')
# send this to ping and test the health of a receiver
PINGKEY = Byt('__png__')
# send this followed with a report-type message
REPORTKEY = Byt('__rpt__')
# send this followed with a raw-type message
RAWKEY = Byt('__raw__')
# send this followed with a dictionary-type message
DICTKEY = Byt('__dic__')

# sending frequency in Hz
SENDBUFFERFREQ = 50


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
        try:
            return Byt(sock.recv(int(l)))
        except:
            sock.close()
            return None
    else:
        return None


def getAR(sock, timeout=1):
    """
    Checks for the acknowledgement on a socket

    Args:
      * sock (socket): the sock to listen to
      * timeout (float): the timeout in seconds
    """
    return receive(sock, l=len(ACK), timeout=timeout) == ACK


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
    Packages the message by adding the end character and escaping

    Args:
      * txt (Byt): the message to escape
    """
    return txt.replace(MESSAGEEND, ESCAPEDMESSAGEEND) + MESSAGEEND*2


def split_flow(data, n=-1):
    """
    Splits messages from flow and recovers escaped chars for all
    but the last one, being the remainder of the split operation

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


def split_socket_info(data):
    """
    Splits the data using the dictionary separator and returns a
    dictionary

    Args:
      * data (Byt): the data to split
    """
    dic = {}
    for item in data.split(DICTSEPARATOR*2):
        if len(item) == 0:
            continue
        k, v = item.replace(ESCAPEDDICTSEPARATOR, DICTSEPARATOR)\
                   .split(DICTMAPPER, 1)
        dic[str(k)] = v
    return dic
