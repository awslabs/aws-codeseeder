#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from typing import List, Optional

from aws_codeseeder import LOGGER, cfn_seedkit
from aws_codeseeder.services import cfn, s3


def deploy_seedkit(seedkit_name: str, managed_policy_arns: Optional[List[str]]) -> None:
    """Deploy seedkit resources (Bucket, KMS Key, Role, Policy, CodeBuild Project) into the environment

    :param seedkit_name: Name of the seedkit to deploy. All resources will include this in their naming conventions
    :type seedkit_name: str
    :param managed_policy_arns: List of Managed Policy to ARNs to attach to the default IAM Role created and used
        by the CodeBuild Project
    :type managed_policy_arns: Optional[List[str]]
    """
    stack_name: str = cfn.get_stack_name(seedkit_name=seedkit_name)
    LOGGER.info("Deploying Seedkit %s with Stack Name %s", seedkit_name, stack_name)
    LOGGER.debug("Managed Policy Arns: %s", managed_policy_arns)
    deploy_id: Optional[str] = None
    stack_exists, stack_outputs = cfn.does_stack_exist(stack_name=stack_name)
    if stack_exists:
        deploy_id = stack_outputs.get("DeployId")
        LOGGER.info("Seedkit found with DeployId: %s", deploy_id)
    template_filename: str = cfn_seedkit.synth(
        seedkit_name=seedkit_name, deploy_id=deploy_id, managed_policy_arns=managed_policy_arns
    )
    cfn.deploy_template(stack_name=stack_name, filename=template_filename, seedkit_tag=f"codeseeder-{seedkit_name}")
    LOGGER.info("Seedkit Deployed")


def destroy_seedkit(seedkit_name: str) -> None:
    """Destroys the seedkit resources (Bucket, KMS Key, Role, Policy, CodeBuild Project)

    :param seedkit_name: Name of the seedkit to destroy.
    :type seedkit_name: str
    """
    stack_name: str = cfn.get_stack_name(seedkit_name=seedkit_name)
    LOGGER.info("Destroying Seedkit %s with Stack Name %s", seedkit_name, stack_name)
    stack_exists, stack_outputs = cfn.does_stack_exist(stack_name=stack_name)
    if stack_exists:
        seedkit_bucket = stack_outputs.get("Bucket")
        if seedkit_bucket:
            s3.delete_bucket(bucket=seedkit_bucket)
        cfn.destroy_stack(stack_name=stack_name)
        LOGGER.info("Seedkit Destroyed")
    else:
        LOGGER.warn("Seedkit/Stack does not exist")
