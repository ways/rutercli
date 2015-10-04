#!/usr/bin/env python3

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
import sys
from wsgiref.validate import validator

sys.path.insert(0, '/local/www/graph.no/ruter/')

import ruter

stopname=''
html = """
<html>
<body>
  %s
   <form method="get" action="">
      <p>
         Stopp: <input type="text" name="stopname">
         </p>
      <p>
         <input type="submit" value="Submit">
         </p>
      </form>
   <p>
      Stopp: %s<br>
      </p>
   </body>
</html>"""

def application(environ, start_response):

  # Returns a dictionary containing lists as values.
  d = parse_qs(environ['QUERY_STRING'])

  # In this idiom you must issue a list containing a default value.
  stopname = d.get('stopname', [''])[0] # Returns the first age value.

  # Always escape user input to avoid script injection
  stopname = escape(stopname)

  ruteroutput = ruter.TransportationType['bus']

  stopid = ruter.get_stopid(stopname)
  departures = ruter.get_departures(stopid)
  ruteroutput += format_departures(departures)

  response_body = html % (ruteroutput, stopname or 'Empty')

  status = '200 OK'

  # Now content type is text/html
  response_headers = [('Content-Type', 'text/html; charset=utf-8'),
                      ('Content-Length', str(len(response_body)))]
  start_response(status, response_headers)

  return [response_body.encode("utf-8")]

