import webview
from urllib.parse import urlparse, parse_qs

# Global variables to store form data
form_data = {}

def on_navigation(url):
    """Handle custom URL navigation"""
    global form_data
    
    if url.startswith('submit://'):
        # Parse the URL parameters
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Store form data
        form_data['source'] = params.get('source', [''])[0]
        form_data['destination'] = params.get('destination', [''])[0]
        form_data['vmname'] = params.get('vmname', [''])[0]
        
        # Load processing page
        show_processing_page()
        
        return False  # Prevent default navigation

def show_processing_page():
    """Load the processing page with form data"""
    with open('C:/projects/nomadsky/code/nomadsky-engine/UI/2)processing-page.html', 'r') as f:
        html = f.read()
    
    # Replace placeholders
    html = html.replace('{{source}}', form_data.get('source', ''))
    html = html.replace('{{destination}}', form_data.get('destination', ''))
    html = html.replace('{{vmname}}', form_data.get('vmname', ''))
    
    window.load_html(html)

# Read the form HTML
with open('C:/projects/nomadsky/code/nomadsky-engine/UI/frontend.html', 'r') as f:
    form_html = f.read()

# Create window
class Api:
    def navigate(self, source, destination, vmname):
        global form_data
        form_data = {'source': source, 'destination': destination, 'vmname': vmname}
        show_processing_page()

api = Api()
window = webview.create_window('VM Migration Tool', html=form_html, js_api=api)

# Start webview
webview.start()
