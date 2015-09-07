Example run of alpha:

wget --header "Accept: application/xml" https://reisapi.ruter.no/stopvisit/getdepartures/3010407 -O ruter.temp

./ruter.py -l -v 3010407
['-l', '3010407']
stopname 3010407
Looking up stopid.
Linje/Destinasjon        Spor Tid             Type Forsinkelse
 28 Fornebu              2    15:09:00        🚌    [PT35S]
345 Vardefjellet         2    15:12:00        🚌    [PT137S]
 28 Fornebu              2    15:19:00        🚌    [PT79S]
435 John Colletts plass  1    15:21:00        🚌    [PT247S]
 28 Fornebu              2    15:29:00        🚌
363 Guldhaug-Tømte       2    15:30:00        🚌
 28 Helsfyr T            1    15:30:00        🚌
363 John Colletts plass  1    15:31:00        🚌    [PT225S]
 28 Fornebu              2    15:39:00        🚌
 28 Helsfyr T            1    15:40:00        🚌
345 Vardefjellet         2    15:42:00        🚌
 28 Fornebu              2    15:49:00        🚌
 28 Helsfyr T            1    15:50:00        🚌
435 John Colletts plass  1    15:51:00        🚌
 28 Fornebu              2    15:59:00        🚌
363 Guldhaug-Tømte       2    16:00:00        🚌
 28 Helsfyr T            1    16:00:00        🚌
363 John Colletts plass  1    16:01:00        🚌    [PT125S]

