from receptionist import init_db
import os
import json
from flask import Flask
import app as app_module

def test_version_list():
    # call the endpoint function directly
    client = app_module.app.test_client()
    res = client.get('/api/version')
    assert res.status_code == 200
    j = res.get_json()
    assert 'versions' in j
    assert 'v1.0' in j['versions']
    assert 'v1.1' in j['versions']
