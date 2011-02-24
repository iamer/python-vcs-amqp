#!/usr/bin/env python
import pika
import sys
from vcsamqp.payload.common import Payload

class baseListener():
    def __init__(self,host="127.0.0.1",port=5627,vhost="/",user=None,password=None):
        self.setup()
        self.setup_connection(host,port,vhost,user,password)

    def setup(self):
        self.name=""
        self.exchange_type="topic"
        self.routing_key="*"

    # Step #1: Connect to RabbitMQ
    def setup_connection(self,host,port,vhost,user,password):
        credentials = None
        if user and password:
            credentials = pika.PlainCredentials(user,password)
        parameters = pika.ConnectionParameters(host=host,port=port,virtual_host=vhost,credentials=credentials)
        self.connection = pika.adapters.SelectConnection(parameters, self.on_connected)

    # Step #2
    def on_connected(self, connection):
        """Called when we are fully connected to RabbitMQ"""
        # Open a channel
        self.connection.channel(self.on_channel_open)
    
    # Step #3
    def on_channel_open(self, new_channel):
        """Called when our channel has opened"""
        self.channel = new_channel
        self.channel.exchange_declare(exchange=self.name,type=self.exchange_type,durable=True,callback=self.on_exchange_declared)
    
    def on_exchange_declared(self, frame):
        self.channel.queue_declare(queue=self.name, durable=True, exclusive=False, auto_delete=False,callback=self.on_queue_declared)
    
    # Step #4
    def on_queue_declared(self, frame):
        """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
        self.channel.queue_bind(queue=self.name,exchange=self.name,routing_key=self.routing_key,callback=self.on_queue_bound)
    
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
