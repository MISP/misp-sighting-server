# misp-sighting-server

MISP sighting server is a fast sighting server to store and look-up sightings on attributes (network indicators, file hashes, system indicators) in a
space efficient way.

## Features

- Simple ReST API to get or set sighting
- TODO - fast DNS server to allow lookup of sighting via DNS queries
- TODO - fast import of sighting via pub-sub channel like ZMQ

## Back-end database

MISP sighting server rely on a [ardb](https://github.com/yinqiwen/ardb) using [RocksDB](https://github.com/facebook/rocksdb) at the current stage. The back-end database might
change following the evolution of the requirements or capabilities but the objective is to keep a compatibility layer to ensure use of the sighting database have the same
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

~~~
curl --header 'X-API-Key: afdef83f9cc7c87b801c36e4af632ef06af2f2ef' -X PUT  http://127.0.0.1:5000/add -d "value=127.0.0.1"  -d "source=honeypot"
~~~

## Get a sighting

~~~
curl -X GET http://127.0.0.1:5000/get -d "value=127.0.0.1"
{
    "1514737886": "honeypot",
    "1514736878": "unknown",
    "1514737898": "honeypot",
    "1514737866": "honeypot",
    "1514750757": "honeypot",
    "1514736844": "unknown",
    "1514737114": "blackhole",
    "1514750755": "honeypot",
    "1514750799": "honeypot",
    "1514736877": "unknown",
    "1514736840": "honeypot",
    "1514737641": "honeypot",
    "1514750760": "honeypot",
    "1514737028": "unknown",
    "1514736904": "unknown",
    "1514737110": "blackhole",
    "1514737219": "honeypot",
    "1514737900": "honeypot",
    "1514737901": "honeypot",
    "1514737216": "honeypot",
    "1514737102": "honeypot",
    "1514736900": "honeypot",
    "1514735898": "honeypot",
    "1514736727": "honeypot",
    "1514737113": "blackhole",
    "1514737841": "honeypot",
    "1514737111": "blackhole",
    "1514750756": "honeypot",
    "1514736848": "honeypot",
    "1514737709": "honeypot",
    "1514737115": "blackhole",
    "1514737680": "honeypot",
    "1514735899": "honeypot",
    "1514737117": "blackhole",
    "1514737109": "blackhole"
}
~~~

