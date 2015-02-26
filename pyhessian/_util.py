try:
    from cStringIO import StringIO
except ImportError:
    from six import BytesIO as StringIO


class BufferedReader(object):

    def __init__(self, input, buffer_size=65535):
        self.__input       = input
        self.__buffer_size = buffer_size
        self.__buffer      = StringIO()

        # initial fill
        chunk = input.read(buffer_size)
        self.__byte_count = len(chunk)
        self.__buffer.write(chunk)
        self.__buffer.seek(0)

    def read(self, byte_count):
        difference = byte_count - self.__byte_count

        if difference < 0:
            chunk = self.__buffer.read(byte_count)
            self.__byte_count -= byte_count
        else:
            chunk = self.__buffer.read() + self.__input.read(difference)

            # verify size
            if len(chunk) != byte_count:
                raise EOFError("Encountered unexpected end of stream")

            # reset internal buffer
            self.__buffer.seek(0)
            self.__buffer.truncate()

            # replenish
            fresh_chunk = self.__input.read(self.__buffer_size)
            self.__byte_count = len(fresh_chunk)
            self.__buffer.write(fresh_chunk)
            self.__buffer.seek(0)

        return chunk

