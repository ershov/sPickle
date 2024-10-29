""" Safe pickle/unpickle """

from collections import namedtuple
import itertools
from struct import pack, unpack
from types import NoneType
import dataclasses, enum

import io

VERSION = "0.3.0"

class PickleError(Exception): pass
class PicklingError(PickleError): pass
class UnpicklingError(PickleError): pass

#  len:
#       int -> constant length
#       True -> self-contained
#       None -> need to encode/decode via encode_len
PickleType = namedtuple('PickleType', ['key', 'enumLive', 'len', 'pack', 'unpack', 'construct'])
# add default constructor params
PickleType.__new__.__defaults__ = (None,)*len(PickleType._fields)

def __enum_dict(x):
    for i in sorted(x.items(), key=lambda a:a[0]):
        yield i[0]
        yield i[1]

def __enum_set(x):
    for i in sorted(list(x)):
        yield i

def __enum_list(x):
    for i in x:
        yield i

__int_len = len(pack("<i",0))
__float_len = len(pack("<d",0.))

# Construct a dictionary from a flat list of key-value pairs
def __construct_dict(elems):
    return dict([(elems[i], elems[i+1]) for i in range(0, len(elems), 2)])
    # class Pairs:
    #     def __init__(self): self.idx = -1
    #     def __call__(self, _): self.idx += 1; return self.idx & 2
    # return dict([(x[1].next(),x[1].next()) for x in itertools.groupby(elems, Pairs())])

# Encode small non-negative number
def encode_len(x, strm):
    assert x >= 0

    while x > 0x7F:
        strm.write(pack("B", (x & 127) | 0x80))
        x >>= 7
    strm.write(pack("B", x))

def encode_len_s(x):
    assert x >= 0

    ret = []
    while x > 0x7F:
        ret.append(pack("B", (x & 127) | 0x80))
        x >>= 7
    ret.append(pack("B", x))
    return b"".join(ret)

# Encode small number
def encode_small(x, strm):
    if x < 0:
        sign = 1
        x = -x - 1
    else:
        sign = 0
    x = x*2 + sign
    encode_len(x, strm)

def encode_small_s(x):
    if x < 0:
        sign = 1
        x = -x - 1
    else:
        sign = 0
    x = x*2 + sign
    return encode_len_s(x)

# Decode small non-negative number
def decode_len(strm):
    ret = 0
    shift = 0
    x = ord(strm.read(1))
    while (x & 0x80) != 0:
        ret |= ((x & 0x7F) << shift)
        x = ord(strm.read(1))
        shift += 7
    ret |= x << shift
    return ret

# Decode small number
def decode_small(strm):
    ret = decode_len(strm)
    sign = ret & 1
    ret = ret >> 1
    if sign:
        ret = -ret - 1
    return ret

def encode_uint8(x, strm):
    strm.write(pack("B", x & 0xFF))
    # strm.write(chr(x & 0xFF))
def encode_uint8_s(x):
    return pack("B", x & 0xFF)
    # return chr(x & 0xFF)

# for encoding
t2i = {
    int:        PickleType(b'i', pack=encode_small_s, len=True,              unpack=decode_small),
    # long:     PickleType(b'l', pack=encode_small_s, len=True,              unpack=decode_small),
    float:      PickleType(b'd', pack=lambda x:pack('>d', x), len=__float_len,unpack=lambda data:unpack(">d",data)[0] ),
    str:        PickleType(b's', pack=lambda x:str.encode(x),                            unpack=lambda x:x.decode("utf-8")),
    # unicode:  PickleType(b'u', pack=lambda x:x.encode('utf-8'),            unpack=lambda x:unicode(x,'utf-8')),
    # buffer:       PickleType(b'f', pack=lambda x:x,                            unpack=lambda x:buffer(x)),
    bytes:      PickleType(b'b', pack=lambda x:x,                            unpack=lambda x:x),
    NoneType:   PickleType(b'n', pack=lambda x:b"", len=0,                    unpack=lambda _:None),
    bool:       PickleType(b'b', pack=lambda x:pack("B", int(x)), len=1,                unpack=lambda x:bool(x)),
    # bool:       PickleType(b'b', pack=lambda x:chr(x), len=1,                unpack=lambda x:bool(x)),

    dict:       PickleType(b'D', enumLive = __enum_dict,             construct=__construct_dict),
    set:        PickleType(b'S', enumLive = __enum_set,              construct=lambda x:set(x)),
    frozenset:  PickleType(b'F', enumLive = __enum_set,              construct=lambda x:frozenset(x)),
    list:       PickleType(b'L', enumLive = __enum_list,             construct=lambda x:list(x)),
    tuple:      PickleType(b'T', enumLive = __enum_list,             construct=lambda x:tuple(x)),
}

