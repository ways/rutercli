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

system_version = '0.4'
system_name = 'ruter.py'

import sys, datetime, time, urllib.request, urllib.error, re, os.path
import xml.etree.ElementTree as ET

TransportationType = {
  'bus':   '🚌',
  'ferry': '⛴',
  'rail':  '🚆',
  'tram':  '🚋',
  'metro': 'Ⓣ', #🚇
}
stopicon="🚏"
timeicon="🕒"

# html to terminal safe colors
color_codes = {
  'F07800': 'orange',
}

apiurl='https://reisapi.ruter.no/stopvisit/getdepartures/'
schema='{http://schemas.datacontract.org/2004/07/Ruter.Reis.Api.Models}'
stopsfile='GetStopsRuter.xml'
stopsurl='http://reisapi.ruter.no/Place/GetStopsRuter'
verbose=False
ascii=False

def usage():
  print('Bruk: %s [-a] [-l] [-n] [-v] <stasjonsnavn|stasjonsid>' % sys.argv[0])
  print('''
  -h       Vis denne hjelpen.
  -l       Begrens treff til kun linje-nummer.
  -n       Begrens treff pr. platform, tilbakefall er 5.
  -p       Begrens treff til platform-nummer.
  -v       Verbose for utfyllende informasjon
  ''')

  for icon in TransportationType:
    print (icon, TransportationType[icon])

  for color_code in color_codes:
    print (color_code, color_codes[color_code])

  #-a       ASCII for ikke å bruke Unicode symboler/ikoner
  #-t       Bruk lokal fil ruter.temp som xml-kilde (kun for utvikling)

  print(system_name, 'version', system_version)
  sys.exit(1)

def err(string):
  sys.stdout.write('%s: Error: %s\n' % (sys.argv[0], string))
  sys.exit(1)

""" Check if stopsfile exists, download if necessary.
    Read stopsfile, search for stop, return matches as dict """
def fetch_stops(filename, name_needle):
  name_needle = name_needle.lower()
  result = {}
  start = time.time()

  if not os.path.isfile(filename):
    print("Oversikt over stop mangler (%s), laster ned... " % filename, end="")
    request = urllib.request.Request(stopsurl, headers={"Accept" : 'application/xml'})
    with urllib.request.urlopen(request, timeout=10) as response, open(filename, 'wb') as out_file:
      data = response.read() # a `bytes` object
      out_file.write(data)
    print("ferdig.")

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

  # Loop through all stop names, searching for name_needle
  for counter, stop in enumerate(root.findall(schema + 'Stop')):
    # Current stopid and stopname
    stopid = int(stop.find(schema + 'ID').text)
    stopname = stop.find(schema + 'Name').text.lower()

    # Attempt 1:1 match
    if name_needle == stopname:
      if verbose:
        print("Direct hit: %d - %s" % (stopid, stopname))
      result.clear()
      result[stopname] = stopid
      break

    if re.match(
      name_needle.replace(' ', '').replace('(', '').replace(')', '').replace('-','') + '*',
      stopname):
      if verbose:
        print("Hit: %d - %s" % (stopid, stopname))
      result[stopname] = stopid

    # Print progress every 1k stops
    if verbose and counter % 1000 == 0:
      print("Reading stops...", counter)
      print("%d - %s %s" % (stopid, stopname.lower(), name_needle))

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
    html=urllib.request.urlopen(request, timeout=10).read()
  except urllib.error.HTTPError as error:
    print(url, error)
  except:
    print("Fikk ikke tak i ruter.no, prøv igjen.")
    sys.exit(1)

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


def get_stopid(stopname):
  if verbose:
    print("stopname", stopname)

  stopid=None

  ''' Check if we have number or name '''
  if not stopname.isdigit():
    if verbose:
      print("Looking up stopname.")
    stops = fetch_stops(stopsfile, stopname)

    if len(stops) > 30:
      print("%s ga for mange treff, prøv igjen." % stopname)
      sys.exit(3)
    elif len(stops) > 1:
      print("Flere treff, angi mer nøyaktig:")
      for key in stops:
        print("[%d] %s" % (stops[key], key))
      sys.exit(3) #Too many hits
    elif 0 == len(stops):
      print("Ingen treff på stoppnavn.")
      sys.exit(4) #No hits

    selected_stop = list(stops.keys())[0]
    stopid = stops[selected_stop]
    print("Avganger fra %s, oppdatert %s" \
      % (selected_stop, datetime.datetime.now().strftime("%H:%M")))

  else:
    if verbose:
      print("Looking up stopid.")
    stopid = stopname

  return stopid


