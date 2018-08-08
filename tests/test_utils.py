# -*- coding: utf-8 -*-
import pytest

from minikin.utils import base62_encode, generate_slug, validate_url


@pytest.mark.parametrize('num,expected', [
    (0, '0'),
    (9, '9'),
    (10, 'a'),
    (35, 'z'),
    (36, 'A'),
    (61, 'Z'),
    (62, '10'),
    (3843, 'ZZ'),
])
def test_base62_encode(num, expected):
    encoded = base62_encode(num)
    assert encoded == expected, f'expected {expected} got {encoded}'


@pytest.mark.parametrize('text,size,expected', [
    ('a', 1, 'o'),
    ('a', 7, 'o4jNvaw'),
    ('z', 1, '7'),
    ('z', 7, '7EUyh3c'),
    ('z', 22, '7EUyh3cL3Jo3PG38xJF97p'),
    ('z', 34, '7EUyh3cL3Jo3PG38xJF97p'),
    ('a12345', 22, '5lhi0wm1g2jkSEemLTupXw')
])
def test_generate_slug(text, size, expected):
    slug = generate_slug(text, size)
    assert slug == expected, f'expected {expected} got {slug}'
    assert len(slug) <= size


@pytest.mark.parametrize('url', [
    'https://google.com',
    'www.helloworld.com',
])
def test_valid_url(url):
    assert validate_url(url)


@pytest.mark.parametrize('url', [
    'ssh://git@github.com',
    'abc def',
])
def test_invalid_url(url):
    assert not validate_url(url)
