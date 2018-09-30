import app
import json
import os
import unittest


class AdvertiserTest(unittest.TestCase):

    PATH = os.getcwd() + '/fixtures/'

    def test_get_publisher_info(self):
        print(os.getcwd())
        filename = 'valid_basic_input.json'

        with open(self.PATH + filename) as f:
            data = json.load(f)

        publisher = app.get_publisher_info(data['site']['id'])
        publisher_id = publisher['publisher']['id']
        publisher_name = publisher['publisher']['name']

        self.assertIsNotNone(publisher_id)
        self.assertIsNotNone(publisher_name)

    def test_get_demographics_info(self):

        filename = 'valid_basic_input.json'

        with open(self.PATH + filename) as f:
            data = json.load(f)

        percent_female = app.get_demographics_info(data['site']['id'])
        percent_male = 100.0 - percent_female

        self.assertAlmostEqual(percent_male + percent_female, 100.0)

    def test_invalid_input(self):

        filename = 'invalid_basic_input.json'

        with open(self.PATH + filename) as f:
            data = json.load(f)

        self.assertIsNone(data['site']['id'])

        publisher = app.get_publisher_info(data['site']['id'])
        self.assertIsNone(publisher)

    def test_invalid_country_ip(self):
        filename = 'invalid_geo_input.json'

        with open(self.PATH + filename) as f:
            data = json.load(f)

        self.assertNotEqual(app.get_source_country(data['device']['ip']), 'United States')

def main():
    unittest.main()

if __name__ == "__main__":
    main()

