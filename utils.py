# -*- coding: utf-8 -*-
"""
utility functions
"""
import hashlib
import string


def base62_encode(num: int):
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


def generate_slug(url: str, size: int):
    """
    generate slug from a url
    """
    hash_num = int(hashlib.md5(url.encode('utf-8')).hexdigest(), 16)
    encoded = base62_encode(hash_num)
    return encoded[:size]


def validate_url(url: str) -> bool:
    """
    validate url
    """
    # TODO implement me
    return True
