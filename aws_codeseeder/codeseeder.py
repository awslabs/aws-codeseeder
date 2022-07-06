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

import functools
import json
import os
import textwrap
from typing import Any, Callable, Dict, List, Mapping, Optional, cast

from aws_codeseeder import LOGGER, __version__, _bundle, _classes, _remote
from aws_codeseeder._classes import CodeSeederConfig, ConfigureDecorator, ModuleImporterEnum, RemoteFunctionDecorator
from aws_codeseeder.commands import deploy_seedkit, seedkit_deployed
from aws_codeseeder.services import codebuild

__all__ = [
    "CodeSeederConfig",
    "ConfigureDecorator",
    "ModuleImporterEnum",
    "RemoteFunctionDecorator",
    "configure",
    "remote_function",
    "deploy_seedkit",
    "seedkit_deployed",
]

MODULE_IMPORTER = (
    _classes.ModuleImporterEnum.CODESEEDER_CLI
    if os.environ.get("AWS_CODESEEDEER_CLI_EXECUTING", "No") == "Yes"
    else _classes.ModuleImporterEnum.OTHER
)

EXECUTING_REMOTELY = os.environ.get("AWS_CODESEEDEER_CLI_EXECUTING", "No") == "Yes"

SEEDKIT_REGISTRY: Dict[str, _classes.RegistryEntry] = {}
RESULT_EXPORT_FILE = "/tmp/codeseeder_export.sh"


def configure(seedkit_name: str, deploy_if_not_exists: bool = False) -> ConfigureDecorator:
    """Decorator marking a Configuration Function

    Decorated Configuration Functions are executed lazily when a ``remote_function`` for a particular Seedkit is called.
    The Configuration Function sets the default configuration for the Seedkit.

    Parameters
    ----------
    seedkit_name : str
        The name of the previously deployed Seedkit to associate this configuration with
    deploy_if_not_exists: bool
        Deploy a Seedkit of ``seedkit_name`` if it does not exist, by default False

    Returns
    -------
    ConfigureDecorator
        The decorated function
    """

    def decorator(func: _classes.ConfigureFn) -> _classes.ConfigureFn:
        SEEDKIT_REGISTRY[seedkit_name] = _classes.RegistryEntry(
            config_function=func, deploy_if_not_exists=deploy_if_not_exists
        )

        return func

    return decorator


