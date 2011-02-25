#!/usr/bin/env python -tt

"""AMQP sender."""

import logging
from abc import ABCMeta, abstractmethod

import pika
import simplejson

LOG = logging.getLogger(__name__)

class BasicAMQPSender(object):

    """Base abstract class for AMQP senders."""

    __metaclass__ = ABCMeta

    def __init__(self, config):

        self._host = config["amqp_host"]
        self._port = config["amqp_port"]
        self._user = config["amqp_user"]
        self._password = config["amqp_password"]
        self._vhost = config["amqp_vhost"]
        self._exchange = config['amqp_exchange']
        self._routing_key = config['amqp_routing_key']
        self._queue = config['amqp_queue_name']
        self._durable = config['amqp_queue_durable']
        self._exclusive = config['amqp_queue_exclusive']
        self._auto_delete = config['amqp_queue_auto_delete']
        self._delivery_mode = config['amqp_delivery_mode']

        self._credentials = pika.PlainCredentials(self._user, self._password)
        self._parameters = pika.ConnectionParameters(host=self._host,
                                    port=self._port, virtual_host=self._vhost,
                                    credentials=self._credentials)

        self._connection = None
        self._channel = None
        self._payload = None

    @abstractmethod
    def send_payload(self, payload):
        """Send payload to the server."""
        raise NotImplementedError


class BlockingAMQPSender(BasicAMQPSender):

    """Blocking (synchronous) sender."""

    def send_payload(self, payload):

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

    """Asynchronous Sender."""

    def on_connected(self, connection):
        """Step #2: Called when we are fully connected to RabbitMQ."""
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        """Step #3: Called when our channel has opened."""
        self._channel = channel
        channel.queue_declare(queue=self._queue, durable=self._durable,
                              exclusive=self._exclusive,
                              auto_delete=self._auto_delete,
                              callback=self.on_queue_declared)


    def on_queue_declared(self, _frame):
        """Step #4: Called when RabbitMQ has told us our Queue has been
           declared, frame is the response from RabbitMQ."""

        self._channel.basic_publish(exchange=self._exchange,
                                    routing_key=self._routing_key,
                                    body=self._payload,
                                    properties=pika.BasicProperties(
                                        content_type="text/plain",
                                        delivery_mode=self._delivery_mode))
        self._connection.close()


    def send_payload(self, payload):

        self._connection = pika.SelectConnection(self._parameters,
                                                 self.on_connected)
        self._payload = simplejson.dumps(payload)
        self._connection.ioloop.start()
