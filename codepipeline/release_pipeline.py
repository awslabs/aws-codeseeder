#!/usr/bin/env python3

# type: ignore

import os

from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import core

app = core.App()

pipeline_params = app.node.try_get_context("release-pipeline")
deployment_secret = pipeline_params["deployment-secret"]

stack = core.Stack(
    app,
    "CodeSeederReleaseDeploymentPipeline",
    env=core.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]),
)

artifacts_bucket = s3.Bucket(stack, "ArtifactsBucket")

source_output = codepipeline.Artifact("SourceOutput")
release_output = codepipeline.Artifact("ReleaseOutput")

code_build_role = iam.Role(
    stack,
    "CodeSeederReleaseBuildRole",
    role_name="CodeSeederReleaseBuildRole",
    assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
    managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name("PowerUserAccess"),
        iam.ManagedPolicy.from_aws_managed_policy_name("IAMFullAccess"),
    ],
)

pipeline = codepipeline.Pipeline(
    stack,
    "CodePipeline",
    pipeline_name="CodeSeeder_Release",
    restart_execution_on_update=True,
    artifact_bucket=artifacts_bucket,
    stages=[
        codepipeline.StageProps(
            stage_name="Source",
            actions=[
                codepipeline_actions.GitHubSourceAction(
                    action_name="GitHub_Source",
                    repo="aws-codeseeder",
                    branch=pipeline_params["github-branch"],
                    owner=pipeline_params["github-owner"],
                    oauth_token=core.SecretValue.secrets_manager(
                        secret_id=deployment_secret["secret-id"],
                        json_field=deployment_secret["json-fields"]["github-oauth-token"],
                    ),
                    trigger=codepipeline_actions.GitHubTrigger.WEBHOOK,
                    output=source_output,
                )
            ],
        ),
        codepipeline.StageProps(
            stage_name="Build",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="Build_Code_Build_Image",
                    project=codebuild.PipelineProject(
                        stack,
                        "BuildCodeBuildImage",
                        build_spec=codebuild.BuildSpec.from_source_filename("codepipeline/codebuild-buildspecs/build-code-build-image-buildspec.yaml"),
                        role=code_build_role,
                        environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.STANDARD_4_0,
                        ),
                    ),
                    input=source_output,
                )
            ],
        ),
        codepipeline.StageProps(
            stage_name="Test",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="Test",
                    project=codebuild.PipelineProject(
                        stack,
                        "TestBuild",
                        build_spec=codebuild.BuildSpec.from_source_filename("codepipeline/codebuild-buildspecs/test-buildspec.yaml"),
                        role=code_build_role,
                        environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.STANDARD_4_0,
                        ),
                    ),
                    input=source_output,
                )
            ],
        ),
        codepipeline.StageProps(
            stage_name="Approval-For-Release",
            actions=[codepipeline_actions.ManualApprovalAction(action_name="Approve_Release")],
        ),
        codepipeline.StageProps(
            stage_name="Pypi-Release",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="PyPi_Release",
                    project=codebuild.PipelineProject(
                        stack,
                        "PyPiReleaseBuild",
                        build_spec=codebuild.BuildSpec.from_source_filename("codepipeline/codebuild-buildspecs/release-buildspec.yaml"),
                        role=code_build_role,
                        environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.STANDARD_4_0,
                        ),
                    ),
                    input=source_output,
                    outputs=[release_output],
                )
            ],
        ),
        codepipeline.StageProps(
            stage_name="Image-to-Public-ECR",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="Code_Build_Base_Release",
                    project=codebuild.PipelineProject(
                        stack,
                        "PublicECRRelease",
                        build_spec=codebuild.BuildSpec.from_source_filename("codepipeline/codebuild-buildspecs/release-public-ecr-buildspec.yaml"),
                        role=code_build_role,
                        environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.STANDARD_4_0,
                        ),
                    ),
                    input=source_output,
                    outputs=[release_output],
                )
            ],
        ),
    ],
)

# notification_rule = notifications.CfnNotificationRule(
#     stack,
#     "CodePipelineNotifications",
#     detail_type="FULL",
#     event_type_ids=[
#         "codepipeline-pipeline-pipeline-execution-failed",
#         "codepipeline-pipeline-pipeline-execution-canceled",
#         "codepipeline-pipeline-pipeline-execution-succeeded",
#     ],
#     name="aws-codeseeder-codepipeline-notifications",
#     resource=pipeline.pipeline_arn,
#     targets=[
#         notifications.CfnNotificationRule.TargetProperty(
#             target_address=core.Token.as_string(
#                 core.SecretValue.secrets_manager(
#                     secret_id=deployment_secret["secret-id"],
#                     json_field=deployment_secret["json-fields"]["slack-chatbot"],
#                 )
#             ),
#             target_type="AWSChatbotSlack",
#         )
#     ],
# )

app.synth()
