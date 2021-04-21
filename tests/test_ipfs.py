import unittest
from storage import ipfs

test_hash = "Qmdb6QCW1AWCyjrtLc8WXwFPU8fAh1ZvrVkqduFiVFiEYS"


class TestIPFS(unittest.TestCase):
    def test_write(self):
        data = {'test': 1}
        hash = ipfs.write_json(data)
        self.assertEqual(hash, test_hash)

    def test_read(self):
        data = ipfs.read_json(test_hash)
        self.assertEqual(data['test'], 1)


if __name__ == '__main__':
    unittest.main()
