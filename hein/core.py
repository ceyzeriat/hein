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
import re
import sys
TZON = True
try:
    import pytz
except ImportError:
    TZON = False
try:
    unicode
except:
    unicode = str


__all__ = ['Message']


# acknowledgement character
ACK = Byt('\x06')


# basic encoding
ENCODING = "utf-8"

# escape character
ESCAPE = Byt('\xee')
# split character between key and value of a dictionary item
# must a character that cannot be in a dict key
DICTMAPPER = Byt(':')
# end character of a communication
MESSAGEEND = Byt('\xac\x96')
DMESSAGEEND = MESSAGEEND*2
ESCAPEDMESSAGEEND = MESSAGEEND + ESCAPE

# maximum tag length
TAGLEN = 15

# length of pre-pending keys - all must have the same length
KEYPADDING = Byt('__')
TINYKEYLENGTH = 3
KEYLENGTH = TINYKEYLENGTH + 2*len(KEYPADDING)
# send this to kill a receiver
DIEKEY = KEYPADDING + Byt('die') + KEYPADDING
# send this to ping and test the health of a receiver
PINGKEY = KEYPADDING + Byt('png') + KEYPADDING
# send this followed with a raw-type message
RAWKEY = KEYPADDING + Byt('raw') + KEYPADDING
# send this with a JSON-type message
JSONKEY = KEYPADDING + Byt('jsn') + KEYPADDING

# tags for type conservation
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

ALLOWCHAR = re.compile('[^a-zA-Z\.\-_0-9 ]')

STRINGTYPES = (unicode, Byt, str, bytes)

PYTHON3 = sys.version_info > (3,)


def receive(sock, l=16, timeout=1.):
    """
    Listens to a socket and returns a chain of bytes, or ``None``

    Args:
      * sock (socket): the sock to listen to
      * l (int): the length of the message to read
      * timeout (float): the timetout in second
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


def getAR(sock, timeout=1.):
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


def clean_name(txt):
    """Returns a cleaned up name
    """
    return ALLOWCHAR.sub('', txt)


def extended_type2bytes(v, keep_typ, json=False):
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
        return base_type2bytes(v, keep_typ, json)


def base_type2bytes(v, keep_typ, json=False):
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
        if json:
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
        if json:
            data = esc_quote(data)
        if keep_typ:
            return UNICODE + DICTMAPPER + data
        return data
    # only python2 str reach here
    elif isinstance(v, str):
        data = Byt(v)
        if json:
            data = esc_quote(data)
        if keep_typ:
            return STRCODE + DICTMAPPER + data
        return data
    # only python3 bytes here
    elif isinstance(v, bytes):
        data = Byt(v)
        if json:
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
        data = Byt(data)
        if json:
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
            # last argument is TZ, and pytz needs a str here
            tzpoped = str(l.pop(-1))
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


def json_loads(data):
    """Loads an extended json string

    Args:
      * data (Byt or str): the raw extended-json string to unpack
    """
    def unpack(d):
        if isinstance(d, (list, tuple)):
            return [unpack(item) for item in d]
        elif isinstance(d, dict):
            return dict((str(k), unpack(v)) for k, v in d.items())
        else:
            return bytes2type(d)
    if PYTHON3:
        return unpack(json.loads(str(data), strict=False))
    else:
        return json.loads(str(data), cls=NoUTFUnpacker)


def json_dumps(data):
    """Dumps an extended json variable

    Args:
      * data: the variable to dump to json
    """
    if isinstance(data, (list, tuple)):
        ret = _BRACKETL
        ret += _COMMA.join([json_dumps(item) for item in data])
        ret += _BRACKETR
        return ret
    elif isinstance(data, dict):
        ret = _CURLYL
        ret += _COMMA.join([_QUOTE + Byt(k) + _QUOTECOLON + json_dumps(v)\
                                for k, v in data.items()])
        ret += _CURLYR
        return ret
    else:
        return _QUOTE\
            + esc_quote(extended_type2bytes(data, keep_typ=True, json=True))\
            + _QUOTE


class Message(object):
    def __init__(self, v):
        self._raw = v
        self._message = None

    def __repr__(self):
        return str(self.message)

    __str__ = __repr__

    @property
    def raw(self):
        """The raw message
        """
        return self._raw

    @raw.setter
    def raw(self, value):
        return

    @property
    def message(self):
        """Unpack the message
        """
        if self._message is None:
            self._message = json_loads(self.raw)
        return self._message

    @message.setter
    def message(self, value):
        return


class NoUTFUnpacker(json.JSONDecoder):
    MATCH = re.compile('x([0-9a-fA-F]{2,2})')

    XHEX = dict(
        (chr(l), chr(l) if 31 < l < 128 else 'x{:0>2}'.format(hex(l)[2:]))\
            for l in range(256))

    REV_XHEX = dict((v, k) for k, v in XHEX.items())

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook,
            *args, **kwargs)

    def object_hook(self, obj):
        def unpack(d):
            if isinstance(d, (list, tuple)):
                return [unpack(item) for item in obj]
            elif isinstance(d, dict):
                return dict((str(k), unpack(v)) for k, v in d.items())
            else:
                d = self.MATCH.sub(
                        lambda x: self.REV_XHEX[x.group()],
                        str(d))
                d = d.replace('x/', 'x')
                return bytes2type(d)
        return unpack(obj)

    def raw_decode(self, s, idx=0):
        s = s.replace('x', 'x/')
        s = ''.join([self.XHEX[l] for l in s])
        s = json.JSONDecoder.raw_decode(self, s=s, idx=idx)
        return s
