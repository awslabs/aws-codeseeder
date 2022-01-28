# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- new `env_vars` and `extra_env_vars` parameters to set Environment Variables in the CodeBuild Execution

## [0.1.5]

### Added

- new EXECUTING_REMOTELY boolean to simplify conditional code executions

### Changed

- updated MODULE_IMPORTER determination (uses ENV var)
- fixed `aws_codeseeder.services` imports (eliminated circular imports)
