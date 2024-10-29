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
(b'sP\x80s\x81ai\x82s\x81bs\x81ci\x84s\x81ds\x81eS\x81\x86D\x84\x83'
 b'\x84\x85\x87s\x81gns\x81hs\x84tests\x81id@\t\x1e\xb8Q\xeb\x85\x1fs\x81ji'
 b'\x86L\x83\x81\x84\x90s\x81ki\x88i\x8ai\x8cT\x83\x93\x94\x95D\x8e\x80\x81'
 b'\x82\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x91\x92\x96.\x97')
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
