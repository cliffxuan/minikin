# -*- coding: utf-8 -*-
from asyncio import Future
from typing import Optional


class FakeConnection:

    def __init__(self, results: Optional[dict]=None) -> None:
        """
        resutls is used to pass in the result for futures,
        example: results={
            'execute': None,
            'fetchrow': {'column': 'value'}
        }
        """
        if results is None:
            results = {}
        self.results = results

    def __aenter__(self):
        future = Future()
        future.set_result(self)
        return future

    def __aexit__(self, *args):
        future = Future()
        future.set_result(False)
        return future

    def transaction(self):
        class _Transaction:

            def __aenter__(self):
                future = Future()
                future.set_result(None)
                return future

            def __aexit__(self, *args):
                future = Future()
                future.set_result(False)
                return future
        return _Transaction()

    def execute(self, *args, **kw):
        future = Future()
        future.set_result(self.results.get('execute'))
        return future

    def fetchrow(self, *args, **kw):
        future = Future()
        future.set_result(self.results.get('fetchrow'))
        return future


def make_future(result=None, exception=None):
    future = Future()
    if exception:
        future.set_exception(exception)
    else:
        future.set_result(result)
    return future
