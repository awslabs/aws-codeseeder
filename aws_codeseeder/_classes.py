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


class ModuleImporter(str, enum.Enum):
    CODESEEDER_CLI = "codeseeder"
    IMPORT = "import"


@dataclasses.dataclass()
class RemoteCtlConfig:
    """[summary]

    [extended_summary]
    """

    timeout: Optional[int] = 30
    python_modules: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    local_modules: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    requirements_files: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    codebuild_image: Optional[str] = None
    codebuild_role: Optional[str] = None
    install_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    pre_build_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    build_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    post_build_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    dirs: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    files: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))


ConfigureFn = Callable[[NamedArg(RemoteCtlConfig, "configuration")], None]  # noqa: F821
RemoteFunctionFn = Callable[[VarArg(Any), KwArg(Any)], Any]

ConfigureDecorator = Callable[[ConfigureFn], ConfigureFn]
RemoteFunctionDecorator = Callable[..., RemoteFunctionFn]


@dataclasses.dataclass()
class RegistryEntry:
    configured: bool = False
    config_function: Optional[ConfigureFn] = None
    config_object: RemoteCtlConfig = RemoteCtlConfig()
    stack_outputs: Optional[Dict[str, str]] = None
    remote_functions: Dict[str, RemoteFunctionFn] = dataclasses.field(default_factory=dict)
