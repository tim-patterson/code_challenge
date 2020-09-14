#!/usr/bin/python3

import random
import hashlib
import csv
import sys
from datetime import date, timedelta

def generate_csv(file, lines=100):
    '''
    Generates a csv file of random names, addresses and dates of birth
    '''
    writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('first_name', 'last_name', 'address', 'date_of_birth'))
    for _ in range(lines):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        address_num = random.randint(1,100)
        address_street = random.choice(STREET_NAMES)
        address_city = random.choice(CITIES)
        address = f'{address_num} {address_street}, {address_city}'
        date_of_birth = _generate_random_date_of_birth()
        writer.writerow((first_name, last_name, address, date_of_birth.isoformat()))
            

def _generate_random_date_of_birth():
    '''
    Returns a random date of birth for ages ~0-90 years.
    '''
    # The distribution of ages of a population is a complex thing.
    # A far better approximation would be to create a distribution
    # based on "real data" for the population, ie either census data
    # or a histogram of ages from the actual production data.
    return date.today() - timedelta(days=random.randint(1, 90*365))


def anonymise(input_file, output_file, salt):
    '''
    Anonymises the first_name, last_name and address of the input csv.
    '''
    # We really need to have more info about what we plan to do with the anonymised data
    # If simply being loaded into a transactional system for testing then setting the names
    # to "user<N>" and all the addresses to a constant of "1 dummy street, foobar" is more
    # than enough and is the lowest risk option as far as leakage goes.
    # 
    # If being used for testing data analysis then we may need to maintain certain relationships
    # and distributions.
    # For this exersice I'm going to assume:
    # 1. That we should maintain the ability to match people who live at the same address
    # 2. That we should maintain the ability to match people with the same last name.
    # 3. That we should maintain the ability to identify possible duplicates by matching on a full name.
    # 4. That we should minimise other leakage.
    # 5. That the anonymised data should be obviously anonymised to minimise the accidential mixing of test and prod data or systems
    reader = csv.reader(input_file, quoting=csv.QUOTE_MINIMAL)
    writer = csv.writer(output_file, quoting=csv.QUOTE_MINIMAL)

    # Copy across the header
    writer.writerow(next(reader))
    # Process the contents
    for row in reader:
        writer.writerow(anonymise_row(row, salt))

def anonymise_row(row, salt):
    (first_name, last_name, address, date_of_birth) = row
        
    # Anonymise Address
    m = hashlib.sha256(salt)
    m.update(address.encode('utf-8'))
    anonymised_address = '5 %s street, Some City' % m.hexdigest()[:10]

    # Anonymise LastName
    m = hashlib.sha256(salt)
    m.update(last_name.encode('utf-8'))
    anonymised_last_name = 'Last' + m.hexdigest()[:10]

    # Anonymise Firstname, we also want to salt with the last name here
    # to prevent leakage due to first name distributions etc.
    # By salting with the last name we still allow full name matches to be
    # able to happen
    m = hashlib.sha256(salt)
    m.update(last_name.encode('utf-8'))
    m.update(first_name.encode('utf-8'))
    anonymised_first_name = 'First' + m.hexdigest()[:6]
    return (anonymised_first_name, anonymised_last_name, anonymised_address, date_of_birth)

def main():
    '''
    Main constructs some sample data and then anonymises it.
    a single argument can be passed in to change the number of generated
    rows
    '''
    if len(sys.argv) >= 2:
        lines = int(sys.argv[1])
    else:
        lines = 100

    # Generate sample data
    with open('name_addresses.csv', mode='w') as address_file:
        generate_csv(address_file, lines)

    # Anonymise data
    # salt should be stored as a secret somewhere, it prevents being able to identify known
    # individuals in the dataset by simply following the anonymisation process.
    salt = b'abjewio3'
    with open('name_addresses.csv', mode='r') as input_file:
        with open('anonymised.csv', mode='w') as output_file:
            anonymise(input_file, output_file, salt)

### Data Section...
FIRST_NAMES = [
    'Eva',
    'Coreen',
    'Tisa',
    'Aldo',
    'Toshia',
    'Kayleen',
    'Prudence',
    'Dalton',
    'Phuong',
    'Wilton',
    'Hilaria',
    'Alpha',
    'Lakisha',
    'Brittaney',
    'Nicholas',
    'Cinthia',
    'Orpha',
    'Kerry',
    'Jamee',
    'Eusebio',
    'Lue',
    'Rosemarie',
    'Senaida',
    'Gabriella',
    'Lahoma',
    'Tuyet',
    'Kasey',
    'Kallie',
    'Dara',
    'Emmett',
]

LAST_NAMES = [
    'Davis',
    'Huber',
    'Blevins',
    'Shaw',
    'Bartlett',
    'Castillo',
    'Barrett',
    'Barrera',
    'Levine',
    'Cabrera',
    'Oneal',
    'Richardson',
    'Randall',
    'Fowler',
    'Bailey',
    'Frederick',
    'Beltran',
    'Soto',
    'Gross',
    'Stevenson',
]

STREET_NAMES = [
    'Country Club Road',
    'Berkshire Drive',
    'Willow Street',
    'Lafayette Avenue',
    'Park Street',
    '14th Street',
    'Hill Street',
    'Route 4',
    'Durham Court',
    'Dogwood Lane',
    'Hamilton Street',
    'Park Drive',
]

CITIES = [
    'Melbourne',
    'Sydney',
    'Wellington',
    'Auckland'
]

if __name__ == '__main__':
    main()