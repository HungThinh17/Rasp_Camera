import http.server
from io import BytesIO
from multiprocessing import Queue
from http import HTTPStatus
from PIL import Image

class ImageStreamer(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.data_queue: Queue = server.data_queue
        super().__init__(request, client_address, server)

    def do_GET(self):
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            self.wfile.write(b'--frame\r\n')
            self.stream_frames()

        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def stream_frames(self):
        try:
            while True:
                # Capture frame-by-frame
                frame = self.data_queue.get()

                # Assuming 'frame' is a NumPy array representing the image data
                pil_image = Image.fromarray(frame)

                # Check if the image mode is RGBA and convert to RGB if necessary
                if pil_image.mode == 'RGBA':
                    pil_image = pil_image.convert('RGB')

                # Create a BytesIO object to store the JPEG data
                buffer = BytesIO()

                # Save the image to the BytesIO object as JPEG with optimized settings
                pil_image.save(buffer, format='JPEG', optimize=True, quality=80)

                # Get the JPEG byte data from the BytesIO object
                jpeg_bytes = buffer.getvalue()

                # Check if the client has requested a capture
                if self.headers.get('Capture') == 'true':
                    self.send_response(HTTPStatus.OK)
                    self.send_header('Content-Type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(jpeg_bytes)
                    break

                # Write the frame as a multipart response
                self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n--frame\r\n')

                # Clean up the BytesIO object
                buffer.close()
        except BrokenPipeError:
            # Handle broken pipe error (client disconnected)
            pass

def image_streamer_worker(image_queue: Queue, port=5000):
    try:
        server_address = ('localhost', port)
        class StreamingServer(http.server.HTTPServer):
            def __init__(self, server_address, RequestHandlerClass, data_queue: Queue):
                super().__init__(server_address, RequestHandlerClass)
                self.data_queue: Queue = data_queue

        httpd = StreamingServer(server_address, ImageStreamer, image_queue)
        print(f"Serving at http://localhost:{port}/stream")
        httpd.serve_forever()
    except Exception as e:
        print(f"Error in image streamer: {e}")
