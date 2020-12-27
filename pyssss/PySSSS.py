#!/usr/bin/env python
#
#  Copyright 2020 Nimrod Zimerman
#  Copyright 2010 Mathias Herberts
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
# -*- coding: utf-8 -*-
import secrets

from pyssss.GF256elt import GF256elt
from pyssss.PGF256 import PGF256
from pyssss.PGF256Interpolator import PGF256Interpolator


def pick_random_polynomial(degree, value):
    """
    Pick a random PGF256 polynomial P such that P(0) = value
    """

    # noinspection PyListCreation
    coeffs = []

    # Set f(0)
    coeffs.append(value)

    # Pick coefficients for x^n with n <= degree
    for c in range(1, degree + 1):
        coeffs.append(GF256elt(secrets.SystemRandom().randint(0, 255)))

    return PGF256(coeffs)


def pick_random_x_values(n):
    # X values must be within the range [1,255], and must not have duplicates.
    return secrets.SystemRandom().sample(range(1, 255+1), n)


def split_byte(byte, shares_count, shares_threshold, x_values):
    # Pick a random polynomial
    poly = pick_random_polynomial(shares_threshold - 1, GF256elt(byte))

    # Generate the shares
    shares = []

    for i in range(0, shares_count):
        x = GF256elt(x_values[i])
        y = poly.f(x)

        shares.append(bytes([int(y)]))

    return shares


def split(plaintext_stream, share_streams, shares_count, shares_threshold):
    """
    Split bytes from 'plaintext_stream' into 'shares_count' share streams,
    with a combine threshold of "shares_threshold".
    """
    if len(share_streams) != shares_count:
        raise Exception(f'Amount of streams {len(share_streams)} must be identical to shares count {shares_count}')

    # Pick and emit random X values
    x_values = pick_random_x_values(shares_count)
    for i in range(0, shares_count):
        share_streams[i].write(bytes([x_values[i]]))

    # Loop through the stream bytes
    while True:
        data = plaintext_stream.read(1)
        if len(data) == 0:
            break
        byte = data[0]

        shares = split_byte(byte, shares_count, shares_threshold, x_values)

        for i in range(0, shares_count):
            share_streams[i].write(shares[i])


def combine(share_streams, plaintext_stream):
    interpolator = PGF256Interpolator()
    zero = GF256elt(0)

    # Read X values
    x_values = []
    for i in range(0, len(share_streams)):
        data = share_streams[i].read(1)
        if len(data) == 0:
            raise Exception(f'Unexpected EOF while reading X of share {i}')
        x_values.append(data[0])

    end_of_share = False
    while not end_of_share:
        points = []
        i = 0
        for i in range(0, len(share_streams)):
            # Extract Y
            data = share_streams[i].read(1)
            if len(data) == 0:
                end_of_share = True
                break
            y = data[0]

            # Push point
            points.append((GF256elt(x_values[i]), GF256elt(y)))

        if end_of_share:
            if i != 0:
                raise Exception(f'Unexpected EOF while reading share {i}')
            break

        # Decode next byte
        byte_value = interpolator.interpolate(points).f(zero)
        plaintext_stream.write(bytes([int(byte_value)]))


def main():
    from io import BytesIO

    plaintext = BytesIO(b"Too many secrets, Marty!")
    shares_count = 5
    shares_threshold = 3
    shares = []
    for _ in range(shares_count):
        shares.append(BytesIO())

    split(plaintext, shares, shares_count, shares_threshold)

    for share in shares:
        print(share.getvalue().hex())

    # Pick a subset of the shares at random
    shares_subset = secrets.SystemRandom().sample(shares, shares_threshold)
    for share in shares_subset:
        share.seek(0)

    output_plaintext = BytesIO()
    combine(shares_subset, output_plaintext)
    print(output_plaintext.getvalue())


if __name__ == "__main__":
    main()
