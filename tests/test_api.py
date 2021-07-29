import unittest
import json
from dotenv import load_dotenv
load_dotenv()
from backend import create_app
from _test_data import *


class TestAPI(unittest.TestCase):
    def setUp(self):
        app = create_app()
        self.app = app.test_client()

    def test_add_incident(self):
        incident = open('../data/entities.json', 'r')
        attachment = open(test_file, 'rb')
        response = self.app.post('/contract/incidents', data={
            'incident': incident.read(),
            'attachment': attachment,
            'attachmentName': test_file
        }, content_type="multipart/form-data")
        incident.close()
        attachment.close()
        self.assertEqual(response.status_code, 200)

    def test_incidents(self):
        response = self.app.get('/contract/incidents')
        incidents = json.loads(response.data)
        self.assertGreaterEqual(len(incidents), 1)
        self.assertGreaterEqual(len(incidents[0]['comments']), 1)
        self.assertEqual(response.status_code, 200)

    def test_ipfs(self):
        response = self.app.get('/ipfs/' + incident1)
        result = json.loads(response.data)
        self.assertEqual(len(result), 8)


if __name__ == '__main__':
    unittest.main()
