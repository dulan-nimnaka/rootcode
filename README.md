Receptionist Robot Simulator
=================================

This repository contains a simple, local simulation of a robot receptionist's core features: contextual greetings, basic NLP to parse party size, table allocation with combinable tables and sync constraints, and a grid-based path planner to guide guests.

What's included
- `app.py` - Flask application exposing JSON endpoints used by the UI.
- `index.html` - Front-end simulator that interacts with the Flask API.
- `receptionist/` - Core modules: greeting, nlp, db, allocator, navigation, speech (stubs).
- `requirements.txt` - Python dependencies.
- `tests/` - Pytest unit tests for greeting and allocator.

Run locally

1. Create a virtual environment and install deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the server:

```bash
python app.py
```

3. Open `http://127.0.0.1:5000/` in your browser to use the UI.

Run tests

```bash
pytest -q
```

Notes
- This is a simulation and intentionally avoids cloud STT/TTS and heavy CV models. Replace modules under `receptionist/` with production-grade services to integrate into a real robot.
# rootcode