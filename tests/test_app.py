import unittest

from app.app import app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_upload_no_file(self):
        response = self.client.post("/upload")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No file uploaded", response.data)


if __name__ == "__main__":
    unittest.main()
