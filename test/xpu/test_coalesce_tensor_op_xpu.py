#   Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import numpy as np

from paddle.fluid import core

alignment = 256
from get_test_cover_info import (
    XPUOpTestWrapper,
    create_test_class,
    get_xpu_op_support_types,
)
from op_test_xpu import XPUOpTest

import paddle

paddle.enable_static()


class XPUTestCoalesceTensorOp(XPUOpTestWrapper):
    def __init__(self):
        self.op_name = 'coalesce_tensor'
        self.use_dynamic_create_class = False

    class TestAllocContinuousSpace(XPUOpTest):
        def setUp(self):
            self.op_type = "coalesce_tensor"
            self.use_xpu = True
            self.dtype, self.fluid_dtype = self.init_dtype()
            attrs = self.init_attr()
            self.copy_data = attrs["copy_data"]
            self.constant = attrs["constant"]
            self.set_constant = attrs["set_constant"]
            self.Inputs = self.init_input()
            self.Outputs, self.FusedOutput = self.init_output(
                self.Inputs, self.set_constant, self.constant
            )
            self.inputs = {'Input': self.Inputs}
            self.attrs = attrs
            self.outputs = {
                'Output': self.Outputs,
                'FusedOutput': self.FusedOutput,
            }

        def init_dtype(self):
            return np.float32, int(core.VarDesc.VarType.FP32)

        def init_input(self):
            inputs = []
            inputs.append(("x1", np.random.random([20, 3]).astype(self.dtype)))
            inputs.append(("x2", np.random.random([20]).astype(self.dtype)))
            inputs.append(("x3", np.random.random([1]).astype(self.dtype)))
            inputs.append(
                ("x4", np.random.random([200, 30]).astype(self.dtype))
            )
            inputs.append(("x5", np.random.random([30]).astype(self.dtype)))
            inputs.append(("x6", np.random.random([1]).astype(self.dtype)))
            return inputs

        def init_attr(self):
            return {
                "copy_data": True,
                "set_constant": False,
                "constant": 0.0,
                "dtype": self.fluid_dtype,
            }

        def init_output(self, input_list, set_constant, constant):
            inputs = []
            outputs = input_list

            for input in input_list:
                length = len(input[1].flatten())
                aligned_len = (length + alignment) / alignment * alignment
                out = np.zeros(int(aligned_len))
                out[0:length] = input[1].flatten()
                inputs.append(out)

            coalesce_tensor_var = np.concatenate(list(inputs))
            if set_constant:
                coalesce_tensor_var = (
                    np.ones(len(coalesce_tensor_var)) * constant
                )
                outputs = [
                    (
                        out[0],
                        np.ones(out[1].shape).astype(self.dtype) * constant,
                    )
                    for out in outputs
                ]
            return outputs, coalesce_tensor_var

        def test_check_output(self):
            self.check_output_with_place(
                place=core.XPUPlace(0), no_check_set=["FusedOutput"], atol=1e-5
            )

    class TestAllocContinuousSpace2(TestAllocContinuousSpace):
        def init_attr(self):
            return {
                "copy_data": False,
                "set_constant": True,
                "constant": 0.5,
                "dtype": self.fluid_dtype,
                "user_defined_size_of_dtype": 2,
            }

        def test_check_output(self):
            self.check_output_with_place(
                place=core.XPUPlace(0), no_check_set=["FusedOutput"], atol=1e-5
            )


support_types = get_xpu_op_support_types('coalesce_tensor')
for stype in support_types:
    create_test_class(globals(), XPUTestCoalesceTensorOp, stype)

if __name__ == '__main__':
    unittest.main()
