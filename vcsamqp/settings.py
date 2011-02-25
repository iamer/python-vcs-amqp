#!/usr/bin/python -tt

AMQP = {
    "host": "hemeego-sidev-h001.europe.nokia.com",
    "port": 5672,
    "user": "vcsamqp",
    "password": "123",
    "vhost": "/vcsamqp",
    "exchange": "",
    "exchange_type": "topic",
    "routing_key": "vcsamqp-queue",
    "queue_name": "vcsamqp-queue",
    "queue_durable": True,
    "queue_exclusive": False,
    "queue_auto_delete": False,
    "delivery_mode": 1
}
