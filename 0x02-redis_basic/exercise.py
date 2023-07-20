#!/usr/bin/env python3
"""
0.Create a Cache class. In the __init__ method, store an instance of
the Redis client as a private variable named _redis (using redis.Redis())
and flush the instance using flushdb.
Create a store method that takes a data argument and returns a string.
The method should generate a random key (e.g. using uuid), store the
input data in Redis using the random key and return the key.

1.Create a get method that take a key string argument and an optional Callable
argument named fn. This callable will be used to convert the data back to the
desired format.
Remember to conserve the original Redis.get behavior if the key does not exist.
Also, implement 2 new methods: get_str and get_int that will automatically
parametrize Cache.get with the correct conversion function.

2.Implement a system to count how many times methods of the Cache class are
called.
Above Cache define a count_calls decorator that takes a single method
Callable
argument and returns a Callable.
As a key, use the qualified name of method using the __qualname__ dunder
method.
Create and return function that increments the count for that key every
time the method is called and returns the value returned by the original
method.

3.Define a call_history decorator to store the history of inputs and outputs
for a particular function.
Everytime the original function will be called, we will add its input
parameters to one list in redis, and store its output into another list.
In call_history, use the decorated function’s qualified name and append
":inputs"and ":outputs" to create input and output list keys, respectively.

Call_history has a single parameter named method that is a Callable and returns
a Callable.
In the new function that the decorator will return, use rpush to append the
input arguments. Remember that Redis can only store strings, bytes and numbers.
Therefore, we can simply use str(args) to normalize. We can ignore potential
kwargs for now.
Execute the wrapped function to retrieve the output. Store the output using
rpush in the "...:outputs" list, then return the output.
Decorate Cache.store with call_history
"""

import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """returns a Callable"""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper for decorated function"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """store the history of inputs and outputs"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper for the decorated function"""
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output

    return wrapper


def replay(fn: Callable):
    """display the history of calls of a particular function"""
    r = redis.Redis()
    function_name = fn.__qualname__
    value = r.get(function_name)
    try:
        value = int(value.decode("utf-8"))
    except Exception:
        value = 0

    # print(f"{function_name} was called {value} times")
    print("{} was called {} times:".format(function_name, value))
    # inputs = r.lrange(f"{function_name}:inputs", 0, -1)
    inputs = r.lrange("{}:inputs".format(function_name), 0, -1)

    # outputs = r.lrange(f"{function_name}:outputs", 0, -1)
    outputs = r.lrange("{}:outputs".format(function_name), 0, -1)

    for input, output in zip(inputs, outputs):
        try:
            input = input.decode("utf-8")
        except Exception:
            input = ""

        try:
            output = output.decode("utf-8")
        except Exception:
            output = ""

        # print(f"{function_name}(*{input}) -> {output}")
        print("{}(*{}) -> {}".format(function_name, input, output))


class Cache:
    """Create a Cache class"""

    def __init__(self):
        """store an instance of the Redis client"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """generate a random key"""
        random_key = str(uuid4())
        self._redis.set(random_key, data)
        return random_key

    def get(self, key: str,
            fn: Optional[callable] = None) -> Union[str, bytes, int, float]:
        """convert the data back to the desired format"""
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        """automatically parametrize Cache.get with the correct
        conversion function"""
        value = self._redis.get(key)
        return value.decode("utf-8")

    def get_int(self, key: str) -> int:
        """automatically parametrize Cache.get with the correct
        conversion function"""
        value = self._redis.get(key)
        try:
            value = int(value.decode("utf-8"))
        except Exception:
            value = 0
        return value
