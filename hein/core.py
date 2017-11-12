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
from datetime import datetime
from datetime import date
from datetime import time
TZON = True
try:
    import pytz
except ImportError:
    TZON = False
try:
    unicode('')
except:
    unicode = str


# acknowledgement character
ACK = Byt('\x06')


# escape character
ESCAPE = Byt('\xee')
# split character for dictionaries between items
DICTSEPARATOR = Byt('\xac\xbd')
ESCAPEDDICTSEPARATOR = DICTSEPARATOR + ESCAPE
# split character between key and value of a dictionary item
# must a character that cannot be in a dict key
DICTMAPPER = Byt(':')
# split character between elements of a list
LISTSEPARATOR = Byt('\xac\xbd')
ESCAPEDLISTSEPARATOR = LISTSEPARATOR + ESCAPE
# end character of a communication
MESSAGEEND = Byt('\xac\x96')
ESCAPEDMESSAGEEND = MESSAGEEND + ESCAPE

# length of pre-pending keys - all must have the same length
KEYPADDING = Byt('__')
TINYKEYLENGTH = 3
KEYLENGTH = TINYKEYLENGTH + 2*len(KEYPADDING)
# send this to kill a receiver
DIEKEY = KEYPADDING + Byt('die') + KEYPADDING
# send this to ping and test the health of a receiver
PINGKEY = KEYPADDING + Byt('png') + KEYPADDING
# send this followed with a report-type message
REPORTKEY = KEYPADDING + Byt('rpt') + KEYPADDING
# send this followed with a raw-type message
RAWKEY = KEYPADDING + Byt('raw') + KEYPADDING
# send this followed with a dictionary-type message
DICTKEY = KEYPADDING + Byt('dic') + KEYPADDING
# send this followed with a dictionary-type message conserving types
DICTKEYTYPE = KEYPADDING + Byt('tdi') + KEYPADDING
BOOLCODE = Byt("b")
INTCODE = Byt("i")
FLOATCODE = Byt("f")
BYTESCODE = Byt("B")
NONECODE = Byt("N")
BYTCODE = Byt("Y")
DTCODE = Byt("t")
DATECODE = Byt("D")
TIMECODE = Byt("T")
UNICODE = Byt("u")
STRCODE = Byt("s")
# send this followed with a JSON-type message
JSONKEY = KEYPADDING + Byt('jsn') + KEYPADDING
# send this followed with a list-type message
LISTKEY = KEYPADDING + Byt('lst') + KEYPADDING
LISTKEYTYPE = KEYPADDING + Byt('tls') + KEYPADDING

# sending frequency in Hz
SENDBUFFERFREQ = 100


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
    if sock is not None:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()


def valtype2bytes(v):
    """Returns (type(v), value) both as Byt
    Works for any type in (int, float, bool, None, Byt, datetime,
        date, time) and string types in (Byt, unicode, str, bytes)
    Any other type will go through a repr call
    """
    if isinstance(v, Byt):
        return BYTCODE, v
    elif isinstance(v, bool):
        return BOOLCODE, Byt("1" if v else "0")
    elif isinstance(v, int):
        return INTCODE, Byt(repr(v))
    elif isinstance(v, float):
        return FLOATCODE, Byt(repr(v))
    elif v is None:
        return NONECODE, Byt()
    elif isinstance(v, datetime):
        return DTCODE, Byt("{:d},{:d},{:d},{:d},{:d},{:d},{:d},{}"\
                            .format(v.year, v.month, v.day, v.hour,
                                    v.minute, v.second, v.microsecond,
                                    getattr(v.tzinfo, "zone", "")))
    elif isinstance(v, date):
        return DATECODE, Byt("{:d},{:d},{:d}".format(v.year, v.month, v.day))
    elif isinstance(v, time):
        return TIMECODE, Byt("{:d},{:d},{:d},{:d},{}"\
                                .format(v.hour, v.minute, v.second,
                                        v.microsecond,
                                        getattr(v.tzinfo, "zone", "")))
    else:
        return any2bytes(v)


