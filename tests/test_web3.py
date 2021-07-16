import unittest
import os
from base58 import b58decode
from dotenv import load_dotenv
os.chdir('..')
load_dotenv()
from storage import ethereum

ipfsRef = "Qmdb6QCW1AWCyjrtLc8WXwFPU8fAh1ZvrVkqduFiVFiEYS"
bytes = '0x' + bytearray(b58decode(ipfsRef)).hex()[4:]


class TestWeb3(unittest.TestCase):

    def test_add_incident(self):
        res = ethereum.add_incident(bytes, [{'name': 'test', 'content': bytes}])
        self.assertEqual(res, '')

    def test_get_incidents(self):
        incidents = ethereum.get_incidents()
        self.assertGreater(len(incidents), 0)

    def test_get_incident(self):
        res = ethereum.get_incident(bytes)
        self.assertEqual(len(res), 32)

    def test_vote_incident(self):
        res = ethereum.vote_incident(bytes, True)
        self.assertEqual(len(res), 32)

    def test_remove_incident(self):
        res = ethereum.remove_incident(bytes, 0)
        self.assertEqual(len(res), 32)


if __name__ == '__main__':
    unittest.main()
