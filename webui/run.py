from app import app



# Run Server
app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, processes=8)
