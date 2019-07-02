from scrapy.utils.reqser import request_to_dict, request_from_dict

from fifa_data import scrapy_redis_picklecompat


class Base(object):
    """Per-spider base queue class"""

    def __init__(self, server, spider, key, serializer=None):
        """Initialize per-spider redis queue.
        Parameters
        ----------
        server : StrictRedis
            Redis client instance.
        spider : Spider
            Scrapy spider instance.
        key: str
            Redis key where to put and get messages.
        serializer : object
            Serializer object with ``loads`` and ``dumps`` methods.
        """
        if serializer is None:
            # Backward compatibility.
            # TODO: deprecate pickle.
            serializer = scrapy_redis_picklecompat
        if not hasattr(serializer, 'loads'):
            raise TypeError("serializer does not implement 'loads' function: %r"
                            % serializer)
        if not hasattr(serializer, 'dumps'):
            raise TypeError("serializer '%s' does not implement 'dumps' function: %r"
                            % serializer)

        self.server = server
        self.spider = spider
        self.key = 'club_urls'
#        self.key = key % {'spider': spider.name}
        self.serializer = serializer

#    def _encode_request(self, request):
#        """Encode a request object"""
#        obj = request_to_dict(request, self.spider)
#        return obj
#
#    def _decode_request(self, request):
#        """Decode an request previously encoded"""
#        obj = request_to_dict(request, self.spider)
#        return obj

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, request):
        """Push a request"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    def clear(self):
        """Clear queue/stack"""
        self.server.delete(self.key)


class FifoQueue(Base):
    """Per-spider FIFO queue"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.scard(self.key)

    def push(self, request):
        """Push a request"""
        self.server.spop(self.key)

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.spop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.spop(self.key)
        if data:
            return data


class PriorityQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.scard(self.key)

    def push(self, request):
        """Push a request"""
        data = self._encode_request(request)
        score = -request.priority
        # We don't use zadd method as the order of arguments change depending on
        # whether the class is Redis or StrictRedis, and the option of using
        # kwargs only accepts strings, not bytes.
        #self.server.execute_command('ZADD', self.key, score, data)

    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        """
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            return self._decode_request(results[0])


class LifoQueue(Base):
    """Per-spider LIFO queue."""

    def __len__(self):
        """Return the length of the stack"""
        return self.server.scard(self.key)

    def push(self, request):
        """Push a request"""
        self.server.spop(self.key)

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.spop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.spop(self.key)

        if data:
            return self._decode_request(data)


# TODO: Deprecate the use of these names.
SpiderQueue = FifoQueue
SpiderStack = LifoQueue
SpiderPriorityQueue = PriorityQueue
