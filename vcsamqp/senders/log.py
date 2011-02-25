#!/usr/bin/env python -tt


class FileLogger:
    def __init__(self, filename):
        self._filename = filename

    def send_payload(self, payload):
    
        with open(self._filename, "wa") as fhandler:
            fhandler.write(str(payload) + "\n")
