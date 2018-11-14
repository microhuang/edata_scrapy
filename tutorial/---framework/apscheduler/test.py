# -*- coding: utf-8 -*-


import threading
import _thread
#from redis import StrictRedis as Redis
#import redis

from threading import RLock
import six
import abc
from abc import ABCMeta, abstractmethod
from copyreg import dispatch_table
import dill as pickle #不能处理虚类
import cloudpickle as pickle #不能处理_thread.lock
#import pickle
#from pickle import _Pickler as Pickler

#import cloudpickle as cpickle
#import dill as dpickle

#import copy_reg as copyreg
import copyreg
import types
import io

#def mdispatch():
#    import cloudpickle
#    p=cloudpickle.CloudPickler(io.BytesIO())
#    print(p.dispatch)
#mdispatch()
#exit()
##f = io.BytesIO()
#p = pickle.Pickler(io.BytesIO())
#p.dispatch_table = copyreg.dispatch_table.copy()
##p.dispatch_table[SomeClass] = reduce_SomeClass
#
#print(p.dispatch)#获得dispatch
#exit()

#pickle.settings['recurse'] = True

lck = threading.Lock()

#{<class 'NoneType'>: <function _Pickler.save_none at 0x104130b70>, <class 'bool'>: <function _Pickler.save_bool at 0x104130bf8>, <class 'int'>: <function _Pickler.save_long at 0x104130c80>, <class 'float'>: <function _Pickler.save_float at 0x104130d08>, <class 'bytes'>: <function _Pickler.save_bytes at 0x104130d90>, <class 'str'>: <function _Pickler.save_str at 0x104130e18>, <class 'tuple'>: <function _Pickler.save_tuple at 0x104130ea0>, <class 'list'>: <function _Pickler.save_list at 0x104130f28>, <class 'dict'>: <function _Pickler.save_dict at 0x10412f0d0>, <class 'set'>: <function _Pickler.save_set at 0x10412f1e0>, <class 'frozenset'>: <function _Pickler.save_frozenset at 0x10412f268>, <class 'function'>: <function CloudPickler.save_function at 0x103ff7730>, <class 'type'>: <function CloudPickler.save_global at 0x103ff7b70>, <class 'memoryview'>: <function CloudPickler.save_memoryview at 0x103ff7598>, <class 'module'>: <function CloudPickler.save_module at 0x103ff7620>, <class 'code'>: <function CloudPickler.save_codeobject at 0x103ff76a8>, <class 'builtin_function_or_method'>: <function CloudPickler.save_builtin_function at 0x103ff7ae8>, <class 'method'>: <function CloudPickler.save_instancemethod at 0x103ff7bf8>, <class 'property'>: <function CloudPickler.save_property at 0x103ff7d08>, <class 'classmethod'>: <function CloudPickler.save_classmethod at 0x103ff7d90>, <class 'staticmethod'>: <function CloudPickler.save_classmethod at 0x103ff7d90>, <class 'operator.itemgetter'>: <function CloudPickler.save_itemgetter at 0x103ff7e18>, <class 'operator.attrgetter'>: <function CloudPickler.save_attrgetter at 0x103ff7ea0>, <class '_io.TextIOWrapper'>: <function CloudPickler.save_file at 0x103ff7f28>, <class 'ellipsis'>: <function CloudPickler.save_ellipsis at 0x103ff9048>, <class 'NotImplementedType'>: <function CloudPickler.save_not_implemented at 0x103ff90d0>, <class '_weakrefset.WeakSet'>: <function CloudPickler.save_weakset at 0x103ff9158>, <class 'logging.Logger'>: <function CloudPickler.save_logger at 0x103ff91e0>, <class 'logging.RootLogger'>: <function CloudPickler.save_root_logger at 0x103ff9268>}
#{<class 'NoneType'>: <function _Pickler.save_none at 0x10c566b70>, <class 'bool'>: <function _Pickler.save_bool at 0x10c566bf8>, <class 'int'>: <function _Pickler.save_long at 0x10c566c80>, <class 'float'>: <function _Pickler.save_float at 0x10c566d08>, <class 'bytes'>: <function _Pickler.save_bytes at 0x10c566d90>, <class 'str'>: <function _Pickler.save_str at 0x10c566e18>, <class 'tuple'>: <function _Pickler.save_tuple at 0x10c566ea0>, <class 'list'>: <function _Pickler.save_list at 0x10c566f28>, <class 'dict'>: <function _Pickler.save_dict at 0x10c5670d0>, <class 'set'>: <function _Pickler.save_set at 0x10c5671e0>, <class 'frozenset'>: <function _Pickler.save_frozenset at 0x10c567268>, <class 'function'>: <function _Pickler.save_global at 0x10c5672f0>, <class 'type'>: <function _Pickler.save_type at 0x10c567378>}
#{<class 'NoneType'>: <function _Pickler.save_none at 0x10529e598>, <class 'bool'>: <function _Pickler.save_bool at 0x10529e620>, <class 'int'>: <function _Pickler.save_long at 0x10529e6a8>, <class 'float'>: <function _Pickler.save_float at 0x10529e730>, <class 'bytes'>: <function _Pickler.save_bytes at 0x10529e7b8>, <class 'str'>: <function _Pickler.save_str at 0x10529e840>, <class 'tuple'>: <function _Pickler.save_tuple at 0x10529e8c8>, <class 'list'>: <function _Pickler.save_list at 0x10529e950>, <class 'dict'>: <function save_module_dict at 0x105319158>, <class 'set'>: <function _Pickler.save_set at 0x10529eb70>, <class 'frozenset'>: <function _Pickler.save_frozenset at 0x10529ebf8>, <class 'function'>: <function save_function at 0x105319f28>, <class 'type'>: <function save_type at 0x105319e18>, <class 'code'>: <function save_code at 0x1053190d0>, <class '_thread.lock'>: <function save_lock at 0x105319268>, <class '_thread.RLock'>: <function save_rlock at 0x1053192f0>, <class 'operator.itemgetter'>: <function save_itemgetter at 0x105319378>, <class 'operator.attrgetter'>: <function save_attrgetter at 0x105319400>, <class '_io.TextIOWrapper'>: <function save_file at 0x105319730>, <class '_io.BufferedWriter'>: <function save_file at 0x105319730>, <class '_io.BufferedReader'>: <function save_file at 0x105319730>, <class '_io.BufferedRandom'>: <function save_file at 0x105319730>, <class '_io.FileIO'>: <function save_file at 0x105319730>, <class '_pyio.TextIOWrapper'>: <function save_file at 0x1053196a8>, <class '_pyio.BufferedWriter'>: <function save_file at 0x1053196a8>, <class '_pyio.BufferedReader'>: <function save_file at 0x1053196a8>, <class '_pyio.BufferedRandom'>: <function save_file at 0x1053196a8>, <class 'functools.partial'>: <function save_functor at 0x105319510>, <class 'super'>: <function save_super at 0x105319598>, <class 'builtin_function_or_method'>: <function save_builtin_method at 0x105319620>, <class 'method'>: <function save_instancemethod0 at 0x1053197b8>, <class 'classmethod_descriptor'>: <function save_wrapper_descriptor at 0x105319a60>, <class 'wrapper_descriptor'>: <function save_wrapper_descriptor at 0x105319a60>, <class 'method_descriptor'>: <function save_wrapper_descriptor at 0x105319a60>, <class 'getset_descriptor'>: <function save_wrapper_descriptor at 0x105319a60>, <class 'member_descriptor'>: <function save_wrapper_descriptor at 0x105319a60>, <class 'method-wrapper'>: <function save_instancemethod at 0x105319840>, <class 'cell'>: <function save_cell at 0x1053198c8>, <class 'mappingproxy'>: <function save_dictproxy at 0x105319950>, <class 'slice'>: <function save_slice at 0x1053199d8>, <class 'NotImplementedType'>: <function save_singleton at 0x105319bf8>, <class 'ellipsis'>: <function save_singleton at 0x105319bf8>, <class 'range'>: <function save_singleton at 0x105319bf8>, <class 'weakref'>: <function save_weakref at 0x105319c80>, <class 'weakcallableproxy'>: <function save_weakproxy at 0x105319d90>, <class 'weakproxy'>: <function save_weakproxy at 0x105319d90>, <class 'module'>: <function save_module at 0x105319d08>, <class 'property'>: <function save_property at 0x105319ea0>, <class 'classmethod'>: <function save_classmethod at 0x10531a048>, <class 'staticmethod'>: <function save_classmethod at 0x10531a048>}

