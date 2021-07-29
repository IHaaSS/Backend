import aiounittest
import unittest
from dotenv import load_dotenv

load_dotenv()
from backend.storage import ethereum as eth
from _test_data import *

incident1b = eth.ipfs2bytes(incident1)
incident2b = eth.ipfs2bytes(incident2)
comment1b = eth.ipfs2bytes(comment1)
comment2b = eth.ipfs2bytes(comment2)
attachb = eth.ipfs2bytes(attachment)


class TestWeb3(aiounittest.AsyncTestCase):

    @unittest.skip
    def test_init_contract(self):
        eth.add_incident(incident1b, [{'name': 'test', 'content': attachb}])
        eth.add_incident(incident2b, [])
        eth.add_comment(comment1b, incident1b, comment1b, [('testattachment', attachb)])
        eth.add_comment(comment1b, incident1b, comment2b, [])
        eth.add_comment(comment1b, incident2b, comment1b, [])

    def test_add_incident(self):
        res = eth.add_incident(incident1, [{'name': 'test', 'content': attachb}])
        self.assertEqual(len(res), 32)

    def test_get_incidents(self):
        incidents = eth.get_incidents()
        self.assertGreater(len(incidents), 0)

    def test_get_incident(self):
        res = eth.get_incident(incident1b)
        self.assertEqual(len(res), 7)

    def test_vote_incident(self):
        res = eth.vote_incident(incident1b, True)
        self.assertEqual(len(res), 32)

    def test_remove_incident(self):
        res = eth.remove_incident(incident1b, 0)
        self.assertEqual(len(res), 32)

    async def test_get_comment(self):
        res = await eth.get_comment(bytes, 0)
        self.assertEqual(len(res), 7)

    def test_add_comment(self):
        res = eth.add_comment(comment1b, incident1b, comment1b, [('testattachment', attachb)])
        self.assertEqual(len(res), 32)


if __name__ == '__main__':
    aiounittest.main()
