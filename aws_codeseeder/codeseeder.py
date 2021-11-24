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
import functools
import os
from typing import Any, Callable, Dict, List, Mapping, Optional, cast

from mypy_extensions import KwArg, NamedArg, VarArg

import __main__
from aws_codeseeder import LOGGER, __version__, bundle, remote
from aws_codeseeder.services import cfn, codebuild


class ModuleImporter(str, enum.Enum):
    CODESEEDER_CLI = "codeseeder"
    IMPORT = "import"


MODULE_IMPORTER = (
    ModuleImporter.CODESEEDER_CLI
    if os.path.basename(__main__.__file__).strip(".py") == "codeseeder"
    else ModuleImporter.IMPORT
)


@dataclasses.dataclass()
class RemoteCtlConfig:
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


TOOLKIT_REGISTRY: Dict[str, RegistryEntry] = {}


def configure(
    toolkit_name: str,
) -> ConfigureDecorator:
    def decorator(func: ConfigureFn) -> ConfigureFn:
        stack_name = cfn.get_stack_name(toolkit_name=toolkit_name)
        stack_exists, stack_outputs = cfn.does_stack_exist(stack_name=stack_name)
        if not stack_exists:
            raise ValueError(f"Toolkit/Stack named {toolkit_name} is not yet deployed")
        TOOLKIT_REGISTRY[toolkit_name] = RegistryEntry(config_function=func, stack_outputs=stack_outputs)

        return func

    return decorator


