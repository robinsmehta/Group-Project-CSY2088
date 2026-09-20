# run.py — Application Entry Point
#
# Starts the Flask server by calling create_app() from app/__init__.py.
#
# Usage:
#   python run.py

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
