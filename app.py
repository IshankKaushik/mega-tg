import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

# This tiny server responds to Koyeb's health checks
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    # Koyeb uses port 8000 by default, but we check the environment variable just in case
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    # Start the web server in the background
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # Now run your actual bot script
    print("Starting bot.py...")
    subprocess.run(["python", "bot.py"])