def remote_function(
    toolkit_name: str,
    *,
    function_module: Optional[str] = None,
    function_name: Optional[str] = None,
    timeout: Optional[int] = None,
    codebuild_log_callback: Optional[Callable[[str], None]] = None,
    extra_python_modules: Optional[List[str]] = None,
    extra_local_modules: Optional[Dict[str, str]] = None,
    extra_requirements_files: Optional[Dict[str, str]] = None,
    codebuild_image: Optional[str] = None,
    codebuild_role: Optional[str] = None,
    extra_install_commands: Optional[List[str]] = None,
    extra_pre_build_commands: Optional[List[str]] = None,
    extra_build_commands: Optional[List[str]] = None,
    extra_post_build_commands: Optional[List[str]] = None,
    extra_dirs: Optional[Dict[str, str]] = None,
    extra_files: Optional[Dict[str, str]] = None,
    bundle_id: Optional[str] = None,
) -> RemoteFunctionDecorator:
    def decorator(func: Callable[..., Any]) -> RemoteFunctionFn:
        stack_name = cfn.get_stack_name(toolkit_name=toolkit_name)
        stack_exists, stack_outputs = cfn.does_stack_exist(stack_name=stack_name)
        if not stack_exists:
            raise ValueError(f"Toolkit/Stack named {toolkit_name} is not yet deployed")
        if toolkit_name not in TOOLKIT_REGISTRY:
            TOOLKIT_REGISTRY[toolkit_name] = RegistryEntry(stack_outputs=stack_outputs)

        fn_module = function_module if function_module else func.__module__
        fn_name = function_name if function_name else func.__name__
        fn_id = f"{fn_module}:{fn_name}"

        registry_entry = TOOLKIT_REGISTRY[toolkit_name]
        config_object = registry_entry.config_object

        python_modules = decorator.python_modules  # type: ignore
        local_modules = decorator.local_modules  # type: ignore
        requirements_files = decorator.requirements_files  # type: ignore
        codebuild_image = decorator.codebuild_image  # type: ignore
        codebuild_role = decorator.codebuild_role  # type: ignore
        install_commands = decorator.install_commands  # type: ignore
        pre_build_commands = decorator.pre_build_commands  # type: ignore
        build_commands = decorator.build_commands  # type: ignore
        post_build_commands = decorator.post_build_commands  # type: ignore
        dirs = decorator.dirs  # type: ignore
        files = decorator.files  # type: ignore

        if not registry_entry.configured:
            if registry_entry.config_function:
                registry_entry.config_function(configuration=config_object)

                LOGGER.info("Toolkit Configuration Complete")
            registry_entry.configured = True

        # update modules and requirements after configuration
        python_modules = config_object.python_modules + python_modules
        local_modules = {**cast(Mapping[str, str], config_object.local_modules), **local_modules}
        requirements_files = {**cast(Mapping[str, str], config_object.requirements_files), **requirements_files}
        codebuild_image = codebuild_image if codebuild_image else config_object.codebuild_image
        codebuild_role = codebuild_role if codebuild_role else config_object.codebuild_role
        install_commands = config_object.install_commands + install_commands
        pre_build_commands = config_object.pre_build_commands + pre_build_commands
        build_commands = config_object.build_commands + build_commands
        post_build_commands = config_object.post_build_commands + post_build_commands
        dirs = {**cast(Mapping[str, str], config_object.dirs), **dirs}
        files = {**cast(Mapping[str, str], config_object.files), **files}

        if MODULE_IMPORTER == ModuleImporter.IMPORT:
            if any([not os.path.isdir(p) for p in cast(Dict[str, str], local_modules).values()]):
                raise ValueError(f"One or more local modules could not be resolved: {local_modules}")
            if any([not os.path.isfile(p) for p in cast(Dict[str, str], requirements_files).values()]):
                raise ValueError(f"One or more requirements files could not be resolved: {requirements_files}")
            if any([not os.path.isdir(p) for p in cast(Dict[str, str], dirs).values()]):
                raise ValueError(f"One or more dirs could not be resolved: {dirs}")
            if any([not os.path.isfile(p) for p in cast(Dict[str, str], files).values()]):
                raise ValueError(f"One or more files could not be resolved: {files}")

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if MODULE_IMPORTER == ModuleImporter.CODESEEDER_CLI:
                # Exectute the module locally
                return func(*args, **kwargs)
            elif MODULE_IMPORTER == ModuleImporter.IMPORT:
                # Bundle and execute remotely in codebuild
                LOGGER.info("Beginning Remote Execution: %s", fn_id)
                fn_args = {"fn_id": fn_id, "args": args, "kwargs": kwargs}
                LOGGER.debug("fn_args: %s", fn_args)
                registry_entry = TOOLKIT_REGISTRY[toolkit_name]
                stack_outputs = registry_entry.stack_outputs

                cmds_install = [
                    "python3 -m venv ~/.venv",
                    ". ~/.venv/bin/activate",
                    "cd ${CODEBUILD_SRC_DIR}/bundle",
                    f"pip install aws-codeseeder~={__version__}",
                ]
                if requirements_files:
                    cmds_install += [f"pip install -r requirements-{f}" for f in requirements_files.keys()]
                if local_modules:
                    cmds_install += [f"pip install {m}/" for m in local_modules.keys()]
                if python_modules:
                    cmds_install.append(f"pip install {' '.join(python_modules)}")

                dirs_tuples = [(v, k) for k, v in local_modules.items()] + [(v, k) for k, v in dirs.items()]
                files_tuples = [(v, f"requirements-{k}") for k, v in requirements_files.items()] + [
                    (v, f"{k}") for k, v in files.items()
                ]

                bundle_zip = bundle.generate_bundle(
                    fn_args=fn_args, dirs=dirs_tuples, files=files_tuples, bundle_id=bundle_id
                )
                buildspec = codebuild.generate_spec(
                    stack_outputs=cast(Dict[str, str], stack_outputs),
                    cmds_install=cmds_install + install_commands,
                    cmds_pre=[
                        ". ~/.venv/bin/activate",
                        "cd ${CODEBUILD_SRC_DIR}/bundle",
                    ]
                    + pre_build_commands,
                    cmds_build=[
                        ". ~/.venv/bin/activate",
                        "cd ${CODEBUILD_SRC_DIR}/bundle",
                        "codeseeder execute --args-file fn_args.json --debug",
                    ]
                    + build_commands,
                    cmds_post=[
                        ". ~/.venv/bin/activate",
                        "cd ${CODEBUILD_SRC_DIR}/bundle",
                    ]
                    + post_build_commands,
                )

                overrides = {}
                if codebuild_image:
                    overrides["imageOverride"] = codebuild_image
                if codebuild_role:
                    overrides["serviceRoleOverride"] = codebuild_role

                remote.run(
                    stack_outputs=cast(Dict[str, str], stack_outputs),
                    bundle_path=bundle_zip,
                    buildspec=buildspec,
                    timeout=timeout if timeout else config_object.timeout if config_object.timeout else 30,
                    codebuild_log_callback=codebuild_log_callback,
                    overrides=overrides if overrides != {} else None,
                )
                # value = func(*args, **kwargs)
            else:
                raise ValueError(f"Invalid value for attribute module_importer: {MODULE_IMPORTER}")

        registry_entry.remote_functions[fn_id] = wrapper
        return wrapper

    decorator.python_modules = [] if extra_python_modules is None else extra_python_modules  # type: ignore
    decorator.local_modules = {} if extra_local_modules is None else extra_local_modules  # type: ignore
    decorator.requirements_files = {} if extra_requirements_files is None else extra_requirements_files  # type: ignore
    decorator.codebuild_image = codebuild_image  # type: ignore
    decorator.codebuild_role = codebuild_role  # type: ignore
    decorator.install_commands = [] if extra_install_commands is None else extra_install_commands  # type: ignore
    decorator.pre_build_commands = [] if extra_pre_build_commands is None else extra_pre_build_commands  # type: ignore
    decorator.build_commands = [] if extra_build_commands is None else extra_build_commands  # type: ignore
    decorator.post_build_commands = (  # type: ignore
        [] if extra_post_build_commands is None else extra_post_build_commands
    )
    decorator.dirs = {} if extra_dirs is None else extra_dirs  # type: ignore
    decorator.files = {} if extra_files is None else extra_files  # type: ignore

    return decorator
