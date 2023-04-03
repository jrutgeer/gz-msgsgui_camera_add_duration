#!/usr/bin/env python3
#
# Copyright (C) 2022 Open Source Robotics Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import subprocess
import sys

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Generate protobuf support files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--protoc-exec',
        required=True,
        help='The path to the protoc executable')
    parser.add_argument(
        '--gz-generator-bin',
        help='The path to the gz specific protobuf generator')
    parser.add_argument(
        '--generate-cpp',
        help='Flag to indicate if C++ bindings should be generated')
    parser.add_argument(
        '--generate-ruby',
        help='Flag to indicate if Ruby bindings should be generated')
    parser.add_argument(
        '--output-cpp-path',
        help='The basepath of the generated C++ files')
    parser.add_argument(
        '--output-ruby-path',
        help='The basepath of the generated C++ files')
    parser.add_argument(
        '--proto-path',
        required=True,
        help='The location of the protos')
    parser.add_argument(
        '--input-path',
        required=True,
        help='The location of the template files')
    args = parser.parse_args(argv)

    # First generate the base cpp and ruby files
    cmd = [args.protoc_exec]
    cmd += [f'--proto_path={args.proto_path}']

    if args.generate_cpp:
        cmd += [f'--plugin=protoc-gen-ignmsgs={args.gz_generator_bin}']
        cmd += [f'--cpp_out=dllexport_decl=GZ_MSGS_VISIBLE:{args.output_cpp_path}']
        cmd += [f'--ignmsgs_out={args.output_cpp_path}']
    if args.generate_ruby:
        cmd += [f'--ruby_out=dllexport_decl=GZ_MSGS_VISIBLE:{args.output_ruby_path}']
    cmd += [args.input_path]

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f'Failed to execute protoc compiler: {e}')
        sys.exit(-1)

    # Move original generated cpp to details/
    proto_file = os.path.splitext(os.path.relpath(args.input_path, args.proto_path))[0]
    detail_proto_file = proto_file.split(os.sep)

    detail_proto_dir = detail_proto_file[:-1]
    detail_proto_dir.append('details')
    detail_proto_dir = os.path.join(*detail_proto_dir)
    detail_proto_file.insert(-1, 'details')
    detail_proto_file = os.path.join(*detail_proto_file)

    header = os.path.join(args.output_cpp_path, proto_file + ".pb.h")
    gz_header = os.path.join(args.output_cpp_path, proto_file + ".gz.h")
    detail_header = os.path.join(args.output_cpp_path, detail_proto_file + ".pb.h")

    try:
        os.makedirs(os.path.join(args.output_cpp_path, detail_proto_dir),
                exist_ok=True)
        # Windows cannot rename a file to an existing file
        if os.path.exists(detail_header):
            os.remove(detail_header)
        os.rename(header, detail_header)
        os.rename(gz_header, header)
    except e:
        print(f'Failed to manipulate gz-msgs headers: {e}')
        sys.exit(-1)

if __name__ == '__main__':
    sys.exit(main())
