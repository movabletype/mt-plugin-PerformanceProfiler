import json


class StreamLoader:
    def __init__(self, opts):
        self.stream = opts["stream"]

    def load(self, data):
        self.stream.write(json.dumps(data) + "\n")
