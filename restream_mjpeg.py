#!/usr/bin/env python

from flask import Flask, render_template, Response, send_file
import urllib

import logging

# Comment out this line to hide the log lines
logging.basicConfig(level=logging.DEBUG)

# Initialize app
app = Flask(__name__)

#############
# Functions #
#############

def gen(stream, error_image, boundary):
    # Add headers to the error
    with open(error_image, 'rb') as f:
        error_with_headers = b'--' + boundary + '\r\nContent-Type: image/jpeg\r\n\r\n' + f.read() + b'\r\n'

    while True:
        content_length_found = False

        # Start with blank data var
        data = ''

        # Read first several lines, looking for content length line
        for line in range(10):
            data += stream.readline()

            if 'Content-Length' in data:
                content_length_found = True
                break

        if content_length_found:
            # Figure out the content length
            try:
                content_length = int(data.splitlines()[-1].rstrip().split()[-1])
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as ex:
                logging.debug("Failed to parse the content length line")
                yield error_with_headers
                raise StopIteration

            logging.debug("Content_Length: %d" % content_length)
        else:
            # Unable to figure out content length
            logging.debug("Content length field not found")
            yield error_with_headers
            raise StopIteration

        # Read the line before the jpeg
        data += stream.readline()

        # Read the jpeg
        data += stream.read(content_length)

        # Return the jpeg
        yield data

##########
# Routes #
##########

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""

    # URL to open
    LINK = 'http://username:password@IP:port/path/to/mjpeg_stream'

    # Error image
    # Relative path if in the same directory as your flask app
    # Otherwise absolute path
    error_image = 'error_image.jpg'

    # Connect to stream
    try:
        logging.debug("Connecting to stream...")
        stream = urllib.urlopen(LINK)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as ex:
        logging.debug("Failed to connect to stream: " + str(ex))
        return send_file(error_image, mimetype="image/jpeg")

    # Check if data looks like an mjpeg stream
    if 'multipart/x-mixed-replace' not in stream.info()["content-type"]:
        logging.debug("'%s' did not produce an mjpeg stream" % LINK)
        return send_file(error_image, mimetype="image/jpeg")

    # Figure out boundary string
    try:
        boundary = [ x[9:] for x in stream.info()["content-type"].split(';') if 'boundary' in x ][0]
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as ex:
        logging.debug("Failed to figure out boundary string: " + str(ex))
        return send_file(error_image, mimetype="image/jpeg")

    # Start returning data
    return Response(gen(stream, error_image, boundary), mimetype='multipart/x-mixed-replace; boundary=%s' % boundary)

#############
# Start App #
#############

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
