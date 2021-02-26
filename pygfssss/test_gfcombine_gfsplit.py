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
import pathlib
import random
import subprocess
import sys
import tempfile
import unittest


class TestGfsplitGfcombine(unittest.TestCase):

    def run_gfsplit_gfcombine(self, threshold, shares_count_to_create, share_indices_to_combine, secret_bytes_count):
        python_bin = sys.executable

        input_file_name = "input.txt"

        temp_dir = tempfile.TemporaryDirectory()
        temp_dir_path = pathlib.Path(temp_dir.name)

        input_file_path = temp_dir_path / input_file_name

        f = input_file_path.open("wb")
        # Generate deterministic random bytes content using deterministic seed.
        rnd = random.Random(str(threshold) + str(shares_count_to_create) + str(share_indices_to_combine) +
                            str(secret_bytes_count))
        secret_bytes = bytes([rnd.randint(0, 255) for _ in range(secret_bytes_count)])
        f.write(secret_bytes)
        f.close()

        subprocess.check_call(f"{python_bin} gfsplit.py -n {threshold} -m {shares_count_to_create} {input_file_path}",
                              shell=True)

        shares = temp_dir_path.glob(f"{input_file_name}.*")
        shares = [str(share) for share in shares]

        shares_subset = [shares[t] for t in share_indices_to_combine]
        shares_file_paths = " ".join(shares_subset)

        output_file_path = temp_dir_path / "output.txt"

        subprocess.check_call(f"{python_bin} gfcombine.py {shares_file_paths} -o {output_file_path}", shell=True)

        with open(output_file_path, "rb") as f:
            secret_bytes_output = f.read()

        temp_dir.cleanup()

        self.assertEqual(secret_bytes, secret_bytes_output)

    def test_split_combine_simple(self):
        self.run_gfsplit_gfcombine(3, 5, [0, 1, 4], 20)

    def test_split_combine_all_shares(self):
        self.run_gfsplit_gfcombine(15, 15, range(0, 15), 150)

    def test_split_combine_one_share(self):
        self.run_gfsplit_gfcombine(1, 7, [4], 45)

    def test_split_combine_permutations(self):
        share_indices = range(0, 4)
        for subset in itertools.permutations(share_indices, 2):
            self.run_gfsplit_gfcombine(2, 4, subset, 100)


if __name__ == '__main__':
    unittest.main()
