#!/bin/sh
# File is sourced on `cs` into the project's root. Allows to define a set of project-specific commands and aliases.

u() {
	version=$(python ${HOME}/s/help_scripts/bump_version.py $(pwd)/pyproject.toml $1) || { return 1; }

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
}
