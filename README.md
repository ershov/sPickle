# restrictedpickle - Safe Pickle for Python

This is a safe version of Python's pickle module. It will only pickle and unpickle safe tyes like int, float, str, list, dict, etc. It will not unpickle malicious code. It is safe to use `restrictedpickle` on untrusted data.

This module is compatible standard pickle module. You can use `restrictedpickle` as a drop-in replacement for `pickle`.

## Installation

```bash
pip install restrictedpickle
```
