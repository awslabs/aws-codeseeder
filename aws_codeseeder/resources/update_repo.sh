#!/usr/bin/env bash

# set -ex

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

DOMAIN=$1
REPOSITORY=$2
MODULE_DIR=$3
PACKAGE=$4
IGNORE_TWINE_ERROR=${5:-1}  # Default is to return -1 on twine error (not ignorred)

cd ${DIR}/$MODULE_DIR \
    && echo "Changed directory to ${PWD}" \
    || echo "ERROR: Failed to change directory to ${PWD}"

VERSION=$(cat VERSION)
rm dist/* && echo "Removed dist/" || echo "No dist/ to delete"
rm build/* && echo "Removed build/" || echo "No build/ to delete"

aws codeartifact login --tool twine --domain ${DOMAIN} --repository ${REPOSITORY} \
    && echo "Logged in to codeartifact domain/repository: ${DOMAIN}/${REPOSITORY}" \
    || (echo "ERROR: Failed to login to codeartifact domain/repository: ${DOMAIN}/${REPOSITORY}"; exit 1)

aws codeartifact delete-package-versions \
    --domain ${DOMAIN} \
    --repository ${REPOSITORY} \
    --package ${PACKAGE} \
    --versions ${VERSION} \
    --format pypi \
    && echo "Deleted codeartifact package version: ${DOMAIN}/${REPOSITORY}/${PACKAGE}/${VERSION}" \
    || echo "Checked for codeartifact package version: ${DOMAIN}/${REPOSITORY}/${PACKAGE}/${VERSION}"

python setup.py bdist_wheel \
    && echo "Built python wheel" \
    || (echo "ERROR: Failed to build python wheel"; exit 1)
echo "Sleeping briefly"
sleep 3
twine upload --repository codeartifact dist/* \
    && echo "Twine upload successful" \
    || (echo "ERROR: Twine upload failed, this may be an eventual consistency issue (Try it again)"; exit ${IGNORE_TWINE_ERROR})
