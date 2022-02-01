# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).

## Unreleased
---

### New

- new `env_vars` and `extra_env_vars` parameters to set Environment Variables in the CodeBuild Execution

### Changes

### Fixes

### Breaks


## 0.1.5  (2021-01-24)
---

### New

- new EXECUTING_REMOTELY boolean to simplify conditional code executions

### Changes

- updated MODULE_IMPORTER determination (uses ENV var)

### Fixes

- fixed `aws_codeseeder.services` imports (eliminated circular imports)
