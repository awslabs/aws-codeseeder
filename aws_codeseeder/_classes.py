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
import threading
from typing import Any, Callable, Dict, List, Optional, Union, cast

import boto3
from mypy_extensions import KwArg, NamedArg, VarArg


class ModuleImporterEnum(str, enum.Enum):
    CODESEEDER_CLI = "codeseeder-cli"
    OTHER = "other"


class EnvVarType(str, enum.Enum):
    PLAINTEXT = "PLAINTEXT"
    PARAMETER_STORE = "PARAMETER_STORE"
    SECRETS_MANAGER = "SECRETS_MANAGER"


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances: Dict[Any, Any] = {}

    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args: List[Any], **kwargs: Dict[Any, Any]) -> Any:
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class SessionSingleton(metaclass=SingletonMeta):
    _value: Optional[boto3.Session] = None

    @property
    def value(self) -> Optional[boto3.Session]:
        return self._value

    @value.setter
    def value(self, v: Optional[boto3.Session]) -> None:
        self._value = v


@dataclasses.dataclass()
class EnvVar:
    """EnvVar dataclass

    This class is used to define environment variables made available inside of CodeBuild. Use of this
    class enables delcaration of all environment variable types that CodeBuild supports.

    Parameters
    ----------
    value : string
        The value for the environment variable. The effect of this value varies depending on the type
        of environment variable created. See the AWS official documention for usage information:
        https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.variables
        https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.parameter-store
        https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.secrets-manager
    type : EnvVarType
        The type of environment variable: PLAINTEXT, PARAMETER_STORE, or SECRETS_MANAGER. See the AWS
        official documentation for usage, by default PLAINTEXT
    """

    value: str
    type: EnvVarType = EnvVarType.PLAINTEXT


@dataclasses.dataclass()
class CodeSeederConfig:
    """Configuration dataclass

    Parameters
    ----------
    timeout : Optional[int], optional
        Set the CodeBuild execution timeout, by default 30
    python_modules : Optional[List[str]], optional
        List of python modules to install during CodeBuild execution, by default None
    pythonpipx_modules : Optional[List[str]], optional
        List of python modules that leverage CLI to install during CodeBuild execution, by default None
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
    npm_mirror: Optional[str]
        Global config for the npm mirror to use, by default None
    pypi_mirror: Optional[str]
        Global config for the pypi mirror to use, by default None
    install_commands : Optional[List[str]], optional
        Commands to execute during the Install phase of the CodeBuild execution, by default None
    pre_build_commands : Optional[List[str]], optional
        Commands to execute during the PreBuild phase of the CodeBuild execution, by default None
    pre_execution_commands : Optional[List[str]], optional
        Commands to execute during the Build phase of the CodeBuild execution prior to calling the remote_function,
        by default None
    build_commands : Optional[List[str]], optional
        Commands to execute during the Build phase of the CodeBuild execution after calling the remote_functin,
        by default None
    post_build_commands : Optional[List[str]], optional
        Commands to execute during the PostBuild phase of the CodeBuild execution, by default None
    dirs : Optional[Dict[str, str]], optional
        Name and Location of local directories to bundle and include in the CodeBuild exeuction,by default None
    files : Optional[Dict[str, str]], optional
        Name and Location of local files to bundle and include in the CodeBuild execution, by default None
    env_vars :  Optional[Dict[str, Union[str, EnvVar]]], optional
        Environment variables to set in the CodeBuild execution, by default None
    exported_env_vars : Optional[List[str], optional
        Environment variables to export from the CodeBuild execution, by default None
    abort_phases_on_failure: bool
        Toggle aborting CodeBuild Phases when an execution failure occurs, by default True
    runtime_versions: Optional[Dict[str, str]], optional
        Runtime versions (e.g. python, nodejs) to install, by default
        ``{"python": "3.7", "nodejs": "12", "docker": "19"}``
    prebuilt_bundle: Optional[str]
        Provide S3 path to a prebuild bundle to use to deploy
    """

    timeout: Optional[int] = 30
    python_modules: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    pythonpipx_modules: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    local_modules: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    requirements_files: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    codebuild_image: Optional[str] = None
    codebuild_role: Optional[str] = None
    codebuild_environment_type: Optional[str] = None
    codebuild_compute_type: Optional[str] = None
    npm_mirror: Optional[str] = None
    pypi_mirror: Optional[str] = None
    install_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    pre_build_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    pre_execution_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    build_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    post_build_commands: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    dirs: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    files: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    env_vars: Optional[Dict[str, Union[str, EnvVar]]] = cast(
        Dict[str, Union[str, EnvVar]], dataclasses.field(default_factory=dict)
    )
    exported_env_vars: Optional[List[str]] = cast(List[str], dataclasses.field(default_factory=list))
    abort_phases_on_failure: bool = True
    runtime_versions: Optional[Dict[str, str]] = cast(Dict[str, str], dataclasses.field(default_factory=dict))
    prebuilt_bundle: Optional[str] = None


ConfigureFn = Callable[[NamedArg(CodeSeederConfig, "configuration")], None]  # noqa: F821
RemoteFunctionFn = Callable[[VarArg(Any), KwArg(Any)], Any]

ConfigureDecorator = Callable[[ConfigureFn], ConfigureFn]
RemoteFunctionDecorator = Callable[..., RemoteFunctionFn]


@dataclasses.dataclass()
class RegistryEntry:
    configured: bool = False
    config_function: Optional[ConfigureFn] = None
    config_object: CodeSeederConfig = dataclasses.field(default_factory=CodeSeederConfig)
    stack_outputs: Optional[Dict[str, str]] = None
    remote_functions: Dict[str, RemoteFunctionFn] = dataclasses.field(default_factory=dict)
    deploy_if_not_exists: bool = False
    lock: threading.Lock = dataclasses.field(default_factory=threading.Lock)
