#!/bin/bash

cd ../data/in

# remove all spaces from the csv files:
sed -i -e 's/ //g' *csv

# use ' as field separators:
sed -i 's/,/;/g' *csv

# join date+time into one col:
sed -i -e 's/;/ /' *csv

