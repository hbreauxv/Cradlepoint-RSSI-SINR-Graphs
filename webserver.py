'''
webserver.py runs a basic python web server to serve up the rssi/sinr graphs page
'''


try:
    import cs
    import sys
    import traceback

    from http.server import BaseHTTPRequestHandler
    from app_logging import AppLogger

except Exception as ex:
    # Output DEBUG logs indicating what import failed. Use the logging in the
    # CSClient since app_logging may not be loaded.
    cs.CSClient().log('getsignal.py', 'Import failure: {}'.format(ex))
    cs.CSClient().log('getsignal.py', 'Traceback: {}'.format(traceback.format_exc()))
    sys.exit(-1)

# Create an AppLogger for logging to syslog in NCOS.
log = AppLogger()
log.debug('Started webserver.py')


class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        # serve the index.html file
        if self.path == '/':
            try:
                f = open('index.html','rb')

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())

                f.close()
                return
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)

        # serve the Chart.js file
        if self.path == '/Chart.js':
            try:
                f = open('Chart.js','rb')
                self.send_response(200)
                self.send_header('Content-type', 'text/javascript')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)

        # serve the css file
        if self.path == '/teststyle.css':
            try:
                f = open('teststyle.css','rb')
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)

        # serve the rssiChart.js file
        if self.path == '/rssiChart.js':
            try:
                f = open('rssiChart.js','rb')
                self.send_response(200)
                self.send_header('Content-type', 'text/javascript')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)

        # serve the sinrChart.js file
        if self.path == '/sinrChart.js':
            try:
                f = open('sinrChart.js','rb')
                self.send_response(200)
                self.send_header('Content-type', 'text/javascript')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)


if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('', 9001), GetHandler)
    log.debug('Starting web server...')
    server.serve_forever()
