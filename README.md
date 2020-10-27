Sofware Heritage SHA1 HTTP indexer

1. From Zenodo, download the sql_content.csv.gz file 

	https://zenodo.org/record/2583978/files/sql_content.csv.gz?download=1

2. Build the SHA1 file index 
	
	zcat sql_content.csv.gz| python3 csv2bin.py

3. Sort it with bsort : https://github.com/pelotoncycle/bsort

	bsort -k 20 -r 20 data.bin


Dev

export PREINDEX_MEMORY_SIZE=1048576



