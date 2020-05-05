#!/bin/bash

logFile='all-combined.txt'
path='/home/ibisek/data/btsync/doma/radec/out-2020-04-15'

pattern='Omitting; NG = fn (SP)'
var='ng-sp'

pattern='Omitting; FC = fn (SP)'
var='fc-sp'

pattern='Omitting; ITT = fn (NG)'
var='itt-ng'

pattern='Omitting; ITT = fn (SP)'
var='itt-sp'


cat $path/$logFile |grep "$pattern" > $path/$var.txt

cat $path/$var.txt |cut -d'<' -f 2| cut -d'>' -f 1 > $path/$var.csv


