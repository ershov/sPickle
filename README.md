# restrictedpickle - Safe Pickle for Python

This is a safe version of Python's pickle module. It will only pickle and unpickle safe tyes like int, float, str, list, dict, etc. It will not unpickle malicious code. It is safe to use `restrictedpickle` on untrusted data.

This module is compatible standard pickle module. You can use `restrictedpickle` as a drop-in replacement for `pickle`.

## Installation

```bash
pip install restrictedpickle
```

## Usage

```python
import restrictedpickle.classic as pickle

data = {'a': 1, 'b': 2}
data_serialized = pickle.dumps(data)
data_unserialized = pickle.loads(data_serialized)
assert data == data_unserialized
```
