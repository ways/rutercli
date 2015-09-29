A python3 client for ruter.no, made using the API at http://labs.ruter.no/

GNU AFFERO GENERAL PUBLIC LICENSE

Example run of beta 0.5:


Direct hit:

```
./ruter.py lijordet -n 2
Avganger fra lijordet, oppdatert 11:14
Linje/Destinasjon             Platform            Tid    Forsinkelse
Ⓣ  5 Vestli                   1 (Retning sentrum) 11:19
Ⓣ  5 Vestli                   1 (Retning sentrum) 11:29
Ⓣ  5 Østerås                  2 (Retning Østerås) 11:13   PT177S
Ⓣ  5 Østerås                  2 (Retning Østerås) 11:22   PT46S
```

Long name:

```
./ruter.py "majorstuen (i kirkeveien)" -n 1
Avganger fra majorstuen (i kirkeveien), oppdatert 11:21
Linje/Destinasjon             Platform            Tid    Forsinkelse
🚌 20 Galgeberg                1                   11:24   PT173S
🚋 19 Ljabru                   11                  11:30
🚋 12 Disen                    12                  11:30
🚋 11 Kjelsås                  14                  11:24
🚌 20 Skøyen                   2                   11:17   PT382S
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
./ruter.py vøyenbrua -l 28 -p 2 -n 2
Avganger fra vøyenbrua, oppdatert 11:21
Linje/Destinasjon             Platform            Tid    Forsinkelse
🚌 28 Fornebu                  2                   14:39
🚌 28 Fornebu                  2                   14:49
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
```
./ruter.py vøyenbrua -l 28 -p 2
🚌 28 Fornebu fra vøyenbrua 15:49 (1 min)  15:59 (Kø, 11 min)  16:09 (21 min.)
```
