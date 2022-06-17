#!/bin/bash
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

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";
ROOT_DIR="$SCRIPT_DIR/.."
CODEBUILD_IMAGE_DIR="${ROOT_DIR}/images/code-build-image"
CODEBUILD_IMAGE_VERSION=`cat $CODEBUILD_IMAGE_DIR/VERSION`

mkdir -p "${ROOT_DIR}/tmp"

cd "${ROOT_DIR}/tmp/aws-codebuild-docker-images/ubuntu/standard/5.0"

git clone https://github.com/aws/aws-codebuild-docker-images.git

docker build -t aws/codebuild/standard .

cd "${ROOT_DIR}/images/code-build-image"

docker build -t codeseeder-codebuild-image .

docker tag codeseeder-codebuild-image public.ecr.aws/v3o4w1g6/aws-codeseeder/code-build-base:latest
docker tag codeseeder-codebuild-image public.ecr.aws/v3o4w1g6/aws-codeseeder/code-build-base:$CODEBUILD_IMAGE_VERSION

docker push public.ecr.aws/v3o4w1g6/aws-codeseeder/code-build-base:latest
docker push public.ecr.aws/v3o4w1g6/aws-codeseeder/code-build-base:$CODEBUILD_IMAGE_VERSION

rm -rf "${ROOT_DIR}/tmp/"