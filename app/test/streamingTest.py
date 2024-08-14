import http.server
from http import HTTPStatus
from picamera2 import Picamera2
import sys
import io
from PIL import Image

# =============================================
# For debugging ...
# =============================================
if '--debug' in sys.argv:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger attach...")
    debugpy.wait_for_client()
    debugpy.breakpoint()
    print("Debugger is attached!")

# =============================================

# Initialize Picamera2
picam2 = Picamera2()
picam2.start()

class StreamingHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/video_feed':
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
                frame = picam2.capture_array()

                # Assuming 'frame' is a NumPy array representing the image data
                pil_image = Image.fromarray(frame)

                # Check if the image mode is RGBA and convert to RGB if necessary
                if pil_image.mode == 'RGBA':
                    pil_image = pil_image.convert('RGB')

                # Create a BytesIO object to store the JPEG data
                buffer = io.BytesIO()

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

if __name__ == "__main__":
    server_address = ('', 5000)
    httpd = http.server.HTTPServer(server_address, StreamingHandler)
    print(f"Serving at http://localhost:{5000}/video_feed")
    httpd.serve_forever()
