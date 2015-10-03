A python3 client for ruter.no, made using the API at http://labs.ruter.no/

GNU AFFERO GENERAL PUBLIC LICENSE

Example run of beta 0.5:


Direct hit:

```
./ruter.py lijordet -n 2
Avganger fra lijordet, oppdatert 12:21
Linje/Destinasjon                 Platform            Full  Tid     Forsinkelse Avvik
Ⓣ Ⓣ    5 Vestli                   1 (Retning sentrum)   -   12:34   -           -
Ⓣ Ⓣ    5 Vestli                   1 (Retning sentrum)   -   12:49   -           -
Ⓣ Ⓣ    5 Østerås                  2 (Retning Østerås)   -   12:22   PT136S      -
Ⓣ Ⓣ    5 Østerås                  2 (Retning Østerås)   -   12:37   PT117S      -
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
./ruter.py alexander -l 54 -p 2 -n 2
Avganger fra alexander kiellands plass, oppdatert 12:25
Linje/Destinasjon                 Platform            Full  Tid     Forsinkelse Avvik
🚌     54 Kjelsås stasjon          2                     0%  12:35   PT179S      -
🚌     54 Kjelsås stasjon          2                     0%  12:45   -           -
```

TODO:
* Colors for lines
* One-line interface for status bar
* Decode delay data
* Set up as finger/web service?
* Split core functions to a library.

One-liner sketches:
```
./ruter.py vøyenbrua -o -l 28 -p 2
🚌 28 Fornebu fra vøyenbrua 15:49 (1 min)  15:59 (Kø, 11 min)  16:09 (21 min.)
```
