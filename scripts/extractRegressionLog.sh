#!/bin/bash

logFile='all-combined.txt'
path='/home/ibisek/data/btsync/doma/radec/out-2020-04-16b'

pattern1='REGRESSION'

pattern2='NG = fn (SP)'
var='ng-sp'

pattern2='FC = fn (SP)'
var='fc-sp'

pattern2='ITT = fn (NG)'
var='itt-ng'

pattern2='ITT = fn (SP)'
var='itt-sp'


cat $path/$logFile |grep "$pattern1" |grep "$pattern2" > $path/$var.txt

cat $path/$var.txt |cut -d';' -f 2,5,7,8 > $path/$var.csv


