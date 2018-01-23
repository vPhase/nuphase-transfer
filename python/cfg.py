###########################################################
#   Configuration for nuphase-transfer
#       This is just a python module that gets imported. Be careful! 
# 
############################################################

#################### MANAGER CONFIG ##################

#Maximum age (in seconds) to conssider a run directory
max_age_to_check_run = 5  * 24 * 3600 

#Minimum age (in seconds) to consdier a run directory
min_age_to_check_run = 0 

# The directory holding the raw data
raw_data_dir = "/home/radio/data/nuphase{detid}/{year}/raw_data/"

years = (2018,) 

detids = (1,) 

sleep_amount = 600 

manager_lockfile = '/tmp/nuphase.manager.lock'

##################### RUN CONFIG ###################


# Number of events to telemeter 
N_best = 100 
N_rf = 75 
N_sw = 25

run_dropbox_north_prefixes = { "header" : "/home/dropboxes/nuphase{detid}/north/hk/SPS_NUPHASE_HEADER", "status" : "/home/dropboxes/nuphase{detid}/north/hk/SPS_NUPHASE_STATUS", "event" : "/home/dropboxes/nuphase{detid}/north/hk/SPS_NUPHASE_EVENT" }
run_dropbox_south_prefix = "/home/dropboxes/nuphase{detid}/south/SPS_NUPHASE_RAW"; 



#################### HK CONFIG ####################

hk_dropbox_south_prefix = "/home/dropboxes/nuphase{detid}/south/SPS_NUPHASE_RAW_hk_" 
hk_dropbox_north_prefix = "/home/dropboxes/nuphase{detid}/north/hk/SPS_NUPHASE_HK_" 
hk_lock_file = '/tmp/nuphase.process_hk.lock'

#################### STARTUP CONFIG ####################

startup_dropbox_south_prefix = "/home/dropboxes/nuphase{detid}/south/SPS_NUPHASE_RAW_startup_" 
startup_dropbox_north_prefix = "/home/dropboxes/nuphase{detid}/north/hk/SPS_NUPHASE_HK_startup_" 
startup_lock_file = '/tmp/nuphase.process_startup.lock'






