#!/usr/bin/env python
import pika
import sys
import simplejson

from vcsamqp.settings import AMQP
from vcsamqp.payload.common import Payload

class baseListener():
    """ Base AMQP listener class based on pika """
    def __init__(self,host="127.0.0.1",port=5627,vhost="/",user=None,
                 password=None):
        """ Class initialization sets up names and connection """
        self.setup()
        self.setup_connection(host,port,vhost,user,password)

    def setup(self):
        """ Overrid this method in your class to set name, type and routing_key """
        self.name=""
        self.exchange_type="topic"
        self.routing_key="*"

    def setup_connection(self,host,port,vhost,user,password):
        """ Step #1: Connect to RabbitMQ """
        credentials = None
        if user and password:
            credentials = pika.PlainCredentials(user,password)
        parameters = pika.ConnectionParameters(host=host,port=port,
                                               virtual_host=vhost,
                                               credentials=credentials)
        self.connection = pika.adapters.SelectConnection(parameters,
                                                         self.on_connected)

    def on_connected(self, connection):
        """ Step #2: Called when we are fully connecte d to RabbitMQ """
        self.connection.channel(self.on_channel_open)

    # Step #3
    def on_channel_open(self, new_channel):
        """Called when our channel has opened"""
        self.channel = new_channel
        self.channel.exchange_declare(exchange=self.name,
                                      type=self.exchange_type,durable=True,
                                      callback=self.on_exchange_declared)

    def on_exchange_declared(self, frame):
        self.channel.queue_declare(queue=self.name,durable=True,
                                   exclusive=False,auto_delete=False,
                                   callback=self.on_queue_declared)

    # Step #4
    def on_queue_declared(self, frame):
        """Called when RabbitMQ has told us our Queue has been declared,
        frame is the response from RabbitMQ"""
        self.channel.queue_bind(queue=self.name,exchange=self.name,
                                routing_key=self.routing_key,
                                callback=self.on_queue_bound)

    def on_queue_bound(self, frame):
        self.channel.basic_consume(self.consume, queue=self.name, no_ack=True)

    # Step #5
    def consume(self, channel, method, header, body):
        """Called when we receive a message from RabbitMQ"""
        x = Payload(body)
        print x

    def start(self):
        try:
            # Loop so we can communicate with RabbitMQ
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            self.connection.close()
            # Loop until we're fully closed, will stop on its own
            self.connection.ioloop.start()

class AMQPListener(baseListener):
    
    def setup(self):
        """ Overrid this method in your class to set name, type and routing_key """
        self.name = AMQP["queue_name"]
        self.exchange_type = "topic"
        self.routing_key = AMQP["routing_key"]

        # Step #5
    def consume(self, channel, method, header, body):
        """Called when we receive a message from RabbitMQ"""
        print simplejson.loads(body)


def main(argv):
    listener = AMQPListener(AMQP["host"], AMQP["port"], AMQP["vhost"],
                            AMQP["user"], AMQP["password"])
    listener.start()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
