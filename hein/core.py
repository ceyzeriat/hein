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
import json
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


# basic encoding
ENCODING = "utf-8"

# escape character
ESCAPE = Byt('\xee')
# split character for dictionaries between items
DICTSEPARATOR = Byt('\xac\xbd')
DDICTSEPARATOR = DICTSEPARATOR*2
ESCAPEDDICTSEPARATOR = DICTSEPARATOR + ESCAPE
# split character between key and value of a dictionary item
# must a character that cannot be in a dict key
DICTMAPPER = Byt(':')
# split character between elements of a list
LISTSEPARATOR = Byt('\xac\xbd')
DLISTSEPARATOR = LISTSEPARATOR*2
ESCAPEDLISTSEPARATOR = LISTSEPARATOR + ESCAPE
# end character of a communication
MESSAGEEND = Byt('\xac\x96')
DMESSAGEEND = MESSAGEEND*2
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
# send this with a dictionary-type message
DICTKEY = KEYPADDING + Byt('dic') + KEYPADDING
# send this with a dictionary-type message conserving types
DICTKEYTYPE = KEYPADDING + Byt('tdi') + KEYPADDING
BOOLCODE = Byt("b")
INTCODE = Byt("i")
FLOATCODE = Byt("f")
BYTESCODE = Byt("y")
NONECODE = Byt("n")
BYTCODE = Byt("Y")
DTCODE = Byt("t")
DATECODE = Byt("D")
TIMECODE = Byt("T")
UNICODE = Byt("u")
STRCODE = Byt("s")
# send this with a JSON-type message
JSONKEY = KEYPADDING + Byt('jsn') + KEYPADDING
JSONXKEY = KEYPADDING + Byt('jxn') + KEYPADDING
# send this with a list-type message
LISTKEY = KEYPADDING + Byt('lst') + KEYPADDING
LISTKEYTYPE = KEYPADDING + Byt('tls') + KEYPADDING

