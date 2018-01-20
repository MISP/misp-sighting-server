#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    ReST server for misp sighting server
#
#    Copyright (C) 2017 Alexandre Dulaunoy
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import Flask, request
from flask_restful import Resource, Api
import redis
import datetime
import pytz
import time
import configparser

app = Flask(__name__)
api = Api(app)

cfg = configparser.ConfigParser()
cfg.read('../cfg/server.cfg')

ardb_port = cfg.get('server', 'ardb_port')
ardb_socket = cfg.get('server', 'ardb_socket')
api_key = cfg.get('server', 'api_key')
default_source = cfg.get('server', 'default_source')

version = '0.1'
r = [
    redis.StrictRedis(unix_socket_path=ardb_socket, db=0, decode_responses=True,
                      charset='utf-8'),
    redis.StrictRedis(unix_socket_path=ardb_socket, db=1, decode_responses=True,
                      charset='utf-8')
]

    
def Init():
    d = datetime.datetime.utcnow()
    d_with_timezone = d.replace(tzinfo=pytz.UTC)
    for i in range(0, 1):
        r[i].set('misp-sighting-server:version', version)
        r[i].set('misp-sighting-server:startup', d_with_timezone.isoformat())

def TestBackend(version=version):
    version = r.get('misp-sighting-server:version')
    startup = r.get('misp-sighting-server:startup')
    return (version, startup)


class GetStatus(Resource):
    def get(self):
        status = TestBackend()
        return {'version': status[0], 'startup': status[1]}

class AddSighting(Resource):
    def put(self):
        if request.form['value'] is None:
            return False
        if not (request.headers.get('X-Api-Key') == api_key):
            print (request.headers)
            return False
        if not request.form.get('epoch'):
            when = int(time.time())
        else:
            when = request.form['epoch']
        if not request.form.get('source'):
            source = default_source
        else:
            source = request.form['source']
        request_type = 0
        if request.form.get('type'):
            request_type = int(request.form['type'])
        if r[request_type].hset(request.form['value'], when,
                  source):
            return True
        else:
            return False

class GetSighting(Resource):
    def get(self):
        if request.form['value'] is None:
            return False
        request_type = 0
        if request.form.get('type'):
            request_type = int(request.form['type'])
        return r[request_type].hgetall(request.form['value'])

api.add_resource(GetStatus, '/')
api.add_resource(AddSighting, '/add')
api.add_resource(GetSighting, '/get')

if __name__ == '__main__':
    Init()
    app.run(debug=True)
