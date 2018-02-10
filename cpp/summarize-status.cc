/** This program summarizes status files , inserting results into a db
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
    fprintf(stderr, "Usage: summarize_status file.status.gz period_in_secs"); 
    return 1; 
  }

  const char * file = args[1]; 
  int period = atoi(args[2]); 

  double last_time = 0; 
  nuphase_status_t status; 

  gzFile f = gzopen(file,"r"); 

  sqlite3 * db = 0; 
  int rc = sqlite3_open(getenv("NUPHASE_DATABASE"), &db); 

  if (rc) 
  {
    fprintf(stderr, "Couldn't open database!!!! %s\n", sqlite3_errmsg(db)); 
  }

  sqlite3_exec(db, "BEGIN", 0,0,0); 

  double sum_rate = 0; 
  int n_rate = 0; 
  double max_rate = 0;
  double min_rate = 1e9; 

  while (!nuphase_status_gzread(f, &status))
  {
    double t =  status.readout_time + 1e-9 * status.readout_time_ns; 
    double rate = status.global_scalers[SCALER_SLOW]/double(NP_SCALER_TIME(SCALER_SLOW)); 
    sum_rate += rate; 
    n_rate ++; 

    if (rate > max_rate) max_rate = rate; 
    if (rate < min_rate) min_rate = rate; 
    if ( t > last_time + period) 
    {
      last_time = t; 
      char * statement; 
      asprintf(&statement, 
               "INSERT INTO status_summary (unixtime, rate, avg_rate, max_rate, min_rate) VALUES(%f, %f, %f, %f, %f);", 
               t, rate, sum_rate/n_rate, max_rate, min_rate); 
      sqlite3_exec(db,statement,0,0,0); 
      sum_rate = 0; 
      min_rate = 1e9; 
      n_rate = 0;
      max_rate = 0; 
    }
  }

  sqlite3_exec(db, "COMMIT", 0,0,0); 
  sqlite3_close(db); 
  gzclose(f); 
  return 0; 
}




