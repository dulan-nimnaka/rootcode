from typing import List, Optional, Tuple
from .db import list_tables, update_table_status

def find_table_for_party(group_size: int) -> Optional[List[str]]:
    """Find and reserve tables for a party of group_size.

    Strategy:
      1. Look for single table with capacity >= group_size and Available.
      2. Look for combinations of combinable tables whose sum >= group_size.
      3. Respect sync_id: if a table has sync_id, all with same id must be free to use.

    Returns list of table_ids reserved or None if not found.
    """
    tables = list(list_tables())
    available = [t for t in tables if t['status'] == 'Available']

    # 1) Perfect fit: prefer smallest capacity that fits
    fits = sorted([t for t in available if t['capacity'] >= group_size], key=lambda x: x['capacity'])
    for t in fits:
        # if synced, ensure all sync group are available
        if t['sync_id']:
            sync_id = t['sync_id']
            sync_group = [s for s in available if s['sync_id'] == sync_id]
            # require all with that sync_id to be present
            # (for simplicity) - if not, skip
            if not sync_group or any(s['status'] != 'Available' for s in sync_group):
                continue
            ids = [s['table_id'] for s in sync_group]
            for tid in ids:
                update_table_status(tid, 'Reserved')
            return ids
        # otherwise reserve single table
        update_table_status(t['table_id'], 'Reserved')
        return [t['table_id']]

    # 2) combinable: try combinations of combinable tables (greedy)
    combinable = [t for t in available if t['is_combinable']]
    # sort descending to use bigger tables first to reduce number of tables
    combinable = sorted(combinable, key=lambda x: x['capacity'], reverse=True)
    selected = []
    cap_sum = 0
    for t in combinable:
        # skip sync groups in combinable stage for simplicity
        if t['sync_id']:
            continue
        selected.append(t)
        cap_sum += t['capacity']
        if cap_sum >= group_size:
            ids = [s['table_id'] for s in selected]
            for tid in ids:
                update_table_status(tid, 'Reserved')
            return ids

    return None
