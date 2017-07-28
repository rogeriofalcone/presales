#!/bin/bash
createdb $1
pg_restore --no-owner -1 -v -n public -d $1 $2
