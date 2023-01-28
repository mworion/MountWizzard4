############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest
import unittest.mock as mock
import socket

# external packages

# local imports
from base.loggerMW import setupLogging
setupLogging()
from mountcontrol.connection import Connection


class TestConnection(unittest.TestCase):

    def setUp(self):
        pass

    #
    #
    # testing the command analyses against structural faults
    #
    #

    def test_responses_withoutCommand_analyseCommand(self):
        conn = Connection()
        chunksToReceive, getData, minBytes = conn.analyseCommand('')
        self.assertEqual(False, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_responses_withoutCommand_analyseCommand_1(self):
        conn = Connection()
        chunksToReceive, getData, minBytes = conn.analyseCommand(':Q#')
        self.assertEqual(False, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_responses_withoutCommand_analyseCommand_2(self):
        conn = Connection()
        chunksToReceive, getData, minBytes = conn.analyseCommand(':QaXa#')
        self.assertEqual(True, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(1, chunksToReceive)

    def test_responses_withoutCommand_analyseCommand_3(self):
        conn = Connection()
        chunksToReceive, getData, minBytes = conn.analyseCommand(':Q#:QaXa#')
        self.assertEqual(True, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(1, chunksToReceive)

    def test_responses_typeA_analyseCommand(self):
        conn = Connection()
        command = ':AP#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(False, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_responses_typeB_analyseCommand(self):
        conn = Connection()
        command = ':FLIP#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(True, getData)
        self.assertEqual(1, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_responses_typeC_analyseCommand(self):
        conn = Connection()
        command = ':GTMP1#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(True, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(1, chunksToReceive)

    def test_responses_typeAB_analyseCommand(self):
        conn = Connection()
        command = ':AP#:FLIP#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(True, getData)
        self.assertEqual(1, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_responses_typeAC_analyseCommand(self):
        conn = Connection()
        command = ':AP#:GTMP1#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(True, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(1, chunksToReceive)

    def test_responses_typeBC_analyseCommand(self):
        conn = Connection()
        command = ':FLIP#:GTMP1#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(True, getData)
        self.assertEqual(1, minBytes)
        self.assertEqual(1, chunksToReceive)

    def test_responses_typeABC_analyseCommand(self):
        conn = Connection()
        command = ':AP#:FLIP#:GTMP1#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(True, getData)
        self.assertEqual(1, minBytes)
        self.assertEqual(1, chunksToReceive)

    def test_responses_typeABCABC_analyseCommand(self):
        conn = Connection()
        command = ':AP#:FLIP#:GTMP1#:AP#:FLIP#:GTMP1#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(True, getData)
        self.assertEqual(2, minBytes)
        self.assertEqual(2, chunksToReceive)

    def test_responses_typeABBCCABC_analyseCommand(self):
        conn = Connection()
        command = ':AP#:FLIP#:FLIP#:GTMP1#:GTMP1#:AP#:FLIP#:GTMP1#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(True, getData)
        self.assertEqual(3, minBytes)
        self.assertEqual(3, chunksToReceive)

    def test_responses_real_analyseCommand(self):
        conn = Connection()
        command = ':U2#:GTsid#:Ga#:Gz#:Gr#:Gd#:QaXa#:QaXb#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(True, getData)
        self.assertEqual(1, minBytes)
        self.assertEqual(6, chunksToReceive)

    def test_responses_real_analyseCommand_2(self):
        conn = Connection()
        command = ':Suaf1#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(False, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_responses_real_analyseCommand_3(self):
        conn = Connection()
        command = ':RC3#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(False, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_responses_real_analyseCommand_4(self):
        conn = Connection()
        command = ':RG2#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(False, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_responses_real_analyseCommand_5(self):
        conn = Connection()
        command = ':RG#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(False, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_responses_real_analyseCommand_6(self):
        conn = Connection()
        command = ':RC#'
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        self.assertEqual(False, getData)
        self.assertEqual(0, minBytes)
        self.assertEqual(0, chunksToReceive)

    def test_closeClientHard_1(self):
        conn = Connection()
        val = conn.closeClientHard('')
        self.assertFalse(val)

    def test_closeClientHard_2(self):
        conn = Connection('test')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with mock.patch.object(socket.socket,
                               'shutdown',
                               side_effect=Exception):
            val = conn.closeClientHard(client)
            self.assertFalse(val)

    def test_closeClientHard_3(self):
        conn = Connection('test')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with mock.patch.object(socket.socket,
                               'shutdown'):
            with mock.patch.object(socket.socket,
                                   'close'):
                val = conn.closeClientHard(client)
                self.assertTrue(val)

        #
        #
        # testing the connection without host presence
        #
        #

    def test_ok(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
            m_socket.return_value.connect.assert_called_with(('localhost', 3492))
            m_socket.return_value.sendall.assert_called_with(':GVN#'.encode())
        self.assertEqual(True, suc)
        self.assertEqual('10micron GM1000HPS', response[0])

    def test_no_host_defined(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            conn = Connection()
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)
        self.assertEqual('', response)

    def test_no_port_defined(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            conn = Connection(host='localhost')
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)
        self.assertEqual('', response)

    def test_no_response(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate('')
        self.assertEqual(True, suc)
        self.assertEqual('', response)

    def test_no_chunk(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = ''.encode
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate('')
        self.assertEqual(True, suc)
        self.assertEqual('', response)

    def test_connect_timeout(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            m_socket.return_value.connect.side_effect = socket.timeout
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)

    def test_sendall_timeout(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            m_socket.return_value.sendall.side_effect = socket.timeout
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)

    def test_recv_timeout(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            m_socket.return_value.recv.side_effect = socket.timeout
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)

    def test_connect_socket_error(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            m_socket.return_value.connect.side_effect = socket.error
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)

    def test_sendall_socket_error(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            m_socket.return_value.sendall.side_effect = socket.error
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)

    def test_recv_socket_error(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            m_socket.return_value.recv.side_effect = socket.error
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)

    def test_connect_exception(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            m_socket.return_value.connect.side_effect = Exception('Test')
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)

    def test_sendall_exception(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            m_socket.return_value.sendall.side_effect = Exception('Test')
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)

    def test_recv_exception(self):
        with mock.patch('socket.socket') as m_socket:
            m_socket.return_value.recv.return_value = '10micron GM1000HPS#'.encode()
            m_socket.return_value.recv.side_effect = Exception('Test')
            conn = Connection(host=('localhost', 3492))
            suc, response, chunks = conn.communicate(':GVN#')
        self.assertEqual(False, suc)

    def test_commands_valid_A(self):
        conn = Connection()
        for command in conn.COMMAND_A:
            self.assertTrue(command in conn.COMMANDS)

    def test_commands_valid_B(self):
        conn = Connection()
        for command in conn.COMMAND_B:
            self.assertTrue(command in conn.COMMANDS)

    def test_valid_commandSet_1(self):
        conn = Connection()
        suc = conn.validCommandSet(':AP#')
        self.assertTrue(suc)

    def test_valid_commandSet_2(self):
        conn = Connection()
        suc = conn.validCommandSet(':AP#:AP#:AP#')
        self.assertTrue(suc)

    def test_invalid_commandSet_1(self):
        conn = Connection()
        suc = conn.validCommandSet(':test#')
        self.assertFalse(suc)

    def test_invalid_commandSet_2(self):
        conn = Connection()
        suc = conn.validCommandSet(':AP#:test#')
        self.assertFalse(suc)

    def test_invalid_command_1(self):
        conn = Connection()
        suc = conn.validCommand(':AP#')
        self.assertTrue(suc)

    def test_invalid_command_2(self):
        conn = Connection()
        suc = conn.validCommand(':test#')
        self.assertFalse(suc)

    def test_communicate_invalid_command_1(self):
        conn = Connection()
        suc, msg, num = conn.communicate(':test#')
        self.assertFalse(suc)

    def test_communicate_invalid_command_2(self):
        conn = Connection()
        suc, msg, num = conn.communicate(':AP#:test#')
        self.assertFalse(suc)

    def test_receiveData_1(self):
        class Test:
            @staticmethod
            def decode(a):
                return

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = Connection()
        with mock.patch.object(socket.socket,
                               'recv',
                               return_value=Test()):
            with mock.patch.object(Test,
                                   'decode',
                                   side_effect=Exception):
                val = conn.receiveData(client=client, numberOfChunks=0, minBytes=0)
                assert val == (False, '')

    def test_receiveData_2(self):
        class Test:
            @staticmethod
            def decode(a):
                return ''

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = Connection()
        with mock.patch.object(socket.socket,
                               'recv',
                               return_value=Test()):
            val = conn.receiveData(client=client, numberOfChunks=0, minBytes=0)
            assert val == (True, [''])

    def test_receiveData_3(self):
        class Test:
            @staticmethod
            def decode(a):
                return '12345'

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = Connection()
        with mock.patch.object(socket.socket,
                               'recv',
                               return_value=Test()):
            val = conn.receiveData(client=client, numberOfChunks=0, minBytes=5)
            assert val == (True, ['12345'])

    def test_communicateRaw_0(self):
        class Test:
            @staticmethod
            def decode(a):
                return

            @staticmethod
            def settimeout(a):
                return

            @staticmethod
            def recv(a):
                return 'test'.encode('ASCII')

        conn = Connection()
        with mock.patch.object(conn,
                               'buildClient',
                               return_value=None):
            with mock.patch.object(conn,
                                   'sendData',
                                   return_value=False):
                with mock.patch.object(Test,
                                       'recv',
                                       side_effect=socket.timeout):
                    suc = conn.communicateRaw('test')
                    assert not suc[0]
                    assert not suc[1]
                    assert suc[2] == 'Socket error'

    def test_communicateRaw_1(self):
        class Test:
            @staticmethod
            def decode(a):
                return

            @staticmethod
            def settimeout(a):
                return

            @staticmethod
            def recv(a):
                return 'test'.encode('ASCII')

        conn = Connection()
        with mock.patch.object(conn,
                               'buildClient',
                               return_value=Test()):
            with mock.patch.object(conn,
                                   'sendData',
                                   return_value=False):
                with mock.patch.object(Test,
                                       'recv',
                                       side_effect=socket.timeout):
                    suc = conn.communicateRaw('test')
                    assert not suc[0]
                    assert not suc[1]
                    assert suc[2] == 'Timeout'

    def test_communicateRaw_2(self):
        class Test:
            @staticmethod
            def decode(a):
                return

            @staticmethod
            def settimeout(a):
                return

            @staticmethod
            def recv(a):
                return 'test'.encode('ASCII')

        conn = Connection()
        with mock.patch.object(conn,
                               'buildClient',
                               return_value=Test()):
            with mock.patch.object(conn,
                                   'sendData',
                                   return_value=True):
                with mock.patch.object(Test,
                                       'recv',
                                       side_effect=Exception):
                    suc = conn.communicateRaw('test')
                    assert suc[0]
                    assert not suc[1]
                    assert suc[2] == 'Exception'

    def test_communicateRaw_3(self):
        class Test:
            @staticmethod
            def decode(a):
                return

            @staticmethod
            def settimeout(a):
                return

            @staticmethod
            def recv(a):
                return 'test'.encode('ASCII')

        conn = Connection()
        with mock.patch.object(conn,
                               'buildClient',
                               return_value=Test()):
            with mock.patch.object(conn,
                                   'sendData',
                                   return_value=True):
                suc = conn.communicateRaw('test')
                assert suc[0]
                assert suc[1]
                assert suc[2] == 'test'
