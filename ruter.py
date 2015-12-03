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

system_version = '0.6'
system_name = 'ruter.py'

import sys, datetime, time, urllib.request, urllib.error, re, os.path
import xml.etree.ElementTree as ET

TransportationType = {
  'bus':   '🚌',
  'ferry': '⛴',
  'rail':  '🚆',
  'tram':  '🚋',
  'metro': '🚃' , #🚇 Ⓣ
}

TransportationTypeAscii = {
  'bus':   'B',
  'ferry': 'F',
  'rail':  'R',
  'tram':  'T',
  'metro': 'M',
}

# html to terminal safe colors
#TODO: colors!
color_codes = {
  'F07800': 'orange',
}

apiurl='https://reisapi.ruter.no/stopvisit/getdepartures/'
schema='{http://schemas.datacontract.org/2004/07/Ruter.Reis.Api.Models}'
stopsfile='/tmp/GetStopsRuter.xml'
stopsurl='http://reisapi.ruter.no/Place/GetStopsRuter'
verbose=False
ascii=False
deviations=True

def usage(limitresults = 5):
  print('Bruk: %s [-a] [-l] [-n] [-v] <stasjonsnavn|stasjonsid>' % sys.argv[0])
  print('''
  -h       Vis denne hjelpen.

  -a       ASCII for ikke å bruke Unicode symboler/ikoner.
  -d       Ikke vis avvik.
  -l       Begrens treff til kun linje-nummer.
  -n       Begrens treff pr. platform, tilbakefall er %s.
  -o       En-linje-visning.
  -p       Begrens treff til platform-nummer.
  -t       Bruk lokal fil ruter.temp som xml-kilde (kun for utvikling).
  -v       Verbose for utfyllende informasjon.
  ''' % limitresults)

  for icon in TransportationType:
    print (icon, TransportationType[icon])

  for color_code in color_codes:
    print (color_code, color_codes[color_code])

  print(system_name, 'version', system_version)
  sys.exit(1)


""" Check if stopsfile exists, download if necessary.
    Read stopsfile, search for stop, return matches as dict """
def fetch_stops(name_needle, filename = '/tmp/GetStopsRuter.xml'):
  name_needle = name_needle.lower()
  results = {}
  start = time.time()
  status=None

  if not os.path.isfile(filename):
    if verbose:
      print("Oversikt over stop mangler (%s), laster ned... " % filename, end="")
    request = urllib.request.Request(stopsurl, headers={"Accept" : 'application/xml'})
    with urllib.request.urlopen(request, timeout=10) as response, open(filename, 'wb') as out_file:
      data = response.read() # a `bytes` object
      out_file.write(data)
    if verbose:
      print("ferdig.")

  if verbose:
    print("Parsing stopsfile", filename)

  try:
    root = ET.parse(filename)
  except ET.ParseError as error:
    print("Error loading stopsfile")

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
      results.clear()
      results[stopname] = stopid
      status=1
      break

    if re.match(
      name_needle.replace(' ', '').replace('(', '').replace(')', '').replace('-','') + '*',
      stopname):
      if verbose:
        print("Hit: %d - %s" % (stopid, stopname))
      results[stopname] = stopid

    # Print progress every 1k stops
    if verbose and counter % 1000 == 0:
      print("Reading stops...", counter)
      print("%d - %s %s" % (stopid, stopname.lower(), name_needle))

  stop = time.time()
  if verbose:
    print("File searched names in %0.3f ms" % (stop-start))

  status=len(results)

  if verbose:
    print("Results: ", status)
    print(results)

  return results, status


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
  status=None
  messages=''
  stopid=None

  if verbose:
    print("stopname", stopname)

  ''' Check if we have number or name '''
  if not stopname.isdigit():
    if verbose:
      print("Looking up stopname.")
    stops, stops_status = fetch_stops(stopname)

    if len(stops) > 1:
      messages+="Flere treff, angi mer nøyaktig:\n"
      status=3
      for key in stops:
        messages+="[%d] \"%s\" \n" % (stops[key], key)
    elif 0 == len(stops):
      messages+="Ingen treff på stoppnavn."
      status=4
    else:
      selected_stop = list(stops.keys())[0]
      stopid = stops[selected_stop]
      messages+="Avganger fra %s, oppdatert %s" \
      % (selected_stop, datetime.datetime.now().strftime("%H:%M"))
      status=0

  else:
    if verbose:
      print("Looking up stopid.")
    stopid = stopname

  return stopid, status, messages