#print(pickle.loads(pickle.dumps(lck)))
#exit()

def f():
        class A(six.with_metaclass(ABCMeta)):
                def __init__(self):
#                        _check_lock = threading.Lock()
                        self.lck=lck #直接取globals导致没有有效手段清理与重建？
                        #self.mutex = _thread.allocate_lock()
                        #self.pool = redis.ConnectionPool(host = '127.0.0.1', port = 6379, decode_responses=True)
                        #self.lock_store = Redis(connection_pool = self.pool)
                        print(22222)
                        #self._executors_lock = self._create_lock() #序列化线程全局锁成员时出差！
                        pass
                def _create_lock(self):
                        return RLock()
#                def __setstate__(self,state):
#                    print(111)
#                    self.lck=None
#                def __getstate__(self):
#                    print(333)
#                    self.lck=None
#                    return "fdsljkflskdfj"
        #class A(six.with_metaclass(ABCMeta)): pass
        
#        def _pickle_method(obj):
#            print(99999,obj)
#            return _thread.LockType, () #重建
#        def _unpickle_method(func_name, obj, cls):
#            print(5555)
#            return obj   #重建
#        import _thread
#        copyreg.pickle(_thread.LockType, _pickle_method, _unpickle_method)
        
        return A

localA = f()
la = localA()


