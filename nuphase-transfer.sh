#! /bin/sh 

export PATH=$PATH:`pwd`/cpp 
export NUPHASE_DATABASE=`pwd`/nuphase-transfer.db 
export NUPHASE_SUM_DATABASE=`pwd`/nuphase-summary.db 
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`pwd`/../libnuphase 

echo "-------  `date ` ------------" >> nuphase-transfer.log; 
echo "-------  `date ` ------------" >> nuphase-transfer.err; 
nohup python/manager.py >> nuphase-transfer.log 2>> nuphase-transfer.err < /dev/null  &

echo "Started monitor program." 

