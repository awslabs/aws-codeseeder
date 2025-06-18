# aws-codeseeder

#  *** As of June 2, 2025, AWS CodeSeeder is in Keep The Lights On (KTLO) status.
## We will not be accepting any Feature Requests for AWSCodeSeeder. We will be releasing AWS CodeSeeder based on necessary patches going forward.


## All logic of AWS Codeseeder has been replicated into [Seed Farmer](https://github.com/awslabs/seed-farmer).  Seed Farmer is not impacted by this change and will continue to operate, receive feature requests, and release on regular intervals with full support.



[![PyPi](https://img.shields.io/pypi/v/aws-codeseeder)](https://pypi.org/project/aws-codeseeder/)
[![Python Version](https://img.shields.io/pypi/pyversions/aws-codeseeder.svg)](https://pypi.org/project/aws-codeseeder/)
[![License](https://img.shields.io/pypi/l/aws-codeseeder)](https://github.com/awslabs/aws-codeseeder/blob/main/LICENSE)

The `aws-codeseeder` project enables builders to easily "seed" python code to AWS CodeBuild for execution in their cloud environments.

The library and its CLI utility are typically used to simplify the development and deployment of complex __Infrastructure as Code__ projects. These projects may have many dependencies and require multiple CLI utilities to orchestrate their deployments. For example, a project that deploys networking resources with the __AWS CDK__, an Amazon EKS Cluster with the `eskctl` CLI utility, and Kubernetes applications with `kubectl` and `helm` CLI utilities.

The `aws-codeseeder` eliminates the need to install and configure libraries and utilities locally or on a build system (i.e. Jenkins). Instead, the library enables builders to easily execute an AWS CodeBuild instance with the utilities they require, then seed local python code to, and execute it within, the CodeBuild instance. By bundling and executing local python code in AWS CodeBuild, `aws-codeseeder` can enable GitOps type deployments of complex, mixed technology projects.

## Usage

See the [Example project](example/) for basic usage info and the documentation for more advanced usage.
