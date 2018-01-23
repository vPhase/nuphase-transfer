#! /usr/bin/env python


import fcntl 
import sqlite3 
import time
import os
import sys 
import cfg

north_prefixes = cfg.run_dropbox_north_prefixes
south_prefix = cfg.run_dropbox_south_prefix

n_best = cfg.N_best
n_rf = cfg.N_rf
n_sw = cfg.N_sw

if not 'NUPHASE_DATABASE' in os.environ: 
    print "You must define the NUPHASE_DATABASE environmental variable to point to the appropriate sqlite3 database" 
    sys.exit(1) 


db = sqlite3.connect(os.environ['NUPHASE_DATABASE']) 
c = db.cursor() 


def is_in_db(detid,db_name,run, filename): 
    c.execute("select count(id) from %s where filename=? and run=? and detid=?" % (db_name,), (filename, run, detid))
    return int(c.fetchone()[0])



def get_list_to_process(det_id, data_dir, run, filetype): 

    process_list = []
    process_list = []
    for f in os.listdir("%s/%d/%s" % (data_dir, run, filetype)): 

            filename = int(f.split(".")[0])
            if not is_in_db(det_id, filetype, run, filename): 
                process_list.append(filename)
    
    process_list.sort() 
    return process_list

           



def process_run(det_id, data_dir, run): 

    # make sure we only have one process on this run 
    lock_file = open("/tmp/nuphase.process_run_%d.lock" % 20,'w+'); 

    while True: 
        try: 
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except IOError as e: 
            if e.errno != errno.EAGAIN: 
                raise 
            else: 
                time.sleep(1) 

    

    south_tar_file = "%s_run%d_%d "% (south_prefix.replace("{detid}", "%02d" % (detid,)), run, int(time.time())), 
    c.execute("insert into south_tar_files(tar_file) values(?)", (os.path.basename(south_tar_file),))
    south_tar_file_id = c.lastrowid 

    for ftype in ( "header", "status", "event"): 
        process_list = get_list_to_process(det_id, data_dir, run, ftype); 


        north_tar_file = "%s_r%d_%d-%d.tar", north_prefix[filetype].replace("{detid}","%02d" % (detid,)), run, process_list[0], process_list[-1]; 

        c.execute("insert into north_tar_files(tar_file) values(?)", (os.path.basename(north_tar_file),))
        north_tar_file_id = c.lastrowid

        for i in process_list: 

            f = "%s/%d.%s.gz" % (ftype, i, ftype) 

            if ftype != "event": 
                os.system("tar -rf %s -C %s %s" % (north_tar_file, data_dir, f) )
                os.system("tar -rf %s -C %s %s" % (south_tar_file, data_dir, f) )
                c.execute("insert into %s(run, detector, filename, bytes, north_file_id,south_file_id) VALUES(?,?,?,?,?,?)" % (ftype,),(run, det_id, i, os.stat(f).st_size,north_tar_file_id, south_tar_file_id))

            else:
                # generate filtered file 

                filtered = f.replace("event.gz","filtered.gz") 
                ret = os.system("nuphase-event-filter %s %s %s %d %d %d", f, f.replace("event","header"), filtered, n_best, n_rf, n_sw) 
                if ret == 0: 
                    os.system("tar -rf %s -C %s %s" % (north_tar_file, data_dir, filtered) )
                    os.system("tar -rf %s -C %s %s" % (south_tar_file, data_dir, f) )
                    c.execute("insert into %s(run, detector, filename, bytes, north_file_id, south_file_id) VALUES(?,?,?,?,?,?)" % (ftype,), (run, det_id, i, os.stat(filtered).st_size, north_tar_file_id, south_tar_file_id))

        c.commit() 

        north_sem = north_tar_file.replace(".tar",".sem"); 
        os.system("touch %s" % (north_sem))


    south_sem = south_tar_file.replace(".tar",".sem"); 
    os.system("touch %s" % (south_sem))
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    close(lock_file) 
    os.unlink(lock_file) 

if __name__=="__main__": 

    if len(sys.argv) < 3 :
      print " usage : process_run.py detid data_dir run" 
      sys.exit(1) 

    process_run(int(sys.argv[1]), sys.argv[2], sys.argv[3])
                        
 
