#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import random
import time
from typing import Any, Callable

import boto3
import botocore

from aws_codeseeder import LOGGER, __version__


def _get_botocore_config() -> botocore.config.Config:
    return botocore.config.Config(
        retries={"max_attempts": 5},
        connect_timeout=10,
        max_pool_connections=10,
        user_agent_extra=f"aws-codeseeder/{__version__}",
    )


def boto3_client(service_name: str) -> boto3.client:
    return boto3.Session().client(service_name=service_name, use_ssl=True, config=_get_botocore_config())


def boto3_resource(service_name: str) -> boto3.client:
    return boto3.Session().resource(service_name=service_name, use_ssl=True, config=_get_botocore_config())


def get_region() -> str:
    session = boto3.Session()
    if session.region_name is None:
        raise ValueError("It is not possible to infer AWS REGION from your environment.")
    return str(session.region_name)


def get_account_id() -> str:
    return str(boto3_client(service_name="sts").get_caller_identity().get("Account"))


def try_it(
    f: Callable[..., Any],
    ex: Any,
    base: float = 1.0,
    max_num_tries: int = 3,
    **kwargs: Any,
) -> Any:
    """Run function with decorrelated Jitter.

    Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    """
    delay: float = base
    for i in range(max_num_tries):
        try:
            return f(**kwargs)
        except ex as exception:
            if i == (max_num_tries - 1):
                raise exception
            delay = random.uniform(base, delay * 3)
            LOGGER.error(
                "Retrying %s | Fail number %s/%s | Exception: %s",
                f,
                i + 1,
                max_num_tries,
                exception,
            )
            time.sleep(delay)
