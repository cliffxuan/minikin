#!/usr/bin/env bash
DB=minikin
USER=postgres

dropdb -U $USER $DB
createdb -U $USER $DB
psql -U $USER $DB <<EOF 
CREATE TABLE short_url (
    slug CHAR(16),
    url TEXT,
    PRIMARY KEY (slug)
);
EOF
