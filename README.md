# minikin
[![Build Status](https://travis-ci.org/cliffxuan/minikin.svg?branch=master)](https://travis-ci.org/cliffxuan/minikin) ![Open Source Licence](https://img.shields.io/github/license/cliffxuan/minikin.svg) [![Test Coverage](https://api.codeclimate.com/v1/badges/05a36da8519e15658e1c/test_coverage)](https://codeclimate.com/github/cliffxuan/minikin/test_coverage) [![Maintainability](https://api.codeclimate.com/v1/badges/05a36da8519e15658e1c/maintainability)](https://codeclimate.com/github/cliffxuan/minikin/maintainability)
<p align="center">
  <a href="https://minik.in"><img width="240" height="240" src="./static/logo.png"></a>
</p>
Minikin is a url shortener built in Python with asyncio. It's small in footprint, performant with little resources and yet can scale up big.

## How to use

Check it out using [httpie](https://httpie.org/).

- Create a short url for the 10,000 bitcoin for 2 pizza transaction on the bitcoin blockchain
> http POST https://minik.in/shorten_url url='https://www.blockchain.com/btc/tx/a1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d'

```
HTTP/1.1 201 Created
Connection: keep-alive
Content-Length: 45
Content-Type: application/json; charset=utf-8
Date: Thu, 09 Aug 2018 10:56:22 GMT
Server: nginx/1.14.0 (Ubuntu)

{
    "shortened_url": "https://minik.in/6ypXVDH"
}
```
- Click this url [https://minik.in/6ypXVDH](https://minik.in/6ypXVDH) or use `httpie`
> http https://minik.in/6ypXVDH
```
HTTP/1.1 302 Found
Connection: keep-alive
Content-Length: 114
Content-Type: application/json
Date: Thu, 09 Aug 2018 10:55:47 GMT
Location: https://www.blockchain.com/btc/tx/a1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d
Server: nginx/1.14.0 (Ubuntu)

{
    "location": "https://www.blockchain.com/btc/tx/a1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d"
}
```

## Building Components

- [aiohttp](https://github.com/aio-libs/aiohttp) HTTP server for asyncio
- [asyncpg](https://github.com/MagicStack/asyncpg) A fast PostgreSQL Database Client Library for Python/asyncio
- [postgresql](https://www.postgresql.org/) The world's most advanced open source relational database.

## Installation

This requires python3.6 and above.

- install pipenv
`pip install pipenv`

- install dependencies
`pipenv install`

- create postgresql database and table
One table with two columns (slug and url) are the minimum needed. The slug, i.e. the path of the short url is the primary key and is indexed.
```
createdb -U postgres minikin
psql -U postgres minikin <<EOF
CREATE TABLE short_url (
    slug CHAR(16),
    url TEXT,
    PRIMARY KEY (slug)
);
EOF
```

- start the server
`pipenv run python minikin/app.py`

- then it should be available
```
======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)
```

## Running Test

Automated tests are run on travis-ci [https://travis-ci.org/cliffxuan/minikin](https://travis-ci.org/cliffxuan/minikin).

These are 3 types tests currently and integration test will be added later.
- unittest
- flake8 for style
- mypy for type checking

To run these locally:
```
pip install tox
tox
```

## Design decisions and tradeoffs

### shortening algorithm
`full url` -> `md5` -> `base62` -> `take 7`

The hashing algorithm ensures the process is deterministic. 7 characters from 62 candidates allows 3.5 trillion different urls, which should allow the system to grow for 110 years if growing at 1000 per second.

### conflict and hash collision

Hash collision is not protected. If two urls hash into the same string, the latter will override the former. Because the chance of collision is really small, the overhead is not justified. This is also because url shortening is not critical that losing a url would not cause a big loss.

Also because the process is deterministic, the system doesn't check if the url already exists in the database and always performs an upsert.

### concurrency model

Event driven async socket is used instead of multi threading because it is in theory more efficient in handling heavy traffic. However, given that requests will be very short lived, thread pooling is probably also going to work well.


### database

A relational database in Postgresql is picked instead of a NoSQL database. This is mainly because Postgresql is one of the better supported databases for asyncio/aiohttp and also there are repeated reports of Postgresql out performing NoSQL database. A key value store in theory should be better for the system.


## Load Test Benchmark

Load test uses [Locust](https://locust.io/). The script are defined as [locustfile.py](tests/load/locustfile.py).

start the load test:
```
locust -f tests/load/locustfile.py --host=https://minik.in
```

<img src="benchmark.png"/>

Load profile:

- number of urls in db: 30k
- number of concurrent users: 2,000
- traffic distribution
    * 10% POST /shorten_url
    * 10% GET /[NOT FOUND]
    * 80% GET /[FOUND]

The machine under test:

- Cloud provider: Google Compute Engine
- Type: n1-standard-1
- Number of vCPU: 1
- RAM: 3.75GB
- Hard driver: 30GB SSD
- Monthly cost: $40
- Number of processes: 4
- Reverse proxy server: Nginx

Result:

- Request Per Second: it servers around 400 when the concurrent user number is less than 1000. at 2000 it's between 200 and 250.
- Error rate: around 1% all of which are connection errors
- CPU utilisation: 30% - 80%
- RAM: around 500MB

## Scale up and out

Because the state is not shared and the shortening process is determnistic, it can be easily scaled up. several instruments can be used independantly or collectively.

### get better hardware

Increasing the number of CPU should have an immediate impact. With more data, bigger RAM and hard drive will also boost the performance.

### traffic routing

Load balancing and traffic routing and will not only increase the capacity but also reliability. Several strategies can be used independantly or collectively. These include:

- Load balancing - split the load between multiple applications
- Failover routing - active-passive failover
- Geolocation routing - route traffic based on user location
- Geopromixity routing - route traffic based on location of the resource
- Latency routing - route traffic to server which provides the best latency

### scale database

Data and accessing of data can be split so each sub system can only deal with a partition of the data.

- split read and write - the system is heavier on read (url lookup) and lighter on write (short url creation). read operation can use slaves of a master database.
- sharding - without any dependency, data can be split based on the value of slug. for example, if split into 2, anything slug smaller than 1.76T can go to one partition and the rest to the other. It can be split infinitely based on needs as the results from the hashing algorith follows uniform distribution.

