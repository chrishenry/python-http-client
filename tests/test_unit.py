import os
from os import path
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from python_http_client.client import Client, Response


try:
    # Python 3
    import urllib.request as urllib
except ImportError:
    # Python 2
    import urllib2 as urllib


try:
    basestring
except NameError:
    basestring = str


class MockResponse(urllib.HTTPSHandler):

    def __init__(self, response_code):
        self.response_code = response_code

    def getcode(self):
        return self.response_code

    def info(self):
        return 'HEADERS'

    def read(self):
        return 'RESPONSE BODY'


class MockClient(Client):

    def __init__(self, host, response_code):
        self.response_code = 200
        Client.__init__(self, host)

    def _make_request(self, opener, request):
        return MockResponse(self.response_code)


class TestClient(unittest.TestCase):
    def setUp(self):
        self.host = 'http://api.test.com'
        self.client = Client(host=self.host)
        self.api_key = "SENDGRID_API_KEY"
        self.request_headers = {
                                 'Content-Type': 'application/json',
                                 'Authorization': 'Bearer ' + self.api_key
                                }
        self.client = Client(host=self.host,
                             request_headers=self.request_headers,
                             version=3)

    def test__init__(self):
        default_client = Client(host=self.host)
        self.assertEqual(default_client.host, self.host)
        self.assertEqual(default_client.request_headers, {})
        methods = ['delete', 'get', 'patch', 'post', 'put']
        self.assertEqual(default_client.methods, methods)
        self.assertEqual(default_client._version, None)
        self.assertEqual(default_client._url_path, [])

        request_headers = {'X-Test': 'test', 'X-Test2': 1}
        version = 3
        client = Client(host=self.host,
                        request_headers=request_headers,
                        version=version)
        self.assertEqual(client.host, self.host)
        self.assertEqual(client.request_headers, request_headers)
        methods = ['delete', 'get', 'patch', 'post', 'put']
        self.assertEqual(client.methods, methods)
        self.assertEqual(client._version, 3)
        self.assertEqual(client._url_path, [])

    def test__build_versioned_url(self):
        url = '/api_keys?hello=1&world=2'
        versioned_url = self.client._build_versioned_url(url)
        url = '{0}/v{1}{2}'.format(self.host, str(self.client._version), url)
        self.assertEqual(versioned_url, url)

    def test__build_url(self):
        self.client._url_path = self.client._url_path + ['here']
        self.client._url_path = self.client._url_path + ['there']
        self.client._url_path = self.client._url_path + [1]
        self.client._version = 3
        url = '{0}/v{1}{2}'.format(self.host,
                                   str(self.client._version),
                                   '/here/there/1?hello=0&world=1')
        query_params = {'hello': 0, 'world': 1}
        built_url = self.client._build_url(query_params)
        self.assertEqual(built_url, url)

    def test__update_headers(self):
        request_headers = {'X-Test': 'Test'}
        self.client._update_headers(request_headers)
        self.assertTrue('X-Test' in self.client.request_headers)
        self.client.request_headers.pop('X-Test', None)

    def test__build_client(self):
        new_client = self.client._build_client('test')
        self.assertTrue(new_client)

    def test__(self):
        self.assertEqual(self.client._url_path, [])
        client = self.client._('hello')
        url_path = ['hello']
        self.assertEqual(client._url_path[0], url_path[0])

    def test__getattr__(self):
        mock_client = MockClient(self.host, 200)
        client = mock_client.__getattr__('hello')
        url_path = ['hello']
        self.assertEqual(client._url_path, url_path)
        self.assertEqual(client.__getattr__('get').__name__, 'http_request')

        # Test Version
        client.version(3)
        self.assertEqual(client._version, 3)

        # Test GET
        mock_client._url_path+['test']
        r = mock_client.get()
        self.assertEqual(r.status_code, 200)

        # Test POST
        r = mock_client.put()
        self.assertEqual(r.status_code, 200)

        # Test PATCH
        r = mock_client.patch()
        self.assertEqual(r.status_code, 200)

        # Test POST
        mock_client.response_code = 201
        r = mock_client.post()
        self.assertEqual(r.status_code, 201)

        # Test DELETE
        mock_client.response_code = 204
        r = mock_client.delete()
        self.assertEqual(r.status_code, 204)


if __name__ == '__main__':
    unittest.main()
