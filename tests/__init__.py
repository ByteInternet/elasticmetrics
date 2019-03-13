import unittest
import mock


class BaseTestCase(unittest.TestCase):
    def set_up_patch(self, target, mock_=None, **kwargs):
        if mock_ is None:
            mock_ = mock.Mock()
        if 'return_value' in kwargs:
            mock_.return_value = kwards['return_value']
        patcher = mock.patch(target, mock_)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def _mock_urlopen_response(self, body=b'', status=200, url=''):
        mock_resp = mock.Mock()
        mock_resp.getcode.return_value = status
        mock_resp.read.return_value = body
        mock_resp.geturl.return_value = url
        return mock_resp
