# -*- coding: utf-8 -*-

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.


from scrapy_redis.queue import Base

#from . import picklecompat

import json

from scrapy.utils.serialize import ScrapyJSONEncoder

#from queue import Queue
#q = Queue()

def key_to_json(data):
    if isinstance(data, (bytes)):
        return str(data,encoding='utf-8')
    return data

def to_json(data):
    if isinstance(data, dict):
        return {key_to_json(key): to_json(data[key]) for key in data}
    return data

#def json_to_key(data):
#    if data.startswith("b'"):
#        return data
#    return data
#
#def json_to(data):
#    if isinstance(data, dict):
#        return {key_to_json(key): json_to(data[key]) for key in data}
#    return data

class BytesEncoder(ScrapyJSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8');
        return ScrapyJSONEncoder.default(self, obj)

class JsonCompat(object):
    def loads(s):
        return json.loads(s)
    def dumps(obj):
        return json.dumps(to_json(obj), cls=BytesEncoder)

#权重轮询算法
class PollingQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""
    
    def __init__(self, server, spider, key, serializer=None):
        if serializer is None:
            serializer = JsonCompat
        super(PollingQueue, self).__init__(server, spider, key, serializer)

    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def push(self, request):
        """Push a request"""
#        request.priority = 222097 #todo:xxxxxx
        data = self._encode_request(request)
        score = -request.priority
        # We don't use zadd method as the order of arguments change depending on
        # whether the class is Redis or StrictRedis, and the option of using
        # kwargs only accepts strings, not bytes.
        self.server.execute_command('ZADD', self.key, score, data)

    #-xxyyy.zzzz
    #负分值优先级
    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        """

        #原子操作
        def _polling_safe(server, key):
            script = """
            local last_priority = redis.call('get', 'last_priority');
            if last_priority then
                local last_s=tostring(last_priority);
                local polling=tonumber(string.sub(last_s,-3));
                local shard=math.abs(tonumber(string.sub(last_s,1,-4)));
                if tonumber(math.abs(last_priority))>100 then
                    local shard1=0;
                    local shard3=0;
                    if math.random(1,100)<polling then
                        shard1=shard*1000+999;
                        shard3=0;
                    else
                        shard1=shard*1000-1000;
                        shard3=0;
                    end
                    local req=redis.call('zrangebyscore', KEYS[1], -shard1, shard3, 'WITHSCORES', 'LIMIT', 0, 1);
                    if req and req[1] then
                        -- redis.call('set', 'last_priority', cjson.decode(req[1])['priority']);
                        redis.call('set', 'last_priority', req[2]);
                        redis.call('zrem', KEYS[1], req[1]);
                        return req;
                    end
                end
            end
            """
            result = server.register_script(script)(keys=[key])
#            print(8888888888, result)
            if result is not None:
                return result,1
            else:
                return None,0
        
#        priority = q.get()
##        priority = spider.crawler.stats.get_value('response_priority')
#        #带有分片权重的数值： 后三位表示权重，前缀用作分片策略
##        if response is not None and isinstance(response.request.priority,int) and abs(response.request.priority)>100:
#        if spider is not None and priority>100:#todo:xxxx
#            import random
#            import sys
#            polling = int(str(priority)[-3:])#todo:xxxx
#            shard = int(str(priority)[:-3])#todo:xxxx
##            pipe = self.server.pipeline()
##            pipe.multi()
#            if random.randint(1, 100)<polling:
#                #当前分片、以及后续分片
#                shard1 = shard*1000 #当前分片
##                shard2 = shard*1000-999 #当前分片
##                shard3 = sys.maxsize #后续分片
#                shard3 = 0 #后续分片
#            else:
#                #后续分片
#                shard1 = shard*1000-999+1000 #后续分片
##                shard3 = sys.maxsize #后续分片
#                shard3 = 0 #后续分片
##            pipe.zrangebyscore(self.key, shard1, shard3, start=0, num=1, withscores=True).zrem(self.key, 'todo:xxx') #需要原子操作
##            results, count = pipe.execute()
#            results, count = zrangebyscore_safe(self.server, self.key, shard1, shard3)
#            if results:
##                spider.crawler.stats.set_value('response_priority',7777)#todo:xxxx
#                q.put(7777)#todo:xxx
#                return self._decode_request(results[0])
            
        #从当前开始
        
        results, count = _polling_safe(self.server, self.key)
        if results:
            return self._decode_request(results[0])
                
        #从头开始
        
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            if len(results)>1 and results[1]>100:
                self.server.set('last_priority', results[1]);
            return self._decode_request(results[0])
        