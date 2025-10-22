
from flask import Flask, request, jsonify, send_file
from receptionist import get_greeting, parse_party_size, init_db, find_table_for_party, plan_path, avoid_obstacle
from receptionist.db import list_tables, init_db as _init_db

app = Flask(__name__)

init_db()

@app.route('/')
def index():
	return send_file('index.html')

@app.route('/api/greeting')
def api_greeting():
	g = get_greeting()
	return jsonify({'greeting': g})


# Compatibility endpoints for the existing UI
TABLE_COORDS = {
	'T1': (3, 3),
	'T2': (5, 3),
	'T3_A': (9, 4),
	'T3_B': (9, 6),
	'T4': (4, 6),
}


@app.route('/api/greet')
def api_greet():
	msg = get_greeting()
	return jsonify({'message': msg})


@app.route('/api/handle_request', methods=['POST'])
def api_handle_request():
	data = request.get_json() or {}
	text = data.get('text', '')
	party = parse_party_size(text)
	if party is None:
		return jsonify({'success': False, 'message': 'Sorry, I did not understand the party size.'})
	tables = find_table_for_party(int(party))
	if not tables:
		return jsonify({'success': False, 'message': 'No table available for that party size.'})
	# choose first table's coords as target
	target_table = tables[0]
	coords = TABLE_COORDS.get(target_table, (7,7))
	return jsonify({'success': True, 'message': f'Got it, a table for {party}. Please follow me.', 'target_coords': {'x': coords[0], 'y': coords[1]}})


@app.route('/api/get_path', methods=['POST'])
def api_get_path():
	data = request.get_json() or {}
	x = int(data.get('x', 5))
	y = int(data.get('y', 5))
	# robot start is (1,1)
	path = plan_path((1,1), (x,y), obstacles=[])
	if not path:
		return jsonify({'success': False, 'message': 'No path found.'})
	return jsonify({'success': True, 'path': path})


@app.route('/api/reset_sim', methods=['POST'])
def api_reset_sim():
	# reset DB
	_init_db(force=True)
	return jsonify({'success': True, 'message': 'Simulation reset.'})


@app.route('/api/get_tables')
def api_get_tables():
	# return mapped table data with coords used by UI
	rows = list(list_tables())
	out = []
	for r in rows:
		tid = r['table_id']
		x,y = TABLE_COORDS.get(tid, (0,0))
		out.append({'name': tid, 'status': r['status'], 'x_coord': x, 'y_coord': y})
	return jsonify(out)

@app.route('/api/parse_party', methods=['POST'])
def api_parse_party():
	data = request.get_json() or {}
	text = data.get('text', '')
	party = parse_party_size(text)
	return jsonify({'party_size': party})

@app.route('/api/find_table', methods=['POST'])
def api_find_table():
	data = request.get_json() or {}
	size = data.get('size')
	if size is None:
		return jsonify({'error': 'size required'}), 400
	tables = find_table_for_party(int(size))
	if tables is None:
		return jsonify({'available': False, 'tables': []})
	return jsonify({'available': True, 'tables': tables})

@app.route('/api/plan_path', methods=['POST'])
def api_plan_path():
	data = request.get_json() or {}
	start = tuple(data.get('start', (0,0)))
	goal = tuple(data.get('goal', (5,5)))
	obstacles = [tuple(o) for o in data.get('obstacles', [])]
	path = plan_path(start, goal, obstacles)
	return jsonify({'path': path})

@app.route('/api/avoid', methods=['POST'])
def api_avoid():
	data = request.get_json() or {}
	path = [tuple(p) for p in data.get('path', [])]
	obs = tuple(data.get('obstacle'))
	new = avoid_obstacle(path, obs)
	return jsonify({'path': new})

if __name__ == '__main__':
	app.run(debug=True, port=5000)