def get_departures (stopid, localxml=None):
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

    departure['OccupancyPercentage'] = -1
    if 'true' == MonitoredStopVisit.find(schema + 'Extensions').find(schema + 'OccupancyData').find(schema + 'OccupancyAvailable').text:
      departure['OccupancyPercentage'] = MonitoredStopVisit.find(schema + 'Extensions').find(schema + 'OccupancyData').find(schema + 'OccupancyPercentage').text

    departure['LineColour'] = MonitoredStopVisit.find(schema + 'Extensions').find(schema + 'LineColour')
    departure['Deviations'] = {}
    for deviation in MonitoredStopVisit.find(schema + 'Extensions').find(schema + 'Deviations').getchildren(): #id, header
      departure['Deviations'][deviation.find(schema + 'ID').text] = deviation.find(schema + 'Header').text
    
    # Lenght of vehicle
    departure['NumberOfBlockParts'] = 0
    try:
      departure['NumberOfBlockParts'] = MonitoredVehicleJourney.find(schema + 'TrainBlockPart').find(schema + 'NumberOfBlockParts').text
      if verbose:
        print (NumberOfBlockParts, departure['NumberOfBlockParts'])
    except AttributeError:
      pass
    except NameError:
      pass

    departures.append(departure)

  # Sort departures by platform name
  return sorted(departures, key=lambda k: k['DeparturePlatformName'])


''' Prepare main output '''
def format_departures(departures, limitresults=7, platform_number=None, line_number=None):
  if verbose:
    print(departures[0])
  output="Linje/Destinasjon                 Platform            Full  Tid (forsink.) Avvik\n"
  directions={}

  for counter, departure in enumerate(departures):
    outputline=''

    # Limit results by line_number
    if line_number:
      if str(line_number) != departure['PublishedLineName']:
        continue

    # Limit results by platform_number
    if platform_number:
      if str(platform_number) != departure['DeparturePlatformName']:
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

    # Icon, double for long vehicles
    icon = '{:<4.4}'.format(
        (TransportationTypeAscii[departure['VehicleMode']]
          if departure['NumberOfBlockParts'] in [0,1,3]
          else TransportationTypeAscii[departure['VehicleMode']] + ' ' + TransportationTypeAscii[departure['VehicleMode']] ))
    if not ascii:
      icon = '{:<4.4}'.format( 
        (TransportationType[departure['VehicleMode']]
          if departure['NumberOfBlockParts'] in [0,1,3]
          else TransportationType[departure['VehicleMode']] + ' ' + TransportationType[departure['VehicleMode']] ))

    outputline += "%s %s %s %s " % (
      icon, # Icon for type of transportation
      '{:<3.3}'.format(departure['PublishedLineName'].rjust(3)), # Line number, name, platform
      '{:<24.24}'.format(departure['DestinationName']),
      '{:<19.19}'.format(departure['DeparturePlatformName'])
    )

    # Occupancy
    outputline += '{:<3.3}%  '.format(departure['OccupancyPercentage'].rjust(3)) if -1 < int(departure['OccupancyPercentage']) else '  -   '

    # Delay as hour+/-delay_in_minutes
    delay = ''
    if departure['Delay'] and 'PT0S' != departure['Delay']:
      if '+' in departure['Delay']:
        delay = ' (+' + departure['Delay'][3:-1] + 's)'
      elif '-' in departure['Delay']:
        delay = ' (-' + departure['Delay'][3:-1] + 's)'

    # Time as HH:MM[kø] if today
    if departure['AimedDepartureTime'].day == datetime.date.today().day:
      outputline += '{:<15.15}'.format(departure['AimedDepartureTime'].strftime("%H:%M") + \
                    delay + \
                    ('kø' if 'true' == departure['InCongestion'] else ''))
    else:
      outputline += "%s" % str(departure['AimedDepartureTime']).ljust(17)

    # Deviations
    deviation_formatted = ''
    for deviation in departure['Deviations']:
      deviation_formatted += "(%s) %s " % (deviation, departure['Deviations'][deviation])
    if '' == deviation_formatted:
      deviation_formatted = '-'

    # Done
    if not ascii:
      output += outputline + deviation_formatted + "\n"
    else: #TODO: Ugly hack to not care about encoding problems on various platforms yet.
      output += str(outputline.encode('ascii','ignore')) + "\n"

  return output


