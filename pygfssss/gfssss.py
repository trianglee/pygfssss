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
import binascii
import sys
from io import BytesIO

from pygfssss import core


def split(args):
    shares = []
    for _ in range(args.shares_count):
        shares.append(BytesIO())

    core.split(sys.stdin.buffer, shares, args.shares_count, args.threshold)

    for share in shares:
        print(share.getvalue().hex())


def combine(_):
    shares_text = sys.stdin.readlines()
    shares_text = [t.strip() for t in shares_text]

    shares = []
    for share_text in shares_text:
        share_bin = binascii.unhexlify(share_text)
        shares.append(BytesIO(share_bin))

    output_secret = BytesIO()
    core.combine(shares, output_secret)
    sys.stdout.buffer.write(output_secret.getvalue())


def main():
    parser = argparse.ArgumentParser(
        description='pygfssss - split and combine secrets using Shamir Secret Sharing Scheme ' +
                    'over GF(256) with 0x11d prime polynomial')

    subparsers = parser.add_subparsers(title="commands",
                                       required=True,
                                       dest="command")

    split_parser = subparsers.add_parser('split',
                                         help="split secret into shares")
    split_parser.add_argument('threshold',
                              action='store',
                              type=int,
                              nargs="?",
                              default=3,
                              help='number of shares needed to combine')
    split_parser.add_argument('shares_count',
                              action='store',
                              type=int,
                              nargs="?",
                              default=5,
                              help='number of shares to create')
    split_parser.set_defaults(func=split)

    split_parser = subparsers.add_parser('combine',
                                         help="combine shares back into a secret")
    split_parser.set_defaults(func=combine)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
