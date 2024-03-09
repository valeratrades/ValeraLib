#!/bin/sh

#TODO: with sed add 1 to this value, then resource this script recursively once.
export UPLOAD_WITH_VERSION="1.0.2"

alias u="./upload.sh"

alias g="git add -A && git commit -m '.' && git push"

