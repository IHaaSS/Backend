import unittest
import json
from backend import create_app
from _test_data import *


class TestAPI(unittest.TestCase):
    def setUp(self):
        app = create_app()
        self.app = app.test_client()

    def test_post_incident(self):
        data = open(test_incident, 'r')
        response = self.app.post('/incidents', json=json.load(data))
        self.assertEqual(response.status_code, 200)

    def test_post_user_incident(self):
        data = open(test_incident, 'r')
        response = self.app.post('/user_incidents', json=json.load(data))
        self.assertEqual(response.status_code, 200)

    def test_approve_user_incident(self):
        response = self.app.post('/user_incidents/approve', json={'myId': 0})
        self.assertEqual(response.status_code, 200)

    def test_post_answer(self):
        data = {"id":9,"phase":1,"answers":[{"value":1,"attributeId":"2","topicId":1},{"value":1,"attributeId":"2","topicId":2},{"value":1,"attributeId":"3","topicId":4}]}
        response = self.app.post('/answer', json=data)
        self.assertEqual(response.status_code, 200)
        data = {"id":11,"phase":2,"answers":[{"value":1,"attributeId":"2-2-2-2","topicId":2}]}
        response = self.app.post('/answer', json=data)
        self.assertEqual(response.status_code, 200)

    def test_add_incident(self):
        incident = open(test_incident, 'r')
        attachment = open(test_file, 'rb')
        response = self.app.post('/contract/incidents', data={
            'incident': incident.read(),
            'attachment': attachment,
            'attachmentName': test_file
        }, content_type="multipart/form-data")
        incident.close()
        attachment.close()
        self.assertEqual(response.status_code, 200)

    def test_add_incident_comment(self):
        attachment = open(test_file, 'rb')
        response = self.app.post('/contract/incidents/comments', data={
            'parent': comment1b,
            'incident': incident1b,
            'attachment': attachment,
            'attachmentName': test_file
        }, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)

    def test_get_incidents(self):
        response = self.app.get('/contract/incidents')
        incidents = json.loads(response.data)
        self.assertGreaterEqual(len(incidents), 1)
        self.assertGreaterEqual(len(incidents[0]['comments']), 1)
        self.assertEqual(response.status_code, 200)

    def test_vote_incident(self):
        response = self.app.post('/contract/incidents/vote', json={
                                 'ref': incident1b,
                                 'vote': 1
        })
        self.assertEqual(response.status_code, 200)

    def test_vote_comment(self):
        ref = eth.keccak256(incident1b, 1).hex()
        response = self.app.post('/contract/incidents/comments/vote', json={
            'ref': ref,
            'vote': -1
        })
        self.assertEqual(response.status_code, 200)

    def test_ipfs(self):
        response = self.app.get('/ipfs/' + incident1)
        result = json.loads(response.data)
        self.assertEqual(len(result), 8)

    def test_ipfs_file(self):
        response = self.app.get('/ipfs/' + attachment)
        self.assertGreater(len(response.data)/1000, 100)


if __name__ == '__main__':
    unittest.main()
