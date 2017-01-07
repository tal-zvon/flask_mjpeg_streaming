# flask_mjpeg_streaming
Sample apps for reading an mjpeg stream and rebroadcasting it

This can login to a server that uses authentication, and broadcast it as an open stream that doesn't require a username or password (ex. on your lan)

Just set the LINK variable in `@app.route('/video_feed')` to the URL of your MJPEG stream

The only thing this requires is the flask package to be installed on your system, or in your virtualenv
