import webview
from urllib.parse import urlparse, parse_qs
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import threading

# Flask setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Global variables to store form data
form_data = {}

# Flask API endpoint to run scripts
@app.route('/api/run-script', methods=['POST'])

@app.route("/api/ping", methods=["GET"])
def ping():
    return {"pong": True}, 200

def run_script():
    data = request.json
    script_name = data.get('script')
    source = data.get('source')
    destination = data.get('destination')
    vmname = data.get('vmname')
    
    # Path to your scripts
    script_path = f'C:/projects/nomadsky/code/nomadsky-engine/scripts/{script_name}'
    
    try:
        result = subprocess.run(
            ['python', script_path, source, destination, vmname],
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({
            'success': True,
            'output': result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            'success': False,
            'error': e.stderr
        }), 500

def run_flask():
    """Run Flask in background thread"""
    app.run(port=5000, debug=False, use_reloader=False)

def show_processing_page():
    """Load the processing page with form data"""
    with open('C:/projects/nomadsky/code/nomadsky-engine/UI/2)processing-page.html', 'r') as f:
        html = f.read()
    
    # Replace placeholders
    html = html.replace('{{source}}', form_data.get('source', ''))
    html = html.replace('{{destination}}', form_data.get('destination', ''))
    html = html.replace('{{vmname}}', form_data.get('vmname', ''))
    
    window.load_html(html)

# Pywebview API
class Api:
    def navigate(self, source, destination, vmname):
        global form_data
        form_data = {'source': source, 'destination': destination, 'vmname': vmname}
        
        import threading
        def load():
            import time
            time.sleep(0.1)
            show_processing_page()
        threading.Thread(target=load, daemon=True).start()

# Read the form HTML
with open('C:/projects/nomadsky/code/nomadsky-engine/UI/frontend.html', 'r') as f:
    form_html = f.read()

# Start Flask in background thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Create pywebview window
api = Api()
window = webview.create_window('VM Migration Tool', html=form_html, js_api=api)

# Start webview (this blocks until window closes)
webview.start()
