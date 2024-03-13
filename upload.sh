#!/bin/sh

version=$(python .build_utils/bump_version.py)
echo "Bumping version to $version"

rm -rf ./dist ./build
python -m build
twine upload ./dist/* -u __token__ -p $PYPI_KEY

push_git() {
	version=$(grep -oP '^version = "\K[0-9]+\.[0-9]+\.[0-9]+' ./pyproject.toml)
	message="."
	if [ -n "$1" ]; then
		message="$@"
	fi
	git add -A && git commit -m "$message" && git tag "v${version}" && git push --follow-tags
}
push_git
