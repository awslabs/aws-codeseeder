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

from aws_codeseeder import LOGGER, cfn_toolkit
from aws_codeseeder.services import cfn, s3


def deploy_toolkit(toolkit_name: str, managed_policy_arns: Optional[List[str]]) -> None:
    stack_name: str = cfn.get_stack_name(toolkit_name=toolkit_name)
    LOGGER.info("Deploying Toolkit %s with Stack Name %s", toolkit_name, stack_name)
    LOGGER.debug("Managed Policy Arns: %s", managed_policy_arns)
    deploy_id: Optional[str] = None
    stack_exists, stack_outputs = cfn.does_stack_exist(stack_name=stack_name)
    if stack_exists:
        deploy_id = stack_outputs.get("DeployId")
        LOGGER.info("Toolkit found with DeployId: %s", deploy_id)
    template_filename: str = cfn_toolkit.synth(
        toolkit_name=toolkit_name, deploy_id=deploy_id, managed_policy_arns=managed_policy_arns
    )
    cfn.deploy_template(stack_name=stack_name, filename=template_filename, toolkit_tag=f"codeseeder-{toolkit_name}")
    LOGGER.info("Toolkit Deployed")


def destroy_toolkit(toolkit_name: str) -> None:
    stack_name: str = cfn.get_stack_name(toolkit_name=toolkit_name)
    LOGGER.info("Destroying Toolkit %s with Stack Name %s", toolkit_name, stack_name)
    stack_exists, stack_outputs = cfn.does_stack_exist(stack_name=stack_name)
    if stack_exists:
        toolkit_bucket = stack_outputs.get("Bucket")
        if toolkit_bucket:
            s3.delete_bucket(bucket=toolkit_bucket)
        cfn.destroy_stack(stack_name=stack_name)
        LOGGER.info("Toolkit Destroyed")
    else:
        LOGGER.warn("Toolkit/Stack does not exist")