def get_departures (stopid, localxml):
  departures=[]

  xmlroot = None
  if localxml:
    xmlroot = parse_xml(None, localxml)
  else:
    xmlroot = parse_xml(fetch_api_xml(apiurl + str(stopid)), None)

  ''' Dig out values from xml '''
  if verbose:
    print ("Found %d MonitoredStopVisits" % len(xmlroot.findall(schema + 'MonitoredStopVisit')))

  for counter, MonitoredStopVisit in enumerate(xmlroot.findall(schema + 'MonitoredStopVisit')):
    departure={}

    MonitoredVehicleJourney = \
      MonitoredStopVisit.find(schema + 'MonitoredVehicleJourney')
    departure['DestinationName'] = MonitoredVehicleJourney.find(schema + \
      'DestinationName').text

    departure['Delay'] = MonitoredVehicleJourney.find(schema + 'Delay').text
    departure['VehicleMode'] = MonitoredVehicleJourney.find(schema + 'VehicleMode').text
    MonitoredCall = MonitoredVehicleJourney.find(schema + 'MonitoredCall')
    #MonitoredVehicleJourney.find(schema + 'Delay')
    departure['PublishedLineName'] = MonitoredVehicleJourney.find(schema + \
      'PublishedLineName').text

    departure['DeparturePlatformName'] = MonitoredCall.find(schema + 'DeparturePlatformName').text

    #print "MonitoredVehicleJourney", MonitoredVehicleJourney.getchildren()

    # Fetch and convert time, original 2015-09-03T18:19:00+02:00
    # TODO: currently skipping UTC offset
    departure['AimedDepartureTime'] = \
      datetime.datetime.strptime(MonitoredCall.find(schema + \
      'AimedDepartureTime').text[:19], "%Y-%m-%dT%H:%M:%S")

    departure['InCongestion'] = MonitoredVehicleJourney.find(schema + 'InCongestion').text

    departures.append(departure)

  # Sort departures by platform name
  return sorted(departures, key=lambda k: k['DeparturePlatformName'])


''' Print main output '''
def print_departures(departures, platform_number, limitresults, line_number):
  if verbose:
    print(departures[0])
  output=[]
  directions={}

  print("Linje/Destinasjon             Platform            Tid    Forsinkelse")

  for counter, departure in enumerate(departures):
    outputline=''

    # Limit results by line_number
    if line_number:
      if str(line_number) != PublishedLineName:
        continue

    # Limit results by platform_number
    if platform_number:
      if str(platform_number) != DeparturePlatformName:
        continue

    # Keep list of platforms with number of hits
    if departure['DeparturePlatformName'] not in directions.keys():
      directions[departure['DeparturePlatformName']] = 1
    else:
      directions[departure['DeparturePlatformName']] += 1

    # Limit hits by platform
    if directions[departure['DeparturePlatformName']] > limitresults:
      continue

    # Start outputting

    # Icon for type of transportation
    outputline += TransportationType[departure['VehicleMode']]

    # Line number, name, platform
    outputline += "%s %s %s " \
      % (departure['PublishedLineName'].rjust(3), departure['DestinationName'].ljust(24), '{:<19.19}'.format(departure['DeparturePlatformName']))

    if departure['AimedDepartureTime'].day == datetime.date.today().day:
      outputline += \
      "%s" % str(departure['AimedDepartureTime'].strftime("%H:%M"))
      outputline += 'kø' if 'true' == departure['InCongestion'] else '  '
    else:
      outputline += \
      "%s" % str(departure['AimedDepartureTime']).ljust(17)

    if departure['Delay'] and 'PT0S' != departure['Delay']:
      outputline += ' ' + str(departure['Delay']).ljust(10)

    print(outputline)


if __name__ == '__main__':
  stopname=''
  limitresults=20
  localxml=None
  output=[]
  line_number=None
  platform_number=None
  stopid = None

  args = sys.argv[1:]

  if '-h' in args:
    usage()

  if '-v' in args:
    verbose = True
    args.pop(args.index('-v'))
    print(args)

  if '-n' in args:
    limitresults = int(args[ args.index('-n')+1 ])
    args.pop(args.index('-n')+1)
    args.pop(args.index('-n'))
    if verbose:
      print("limitresults", limitresults)
      print(args, stopname)

  if '-l' in args:
    line_number = args[ args.index('-l')+1 ]
    args.pop(args.index('-l')+1)
    args.pop(args.index('-l'))
    if verbose:
      print("line_number", line_number)

  if '-p' in args:
    platform_number = args[ args.index('-p')+1 ]
    args.pop(args.index('-p')+1)
    args.pop(args.index('-p'))
    if verbose:
      print("platform_number", platform_number)

  if '-d' in args:
    localxml = 'ruter.temp'
    args.pop(args.index('-l'))

  if len(args) < 1:
    usage()
  else:
    stopname = ''.join(args[0:])

  stopid = get_stopid(stopname)
  departures = get_departures(stopid, localxml)
  print_departures(departures, platform_number, limitresults, line_number)  

  sys.exit(0)
