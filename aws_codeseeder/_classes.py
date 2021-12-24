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

import dataclasses
import enum
from typing import Any, Callable, Dict, List, Optional, cast

from mypy_extensions import KwArg, NamedArg, VarArg


class ModuleImporterEnum(str, enum.Enum):
    CODESEEDER_CLI = "codeseeder-cli"
    OTHER = "other"


@dataclasses.dataclass()
class CodeSeederConfig:
    """Configuration dataclass

    Parameters
    ----------
    timeout : Optional[int], optional
        Set the CodeBuild execution timeout, by default 30
    python_modules : Optional[List[str]], optional
        List of python modules to install during CodeBuild exection, by default None
    local_modules : Optional[Dict[str, str]], optional
        Name and Location of local python modules to bundle and install during CodeBuild execution,
        by default None
    requirements_files : Optional[Dict[str, str]], optional
        Local requirements.txt files to bundle and install during CodeBuild execution, by default None
    codebuild_image : Optional[str], optional
        Alternative container image to use during CodeBuild execution, by default None
    codebuild_role : Optional[str], optional
        Alternative IAM Role to use during CodeBuild execution, by default None
    codebuild_environment_type : Optional[str], optional
        Alternative Environment to use for the CodeBuild execution (e.g. LINUX_CONTAINER), by default None
    codebuild_compute_type : Optional[str], optional
        Alternative Compute to use for the CodeBuild execution (e.g. BUILD_GENERAL1_SMALL), by default None
    install_commands : Optional[List[str]], optional
        Commands to execute during the Install phase of the CodeBuild execution, by default None
    pre_build_commands : Optional[List[str]], optional
        Commands to execute during the PreBuild phase of the CodeBuild execution, by default None
    build_commands : Optional[List[str]], optional
        Commands to execute during the Build phase of the CodeBuild execution, by default None
    post_build_commands : Optional[List[str]], optional
        Commands to execute during the PostBuild phase of the CodeBuild execution, by default None
    dirs : Optional[Dict[str, str]], optional
        Name and Location of local directories to bundle and include in the CodeBuild exeuction,by default None
    files : Optional[Dict[str, str]], optional
        Name and Location of local files to bundle and include in the CodeBuild execution, by default None
    """

    timeout: Optional[int] = 30
    python_modules: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    local_modules: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    requirements_files: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    codebuild_image: Optional[str] = None
    codebuild_role: Optional[str] = None
    codebuild_environment_type: Optional[str] = None
    codebuild_compute_type: Optional[str] = None
    install_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    pre_build_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    build_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    post_build_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    dirs: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    files: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))


ConfigureFn = Callable[[NamedArg(CodeSeederConfig, "configuration")], None]  # noqa: F821
RemoteFunctionFn = Callable[[VarArg(Any), KwArg(Any)], Any]

ConfigureDecorator = Callable[[ConfigureFn], ConfigureFn]
RemoteFunctionDecorator = Callable[..., RemoteFunctionFn]


@dataclasses.dataclass()
class RegistryEntry:
    configured: bool = False
    config_function: Optional[ConfigureFn] = None
    config_object: CodeSeederConfig = CodeSeederConfig()
    stack_outputs: Optional[Dict[str, str]] = None
    remote_functions: Dict[str, RemoteFunctionFn] = dataclasses.field(default_factory=dict)
