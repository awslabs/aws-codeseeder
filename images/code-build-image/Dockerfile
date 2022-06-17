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


# From the official CodeBuild Ubuntu Standard 5.0 image built locally
FROM aws/codebuild/standard

ARG BOTO_VERSION=1.21.37

RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get -y install nodejs

### AWS Tools

# Install EKSCTL
RUN curl --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp && \
    mv /tmp/eksctl /usr/local/bin

# Install KubeCTL
RUN curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x ./kubectl && mv ./kubectl /usr/local/bin/kubectl

# Install aws-iam-authenticator
# https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html
RUN curl -o aws-iam-authenticator https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/aws-iam-authenticator && \
    chmod +x ./aws-iam-authenticator && \
    mv ./aws-iam-authenticator /usr/local/bin

# Install Helm tools
RUN curl -sSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash && \
    helm version --short && \
    helm plugin install https://github.com/hypnoglow/helm-s3.git && \
    helm repo add stable https://charts.helm.sh/stable

RUN npm install -g yarn

RUN pip install boto3~=$BOTO_VERSION

RUN mkdir -p /var/scripts/
ADD retrieve_docker_creds.py /var/scripts/retrieve_docker_creds.py

ENTRYPOINT ["bash"]
