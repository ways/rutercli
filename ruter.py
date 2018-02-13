#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2018 Lars Falk-Petersen <dev@falkp.no>.
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

system_version = '0.9'
system_name = 'ruter.py'

from tabulate import tabulate
from colors import line_color, colored
from colorama import init, Fore, Style
init()

import sys
import datetime
import time
import urllib.request
import urllib.error
import re
import os.path
import xml.etree.ElementTree as ET

TransportationType = {
    'bus':   '🚌',
    'ferry': '⛴',
    'rail':  '🚆',
    'tram':  '🚋',
    'metro': '🚃',  # 🚇 Ⓣ
}

TransportationTypeAscii = {
    'bus':   'B',
    'ferry': 'F',
    'rail':  'R',
    'tram':  'T',
    'metro': 'M',
}

apiurl = 'https://reisapi.ruter.no/stopvisit/getdepartures/'
schema = '{http://schemas.datacontract.org/2004/07/Ruter.Reis.Api.Models}'
stopsfile = '/tmp/GetStopsRuter.xml'
stopsurl = 'http://reisapi.ruter.no/Place/GetStopsRuter'

verbose = False
ascii = False
deviations = True
journey = False
html = False
limitresults = 7
line_number = None
platform_prefix = None
show_colors = True

class columns:
    LINE = 'Linje'
    DESTINATION = 'Destinasjon'
    PLATFORM = 'Plattform'
    OCCUPANCY = 'Full'
    TIME = 'Tid (forsink.)'
    JOURNEY = 'Turnummer'
    DEVIATION = 'Avvik'

    order = [ LINE, DESTINATION, PLATFORM, OCCUPANCY, TIME, JOURNEY, DEVIATION ]

def usage():
    print('Bruk: %s [-a] [-l] [-n] [-v] <stasjonsnavn|stasjonsid>' % sys.argv[0])
    print('''
    -h       Vis denne hjelpen.

    -a       Ikke bruk Unicode symboler/ikoner, kun tekst.
    -c       Deaktiver linjefarger.
    -d       Ikke vis avvik.
    -j       Vis turnummer.
    -l       Begrens treff til kun linje-nummer (kommaseparert).
    -n       Begrens treff pr. platform, tilbakefall er %s.
    -p       Begrens treff til platform-navn (prefix).
    -w       Skriv ut HTML.
    -t       Bruk lokal fil ruter.temp som xml-kilde (kun for utvikling).
    -v       Verbose for utfyllende informasjon.
    ''' % limitresults)

    for icon in TransportationType:
        print (icon, TransportationType[icon])

    print(system_name, colored(Fore.BLUE, 'version'), system_version)
    sys.exit(1)


""" Check if stopsfile exists, download if necessary.
    Read stopsfile, search for stop, return matches as dict """


