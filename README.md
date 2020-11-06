# search-engine-with-DHT-based-inverted-index-
search engine with DHT based inverted index

search engine with DHT based inverted index is a search engine based BBC news article crawled for the year 2020. the DHT 
is implemented with CHORD archietecture. 

## requirements
python 3

### run single node instance:
python chordImpl.py node_port_number 
> python chordImpl.py 3000 

### node join the chord ring in port 3000:
python chordImpl.py port_number node_port_number 
> python chordImpl.py 4000 3000 

use different port to add more nodes to the chord ring

### to run the web interface for search engine 
python web_interface.py ip_address port_number 
> python web_interface.py '127.0.0.1' 3000 
