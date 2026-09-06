#!/bin/bash
DIR=$(dirname "$0")/$(uname)$(getconf LONG_BIT)_$(arch)
if [ ! -d "$DIR" ]; then
  cd "$(dirname "$0")/Linux32_armv7l"
else
  cd "$DIR"
fi

pkill -f mediamtx 2>/dev/null
pkill -f "ffmpeg.*rtsp://127.0.0.1:8554" 2>/dev/null
sleep 1

chmod +x ./mediamtx
./mediamtx &
RTSP_PID=$!
sleep 2

MJPEG_URL="${MJPEG_URL:-http://127.0.0.1:8080/?action=stream}"
ffmpeg -loglevel warning -f mjpeg -r 15 -i "$MJPEG_URL" \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -g 30 -keyint_min 15 \
  -b:v 1500k -maxrate 1500k -bufsize 1500k \
  -pix_fmt yuv420p \
  -f rtsp rtsp://127.0.0.1:8554/ch0_0 &
FFMPEG_PID=$!

wait $RTSP_PID $FFMPEG_PID
