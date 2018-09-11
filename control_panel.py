import manage_data
import screen
import argparse
import os
import learning
import threading

parser = argparse.ArgumentParser(description="")
parser.add_argument("-learn", help="-learn : Delete all experiences and learn new data", dest="learn", action="store")
parser.set_defaults(learn=None)
parser.add_argument("-run", help="-run : Run face recognition system", dest="run", action="store_true")
parser.set_defaults(run=False)
parser.add_argument("--server", help="--server = get image from server", dest="server", action="store")
parser.set_defaults(server= None)

from flask import Flask, render_template, Response
app = Flask(__name__)
frame_buffer = b''

def gen():
    global frame_buffer
    while True:
        frame = screen.q_frame_web.get()
        if frame is None:
            continue
        frame_buffer = (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def run_gen():
    global frame_buffer
    while True:
        yield frame_buffer

@app.route('/video_feed')
def video_feed():
    global frame_buffer
    return Response(run_gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def main(args):
    if args.learn is not None:
        learning.offline_learning(args.learn)
    if args.run == True:
        if args.server == None:
            screen.run()
        else:
            screen.run(args.server)

if __name__ == '__main__':
    main(parser.parse_args())
    threading.Thread(target=gen, args=()).start()
    app.run(host='127.0.0.1' , port=5001)
