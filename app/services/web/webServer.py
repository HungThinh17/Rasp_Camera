
import os
import http.server
import json
import socket
import threading
import mimetypes
from enum import Enum
from io import BytesIO
from multiprocessing import Queue
from http import HTTPStatus
from PIL import Image

class UserRequest(Enum):
    UPDATE_INFO = 'UPDATE_INFO'
    STREAMING = 'STREAMING'
    STOP_STREAMING = 'STOP_STREAMING'
    SINGLE_CAPTURE = 'SINGLE_CAPTURE'
    AUTO_CAPTURE = 'AUTO_CAPTURE'
    PREVIEW = 'PREVIEW'
    CLEAN = 'CLEAN'
    EXIT = 'EXIT'

class WebServer(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.data_queue: Queue = server.data_queue
        self.user_request_dict: dict = server.user_request_dict
        self.server = server
        super().__init__(request, client_address, server)

    def do_GET(self):
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.serve_html_file('index.html')

        elif self.path.startswith('/img'):
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'image/jpeg')
            self.end_headers()
            self.get_img()

        elif self.path.startswith('/stream'):
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Connection', 'keep-alive')  # Keep the connection alive
            self.end_headers()
            threading.Thread(target=self.stream_imgs, args=(self.server.is_streaming,)).start()

        elif self.path.startswith('/info'):
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.update_info()

        elif self.path.startswith('Digime.jpeg'):
            try:
                # stop streaming
                self.stopStreaming()
                # show digime image instead.
                file_path = os.path.join(os.path.dirname(__file__), self.path.lstrip('/'))
                with open(file_path, 'rb') as file:
                    self.send_response(HTTPStatus.OK)
                    self.send_header('Content-Type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND)
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
        if self.path == '/request_stream':
            self.handle_stream_request()
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def update_info(self):
        self.user_request_dict[UserRequest.UPDATE_INFO] = True
        while(self.user_request_dict[UserRequest.UPDATE_INFO]): pass
        info = self.user_request_dict['info']
        self.wfile.write(info.encode('utf-8'))

    def handle_stream_request(self):
        # handle request data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        start_stream = data.get('startStream', False)

        if start_stream:
            self.user_request_dict[UserRequest.STREAMING] = True
            self.server.is_streaming = True
        else:
            self.user_request_dict[UserRequest.STREAMING] = False
            self.server.is_streaming = False
    
        # handle request response
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = json.dumps({'isStreaming': start_stream})
        self.wfile.write(response.encode('utf-8'))

    def startStreaming(self):
        self.user_request_dict[UserRequest.STREAMING] = True
        self.user_request_dict[UserRequest.STOP_STREAMING] = False
        self.server.is_streaming = True

    def stopStreaming(self):
        self.user_request_dict[UserRequest.STREAMING] = False
        self.user_request_dict[UserRequest.STOP_STREAMING] = True
        self.server.is_streaming = False

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

    def get_img(self):
        try:
            frame = self.data_queue.get()
            jpeg_bytes = self.convert_frame_to_jpeg(frame)
            self.wfile.write(jpeg_bytes)
        
        except Exception as e:
            print(f"Error in stream_frames: {e}")
            raise

    def stream_imgs(self, is_streaming):
        try:
            while(is_streaming):
                frame = self.data_queue.get()
                jpeg_bytes = self.convert_frame_to_jpeg(frame)

                # Send the image part with headers
                try:
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(b'Content-Length: ' + str(len(jpeg_bytes)).encode() + b'\r\n\r\n')
                    self.wfile.write(jpeg_bytes + b'\r\n')
                except IOError as e:
                    print(f"IOError: {e}")
                    break
        
            # Send the final boundary to indicate the end of the multipart response
            self.wfile.write(b'--frame--\r\n')

        except Exception as e:
            print(f"Error in stream_frames: {e}")

    def convert_frame_to_jpeg(self, frame):
        # Check if the image mode is RGBA and convert to RGB if necessary
        pil_image = Image.fromarray(frame)
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')
        buffer = BytesIO()
        pil_image.save(buffer, format='JPEG', optimize=True, quality=80)

        return buffer.getvalue()
      
def web_server_worker(image_queue: Queue, user_request_dict, port=5000):
    try:
        server_address = ('localhost', port)
        class StreamingServer(http.server.HTTPServer):
            def __init__(self, server_address, RequestHandlerClass, data_queue: Queue):
                super().__init__(server_address, RequestHandlerClass)
                self.data_queue: Queue = data_queue
                self.user_request_dict = user_request_dict
                self.is_streaming = False

        httpd = StreamingServer(server_address, WebServer, image_queue)
        print(f"Serving at http://localhost:{port}")
        httpd.serve_forever()
    except Exception as e:
        print(f"Error in image streamer: {e}")
