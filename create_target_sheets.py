#!/usr/bin/env python3

'''
Generate printable PDF of circular coded photogrammetry targets described by
(expired) patent DE19733466A1.

Requires Inkscape and PDFtk.

Matthew Petroff <https://mpetroff.net>, 2018

This script is released into the public domain using the CC0 1.0 Public
Domain Dedication: https://creativecommons.org/publicdomain/zero/1.0/
'''

import subprocess
import tempfile
import os.path
import math
import numpy as np

import find_codes

UNIT = 'in'         # SVG unit
WIDTH = 8.5         # Page width
HEIGHT = 11         # Page height
DOT_DIAMETER = 0.4  # Diameter of dot at center of target
ROWS = 5            # Rows of targets per page
COLUMNS = 4         # Columns of targets per page
X_MARGIN = 0.65     # X-axis page margin for targets
Y_MARGIN = 0.9      # Y-axis page margin for targets
BACKGROUND_X_MARGIN = 0.25  # X-axis page margin for black background
BACKGROUND_Y_MARGIN = 0.5   # Y-axis page margin for black background
CODES = find_codes.generate_codes(14)   # Codes for targets
FILENAME = 'targets.pdf'

def add_target(x_center, y_center, dot_radius, code, code_num, first_segment):
    '''
    Returns SVG data for a given target.
    '''
    out = '<circle fill="#fff" cx="{}" cy="{}" r="{}"/>\n'.format(x_center, \
        y_center, dot_radius)
    out += '<g stroke="#fff" stroke-width="{}" fill="none">\n'.format( \
        dot_radius)
    for i in range(14):
        if (1 << (13-i)) & code:
            x_start = np.cos(np.deg2rad(360 / 14 * i)) * dot_radius * 2.5
            y_start = np.sin(np.deg2rad(360 / 14 * i)) * dot_radius * 2.5
            x_end = np.cos(np.deg2rad(360 / 14 * (i + 1))) \
                * dot_radius * 2.5 - x_start
            y_end = np.sin(np.deg2rad(360 / 14 * (i + 1))) \
                * dot_radius * 2.5 - y_start
            x_start += x_center
            y_start += y_center
            out += '<path fill="#fff" d="m{} {}a{} {} 0 0 1 {} {}"' \
                ' {}/>\n'.format(x_start, y_start, dot_radius * 2.5, \
                dot_radius * 2.5, x_end, y_end, \
                'id="first"' if first_segment else '')
            first_segment = False
    out += '</g>\n'
    out += '<text x="{}" y="{}" font-size="{}" alignment-base="bottom" ' \
        'font-family="Source Sans Pro, sans-serif" fill="#fff">{}' \
        '</text>'.format(x_center - dot_radius * 3, \
        y_center + dot_radius * 3, dot_radius / 2, code_num + 1)
    return out

def create_sheet(n, pdf_filename):
    '''
    Constructs SVG file for sheet of targets and then uses Inkscape to combine
    adjacent target segments into a single path and to export a PDF.
    '''
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="{w}{u}" ' \
        'height="{h}{u}" version="1.1" viewBox="0 0 {w} {h}">\n'.format( \
        w=WIDTH, h=HEIGHT, u=UNIT)
    target_size = DOT_DIAMETER * 3
    x_spacing = (WIDTH - X_MARGIN * 2 - target_size) / (COLUMNS - 1)
    y_spacing = (HEIGHT - Y_MARGIN * 2 - target_size) / (ROWS - 1)
    svg += '<rect x="{}" y="{}" width="{}" height="{}"/>'.format( \
        BACKGROUND_X_MARGIN, BACKGROUND_Y_MARGIN, \
        WIDTH - BACKGROUND_X_MARGIN * 2, HEIGHT - BACKGROUND_Y_MARGIN * 2)
    for i in range(ROWS):
        for j in range(COLUMNS):
            num = n * COLUMNS * ROWS + i * COLUMNS + j
            if num < len(CODES):
                svg += add_target(X_MARGIN + target_size / 2 + j * x_spacing,
                                  Y_MARGIN + target_size / 2 + i * y_spacing,
                                  DOT_DIAMETER / 2, CODES[num], num,
                                  i == 0 and j == 0)
    svg += '</svg>'

    svg_filename = os.path.join(tmp_dir, 'sheet.svg')
    with open(svg_filename, 'w') as out_file:
        out_file.write(svg)
    subprocess.run(['inkscape', '-g', '--select=first',
                    '--verb', 'EditSelectSameObjectType',
                    '--verb', 'StrokeToPath', '--verb', 'SelectionUnion',
                    '--verb', 'FileSave', '--verb', 'FileQuit', svg_filename])
    subprocess.run(['inkscape', '--export-pdf=' + pdf_filename, svg_filename])

with tempfile.TemporaryDirectory() as tmp_dir:
    # Create sheets of targets in temporary directory
    pdfs = []
    for n in range(math.ceil(len(CODES) / ROWS / COLUMNS)):
        pdf_filename = os.path.join(tmp_dir, str(n) + '.pdf')
        create_sheet(n, pdf_filename)
        pdfs.append(pdf_filename)
    # Combine sheets into a single PDF
    subprocess.run(['pdftk'] + pdfs + ['cat', 'output', FILENAME])
