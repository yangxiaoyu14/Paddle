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

#include <gtest/gtest.h>
#include <map>

#include "paddle/ir/core/attribute.h"
#include "paddle/ir/core/attribute_base.h"
#include "paddle/ir/core/builtin_attribute.h"
#include "paddle/ir/core/builtin_dialect.h"
#include "paddle/ir/core/builtin_type.h"
#include "paddle/ir/core/dialect.h"
#include "paddle/ir/core/ir_context.h"

class AttributeA {};
IR_DECLARE_EXPLICIT_TYPE_ID(AttributeA)
IR_DEFINE_EXPLICIT_TYPE_ID(AttributeA)

struct FakeDialect : ir::Dialect {
  explicit FakeDialect(ir::IrContext *context)
      : ir::Dialect(name(), context, ir::TypeId::get<FakeDialect>()) {}
  static const char *name() { return "fake"; }
};
IR_DECLARE_EXPLICIT_TYPE_ID(FakeDialect)
IR_DEFINE_EXPLICIT_TYPE_ID(FakeDialect)

TEST(attribute_test, attribute_base) {
  // Test 1: Test the function of IrContext to register Dialect.
  ir::IrContext *ctx = ir::IrContext::Instance();
  ir::Dialect *fake_dialect = ctx->GetOrRegisterDialect<FakeDialect>();
  // Test 2: Test the get method of AbstractType.
  ir::TypeId a_id = ir::TypeId::get<AttributeA>();
  ir::AbstractAttribute abstract_attribute_a =
      ir::AbstractAttribute::get(a_id, *fake_dialect);
  EXPECT_EQ(abstract_attribute_a.type_id(), a_id);
  // Test 3: Test the constructor of AbstractStorage.
  ir::AttributeStorage storage_a(&abstract_attribute_a);
  EXPECT_EQ(storage_a.abstract_attribute().type_id(),
            abstract_attribute_a.type_id());
}

TEST(attribute_test, built_in_attribute) {
  ir::IrContext *ctx = ir::IrContext::Instance();
  // Test 1: Test the parametric built-in attribute of IrContext.
  std::string str_tmp = "string_a";
  ir::Attribute string_attr_1 = ir::StrAttribute::get(ctx, str_tmp);
  ir::Attribute string_attr_2 = ir::StrAttribute::get(ctx, str_tmp);
  EXPECT_EQ(string_attr_1, string_attr_2);
  EXPECT_EQ(ir::StrAttribute::classof(string_attr_1), 1);
  // Test 2: Test isa and dyn_cast.
  EXPECT_EQ(string_attr_1.isa<ir::StrAttribute>(), true);
  ir::StrAttribute string_attr_cast_1 =
      string_attr_1.dyn_cast<ir::StrAttribute>();
  EXPECT_EQ(string_attr_cast_1.isa<ir::StrAttribute>(), true);
  EXPECT_EQ(string_attr_cast_1.size() == 8, 1);

  ir::Int32Type i32_type = ir::Int32Type::get(ctx);
  ir::Attribute type_attr = ir::TypeAttribute::get(ctx, i32_type);
  EXPECT_TRUE(type_attr.isa<ir::TypeAttribute>());
  EXPECT_EQ(type_attr.dyn_cast<ir::TypeAttribute>().data().type_id(),
            i32_type.type_id());
}
