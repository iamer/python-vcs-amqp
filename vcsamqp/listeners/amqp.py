#!/usr/bin/env python -tt

"""AMQP Listener."""

import logging
from abc import ABCMeta, abstractmethod

import pika, sys, simplejson
from vcsamqp.settings import AMQP
from vcsamqp.payload.common import Payload

LOG = logging.getLogger(__name__)

class BaseAMQPListener(object):

    """Base abstract class for AMQP listeners."""

    __metaclass__ = ABCMeta

    def __init__(self, config=AMQP):

        self._host = config["host"]
        self._port = config["port"]
        self._user = config["user"]
        self._password = config["password"]
        self._vhost = config["vhost"]
        self._exchange = config["exchange"]
        self._exchange_type = config["exchange_type"]
        self._routing_key = config["routing_key"]
        self._queue = config["queue_name"]
        self._durable = config["queue_durable"]
        self._exclusive = config["queue_exclusive"]
        self._auto_delete = config["queue_auto_delete"]
        self._delivery_mode = config["delivery_mode"]

        self._credentials = pika.PlainCredentials(self._user, self._password)
        self._parameters = pika.ConnectionParameters(host=self._host,
                                    port=self._port, virtual_host=self._vhost,
                                    credentials=self._credentials)

        self._connection = None
        self._channel = None
        self._payload = None

    @abstractmethod
    def receive_payload(self, channel, method, header, body):

        """Recieve payload from the server."""

        raise NotImplementedError


class AsyncAMQPListener(BaseAMQPListener):

    """Asynchronous Listener."""

    def __init__(self, config=AMQP):

        """ Setup the connection """

        super(AsyncAMQPListener, self).__init__(config = config)
        self.setup_connection()

    def setup_connection(self):

        """Step #1: Connect to RabbitMQ."""

        self._connection = pika.adapters.SelectConnection(self._parameters,
                                                         self.on_connected)

    def on_connected(self, connection):

        """Step #2: Called when we are fully connected to RabbitMQ."""

        connection.channel(self.on_channel_open)
        self._connection = connection

    def on_channel_open(self, channel):

        """Step #3: Called when our channel has opened."""

        self._channel = channel
        channel.exchange_declare(exchange = self._exchange,
                                 type = self._exchange_type,
                                 durable = self._durable,
                                 callback = self.on_exchange_declared)

    def on_exchange_declared(self, frame):

        """Step #4: Called when the exchange has been declared."""

        self._channel.queue_declare(queue = self._queue, 
                                   durable = self._durable,
                                   exclusive = self._exclusive,
                                   auto_delete = self._auto_delete,
                                   callback = self.on_queue_declared)

    # Step #4
    def on_queue_declared(self, frame):

        """Step #5: Called when Queue has been declared.

        frame is the response from RabbitMQ"""

        self._channel.queue_bind(queue = self._queue, 
                                exchange = self._exchange,
                                routing_key = self._routing_key,
                                callback = self.on_queue_bound)

    def on_queue_bound(self, frame):

        """Step #6: Called when the queue has been bound to the exchange."""

        self._channel.basic_consume(self.receive_payload, 
                                   queue = self._queue, 
                                   no_ack=True)

    def receive_payload(self, channel, method, header, body):
        """Step #7: Called when we receive a message from RabbitMQ."""
        self._payload = Payload(body)
        print self._payload

    def consume(self):

        """ Start the IO event loop """

        try:
            # Loop so we can communicate with RabbitMQ
            self._connection.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            self._connection.close()
            # Loop until we're fully closed, will stop on its own
            self._connection.ioloop.start()


class TestListener(AsyncAMQPListener):

    def receive_payload(self, channel, method, header, body):
        print simplejson.loads(body)


def main(argv):
    listener = TestListener(config = AMQP)
    listener.consume()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
