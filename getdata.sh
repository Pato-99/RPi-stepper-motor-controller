#!/bin/bash

TIMEFORMAT='%lR'
for i in {1..20}
do
	(time ./run.py 45 45) &>> data/data45
done

for i in {1..20}
do
	(time ./run.py 90 45) &>> data/data90
done

for i in {1..20}
do
	(time ./run.py 135 45) &>> data/data135
done

for i in {1..20}
do
	(time ./run.py 180 45) &>> data/data180
done

for i in {1..20}
do
	(time ./run.py 360 45) &>> data/data360
done

