import concurrent.futures
import logging
import os
from typing import Dict, Optional

from aws_codeseeder import BUNDLE_ROOT, LOGGER, EnvVar, codeseeder, commands, services

DEBUG_LOGGING_FORMAT = "[%(asctime)s][%(filename)-13s:%(lineno)3d] %(message)s"
CLI_ROOT = os.path.dirname(os.path.abspath(__file__))


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
    LOGGER.setLevel(level=level)

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
        LOGGER.info(msg)


@codeseeder.configure("my-example", deploy_if_not_exists=True)
def configure(configuration: codeseeder.CodeSeederConfig) -> None:
    """An example of global ``codeseeder.configure``

    Parameters
    ----------
    configuration : codeseeder.CodeSeederConfig
        The configuration object that will be used by ``codeseeder.remote_functions``
    """
    configuration.python_modules = ["boto3~=1.19.0"]
    configuration.local_modules = {
        "aws-codeseeder": os.path.realpath(os.path.join(CLI_ROOT, "../../")),
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
    # codebuild_role = "some-other-role"

    # Execute this if we're being run by CodeBuild
    if codeseeder.EXECUTING_REMOTELY:
        LOGGER.info("Executing remotely in CodeBuild")
    else:
        LOGGER.info("Executing locally")

        # Example of using a different Session for remote CodeBuild execution
        # Here we can assume role, even cross-account, for execution
        # The account must have a SeedKit already deployed
        # role_arn = "arn:aws:iam::000000000000:role/other-role"
        # role = services.boto3_client("sts").assume_role(
        #     RoleArn=role_arn,
        #     RoleSessionName="adminrole",
        # )
        # session = Session(
        #     aws_access_key_id=role["Credentials"]["AccessKeyId"],
        #     aws_secret_access_key=role["Credentials"]["SecretAccessKey"],
        #     aws_session_token=role["Credentials"]["SessionToken"],
        #     region_name="us-east-2",
        # )

    @codeseeder.remote_function(
        "my-example",
        extra_python_modules=["python-slugify~=4.0.1"],
        # codebuild_role=codebuild_role,
        extra_files={"VERSION": os.path.realpath(os.path.join(CLI_ROOT, "../VERSION"))},
        extra_post_build_commands=[f"export ANOTHER_EXPORTED_VAR='{name}'"],
        extra_exported_env_vars=["ANOTHER_EXPORTED_VAR"],
        bundle_id=name,
        # boto3_session=session,
        extra_env_vars={
            "OTHER_KEY_1": "key1",
            "OTHER_KEY_2": EnvVar(value="PlainText"),
            # "OTHER_KEY_3": EnvVar(value="ParameterStoreValue", type=EnvVarType.PARAMETER_STORE),
            # "OTHER_KEY_4": EnvVar(value="SecretsManagerValue", type=EnvVarType.SECRETS_MANAGER),
        },
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
    seedkit_deployed, stack_name, stack_outputs = commands.seedkit_deployed(seedkit_name="my-example")

    if seedkit_deployed and not codeseeder.EXECUTING_REMOTELY:
        test_stack_name = "my-example-stack"
        test_stack_exists, _ = services.cfn.does_stack_exist(stack_name=test_stack_name)

        if not test_stack_exists:
            LOGGER.info("Deploying Test Stack")
            template_filename = os.path.join(CLI_ROOT, "resources", "template.yaml")
            services.cfn.deploy_template(
                stack_name=test_stack_name,
                filename=template_filename,
                seedkit_tag="my-example",
                parameters={"RoleName": stack_outputs["CodeBuildRole"]},
            )
        else:
            LOGGER.info("Test Stack already exists")


def main() -> None:
    set_log_level(level=logging.DEBUG)

    deploy_test_stack()

    params = ["Bart", "List", "Maggie"]
    with concurrent.futures.ThreadPoolExecutor(3) as workers:
        for result in workers.map(remote_hello_world_2, params):
            LOGGER.info("name_dict: %s", result)

    name_dict = remote_hello_world_1("Bart")
    LOGGER.info("name_dict: %s", name_dict)

    # name_str = remote_hello_world_2("Lisa")
    # LOGGER.info("name_str: %s", name_str)


if __name__ == "__main__":
    main()
