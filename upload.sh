#!/bin/sh


last_modified_min_ago=$((($(date +%s) - $(date +%s -r ./pyproject.toml)) / 60))
if [ $last_modified_min_ago > 5 ]; then
	python .build_utils/bump_version.py
fi

rm -rf ./dist ./build
python -m build
twine upload ./dist/* -u __token__ -p $PYPI_KEY

push_git() {
	version=$(grep -oP '^version = "\K[0-9]+\.[0-9]+\.[0-9]+' ./pyproject.toml)
	message="."
	if [ -n "$1" ]; then
		message="$@"
	fi
	git add -A && git commit -m "$message" && git tag -a "v${version}" -m "v${version}" && git push
}
push_git
