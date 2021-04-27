from .file_loader import FileLoader
from .big_query_loader import BigQueryLoader


class Factory:
    @classmethod
    def new_loader(cls, name, opts):
        if name == "file":
            return FileLoader(opts)
        elif name == "big_query":
            return BigQueryLoader(opts)
        else:
            raise Exception("Unsupported loader %s" % name)
