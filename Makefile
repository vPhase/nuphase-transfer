


BINS=cpp/nuphase-event-filter

all: $(BINS) 

cpp/%: cpp/%.cc
	g++ $< -o $@ -L../libnuphase -lnuphase -I../libnuphase  -lz

clean: 
	rm -f $(BINS) 