_EMPTY = Byt("")
_SPACE = Byt(" ")
_ONE = Byt("1")
_ZERO = Byt("0")
_QUOTE = Byt('"')
_COLON = Byt(":")
_QUOTECOLON = _QUOTE + _COLON
_ESC = Byt('\\')
_ESCQUOTE = _ESC + _QUOTE
_COMMA = Byt(',')
_CURLYL = Byt('{')
_CURLYR = Byt('}')
_BRACKETL = Byt('[')
_BRACKETR = Byt(']')

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
      * sock (socket): the socket to kill
    """
    if sock is not None:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()


def esc_quote(v):
    """Returns a "-escaped string, for json-representation

    Args:
      * v (Byt): the string to escape
    """
    return v.replace(_QUOTE, _ESCQUOTE)


def extended_type2bytes(v, keep_typ, jsonX=False):
    """Returns a bytes representation of v

    Args:
      * v: the value to transform
      * keep_type (bool): whether to keep track of the type of v in
        the output

    Note:
      * Works with types in (int, float, bool, None, Byt, datetime,
        date, time (with timezones if pytz is available)) and string
        types in (Byt, unicode, str, bytes)
      * Any other type will undergo a repr() call
    """
    if isinstance(v, datetime):
        data = Byt("{:d},{:d},{:d},{:d},{:d},{:d},{:d},{}"\
                    .format(v.year, v.month, v.day, v.hour,
                            v.minute, v.second, v.microsecond,
                            getattr(v.tzinfo, "zone", "")))
        if keep_typ:
            return DTCODE + DICTMAPPER + data
        return data
    elif isinstance(v, date):
        data = Byt("{:d},{:d},{:d}".format(v.year, v.month, v.day))
        if keep_typ:
            return DATECODE + DICTMAPPER + data
        return data
    elif isinstance(v, time):
        data = Byt("{:d},{:d},{:d},{:d},{}"\
                    .format(v.hour, v.minute, v.second,
                            v.microsecond,
                            getattr(v.tzinfo, "zone", "")))
        if keep_typ:
            return TIMECODE + DICTMAPPER + data
        return data
    else:
        return base_type2bytes(v, keep_typ, jsonX)


def base_type2bytes(v, keep_typ, jsonX=False):
    """Returns a bytes representation of v

    Args:
      * v: the value to transform
      * keep_type (bool): whether to keep track of the type of v in
        the output

    Note:
      * Works with types in (int, float, bool, None, Byt) and string
        types in (Byt, unicode, str, bytes)
      * Any other type will undergo a repr() call
    """
    if isinstance(v, Byt):
        if jsonX:
            v = esc_quote(v)
        if keep_typ:
            return BYTCODE + DICTMAPPER + v
        return v
    elif isinstance(v, bool):
        data = _ONE if v else _ZERO
        if keep_typ:
            return BOOLCODE + DICTMAPPER + data
        return data
    elif isinstance(v, int):
        if keep_typ:
            return INTCODE + DICTMAPPER + Byt(repr(v))
        return Byt(repr(v))
    elif isinstance(v, float):
        if keep_typ:
            return FLOATCODE + DICTMAPPER + Byt(repr(v))
        return Byt(repr(v))
    elif v is None:
        if keep_typ:
            return NONECODE + DICTMAPPER
        return _EMPTY
    # catches python3 str and python2 unicode
    elif isinstance(v, unicode):
        data = Byt(v.encode(ENCODING))
        if jsonX:
            data = esc_quote(data)
        if keep_typ:
            return UNICODE + DICTMAPPER + data
        return data
    # only python2 str reach here
    elif isinstance(v, str):
        data = Byt(v)
        if jsonX:
            data = esc_quote(data)
        if keep_typ:
            return STRCODE + DICTMAPPER + data
        return data
    # only python3 bytes here
    elif isinstance(v, bytes):
        data = Byt(v)
        if jsonX:
            data = esc_quote(data)
        if keep_typ:
            return BYTESCODE + DICTMAPPER + data
        return data
    else:
        data = repr(v)
        # catches python3 str and python2 unicode
        if isinstance(data, unicode):
            code = UNICODE
            data = data.encode(ENCODING)
        # only python2 str reach here
        else:
            code = STRCODE
        if jsonX:
            data = esc_quote(data)
        if keep_typ:
            return code + DICTMAPPER + data
        return data

def bytes2type(v):
    typ, v = Byt(v).split(DICTMAPPER, 1)
    if typ == BOOLCODE:
        return bool(int(v))
    elif typ == INTCODE:
        return int(v)
    elif typ == FLOATCODE:
        return float(v)
    # only python3 bytes here as input
    elif typ == BYTESCODE:
        # python2/3 ASCII (latin-1)
        return bytes(v)
    elif typ == NONECODE:
        return None
    elif typ == BYTCODE:
        return v
    elif typ in (DTCODE, DATECODE, TIMECODE):
        l = v.split(Byt(','))
        tz = None
        if typ in (DTCODE, TIMECODE):
            tzpoped = l.pop(-1)
            if len(tzpoped) > 0:
                if TZON:
                    tz = pytz.timezone(tzpoped)
                else:
                    print("WARNING: the timezone information '{}' was not "\
                          "understood because pytz could not be imported"\
                          .format(tzpoped))
        l = [int(item) if item != _EMPTY else 0 for item in l]
        if typ in DATECODE:
            return date(*l[:3])
        elif typ in TIMECODE:
            return time(*l[:4], tzinfo=tz)
        elif typ in DTCODE:
            return datetime(*l[:7], tzinfo=tz)
    # catches python3 str and python2 unicode
    elif typ == UNICODE:
        return unicode(v)
    # only python2 str here as input, to python2/3 latin-1
    elif typ == STRCODE:
        return bytes(v)


def package_message(txt):
    """
    Packages the message by adding the end character and escaping

    Args:
      * txt (Byt): the message to escape
    """
    return txt.replace(MESSAGEEND, ESCAPEDMESSAGEEND) + DMESSAGEEND


def split_flow(data, n=-1):
    """
    Splits messages from flow and recovers escaped chars for all
    but the last one, being the remainder of the split operation

    Args:
      * data (Byt): the data flow to split
      * n (int): how many packets should be splited, at maximum,
        set to -1 for all

    """
    res = data.split(DMESSAGEEND, int(n))
    if len(res) <= 1:  # no split found
        return res
    # apply recovery of escaped chars to all splits found except last one
    return [item.replace(ESCAPEDMESSAGEEND, MESSAGEEND)\
                for item in res[:-1]]\
            + res[-1:]


def jsonX_loads(data):
    """Loads an extended json string

    Args:
      * data (Byt or str): the raw extended-json string to unpack
    """
    def unpack(d):
        if isinstance(d, (list, tuple)):
            return [unpack(item) for item in d]
        elif isinstance(d, dict):
            return dict([(str(k), unpack(v)) for k, v in d.items()])
        else:
            return bytes2type(d)
    data = json.loads(str(data))
    return unpack(data)


def jsonX_dumps(data):
    """Dumps an extended json variable

    Args:
      * data: the variable to dump to json
    """
    if isinstance(data, (list, tuple)):
        ret = _BRACKETL
        ret += _COMMA.join([jsonX_dumps(item) for item in data])
        ret += _BRACKETR
        return ret
    elif isinstance(data, dict):
        ret = _CURLYL
        ret += _COMMA.join([_QUOTE + Byt(k) + _QUOTECOLON + jsonX_dumps(v)\
                                for k, v in data.items()])
        ret += _CURLYR
        return ret
    else:
        return _QUOTE\
            + esc_quote(extended_type2bytes(data, keep_typ=True, jsonX=True))\
            + _QUOTE


def merge_socket_dict(keep_typ, dico):
    """
    Merges the data using the socket separator and returns a string

    Args:
      * keep_typ: bool, whether to keep track of the types of values
      * dico (dict): the keys-values to merge into a socket-compatible string
    """
    ret = Byt()
    for k, v in dico.items():
        abit = Byt(k) + DICTMAPPER + extended_type2bytes(v, keep_typ)
        ret += abit.replace(DICTSEPARATOR, ESCAPEDDICTSEPARATOR)
        ret += DDICTSEPARATOR
    return ret


def split_socket_dict(keep_typ, data):
    """
    Splits the data using the dictionary separator and returns a
    dictionary

    Args:
      * keep_typ (bool): whether to retrieve the type from the data
      * data (Byt): the data to split
    """
    dic = {}
    for item in data.split(DDICTSEPARATOR):
        if len(item) == 0:
            continue
        k, v = item.replace(ESCAPEDDICTSEPARATOR, DICTSEPARATOR)\
                   .split(DICTMAPPER, 1)
        if keep_typ:
            v = bytes2type(v)
        dic[str(k)] = v
    return dic


def merge_socket_list(keep_typ, lst):
    """
    Merges the data using the socket separator and returns a string

    Args:
      * keep_typ (bool): whether to retrieve the type from the data
      * the values to merge into a socket-compatible string
    """
    ret = Byt()
    for v in lst:
        v = extended_type2bytes(v, keep_typ)
        ret += v.replace(LISTSEPARATOR, ESCAPEDLISTSEPARATOR)
        ret += DLISTSEPARATOR
    return ret


def split_socket_list(keep_typ, data):
    """
    Splits the data using the list separator and returns a
    list

    Args:
      * keep_typ (bool): whether to retrieve the type from the data
      * data (Byt): the data to split
    """
    ret = []
    for item in data.split(DLISTSEPARATOR):
        if len(item) == 0:
            continue
        item = item.replace(ESCAPEDLISTSEPARATOR, LISTSEPARATOR)
        if keep_typ:
            item = bytes2type(item)
        ret.append(item)
    return ret
