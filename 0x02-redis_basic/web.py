#!/usr/bin/env python3
"""
Implement a get_page function (prototype: def get_page(url: str) -> str:).
The core of the function is very simple. It uses the requests module to
obtain the HTML content of a particular URL and returns it.
"""
import redis
import requests
from typing import Callable
from functools import wraps

r = redis.Redis()


def count_url_access(func: Callable) -> Callable:
    """Decorator function that counts the number
    of times a particular URL was accessed
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Function responsible for incrementing count"""
        key = "count:{}".format(*args)
        text = func(*args, **kwargs)
        r.incr(key)
        r.expire(key, 10)
        return text
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """Obtains the HTML content of a particular
    URL.
    Returns:
        content (str): The HTML content of a url
    """
    results = requests.get(url)
    return results.text
