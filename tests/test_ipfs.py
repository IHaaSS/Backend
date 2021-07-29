import unittest
from dotenv import load_dotenv
load_dotenv()
from backend.storage import ipfs
from _test_data import *


class TestIPFS(unittest.TestCase):
    def test_write_file(self):
        with open(test_file, 'rb') as f:
            hash = ipfs.write_file(f)

        self.assertEqual(hash[:2], 'Qm')

    def test_write_json(self):
        data = {'content': 'test parent comment'}
        hash = ipfs.write_json(data)
        self.assertEqual(hash, comment1)

    def test_read_json(self):
        data = ipfs.read_json(comment1)
        self.assertIn('content', data)


if __name__ == '__main__':
    unittest.main()
