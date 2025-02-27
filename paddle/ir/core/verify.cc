// Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "paddle/ir/core/verify.h"
#include "paddle/ir/core/operation.h"
namespace ir {
void Verify(Operation *op, bool verify_recursively) {
  op->Verify();
  if (!verify_recursively) return;
  for (size_t index = 0; index < op->num_regions(); ++index) {
    auto &region = op->region(index);
    for (auto block : region) {
      for (auto op_item : *block) {
        Verify(op_item, verify_recursively);
      }
    }
  }
}
}  // namespace ir
