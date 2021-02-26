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

import itertools
import random
import subprocess
import sys
import unittest


class TestGfssss(unittest.TestCase):

    def run_split_combine(self, threshold, shares_count_to_create, share_indices_to_combine, secret_bytes_count):
        python_bin = sys.executable

        # Generate deterministic random bytes content using deterministic seed.
        rnd = random.Random(str(threshold) + str(shares_count_to_create) + str(share_indices_to_combine) +
                            str(secret_bytes_count))
        secret_bytes = bytes([rnd.randint(0, 255) for _ in range(secret_bytes_count)])

        result = subprocess.run(
            f"{python_bin} gfssss.py split {threshold} {shares_count_to_create}",
            input=secret_bytes,
            capture_output=True,
            check=True,
            shell=True)

        shares_bin = result.stdout
        shares_text = shares_bin.decode("ascii")

        shares = shares_text.splitlines()
        shares_subset = [shares[t] for t in share_indices_to_combine]

        shares_subset_text = "\n".join(shares_subset)
        shares_subset_bin = bytes(shares_subset_text, "ascii")

        result = subprocess.run(
            f"{python_bin} gfssss.py combine",
            input=shares_subset_bin,
            capture_output=True,
            check=True,
            shell=True)

        secret_bytes_output = result.stdout

        self.assertEqual(secret_bytes, secret_bytes_output)

    def test_split_combine_simple(self):
        self.run_split_combine(3, 5, [0, 1, 4], 20)

    def test_split_combine_all_shares(self):
        self.run_split_combine(15, 15, range(0, 15), 150)

    def test_split_combine_one_share(self):
        self.run_split_combine(1, 7, [4], 45)

    def test_split_combine_permutations(self):
        share_indices = range(0, 4)
        for subset in itertools.permutations(share_indices, 2):
            self.run_split_combine(2, 4, subset, 100)


if __name__ == '__main__':
    unittest.main()
