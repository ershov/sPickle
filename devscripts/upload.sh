#!/bin/bash
. .venv/bin/activate
twine check dist/* && twine upload dist/*
