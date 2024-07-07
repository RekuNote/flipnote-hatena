from flask import Flask, request, send_from_directory, Response
import os
import logging
import socket
import re

app = Flask(__name__)

ASSET_FOLDER = 'ASSET'  # Update this path to your actual ASSET folder location

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/<path:path>', methods=['GET'])
def proxy(path):
    logger.info(f'[REQ] DSi GET requested {request.url}')
    
    # Handle requests for ds/v2-us and ds/v2-jp
    if path.startswith('ds/v2-us/') or path.startswith('ds/v2-jp/'):
        path = path.replace('ds/v2-us/', 'ds/v2-eu/').replace('ds/v2-jp/', 'ds/v2-eu/')
    
    # Check if the request matches the pattern ds/v2-eu/\d{16}/
    match = re.match(r'ds/v2-eu/\d{16}/', path)
    if match:
        # Redirect to ASSET/ds/v2-eu/user/
        new_path = os.path.join('ds/v2-eu/user/', os.path.basename(path))
        file_path = os.path.join(ASSET_FOLDER, new_path)
    else:
        # Normal path handling
        file_path = os.path.join(ASSET_FOLDER, path)
    
    if os.path.isfile(file_path):
        logger.info(f'[RES] Server responded {file_path}')
        directory, filename = os.path.split(file_path)
        response = send_from_directory(directory, filename)
        logger.info(f'[CODE] Returned Code {response.status_code}')
        return response
    else:
        logger.warning(f'[RES] File not found: {file_path}')
        response = Response("File not found", status=404)
        logger.info(f'[CODE] Returned Code {response.status_code}')
        return response

if __name__ == '__main__':
    local_ip = get_local_ip()
    logger.info(f'Hatena Server proxy running at {local_ip} on Port 8080.')
    logger.info('Running on:')
    logger.info(f'* (0.0.0.0)')
    logger.info(f'* http://127.0.0.1:8080')
    logger.info(f'* http://{local_ip}:8080')
    app.run(host='0.0.0.0', port=8080)

