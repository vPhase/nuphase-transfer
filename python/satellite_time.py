import time

sidereal_day = 23 * 60 * 60 + 60 * 56 + 4.0916 


reference_up = 1517885100 # 2:45 am, feb 6, 2018. Actually came up at 2:43, but add a bit of padding

def secs_since_dscs_up(): 
  now = time.time() 
  since = now - reference_up; 
  ndays = since / sidereal_day; 
  return (ndays - int(ndays)) * 24 * 3600; 




