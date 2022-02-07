# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New
* Enable toggling aborting CodeBuild phases on command execution failure
* Support CodeBuild spec runtime-versions

### Changes

### Fixes

### Breaks


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
