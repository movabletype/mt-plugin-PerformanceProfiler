from .stream_loader import StreamLoader
from .big_query_loader import BigQueryLoader


class Factory:
    @classmethod
    def new_loader(cls, name, opts):
        if name == "stream":
            return StreamLoader(opts)
        elif name == "big_query":
            return BigQueryLoader(opts)
        else:
            raise Exception("Unsupported loader %s" % name)
