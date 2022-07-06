#!/usr/bin/env bash
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

set -ex

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${DIR}
source ./vars.sh

aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${PUBLIC_ECR_ADDRESS}

docker build --tag ${REPOSITORY}:${VERSION} .
docker tag ${REPOSITORY}:${VERSION} ${PUBLIC_ECR_ADDRESS}/${REPOSITORY}:${VERSION}
docker push ${PUBLIC_ECR_ADDRESS}/${REPOSITORY}:${VERSION}

docker tag ${REPOSITORY}:${VERSION} ${PUBLIC_ECR_ADDRESS}/${REPOSITORY}:latest
docker push ${PUBLIC_ECR_ADDRESS}/${REPOSITORY}:latest
