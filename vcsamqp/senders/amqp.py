#!/usr/bin/env python -tt

"""AMQP sender."""

import pika
import simplejson

class AMQPSender:

    """Sender. Sends payload to AMQP host."""

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
        
        # make connection to AMQP host
        credentials = pika.PlainCredentials(self._user, self._password)
        parameters = pika.ConnectionParameters(host=self._host,
                                               virtual_host=self._vhost,
                                               credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        self._channel = connection.channel()

    def send_payload(self, payload):
        """Entry point."""

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
