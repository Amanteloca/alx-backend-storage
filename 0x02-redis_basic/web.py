#!/usr/bin/env python3
"""
Caching request module
"""
import redis
import requests
from functools import wraps
from typing import Callable

def track_get_page(fn: Callable) -> Callable:
    """ Decorator for get_page
    """
    @wraps(fn)
    def wrapper(url: str) -> str:
        """ Wrapper that:
            - check whether a URL's data is cached
            - tracks how many times get_page is called
        """
        client = redis.Redis()
        # Increment the access count and set an expiration time for the count
        client.incr(f'count:{url}')
        client.expire(f'count:{url}', 10)

        # Check if the content is cached
        cached_page = client.get(f'{url}')
        if cached_page:
            return cached_page.decode('utf-8')

        # If not cached, make an HTTP request
        response = fn(url)
        
        # Cache the response with a 10-second expiration
        client.setex(f'{url}', 10, response)
        return response
    return wrapper

@track_get_page
def get_page(url: str) -> str:
    """ Makes an HTTP request to a given endpoint
    """
    response = requests.get(url)
    return response.text
