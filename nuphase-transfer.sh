#! /bin/sh 

export PATH=$PATH:`pwd`/cpp 
export NUPHASE_DATABASE=`pwd`/nuphase-transfer.db 

echo "-------  `date ` ------------" >> nuphase-transfer.log; 
echo "-------  `date ` ------------" >> nuphase-transfer.err; 
nohup python python/manager.py >> nuphase-transfer.log 2>> nuphase-transfer.err < /dev/null  &

echo "Started monitor program." 
