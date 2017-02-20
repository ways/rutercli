#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2017 Lars Falk-Petersen <dev@falkp.no>.
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

system_version = '0.8'
system_name = 'ruter.py'

from tabulate import tabulate

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

# Define terminal colors
txtblk='\033[0;30m' # Black - Regular
txtred='\033[0;31m' # Red
txtgrn='\033[0;32m' # Green
txtylw='\033[0;33m' # Yellow
txtblu='\033[0;34m' # Blue
txtpur='\033[0;35m' # Purple
txtcyn='\033[0;36m' # Cyan
txtwht='\033[0;37m' # White
bldblk='\033[1;30m' # Black - Bold
bldred='\033[1;31m' # Red
bldgrn='\033[1;32m' # Green
bldylw='\033[1;33m' # Yellow
bldblu='\033[1;34m' # Blue
bldpur='\033[1;35m' # Purple
bldcyn='\033[1;36m' # Cyan
bldwht='\033[1;37m' # White
unkblk='\033[4;30m' # Black - Underline
undred='\033[4;31m' # Red
undgrn='\033[4;32m' # Green
undylw='\033[4;33m' # Yellow
undblu='\033[4;34m' # Blue
undpur='\033[4;35m' # Purple
undcyn='\033[4;36m' # Cyan
undwht='\033[4;37m' # White
bakblk='\033[40m'   # Black - Background
bakred='\033[41m'   # Red
bakgrn='\033[42m'   # Green
bakylw='\033[43m' #'\033[43m'   # Yellow
bakblu='\033[44m'   # Blue
bakpur='\033[45m'   # Purple
bakcyn='\033[46m'   # Cyan
bakwht='\033[47m'   # White
txtrst='\033[0m'    # Text Reset

apiurl = 'https://reisapi.ruter.no/stopvisit/getdepartures/'
schema = '{http://schemas.datacontract.org/2004/07/Ruter.Reis.Api.Models}'
stopsfile = '/tmp/GetStopsRuter.xml'
stopsurl = 'http://reisapi.ruter.no/Place/GetStopsRuter'
verbose = False
ascii = False
deviations = True
journey = False


def usage(limitresults=5):
    print('Bruk: %s [-a] [-l] [-n] [-v] <stasjonsnavn|stasjonsid>' % sys.argv[0])
    print('''
    -h       Vis denne hjelpen.

    -a       Ikke bruk Unicode symboler/ikoner, kun tekst.
    -c       Deaktiver linjefarger.
    -d       Ikke vis avvik.
    -j       Vis turnummer.
    -l       Begrens treff til kun linje-nummer (kommaseparert).
    -n       Begrens treff pr. platform, tilbakefall er %s.
    -o       En-linje-visning.
    -p       Begrens treff til platform-navn (prefix).
    -P       Lenge på platformnavn (fra 0 og opp)
    -t       Bruk lokal fil ruter.temp som xml-kilde (kun for utvikling).
    -v       Verbose for utfyllende informasjon.
    ''' % limitresults)

    for icon in TransportationType:
        print (icon, TransportationType[icon])

    print(system_name, txtblu + 'version' + txtrst, system_version)
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
                % (selected_stop, bldwht + datetime.datetime.now().strftime("%H:%M") + txtrst)
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

def colormap(line):
    # Map ruter line numbers to terminal safe colors
    if '1' == line:
        return bakcyn
    elif line in ['2', '18', '19', '33', '51', '60']:
        return bakylw
    elif line in ['3', '12', '34']:
        return bakpur
    elif line in ['4', '21', '54', '56', '70']:
        return bakblu
    elif line in ['5', '11', '13', '30', '58']:
        return bakgrn
    elif line in ['17', '20', '28', '37']:
        return bakred
    else:
        return txtwht