# for decoding
k2i = dict([(v.key, v) for k,v in t2i.items()])
# del k, v

class StopType: KEY = b'.'
STOP = StopType()
k2i[STOP.KEY] = STOP

def _class_construct(classmodule, classname, *args):
    from importlib import import_module
    return getattr(import_module(classmodule), classname)(*args)
    # import sys
    # __import__(classmodule, level=0)
    # module = sys.modules[classmodule]
    # classobj = _getattribute(module, classname)[0]
    # return classobj(*args)

def _class_enumLive(val, enum_fn):
    classtype = type(val)
    yield classtype.__module__
    yield classtype.__name__
    yield from enum_fn(val)

enum_pickle = PickleType(b'E',
                         enumLive = lambda x: _class_enumLive(x, lambda _: (yield x.value)),
                         construct = lambda x: _class_construct(*x))

k2i[enum_pickle.key] = enum_pickle

def _enum_dataclass(x):
    for field in dataclasses.fields(x):
        # yield field.name
        yield getattr(x, field.name)

dataclass_pickle = PickleType(b'C',
                              enumLive = lambda x: _class_enumLive(x, _enum_dataclass),
                              construct = lambda x: _class_construct(*x))

k2i[dataclass_pickle.key] = dataclass_pickle

MAGIC = b"sP"

def _get_pickle_type(obj):
    objtype = type(obj)
    if objtype in t2i:
        return t2i[objtype]
    if dataclasses.is_dataclass(obj):
        return dataclass_pickle
    if isinstance(obj, enum.Enum):
        return enum_pickle
    if isinstance(obj, list):
        return t2i[list]
    if isinstance(obj, tuple):
        return t2i[tuple]
    return None

# memo: id -> index

def __dump_simple(obj, strm, typePickle):
    packed = typePickle.pack(obj)
    strm.write(typePickle.key)
    l = typePickle.len
    if l is None:           # Encode the length we got
        encode_len(len(packed), strm)
    # no need to encode if len is INT or True
    if len(packed):
        strm.write(packed)

def __dump(obj, strm, memo, circular):
    objId = id(obj)
    if objId in memo:
        return memo[id(obj)]

    if not (typePickle := _get_pickle_type(obj)):
        raise PicklingError(f"Cannot pickle value of type {type(obj)}")

    if not (iterator := typePickle.enumLive):     # simple type
        memo[objId] = myIndex = len(memo)
        __dump_simple(obj, strm, typePickle)
        return myIndex

    if objId in circular:
        raise PicklingError("Pickling of recursive objects is not implemented")
        # return __dump(None, strm, memo, circular)
    # assert objId not in circular
    circular.add(objId)

    objects = []
    for i in iterator(obj):
        objects.append(__dump(i, strm, memo, circular))

    strm.write(typePickle.key)
    encode_len(len(objects), strm)
    for i in objects:
        encode_len(i, strm)

    memo[objId] = myIndex = len(memo)
    circular.discard(objId)
    return myIndex

# memo: index -> object

def __load_simple(strm, typePickle):
    l = typePickle.len
    if l is None:           # read length
        l = decode_len(strm)
        return typePickle.unpack(strm.read(l) if l > 0 else b'')
    elif l is True:         # no length
        return typePickle.unpack(strm)
    else:                   # l is integer
        return typePickle.unpack(strm.read(l) if l > 0 else b'')

def __load1(strm, memo):
    key = strm.read(1)
    typePickle = k2i[key]

    if typePickle is STOP:
        return STOP

    if typePickle.unpack:
        obj = __load_simple(strm, typePickle)
        memo.append(obj)
        return obj

    l = decode_len(strm)
    objects = [memo[decode_len(strm)] for _ in range(l)]
    obj = typePickle.construct(objects)

    memo.append(obj)

    return obj

# Public API

def dump(obj, file, protocol=1):
    if protocol != 1:
        raise PicklingError("Unsupported protocol version")
    file.write(MAGIC)
    encode_len(protocol, file)

    memo = dict()
    __dump(obj, file, memo, set())
    file.write(STOP.KEY)
    encode_len(memo[id(obj)], file)

def dumps(obj, protocol=None):
    file = io.BytesIO()
    dump(obj, file)
    return file.getvalue()

def load(file):
    if file.read(len(MAGIC)) != MAGIC:
        raise UnpicklingError("Invalid pickle file")
    protocol = decode_len(file)
    if protocol != 1:
        raise UnpicklingError("Unsupported protocol version")

    memo = []
    while __load1(file, memo) is not STOP:
        pass
    return memo[decode_len(file)]

def loads(str):
    file = io.BytesIO(str)
    return load(file)

