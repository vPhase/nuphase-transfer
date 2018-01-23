


BINS=cpp/nuphase-event-filter

all: $(BINS) nuphase-transfer.db  nuphase.cfg

nuphase-transfer.db: sqlite/create.sql 
	sqlite3 nuphase-transfer.db < sqlite/create.sql; 
	ln -f nuphase-transfer.db .nuphase-transfer.db.harder_to_accidentally_delete

nuphase.cfg: 
	ln -sf python/cfg.py nuphase.cfg 

cpp/%: cpp/%.cc
	g++ $< -o $@ -L../libnuphase -lnuphase -I../libnuphase  -lz

clean: 
	rm -f $(BINS) 