def fetch_stops(name_needle, filename='/tmp/GetStopsRuter.xml'):
    name_needle = name_needle.lower()
    results = {}
    start = time.time()
    status = None

    if not os.path.isfile(filename):
        if verbose:
            print("Oversikt over stop mangler (%s), laster ned... " % filename, end="")
        request = urllib.request.Request(stopsurl, headers={"Accept": 'application/xml'})
        with urllib.request.urlopen(request, timeout=10) as response, open(filename, 'wb') as out_file:
            data = response.read() #  a `bytes` object
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
            status = 1
            break

        if re.match(
            name_needle.replace(' ', '').replace('(', '').replace(')', '').replace('-', '') + '*',
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

    status = len(results)

    if verbose:
        print("Results: ", status)
        print(results)

    return results, status


""" Fetch xml file from url, return string """


def fetch_api_xml(url):
    html = None
    api_latency = None

    start = time.time()
    try:
        if verbose:
            print("fetch_api_xml", url)

        request = urllib.request.Request(url, headers={"Accept": 'application/xml'})
        html = urllib.request.urlopen(request, timeout=10).read()
    except urllib.error.HTTPError as error:
        print(url, error)
    except:
        print("Fikk ikke tak i ruter.no, prøv igjen.")
        sys.exit(1)

    stop = time.time()
    api_latency = stop-start

    if verbose:
        print("Data fetched in %0.3f s" % api_latency)
    return html, api_latency


def parse_xml(xml, filename):
    if None == xml:
        tree = ET.parse(filename).getroot()
    else:  # None == filename
        tree = ET.fromstring(xml)
    return tree


def get_stopid(stopname):
    status = None
    messages = ''
    stopid = None

    if verbose:
        print("stopname", stopname)

    ''' Check if we have number or name '''
    if not stopname.isdigit():
        if verbose:
            print("Looking up stopname.")
        stops, stops_status = fetch_stops(stopname)

        if len(stops) > 1:
            messages += "Flere treff, angi mer nøyaktig:\n"
            status = 3
            for key in stops:
                messages += "[%d] \"%s\" \n" % (stops[key], key)
        elif 0 == len(stops):
            messages += "Ingen treff på stoppnavn."
            status = 4
        else:
            selected_stop = list(stops.keys())[0]
            stopid = stops[selected_stop]
            messages += "Avganger fra %s, oppdatert %s\n" \
                % (selected_stop, colored(Style.BRIGHT, datetime.datetime.now().strftime("%H:%M")))
            status = 0

    else:
        if verbose:
            print("Looking up stopid.")
        status = 0
        stopid = stopname

    return stopid, status, messages


def get_departures(stopid, localxml=None):
    departures = []
    api_latency = None

    xmlroot = None
    if localxml:
        xmlroot = parse_xml(None, localxml)
    else:
        xml, api_latency = fetch_api_xml(apiurl + str(stopid))
        xmlroot = parse_xml(xml, None)

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
        try:
            if 'true' == MonitoredStopVisit.find(schema + 'Extensions').find(schema + 'OccupancyData').find(schema + 'OccupancyAvailable').text:
                departure['OccupancyPercentage'] = MonitoredStopVisit.find(schema + 'Extensions').find(schema + 'OccupancyData').find(schema + 'OccupancyPercentage').text
        except AttributeError:
            pass

        departure['LineColour'] = MonitoredStopVisit.find(schema + 'Extensions').find(schema + 'LineColour')

# TODO:
# Look up deviation info:
# sx/GetSituation/{situationNumber}
# http://sirisx.ruter.no/help
# i.e. http://sirisx.ruter.no/sx/GetSituation/42693

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

        # Journey name
        departure['VehicleJourneyName'] = MonitoredVehicleJourney.find(schema + 'VehicleJourneyName').text
        departures.append(departure)

    # Sort departures by platform name
    return sorted(departures, key=lambda k: k['DeparturePlatformName']), api_latency

# Example patterns:
# PT0S -PT140S PT6M0S

delay_pattern_s = re.compile("(-?)PT(\d+)S")
delay_pattern_ms = re.compile("(-?)PT(\d+)M(\d+)S")

def format_delay(delay):
    if not delay:
        return ""
    match_s = delay_pattern_s.match(delay)
    match_ms = delay_pattern_ms.match(delay)
    negative = False
    if match_s:
        seconds = int(match_s.group(2))
        negative = match_s.group(1) == '-'
    elif match_ms:
        seconds = 60*int(match_ms.group(2)) + int(match_ms.group(3))
        negative = match_ms.group(1) == '-'
    else:
        return ''
    m = s = 0
    if seconds != 0:
        m, s = divmod(seconds, 60)

    formatted = ' ('
    if negative:
        formatted += '-'
    if m != 0:
        formatted += '%sm' % m
    formatted += '%ss' % s
    formatted += ')'
    return formatted


''' Filter lines '''
def filter_departures(departures):
    filtered = []
    directions = {}

    for counter, departure in enumerate(departures):
        # Limit results by line_number
        if line_number:
            if departure['PublishedLineName'] not in line_number:
                continue

        # Limit results by platform_prefix
        if platform_prefix:
            if platform_prefix.endswith('$'):
                if departure['DeparturePlatformName'] != platform_prefix[:-1]:
                    continue
            elif not departure['DeparturePlatformName'].startswith(str(platform_prefix)):
                continue

        # Keep list of platforms with number of hits
        try:
            if departure['DeparturePlatformName'] not in directions.keys():
                directions[departure['DeparturePlatformName']] = 1
            else:
                directions[departure['DeparturePlatformName']] += 1
        except TypeError:
            pass

        # Limit hits by platform
        if directions[departure['DeparturePlatformName']] > limitresults:
            continue
        filtered.append(departure)
    return filtered


''' Format as table '''
def to_table(departures):
    result = []
    last_direction=None

    for counter, departure in enumerate(departures):
        row = {}
        # Add a blank entry when switching platforms
        if last_direction and last_direction != departure['DeparturePlatformName']:
            result.append({});
        last_direction=departure['DeparturePlatformName']

        ### Start formatting

        # Icon, double for long vehicles
        if ascii:
            symbol = TransportationTypeAscii[departure['VehicleMode']]
        else:
            symbol = TransportationType[departure['VehicleMode']]
        icon = '{:<2.2}'.format(symbol if departure['NumberOfBlockParts'] in [0,1,3] else symbol + symbol)
               # padding, truncate. https://pyformat.info/

        # TODO: pad/trunc line name
        line = departure['PublishedLineName']
        if show_colors:
            line = line_color(line)

        row[columns.LINE] = icon + line
        row[columns.DESTINATION] = departure['DestinationName']
        row[columns.PLATFORM] = departure['DeparturePlatformName']
        row[columns.OCCUPANCY] = '{:<3.3}%'.format(departure['OccupancyPercentage'].rjust(3)) if -1 < int(departure['OccupancyPercentage']) else None

        delay = format_delay(departure['Delay'])

        # Time as HH:MM[kø] if today
        if departure['AimedDepartureTime'].day == datetime.date.today().day:
            row[columns.TIME] = departure['AimedDepartureTime'].strftime("%H:%M") + \
                          ('kø' if 'true' == departure['InCongestion'] else '') + \
                          delay
        else:
            row[columns.TIME] = str(departure['AimedDepartureTime'])

        # Journey
        if journey:
            row[columns.JOURNEY] = str(departure['VehicleJourneyName'])

        # Deviations
        if deviations:
            deviation_formatted = ''
            for deviation in departure['Deviations']:
                deviation_formatted += "(%s) %s " % (deviation, departure['Deviations'][deviation])
            if '' == deviation_formatted:
                deviation_formatted = None
            row[columns.DEVIATION] = deviation_formatted

        # Done
        result.append(row)
    return result

''' Order columns according to columns.order '''
def order_columns(rows):
    # Find all columns with values
    all = [c for r in rows for c in r if r[c] != None]
    keys = [c for c in columns.order if c in all]

    ordered = []
    ordered.append(keys)
    # Retrieve column from each row
    for r in rows:
        ordered.append([r.get(k, None) or '' for k in keys])
    return ordered

if __name__ == '__main__':
    stopname=''
    localxml=None
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
        line_number = args[ args.index('-l')+1 ].split(",")
        args.pop(args.index('-l')+1)
        args.pop(args.index('-l'))
        if verbose:
            print("line_number", line_number)

    if '-p' in args:
        platform_prefix = args[ args.index('-p')+1 ]
        args.pop(args.index('-p')+1)
        args.pop(args.index('-p'))
        if verbose:
            print("platform_prefix", platform_prefix)

    if '-P' in args:
        platform_width = int(args[ args.index('-P')+1 ])
        args.pop(args.index('-P')+1)
        args.pop(args.index('-P'))
        if verbose:
            print("platform_width", platform_width)

    if '-t' in args:
        localxml = 'ruter.temp'
        args.pop(args.index('-t'))

    if '-d' in args:
        deviations = False
        args.pop(args.index('-d'))

    if '-j' in args:
        journey = True
        args.pop(args.index('-j'))

    if '-a' in args:
        ascii = True
        args.pop(args.index('-a'))

    if '-c' in args:
        show_colors = False
        args.pop(args.index('-c'))

    if '-w' in args:
        html = True
        args.pop(args.index('-w'))

    if len(args) < 1:
        usage()
    else:
        stopname = ''.join(args[0:])

    format = 'simple'
    if html:
        format = 'html'
        show_colors = False
        ascii = True

    stopid, stopid_status, messages = get_stopid(stopname)
    print (messages)
    if 0 < stopid_status:
        sys.exit(stopid_status)

    departures, api_latency = get_departures(stopid, localxml)
    departures = filter_departures(departures)
    print (tabulate(order_columns(to_table(departures)), headers="firstrow", tablefmt=format))
    latency_string = 'Waited %0.3f s for ruter.no to respond' % api_latency
    if not html:
        print(latency_string)
    else:
        print ("<small>" + latency_string + "</small>")

    sys.exit(0)
