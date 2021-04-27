import fcntl
import json
import os


class FileLoader:
    def __init__(self, opts):
        self.file = opts.get("file")

    def load(self, new_data):

        while True:
            f = open(self.file, "a+")
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
            except OSError:
                continue
            else:
                break

        f.seek(os.SEEK_SET)

        try:
            if os.path.exists(self.file) and os.stat(self.file).st_size > 0:
                data = json.loads(f.read())
            else:
                data = {}

            for k in new_data.keys():
                if k in data:
                    data[k] += new_data[k]
                else:
                    data[k] = new_data[k]

            f.truncate(0)
            f.seek(os.SEEK_SET)

            f.write(json.dumps(data) + "\n")
        except Exception as e:
            print(e)
