#! /usr/bin/env python3

# This script manages the other scripts. Some day we might read a config file, but for now, just modify things here

# Right now, this is single threaded and only does one thing at a time. For one station, this is probably fine, 
# but it won't be too hard to add parallel support by using e.g. multiprocess.Pool with process_run. 

# Recommend you don't run this directly unless you know what you're doing, but instead use shell script



## import the configuration file 


import cfg 
import process_hk as hk
import io
import process_startup as startup
import process_run  as run
import smtplib 
from email.mime.text import MIMEText
import traceback
import satellite_time
import send_monitor_email 
import time 
import signal 
import os
import stat
import sys 
import fcntl 
from importlib import reload 



time_to_stop = False


def handle_signal(signum, frame): 
    global time_to_stop 
    print ("Caught deadly signal %d..." % (signum))
    print ("Will quit after current transaction")
    time_to_stop = True

signal.signal(signal.SIGINT, handle_signal) 
signal.signal(signal.SIGTERM, handle_signal) 



def loop(): 

    global time_to_stop 
    time_to_stop = False 

    last_sat = 0; 

    lock_file = open(cfg.manager_lockfile,'w+'); 
    try: 
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except: 
        print("Could not get lock file. Is more than one manager running? lockfile")
        sys.exit(1)


    while time_to_stop == False: 
      try: 

        reload(cfg) 
      
        if satellite_time.secs_since_dscs_up() < 6*3600 and time.time() - os.stat(".last_email").st_mtime > 3600*12: 
          os.system("touch .last_email"); 
          send_monitor_email.send_email() 



        for year in cfg.years: 
            if time_to_stop: 
              break 
            for detid in cfg.detids: 
                this_data_dir = cfg.raw_data_dir.replace("{detid}", "%02d" % (detid)).replace("{year}", str(year))

                startup.process_startup(detid, this_data_dir + "/startup")

                hk.process_hk(detid, this_data_dir + "/hk")

                #now loop over runs and check if they should be processed 
                for subdir in sorted(os.listdir(this_data_dir), reverse=True): 
                     
                    if time_to_stop: 
                      break 

                    if subdir.startswith("run") and subdir[3:].isdigit(): 
                        stinfo = os.stat(this_data_dir + "/" + subdir)
                        age = time.time() - stinfo.st_mtime 
                        if stat.S_ISDIR(stinfo.st_mode) and age < cfg.max_age_to_check_run and age > cfg.min_age_to_check_run: 
                            # is a directory, and not too old, let's do it
                            run.process_run(detid, this_data_dir, int(subdir[3:])) 

  

        if not time_to_stop: 
          time.sleep(cfg.sleep_amount) 

      except Exception as e: 


        msg = MIMEText(str(e))
        traceback.print_tb(sys.exc_info()[2])

        me = os.environ["USER"] + "@" + os.environ["HOSTNAME"]  
        msg['To'] = cfg.email; 
        msg['From'] = me
        msg['Subject'] = "nuphase-transfer crashed :(" 

        smtplib.SMTP('localhost').sendmail(me,[cfg.email], msg.as_string())

        raise e

    print ("Goodbye") 
    fcntl.flock(lock_file, fcntl.LOCK_UN)

if __name__=="__main__": 
    loop() 
                        
                        






