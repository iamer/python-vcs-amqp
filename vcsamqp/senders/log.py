#!/usr/bin/env python -tt
import json


class FileLogger:
    def __init__(self, filename):
        self._filename = filename

    def send_payload(self, payload):
        with open(self._filename, "a") as fhandler:
            fhandler.write(str(
                json.dumps(
                    payload,
                    sort_keys=True,
                    indent=4,
                    separators=(",", ": "))
            ) + "\n")
