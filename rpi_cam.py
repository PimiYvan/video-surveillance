from flask import Flask, render_template, Response
from Stream import Streamer
app = Flask(__name__)

streamer = Streamer('0.0.0.0', 8089)

def gen():
    # streamer = Streamer('0.0.0.0', 8089)
    if(not streamer.client_connected()):
        streamer.start()

    while True:
        if streamer.client_connected() :
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + streamer.get_jpeg() + b'\r\n\r\n')

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
  return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Streamer stream = Streamer('0.0.0.0', 8089)
    app.run()