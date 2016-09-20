# Copyright 2016 Erle Robotics, LLC
#
# A relevant part of the code has been written taking inpiration
# from ROS 1 ros_comm package attributed to Open Source Robotics Foundation, Inc.
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

import rclpy
import time
import os
import errno
import sys
import socket
from optparse import OptionParser
from rclpy.qos import qos_profile_default
import itertools
import importlib
from rclpy.impl.rmw_implementation_tools import select_rmw_implementation

NAME='rostopic'

# TODO implement
def _rostopic_cmd_hz(argv):
    print("NOT IMPLEMENTED\n")
    sys.exit(0)

# TODO implement
def _rostopic_cmd_type(argv):
    print("NOT IMPLEMENTED\n")
    sys.exit(0)

def _rostopic_cmd_list(argv):
    result = rclpy.get_remote_topic_names_and_types()
    for topic in result:
        print(topic)
    sys.exit(0)

# TODO implement
def _rostopic_cmd_info(argv):
    print("NOT IMPLEMENTED\n")
    sys.exit(0)

# TODO implement
def _rostopic_cmd_pub(argv):
    print("NOT IMPLEMENTED\n")
    sys.exit(0)

# TODO implement
def _rostopic_cmd_bw(argv):
    print("NOT IMPLEMENTED\n")
    sys.exit(0)

# TODO implement
def _rostopic_cmd_find(argv):
    print("NOT IMPLEMENTED\n")
    sys.exit(0)

# TODO implement
def _rostopic_cmd_delay(argv):
    print("NOT IMPLEMENTED\n")
    sys.exit(0)

module= None
class_ = None

def _convert_getattr(val, f, t): 
    attr = getattr(val, f) 
    if type(attr) is (str) and 'uint8[' in t: 
        return [ord(x) for x in attr] 
    else: 
        return attr 

def strify_message(val, indent=''): 
    global module
    global class_
    type_ = type(val) 
    if type_ in (int, float, bool): 
      return str(val) 
    elif type_ is (str): 
      #TODO: need to escape strings correctly 
      if not val: 
          return "''" 
      return val 

    elif type_ in (list, tuple): 
      if len(val) == 0: 
          return "[]" 
      val0 = val[0] 
      if type(val0) in (int, float, str, bool): 
          # TODO: escape strings properly 
          return str(list(val)) 
      else: 
          pref = indent + '- ' 
          indent = indent + '  ' 
          return '\n'+'\n'.join([pref+strify_message(v, indent) for v in val]) 
    elif isinstance(val, class_): 
        fields = val.__slots__ 

        type_list = [];
        for a in val.__slots__:
            try:
                type_list.append(val.__getattribute__(a))
            except:
                type_list.append(str)

        p = '%s%%s: %%s'%(indent) 
        ni = '  '+indent 
        vals = '\n'.join([p%(f, 
                           strify_message(_convert_getattr(val, f, t), ni)) for f,t in zip(val.__slots__, type_list) if f in fields]) 
        if indent: 
          return '\n'+vals 
        else: 
          return vals 

    else: 
      return str(val) #pun

def chatter_callback(msg):
    print('------------------')
    print(strify_message(msg))
    print('------------------')

def _rostopic_cmd_echo(argv):
    global module
    global class_

    node = rclpy.create_node('rostopic_echo')

    # from args[1] import args[2]
    module = importlib.import_module(argv[2])

    class_ = getattr(module, argv[3])

    sub = node.create_subscription(class_,
                                argv[4],
                                chatter_callback,
                                qos_profile_default)
    assert sub  # prevent unused warning

    while rclpy.ok():
        rclpy.spin_once(node)

def _fullusage():
    print("""rostopic is a command-line tool for printing information about ROS Topics.
Commands:
\trostopic bw\tdisplay bandwidth used by topic
\trostopic delay\tdisplay delay of topic from timestamp in header
\trostopic echo module message topic\tprint messages to screen
\trostopic find\tfind topics by type
\trostopic hz\tdisplay publishing rate of topic    
\trostopic info\tprint information about active topic
\trostopic list\tlist active topics
\trostopic pub\tpublish data to topic
\trostopic type\tprint topic type
Type rostopic <command> -h for more detailed usage, e.g. 'rostopic echo -h'
""")
    sys.exit(getattr(os, 'EX_USAGE', 1))

def rostopicmain(argv=None):

    if argv is None:
        argv=sys.argv

    # TODO FIXME, review
    # filter out remapping arguments in case we are being invoked via roslaunch
    #argv = rospy.myargv(argv)
    
    # process argv
    if len(argv) == 1:
        _fullusage()
    try:
        command = argv[1]
        if command == 'echo':
            select_rmw_implementation("rmw_opensplice_cpp")
            rclpy.init(argv)
            _rostopic_cmd_echo(argv)
        elif command == 'hz':
            _rostopic_cmd_hz(argv)
        elif command == 'type':
            _rostopic_cmd_type(argv)
        elif command == 'list':
            select_rmw_implementation("rmw_fastrtps_cpp")
            rclpy.init(argv)
            _rostopic_cmd_list(argv)
        elif command == 'info':
            _rostopic_cmd_info(argv)
        elif command == 'pub':
            _rostopic_cmd_pub(argv)
        elif command == 'bw':
            _rostopic_cmd_bw(argv)
        elif command == 'find':
            _rostopic_cmd_find(argv)
        elif command == 'delay':
            _rostopic_cmd_delay(argv)
        else:
            _fullusage()
    except socket.error:
        sys.stderr.write("Network communication failed.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write("ERROR: %s\n"%str(e))
        sys.exit(1)
