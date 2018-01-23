#! /usr/bin/env python

# This script manages the other scripts. Some day we might read a config file, but for now, just modify things here

# Right now, this is single threaded and only does one thing at a time. For one station, this is probably fine, 
# but it won't be too hard to add parallel support 
# For things to function properly, 


#################### BEGIN CONFIGURATION #########################

#Maximum number of days to check a run for new files 
max_age_to_check_run = 5  

# The directory holding the raw data
raw_data_dir = "/home/radio/data/nuphase{detid}/{year}/raw_data/"

years = (2018) 
detids = (1) 

sleep_amount = 600 

nprocs = 4; 


#################### END CONFIGURATION #########################



import process_hk as hk
import process_startup as startup
import process_run  as run


import time 
import signal 
import os
import stat


time_to_stop = False


def handle_signal(signum, frame): 
    print "Caught deadly signal %d..." % (signum) 
    time_to_stop = True

signal.signal(signal.SIGINT, handle_signal) 
signal.signal(signal.SIGTERM, handle_signal) 


def loop(): 

    time_to_stop = False 

    while not time_to_stop: 

        hk_tasks = [] 
        run_tasks = [] 
        startup_tasks = [] 

        for year in years: 
            for detid in detids: 
                this_data_dir = raw_data_dir.replace("{detid}", "%02d" % (detid)).replace("{year}", str(year))

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

if __name__=="__main__": 
    loop() 
                        
                        






