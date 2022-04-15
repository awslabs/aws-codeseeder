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

import importlib
import json
import logging
import os
from typing import Optional, Tuple

import click

from aws_codeseeder import LOGGER, commands

DEBUG_LOGGING_FORMAT = "[%(asctime)s][%(filename)-13s:%(lineno)3d] %(message)s"
DEBUG_LOGGING_FORMAT_REMOTE = "[%(filename)-13s:%(lineno)3d] %(message)s"


def set_log_level(level: int, format: Optional[str] = None) -> None:
    kwargs = {"level": level}
    if format:
        kwargs["format"] = format  # type: ignore
    logging.basicConfig(**kwargs)  # type: ignore
    LOGGER.setLevel(level)
    logging.getLogger("boto3").setLevel(logging.ERROR)
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger("s3transfer").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)


@click.group()
def cli() -> None:
    """AWS CodeSeeder CLI utility"""
    pass


@click.group(name="deploy")
def deploy() -> None:
    pass


@click.group(name="destroy")
def destroy() -> None:
    pass


################################################################################
#
# Seedkit Commands
#
################################################################################
@deploy.command(name="seedkit")
@click.argument(
    "name",
    type=str,
    required=True,
)
@click.option("--policy-arn", required=False, type=str, multiple=True, default=[])
@click.option(
    "--deploy-codeartifact/--skip-codeartifact",
    default=False,
    help="Deploy the optional CodeArtifact Domain and Repository",
    show_default=True,
)
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable detailed logging.",
    show_default=True,
)
def deploy_seedkit(name: str, policy_arn: Tuple[str, ...], deploy_codeartifact: bool, debug: bool) -> None:
    if debug:
        set_log_level(level=logging.DEBUG, format=DEBUG_LOGGING_FORMAT)
    else:
        set_log_level(level=logging.INFO, format="%(message)s")
    commands.deploy_seedkit(
        seedkit_name=name, managed_policy_arns=[p for p in policy_arn], deploy_codeartifact=deploy_codeartifact
    )


@destroy.command(name="seedkit")
@click.argument(
    "name",
    type=str,
    required=True,
)
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable detailed logging.",
    show_default=True,
)
def destroy_seedkit(name: str, debug: bool) -> None:
    if debug:
        set_log_level(level=logging.DEBUG, format=DEBUG_LOGGING_FORMAT)
    else:
        set_log_level(level=logging.INFO, format="%(message)s")
    commands.destroy_seedkit(seedkit_name=name)


################################################################################
#
# Module Commands
#
################################################################################
@deploy.command(name="modules")
@click.argument(
    "name",
    type=str,
    required=True,
)
@click.option("--module", required=False, type=str, multiple=True, default=[])
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable detailed logging.",
    show_default=True,
)
def deploy_modules(name: str, module: Tuple[str, ...], debug: bool) -> None:
    if debug:
        set_log_level(level=logging.DEBUG, format=DEBUG_LOGGING_FORMAT)
    else:
        set_log_level(level=logging.INFO, format="%(message)s")
    commands.deploy_modules(seedkit_name=name, python_modules=[m for m in module])


################################################################################
#
# Execute Commands
#
################################################################################
@cli.command(name="execute")
@click.option("--args-file", type=str, required=True)
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable detailed logging.",
    show_default=True,
)
def execute(args_file: str, debug: bool) -> None:
    if debug:
        set_log_level(level=logging.DEBUG, format=DEBUG_LOGGING_FORMAT)
    else:
        set_log_level(level=logging.INFO, format="%(message)s")
    with open(args_file, "r") as file:
        fn_args = json.load(file)
    LOGGER.info("fn_args: %s", fn_args)
    module_name, func_name = fn_args["fn_id"].split(":")
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    func(*fn_args["args"], **fn_args["kwargs"])


def main() -> int:
    os.environ.setdefault("AWS_CODESEEDEER_CLI_EXECUTING", "Yes")

    cli.add_command(deploy)
    cli.add_command(destroy)
    cli()
    return 0


if __name__ == "__main__":
    main()
