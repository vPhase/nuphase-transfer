


BINS=cpp/nuphase-event-filter

all: $(BINS) nuphase-transfer.db  python/cfg.py

nuphase-transfer.db: sqlite/create.sql 
	sqlite3 nuphase-transfer.db < sqlite/create.sql; 
	ln -f nuphase-transfer.db .nuphase-transfer.db.harder_to_accidentally_delete

python/cfg.py: 
	ln -s ../nuphase.cfg python/cfg.py 

cpp/%: cpp/%.cc
	g++ $< -o $@ -L../libnuphase -lnuphase -I../libnuphase  -lz

clean: 
	rm -f $(BINS) 