''' Prepare main output '''
def format_departures(departures, deviations, journey, limitresults=7,
    platform_prefix = None, line_number=None, api_latency=None):

    if verbose:
        print(departures[0])

    # Header
    output="Linje/Destinasjon                 %s Full Tid (forsink.)" \
        % ( '{0:{fill}{align}{width}}'.format('Platform           '[:platform_width],
        fill=' ', align='<', width=platform_width) )

    if journey:
        output+= " Turnummer   "
    if deviations:
        output+= " Avvik"
    output+="\n"
    directions={}
    last_direction=None

    for counter, departure in enumerate(departures):
        outputline=''

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

        # Add a newline when switching platforms
        if last_direction and last_direction != departure['DeparturePlatformName']:
            output += "\n"
        last_direction=departure['DeparturePlatformName']

        ### Start outputting

        # Icon, double for long vehicles
        icon = '{:<4.4}'.format(
            (TransportationTypeAscii[departure['VehicleMode']]
              if departure['NumberOfBlockParts'] in [0,1,3]
              else TransportationTypeAscii[departure['VehicleMode']] + TransportationTypeAscii[departure['VehicleMode']] ))
        if not ascii:
            icon = '{0:{fill}{align}{width}}'.format(
              (TransportationType[departure['VehicleMode']] + '  '
                if departure['NumberOfBlockParts'] in [0,1,3]
                else TransportationType[departure['VehicleMode']] + TransportationType[departure['VehicleMode']] ), fill='X', align='<', width=2)

        line_name = departure['PublishedLineName']
        if showColors:
            line_name = "%s%s %s %s" % (txtblk, colormap(line_name), departure['PublishedLineName'], txtrst)

        outputline += "%s%s %s %s " % (
          icon, # Icon for type of transportation
          line_name, # Line number, name
          txtrst,
          '{:<24.24}'.format(departure['DestinationName'])
        )

        # platform_width
        outputline += "%s" % ('{0:{fill}{align}{width}}'.format(departure['DeparturePlatformName'][:platform_width], fill=' ', align='<', width=platform_width))

        # Occupancy
        outputline += '{:<3.3}%  '.format(departure['OccupancyPercentage'].rjust(3)) if -1 < int(departure['OccupancyPercentage']) else '  -   '

        delay = format_delay(departure['Delay'])

        # Time as HH:MM[kø] if today
        if departure['AimedDepartureTime'].day == datetime.date.today().day:
            outputline += '{:<15.15}'.format(departure['AimedDepartureTime'].strftime("%H:%M") + \
                          delay +
                          ('kø' if 'true' == departure['InCongestion'] else ''))
        else:
            outputline += "%s" % str(departure['AimedDepartureTime']).ljust(17)

        # Journey
        if journey:
            outputline += "%s" % str(departure['VehicleJourneyName']).ljust(13)

        # Deviations
        deviation_formatted = ''
        if deviations:
            for deviation in departure['Deviations']:
                deviation_formatted += "(%s) %s " % (deviation, departure['Deviations'][deviation])
            if '' == deviation_formatted:
                deviation_formatted = '-'

# TODO:
# Look up deviation info:
# sx/GetSituation/{situationNumber}
# http://sirisx.ruter.no/help
# i.e. http://sirisx.ruter.no/sx/GetSituation/42693

        # Done
        output += outputline + deviation_formatted + "\n"
    return output


''' html formatting (ignoring ascii here) '''
def htmlformat_departures(departures, deviations, journey, limitresults=7,
    platform_prefix=None, line_number=None, api_latency=None):
    if verbose:
        print(departures[0])
    output="<table><tr><th>Linje</th><th>Destinasjon</th><th>Platform</th><th>Full</th><th>Tid (forsinkelse)</th>"
    if journey:
        output+="<th>Turnummer</th>"
    if deviations:
        output+="<th>Avvik</th>"
    output+="</tr>"

    directions={}

    for counter, departure in enumerate(departures):
        outputline=''

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
        #try:
        if directions[departure['DeparturePlatformName']] > limitresults:
            outputline += '<tr></tr>';
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

        delay = format_delay(departure['Delay'])

        # Time as HH:MM[kø] if today
        if departure['AimedDepartureTime'].day == datetime.date.today().day:
            outputline += "<td>%s</td>" % ( str(departure['AimedDepartureTime'].strftime("%H:%M")) + \
                ('kø' if 'true' == departure['InCongestion'] else '') + \
                delay)
        else:
            outputline += "<td>%s</td>" % str(departure['AimedDepartureTime']).ljust(17)

        # Journey
        if journey:
            outputline += "<td>%s</td>" % str(departure['VehicleJourneyName']).ljust(13)

        # Deviations
        deviation_formatted = ''
        if deviations:
            for deviation in departure['Deviations']:
                deviation_formatted += "(%s) %s " % (deviation, departure['Deviations'][deviation])
            if '' == deviation_formatted:
                deviation_formatted = '-'

        # Done
        output += outputline + '<td>' + deviation_formatted + '</td></tr>'

    output += "</table> <br/><br/> <small>Waited %0.3f s for ruter.no to respond.</small>" % api_latency
    return output


if __name__ == '__main__':
    stopname=''
    limitresults=7
    localxml=None
    output=[]
    line_number=None
    platform_prefix=None
    platform_width = 19
    stopid = None
    api_latency = None
    showColors = True

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
        showColors = False
        args.pop(args.index('-c'))

    if len(args) < 1:
        usage(limitresults)
    else:
        stopname = ''.join(args[0:])

    stopid, stopid_status, messages = get_stopid(stopname)
    print (messages)
    if 0 < stopid_status:
        sys.exit(stopid_status)

    departures, api_latency = get_departures(stopid, localxml)
    print (format_departures(departures, deviations, journey, limitresults, platform_prefix, line_number, api_latency))
    print ('Waited %0.3f s for ruter.no to respond' % api_latency)

    sys.exit(0)