#print(localA)
#print(la)
ss=pickle.dumps(localA)
print(ss)
pickle.loads(ss)
exit()
#print(pickle.dumps(la))
#print(pickle.loads(pickle.dumps(la)))

#       ['AsyncGeneratorType', 'BuiltinFunctionType', 'BuiltinMethodType', 'ClassMethodDescriptorType', 'CodeType', 'CoroutineType', 'DynamicClassAttribute', 'FrameType', 'FunctionType', 'GeneratorType', 'GetSetDescriptorType', 'LambdaType', 'MappingProxyType', 'MemberDescriptorType', 'MethodDescriptorType', 'MethodType', 'MethodWrapperType', 'ModuleType', 'SimpleNamespace', 'TracebackType', 'WrapperDescriptorType', '_GeneratorWrapper', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', '_ag', '_calculate_meta', 'coroutine', 'new_class', 'prepare_class', 'resolve_bases']
#['BooleanType', 'BufferType', 'BuiltinFunctionType', 'BuiltinMethodType', 'ClassType', 'CodeType', 'ComplexType', 'DictProxyType', 'DictType', 'DictionaryType', 'EllipsisType', 'FileType', 'FloatType', 'FrameType', 'FunctionType', 'GeneratorType', 'GetSetDescriptorType', 'InstanceType', 'IntType', 'LambdaType', 'ListType', 'LongType', 'MemberDescriptorType', 'MethodType', 'ModuleType', 'NoneType', 'NotImplementedType', 'ObjectType', 'SliceType', 'StringType', 'StringTypes', 'TracebackType', 'TupleType', 'TypeType', 'UnboundMethodType', 'UnicodeType', 'XRangeType', '__all__', '__builtins__', '__doc__', '__file__', '__name__', '__package__']


exit()


print("------------------")

lck = threading.Lock()
class Foo:
    def run(self):
        self.lck=lck
        return None
    
    def bark(self):
        print('barking')
        
def __pickle(m):
    print(888881111)
    print(m)
    return object, ()
def __unpickle(m):
    print(999991111)
    print(m)
    return object, ()
#copyreg.pickle(types.BuiltinMethodType, __pickle, __unpickle)

ff=Foo.run
print(Foo.run.__dict__)
print(isinstance(ff,types.BuiltinMethodType))
print("77777",pickle.dumps(Foo.run))

exit()

print("------------------")
from multiprocessing import Pool

def test_func(x):
     return x**2

class Test:
     @classmethod
     def func(cls, x):
         return x**2

def mp_run(n, func, args):
     return Pool(n).map(func, args)
 
def _pickle_method(method):
    print(555555)
    """
    Pickle methods properly, including class methods.
    """
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    if isinstance(cls, type):
        # handle classmethods differently
        cls = obj
        obj = None
    if func_name.startswith('__') and not func_name.endswith('__'):
        #deal with mangled names
        cls_name = cls.__name__.lstrip('_')
        func_name = '_%s%s' % (cls_name, func_name)

    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    print(88888)
    """
    Unpickle methods properly, including class methods.
    """
    if obj is None:
        return cls.__dict__[func_name].__get__(obj, cls)
    for cls in cls.__mro__:
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

copyreg.pickle(types.MethodType, _pickle_method, _unpickle_method)

new_func = pickle.loads(pickle.dumps(Test.func))

exit()
if __name__ == '__main__':
     args = range(1,6)

     print(mp_run(5, test_func, args))
     # [1, 4, 9, 16, 25]

     print(mp_run(5, Test.func, args))
     """
     Exception in thread Thread-3:
     Traceback (most recent call last):
       File "/usr/lib64/python2.6/threading.py", line 532, in __bootstrap_inner
         self.run()
       File "/usr/lib64/python2.6/threading.py", line 484, in run
         self.__target(*self.__args, **self.__kwargs)
       File "/usr/lib64/python2.6/multiprocessing/pool.py", line 225, in _handle_tasks
         put(task)
     PicklingError: Can't pickle <type 'instancemethod'>: attribute lookup __builtin__.instancemethod failed
     """
     

print("OK")

exit()

