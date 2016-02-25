# Copyright 2016 Open Source Robotics Foundation, Inc.
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

import importlib
import os

import ament_index_python

from rclpy.node import Node

rmw_implementations = sorted(ament_index_python.get_resources('rmw_implementation').keys())


def _load_rmw(rmw_implementation):
    module_name = '._rclpy__{rmw_implementation}'.format(
        rmw_implementation=rmw_implementation,
    )
    return importlib.import_module(module_name, package='rclpy')


global _rclpy
try:
    _rclpy
except NameError:
    _rclpy = None
if _rclpy is None:
    for rmw_implementation in rmw_implementations:
        rmw_module = _load_rmw(rmw_implementation)
        if rmw_module is not None:
            _rclpy = rmw_module
            break


def set_rmw_implementation(rmw_implementation):
    assert rmw_implementation.rclpy_get_implementation_identifier(), \
        'Must be a valid RMW implementation'
    global _rclpy
    _rclpy = rmw_implementation


def init(args):
    rclpy_rmw_env = os.getenv('RCLPY_IMPLEMENTATION')
    if rclpy_rmw_env is not None:
        global _rclpy
        _rclpy = _load_rmw(rclpy_rmw_env)

    assert _rclpy is not None, 'Could not load any RMW implementation'
    return _rclpy.rclpy_init(args)


def create_node(node_name):
    node_handle = _rclpy.rclpy_create_node(node_name)
    return Node(node_handle)


def spin(node):
    wait_set = _rclpy.rclpy_get_zero_initialized_wait_set()

    _rclpy.rclpy_wait_set_init(wait_set, len(node.subscriptions), 0, 0)

    while ok():
        _rclpy.rclpy_wait_set_clear_subscriptions(wait_set)
        for subscription in node.subscriptions:
            _rclpy.rclpy_wait_set_add_subscription(wait_set, subscription.subscription_handle)
            _rclpy.rclpy_wait(wait_set)

            msg = _rclpy.rclpy_take(subscription.subscription_handle, subscription.msg_type)

            if msg:
                subscription.callback(msg)


def ok():
    return _rclpy.rclpy_ok()


def shutdown():
    return _rclpy.rclpy_shutdown()
