#!/bin/bash
FILE_1='/home/wenbin/multiprocess/nohup.out'
FILE_2='/home/wenbin/multiprocess/SETI_MUL_20000_100000.csv'

awk 'END{print NR}' $FILE_1

last_time=$(stat -c %Y $FILE_2)
formart_date=$(date '+%Y-%m-%d/%H:%M:%S' -d @$last_time)
echo $formart_date