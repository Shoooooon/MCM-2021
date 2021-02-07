#!/bin/bash
File="use_these_rows.txt"
Lines=$(cat $File)
for Line in $Lines
do
	echo "$Line"		#Replace with job request to run "python DroneDataProcessing.py $Line", however that works on super computer
done
