#!/usr/bin/env python3
#
#  Copyright 2021 Nimrod Zimerman
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

import secrets

from pygfssss.GF256elt import GF256elt
from pygfssss.PGF256 import PGF256
from pygfssss.PGF256Interpolator import PGF256Interpolator


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


def split(secret_stream, share_streams, shares_count, shares_threshold, x_values=None):
    """
    Split bytes from 'secret_stream' into 'shares_count' share streams,
    with a combine threshold of "shares_threshold".
    If 'x_values' is provided from the outside, they aren't written to the shares.
    """
    if len(share_streams) != shares_count:
        raise Exception(f'Amount of streams {len(share_streams)} must be identical to shares count {shares_count}')

    if x_values is None:
        # Pick and emit random X values
        x_values = pick_random_x_values(shares_count)
        for i in range(0, shares_count):
            share_streams[i].write(bytes([x_values[i]]))

    # Loop through the stream bytes
    while True:
        data = secret_stream.read(1)
        if len(data) == 0:
            break
        byte = data[0]

        shares = split_byte(byte, shares_count, shares_threshold, x_values)

        for i in range(0, shares_count):
            share_streams[i].write(shares[i])


def combine(share_streams, secret_stream, x_values=None):
    """
    Combine shares from 'share_streams' into 'secret_stream'.
    If 'x_values' is provided from the outside, they aren't read from the shares.
    """
    interpolator = PGF256Interpolator()
    zero = GF256elt(0)

    if x_values is None:
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
        secret_stream.write(bytes([int(byte_value)]))


def main():
    from io import BytesIO

    secret = BytesIO(b"Too many secrets, Marty!")
    shares_count = 5
    shares_threshold = 3
    shares = []
    for _ in range(shares_count):
        shares.append(BytesIO())

    split(secret, shares, shares_count, shares_threshold)

    for share in shares:
        print(share.getvalue().hex())

    # Pick a subset of the shares at random
    shares_subset = secrets.SystemRandom().sample(shares, shares_threshold)
    for share in shares_subset:
        share.seek(0)

    output_secret = BytesIO()
    combine(shares_subset, output_secret)
    print(output_secret.getvalue())


if __name__ == "__main__":
    main()
