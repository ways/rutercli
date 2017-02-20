TODO:
* Selectable path for stopsfile
* One-line interface for status bar
* Split core functions to a library?
* Improve webUI.
* Show full description of delays (avvik).
* Make "time waiting for ruter" optional.
* Separate icon for flybuss?
* Update README with fresh examples and screenshots.
* Document good fonts for unicode icons.

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
