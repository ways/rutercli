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
<head>
  <meta name="HandheldFriendly" content="true" />
  <meta name="viewport" content="width=480, user-scalable=yes" />
</head>
<body>

<pre>
<form method="get" action=""> Stopp: <input type="text" name="stopname" value="%s"> <input type="submit" value="Submit">
</form>
%s
</pre>

   </body>
</html>"""

def application(environ, start_response):
  ruteroutput=''

  # Returns a dictionary containing lists as values.
  d = parse_qs(environ['QUERY_STRING'])

  # In this idiom you must issue a list containing a default value.
  stopname = d.get('stopname', [''])[0] # Returns the first value.

  # Always escape user input to avoid script injection
  stopname = escape(stopname)

  if 0 < len(stopname):
    stopid, status, messages = ruter.get_stopid(stopname)
    if 0 < len(messages):
      for line in messages.split('\n'):
        num_start=line.find('[')
        num_end=line.find(']')
        line = line.replace('[', '<a href="/?stopname=' + line[num_start+1:num_end] + '">')
        line = line.replace(']', '</a>')
        ruteroutput += line + '\n'
    if stopid:
      departures = ruter.get_departures(stopid)
      ruteroutput = ruter.format_departures(departures)

  response_body = html % (stopname or '', ruteroutput)

  status = '200 OK'

  # Now content type is text/html
  response_headers = [('Content-Type', 'text/html; charset=utf-8'),
                      ('Content-Length', str(len(response_body)))]
  start_response(status, response_headers)

  return [response_body.encode("utf-8")]

