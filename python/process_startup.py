#!/usr/bin/env python 

# Script for processing startup data


import fcntl 
import sqlite3 
import time
import os
import sys 
import cfg

if not 'NUPHASE_DATABASE' in os.environ: 
    print "You must define the NUPHASE_DATABASE environmental variable to point to the appropriate sqlite3 database" 
    sys.exit(1) 


south_prefix = cfg.startup_dropbox_south_prefix
north_prefix = cfg.startup_dropbox_north_prefix

db = sqlite3.connect(os.environ['NUPHASE_DATABASE']) 

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



def is_in_db(c,detid, fname): 
    c.execute("select count(id) from startup where detector=? and name=?", ( detid, fname))
    return int(c.fetchone()[0]) 

# e.g. process_startup(1, "/home/radio/data/nuphase01/raw_data/startup/") 
def process_startup(detector_id, startup_dir):   

    detid = "%02d" % (detector_id,)
    #ensure we only have one process_startup running at once 
    lock_file = open('/tmp/nuphase.process_startup.lock','w+'); 

    while True: 
        try: 
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break 
        except IOError as e: 
            if e.errno != errno.EAGAIN: 
                raise 
            else: 
                time.sleep(1) 


    c = db.cursor() 
    tar_us  = [] 
    for f in os.listdir(startup_dir): 

        if f.endswith(".hk.gz") and not is_in_db(c,detector_id, f.replace(".hk.gz","")) and os.stat("%s/%s" % (startup_dir, f)).st_size: 
            tar_us.append(f.replace(".hk.gz",""))
                


    if len(tar_us):

        tar_us.sort() 
        print "startup to process: " + str(tar_us)

        ## create tar files
        north_tar_file = "%s%s-%s.tar" % (north_prefix.replace("{detid}",detid), tar_us[0], tar_us[-1]); 
        south_tar_file = "%s%s-%s.tar" % (south_prefix.replace("{detid}",detid), tar_us[0], tar_us[-1]); 

        c.execute("insert into north_tar_files(tar_file) values(?)",(os.path.basename(north_tar_file),))
        north_tar_file_id = c.lastrowid; 
        c.execute("insert into south_tar_files(tar_file) values(?)",(os.path.basename(north_tar_file),))
        south_tar_file_id = c.lastrowid; 


        for name in tar_us: 
            startup_file = "%s.hk.gz" % (name) 

            os.system("tar -rf %s -C %s %s" % (north_tar_file, startup_dir, startup_file)) 
            os.system("tar -rf %s -C %s %s" % (south_tar_file, startup_dir, startup_file)) 
            

            # add to database
            c.execute("insert into startup(detector, name,bytes,north_file_id, south_file_id) VALUES(?, ?,?, ?, ?)",(detector_id, name, os.stat("%s/%s" % (startup_dir, startup_file)).st_size, north_tar_file_id, south_tar_file_id))

        #commit
        db.commit() 

        north_sem = north_tar_file.replace(".tar",".sem"); 
        south_sem = south_tar_file.replace(".tar",".sem"); 

        os.system("touch %s" % (north_sem)); 
        os.system("touch %s" % (south_sem)); 

    fcntl.flock(lock_file, fcntl.LOCK_UN)
    



if __name__=="__main__": 

    if len(sys.argv) < 3 :
      print " usage : process_startup.py detid startup_root" 
      sys.exit(1) 

    process_startup(int(sys.argv[1]), sys.argv[2])
                        
                        




                        
















