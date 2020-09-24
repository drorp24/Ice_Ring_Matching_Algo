import json
import unittest


class JsonFileReader(object):

    def __init__(self, file_name):
        # read file
        with open(file_name, 'r') as my_file:
            data = my_file.read()

        # parse file
        obj = json.loads(data)

class JsonFileReaderTestCase(unittest.TestCase):


    def basic_test(self):
        print('ss')
        reader = JsonFileReader('DeliveryRequest.json')

        self.assertIsNotNone(reader)


