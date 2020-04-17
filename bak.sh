#!/bin/bash

Index=`date +%Y%m%d`
sql_name=/home/andy/projects/mcu_config/Flask/db_learn.sql

mysqldump -uroot -p123456 --databases db_learn >${sql_name}

tar -zcvf Flask${Index}.tar ./Flask

