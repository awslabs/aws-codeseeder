import logging
import os
from string import Template
from typing import Optional

import yaml
from cfn_flip import yaml_dumper
from cfn_tools import load_yaml

from aws_codeseeder import BUNDLE_ROOT, codeseeder, services

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
    configuration.python_modules = ["boto3~=1.19.0"]
    configuration.local_modules = {
        "my-example": os.path.realpath(os.path.join(CLI_ROOT, "../")),
    }
    configuration.requirements_files = {"my-example": os.path.realpath(os.path.join(CLI_ROOT, "../requirements.txt"))}
    configuration.install_commands = ["npm install -g aws-cdk@1.100.0"]
    configuration.dirs = {"images": os.path.realpath(os.path.join(CLI_ROOT, "../images"))}
    configuration.files = {"README.md": os.path.realpath(os.path.join(CLI_ROOT, "../README.md"))}


def remote_hello(name: str) -> None:
    codebuild_role = "Admin"

    @codeseeder.remote_function(
        "my-example",
        extra_python_modules=["python-slugify~=4.0.1"],
        codebuild_role=codebuild_role,
        extra_files={"VERSION": os.path.realpath(os.path.join(CLI_ROOT, "../VERSION"))},
    )
    def remote_hello(name: str) -> None:
        print(f"[RESULT] {name}")

    remote_hello(name)


@codeseeder.remote_function(
    "my-example",
    codebuild_log_callback=print_results_callback,
)
def remote_world(name: str) -> None:
    with open(os.path.join(BUNDLE_ROOT, "README.md"), "r") as readme_file:
        for line in readme_file.readlines():
            print(f"[RESULT] {line.strip()}")


def deployt_test_stack() -> None:
    # Demonstrate deploying a CFN Template with ManagedPolicy and associating the Toolkit Role
    toolkit_stack_name = services.cfn.get_stack_name("orbit")
    toolkit_stack_exists, stack_outputs = services.cfn.does_stack_exist(stack_name=toolkit_stack_name)

    if toolkit_stack_exists and codeseeder.MODULE_IMPORTER == codeseeder.ModuleImporterEnum.OTHER:
        test_stack_name = "my-example-stack"
        test_stack_exists, _ = services.cfn.does_stack_exist(stack_name=test_stack_name)

        if not test_stack_exists:
            _logger.info("Deploying Test Stack")
            src_filename = os.path.join(CLI_ROOT, "resources", "template.yaml")
            with open(src_filename, "r") as src_file:
                src_template = load_yaml(src_file)

            src_template["Resources"]["CodeArtifactPolicy"]["Properties"]["Roles"] = [stack_outputs["CodeBuildRole"]]

            dst_template = Template(yaml.dump(src_template, Dumper=yaml_dumper.get_dumper()))

            dst_dir = codeseeder.create_output_dir("my-example")
            dst_filename = os.path.join(dst_dir, "template.yaml")
            with open(dst_filename, "w") as dst_file:
                dst_file.write(
                    dst_template.safe_substitute(account_id=services.get_account_id(), region=services.get_region())
                )
            services.cfn.deploy_template(stack_name=test_stack_name, filename=dst_filename, toolkit_tag="my-example")
        else:
            _logger.info("Test Stack already exists")


def main() -> None:
    set_log_level(level=logging.INFO)

    # deployt_test_stack()

    remote_hello("monkey")
    remote_world("time")


if __name__ == "__main__":
    main()
