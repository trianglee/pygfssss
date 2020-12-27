#!/usr/bin/env python
#
#  Copyright 2020 Nimrod Zimerman
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

import itertools
import unittest
from io import BytesIO

from pyssss import PySSSS


class TestPySSSS(unittest.TestCase):

    def test_simple_split_combine(self):

        plaintext = BytesIO(b"Too many secrets, Marty!")
        shares_count = 7
        shares_threshold = 5
        shares = []
        for _ in range(shares_count):
            shares.append(BytesIO())

        PySSSS.split(plaintext, shares, shares_count, shares_threshold)

        # Pick a subset of the shares
        shares_subset = shares[1:shares_threshold+1]
        for share in shares_subset:
            share.seek(0)

        output_plaintext = BytesIO()
        PySSSS.combine(shares_subset, output_plaintext)

        self.assertEqual(output_plaintext.getvalue(), plaintext.getvalue())

    def test_single_share(self):

        plaintext = BytesIO(b"The biggest guru-mantra is: never share your secrets with anybody. It will destroy you.")
        shares_count = 1
        shares_threshold = 1
        shares = []
        for _ in range(shares_count):
            shares.append(BytesIO())

        PySSSS.split(plaintext, shares, shares_count, shares_threshold)

        for share in shares:
            share.seek(0)

        output_plaintext = BytesIO()
        PySSSS.combine(shares, output_plaintext)

        self.assertEqual(output_plaintext.getvalue(), plaintext.getvalue())

    def test_single_threshold(self):

        plaintext = BytesIO(
            b"If you reveal your secrets to the wind, you should not blame the wind for revealing them to the trees.")
        shares_count = 2
        shares_threshold = 1
        shares = []
        for _ in range(shares_count):
            shares.append(BytesIO())

        PySSSS.split(plaintext, shares, shares_count, shares_threshold)

        # Pick a subset of the shares
        shares_subset = shares[1:shares_threshold+1]
        for share in shares_subset:
            share.seek(0)

        output_plaintext = BytesIO()
        PySSSS.combine(shares_subset, output_plaintext)

        self.assertEqual(output_plaintext.getvalue(), plaintext.getvalue())

    def test_threshold_shares(self):

        plaintext = BytesIO(b"I don't have any secrets I need kept any more.")
        shares_count = 10
        shares_threshold = 10
        shares = []
        for _ in range(shares_count):
            shares.append(BytesIO())

        PySSSS.split(plaintext, shares, shares_count, shares_threshold)

        for share in shares:
            share.seek(0)

        output_plaintext = BytesIO()
        PySSSS.combine(shares, output_plaintext)

        self.assertEqual(output_plaintext.getvalue(), plaintext.getvalue())

    def test_binary(self):

        plaintext = BytesIO(b"\x00\x01\xff\xfa\xba\xba\xfa\xfb")
        shares_count = 5
        shares_threshold = 3
        shares = []
        for _ in range(shares_count):
            shares.append(BytesIO())

        PySSSS.split(plaintext, shares, shares_count, shares_threshold)

        # Pick a subset of the shares
        shares_subset = shares[1:shares_threshold+1]
        for share in shares_subset:
            share.seek(0)

        output_plaintext = BytesIO()
        PySSSS.combine(shares_subset, output_plaintext)

        self.assertEqual(output_plaintext.getvalue(), plaintext.getvalue())

    def test_empty_plaintext(self):

        plaintext = BytesIO(b"")
        shares_count = 5
        shares_threshold = 3
        shares = []
        for _ in range(shares_count):
            shares.append(BytesIO())

        PySSSS.split(plaintext, shares, shares_count, shares_threshold)

        # Pick a subset of the shares
        shares_subset = shares[1:shares_threshold+1]
        for share in shares_subset:
            share.seek(0)

        output_plaintext = BytesIO()
        PySSSS.combine(shares_subset, output_plaintext)

        self.assertEqual(output_plaintext.getvalue(), plaintext.getvalue())

    def test_all_permutations(self):

        plaintext = BytesIO(b"Do not tell secrets to those whose faith and silence you have not already tested.")
        shares_count = 4
        shares_threshold = 2
        shares = []
        for _ in range(shares_count):
            shares.append(BytesIO())

        PySSSS.split(plaintext, shares, shares_count, shares_threshold)

        # Pick all subsets shares of size larger than or equal to shares_threshold,
        # and verify the plaintext is the same for all
        for shares_subset_count in range(shares_threshold, shares_count + 1):
            for shares_subset in itertools.permutations(shares, shares_subset_count):
                for share in shares_subset:
                    share.seek(0)

                output_plaintext = BytesIO()
                PySSSS.combine(shares_subset, output_plaintext)

                self.assertEqual(output_plaintext.getvalue(), plaintext.getvalue())

    def test_external_x_values(self):

        plaintext = BytesIO(b"The only secrets are the secrets that keep themselves.")
        shares_count = 5
        shares_threshold = 3
        shares = []
        for _ in range(shares_count):
            shares.append(BytesIO())

        x_values = [10, 20, 30, 40, 50]

        PySSSS.split(plaintext, shares, shares_count, shares_threshold, x_values)

        # Pick a subset of the shares
        shares_subset = shares[1:shares_threshold+1]
        x_values_subset = x_values[1:shares_threshold+1]
        for share in shares_subset:
            share.seek(0)

        output_plaintext = BytesIO()
        PySSSS.combine(shares_subset, output_plaintext, x_values_subset)

        self.assertEqual(output_plaintext.getvalue(), plaintext.getvalue())


if __name__ == '__main__':
    unittest.main()
