from io import StringIO
import unittest
import csv
from datetime import date
from problem_2 import *

class GenerateTestCase(unittest.TestCase):
    def test_generate_csv(self):
        csv_file = StringIO()
        generate_csv(csv_file, lines=3)

        lines = csv_file.getvalue().splitlines()
        # We expect 3 data lines and 1 header
        self.assertEqual(4, len(lines))
        # Check the header line
        self.assertEqual('first_name,last_name,address,date_of_birth', lines[0])

        csv_file.seek(0)
        csv_reader = csv.reader(csv_file)
        # consume the header
        next(csv_reader)

        rows = list(csv_reader)
        # check the dates are valid
        for row in rows:
            date_of_birth = row[3]
            date.fromisoformat(date_of_birth)
        
        # check that fields are unique(ish)
        for field_idx in [0,1,2,3]:
            unique_values = set([row[field_idx] for row in rows])
            self.assertGreater(len(unique_values), 1)

class AnonymiseTestCase(unittest.TestCase):
    def test_first_name(self):
        salt = b'1234'
        row1 = ('tim', 'last', 'address', '2000-01-01')
        row2 = ('bob', 'last', 'address', '2000-01-01')
        row3 = ('tim', 'last', 'address2', '2000-01-02')
        row4 = ('tim', 'last2', 'address1', '2000-01-02')

        # Check that for any given lastname the first name is anonymised to the same value
        self.assertEqual(anonymise_row(row1, salt)[0], anonymise_row(row3, salt)[0])

        # Check that different first name's are anonymised to different values
        self.assertNotEqual(anonymise_row(row1, salt)[0], anonymise_row(row2, salt)[0])

        # Check that same first name is anonymised to different values if the last names are different
        self.assertNotEqual(anonymise_row(row1, salt)[0], anonymise_row(row4, salt)[0])
    
    def test_last_name(self):
        salt = b'1234'
        row1 = ('first', 'smith', 'address', '2000-01-01')
        row2 = ('first', 'baker', 'address', '2000-01-01')

        # Check that different last name's are anonymised to different values
        self.assertNotEqual(anonymise_row(row1, salt)[1], anonymise_row(row2, salt)[1])

    def test_address(self):
        salt = b'1234'
        row1 = ('first', 'last', 'address1', '2000-01-01')
        row2 = ('first', 'last', 'address2', '2000-01-01')
        row3 = ('first2', 'last2', 'address1', '2000-01-02')

        # Check that the same address anonymises to the same value.
        self.assertEqual(anonymise_row(row1, salt)[2], anonymise_row(row3, salt)[2])

        # Check that different addresses anonymises to different values.
        self.assertNotEqual(anonymise_row(row1, salt)[2], anonymise_row(row2, salt)[2])

    def test_date_of_birth(self):
        salt = b'1234'
        row1 = ('first', 'last', 'address1', '2000-04-05')

        # Check that the dates of birth are passed through
        self.assertEqual(row1[3], anonymise_row(row1, salt)[3])