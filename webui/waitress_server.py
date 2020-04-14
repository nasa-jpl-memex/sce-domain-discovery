from waitress import serve
import run

serve(run.app, host='0.0.0.0', port=5000)