def remote_function(
    seedkit_name: str,
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
    codebuild_environment_type: Optional[str] = None,
    codebuild_compute_type: Optional[str] = None,
    extra_install_commands: Optional[List[str]] = None,
    extra_pre_build_commands: Optional[List[str]] = None,
    extra_build_commands: Optional[List[str]] = None,
    extra_post_build_commands: Optional[List[str]] = None,
    extra_dirs: Optional[Dict[str, str]] = None,
    extra_files: Optional[Dict[str, str]] = None,
    extra_env_vars: Optional[Dict[str, str]] = None,
    extra_exported_env_vars: Optional[List[str]] = None,
    abort_phases_on_failure: Optional[bool] = None,
    runtime_versions: Optional[Dict[str, str]] = None,
    bundle_id: Optional[str] = None,
) -> RemoteFunctionDecorator:
    """Decorator marking a Remote Function

    Decorated Remote Functions are intercepted on execution and seeded to a CodeBuild Project for remote execution.

    Parameters
    ----------
    seedkit_name : str
        The name of the previously deployed Seedkit to seed execution to.
    function_module : Optional[str], optional
        Name of the module in the seeded code to execute. If None, then inferred from the decorated function's module,
        by default None
    function_name : Optional[str], optional
        Name of the function in the seeded code to execute. If None, the inferred from the decorated function's name,
        by default None
    timeout : Optional[int], optional
        Override the CodeBuild execution timeout, by default None
    codebuild_log_callback : Optional[Callable[[str], None]], optional
        Callback function executed as CodeBuild execution logs are pulled, by default None
    extra_python_modules : Optional[List[str]], optional
        List of additional python modules to install during CodeBuild exection, by default None
    extra_local_modules : Optional[Dict[str, str]], optional
        Name and Location of additional local python modules to bundle and install during CodeBuild execution,
        by default None
    extra_requirements_files : Optional[Dict[str, str]], optional
        Additional local requirements.txt files to bundle and install during CodeBuild execution, by default None
    codebuild_image : Optional[str], optional
        Alternative container image to use during CodeBuild execution, by default None
    codebuild_role : Optional[str], optional
        Alternative IAM Role to use during CodeBuild execution, by default None
    codebuild_environment_type : Optional[str], optional
        Alternative Environment to use for the CodeBuild execution (e.g. LINUX_CONTAINER), by default None
    codebuild_compute_type : Optional[str], optional
        Alternative Compute to use for the CodeBuild execution (e.g. BUILD_GENERAL1_SMALL), by default None
    extra_install_commands : Optional[List[str]], optional
        Additional commands to execute during the Install phase of the CodeBuild execution, by default None
    extra_pre_build_commands : Optional[List[str]], optional
        Additional commands to execute during the PreBuild phase of the CodeBuild execution, by default None
    extra_build_commands : Optional[List[str]], optional
        Additional commands to execute during the Build phase of the CodeBuild execution, by default None
    extra_post_build_commands : Optional[List[str]], optional
        Additional commands to execute during the PostBuild phase of the CodeBuild execution, by default None
    extra_dirs : Optional[Dict[str, str]], optional
        Name and Location of additional local directories to bundle and include in the CodeBuild exeuction,
        by default None
    extra_files : Optional[Dict[str, str]], optional
        Name and Location of additional local files to bundle and include in the CodeBuild execution, by default None
    extra_env_vars : Optional[Dict[str, str]], optional
        Additional environment variables to set in the CodeBuild execution, by default None
    extra_exported_env_vars : Optional[List[str]], optional
        Additional environment variables to export from the CodeBuild execution, by default None
    bundle_id : Optional[str], optional
        Optional identifier to uniquely identify a bundle locally when multiple ``remote_functions`` are executed
        concurrently, by default None
    abort_phases_on_failure: Optional[bool], optional
        Override default abort of CodeBuild Phases when an execution failure occurs, by default None
    runtime_versions: Optional[Dict[str, str]], optional
        Override default runtime versions (e.g. python, nodejs) to install, by default None

    Returns
    -------
    RemoteFunctionDecorator
        The decorated function
    """

    def decorator(func: Callable[..., Any]) -> _classes.RemoteFunctionFn:
        if seedkit_name not in SEEDKIT_REGISTRY:
            SEEDKIT_REGISTRY[seedkit_name] = _classes.RegistryEntry()
        registry_entry = SEEDKIT_REGISTRY[seedkit_name]
        config_object = registry_entry.config_object

        fn_module = function_module if function_module else func.__module__
        fn_name = function_name if function_name else func.__name__
        fn_id = f"{fn_module}:{fn_name}"

        python_modules = decorator.python_modules  # type: ignore
        local_modules = decorator.local_modules  # type: ignore
        requirements_files = decorator.requirements_files  # type: ignore
        codebuild_image = decorator.codebuild_image  # type: ignore
        codebuild_role = decorator.codebuild_role  # type: ignore
        codebuild_environment_type = decorator.codebuild_environment_type  # type: ignore
        codebuild_compute_type = decorator.codebuild_compute_type  # type: ignore
        install_commands = decorator.install_commands  # type: ignore
        pre_build_commands = decorator.pre_build_commands  # type: ignore
        build_commands = decorator.build_commands  # type: ignore
        post_build_commands = decorator.post_build_commands  # type: ignore
        dirs = decorator.dirs  # type: ignore
        files = decorator.files  # type: ignore
        env_vars = decorator.env_vars  # type: ignore
        exported_env_vars = decorator.exported_env_vars  # type: ignore
        abort_on_failure = decorator.abort_on_failure  # type: ignore
        runtimes = decorator.runtimes  # type: ignore

        if not registry_entry.configured:
            if registry_entry.config_function:
                registry_entry.config_function(configuration=config_object)

                LOGGER.info("Seedkit Configuration Complete")
            registry_entry.configured = True

        # update modules and requirements after configuration
        python_modules = config_object.python_modules + python_modules
        local_modules = {**cast(Mapping[str, str], config_object.local_modules), **local_modules}
        requirements_files = {**cast(Mapping[str, str], config_object.requirements_files), **requirements_files}
        codebuild_image = config_object.codebuild_image if config_object.codebuild_image else codebuild_image
        codebuild_role = config_object.codebuild_role if config_object.codebuild_role else codebuild_role
        codebuild_environment_type = (
            config_object.codebuild_environment_type
            if config_object.codebuild_environment_type
            else codebuild_environment_type
        )
        codebuild_compute_type = (
            config_object.codebuild_compute_type if config_object.codebuild_compute_type else codebuild_compute_type
        )
        install_commands = config_object.install_commands + install_commands
        pre_build_commands = config_object.pre_build_commands + pre_build_commands
        build_commands = config_object.build_commands + build_commands
        post_build_commands = config_object.post_build_commands + post_build_commands
        dirs = {**cast(Mapping[str, str], config_object.dirs), **dirs}
        files = {**cast(Mapping[str, str], config_object.files), **files}
        env_vars = {**cast(Mapping[str, str], config_object.env_vars), **env_vars}
        exported_env_vars = config_object.exported_env_vars + exported_env_vars
        abort_on_failure = abort_on_failure if abort_on_failure is not None else config_object.abort_phases_on_failure
        runtimes = runtimes if runtimes is not None else config_object.runtime_versions

        LOGGER.debug("MODULE_IMPORTER: %s", MODULE_IMPORTER)
        LOGGER.debug("EXECUTING_REMOTELY: %s", EXECUTING_REMOTELY)

        if not EXECUTING_REMOTELY:
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
            if EXECUTING_REMOTELY:
                # Exectute the module
                result = func(*args, **kwargs)
                LOGGER.debug("result: %s", result)
                if result is not None:
                    with open(RESULT_EXPORT_FILE, "w") as file:
                        LOGGER.debug("writing env export file: %s", RESULT_EXPORT_FILE)
                        file.write(
                            textwrap.dedent(
                                f"""\
                                read -r -d '' AWS_CODESEEDER_OUTPUT <<'EOF'
                                {json.dumps(result)}
                                EOF
                                """
                            )
                        )
                        file.write("export AWS_CODESEEDER_OUTPUT")
                return result
            else:
                with registry_entry.lock:
                    while True:
                        stack_exists, stack_name, stack_outputs = seedkit_deployed(seedkit_name=seedkit_name)
                        if not stack_exists and registry_entry.deploy_if_not_exists:
                            deploy_seedkit(seedkit_name=seedkit_name)
                        elif not stack_exists:
                            raise ValueError(f"Seedkit/Stack named {seedkit_name} is not yet deployed")
                        else:
                            registry_entry.stack_outputs = stack_outputs
                            break

                # Bundle and execute remotely in codebuild
                LOGGER.info("Beginning Remote Execution: %s", fn_id)
                fn_args = {"fn_id": fn_id, "args": args, "kwargs": kwargs}
                LOGGER.debug("fn_args: %s", fn_args)
                stack_outputs = registry_entry.stack_outputs

                cmds_install = [
                    "python3 -m venv ~/.venv",
                    ". ~/.venv/bin/activate",
                    "cd ${CODEBUILD_SRC_DIR}/bundle",
                    f"pip install aws-codeseeder~={__version__}",
                ]
                # If this local env variable is set, don't attempt install of codeseeder from package repository
                # This is used so that codeseeder can be installed from a local python module included in the bundle
                # and is used for codeseeder development when codeartifact isn't used.
                if os.getenv("AWS_CODESEEDER_DEVELOPMENT"):
                    cmds_install.pop()

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

                bundle_zip = _bundle.generate_bundle(
                    fn_args=fn_args, dirs=dirs_tuples, files=files_tuples, bundle_id=bundle_id
                )
                buildspec = codebuild.generate_spec(
                    stack_outputs=stack_outputs,
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
                        (
                            f"if [[ -f {RESULT_EXPORT_FILE} ]]; then source {RESULT_EXPORT_FILE}; "
                            "else echo 'No return value to export'; fi"
                        ),
                    ]
                    + build_commands,
                    cmds_post=[
                        ". ~/.venv/bin/activate",
                        "cd ${CODEBUILD_SRC_DIR}/bundle",
                    ]
                    + post_build_commands,
                    exported_env_vars=exported_env_vars,
                    abort_phases_on_failure=abort_on_failure,
                    runtime_versions=runtimes,
                )

                overrides = {}
                if codebuild_image:
                    overrides["imageOverride"] = codebuild_image
                if codebuild_role:
                    overrides["serviceRoleOverride"] = codebuild_role
                if codebuild_environment_type:
                    overrides["environmentTypeOverride"] = codebuild_environment_type
                if codebuild_compute_type:
                    overrides["computeTypeOverride"] = codebuild_compute_type
                if env_vars:
                    overrides["environmentVariablesOverride"] = [
                        {"name": k, "value": v, "type": "PLAINTEXT"} for k, v in env_vars.items()
                    ]

                build_info = _remote.run(
                    stack_outputs=stack_outputs,
                    bundle_path=bundle_zip,
                    buildspec=buildspec,
                    timeout=timeout if timeout else config_object.timeout if config_object.timeout else 30,
                    codebuild_log_callback=codebuild_log_callback,
                    overrides=overrides if overrides != {} else None,
                )
                if build_info:
                    LOGGER.debug("exported_env_vars: %s", build_info.exported_env_vars)
                    codeseeder_output = build_info.exported_env_vars.pop("AWS_CODESEEDER_OUTPUT", None)
                    codeseeder_output = json.loads(codeseeder_output) if codeseeder_output else None
                    return (
                        (codeseeder_output, build_info.exported_env_vars)
                        if build_info.exported_env_vars != {}
                        else codeseeder_output
                    )
                else:
                    return None

        registry_entry.remote_functions[fn_id] = wrapper
        return wrapper

    decorator.python_modules = [] if extra_python_modules is None else extra_python_modules  # type: ignore
    decorator.local_modules = {} if extra_local_modules is None else extra_local_modules  # type: ignore
    decorator.requirements_files = {} if extra_requirements_files is None else extra_requirements_files  # type: ignore
    decorator.codebuild_image = codebuild_image  # type: ignore
    decorator.codebuild_role = codebuild_role  # type: ignore
    decorator.codebuild_environment_type = codebuild_environment_type  # type: ignore
    decorator.codebuild_compute_type = codebuild_compute_type  # type: ignore
    decorator.install_commands = [] if extra_install_commands is None else extra_install_commands  # type: ignore
    decorator.pre_build_commands = [] if extra_pre_build_commands is None else extra_pre_build_commands  # type: ignore
    decorator.build_commands = [] if extra_build_commands is None else extra_build_commands  # type: ignore
    decorator.post_build_commands = (  # type: ignore
        [] if extra_post_build_commands is None else extra_post_build_commands
    )
    decorator.dirs = {} if extra_dirs is None else extra_dirs  # type: ignore
    decorator.files = {} if extra_files is None else extra_files  # type: ignore
    decorator.env_vars = {} if extra_env_vars is None else extra_env_vars  # type: ignore
    decorator.exported_env_vars = [] if extra_exported_env_vars is None else extra_exported_env_vars  # type: ignore
    decorator.abort_on_failure = abort_phases_on_failure  # type: ignore
    decorator.runtimes = runtime_versions  # type: ignore

    return decorator
