#!/bin/sh

version=$(python .build_utils/bump_version.py $(pwd)/pyproject.toml)
echo $version

rm -rf ./dist ./build
python -m build
twine upload ./dist/* -u __token__ -p $PYPI_KEY

push_git() {
	message="."
	if [ -n "$1" ]; then
		message="$@"
	fi
	git add -A && git commit -m "$message" && git tag "v${version}" && git push --follow-tags
}
push_git
