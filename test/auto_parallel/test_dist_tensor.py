# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
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

import paddle
import paddle.distributed as dist

class TestDistTensor(unittest.TestCase):
    def test_dist_tensor_creation(self):
        shape = [10, 5]
        mesh = dist.ProcessMesh([[0, 1], [2, 3]], dim_names=["x", "y"])
        dist_attr = dist.DistAttr(mesh=mesh, sharding_specs=['x', 'y'])

        # create dist tensor using numpy
        dist_tensor_with_numpy = dist.shard_tensor(
            np.ones(shape, dtype=np.float32), dist_attr=dist_attr
        )

        # create dist tensor using tensor
        dist_tensor_with_tensor = dist.shard_tensor(
            paddle.ones(shape), dist_attr=dist_attr
        )

        # create normal tensor
        tensor = paddle.ones(shape)

        # test dist tensor properties
        self.assertEqual(dist_tensor_with_numpy.shape, shape)
        self.assertEqual(dist_tensor_with_tensor.shape, shape)
        self.assertEqual(dist_tensor_with_numpy.is_dist(), True)
        self.assertEqual(dist_tensor_with_tensor.is_dist(), True)
        self.assertEqual(tensor.is_dist(), False)
        self.assertEqual(
            str(dist_tensor_with_numpy), str(dist_tensor_with_tensor)
        )
        self.assertEqual(dist_tensor_with_numpy.dist_attr, dist_attr)
        self.assertEqual(dist_tensor_with_tensor.dist_attr, dist_attr)

        
class TestDistributedTensor(unittest.TestCase):
    def test_dtensor_from_fn(self):
        # Define a function for generating a tensor
        def generate_tensor_ones():
            return paddle.ones(shape=[2, 3])
        
        def generate_tensor_zeros():
             return paddle.zeros(shape=[2, 3])

        def generate_tensor_random():
              return paddle.rand(shape=[2, 3])
        

        # Create a distributed attribute
        mesh = dist.ProcessMesh([[2, 4, 5], [0, 1, 3]], dim_names=["x", "y"])
        dist_attr = dist.DistAttr(mesh=mesh, sharding_specs=['x', 'y'])
        
        # Test with generate_tensor_ones()
        # Call the function dtensor_from_fn with dist_attr parameter
        result = dist.dtensor_from_fn(paddle.ones, dist_attr=dist_attr, shape=[2, 3])

        # Verify the result
        self.assertIsInstance(result, paddle.Tensor)
        self.assertEqual(result.shape, [2, 3])
        self.assertEqual(result.dist_attr, dist_attr)

        # Test with generate_tensor_zeros()
        result_zeros = dist.dtensor_from_fn(paddle.zeros, dist_attr=dist_attr, shape=[2, 3])
        self.assertIsInstance(result_zeros, paddle.Tensor)
        self.assertEqual(result_zeros.shape, [2, 3])
        self.assertEqual(result_zeros.dist_attr, dist_attr)

        # Test with generate_tensor_random()
        result_random = dist.dtensor_from_fn(paddle.rand, dist_attr=dist_attr, shape=[2, 3])
        self.assertIsInstance(result_random, paddle.Tensor)
        self.assertEqual(result_random.shape, [2, 3])
        self.assertEqual(result_random.dist_attr, dist_attr)

if __name__ == "__main__":
    unittest.main()