# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
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

### Breaks


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
