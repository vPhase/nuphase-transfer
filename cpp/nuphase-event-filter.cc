
/** This program takes in an event and header file, and will produced a
 * filtered output event file, which will contain the specified number of
 * random events, sw trigger events, and best RF events 
 *
 * right now, it's very dumb and will require holding all events in memory. This could be fixed if it's a problem. 
 */ 

#include "nuphase.h" 
#include <time.h> 
#include <random> 
#include <algorithm> 
#include <stdlib.h> 
#include <stdio.h> 
#include <vector> 


static bool compare_headers (const std::pair<nuphase_header_t, nuphase_event_t> & a, const std::pair<nuphase_header_t, nuphase_event_t> & b)
{
  
  uint32_t max_a = 0; 
  uint32_t max_b = 0; 

  for ( int i = 0; i < NP_NUM_BEAMS; i++)
  {
    if (a.first.triggered_beams & (1 << i) && a.first.beam_power[i] > max_a) max_a = a.first.beam_power[i]; 
    if (b.first.triggered_beams & (1 << i) && b.first.beam_power[i] > max_a) max_b = b.first.beam_power[i]; 
  }
  return max_a > max_b; 
}

int main(int nargs, char ** args) 
{
  if (nargs < 7)
  {
    fprintf(stderr,"Usage: nuphase-event_filter event_file.event.gz header_file.header.gz output.event.gz N_BEST N_RANDOM_RF N_RANDOM_SW\n"); 
    return 1; 
  }

  gzFile in_ev_file = gzopen(args[1],"r"); 
  gzFile in_hd_file = gzopen(args[2],"r"); 
  gzFile out_ev_file = gzopen(args[3],"wx9");   

  int n_best = atoi(args[4]); 
  int n_random = atoi(args[5]); 
  int n_sw = atoi(args[6]); 

  std::vector<std::pair<nuphase_header_t, nuphase_event_t> > rf_events; 
  std::vector<std::pair<nuphase_header_t, nuphase_event_t> > sw_events; 

  nuphase_header_t hd; 
  nuphase_event_t ev; 

  while (nuphase_header_gzread(in_hd_file, &hd))
  {
    if (! nuphase_event_gzread(in_ev_file, &ev))
    {
      fprintf(stderr,"Size mismatch between headers and events. Giving up.\n"); 
      return 12; 
    }

    if (hd.trig_type == NP_TRIG_RF)
    {
      rf_events.push_back(std::pair<nuphase_header_t, nuphase_event_t>(hd,ev));
    }
    else
    {
      sw_events.push_back(std::pair<nuphase_header_t, nuphase_event_t>(hd,ev));
    }
  }

  gzclose(in_ev_file); 
  gzclose(in_hd_file); 

  std::sort(rf_events.begin(), rf_events.end(), compare_headers); 
  //write out the n best (if they exist) 
  for (int i = 0; i < std::min(n_best,(int)rf_events.size()); i++)
  {
    nuphase_event_gzwrite(out_ev_file, &rf_events[i].second);
  }


  //seed rng
  std::srand(time(0)); 

  //shuffle the rest: 
  if (n_random && rf_events.size() > n_best)
  {
    std::random_shuffle(rf_events.begin() + n_best, rf_events.end());
    for (int i = 0; i < std::min(n_random, (int) rf_events.size() - n_best); i++)
    {
      nuphase_event_gzwrite(out_ev_file, &rf_events[n_best+i].second);
    }
  }

  if (n_sw && sw_events.size())
  {
    std::random_shuffle(sw_events.begin(), sw_events.end()); 
    for (int i = 0; i < std::min(n_sw, (int) sw_events.size()); i++)
    {
      nuphase_event_gzwrite(out_ev_file, &sw_events[i].second); 
    }
  }

  gzclose(out_ev_file); 
} 


