# Rutercli

A python command line client for ruter.no, made using the API at http://labs.ruter.no/

See INSTALL.md

## Example run of 0.6:

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

## Web
https://graph.no/ruter/

## License
GNU AFFERO GENERAL PUBLIC LICENSE

## Thanks
* Icons used in web version from https://materialdesignicons.com/
* Thanks to Børge Nordli for lots of patches.
* Thanks to atchoo78 @ github for mac install how-to