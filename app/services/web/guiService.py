import base64
import os
import http.server
import json
import time
import threading
import mimetypes
import queue
import sys
from io import BytesIO
from multiprocessing import Queue, Process
from http import HTTPStatus
from PIL import Image

from services.common.system_store import SystemStore

class ImageStreamer(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.data_queue: Queue = server.data_queue
        self.stream_event = threading.Event()
        self.stream_thread = None
        super().__init__(request, client_address, server)

    def do_GET(self):
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.serve_html_file('index.html')
        elif self.path == '/stream':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            self.stream_frames()
        else:
            # Serve static files
            try:
                file_path = os.path.join(os.path.dirname(__file__), self.path.lstrip('/'))
                with open(file_path, 'rb') as file:
                    self.send_response(HTTPStatus.OK)
                    self.send_header('Content-Type', mimetypes.guess_type(file_path)[0])
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        if self.path == '/handleStream':
            self.handle_stream()
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def handle_stream(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        start_stream = data.get('startStream', False)
        
        if start_stream and not self.stream_thread:
            self.stream_event.set()
            self.stream_thread = threading.Thread(target=self.stream_frames)
            self.stream_thread.start()
        elif not start_stream and self.stream_thread:
            self.stream_event.clear()
            self.stream_thread.join()
            self.stream_thread = None
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = json.dumps({'isStreaming': start_stream})
        self.wfile.write(response.encode('utf-8'))

    def serve_html_file(self, filename):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                content = content.decode('utf-8')
                content = content.replace('{{CWD}}', os.getcwd())
                self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND, f"File {filename} not found")

    def stream_frames(self):
        try:
            while self.stream_event.is_set():
                try:
                    frame = self.data_queue.get(timeout=1)
                    pil_image = Image.fromarray(frame)
                    if pil_image.mode == 'RGBA':
                        pil_image = pil_image.convert('RGB')
                    buffer = BytesIO()
                    pil_image.save(buffer, format='JPEG', optimize=True, quality=80)
                    jpeg_bytes = buffer.getvalue()
                    self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n--frame\r\n')
                    buffer.close()
                except queue.Empty:
                    continue
                except (BrokenPipeError, ConnectionResetError, OSError):
                    # Handle connection errors
                    break
        finally:
            self.stream_event.clear()            
def image_streamer_worker(image_queue: Queue, port=5000):
    try:
        server_address = ('localhost', port)
        class StreamingServer(http.server.HTTPServer):
            def __init__(self, server_address, RequestHandlerClass, data_queue: Queue):
                super().__init__(server_address, RequestHandlerClass)
                self.data_queue: Queue = data_queue
                self.is_streaming = False

        httpd = StreamingServer(server_address, ImageStreamer, image_queue)
        print(f"Serving at http://localhost:{port}/stream")
        httpd.serve_forever()
    except Exception as e:
        print(f"Error in image streamer: {e}")

def web_service_workder(system_store: SystemStore, stop_event):
    try:
        camera_store = system_store.camera_store
        # wait for resources available!
        while (not camera_store.get_preview_img or not camera_store.preview_image_queue)\
               and not stop_event.is_set():
            time.sleep(0.1)
            pass

        image_queue: Queue = camera_store.preview_image_queue
        request_streamer = camera_store.request_streamer
        request_streamer['run'] = True

        streamer_process = Process(target=image_streamer_worker, args=(image_queue, 8000))
        streamer_process.start()

        while not stop_event.is_set():
            if request_streamer['run'] == True:
                image_queue.put(camera_store.get_preview_img())

        streamer_process.terminate()
        streamer_process.join()

    except Exception as e:
        print(f"Error in camera feeding preview image: {e}")
