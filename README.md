A python client for ruter.no, made using the API at http://labs.ruter.no/

GPLv3

Example run of beta:

```

$ ./ruter.py lijordet
Flere treff, angi mer nøyaktig:
{u'lijordetrideveieninadderudv': 2195136, u'lijordet': 2190080}
[2195136] lijordetrideveieninadderudv
[2190080] lijordet

$ ./ruter.py 2190080
Linje/Destinasjon             Spor Tid               Type Forsinkelse
  5 Vestli                    1    15:34:59          Ⓣ
  5 Vestli                    1    15:44:16          Ⓣ
  5 Vestli                    1    15:49:59          Ⓣ
  5 Vestli                    1    15:59:16          Ⓣ
  5 Vestli                    1    16:04:59          Ⓣ
  5 Vestli                    1    16:14:16          Ⓣ
  5 Vestli                    1    16:19:59          Ⓣ
  5 Vestli                    1    16:29:16          Ⓣ
  5 Østerås                   2    15:37:59          Ⓣ    PT101S
  5 Østerås                   2    15:43:58          Ⓣ    PT16S
  5 Østerås                   2    15:52:59          Ⓣ    PT90S
  5 Østerås                   2    15:58:58          Ⓣ
  5 Østerås                   2    16:07:59          Ⓣ
  5 Østerås                   2    16:13:58          Ⓣ    PT80S
  5 Østerås                   2    16:22:59          Ⓣ
  5 Østerås                   2    16:28:58          Ⓣ

```
