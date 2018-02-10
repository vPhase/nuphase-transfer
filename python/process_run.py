#! /usr/bin/env python


import fcntl 
import sqlite3 
import traceback 
import time
import os
import os.path 
import sys 
import cfg

if not 'NUPHASE_DATABASE' in os.environ: 
    print "You must define the NUPHASE_DATABASE environmental variable to point to the appropriate sqlite3 database" 
    sys.exit(1) 


db = sqlite3.connect(os.environ['NUPHASE_DATABASE']) 


def is_in_db(c,detid,db_name,run, filename): 
    c.execute("select count(id) from %s where filename=? and run=? and detector=?" % (db_name,), (filename, run, detid))
    return int(c.fetchone()[0])



def get_list_to_process(c,det_id, data_dir, run, filetype): 

    process_list = []

    
    for d,sd,fs in os.walk("%s/run%d/%s" % (data_dir, run, filetype)): 
        for f in fs: 
          if f[0]==".": 
            continue  #skip hidden files 
#       try: 
          filename = (os.path.join(d,f).replace("%s/run%d/%s/" % (data_dir, run, filetype),"")) if filetype in ("cfg","aux") else int(f.split(".")[0])
          if not is_in_db(c,det_id, filetype, run, filename): 
             process_list.append(filename)
#       except: 
#         traceback.print_tb(sys.exc_info()[2])
#         pass 

    process_list.sort() 
    if len(process_list): 
      print "process list for run %d %s : " % (run,filetype) + str(process_list)  
    return process_list

           


def process_run(det_id, data_dir, run): 

    # reload the config, in case it changed 
    reload(cfg) 

    north_prefixes = cfg.run_dropbox_north_prefixes
    south_prefix = cfg.run_dropbox_south_prefix

    n_best = cfg.N_best
    n_rf = cfg.N_rf
    n_sw = cfg.N_sw


    # make sure we only have one process on this run 
    lockfile = cfg.run_lockfile.replace("{run}","%02d"%(run,))
    lock_file = open(lockfile,'w+'); 

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
    south_tar_file = "%s_run%d_%d.tar "% (south_prefix.replace("{detid}", "%02d" % (det_id,)), run, int(time.time())) 
    c.execute("insert into south_tar_files(tar_file) values(?)", (os.path.basename(south_tar_file),))
    south_tar_file_id = c.lastrowid 
    types_processed = 0

    for ftype in ( "header", "status", "event", "aux", "cfg"): 
        process_list = get_list_to_process(c,det_id, data_dir, run, ftype); 

        if len(process_list) == 0: 
          continue 

        types_processed+=1


        suffix  = str(time.time()) if ftype in ("aux","cfg") else "%d_%d" % (process_list[0], process_list[-1]) 
        north_tar_file = "%s_run%d_%s.tar" % (north_prefixes[ftype].replace("{detid}","%02d" % (det_id,)), run, suffix )  

        c.execute("insert into north_tar_files(tar_file) values(?)", (os.path.basename(north_tar_file),))
        north_tar_file_id = c.lastrowid
        processed = 0
        for i in process_list: 

            f = "run%d/%s/%s" % (run,ftype,i) if ftype in ("aux","cfg") else "run%d/%s/%d.%s.gz" % (run,ftype, i, ftype) 

            if ftype != "event": 
                os.system("tar -rf %s -C %s %s" % (north_tar_file, data_dir, f) )
                os.system("tar -rf %s -C %s %s" % (south_tar_file, data_dir, f) )
                if ftype == "status": 
                  os.system("summarize-status %s/%s %d" % (data_dir,f, cfg.status_summarize_period))
                c.execute("insert into %s(run, detector, filename, bytes, north_file_id,south_file_id) VALUES(?,?,?,?,?,?)" % (ftype,),(run, det_id, i, os.stat("%s/%s" % (data_dir,f)).st_size,north_tar_file_id, south_tar_file_id))
                processed += 1 

            else:
                # generate filtered file 

                filtered = f.replace("event.gz","filtered.gz") 
                ret = os.system("cd %s; nuphase-event-filter %s %s %s %d %d %d" %(data_dir, f, f.replace("event","header"), filtered, n_best, n_rf, n_sw)) 
                if ret == 0: 
                    os.system("tar -rf %s -C %s %s" % (north_tar_file, data_dir, filtered) )
                    os.system("tar -rf %s -C %s %s" % (south_tar_file, data_dir, f) )
                    c.execute("insert into event(run, detector, filename, bytes, north_file_id, south_file_id, nbest, nrf, nsw) VALUES(?,?,?,?,?,?,?,?,?)", (run, det_id, i, os.stat("%s/%s" % (data_dir,filtered)).st_size, north_tar_file_id, south_tar_file_id, n_best, n_rf, n_sw))
                    processed += 1


        if processed: 
          if ftype == "event": 
            os.system("cd %s; echo n_best=%d n_rf=%d n_sw=%d > run%d/filter.cfg; tar -rf %s run%d/filter.cfg" % (data_dir, n_best, n_rf, n_sw, run,  north_tar_file,run) )
          north_sem = north_tar_file.replace(".tar",".sem"); 
          os.system("touch %s" % (north_sem))

  

    if types_processed: 
      db.commit() 
      south_sem = south_tar_file.replace(".tar",".sem"); 
      os.system("touch %s" % (south_sem))
    else: 
      db.rollback() 

    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close() 
    os.unlink(lockfile) 

if __name__=="__main__": 

    if len(sys.argv) < 3 :
      print " usage : process_run.py detid data_dir run" 
      sys.exit(1) 

    process_run(int(sys.argv[1]), sys.argv[2], sys.argv[3])
                        
 
