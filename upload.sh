#!/bin/sh


last_modified_min_ago=$((($(date +%s) - $(date +%s -r ./pyproject.toml)) / 60))
if [ $last_modified_min_ago > 5 ]; then
	python .build_utils/bump_version.py
fi

rm -rf ./dist ./build
python -m build
twine upload ./dist/* -u __token__ -p $PYPI_KEY
