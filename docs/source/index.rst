An `AWS Professional Service <https://aws.amazon.com/professional-services>`_ open source initiative | aws-proserve-opensource@amazon.com

AWS CodeSeeder
==============

The ``aws-codeseeder`` project enables builders to easily "seed" python code to **AWS CodeBuild** for execution in their cloud environments.

The library and its CLI utility can be used to simplify development and deployment of complex **Infrastructure as Code** projects. These projects usually have many dependencies and require mutiple CLI utilities to orchestrate their deployments. For example, a project that deploys networking resources with the **AWS CDK**, an **Amazon EKS** Cluster with the ``eskctl`` CLI utility, and Kubernetes applications with ``kubectl`` and ``helm`` CLI utilities.

The ``aws-codeseeder`` elminates the need to install and configure libraries and utilities locally or on a build system (i.e. Jenkins). Instead the library enables builders to easily execute an **AWS CodeBuild** instance with the utilities they require then seed local python code to, and execute it within, the CodeBuild instance. By bundling and executing local python code in **AWS CodeBuild**, ``aws-codeseeder`` can enable GitOps type deployments of complex, mixed technology projects.

How It Works
------------

Each CodeSeeder client project does a one-time deployment of a named Seedkit of AWS resources. Deployment can be done with the CodeSeeder module or the CLI utility, resources include:

- AWS CodeBuild Project: remote executor
- S3 Bucket: local resources are bundled and uploaded, acts as Source to the CodeBuild executions
- KMS Key: for optional encryption of bundles and source
- AWS CodeArtifact Domain and Repository: for optional serving of shared Python packages
- IAM Role: default Role used by the CodeBuild executions
- IAM Managed Policy: grants access to Seedkit resources

In the CodeSeeder client project, builders use the ``codeseeder.remote_function`` decorator to mark code for execution by the remote CodeBuild Project. When functions marked with the ``remote_function`` decorator are called locally, the CodeSeeder library intercepts the call, bundles the local project and dependencies, pushes the bundle to S3, starts a CodeBuild execution using the bundle in S3 as Source, then executes the marked function remotely in the CodeBuild project.


.. image:: _static/seedkit_resources.png
   :alt: Seedkit Resources

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
