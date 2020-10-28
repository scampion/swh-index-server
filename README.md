Software Heritage SHA1 HTTP indexer
===================================

License : AGPL 

Author: Sebastien Campion sebastien.campion@protonmail.com

The issue:
----------

You need to analyse a source code archive and find if one or several files was already published and indexed by 
Software Heritage. To do that, you will compute the sha1 on each on them and submit it though the SWH API. 

But the SWH API request rate is limited and you will not be able to analyze your entire zip.


The solution:
-------------

You can download the latest SWH dump "The Software Heritage Graph Dataset" (here for example : https://zenodo.org/record/2583978)
and run you own and dedicated HTTP service.

But, it's huge. Indeed, 9 billions files, 20 bytes per sha1 : 180GB  
The simplest and naive solution is to buy an huge memory server. 
The second one, is detailed below.

How to do that: 
---------------

There is no miracle, data doesn't fit in memory so for each request will search in the file. 
(If possible, I recommend an SSD hard drive)

To find the sha1 efficiently we will sort the sha1 file and use binary search algorithm.

To speed up the binary search algorithm on the disk, we can reduce the search space.

We will sample the file in memory and use the same approach. 


Step by step: 
-------------


1. From Zenodo, download the sql_content.csv.gz file 

	https://zenodo.org/record/2583978/files/sql_content.csv.gz?download=1

2. Build the SHA1 file index

We will create a raw list of binary sha1 in a single file named "data.bin" with the following command:

```
zcat sql_content.csv.gz| python3 csv2bin.py
```

3. Sort it with the bsort software : https://github.com/pelotoncycle/bsort

It take 45 minutes on my server
```
bsort -k 20 -r 20 data.bin
```

4. Run the http server 
```
python3 app.py
```

5. Test it
```
curl http://localhost:5000/000033c14ccbd75a2deaa0d2eaa991975a3df12d
```

The http response is empty, the result is provided by the HTTP status code `200` OK, we found it or `404` not found.


Parameter: 
----------

By default, the server will use 80% of you memory to sample the sha1 file.
To reduce the memory indexation time, you can reduce this size with the environment variable `INDEX_MEMORY_SIZE`  
```
    export INDEX_MEMORY_SIZE=2000
```


Container usages:
-----------------

You can build a container with the following command: 
```
docker build -t swhind . 
```


And run the server like that:
```
docker run -p 5000:5000  -e PREINDEX_MEMORY_SIZE=1024 -v `pwd`/data.bin:/app/data.bin:ro swhind
```

It should be possible to sort the file with the container like that (not tested):
```
docker run -v `pwd`/data.bin:/app/data.bin swhind ./bsort-master/bsort -k 20 -r 20 /app/data.bin
```


Open discussion: 
----------------
45 minutes to sort a file, of course, it's not perfect if you want a real time service but a [lambda architecture](https://en.wikipedia.org/wiki/Lambda_architecture) will 
be more appropriate in that case.
