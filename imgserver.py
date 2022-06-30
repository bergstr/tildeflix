
import http.server
from http.server import BaseHTTPRequestHandler
import urllib.parse
import posixpath
from pathlib import Path
import subprocess
import hashlib
import shutil
from os import environ


IMGCACHEDIR = Path("~/.cache/tildeflix").expanduser()


if (not IMGCACHEDIR.is_dir()):
    Path.mkdir(IMGCACHEDIR, mode=0o770)


class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        vpath = urllib.parse.unquote(self.path)

        # Fix urlencoded twice
        if ('%2' in vpath):
            vpath = urllib.parse.unquote(vpath)

        vpath = posixpath.normpath(vpath)
        pathhash = hashlib.sha224(vpath.encode()).hexdigest()

        vidfile = Path(str(VIDEODIR)+vpath)
        imgfile = IMGCACHEDIR.joinpath(pathhash).with_suffix('.jpg')


        if (imgfile.is_file()):

            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.end_headers()

            with open(imgfile, mode='rb') as file:
                shutil.copyfileobj(file, self.wfile)

            return

        else:

            if (not vidfile.exists()):
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return

            vidfile = str(vidfile)
            imgfile = str(imgfile)

            # ffmpeg -ss 00:01:30 -i myvideo.mkv -vframes 1 -s 960x540 screenshot.jpg
            try:
                subprocess.run(["ffmpeg", "-hide_banner", "-n", "-ss", "00:01:30", "-i", vidfile, 
                "-vframes", "1", "-s", "960x540", imgfile], check=True)

            except CalledProcessError:
                self.send_response(500)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return           


            self.send_response(302)
            self.send_header("Location", "/img"+self.path)
            self.send_header("Content-Length", "0")
            self.end_headers()

            return



def run(VDIR,server_class=http.server.HTTPServer, handler_class=HTTPHandler):
    global VIDEODIR
    VIDEODIR = VDIR
    server_address = ('127.0.0.1', 8001)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
