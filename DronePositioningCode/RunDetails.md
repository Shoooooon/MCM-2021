Hi. This file is about how to call/use the code here.

The file 'use_these_rows.txt' contains 900+ row numbers, each on its own line.
These represent the clusters to run.
The bash call to run the script is 'python DroneDataProcessing.py ROW_NUMBER' where ROW_NUMBER is a number from the file.
Note that the above call should be used from inside this folder.

Each of these 900+ calls constitutes a completely separate task, so you should probably have each one be its own job on the supercomputer.
