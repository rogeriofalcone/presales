#!/bin/bash

bfile=$1_`date +"%Y%m%d"`.dump

echo "Start backup time: `date`"

/usr/bin/pg_dump -Fc $1 > $bfile
echo "Created backup $bfile"
echo "End backup time: `date`"
