#!/usr/bin/env python3

'''
Generate codes for circular coded photogrammetry targets.

Implementation of coding scheme of (expired) patent DE19733466A1.
https://patents.google.com/patent/DE19733466A1/
https://register.dpma.de/DPMAregister/pat/register?AKZ=197334660

Matthew Petroff <https://mpetroff.net>, 2018

This script is released into the public domain using the CC0 1.0 Public
Domain Dedication: https://creativecommons.org/publicdomain/zero/1.0/
'''

import argparse

def bitwise_rotate_left(val, bits, total_bits):
    '''
    Perform a bitwise rotation to the left.
    '''
    return (val << bits) & (2**total_bits-1) \
        | ((val & (2**total_bits-1)) >> total_bits-bits)

def find_smallest_rotation(val, total_bits):
    '''
    Check all bitwise rotations to find smallest representation.
    '''
    smallest = val
    for i in range(1, total_bits):
        smallest = min(bitwise_rotate_left(val, i, total_bits), smallest)
    return smallest

def calc_parity(val):
    '''
    Returns True if even parity, else False.
    '''
    parity = True
    while val:
        parity = not parity
        val = val & (val - 1)
    return parity

def count_bit_transitions(val):
    '''
    Count number of bit transitions.
    '''
    transitions = 0
    prev_bit = 0
    while val:
        new_bit = val & 1
        if new_bit > prev_bit:
            transitions += 1
        prev_bit = new_bit
        val >>= 1
    return transitions

def generate_codes(bits, transitions=None):
    '''
    Generate codes for a given number of bits and, optionally, a given number
    of transitions. Number of bits should be even.
    '''
    codes = []
    # Codes all start with 0 and end with 1, allowing us to check fewer numbers
    for i in range(2**(bits-2)):
        # Add 1 bit to end
        code = (i << 1) + 1

        # Perform cyclic shift to minimize value
        code = find_smallest_rotation(code, bits)

        # Check which pairs of opposite segments are both 1
        half_bits = bits >> 1
        diff = (code & (2**half_bits-1)) \
            & ((code & ((2**half_bits-1) << half_bits)) >> half_bits)

        # Find parity
        parity = calc_parity(code)

        # Count number of transitions
        num_transitions = count_bit_transitions(code) if transitions else None

        # Find unique codes with even parity and at least one pair of opposite
        # segments that are both 1 (and correct number of transitions,
        # if applicable)
        if parity and diff > 0 and transitions == num_transitions \
            and code not in codes:
            codes.append(code)

    return codes

def main():
    '''
    Process arguments and generate codes.
    '''
    parser = argparse.ArgumentParser( \
        description='Generate codes for circular coded photogrammetry targets.')
    parser.add_argument('bits', metavar='N', type=int, nargs=1,
                        help='Number of bits in target (even integer)')
    parser.add_argument('--transitions', metavar='T', type=int, nargs=1,
                        help='Number of transitions')
    args = parser.parse_args()
    if args.bits[0] % 2 != 0:
        raise ValueError('Number of bits must be even!')
    if args.bits[0] <= 0:
        raise ValueError('Number of bits must be positive!')
    transitions = None
    if args.transitions:
        if args.transitions[0] <= 0:
            raise ValueError('Number of transitions must be positive!')
        transitions = args.transitions[0]

    codes = generate_codes(args.bits[0], transitions)
    print('Codes (as binary):')
    for code in codes:
        print('{:0{width}b}'.format(code, width=args.bits[0]))
    print('\nCodes (as integer):')
    print(codes)
    print('\nNumber of codes:', len(codes))

if __name__ == '__main__':
    main()
