#  Tencent is pleased to support the open source community by making GNES available.
#
#  Copyright (C) 2019 THL A29 Limited, a Tencent company. All rights reserved.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import List

from google.protobuf.json_format import MessageToJson, Parse

from ..base import BaseDocIndexer
from ...proto import gnes_pb2


class DictIndexer(BaseDocIndexer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._content = {}

    def add(self, keys: List[int], docs: List['gnes_pb2.Document'], *args, **kwargs):
        self._content.update({k: MessageToJson(d) for (k, d) in zip(keys, docs)})

    def query(self, keys: List[int], *args, **kwargs) -> List['gnes_pb2.Document']:
        return [Parse(self._content[k], gnes_pb2.Document()) for k in keys]

    @property
    def size(self):
        return len(self._content)
