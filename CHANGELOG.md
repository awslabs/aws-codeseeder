# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New
- adding support to pass in an existing bundle (assuming it is compliant)
- adding support for python 3.12, removed support for python 3.7 (considered a breaking change)
- adding tox to be able to test on all python versions locally
  
### Changes

### Fixes

### Breaks


## 0.13.0 - (2024-05-09)
---
### New
- adding support for AWS SecretsManager to support mirror credentials
  - the SecretsManager name MUST be of the form `*-mirror-credentials`
  - the content must be JSON
  - the content has the form `{
          "pypi": { "username": "testingpypi", "password": "thepasswordpypi" },
          "something": {"username": "testing","password": "testing"
          }}`

### Changes

### Fixes

### Breaks

## 0.12.1 - (2024-04-23)
---

### New

### Changes
- updating the default codebuild image to `aws/codebuild/standard:7.0`

### Fixes

### Breaks

## 0.12.0 - (2024-04-19)
---

### New
- support for npm mirror and pypi mirror in decorators
### Changes

### Fixes

### Breaks

## 0.11.1 - (2024-01-22)
---

### New

### Changes

### Fixes
- updating readthedocs configs as site has changed their requirements

### Breaks


## 0.11.0 - (2024-01-22)
---

### New

- added bucket policy to deny insecure traffic to seedkit bucket

### Changes
- Allows override of codeseeder build image with aws curated images.
- Updates codeseeder seedkit cloudformation template with a parameter `BuildImage`. This can be used in the future as an input for default image set in the seedkit and referenced as necessary.

### Fixes

### Breaks


## 0.10.2 - (2023-10-30)
---

### New

### Changes
- add the `StackStatus` to the Outputs when checking in `cfn.does_stack_exist` - the stack may exist and not be completed
  
### Fixes

### Breaks


## 0.10.1 - (2023-10-23)
---

### New

### Changes
- pinning `certifi~=2023.7.22` in setup and requirements-dev
- pinning `urllib3~=1.26.18` requirements-dev
### Fixes

### Breaks


## 0.10.0 - (2023-06-19)
---

### New
- adding support for multple AWS partitions (aws-cn and aws-us-gov)

### Changes

### Fixes

### Breaks


## 0.9.2 - (2023-05-09)
---

### New

### Changes

### Fixes
- incompatibility with updated `dataclass` in python 3.11

### Breaks


## 0.9.1 - (2023-05-09)
---

### New

### Changes

### Fixes
- allow the execution of docker login process to fail gracefully if the dir exists
- remove configuration of python and node runtimes by default

### Breaks


## 0.9.0 - (2023-05-02)
---

### New

### Changes

- modifed default version of codebuild image to `aws/codebuild/standard:6.0`
- moved `retrieve_docker_creds.py` to be a resource in the codebase and into the bundle

### Fixes

### Breaks


## 0.8.2 - (2023-04-27)
---

### New
- added `pre_execution_commands` and `extra_pre_execution_commands` to enable commands in the Build phase prior to
  `remote_function execution`


### Fixes
- adding support for Windows OS based deployments when bundling resources
- `files` and `extra_files` failed to create subdirectories in bundles if keys contained director paths


## 0.8.1 - (2023-02-27)
---

### New

### Changes

### Fixes
- fixed logic for applying decorator overrides to configration parameters

### Breaks


## 0.8.0 - (2023-02-06)
---

### New

### Changes
- added VPC support for CodeBuild Project when creating `seedkit`

### Fixes

### Breaks


## 0.7.0 - (2023-01-13)
---

### New

### Changes

### Fixes
* Include bundle_id in S3 path of uploaded bundles


## 0.6.0 - (2022-11-09)
---

### New
* global set of ignored paths when bundling
* remote_funciton supports optional getter function for setting boto3 Session


## 0.5.2 - (2022-09-08)
---

### Fixes
* deploy_seedkit is not threadsafe due to reuse of seedkit/ output directory


## 0.5.1 - (2022-09-07)
---

### Fixes
* Missing support for PARAMETER_STORE and SECRETS_MANAGER env_vars in CodeBuild


## 0.5.0 - (2022-08-30)
---

### New
* enable --profile and --region cli parameters for boto3 operations
* enable distinct boto3.Session per remote_function call


## 0.4.1 - (unreleased)
---

### New

### Changes

### Fixes
- fixed helm tool not installing. specifiying version prevents getting from the actively developed main

### Breaks

## 0.4.0 - (2022-08-16)
---

### New
* enable setting and updating boto3 Session for all operations

### Changes
* refactor error module -> errors hiding private modules


## 0.3.3 - (2022-07-19)
---

### New
- added custom execption class for CodeSeeder errors
- added metadata to failed codebuild deployments (on error)


## 0.3.2 - (2022-07-06)
---

### New
* simple check for whether a seedkit is deployed, the stack_name, and stack_outputs
* simplified seedkit deployment for consumers
* thread safe JIT Seedkit deployment

### Changes
- added build id to logging of codebuild phases

### Fixes
* JIT deployment of the SeedKit Stack when `deploy_if_not_exists` is configured
* Eliminate StackTrace message when Secret is not found


## 0.3.1 - (2022-06-20)
---

### Fixes
* Overrides for remote function(eg codebuild role, codebuild env type) were not being set over the defaults


## 0.3.0 - (2022-04-15)
---

### New
* optionally create a missing seedkit with configure decorator
* Support Python >= 3.7
* Update boto3 version in CodeBuild image
* Remove CDK CLI from CodeBuild image to reduce conflicts


### Fixes
* exclude cdk.out/ from bundles


## 0.2.1 - (2022-02-10)
---

### New
* services.cfn.deploy_template supports input parameters
* Enable toggling aborting CodeBuild phases on command execution failure
* Support CodeBuild spec runtime-versions


## 0.2.0 - (2022-02-03)
---

### New
* enable exported_env_vars from CodeBuild executions back to clients
* enable JSON serializable return values from remote_functions back to clients


## 0.1.6 - (2022-02-01)
---

### New
* new `env_vars` and `extra_env_vars` parameters to set Environment Variables in the CodeBuild Execution


## 0.1.5  (2021-01-24)
---

### New
* new EXECUTING_REMOTELY boolean to simplify conditional code executions

### Changes
* updated MODULE_IMPORTER determination (uses ENV var)

### Fixes
* fixed `aws_codeseeder.services` imports (eliminated circular imports)
