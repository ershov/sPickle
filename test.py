#!/usr/bin/env python3

import sys, os
from pprint import pprint
import pickle as stdpickle
import restrictedpickle as rp
import restrictedpickle.classic as pickle

def test():
    a = {}
    a['a'] = 1
    a['b'] = {}
    a['b']['c'] = 2
    a['b']['d'] = {'e'}
    a['g'] = None
    a['h'] = 'test'
    a['i'] = 3.14
    a['j'] = [1, 2, 3]
    a['k'] = (4, 5, 6)

    pickle1 = pickle.dumps(a)
    restore1 = pickle.loads(pickle1)

    pickle2 = rp.sPickle.dumps(a)
    restore2 = rp.sPickle.loads(pickle2)

    pprint(a)
    print(len(pickle1))
    pprint(restore1)
    # pprint(pickle1)
    print(len(pickle2))
    pprint(pickle2)
    pprint(restore2)

def test_recursive():
    a = {}
    a['a'] = 1
    a['b'] = {}
    a['b']['c'] = 2
    a['b']['d'] = {'e'}
    a['g'] = None
    a['h'] = 'test'
    a['i'] = 3.14
    a['j'] = [1, 2, 3]
    a['k'] = (4, 5, 6)
    a['b']['l'] = a['b']

    pickle1 = pickle.dumps(a)
    restore1 = pickle.loads(pickle1)

    try:
        pickle2 = rp.sPickle.dumps(a)
        print("sPickle supports recursive objects")
    except rp.sPickle.PicklingError as e:
        print(e)

    pprint(a)
    print(len(pickle1))
    pprint(restore1)
    # pprint(restore2)

class MyUnsafeClass:
    def __reduce__(self):
        return (os.system, ("echo 'Hello, world!'",))

class MyUnsafeClass2:
    pass

def test_unsafe(obj):
    a = {}
    a['x'] = {}
    a['y'] = obj
    try:
        pickle1 = pickle.dumps(a)
        print(f"Unsafe class {type(obj)} pickled successfully")
        restore1 = pickle.loads(pickle1)
        print(f"Unsafe class {type(obj)} unpickled successfully")
    except (pickle.PicklingError, pickle.UnpicklingError) as e:
        print(e)
    pickle1 = stdpickle.dumps(a)
    try:
        restore1 = pickle.loads(pickle1)
        print(f"Unsafe class {type(obj)} unpickled successfully")
    except pickle.UnpicklingError as e:
        print(e)

def main():
    test()
    test_recursive()
    test_unsafe(MyUnsafeClass())
    test_unsafe(MyUnsafeClass2())

if __name__ == "__main__":
    main()