def any2bytes(v):
    """Returns (type(v), value) both as Byt
    Works for string types in (Byt, unicode, str, bytes)
    Any other type will go through a repr call
    """
    if isinstance(v, Byt):
        return BYTCODE, v
    elif isinstance(v, unicode):  # catches python3 str and python2 unicode
        return UNICODE, Byt(v.encode("utf-8"))
    elif isinstance(v, str):  # only python2 str reach here
        return STRCODE, Byt(v)
    elif isinstance(v, bytes):  # only python3 bytes here
        return BYTESCODE, Byt(v)
    else:
        v = repr(v)
        # catches python3 str and python2 unicode
        if isinstance(v, unicode):
            return UNICODE, Byt(v.encode("utf-8"))
        # only python2 str reach here
        return STRCODE, Byt(v)


def bytes2type(typ, v=Byt()):
    if typ == BOOLCODE:
        return bool(int(v))
    elif typ == INTCODE:
        return int(v)
    elif typ == FLOATCODE:
        return float(v)
    elif typ == BYTESCODE:  # only python3 bytes here as input
        return bytes(v)  # python2/3 latin-1
    elif typ == NONECODE:
        return None
    elif typ == BYTCODE:
        return v
    elif typ in (DTCODE, DATECODE, TIMECODE):
        l = v.split(Byt(','))
        tz = None
        if TZON and typ in (DTCODE, TIMECODE):
            tzpoped = l.pop(-1)
            if len(tzpoped) >0:
                tz = pytz.timezone(tzpoped)
        l = list(map(int, l))
        if typ in DATECODE:
            return date(*l[:3])
        elif typ in TIMECODE:
            return time(*l[:4], tzinfo=tz)
        elif typ in DTCODE:
            return datetime(*l[:7], tzinfo=tz)
    elif typ == UNICODE:
        return unicode(v)  # catches python3 str and python2 unicode
    elif typ == STRCODE:
        return bytes(v)  # only python2 str here as input, to python2/3 latin-1


def merge_socket_dict(*args, **kwargs):
    """
    Merges the data using the socket separator and returns a string

    Args:
      * 1st: bool, whether to add a repr-type indication to keep track of
        the type

    Kwargs:
      * the keys-values to merge into a socket-compatible string
    """
    ret = Byt()
    for k, v in kwargs.items():
        if not bool(args[0]):
            dum, v = any2bytes(v)
        else:
            typ, v = valtype2bytes(v)
            v = typ + DICTMAPPER + v
        abit = Byt(k) + DICTMAPPER + v
        ret += abit.replace(DICTSEPARATOR, ESCAPEDDICTSEPARATOR)
        ret += DICTSEPARATOR*2
    return ret


def split_socket_dict(typ, data):
    """
    Splits the data using the dictionary separator and returns a
    dictionary

    Args:
      * typ (bool): whether to retrieve the type from the data
      * data (Byt): the data to split
    """
    dic = {}
    for item in data.split(DICTSEPARATOR*2):
        if len(item) == 0:
            continue
        k, v = item.replace(ESCAPEDDICTSEPARATOR, DICTSEPARATOR)\
                   .split(DICTMAPPER, 1)
        if bool(typ):
            v = bytes2type(*v.split(DICTMAPPER, 1))
        dic[str(k)] = v
    return dic


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


def merge_socket_list(typ, *args):
    """
    Merges the data using the socket separator and returns a string

    Args:
      * typ (bool): whether to retrieve the type from the data
      * the values to merge into a socket-compatible string
    """
    ret = Byt()
    for v in args:
        if not typ:
            dum, v = any2bytes(v)
        else:
            typ, v = valtype2bytes(v)
            v = typ + DICTMAPPER + v
        ret += v.replace(LISTSEPARATOR, ESCAPEDLISTSEPARATOR)
        ret += LISTSEPARATOR*2
    return ret


def split_socket_list(typ, data):
    """
    Splits the data using the list separator and returns a
    list

    Args:
      * typ (bool): whether to retrieve the type from the data
      * data (Byt): the data to split
    """
    ret = []
    for item in data.split(LISTSEPARATOR*2):
        if len(item) == 0:
            continue
        item = item.replace(ESCAPEDLISTSEPARATOR, LISTSEPARATOR)
        if bool(typ):
            item = bytes2type(*item.split(DICTMAPPER, 1))
        ret.append(item)
    return ret
