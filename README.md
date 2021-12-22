# aws-codeseeder

The `aws-codeseeder` project enables builders to easily "seed" python code to AWS CodeBuild for execution in their cloud environments.

The library and its CLI utility are typically used to simplify development and deployment of complex __Infrastructure as Code__ projects. These projects may have many dependencies and require mutiple CLI utilities to orchestrate their deployments. For example, a project that deploys networking resources with the __AWS CDK__, an Amazon EKS Cluster with the `eskctl` CLI utility, and Kubernetes applications with `kubectl` and `helm` CLI utilities.

The `aws-codeseeder` elminates the need to install and configure libraries and utilities locally or on a build system (i.e. Jenkins). Instead the library enables builders to easily execute an AWS CodeBuild instance with the utilities they require then seed local python code to, and execute it within, the CodeBuild instance. By bundling and executing local python code in AWS CodeBuild, `aws-codeseeder` can enable GitOps type deployments of complex, mixed technology projects.

## Usage

See the [Example project](example/) for basic usage info and the documentation for more advanced usage.
