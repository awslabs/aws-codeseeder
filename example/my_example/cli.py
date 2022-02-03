import logging
import os
from string import Template
from typing import Dict, Optional

import yaml
from cfn_flip import yaml_dumper
from cfn_tools import load_yaml

from aws_codeseeder import BUNDLE_ROOT, LOGGER, codeseeder, create_output_dir, services

DEBUG_LOGGING_FORMAT = "[%(asctime)s][%(filename)-13s:%(lineno)3d] %(message)s"
CLI_ROOT = os.path.dirname(os.path.abspath(__file__))

_logger = logging.getLogger(__name__)


def set_log_level(level: int, format: Optional[str] = None) -> None:
    """Helper function set LOG_LEVEL and optional log FORMAT

    Parameters
    ----------
    level : int
        logger.LOG_LEVEL
    format : Optional[str], optional
        Optional string format to apply to log lines, by default None
    """
    kwargs = {"level": level}
    if format:
        kwargs["format"] = format  # type: ignore
    logging.basicConfig(**kwargs)  # type: ignore
    _logger.setLevel(level)

    # Force loggers on dependencies to ERROR
    logging.getLogger("boto3").setLevel(logging.ERROR)
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger("s3transfer").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)


def print_results_callback(msg: str) -> None:
    """Function to demonstrate CodeBuild logging callback functionality

    Parameters
    ----------
    msg : str
        Incoming log message
    """
    if msg.startswith("[RESULT] "):
        _logger.info(msg)


@codeseeder.configure("my-example")
def configure(configuration: codeseeder.CodeSeederConfig) -> None:
    """An example of global ``codeseeder.configure``

    Parameters
    ----------
    configuration : codeseeder.CodeSeederConfig
        The configuration object that will be used by ``codeseeder.remote_functions``
    """
    configuration.python_modules = ["boto3~=1.19.0"]
    configuration.local_modules = {
        "my-example": os.path.realpath(os.path.join(CLI_ROOT, "../")),
    }
    configuration.requirements_files = {"my-example": os.path.realpath(os.path.join(CLI_ROOT, "../requirements.txt"))}
    configuration.install_commands = ["npm install -g aws-cdk@1.100.0"]
    configuration.dirs = {"images": os.path.realpath(os.path.join(CLI_ROOT, "../images"))}
    configuration.files = {"README.md": os.path.realpath(os.path.join(CLI_ROOT, "../README.md"))}


@codeseeder.remote_function(
    "my-example", codebuild_log_callback=print_results_callback, extra_env_vars={"MY_EXAMPLE_NAME": "Maggie"}
)
def remote_hello_world_1(name: str) -> Dict[str, str]:
    """A simple ``codeseeder.remote_function`` example with a local callback for CodeBuild Log messages

    Parameters
    ----------
    name : str
        Just some example name
    """
    print(f"[RESULT] {name}")
    with open(os.path.join(BUNDLE_ROOT, "README.md"), "r") as readme_file:
        for line in readme_file.readlines():
            print(f"[RESULT] {line.strip()}")
    return {"name": name}


def remote_hello_world_2(name: str) -> str:
    """Demonstration of an advanced function decoration

    Here the decorated ``codeseeder.remote_function`` is nested in another function. At times in may be necessary to
    programmatically determine the parameters passed to the decorator at function execution time rather than when the
    module is imported. Nesting the decorated function inside another function will work as long as both functions have
    the same name and parameters.

    Keep in mind when nesting like this, when the functions are executed in CodeBuild the outer function is executed
    then the inner function code. The EXECUTING_REMOTELY flag can be used to determine if function is being executed
    locally or by CodeBuild.

    Parameters
    ----------
    name : str
        Just some example name
    """
    codebuild_role = "Admin"

    # Execute this if we're being run by CodeBuild
    if codeseeder.EXECUTING_REMOTELY:
        LOGGER.info("Executing remotely in CodeBuild")
    else:
        LOGGER.info("Executing locally")

    @codeseeder.remote_function(
        "my-example",
        extra_python_modules=["python-slugify~=4.0.1"],
        codebuild_role=codebuild_role,
        extra_files={"VERSION": os.path.realpath(os.path.join(CLI_ROOT, "../VERSION"))},
        extra_post_build_commands=[f"export ANOTHER_EXPORTED_VAR='{name}'"],
        extra_exported_env_vars=["ANOTHER_EXPORTED_VAR"],
    )
    def remote_hello_world_2(name: str) -> str:
        print(f"[RESULT] {name}")
        return name

    return remote_hello_world_2(name)


def deploy_test_stack() -> None:
    """This function demonstrates using the codeseeder library and tools to deploy an additional CloudFormation Stack

    This additional CloudFormation Stack defines an IAM Role with Trust Relationship to AWS CodeBuild. This
    demonstrates how to use the Seedkit tools to create a dedicated IAM Role for use by CodeBuile. The example also
    attachs the Seedkit's IAM Managed Policy to this new Role, granting the Role access to the Seedkit's resources
    """
    toolkit_stack_name = services.cfn.get_stack_name("my-example")
    toolkit_stack_exists, stack_outputs = services.cfn.does_stack_exist(stack_name=toolkit_stack_name)

    if toolkit_stack_exists and not codeseeder.EXECUTING_REMOTELY:
        test_stack_name = "my-example-stack"
        test_stack_exists, _ = services.cfn.does_stack_exist(stack_name=test_stack_name)

        if not test_stack_exists:
            _logger.info("Deploying Test Stack")
            src_filename = os.path.join(CLI_ROOT, "resources", "template.yaml")
            with open(src_filename, "r") as src_file:
                src_template = load_yaml(src_file)

            src_template["Resources"]["CodeArtifactPolicy"]["Properties"]["Roles"] = [stack_outputs["CodeBuildRole"]]

            dst_template = Template(yaml.dump(src_template, Dumper=yaml_dumper.get_dumper()))

            dst_dir = create_output_dir("my-example")
            dst_filename = os.path.join(dst_dir, "template.yaml")
            with open(dst_filename, "w") as dst_file:
                dst_file.write(
                    dst_template.safe_substitute(account_id=services.get_account_id(), region=services.get_region())
                )
            services.cfn.deploy_template(stack_name=test_stack_name, filename=dst_filename, seedkit_tag="my-example")
        else:
            _logger.info("Test Stack already exists")


def main() -> None:
    set_log_level(level=logging.DEBUG)

    deploy_test_stack()

    name_dict = remote_hello_world_1("Bart")
    name_str = remote_hello_world_2("Lisa")

    _logger.info("name_dict: %s", name_dict)
    _logger.info("name_str: %s", name_str)


if __name__ == "__main__":
    main()
