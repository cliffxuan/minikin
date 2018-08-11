# -*- coding: utf-8 -*-
import os
import json
from random import choice

from faker import Faker
from locust import HttpLocust, TaskSet, task

from minikin.utils import generate_slug

PWD = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(PWD, 'slugs')) as fo:
    slugs = fo.readlines()[2:-1]  # ommit header and footer


def gen_url():
    fake = Faker()
    uri, slug = fake.uri().rstrip('/'), fake.slug()
    return f'{uri}#{slug}'


class Tasks(TaskSet):

    @task(1)
    def shorten_url(self):
        self.client.post("/shorten_url", json.dumps({"url": gen_url()}))

    @task(1)
    def not_found(self):
        slug = generate_slug(gen_url(), 7)
        with self.client.get(f'/{slug}',
                             name='/[not-found]',
                             catch_response=True,
                             allow_redirects=False) as response:
            if response.status_code == 404:
                response.success()

    @task(8)
    def found(self):
        slug = choice(slugs).strip()
        self.client.get(f'/{slug}', name='/[found]', allow_redirects=False)


class User(HttpLocust):
    task_set = Tasks
    min_wait = 0
    max_wait = 0
