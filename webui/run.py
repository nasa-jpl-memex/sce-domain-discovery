"""Run the flask server"""
from app import APP

# Run Server
APP.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
