import webview

class API:
    def show_processing_page(self, source, destination, vmname):
        with open('C:/projects/nomadsky/code/nomadsky-engine/UI/2)processing-page.html', 'r') as f:
            html = f.read()
        
        html = html.replace('{{source}}', source)
        html = html.replace('{{destination}}', destination)
        html = html.replace('{{vmname}}', vmname)
        
        window.load_html(html)
        return True

# Read the form HTML
with open('C:/projects/nomadsky/code/nomadsky-engine/UI/frontend.html', 'r') as f:
    form_html = f.read()

# Create the window
api = API()
window = webview.create_window('VM Migration Tool', html=form_html, js_api=api)
webview.start()
