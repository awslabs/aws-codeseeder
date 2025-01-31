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

import os
import random
import string
import sys
from string import Template
from typing import Any, Callable, Dict, List, Optional, Union

import yaml
from boto3 import Session
from cfn_flip import yaml_dumper
from cfn_tools import load_yaml

from aws_codeseeder import CLI_ROOT, LOGGER, create_output_dir

FILENAME = "template.yaml"
RESOURCES_FILENAME = os.path.join(CLI_ROOT, "resources", FILENAME)


def synth(
    seedkit_name: str,
    *,
    deploy_id: Optional[str] = None,
    managed_policy_arns: Optional[List[str]] = None,
    deploy_codeartifact: bool = False,
    session: Optional[Union[Callable[[], Session], Session]] = None,
    vpc_id: Optional[str] = None,
    subnet_ids: Optional[List[str]] = None,
    security_group_ids: Optional[List[str]] = None,
    permissions_boundary_arn: Optional[str] = None,
    synthesize: bool = False,
    **kwargs: Dict[str, Any],
) -> Optional[str]:
    deploy_id = deploy_id if deploy_id else "".join(random.choice(string.ascii_lowercase) for i in range(6))
    out_dir = create_output_dir(f"seedkit-{deploy_id}")
    output_filename = os.path.join(out_dir, FILENAME)
    kwargs = {} if kwargs is None else kwargs

    LOGGER.debug("Reading %s", RESOURCES_FILENAME)
    with open(RESOURCES_FILENAME, "r") as file:
        input_template = load_yaml(file)

    if managed_policy_arns:
        input_template["Resources"]["CodeBuildRole"]["Properties"]["ManagedPolicyArns"] += managed_policy_arns

    if vpc_id and subnet_ids and security_group_ids:
        vpcConfig = {"VpcId": vpc_id, "SecurityGroupIds": security_group_ids, "Subnets": subnet_ids}
        input_template["Resources"]["CodeBuildProject"]["Properties"]["VpcConfig"] = vpcConfig

    if not deploy_codeartifact:
        del input_template["Resources"]["CodeArtifactDomain"]
        del input_template["Resources"]["CodeArtifactRepository"]
        del input_template["Outputs"]["CodeArtifactDomain"]
        del input_template["Outputs"]["CodeArtifactRepository"]

    if permissions_boundary_arn:
        input_template["Resources"]["CodeBuildRole"]["Properties"]["PermissionsBoundary"] = permissions_boundary_arn

    role_prefix = kwargs.get("role_prefix", "/")
    policy_prefix = kwargs.get("policy_prefix", "/")

    output_template = Template(yaml.dump(input_template, Dumper=yaml_dumper.get_dumper()))
    template = output_template.safe_substitute(
        seedkit_name=seedkit_name,
        deploy_id=deploy_id,
        role_prefix=role_prefix,
        policy_prefix=policy_prefix,
    )

    if not synthesize:
        LOGGER.debug("Writing %s", output_filename)
        os.makedirs(out_dir, exist_ok=True)
        with open(output_filename, "w") as file:
            file.write(template)
        return output_filename
    else:
        sys.stdout.write(template)
        return None
