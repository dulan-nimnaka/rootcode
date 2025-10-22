from datetime import datetime
from receptionist.greeting import get_greeting

def test_morning():
    dt = datetime(2025,1,1,8,0)
    assert get_greeting(dt) == 'Good morning.'

def test_afternoon():
    dt = datetime(2025,1,1,13,0)
    assert get_greeting(dt) == 'Good afternoon.'

def test_evening():
    dt = datetime(2025,1,1,20,0)
    assert get_greeting(dt) == 'Good evening.'
