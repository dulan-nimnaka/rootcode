import os
from receptionist.db import init_db, get_db_path, list_tables
from receptionist.allocator import find_table_for_party

def setup_function():
    # reset DB before each test
    init_db(force=True)

def test_single_fit():
    # T1 and T2 are capacity 4; party of 2 should reserve one
    res = find_table_for_party(2)
    assert res is not None
    assert len(res) >= 1

def test_combination():
    # Reserve two tables by requesting large party
    res = find_table_for_party(8)
    # Expect combinable T2 + T1 or similar to be used
    assert res is not None
    assert sum(t.startswith('T') for t in res) >= 1
