#!/bin/bash

# $1 = error message
function err() {
    echo "ERROR: $1" >&2
}

# $1 = relative path to project root
function reset() {
    echo "rolling back changes"

    rm $1/CHANGELOG.tmp
    git checkout $1/CHANGELOG
    git checkout $1/app/version.py
}

# $1 = relative path to project root
# $2 = new version
function change_version() {
    echo "changing version in $1/app/version.py"

    sed -i "s/return.*/return \"$2\"/" $1/app/version.py

    if [[ $? -ne 0 ]]; then
        err "sed failed"
        reset $1
        exit 1
    fi
}

# $1 = relative path to project root
# $2 = new version / tag
function make_changelog() {
    echo "adding entries to changelog"

    last_tag=$(git describe --abbrev=0 --tags)

    if [[ $? -ne 0 ]]; then
        err "could not get previous tag"
        exit 1
    fi

    echo "    found previous tag $last_tag"

    CLOG=$1/CHANGELOG

    if [[ ! -f "$CLOG" ]]; then
        err "could not find changelog at $CLOG"
        exit 1
    fi

    echo "    found $CLOG"

    (echo -e "# Changelog\n\n" && echo -e "## Version $2 (released $(date +%F))\n" && echo "$(git log --pretty=format:'%s' $last_tag..HEAD | sed 's/^/* /')" && sed '1d' $CLOG) > $CLOG.tmp

    if [[ $? -ne 0 ]]; then
        err "addition to $CLOG.tmp failed"
        reset $1
        exit 1
    fi

    echo "    added git log to $CLOG.tmp"

    mv $CLOG.tmp $CLOG

    if [[ $? -ne 0 ]]; then
        err "overriding $CLOG failed"
        reset $1
        exit 1
    fi

    echo "    replaced $CLOG"
}

# $1 = relative Path to project root
# $2 = new version
function make_commit() {
    echo "making commit for $2"
    msg="Increase Version to $2, add Changelog"
    git commit -asm "$msg"

    if [[ $? -ne 0 ]]; then
        err "git commit returned an error"
        reset $1
        exit 1
    fi
}

# $1 = new version/tag
function make_tag() {
    git tag $1

    if [[ $? -ne 0 ]]; then
        err "git tag failed"
        exit 1
    fi
}

# check that new version tag was $1
if [[ "$#" -ne 1 ]]; then
    err "not enough parameters"
    echo "usage: $0 new_version_tag"
    exit 1
fi

if [[ ! -f CHANGELOG ]]; then
    if [[ -f ../CHANGELOG ]]; then
        P=..
    else
        err "could not determine run-path"
        echo "hint: run either from root or ./devtools"
        exit 1
    fi
else
    P=.
fi

V=$1
echo "making new release for version $V..."

change_version $P $V
make_changelog $P $V
make_commit $P $V
make_tag $V

echo 'done'
