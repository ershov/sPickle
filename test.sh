#!/bin/bash

OUTPUT=$(./test.py | perl -npe 's/ with id=\d++//g')

SAMPLE_OUTPUT="{'a': 1,
 'b': {'c': 2, 'd': {'e'}},
 'g': None,
 'h': 'test',
 'i': 3.14,
 'j': [1, 2, 3],
 'k': (4, 5, 6)}
103
{'a': 1,
 'b': {'c': 2, 'd': {'e'}},
 'g': None,
 'h': 'test',
 'i': 3.14,
 'j': [1, 2, 3],
 'k': (4, 5, 6)}
98
(b'sP\x01s\x01ai\x02s\x01bs\x01ci\x04s\x01ds\x01eS\x01\x06D\x04\x03'
 b'\x04\x05\x07s\x01gns\x01hs\x04tests\x01id@\t\x1e\xb8Q\xeb\x85\x1fs\x01ji'
 b'\x06L\x03\x01\x04\x10s\x01ki\x08i\ni\x0cT\x03\x13\x14\x15D\x0e\x00\x01'
 b'\x02\x08\t\n\x0b\x0c\r\x0e\x0f\x11\x12\x16.\x17')
{'a': 1,
 'b': {'c': 2, 'd': {'e'}},
 'g': None,
 'h': 'test',
 'i': 3.14,
 'j': [1, 2, 3],
 'k': (4, 5, 6)}
Pickling of recursive objects is not implemented
{'a': 1,
 'b': {'c': 2, 'd': {'e'}, 'l': <Recursion on dict>},
 'g': None,
 'h': 'test',
 'i': 3.14,
 'j': [1, 2, 3],
 'k': (4, 5, 6)}
109
{'a': 1,
 'b': {'c': 2, 'd': {'e'}, 'l': <Recursion on dict>},
 'g': None,
 'h': 'test',
 'i': 3.14,
 'j': [1, 2, 3],
 'k': (4, 5, 6)}
Unsafe class <class '__main__.MyUnsafeClass'> pickled successfully
Attempting to unpickle unsafe class posix.system
Attempting to unpickle unsafe class posix.system
Unsafe class <class '__main__.MyUnsafeClass2'> pickled successfully
Attempting to unpickle unsafe class __main__.MyUnsafeClass2
Attempting to unpickle unsafe class __main__.MyUnsafeClass2"

if [[ "$OUTPUT" != "$SAMPLE_OUTPUT" ]]; then
    echo $'\nDiff:'
    diff -y --color=auto -L SAMPLE <(echo "$SAMPLE_OUTPUT") -L OUTPUT <(echo "$OUTPUT")
    exit 1
fi
