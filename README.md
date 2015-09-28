A python3 client for ruter.no, made using the API at http://labs.ruter.no/

GNU AFFERO GENERAL PUBLIC LICENSE

Example run of beta 0.4:


Direct hit:

```
$ ./ruter.py lijordet
Avganger fra lijordet, oppdatert 22:15
Linje/Destinasjon             Platform Tid           Type Forsinkelse
  5 Vestli                    1        22:19:59      Ⓣ
  5 Vestli                    1        22:34:59      Ⓣ
  5 Vestli                    1        22:49:59      Ⓣ
```

Long name:

```
./ruter.py "borgen (i sørkedalsveien)"
Avganger fra borgen (i sørkedalsveien), oppdatert 22:15
Linje/Destinasjon             Platform Tid           Type Forsinkelse
 45 Majorstuen                1        22:18:00      🚌
 45 Majorstuen                1        22:48:00      🚌
 45 Voksen skog               2        22:34:00      🚌
```

Several hits:

```
$ ./ruter.py majorstuen
Flere treff, angi mer nøyaktig:
[3010203] majorstuen (i valkyriegata)
[3010200] majorstuen [t-bane]
[3010201] majorstuen (i kirkeveien)
[3010202] majorstuen (i sørkedalsveien)
```

Refined search:

```
./ruter.py vøyenbrua -l 28 -p 2
Avganger fra vøyenbrua, oppdatert 15:45
Linje/Destinasjon             Platform Tid           Type Forsinkelse
 28 Fornebu                   2        15:49:00      🚌    PT70S
 28 Fornebu                   2        15:59:00      🚌
 28 Fornebu                   2        16:09:00      🚌
 28 Fornebu                   2        16:19:00      🚌
 28 Fornebu                   2        16:29:00      🚌
 28 Fornebu                   2        16:39:00      🚌
```

TODO:
* Colors for lines
* Show deviations
* One-line interface for status bar
* Decode delay data
* Check if any vehicles support estimated load data yet
* None-unicode mode
* Set up as finger/web service?
* Split core functions to a library.

One-liner sketches:
./ruter.py vøyenbrua -l 28 -p 2
🚌 28 Fornebu fra vøyenbrua 15:49 (1 min)  15:59 (Kø, 11 min)  16:09 (21 min.)
