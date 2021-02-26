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
import re

from pygfssss import core


def main():
    parser = argparse.ArgumentParser(
        description='gfcombine, input compatible with http://manpages.ubuntu.com/manpages/bionic/man1/gfcombine.1.html')

    parser.add_argument('-o',
                        dest='output_file',
                        action='store',
                        type=str,
                        default="",
                        help='filename to write the combined result to')

    parser.add_argument('input_file',
                        action='store',
                        type=str,
                        nargs="+",
                        help='shares to combine, must be named something.NNN, where NNN is the share number')

    args = parser.parse_args()

    x_values = []
    shares = []
    for input_file in args.input_file:
        matches = re.match(".*[.]([0-9][0-9][0-9])", input_file)
        if matches is None:
            raise Exception(f"Share files must be with a numeric .NNN suffix, '{input_file}' isn't")
        x_values.append(int(matches[1]))
        shares.append(open(input_file, "rb"))

    output_file_path = args.output_file
    if output_file_path == "":
        p = pathlib.Path(args.input_file[0])
        output_file_path = str(p.parents[0] / p.stem)

    output_file = open(output_file_path, "wb")

    core.combine(shares, output_file, x_values)

    output_file.close()
    for share in shares:
        share.close()


if __name__ == '__main__':
    main()
