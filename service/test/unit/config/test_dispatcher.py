import json
import unittest
import thread
import sys
from mockito import mock, when
import os
from pixelated.config import App
from pixelated.config.args import parse as parse_args

from pixelated.config.dispatcher import config_dispatcher


class TestConfigDispatcher(unittest.TestCase):

    def setUp(self):
        self.app = App()
        self.test_data = {'leap_provider_hostname': 'test_provider', 'user': 'test_user', 'password': 'test_password'}

    def test_that_organization_switch_reads_the_credentials_from_pipe(self):
        fifo_path = '/tmp/credentials-pipe'

        sys.argv = ['tmp/does_not_exist', '--dispatcher', fifo_path]
        args = parse_args()

        self._mkfifo(fifo_path)

        config_dispatcher(self.app, args)

        self.assertEquals('test_provider', self.app['LEAP_SERVER_NAME'])
        self.assertEquals('test_user', self.app['LEAP_USERNAME'])
        self.assertEquals('test_password', self.app['LEAP_PASSWORD'])

    def test_that_organization_switch_reads_the_credentials_from_stdin(self):
        data = json.dumps({'leap_provider_hostname': 'test_provider', 'user': 'test_user', 'password': 'test_password'})
        orig_stdin = sys.stdin
        sys.stdin = mock()
        when(sys.stdin).read().thenReturn(data)

        try:
            sys.argv = ['tmp/does_not_exist', '--dispatcher-stdin']
            args = parse_args()

            config_dispatcher(self.app, args)

            self.assertEquals('test_provider', self.app['LEAP_SERVER_NAME'])
            self.assertEquals('test_user', self.app['LEAP_USERNAME'])
            self.assertEquals('test_password', self.app['LEAP_PASSWORD'])
        finally:
            sys.stdin = orig_stdin

    def _spin_up_fifo(self, test_fifo):
        with open(test_fifo, 'w') as fifo:
            fifo.write(json.dumps(self.test_data))

    def _mkfifo(self, fifo_path):
        if os.path.exists(fifo_path):
            os.remove(fifo_path)
        os.mkfifo('/tmp/credentials-pipe')
        thread.start_new_thread(self._spin_up_fifo, (fifo_path,))
