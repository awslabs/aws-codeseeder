#!/usr/bin/env python

import argparse
import json
import logging
import os
import subprocess
from typing import Dict, cast

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_secret(secret_name: str) -> Dict[str, Dict[str, str]]:
    region_name = os.environ.get("AWS_DEFAULT_REGION")
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError:
        logger.info("Secret with SecretId '%s' could not be retrieved from SecretsManager")
        return {}
    else:
        return cast(Dict[str, Dict[str, str]], json.loads(get_secret_value_response.get("SecretString", "{}")))


def main(url: str) -> None:
    secret_name = os.environ.get("AWS_CODESEEDER_NPM_MIRROR_SECRET", "NO_SECRET")
    # Backwards Compatibility
    if secret_name == "NO_SECRET":
        secret_name = os.environ.get("AWS_CODESEEDER_MIRROR_SECRET", "NO_SECRET")
    if secret_name != "NO_SECRET":
        secret_name_key = secret_name.split("::")[0] if "::" in secret_name else secret_name
        key = secret_name.split("::")[1] if "::" in secret_name else "npm"
        creds = get_secret(secret_name=secret_name_key)
        if key in creds.keys():
            ssl_token = creds[key]["ssl_token"] if creds[key].get("ssl_token") else None
            subprocess.call(["npm", "config", "set", f"{url.replace('https:', '')}:_auth={ssl_token}"])
        logger.info("Calling npm config with %s", url)
    else:
        logger.info("'AWS_CODESEEDER_NPM_MIRROR_SECRET' is not set")
    subprocess.call(["npm", "config", "set", "registry", url])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="URL to evaluate")
    parser.add_argument("url", type=str, help="The url to set in npm'")
    args = parser.parse_args()
    main(args.url)
