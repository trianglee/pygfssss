#!/usr/bin/env python3
#
#  Copyright 2021 Nimrod Zimerman
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import argparse
import pathlib

from pygfssss import core


def main():
    parser = argparse.ArgumentParser(
        description='gfsplit, output compatible with http://manpages.ubuntu.com/manpages/bionic/man1/gfsplit.1.html')

    parser.add_argument('-n',
                        dest='threshold',
                        action='store',
                        type=int,
                        default=3,
                        help='number of shares needed to recombine')

    parser.add_argument('-m',
                        dest='shares_count',
                        action='store',
                        type=int,
                        default=5,
                        help='number of shares to build')

    parser.add_argument('input_file',
                        action='store',
                        type=argparse.FileType('rb'),
                        help='file to split')

    parser.add_argument('output_stem',
                        action='store',
                        type=str,
                        nargs="?",
                        default="",
                        help='stem for the output files, files will be named stem.NNN, where NNN is the share number')

    args = parser.parse_args()

    secret_file_path = pathlib.Path(args.input_file.name)
    secret_file_dir = secret_file_path.parents[0]

    output_stem = args.output_stem
    if output_stem == "":
        output_stem = secret_file_path.name

    x_values = core.pick_random_x_values(args.shares_count)

    shares = []
    for t in range(args.shares_count):
        output_path = secret_file_dir / (output_stem + "." + str(x_values[t]).zfill(3))
        shares.append(output_path.open("wb"))

    core.split(args.input_file, shares, args.shares_count, args.threshold, x_values)

    args.input_file.close()
    for share in shares:
        share.close()


if __name__ == '__main__':
    main()
