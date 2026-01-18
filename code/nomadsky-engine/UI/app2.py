import webview

class Api:
    def __init__(self):
        self.window = None
    
    def show_processing_page(self, source, destination, vmname):
        # Load HTML from file
        with open('C:/projects/nomadsky/code/nomadsky-engine/UI/2)processing-page.html', 'r') as f:
            processing_html = f.read()
        
        # Replace placeholders with actual values
        processing_html = processing_html.replace('{{source}}', source)
        processing_html = processing_html.replace('{{destination}}', destination)
        processing_html = processing_html.replace('{{vmname}}', vmname)
        
        self.window.load_html(processing_html)

# Load form HTML from file
with open('C:/projects/nomadsky/code/nomadsky-engine/UI/frontend.html', 'r') as f:
    form_html = f.read()

# Create API instance
api = Api()

# Create window with API
window = webview.create_window('VM Migration Tool', html=form_html, js_api=api, width=500, height=600)

# Set window reference in API
api.window = window

# Start webview
webview.start()
