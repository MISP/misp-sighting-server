# misp-sighting-server

MISP sighting server is a fast sighting server to store and look-up sightings on attributes (network indicators, file hashes, system indicators) in a
space efficient way.

## Features

- Simple ReST API to get or set sighting
- TODO - fast DNS server to allow lookup of sighting via DNS queries
- TODO - fast import of sighting via pub-sub channel like ZMQ

## Back-end database

MISP sighting server rely on [kvrocks](https://github.com/apache/incubator-kvrocks/) using [RocksDB](https://github.com/facebook/rocksdb) at the current stage. 

The back-end database might change following the evolution of the requirements or capabilities but the objective is to keep a compatibility layer to ensure use of the sighting database have the same
API on the long-term.

# Install

~~~
git submodule init
git submodule update
cd back-end/kvrocks
./x.py build
cd ../..
pip3 install -r REQUIREMENTS
~~~

# Starting the servers

## Starting the back-end

~~~
cd back-end/kvrocks
./build/kvrocks -c kvrocks.conf&
~~~

## Starting the ReST API server

~~~
cd cfg
cp server.cfg.sample server.cfg
cd ..
cd ./bin/
python3 sighting-server.py
~~~

# Testing

## Add a sighting

|field|description|
|:---|:---|
|`value`|Value of the sighting or UUID reference to the sighting|
|`type`|Type of sighting (default is `0`)|
|`org_uuid`|UUID of the organisation recording the sighting|

~~~
curl --header 'X-API-Key: afdef83f9cc7c87b801c36e4af632ef06af2f2ef' -X PUT  http://127.0.0.1:5000/add -d "value=127.0.0.1&type=0&org_uuid=0acdaad8-b305-482f-a904-78330640636b"  -d "source=honeypot"
~~~

## Get the sighting of a value

~~~
curl -X GET http://127.0.0.1:5000/get -d "value=127.0.0.1"
{
    "1676925347": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925348": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925349": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925350": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925351": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925352": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925353": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925354": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925355": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925356": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925358": "honeypot:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925618": "blackhole:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925619": "blackhole:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925623": "siem:0:0acdaad8-b305-482f-a904-78330640636b",
    "1676925627": "edr_234:0:0acdaad8-b305-482f-a904-78330640636b"
}
~~~

