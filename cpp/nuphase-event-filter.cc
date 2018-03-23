
/** This program takes in an event and header file, and will produced a
 * filtered output event file, which will contain the specified number of
 * random events, sw trigger events, and calibration  RF events 
 *
 * right now, it's very dumb and will require holding all events in memory. This could be fixed if it's a problem. 
 */ 

#include "nuphase.h" 
#include <time.h> 
#include <algorithm> 
#include <stdlib.h> 
#include <stdio.h> 
#include <vector> 


static bool sort_events (const nuphase_event_t & a, const nuphase_event_t & b)
{
  return a.event_number < b.event_number; 
}

int main(int nargs, char ** args) 
{
  if (nargs < 7)
  {
    fprintf(stderr,"Usage: nuphase-event_filter event_file.event.gz header_file.header.gz output.filtered.gz N_RANDOM_CALIB N_RANDOM_RF N_RANDOM_SW\n"); 
    return 1; 
  }

  gzFile in_ev_file = gzopen(args[1],"r"); 
  gzFile in_hd_file = gzopen(args[2],"r"); 
  gzFile out_ev_file = gzopen(args[3],"wx9");   

  int n_calib = atoi(args[4]); 
  int n_rf = atoi(args[5]); 
  int n_sw = atoi(args[6]); 

  std::vector<nuphase_event_t> rf_events; 
  std::vector<nuphase_event_t> sw_events; 
  std::vector<nuphase_event_t> calib_events; 

  nuphase_header_t hd; 
  nuphase_event_t ev; 

  while (!nuphase_header_gzread(in_hd_file, &hd))
  {
    if (nuphase_event_gzread(in_ev_file, &ev))
    {
      fprintf(stderr,"Size mismatch between headers and events. Giving up.\n"); 
      return 12; 
    }

    if (hd.trig_type == NP_TRIG_RF)
    {
      if(hd.gate_flag) 
      {
        calib_events.push_back(ev);
      }
      else
      {
        rf_events.push_back(ev);
      }
    }
    else
    {
      sw_events.push_back(ev);
    }
  }

  gzclose(in_ev_file); 
  gzclose(in_hd_file); 


  //seed rng
  std::srand(time(0)); 

  //shuffle the events 
  std::random_shuffle(sw_events.begin(), sw_events.end()); 
  std::random_shuffle(rf_events.begin(), rf_events.end()); 
  std::random_shuffle(calib_events.begin(), calib_events.end()); 

  //truncate to the right number
  if (sw_events.size() > n_sw) sw_events.resize(n_sw); 
  if (calib_events.size() > n_calib) calib_events.resize(n_calib); 
  if (rf_events.size() > n_rf) rf_events.resize(n_rf); 

  //combine into one vector
  std::vector<nuphase_event_t> to_write; 
  to_write.insert(to_write.end(), sw_events.begin(), sw_events.end()); 
  to_write.insert(to_write.end(), rf_events.begin(), rf_events.end()); 
  to_write.insert(to_write.end(), calib_events.begin(), calib_events.end()); 

  std::sort(to_write.begin(), to_write.end(), sort_events); 

  //write them out, calib, rf then sw 
  for (unsigned i = 0; i < to_write.size(); i++) nuphase_event_gzwrite(out_ev_file, &to_write[i]); 

  gzclose(out_ev_file); 
  return 0; 

} 


