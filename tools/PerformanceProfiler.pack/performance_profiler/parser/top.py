from struct import unpack
from . import v1


class Top:
    def __parse(self, v, stream):
        if v == 1:
            return v1.Parser().parse(stream)
        else:
            raise Exception("Unsupported version %s" % v)

    def parse(self, stream):
        (v,) = unpack("B", stream.read(1))

        data = self.__parse(v, stream)
        data["version"] = v

        return data
