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

from typing import Any

from aws_codeseeder import codeseeder
from aws_codeseeder._classes import ModuleImporter
from aws_codeseeder.classes import RemoteCtlConfig


def test_remote_function() -> None:
    @codeseeder.configure("test")
    def config(configuration: RemoteCtlConfig) -> None:
        configuration.python_modules = ["test~=0.0.0"]

    @codeseeder.remote_function("test")
    def fn(**_: Any) -> None:
        pass

    # fn.module_importer = ModuleImporter.CODESEEDER_CLI
    assert codeseeder.MODULE_IMPORTER == ModuleImporter.IMPORT
