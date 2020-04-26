#!/bin/bash

# bash script to make the release-process more consistent
# it attempts to do the following things:
#   1. update what version() returns
#   2. add every commit-title since the last tag to CHANGELOG
#   3. update requirements.txt
#   4. commit both those changes
#   5. tag the release-commit with the release-tag
# should an error occur, some of the changes will be rolled back automatically

# print to stderr
# $1 = error message
function err() {
    echo "ERROR: $1" >&2
}

# roll back some potential changes in case of an error
# $1 = relative path to project root
function reset() {
    echo "rolling back changes"

    rm $1/CHANGELOG.tmp
    git checkout $1/CHANGELOG
    git checkout $1/app/version.py
    git checkout $1/requirements.txt
}

# change what version() returns
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

# add all commits since last tag to changelog
# $1 = relative path to project root
# $2 = new version / tag
function make_changelog() {
    echo "adding entries to changelog"

    # get last tag on this branch
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

    # prepend new changelog to a new temporary changelog file (omit first line)
    (echo -e "# Changelog\n\n" && echo -e "## Version $2 (released $(date +%F))\n" && echo "$(git log --pretty=format:'%s' $last_tag..HEAD | sed 's/^/* /')" && sed '1d' $CLOG) > $CLOG.tmp

    if [[ $? -ne 0 ]]; then
        err "addition to $CLOG.tmp failed"
        reset $1
        exit 1
    fi

    echo "    added git log to $CLOG.tmp"

    # replace old changelog with new changelog file
    mv $CLOG.tmp $CLOG

    if [[ $? -ne 0 ]]; then
        err "overriding $CLOG failed"
        reset $1
        exit 1
    fi

    echo "    replaced $CLOG"
}

# update requirements.txt
# $1 = relative Path to project root
function update_requirements() {
    echo "updating requirements"
    # grep out pkg-resources=0.0.0 which is a bug on certain systems
    pip freeze | grep -v "pkg-resources" > requirements.txt

    if [[ $? -ne 0 ]]; then
        err "updating requirements failed"
        reset $1
        exit 1
    fi
}

# make a release commit
# $1 = relative Path to project root
# $2 = new version
function make_commit() {
    echo "making commit for $2"
    msg="Increase Version to $2, add Changelog"
    git add $1/app/version.py
    git add $1/CHANGELOG
    git add $1/requirements.txt
    git commit -sm "$msg"

    if [[ $? -ne 0 ]]; then
        err "git commit returned an error"
        reset $1
        exit 1
    fi
}

# tag the release commit
# $1 = new version/tag
function make_tag() {
    git tag $1

    if [[ $? -ne 0 ]]; then
        err "git tag failed"
        exit 1
    fi
}

### MAIN ###
# check that new version tag was $1
if [[ "$#" -ne 1 ]]; then
    err "not enough parameters"
    echo "usage: $0 new_version_tag"
    exit 1
fi

# check runpath by trying to find CHANGELOG
# only running this tool from the project root or ./devtools works
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
update_requirements $P
make_commit $P $V
make_tag $V

echo 'done'
