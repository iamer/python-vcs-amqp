#!/usr/bin/env python -tt

"""AMQP sender API."""

__all__ = ["BasicAMQPSender", "BlockingAMQPSender", "AsyncAMQPSender"]

import logging
from abc import ABCMeta, abstractmethod

import pika
import simplejson

from vcsamqp.settings import AMQP

LOG = logging.getLogger(__name__)

class BasicAMQPSender(object):

    """Base abstract class for AMQP senders."""

    __metaclass__ = ABCMeta

    def __init__(self, config=AMQP):

        self._host = config["host"]
        self._port = config["port"]
        self._user = config["user"]
        self._password = config["password"]
        self._vhost = config["vhost"]
        self._exchange = config["exchange"]
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
    def send_payload(self, payload):
        """
        Send payload to the server.
        Abstract method. Has to be implemented in derived classes.

        :param payload: data to be sent
        :type payload: dictionary

        """

        raise NotImplementedError


class BlockingAMQPSender(BasicAMQPSender):

    """
    Blocking (synchronous) sender.
    Code is borrowed from Pika Blocking demo_send example_blocking_:

    .. _example_blocking: http://tonyg.github.com/pika/examples.html#id4

    """

    def send_payload(self, payload):
        """
        Send payload to the server using blocking approach.

        :param payload: data to be sent
        :type payload: dictionary

        """

        self._connection = pika.BlockingConnection(self._parameters)
        self._channel = self._connection.channel()

        self._channel.queue_declare(queue=self._queue,
                                    durable=self._durable,
                                    exclusive=self._exclusive,
                                    auto_delete=self._auto_delete)

        properties = pika.BasicProperties("text/plain",
                                          delivery_mode=self._delivery_mode)

        self._channel.basic_publish(exchange=self._exchange,
                                    routing_key=self._routing_key,
                                    body=simplejson.dumps(payload),
                                    properties=properties)


class AsyncAMQPSender(BasicAMQPSender):

    """

    Asynchronous Sender.
    Code is borrowed from Pika Asynchronous demo_send example_async_:

    .. _example_async: http://tonyg.github.com/pika/examples.html#demo-send

    Methods are placed in the same order as they're called by pika

    """

    def on_connected(self, connection):
        """
        Callback. Called when we are fully connected to RabbitMQ.

        :param connection: connection object
        :type connection: object
        """
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        """
        Callback. Called when channel has opened.

        :param channel: channel object
        :type channel: object

        """
        self._channel = channel
        channel.queue_declare(queue=self._queue, durable=self._durable,
                              exclusive=self._exclusive,
                              auto_delete=self._auto_delete,
                              callback=self.on_queue_declared)


    def on_queue_declared(self, _frame):
        """
        Callback: Called when queue has been declared.

        :param _frame: responce from broker
        :type _frame: object

        """

        self._channel.basic_publish(exchange=self._exchange,
                                    routing_key=self._routing_key,
                                    body=self._payload,
                                    properties=pika.BasicProperties(
                                        content_type="text/plain",
                                        delivery_mode=self._delivery_mode))
        self._connection.close()


    def send_payload(self, payload):
        """
        Send payload to the server setting up chain of callbacks:
        on_connected -> on_channel_open -> on_queue_declared.
        (see above)

        :param payload: data to be sent
        :type payload: dictionary

        """


        self._connection = pika.SelectConnection(self._parameters,
                                                 self.on_connected)
        self._payload = simplejson.dumps(payload)
        self._connection.ioloop.start()

