#!/usr/bin/env bash
set -e

ARCH="${ARCH:-amd64}"
DIST="${DIST:-jessie}"
BRANCH="${BRANCH:-master}"

BUILDAREA="/tmp/elasticmetrics-build"
HERE=`dirname $0`

if [ "$(git rev-parse --abbrev-ref HEAD)" != $BRANCH ]; then
    echo "You are not on the $BRANCH branch, aborting"
    exit 1
fi;

export VERSION=$(date "+%Y%m%d.%H%M%S")

echo "Generating package changelog"
gbp dch --debian-tag="%(version)s" --new-version=$VERSION --debian-branch $BRANCH --release --commit

echo "Building package for $DIST"


mkdir -p $BUILDAREA-$DIST
gbp buildpackage --git-pbuilder --git-export-dir=$BUILDAREA-$DIST --git-dist=$DIST --git-arch=$ARCH \
--git-debian-branch=$BRANCH --git-ignore-new


echo
echo "*************************************************************"
echo

echo "Creating tag $VERSION"
git tag $VERSION

echo "Now push the commit with the version update and the tag: git push; git push --tags"
