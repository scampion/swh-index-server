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

You can download the latest SWH dump "[The Software Heritage Graph Dataset](https://zenodo.org/record/2583978)"
and run you own and dedicated HTTP service.

But, it's huge. Indeed, 9 billions files, 20 bytes per sha1 : 180GB  
The simplest and naive solution is to buy an huge memory server. 
The second one, is detailed below.

How to do that: 
---------------

There is no miracle, data doesn't fit in memory so for each request we will search in the file. 
(If possible, I recommend an SSD hard drive)

To find the sha1 efficiently we will sort the sha1 file and use binary search algorithm.

To speed up the binary search algorithm on the disk, we can reduce the search space.

We will sample the file in memory and use the same approach. 


Here is an example: 

 Memory sampling                                             Sorted SHA1 file
+----------------------------------------+                   +----------------------------------------+
|495fe31da0d856520fbffa39757d870aa138f235+----------+        |0926712bd5ad41e9cd760b16b81c58c98bcc7df1|
|7bfc1985bb2b90ebbb48091f7388962e38033a8e|------+   |        |1049c1dc212502dabbc3f5206a650ed416cf4f2a|
|c6917521f775b154a177d1d36999152f221e009d|---+  |   |        |309a9cfbadbebb58b43d1d45fa0a290f2303ea1c|
|f06d70b6063150edeaf7acf146a954a0257448dd+-+ |  |   |        |3eb661cc6fe203d2808f25754f822cbfd3262bae|
+----------------------------------------+ | |  |   +-------->495fe31da0d856520fbffa39757d870aa138f235|
                                           | |  |            |4c7a0bb79b6e30ad11b9da6041945b3accb087d5|
                                           | |  |            |5950680f43da283f82af411164be609edf9b847e|
                                           | |  |            |59dc4e9aead49e5b4837b75be83ea6737350c69e|
                                           | |  |            |72b390514d1e7b7273989c4362dc0cda2f644597|
                                           | |  +------------>7bfc1985bb2b90ebbb48091f7388962e38033a8e|
                                           | |               |865070c9b8f82e014149f3ff15b2065b165fd407|
                                           | |               |bbc9e5b3022d7b220e557d4f8e970f51f57aba44|
                                           | |               |be177fe5bdc9d60a7e882d5b1203f1ba7113390f|
                                           | |               |c2aa971b9a0fe2928b1e189e5204c85accd81915|
                                           | +--------------->c6917521f775b154a177d1d36999152f221e009d|
                                           |                 |c98bc56e3a199516932d22c19dead67905960463|
                                           |                 |dc9d6333f297aa4d7e5d6a622adc2182846b8b1f|
                                           |                 |df79de8c1b84ebf369280c8bc3a9c77fb733ed16|
                                           |                 |e652e8387dc06c399d76c995216ac808016d65c7|
                                           +----------------->f06d70b6063150edeaf7acf146a954a0257448dd|
                                                             +----------------------------------------+



Step by step: 
-------------


1. From Zenodo, download the [sql_content.csv.gz file](https://zenodo.org/record/2583978/files/sql_content.csv.gz?download=1)

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
