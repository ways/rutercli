#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015 Lars Falk-Petersen.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

system_version = '0.3'
system_name = 'ruter.py'

import sys, datetime, time, urllib.request, urllib.error, urllib.parse, codecs, unicodedata, re
import xml.etree.ElementTree as ET

ttycode=sys.stdin.encoding

# icons http://www.fileformat.info/info/unicode/block/transport_and_map_symbols/list.htm

# TransportationType (in SOAP) 	Num value (in JSON response)
#bus 	0 #ferry 	1 #rail 	2 #tram 	3 #metro 	4
TransportationType = {
  'bus':   '🚌',
  'ferry': '🛥',
  'rail':  '🚆',
  'tram':  '🚋',
  'metro': 'Ⓣ',
} #🚇
stopicon="🚏"
timeicon="🕒"

# html to terminal safe colors
colors = {
  'F07800': 'orange',
}

apiurl='https://reisapi.ruter.no/stopvisit/getdepartures/'
#apiurl='http://localhost:8080/'
schema='{http://schemas.datacontract.org/2004/07/Ruter.Reis.Api.Models}'
stopsfile='GetStopsRuter.xml'
xmlroot=None
verbose=False
output=[]
directions={} # Dict of directions at this stop

def usage():
  print('Bruk: %s [-a] [-l] [-n] [-v] <stasjonsnavn|stasjonsid>' % sys.argv[0])
  print('''
  -a       ASCII for ikke å bruke Unicode symboler/ikoner
  -l       Bruk lokal fil ruter.temp som xml-kilde (kun for utvikling)
  -n       Begrens treff pr. spor, tilbakefall er 5.
  -v       verbose for utfyllende informasjon
  ''')
  print(system_name, 'version', system_version)
  sys.exit(1)

def err(string):
  sys.stdout.write('%s: Error: %s\n' % (sys.argv[0], string))
  sys.exit(1)

""" Read stopsfile, search for stop, return matches as dict """
def fetch_stops(filename, searchname):
  #searchname = unicodedata.normalize('NFC', unicode(searchname).lower())
  searchname = searchname.lower()
  result = {}
  start = time.time()

  if verbose:
    print("Parsing stopsfile", filename)
  try:
    root = ET.parse(filename)
  except ET.ParseError as error:
    print("Error loading stopsfile"); print(error)

  stop = time.time()
  if verbose:
    print("File read and parsed in %0.3f ms" % (stop-start))

  start = time.time()

  for counter, stop in enumerate(root.findall(schema + 'Stop')):
    stopid = int(stop.find(schema + 'ID').text)
    stopname = \
      unicodedata.normalize('NFC', str(stop.find(schema + 'Name').text.lower().replace(' ', '').replace('(', '').replace(')', '').replace('-','')))
    if re.match(
      searchname.replace(' ', '').replace('(', '').replace(')', '').replace('-','') + '*',
      stopname):
      if verbose:
        print("Hit: %d - %s" % (stopid, stopname))
      result[stopname] = stopid
    if verbose and counter % 1000 == 0:
      print("Reading stops...", counter)
      print("%d - %s %s" % (stopid, stopname.lower(), searchname))

  stop = time.time()
  if verbose:
    print("File searched names in %0.3f ms" % (stop-start))

  if verbose:
    print("Results: ", len(result))
    print(result)
  return result

""" Fetch xml file from url, return string """
def fetch_api_xml(url):
  html = None

  start = time.time()
  try:
    if verbose:
      print("fetch_api_xml", url)

    request = urllib.request.Request(url, headers={"Accept" : 'application/xml'} )
    html=urllib.request.urlopen(request).read()
  except urllib.error.HTTPError as error:
    print(url, error)
  except urllib2.BadStatusline as error:
    print(url, error)

  stop = time.time()
  if verbose:
    print("Data fetched in %0.3f ms" % (stop-start))
  return html

def parse_xml(xml, filename):
  if None == xml:
    tree = ET.parse(filename).getroot()
  else: #None == filename
    tree = ET.fromstring(xml)
  return tree


''' Read stopfile and return name '''
def find_stop_by_name(searchname):
  return None

def convert(str):
  #attempt to convert string str from iso-8859-1/windows-1252
  newstr=str

  result = chardet.detect(str)
  if verbose:
    print("result")
    print(result,"-",result['encoding'])

  #return str.decode(result['encoding']).encode("UTF-8")
  try:
    #print "result:",str.decode('iso-8859-1').encode("UTF-8")
    newstr = str.decode('utf-8').encode("UTF-8")
  except UnicodeDecodeError as e:
    #print "Err",e,str
    newstr = str.decode('iso-8859-1').encode("UTF-8")
  #except UnicodeEncodeError as e:

  return newstr