''' html formatting (ignoring ascii here) '''
def htmlformat_departures(departures, limitresults=7, platform_number=None, line_number=None):
  if verbose:
    print(departures[0])
  output="<table><tr><th>Linje</th><th>Destinasjon</th><th>Platform</th><th>Full</th><th>Tid</th><th>Forsinkelse</th><th>Avvik</th></tr>"
  directions={}

  for counter, departure in enumerate(departures):
    outputline=''

    # Limit results by line_number
    if line_number:
      if str(line_number) != departure['PublishedLineName']:
        continue

    # Limit results by platform_number
    if platform_number:
      if str(platform_number) != departure['DeparturePlatformName']:
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

    # Icon, double for long vehicles
    icon = '{:<4.4}'.format( 
      (TransportationType[departure['VehicleMode']]
        if departure['NumberOfBlockParts'] in [0,1,3]
        else TransportationType[departure['VehicleMode']] + ' ' + TransportationType[departure['VehicleMode']] ))

    outputline += "<tr><td>%s %s</td><td>%s</td><td>%s</td>" % (
    # Icon for type of transportation
      icon, 
    # Line number, name, platform
      '{:<3.3}'.format(departure['PublishedLineName'].rjust(3)),
      '{:<24.24}'.format(departure['DestinationName']),
      '{:<19.19}'.format(departure['DeparturePlatformName'])
    )

    # Occupancy
    outputline += '<td>{:<3.3}%</td>'.format(departure['OccupancyPercentage'].rjust(3)) if -1 < int(departure['OccupancyPercentage']) else '<td>-</td>'

    # Time as HH:MM[kø] if today
    if departure['AimedDepartureTime'].day == datetime.date.today().day:
      outputline += "<td>%s</td>" % ( str(departure['AimedDepartureTime'].strftime("%H:%M")) + ('kø' if 'true' == departure['InCongestion'] else '') )
    else:
      outputline += "<td>%s</td>" % str(departure['AimedDepartureTime']).ljust(17)

    # Delay
    outputline += '<td>{:<12.12}</td>'.format(
      ( departure['Delay'] if (departure['Delay'] and 'PT0S' != departure['Delay']) else '-' )
    )

    # Deviations
    deviation_formatted = ''
    for deviation in departure['Deviations']:
      deviation_formatted += "(%s) %s " % (deviation, departure['Deviations'][deviation])
    if '' == deviation_formatted:
      deviation_formatted = '-'

    # Done
    output += outputline + '<td>' + deviation_formatted + '</td></tr>'

  return output + '</table>'



if __name__ == '__main__':
  stopname=''
  limitresults=7
  localxml=None
  output=[]
  line_number=None
  platform_number=None
  stopid = None

  args = sys.argv[1:]

  if '-h' in args:
    usage(limitresults)

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

  if '-a' in args:
    ascii = True
    args.pop(args.index('-a'))

  if len(args) < 1:
    usage(limitresults)
  else:
    stopname = ''.join(args[0:])

  stopid, stopid_status, messages = get_stopid(stopname)
  print (messages)
  if 0 < stopid_status:
    sys.exit(stopid_status)

  departures = get_departures(stopid, localxml)
  print (format_departures(departures, limitresults, platform_number, line_number))

  sys.exit(0)
