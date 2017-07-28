#!/bin/bash
createdb $1
pg_restore -1 -v -n public -d $1 $2
