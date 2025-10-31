#!/bin/bash

set -e

IP=$(docker node inspect $(docker node ls -q -f "role=manager") --format '{{.Status.Addr}}')
echo "$IP"
