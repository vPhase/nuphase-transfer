#! /usr/bin/env python

# This script manages the other scripts. Some day we might read a config file, but for now, just modify things here

# Right now, this is single threaded and only does one thing at a time. For one station, this is probably fine, 
# but it won't be too hard to add parallel support by using e.g. multiprocess.Pool with process_run. 

# Recommend you don't run this directly unless you know what you're doing, but instead use shell script


#################### BEGIN CONFIGURATION #########################

#Maximum number of days to check a run for new files 
max_age_to_check_run = 5  

# The directory holding the raw data
raw_data_dir = "/home/radio/data/nuphase{detid}/{year}/raw_data/"

years = (2018,) 
detids = (1,) 

sleep_amount = 600 

nprocs = 4; 
 

lockfile = "/tmp/nuphase.manager.lock" 


#################### END CONFIGURATION #########################



import process_hk as hk
import process_startup as startup
import process_run  as run


import time 
import signal 
import os
import stat
import sys 
import fcntl 



time_to_stop = False


def handle_signal(signum, frame): 
    print "Caught deadly signal %d..." % (signum) 
    time_to_stop = True

signal.signal(signal.SIGINT, handle_signal) 
signal.signal(signal.SIGTERM, handle_signal) 


def loop(): 

    time_to_stop = False 

    lock_file = open(lockfile,'w+'); 
    try: 
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except: 
        print "Could not get lock file. Is more than one manager running? lockfile"
        sys.exit(1)


    while not time_to_stop: 


        for year in years: 
            for detid in detids: 
                this_data_dir = raw_data_dir.replace("{detid}", "%02d" % (detid)).replace("{year}", str(year))

                print this_data_dir

                startup.process_startup(detid, this_data_dir + "/startup")

                hk.process_hk(detid, this_data_dir + "/hk")

                #now loop over runs and check if they should be processed 
                for subdir in sorted(os.listdir(this_data_dir), reverse=True): 

                    if subdir.startswith("run") and subdir[3:].isdigit(): 
                        stinfo = os.stat(this_data_dir + "/" + subdir)

                        if stat.S_ISDIR(stinfo.st_mode) and time.time() - stinfo.mtime < max_age_to_check_run * 3600 * 24: 
                            # is a directory, and not too old, let's do it
                            run.process_run(detid, this_data_dir, int(subdir[3:])) 


        time.sleep(sleep_amount) 

    print "Goodbye"  
    fcntl.flock(lock_file, fcntl.LOCK_UN)

if __name__=="__main__": 
    loop() 
                        
                        






