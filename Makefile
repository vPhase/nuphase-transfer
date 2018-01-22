


BINS=cpp/nuphase-event-filter

all: $(BINS) 

nuphase-transfer.db: 
	sqlite3 nuphase-transfer.db < sqlite/create.sql; 

cpp/%: cpp/%.cc
	g++ $< -o $@ -L../libnuphase -lnuphase -I../libnuphase  -lz

clean: 
	rm -f $(BINS) 


