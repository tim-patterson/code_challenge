import os
from io import BytesIO
import unittest
from problem_1 import *

class LineProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.column_widths = [2,4,3]
        self.line_processor = LineProcessor(self.column_widths)

    def test_basic(self):
        delimited = self.line_processor.convert_line('123456789')
        self.assertEqual('12|3456|789', delimited)

    def test_padding(self):
        delimited = self.line_processor.convert_line('a b   c  ')
        self.assertEqual('a|b|c', delimited)

    def test_custom_padding(self):
        self.line_processor = LineProcessor(self.column_widths, padding_chars='~')
        delimited = self.line_processor.convert_line('a~b~~~c~~')
        self.assertEqual('a|b|c', delimited)

    def test_custom_delimiter(self):
        self.line_processor = LineProcessor(self.column_widths, delimiter=',')
        delimited = self.line_processor.convert_line('123456789')
        self.assertEqual('12,3456,789', delimited)

    @unittest.expectedFailure
    def test_shortline(self):
        delimited = self.line_processor.convert_line('12345')
    
    @unittest.expectedFailure
    def test_longline(self):
        delimited = self.line_processor.convert_line('1234567890')


class Problem1TestCase(unittest.TestCase):
    def setUp(self):
        self.column_widths = [2,4]
        self.column_names = None
        self.input_encoding = 'utf-8'
        self.output_encoding = 'utf-8'
    
    def execute(self, input):
        input_file = BytesIO(input)
        output_file = BytesIO()
        convert_file(
            self.column_widths,
            self.column_names,
            input_file,
            self.input_encoding,
            output_file,
            self.output_encoding)
        return output_file.getvalue()

    def test_basic(self):
        self.assertEqual(b'12|3456\n', self.execute(b'123456'))

    def test_multiline(self):
        self.assertEqual(b'12|3456\n34|5678\n', self.execute(b'123456\n345678'))

    def test_headers(self):
        self.column_names = ['col1', 'col2']
        self.assertEqual(b'col1|col2\n12|3456\n', self.execute(b'123456'))
    
    def test_input_encoding(self):
        self.input_encoding = 'utf-16be'
        self.assertEqual(b'12|3456\n', self.execute(b'\x001\x002\x003\x004\x005\x006'))

    def test_output_encoding(self):
        self.output_encoding = 'utf-16be'
        self.assertEqual(b'\x001\x002\x00|\x003\x004\x005\x006\x00\n', self.execute(b'123456'))

class Problem1IntegrationTestCase(unittest.TestCase):
    def test_cli(self):
        os.system("./problem_1.py --spec tests/test_data/spec.json tests/test_data/input.file > tests/test_data/output.file")
        with open('tests/test_data/expected.file', mode='rb') as f:
            expected = f.read()
        with open('tests/test_data/output.file', mode='rb') as f:
            actual = f.read()
        self.assertEqual(expected, actual)
