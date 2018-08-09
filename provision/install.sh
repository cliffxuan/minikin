#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# install postgresql
apt-get install postgresql
cp $DIR/pg_hba.conf /etc/postgresql/10/main/pg_hba.conf
service postgresql restart

# install nginx
apt-get install nginx
cp $DIR/nginx.conf /etc/nginx/sites-enabled/default
service nginx restart
