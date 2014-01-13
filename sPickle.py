""" Safe pickle/unpickle """

from collections import namedtuple
import itertools
from struct import pack, unpack
from types import NoneType

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

#  len:
#		int -> constant length
#		True -> self-contained
#		None -> need to encode/decode via encode_len
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

def __construct_dict(elems):
	class Pairs:
		def __init__(self): self.idx = -1
		def __call__(self, _): self.idx += 1; return self.idx & 2
	return dict([(x[1].next(),x[1].next()) for x in itertools.groupby(elems, Pairs())])

# Encode small non-negative number
def encode_len(x, strm):
	assert x >= 0

	while x > 0x7F:
		strm.write(chr(x & 127))
		x >>= 7
	strm.write(chr(x | 0x80))

def encode_len_s(x):
	assert x >= 0

	ret = ""
	while x > 0x7F:
		ret += chr(x & 127)
		x >>= 7
	ret += chr(x | 0x80)
	return ret

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
	while (x & 0x80) == 0:
		ret |= (x << shift)
		x = ord(strm.read(1))
		shift += 7
	ret |= (x & 0x7F) << shift
	return ret

# Decode small number
def decode_small(strm):
	ret = decode_len(strm)
	sign = ret & 1
	ret = ret >> 1
	if sign:
		ret = -ret - 1
	return ret


# for encoding
t2i = {
	int:		PickleType('i', pack=encode_small_s, len=True,				unpack=decode_small),
	long:		PickleType('l', pack=encode_small_s, len=True,				unpack=decode_small),
	float:		PickleType('d', pack=lambda x:pack('>d', x), len=__float_len,unpack=lambda data:unpack(">d",data)[0] ),
	str:		PickleType('s', pack=lambda x:x,							unpack=lambda x:str(x)),
	unicode:	PickleType('u', pack=lambda x:x.encode('utf-8'),			unpack=lambda x:unicode(x,'utf-8')),
	buffer:		PickleType('f', pack=lambda x:x,							unpack=lambda x:buffer(x)),
	NoneType:	PickleType('n', pack=lambda x:"", len=0,					unpack=lambda _:None),
	bool:		PickleType('b', pack=lambda x:chr(x), len=1,				unpack=lambda x:bool(x)),

	dict:		PickleType('D', enumLive = __enum_dict,				construct=__construct_dict),
	set:		PickleType('S', enumLive = __enum_set,				construct=lambda x:set(x)),
	frozenset:	PickleType('F', enumLive = __enum_set,				construct=lambda x:frozenset(x)),
	list:		PickleType('L', enumLive = __enum_list,				construct=lambda x:list(x)),
	tuple:		PickleType('T', enumLive = __enum_list,				construct=lambda x:tuple(x)),
}

# for decoding
k2i = dict([(v.key, v) for k,v in t2i.items()])
del k,v

class StopType: KEY = '.'
STOP = StopType()
k2i[STOP.KEY] = STOP

MAGIC = "sP"

# memo: id -> index

def __dump_simple(obj, strm, typePickle):
	packed = typePickle.pack(obj)
	strm.write(typePickle.key)
	l = typePickle.len
	if l is None:			# Encode the length we got
		encode_len(len(packed), strm)
	# no need to encode if len is INT or True
	strm.write(packed)

def __dump(obj, strm, memo, circular):
	objId = id(obj)
	if objId in memo:
		return memo[id(obj)]

	typePickle = t2i[type(obj)]
	iterator = typePickle.enumLive

	if iterator is None:			# simple type
		memo[objId] = myIndex = len(memo)
		__dump_simple(obj, strm, typePickle)
		return myIndex

	assert objId not in circular
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
	if l is None:			# read length
		l = decode_len(strm)
		return typePickle.unpack(strm.read(l) if l > 0 else '')
	elif l is True:			# no length
		return typePickle.unpack(strm)
	else:					# l is integer
		return typePickle.unpack(strm.read(l) if l > 0 else '')

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
	objects = [memo[decode_len(strm)] for _ in xrange(l)]
	obj = typePickle.construct(objects)

	memo.append(obj)

	return obj
#

def dump(obj, file, protocol=0):
	file.write(MAGIC)
	encode_len(protocol, file)

	memo = dict()
	__dump(obj, file, memo, set())
	file.write(STOP.KEY)
	encode_len(memo[id(obj)], file)

def dumps(obj, protocol=None):
    file = StringIO()
    dump(obj, file)
    return file.getvalue()

def load(file):
	assert file.read(len(MAGIC)) == MAGIC
	protocol = decode_len(file)
	assert protocol == 0

	memo = []
	while __load1(file, memo) is not STOP:
		pass
	return memo[decode_len(file)]

def loads(str):
    file = StringIO(str)
    return load(file)


