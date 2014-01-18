'''
    Tests for some basic package's root level functionality.
'''

import distributedlock
import unittest

from distributedlock import _Configuration
from mock import Mock


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.configure = _Configuration()

    def test_update_settings_raises_error_when_updating_invalid_config(self):
        # Raises error when trying to update invalid setting
        self.assertRaises(AttributeError, self.configure.update,
                          invalid_arg='val')

    def test_updates_valid_settings(self):
        # Updates valid setting
        self.configure.update(namespace='something')
        self.assertEqual(self.configure.namespace, 'something')

    def test_backend_gets_backend(self):
        # When backend is not set
        self.assertEqual(self.configure._backend, self.configure.backend)
        self.assertEqual(self.configure._backend, None)

        # When backend is set
        self.configure.backend = distributedlock.backends.REDIS
        self.assertEqual(self.configure._backend, self.configure.backend)
        self.assertEqual(self.configure._backend,
                         distributedlock.backends.REDIS)

    def test_backend_raises_error_on_setting_invalid_backend(self):
        def _test():
            # Set some unexpected value
            self.configure.backend = 0
        self.assertRaises(ValueError, _test)

    def test_backend_raises_import_error_when_library_not_available(self):
        distributedlock.backends.REDIS['available'] = False
        def _test():
            self.configure.backend = distributedlock.backends.REDIS

        self.assertRaises(ImportError, _test)
        distributedlock.backends.REDIS['available'] = True

    def test_backend_sets_backend_value(self):
        self.configure.backend = distributedlock.backends.REDIS
        self.assertEqual(self.configure._backend,
                         distributedlock.backends.REDIS)

    def test_client_returns_the_set_client_object(self):
        client = Mock()
        self.configure._client = client
        self.assertEqual(self.configure.client, self.configure._client)
        self.assertEqual(self.configure._client, client)

    def test_client_raises_error_when_backend_is_not_set(self):
        # Make sure backend is set to None
        self.assertEqual(self.configure.backend, None)
        def _test():
            client = self.configure.client
        self.assertRaises(ValueError, _test)

    def test_client_returns_client_when_not_set_but_backend_is_set(self):
        mock_obj = Mock()
        distributedlock.redis.StrictRedis = Mock
        distributedlock.redis.client.StrictRedis = Mock
        self.configure.backend = distributedlock.backends.REDIS
        self.assertTrue(isinstance(self.configure.client, Mock))

    def test_client_allows_setting_of_valid_client_objects_only(self):
        # When backend is set and client object is invalid
        self.configure.backend = distributedlock.backends.REDIS
        def _test():
            self.configure.client = None
        self.assertRaises(ValueError, _test)

        # When backend is set and client object is valid
        distributedlock.redis.client.StrictRedis = Mock
        self.configure.client = Mock()

        # When backend is not set and client library is available and client is
        # valid
        self.configure._backend = None
        self.assertEquals(self.configure.backend, None)
        client_obj = Mock()
        self.configure.client = client_obj
        self.assertEquals(self.configure.client, client_obj)
        self.assertTrue(isinstance(self.configure.client, Mock))

        # When backend is not set and client library is available and client is
        # invalid
        self.configure._backend = None
        self.configure._client = None
        self.assertEquals(self.configure.backend, None)
        client_obj = 'Random'
        def _test():
            self.configure.client = client_obj
        self.assertRaises(ValueError, _test)

        # When backend is not set and client library is available and client is
        # valid
        self.configure._backend = None
        self.configure._client = None
        self.assertEquals(self.configure.backend, None)
        client_obj = Mock()
        self.configure.client = client_obj

        # When backend is not set and client libraries are not available
        self.configure._backend = None
        self.configure._client = None
        self.assertEquals(self.configure.backend, None)
        distributedlock.backends.REDIS['available'] = False
        distributedlock.backends.MEMCACHED['available'] = False
        distributedlock.backends.ETCD['available'] = False
        def _test():
            self.configure.client = Mock()
        self.assertRaises(ValueError, _test)
        distributedlock.backends.REDIS['available'] = True
        distributedlock.backends.MEMCACHED['available'] = True
        distributedlock.backends.ETCD['available'] = True


def testConfigure():
    '''
    Test the library configure function.
    '''

    distributedlock.configure(namespace='namespace')
    assert distributedlock._configuration.namespace == 'namespace'
