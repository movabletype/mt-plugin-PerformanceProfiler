from .rdb_transformer import RDBTransformer


class Factory:
    @classmethod
    def new_transformer(cls, name):
        if name == "rdb":
            return RDBTransformer()
        else:
            raise Exception("Unsupported loader %s" % name)
