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
from string import Template
from typing import List, Optional

import yaml
from cfn_flip import yaml_dumper
from cfn_tools import load_yaml

from aws_codeseeder import CLI_ROOT, LOGGER, create_output_dir
from aws_codeseeder.services import get_account_id, get_region

FILENAME = "template.yaml"
RESOURCES_FILENAME = os.path.join(CLI_ROOT, "resources", FILENAME)


def synth(
    seedkit_name: str,
    *,
    deploy_id: Optional[str] = None,
    managed_policy_arns: Optional[List[str]] = None,
    deploy_codeartifact: bool = False,
) -> str:
    out_dir = create_output_dir("seedkit")
    output_filename = os.path.join(out_dir, FILENAME)

    LOGGER.debug("Reading %s", RESOURCES_FILENAME)
    with open(RESOURCES_FILENAME, "r") as file:
        input_template = load_yaml(file)

    if managed_policy_arns:
        input_template["Resources"]["CodeBuildRole"]["Properties"]["ManagedPolicyArns"] += managed_policy_arns

    if not deploy_codeartifact:
        del input_template["Resources"]["CodeArtifactDomain"]
        del input_template["Resources"]["CodeArtifactRepository"]
        del input_template["Outputs"]["CodeArtifactDomain"]
        del input_template["Outputs"]["CodeArtifactRepository"]

    output_template = Template(yaml.dump(input_template, Dumper=yaml_dumper.get_dumper()))

    LOGGER.debug("Writing %s", output_filename)
    os.makedirs(out_dir, exist_ok=True)
    with open(output_filename, "w") as file:
        file.write(
            output_template.safe_substitute(
                seedkit_name=seedkit_name,
                account_id=get_account_id(),
                region=get_region(),
                deploy_id=deploy_id if deploy_id else "".join(random.choice(string.ascii_lowercase) for i in range(6)),
                role_prefix="/",
            )
        )

    return output_filename
