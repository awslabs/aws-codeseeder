Usage
=====

A CodeSeeder Seedkit is a set of AWS service resources scoped to a specific project that enables bundling of local projects, files, and libraries and remote execution in AWS CodeBuild. Deploying the Seedkit will configure the AWS CodeBuild Project with an IAM Role and an attached IAM Managed Policy. The Policy is least privilege scoped to grant the CodeBuild Project access to only the AWS resources deployed with the Seedkit. To enable the CodeBuild Project to manage additional resources the user must either attach additional IAM Managed Polices to the Seedkit's IAM Role, or create a new IAM Role with required permissions and attach the Seedkit's IAM Managed Policy to it.

Usage consists of:

1. Installing the AWS CodeSeeder library
2. Deploying a named CodeSeeder Seedkit for a project
3. Configuring IAM permissions by either:
   - Attaching additional IAM Managed Policies to the Seedkit Role. This can be automated during Seedkit deployment or done manually by the User
   - Creating a new IAM Role and attaching the Seedkit Managed Policy to it. This must be done manually by the User
4. Decorating project functions for configuration and remote execution

Installation
------------

AWS CodeSeeder can be installed from PyPi

.. code-block:: bash

    pip install aws-codeseeder


Deploying
---------

A Seedkit can be deployed using the ``codeseedeer`` CLI or within the project using the ``aws_codeseeder.commands`` module. Optionally, additional IAM Managed Policies can be attached to the Seedkit's IAM Role during deployment.

**Basic CLI Deployment**

.. code-block:: bash

    codeseeder deploy seedkit my-example-deployment

**CLI Deployment attaching Permissions Boundary**

.. code-block:: bash

    codeseeder deploy seedkit my-example-deployment \
    --permissions-boundary-arn arn:aws:iam::00000000000:policy/YourBoundaryPolicy

**CLI Deployment attaching Managed Policies**

.. code-block:: bash

    codeseeder deploy seedkit my-example-deployment \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
    --policy-arn arn:aws:iam::00000000000:policy/YourManagedPolicy

**Basic Module Deployment**

.. code-block:: python

    from aws_codeseeder import commands

    commands.deploy_seedkit(seedkit_name="my-example-deployment")

**Module Deployment attaching Permissions Boundary**

.. code-block:: python

    from aws_codeseeder import commands

    commands.deploy_seedkit(
        seedkit_name=name,
        permissions_boundary_arn="arn:aws:iam::00000000000:policy/YourBoundaryPolicy"
    ])

**Module Deployment attaching Manage Policies**

.. code-block:: python

    from aws_codeseeder import commands

    commands.deploy_seedkit(seedkit_name=name, managed_policy_arns=[
        "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
        "arn:aws:iam::00000000000:policy/YourManagedPolicy"
    ])


Configuring IAM Permissions
---------------------------

If IAM Managed Policies are not attached to the Seedkit's IAM Role during deployment or if another IAM Role is to be used for the CodeBuild Project then manual configuration will be required. Users can use the Console, AWS CLI, or AWS SDKs to attach additional Managed Policies to the Seedkit's Role. The same tools can be used to create an IAM Role.

If manually attaching additional Managed Polices to the Seedkit's IAM Role, the Role can be identified by its naming convention: ``codeseeder-[SEEDKIT_NAME]-[REGION]-codebuild``. For example ``codeseeder-my-example-deployment-us-west-2-codebuild``.

If Creating a new IAM Role, the Role will need a Trust Relationship with AWS CodeBuild and the Seedkit's Managed Policy should be attached to grant access to Seedkit resources. The Seedkit Managed Policy can be identified by its naming convention: ``codeseeder-[SEEDKIT_NAME]-[REGION]-resources``. For example ``codeseeder-my-example-deployment-us-west-2-resources``. An example Trust Retlationship Policy doc:

.. code-block:: json

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "codebuild.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }


Decorating Project Code
-----------------------

Two function decorators are provided: ``codeseeder.configure`` and ``codeseeder.remote_function``. The ``codeseeder.configure`` decorator identifies a function that globally configures remote executions. The ``codeseeder.remote_function`` identifies functions that will be intercepted, wrapped, and executed remotely in AWS CodeBuild. See the **example/** project for advanced usage.

**Configuration**

.. code-block:: python

    from aws_codeseeder import codeseeder

    @codeseeder.configure("my-example-deployment")
    def configure(configuration: codeseeder.CodeSeederConfig) -> None:
        configuration.python_modules = ["boto3~=1.19.0"]
        configuration.local_modules = {
            "my-example": os.path.realpath(os.path.join(CLI_ROOT, "../")),
        }
        configuration.requirements_files = {"my-example": os.path.realpath(os.path.join(CLI_ROOT, "../requirements.txt"))}
        configuration.install_commands = ["npm install -g aws-cdk@1.100.0"]
        configuration.dirs = {"images": os.path.realpath(os.path.join(CLI_ROOT, "../images"))}
        configuration.files = {"README.md": os.path.realpath(os.path.join(CLI_ROOT, "../README.md"))}

**Remote Function Execution**

.. code-block:: python

    from aws_codeseeder import codeseeder

    @codeseeder.remote_function("my-example-deployment")
    def remote_hello(name: str) -> None:
        # This code will be executed in AWS CodeBuild
        print(f"Hello {name}")
