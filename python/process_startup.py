#!/usr/bin/env python 

# Script for processing startup data


import fcntl 
import sqlite3 
import time
import os
import sys 

if not 'NUPHASE_DATABASE' in os.environ: 
    print "You must define the NUPHASE_DATABASE environmental variable to point to the appropriate sqlite3 database" 
    sys.exit(1) 


south_prefix = "/home/dropboxes/nuphase01/south/SPS_NUPHASE_RAW_startup_" 
north_prefix = "/home/dropboxes/nuphase01/north/startup/SPS_NUPHASE_HK_startup_" 

db = sqlite3.connect(os.environ['NUPHASE_DATABASE']) 
c = db.cursor() 

def get_int_dirs(path):  

    files = os.listdir(path) 
    int_files = [] 

    for f in files: 
        try: 
            i = int(f) 
            int_files.append(i) 
        except ValueError: 
            pass

    return int_files



def is_in_db(detid, fname): 
    c.execute("select count(id) from startup where detector=? and name=?", ( detid, fname))
    return int(c.fetchone()[0]) 

# e.g. process_startup(1, "/home/radio/data/nuphase01/raw_data/startup/") 
def process_startup(detector_id, startup_dir):   

    #ensure we only have one process_startup running at once 
    lock_file = open('/tmp/nuphase.process_startup.lock','w+'); 

    while True: 
        try: 
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as e: 
            if e.errno != errno.EAGAIN: 
                raise 
            else: 
                time.sleep(1) 


    tar_us  = [] 
    for f in os.listdir(startup_dir): 

        if f.endswith(".hk.gz") and not is_in_db(detid, f.replace("hk.gz","")): 
            tar_us.append(f.replace("hk.gz",""))
                


    if len(tar_us):

        tar_us.sort() 

        ## create tar files
        north_tar_file = "%s%s-%s.tar" % (north_prefix, tar_us[0], tar_us[-1]); 
        south_tar_file = "%s%s-%s.tar" % (south_prefix_prefix, tar_us[0], tar_us[-1]); 

        os.system("tar -cf %s" % (south_tar_file)) 
        os.system("tar -cf %s"% (north_tar_file)) 

        for name in tar_us: 
            startup_file = "%s/%s.hk.gz" % (startup_dir,name) 
            os.system("tar -rf %s %s" % (north_tar_file, startup_file)) 
            os.system("tar -rf %s %s" % (south_tar_file, startup_file)) 
            # add to database
            c.execute("insert into startup(detector, name,processed_time) VALUES(?, ?, datetime(now()))" % (detector_id, name))

        #commit
        c.commit() 

        north_sem = "%s%s-%s.sem" % (north_prefix, tar_us[0], tar_us[-1]); 
        south_sem = "%s%s-%s.sem" % (south_prefix_prefix, tar_us[0], tar_us[-1]); 

    fcntl.flock(lock_file, fcntl.LOCK_UN)
    



if __name__=="__main__": 

    if len(sys.argv) < 3 :
      print " usage : process_startup.py detid startup_root" 
      sys.exit(1) 

    process_startup(int(sys.argv[1]), sys.argv[2])
                        
                        




                        
















