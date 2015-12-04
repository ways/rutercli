A python3 client for ruter.no, made using the API at http://labs.ruter.no/

GNU AFFERO GENERAL PUBLIC LICENSE

Example run of beta 0.6:


Direct hit:

```
./ruter.py lijordet -n 2
Avganger fra lijordet, oppdatert 19:31
Linje/Destinasjon                 Platform            Full  Tid (forsink.) Avvik
🚃 🚃    5 Vestli                   1 (Retning sentrum)   -   19:34          -
🚃 🚃    5 Vestli                   1 (Retning sentrum)   -   19:49          -
🚃 🚃    5 Østerås                  2 (Retning Østerås)   -   19:37 (+53s)   -
🚃 🚃    5 Østerås                  2 (Retning Østerås)   -   19:52 (+44s)   -
```

Long name:

```
./ruter.py "majorstuen (i kirkeveien)" -n 1
Avganger fra majorstuen (i kirkeveien), oppdatert 12:22
Linje/Destinasjon                 Platform            Full  Tid     Forsinkelse Avvik
🚌     20 Galgeberg                1                     -   12:24   PT326S      (33526) Buss 20: Vi tester fleksible rutetider 
🚋     19 Ljabru                   11                    -   12:30   -           (31273) Trikk 18/19: Regn med forsinkelser 
🚋     12 Disen                    12                    0%  12:30   -           (33420) Trikk 12: Omkjøring mellom Kongens gate og Solli retning Majorstuen 
🚋     11 Kjelsås                  14                    -   12:24   -           -
🚌     20 Skøyen                   2                    40%  12:25   PT120S      (33526) Buss 20: Vi tester fleksible rutetider 
```

Several hits:

```
$ ./ruter.py majorstuen
Flere treff, angi mer nøyaktig:
Flere treff, angi mer nøyaktig:
[3010201] "majorstuen (i kirkeveien)"
[3010200] "majorstuen [t-bane]"
[3010202] "majorstuen (i sørkedalsveien)"
[3010203] "majorstuen (i valkyriegata)"
```

Refined search:

```
./ruter.py "aker brygge [båt]" -l B10 -p 1 -n 2
Avganger fra aker brygge [båt], oppdatert 22:20
Linje/Destinasjon                 Platform            Full  Tid     Forsinkelse Avvik
🚌    B10 Nesoddtangen             1                     0%  22:45   -           -
⛴    B10 Nesoddtangen             1                     -   23:45   -           -
```

TODO:
* Selectable path for stopsfile
* Colors for lines
* One-line interface for status bar
* Split core functions to a library.
* Improve webUI.

SKETCHES:

One-liner:
```
./ruter.py vøyenbrua -o -l 28 -p 2
🚌 28 Fornebu fra vøyenbrua 15:49 (1 min)  15:59 (Kø, 11 min)  16:09 (21 min.)
```

Separated on platform:
```
./ruter.py lijordet -n 2
Avganger fra lijordet, oppdatert 12:21

Linje/Destinasjon                 Full  Tid     Forsinkelse Avvik

Platform 1 (Retning sentrum):
Ⓣ Ⓣ    5 Vestli                     -   12:34   -           -
Ⓣ Ⓣ    5 Vestli                     -   12:49   -           -

Platform 2 (Retning Østerås):
Ⓣ Ⓣ    5 Østerås                    -   12:22   PT136S      -
Ⓣ Ⓣ    5 Østerås                    -   12:37   PT117S      -
```

Merging all repeating data:
```
ruter.py lijordet 
Avganger fra lijordet, oppdatert 11:31

Linje/Destinasjon                 Platform
🚃 🚃    5 Vestli                   1 (Retning sentrum)
 Full  Tid     Forsinkelse Avvik
   -   11:34   -           -
   -   11:44   -           -
   -   11:49   -           -
   -   12:04   -           -

🚃 🚃    5 Vestli                   2 (Retning Østerås)
 Full  Tid     Forsinkelse Avvik
   -   11:34   -           -
   -   11:44   -           -
   -   11:49   -           -
   -   12:04   -           -
```

Minimal:
```
Avganger fra lijordet, oppdatert 11:31
Linje/Destinasjon                 Platform
🚃 🚃    5 Vestli                   1 (Retning sentrum)
  11:34   11:44+2   11:49    12:04
🚃 🚃    5 Østerås                  2 (Retning Østerås)
  11:34   11:44     11:49+1  12:04
```

Icon from https://materialdesignicons.com/