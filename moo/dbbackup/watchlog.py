#!/usr/bin/python

import re
import sys
import os
from time import time,ctime
from select import select
CHECKPOINT = re.compile('CHECKPOINTING on Waterpoint.db.new.#[0-9]+# finished$')

f = sys.stdin

print ctime(time()), 'Starting up...'
sys.stdout.flush()

try:
    while 1:
	rd, wr, ex = select([f], [f], [f])
	line = f.readline()
	line = line[:-1]
	if CHECKPOINT.search(line):
	    print line
	    print ctime(time()), ' Running /home/wp/bin/backup...'
	    sys.stdout.flush()	    
	    os.system('/home/wp/bin/backup')
	    print ctime(time()), ' Done.'
	    sys.stdout.flush()
except:
    pass

print ctime(time()), 'Ending...'
sys.stdout.flush()	
