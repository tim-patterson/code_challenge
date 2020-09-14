#!/usr/bin/python3

import argparse
import json
import sys
from io import TextIOWrapper

class ParseError(Exception):
    pass

class LineProcessor:
    '''
    Class converts fixed width lines to delimited.
    '''
    def __init__(self, column_widths, padding_chars=None, delimiter='|'):
        '''
        Creates a new line processor, column_widths are the widths of the
        fixed width fields in code points, the padding_chars are the padding
        fields used in the fixed width data - defaults to whitespace chars,
        delimiter is the delimiter to use for writing out the data.
        '''
        self._column_slices = self._build_column_slices(column_widths)
        self._line_length = sum(column_widths)
        self._padding_chars = padding_chars
        self._delimiter = delimiter

    def convert_line(self, line):
        '''
        Parses a fixed width input line and returns its in delimited form.
        '''
        if len(line) != self._line_length:
            raise ParseError(f'unexpected line length, expected {self._line_length} got {len(line)} for line "{line}"')

        fields = self._split_fw_line(line)
        return self.render_delimited_line(fields)

    def render_delimited_line(self, fields):
        '''
        Renders a list of (string) fields as a delimited line,
        Note this currently doesn't handle any escaping or quoting of embedded delimiters
        '''
        return self._delimiter.join(fields)

    def _split_fw_line(self, line):
        '''
        Splits the input line into fields based on the column_slices.
        The input line should be of type text and the column_slices
        in unicode code points.
        The returned fields are trimmed of extra characters based on the
        padding_chars
        '''
        return [line[cs].rstrip(self._padding_chars) for cs in self._column_slices]

    def _build_column_slices(self, field_widths):
        '''
        Takes the field widths and builds slices.
        field widths should be integer types
        '''
        offset = 0
        slices = []
        for fw in field_widths:
            slices.append(slice(offset, offset + fw))
            offset += fw
        return slices


def main(args=None):
    parser = argparse.ArgumentParser(description='Convert fixed width input to delimited')
    parser.add_argument('--spec', dest='specfile', required=True)
    parser.add_argument('file', nargs='?', default='-')
    parsed = parser.parse_args(args)

    ## Read the spec
    with open(parsed.specfile, mode='rb') as f:
        spec = json.load(f)
    
    column_widths = [int(offset) for offset in spec['Offsets']]

    if spec['IncludeHeader'].upper() == 'TRUE':
        column_names = spec['ColumnNames']
    else:
        column_names = None

    input_encoding = spec['FixedWidthEncoding']
    output_encoding = spec['DelimitedEncoding']

    output_file = sys.stdout.buffer

    if parsed.file == '-':
        convert_file(column_widths, column_names, sys.stdin.buffer, input_encoding, output_file, output_encoding)
    else:
        with open(parsed.file, mode='rb') as input_file:
            convert_file(column_widths, column_names, input_file, input_encoding, output_file, output_encoding)

def convert_file(column_widths, column_names, input_file, input_encoding, output_file, output_encoding):
    '''
    Converts a file from fixed width to delimited.
    column_widths is the width of each field.
    column_names is the headers to use for the delimited file, None means don't write a header.
    input_file/input_encoding is the file(bytes) and encoding to use for the input
    output_file/output_encoding is the file(bytes) and encoding to use for the output
    '''
    input_reader = TextIOWrapper(input_file, encoding=input_encoding)
    output_writer = TextIOWrapper(output_file, encoding=output_encoding)
    try:
        line_processor = LineProcessor(column_widths)

        if column_names:
            delimited_line = line_processor.render_delimited_line(column_names)
            output_writer.write(delimited_line)
            output_writer.write('\n')

        for line in input_reader:
            delimited_line = line_processor.convert_line(line.rstrip('\n'))
            output_writer.write(delimited_line)
            output_writer.write('\n')
    finally:
        # Python has some weird and inconsistent behavour around file/stream wrappers taking ownership and
        # closing the underlying files, we want to opt out of that behaviour in this case
        input_reader.detach()
        output_writer.detach()


if __name__ == '__main__':
    main()