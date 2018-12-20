# -*- coding: utf-8 -*-

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.


from scrapy_redis.queue import Base

#权重轮询算法
class PollingQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def push(self, request):
        """Push a request"""
        data = self._encode_request(request)
        score = -request.priority
        # We don't use zadd method as the order of arguments change depending on
        # whether the class is Redis or StrictRedis, and the option of using
        # kwargs only accepts strings, not bytes.
        self.server.execute_command('ZADD', self.key, score, data)

    #-xxyyy.zzzz
    #负分值优先级
    def pop(self, timeout=0, response=None):
        """
        Pop a request
        timeout not support in this queue class
        """
        
        #带有分片权重的数值： 后三位表示权重，前缀用作分片策略
        if response is not None and isinstance(response.request.priority,int) and abs(response.request.priority)>100:
            import random
            import sys
            polling = int(str(int(response.request.priority))[-3:])
            shard = int(str(int(response.request.priority))[:-3])
#            pipe = self.server.pipeline()
#            pipe.multi()
            if random.randint(1, 100)<polling:
                #当前分片、以及后续分片
                shard1 = shard*1000 #当前分片
#                shard2 = shard*1000-999 #当前分片
#                shard3 = sys.maxsize #后续分片
                shard3 = 0 #后续分片
            else:
                #后续分片
                shard1 = shard*1000-999+1000 #后续分片
#                shard3 = sys.maxsize #后续分片
                shard3 = 0 #后续分片
#            pipe.zrangebyscore(self.key, shard1, shard3, start=0, num=1, withscores=True).zrem(self.key, 'todo:xxx') #需要原子操作
#            results, count = pipe.execute()
            results, count = zrangebyscore_safe(self.server, self.key, shard1, shard3)
            if results:
                return self._decode_request(results[0])
                
        #从头开始
        
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            return self._decode_request(results[0])

def zrangebyscore_safe(server, key, shard1, shard3):
    script = "z=redis.call('zrangebyscore', KEYS[1], KEYS[2], KEYS[3], 'WITHSCORES', 'LIMIT', 0, 1); redis.call('zrem', KEYS[1], z); return z"
    result = opener.register_script(script)(keys=[key, shard1, shard3])
    return result