if __name__ == '__main__':
  stopname=''
  stopid=''
  limitresults=15
  localxml=None
  args = sys.argv[1:]

  if '-v' in args:
    verbose = True
    args.pop(args.index('-v'))
    print(args)

  if '-n' in args:
    limitresults = args[ args.index('-n')+1 ]
    args.pop(args.index('-n'))
    if verbose:
      print("limitresults", limitresults)
      print(args, stopname)

  if '-l' in args:
    localxml = 'ruter.temp'
    args.pop(args.index('-l'))

  if len(args) < 1:
    usage()
  else:
    stopname = ''.join(args[0:])


  if verbose:
    print("stopname", stopname)

  ''' Check if we have number or name '''
  stopid = None
  if not stopname.isdigit():
    if verbose:
      print("Looking up stopname.")
    stops = fetch_stops(stopsfile, stopname)

    if len(stops) > 10:
      print("%s ga for mange treff, prøv igjen." % stopname)
      sys.exit(3)
    elif len(stops) > 1:
      print("Flere treff, angi mer nøyaktig:")
      print(stops)
      for key in stops:
        print("[%d] %s" % (stops[key], key))
      sys.exit(3) #Too many hits
    elif 0 == len(stops):
      print("Ingen treff på stoppnavn.")
      sys.exit(4) #No hits

    stopid = next(iter(stops.values()))

  else:
    if verbose:
      print("Looking up stopid.")
    stopid = stopname

  xmlroot = None
  if localxml:
    xmlroot = parse_xml(None, localxml)
  else:
    xmlroot = parse_xml(fetch_api_xml(apiurl + str(stopid)), None)

  ''' Dig out values from xml '''
  for counter, MonitoredStopVisit in enumerate(xmlroot.findall(schema + 'MonitoredStopVisit')):
    outputline=''
    #if verbose:
    #  print "  MonitoredStopVisits:", len(MonitoredStopVisit)

    #Extensions = MonitoredStopVisit.find(schema + 'Extensions')
    #deviations = MonitoredStopVisit[0][0] # or MonitoredVehicleJourney
    MonitoredVehicleJourney = \
      MonitoredStopVisit.find(schema + 'MonitoredVehicleJourney')
    DestinationName = MonitoredVehicleJourney.find(schema + \
      'DestinationName').text
    DirectionName = MonitoredVehicleJourney.find(schema + 'DirectionName').text
    if DirectionName == None:
      continue

    Delay = MonitoredVehicleJourney.find(schema + 'Delay')
    VehicleMode = MonitoredVehicleJourney.find(schema + 'VehicleMode')
    MonitoredCall = MonitoredVehicleJourney.find(schema + 'MonitoredCall')
    MonitoredVehicleJourney.find(schema + 'Delay')
    PublishedLineName = MonitoredVehicleJourney.find(schema + \
      'PublishedLineName').text

    #print "MonitoredVehicleJourney", MonitoredVehicleJourney.getchildren()
    #print PublishedLineName.text

    # Fetch and convert time, original 2015-09-03T18:19:00+02:00
    # TODO: currently skipping UTC offset
    AimedDepartureTime = \
      datetime.datetime.strptime(MonitoredCall.find(schema + \
      'AimedDepartureTime').text[:19], "%Y-%m-%dT%H:%M:%S")

    outputline += "%s %s %s    " \
      % (PublishedLineName.rjust(3), DestinationName.ljust(25), DirectionName)

    if AimedDepartureTime.day == datetime.date.today().day:
      outputline += \
      "%s " % str(AimedDepartureTime.time()).ljust(17)
    else:
      outputline += \
      "%s" % str(AimedDepartureTime).ljust(17)

    outputline += TransportationType[VehicleMode.text]

    if 'PT0S' != str(Delay.text):
      outputline += '    ' + Delay.text.ljust(10)

    output.append([DirectionName, outputline])
    if DirectionName not in directions:
      directions[DirectionName] = 0

  if verbose:
    print(output)

  output.sort()
  ''' Print main output '''
  print("Linje/Destinasjon             Spor Tid               Type Forsinkelse")
  for counter, outarray in enumerate(output):
    #print outarray
    if limitresults > directions[outarray[0]]:
      print(outarray[1])
      directions[outarray[0]]+=1








  '''
  print "children:"
  print "MonitoredStopVisit", MonitoredStopVisit.getchildren()
  print "Extensions", Extensions.getchildren()
  print "MonitoredVehicleJourney", MonitoredVehicleJourney.getchildren()
  #for mvj in MonitoredStopVisit.getchildren():
  #  print mvj.text
  '''
  #break

'''
MonitoredStopVisit
None
None
2190090
2015-09-01T10:32:12.833+02:00


Extensions
None
false
F07800
None

MonitoredVehicleJourney
504:5H01H02
PT0S
0001-01-01T00:00:00
Vestli
3011730
1
1
None
false
5
true
None
me
0001-01-01T00:00:00
ØSÅ2
2190090
5
None
None
34856
metro
176
'''
