#!/usr/bin/env python -tt

import json
import sys

class Payload(object):
    """ Class to wrap the payload json """

    def __init__(self, body):
        self.payload = json.loads( body )['payload']

    def __getattr__(self, attr):
        return self.payload.get(attr,None)

    def __str__(self):
        return json.dumps(self.payload, sort_keys=True, indent=4)

