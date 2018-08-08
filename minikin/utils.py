# -*- coding: utf-8 -*-
"""
utility functions
"""
import hashlib
import string
from urllib.parse import urlparse

import validators


def base62_encode(num: int) -> str:
    """
    Encode a positive number using 62 characters 0-1a-zA-Z
    """
    charset = string.digits + string.ascii_letters
    size = len(charset)
    result = ''
    while True:
        num, rem = num // size, num % size
        result += charset[rem]
        if num == 0:
            return ''.join(reversed(result))


def generate_slug(text: str, size: int) -> str:
    """
    generate slug from a string
    """
    hash_num = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
    encoded = base62_encode(hash_num)
    return encoded[:size]


def validate_url(url: str) -> str:
    """
    validate url. steps:
    1. if url scheme is missing, use http.
    2. use valilidators.url to validate
    """
    if urlparse(url).scheme == '':
        url = f'http://{url}'
    if not validators.url(url):
        raise ValueError
    return url
