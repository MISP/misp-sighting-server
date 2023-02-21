#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    ReST server for misp sighting server
#
#    Copyright (C) 2017-2023 Alexandre Dulaunoy
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
import uuid
import time

app = Flask(__name__)
api = Api(app)

cfg = configparser.ConfigParser()
cfg.read('../cfg/server.cfg')

ardb_port = cfg.get('server', 'ardb_port')
api_key = cfg.get('server', 'api_key')
default_source = cfg.get('server', 'default_source')
default_org_uuid = cfg.get('server', 'default_org_uuid')
journal = cfg.get('server', 'journal')
version = '0.2'
r = redis.StrictRedis(port=ardb_port, db=0, decode_responses=True, charset='utf-8')


def _validate_uuid(value=None):
    if uuid is None:
        return False
    try:
        _val = uuid.UUID(value)
    except ValueError:
        return False
    return True


def Init():
    d = datetime.datetime.utcnow()
    d_with_timezone = d.replace(tzinfo=pytz.UTC)
    r.set('misp-sighting-server:version', version)
    r.set('misp-sighting-server:startup', d_with_timezone.isoformat())
    r.set('misp-sighting-server:get', 0)
    r.set('misp-sighting-server:set', 0)


Init()


def TestBackend(version=version):
    version = r.get('misp-sighting-server:version')
    startup = r.get('misp-sighting-server:startup')
    get = r.get('misp-sighting-server:get')
    set_stat = r.get('misp-sighting-server:set')

    return (version, startup, get, set_stat)


def UpdateJournal(value=None):
    if value is None:
        return False
    now = datetime.datetime.utcnow()
    year_month_day_format = '%Y%m%d'
    log_day = now.strftime(year_month_day_format)
    ns = time.time_ns()
    r.zadd(log_day, {value: ns})
    return True


def UpdatePayload(value=None, when=None, new_payload=None):
    if when is None or new_payload is None or value is None:
        return False
    ret = r.hset(value, when, new_payload)
    return True


class GetStatus(Resource):
    def get(self):
        status = TestBackend()
        return {
            'version': status[0],
            'startup': status[1],
            'get': status[2],
            'set': status[3],
        }


class AddSighting(Resource):
    def put(self):
        if request.form['value'] is None:
            return False
        if not (request.headers.get('X-Api-Key') == api_key):
            print(request.headers)
            return False
        if not request.form.get('epoch'):
            when = int(time.time())
        else:
            when = request.form['epoch']
        if not request.form.get('source'):
            source = default_source
        else:
            source = request.form['source']
        if not request.form.get('org_uuid'):
            org_uuid = default_org_uuid
        else:
            org_uuid = request.form['org_uuid']
        if not _validate_uuid(org_uuid):
            return {'error': 'org_uuid is not a valid UUID'}

        request_type = 0
        if request.form.get('type'):
            request_type = int(request.form['type'])
        payload = f'{source}:{request_type}:{org_uuid}'
        if r.hset(request.form['value'], when, payload):
            if journal:
                UpdateJournal(value=request.form['value'])
            r.incr('misp-sighting-server:set')
            return True
        else:
            existing_payload = r.hget(request.form['value'], when)
            updated_payload = f'{existing_payload}\n{payload}'
            if UpdatePayload(
                value=request.form['value'], when=when, new_payload=updated_payload
            ):
                UpdateJournal(value=request.form['value'])
                r.incr('misp-sighting-server:set')
                return True


class GetSighting(Resource):
    def get(self):
        if request.form['value'] is None:
            return False
        request_type = 0
        if request.form.get('type'):
            request_type = int(request.form['type'])
        r.incr('misp-sighting-server:get')
        return r.hgetall(request.form['value'])


api.add_resource(GetStatus, '/')
api.add_resource(AddSighting, '/add')
api.add_resource(GetSighting, '/get')

if __name__ == '__main__':
    Init()
    app.run(debug=True)
