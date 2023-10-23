#!/bin/sh

rm -rf ./dist ./build
python setup.py sdist bdist_wheel
twine upload ./dist/* -u __token__ -p $PYPI_KEY
