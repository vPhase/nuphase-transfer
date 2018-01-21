#!/usr/bin/env python 

# Script for processing hk data


import fcntl 
import sqlite3 
import time
import os
import sys 

if not 'NUPHASE_DATABASE' in os.environ: 
    print "You must define the NUPHASE_DATABASE environmental variable to point to the appropriate sqlite3 database" 
    sys.exit(1) 


south_prefix = "/home/dropboxes/nuphase01/south/SPS_NUPHASE_RAW_hk_" 
north_prefix = "/home/dropboxes/nuphase01/north/hk/SPS_NUPHASE_HK_" 

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



def is_in_db(detid, year, month, day, hk_time): 
    c.execute("select count(id) from hk where detector=? and hk_date=? and hk_time=?", ( detid, "%04d-%02d-%02d" %( year,month, day), hk_time))
    return int(c.fetchone()[0]) 

# e.g. process_hk(1, "/home/radio/data/nuphase01/raw_data/hk/") 
def process_hk(detector_id, hk_dir):   

    #ensure we only have one process_hk running at once 
    lock_file = open('/tmp/nuphase.process_hk.lock','w+'); 

    while True: 
        try: 
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as e: 
            if e.errno != errno.EAGAIN: 
                raise 
            else: 
                time.sleep(1) 


    for year in get_int_dirs(hk_dir): 
        for month in get_int_dirs( "%s/%d" % (hk_dir,year)): 
            for day in get_int_dirs( "%s/%d/%02d" % (hk_dir,year,month)): 

                tar_us  = [] 
                for hkfile in os.listdir("%s/%d/%02d/%02d" % (hk_dir,year,month,day)): 
                    if hkfile.endwsith(".hk.gz") and os.stat("%s/%d/%02d/%02d/%s" % (hk_dir,year,month,day,hkfile)).st_size: 
                        try: 
                            hk_time = int(hkfile.replace(".hk.gz",""))
                            if is_in_db(detector_id,year,month,day,hk_time) == 0:
                                tar_us.append(hk_time) 
                        except:
                            pass
                 
                
                if len(tar_us) == 0: 
                    continue 

                tar_us.sort() 

                ## create tar files
                north_tar_file = "%s%d-%d-%d-%d-%d.tar" % (north_prefix, year, month, day, tar_us[0], tar_us[-1]); 
                south_tar_file = "%s%%d-%d-%d-d-%d.tar" % (south_prefix_prefix, year, month, day, tar_us[0], tar_us[-1]); 

                os.system("tar -cf %s" % (south_tar_file)) 
                os.system("tar -cf %s"% (north_tar_file)) 

                for hk_time in tar_us: 

                    hk_file = "%d/%02d/%02d/%06d.hk.gz" % (hk_dir,year,month,day,hk_time) 
                    os.system("tar -rf %s -C %s %s" % (north_tar_file, hk_dir, hk_file)) 
                    os.system("tar -rf %s -C %s %s" % (south_tar_file, hk_dir, hk_file)) 
                    # add to database
                    c.execute("insert into hk(detector, hk_date,hk_time,processed_time) VALUES(?, ?, ?, datetime(now()))" % (detector_id, "%04d-%02d-%02d" % (year,month,day), hk_time))

                #commit
                c.commit() 

                north_sem = north_tar_file.replace(".tar",".sem"); 
                south_sem = south_tar_file.replace(".tar",".sem"); 

                os.system("touch %s" % (north_sem)); 
                os.system("touch %s" % (south_sem)); 


    fcntl.flock(lock_file, fcntl.LOCK_UN)
    




if __name__=="__main__": 

    if len(sys.argv) < 3 :
      print " usage : process_hk.py detid hk_root" 
      sys.exit(1) 

    process_hk(int(sys.argv[1]), sys.argv[2])
                        
                        




                        
















