/** This program summarizes hk files , inserting results into a db
 *
 **/ 

#include "nuphase.h" 
#include <stdio.h> 
#include <stdlib.h>
#include <zlib.h> 
#include <sqlite3.h> 

int main(int nargs, char ** args) 
{

  if (nargs < 3) 
  {
    fprintf(stderr, "Usage: summarize_hk file.status.gz period_in_secs"); 
    return 1; 
  }

  const char * file = args[1]; 
  int period = atoi(args[2]); 

  double last_time = 0; 
  nuphase_hk_t hk; 

  gzFile f = gzopen(file,"r"); 

  sqlite3 * db = 0; 
  int rc = sqlite3_open(getenv("NUPHASE_DATABASE"), &db); 

  if (rc) 
  {
    fprintf(stderr, "Couldn't open database!!!! %s\n", sqlite3_errmsg(db)); 
    return 1; 
  }

  sqlite3_exec(db, "BEGIN", 0,0,0); 

  while (!nuphase_hk_gzread(f, &hk))
  {
    double t =  hk.unixTime + 1e-3 * hk.unixTimeMillisecs; 
    if ( t > last_time + period) 
    {
      last_time = t; 
      char * statement; 
      asprintf(&statement, 
               "INSERT INTO hk_summary (unixtime, temp_master, temp_slave, temp_case, current_master, current_slave, current_frontend) VALUES(%f, %d, %d, %d, %d, %d,%d);", 
               t, hk.temp_master, hk.temp_slave, hk.temp_case, hk.current_master,hk.current_slave, hk.current_frontend); 
      sqlite3_exec(db,statement,0,0,0); 
    }
  }

  sqlite3_exec(db, "COMMIT", 0,0,0); 
  sqlite3_close(db); 
  gzclose(f); 
  return 0; 
}




