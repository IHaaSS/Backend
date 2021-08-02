import aiounittest
from dotenv import load_dotenv
load_dotenv()
from backend.storage import ipfs
from _test_data import *

text_hash = 'QmUmG4P2FwfXQcakZ7zxSgGV8DERRnAGRYrQ9BFg4gzTBB'
text = 'test text'


class TestIPFS(aiounittest.AsyncTestCase):
    async def test_write_file(self):
        with open(test_file, 'rb') as f:
            hash = await ipfs.write_file(f)

        self.assertEqual(hash[:2], 'Qm')

    def test_read_file(self):
        data = ipfs.read(attachment)
        self.assertGreater(len(data)/1024, 100)

    async def test_write_json(self):
        data = {'content': 'test parent comment'}
        hash = await ipfs.write_json(data)
        self.assertEqual(hash, comment1)

    def test_read_json(self):
        data = ipfs.read_json(incident1)
        self.assertIn('content', data)

    async def test_write_text(self):
        data = text
        hash = await ipfs.write_str(data)
        self.assertEqual(hash[:2], 'Qm')

    def test_read_text(self):
        data = ipfs.read(text_hash)
        self.assertEqual(data, text)


if __name__ == '__main__':
    aiounittest.main()
