#!/bin/bash
set -e

echo "Seeding MongoDB with data.json..."

jq -s . < /docker-entrypoint-initdb.d/data.jsonl > /tmp/data.json

mongoimport --db=grantbot --collection=documents --file=/tmp/data.json --jsonArray

echo "Seeding done."
