


BINS=cpp/nuphase-event-filter cpp/summarize-status cpp/summarize-hk cpp/make-monitor-plot

all: $(BINS) nuphase-transfer.db  python/cfg.py nuphase-summary.db 

nuphase-transfer.db: sqlite/create.sql 
	-sqlite3 nuphase-transfer.db < sqlite/create.sql; 
	ln -f nuphase-transfer.db .nuphase-transfer.db.harder_to_accidentally_delete

nuphase-summary.db: sqlite/create_sum.sql 
	-sqlite3 nuphase-summary.db < sqlite/create_sum.sql; 
	ln -f nuphase-summary.db .nuphase-summary.db.harder_to_accidentally_delete



python/cfg.py: 
	ln -s ../nuphase-transfer.cfg python/cfg.py 

cpp/%: cpp/%.cc
	g++ $< -o $@ -g -L../libnuphase -lnuphase -I../libnuphase  -lz -lsqlite3   `root-config --cflags` `root-config --ldflags` `root-config --libs`  

clean: 
	rm -f $(BINS) 


