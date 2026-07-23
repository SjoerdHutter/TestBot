# Weerbot als app op je iPhone

Deze map is een installeerbare webapp. Hij haalt de ensemblevoorspellingen zelf live op bij Open‑Meteo (tot 194 modelleden uit vijf modelsystemen), dus je computer hoeft niet aan te staan. De statistiek is gekalibreerd op een backtest van 150 dagen en volledig walk forward gevalideerd: elke dag werd voorspeld met uitsluitend kennis van voor die dag.

## Eenmalig online zetten (gratis, een minuut of vijf)

1. Maak een gratis account op github.com als je dat nog niet hebt.
2. Klik rechtsboven op het plusje en kies "New repository". Naam bijvoorbeeld `weerbot`, zet hem op Public en klik "Create repository".
3. Klik op de link "uploading an existing file" en sleep alle bestanden uit deze map erin. Klik onderaan op "Commit changes".
4. Ga naar Settings, dan Pages in het linkermenu. Kies bij Branch `main`, laat de map op `/ (root)` staan en klik Save.
5. Na een minuut staat je app op `https://jouwgebruikersnaam.github.io/weerbot/`.

## Installeren op de iPhone

1. Open dat adres in Safari.
2. Tik op de deelknop (het vierkantje met de pijl omhoog).
3. Kies "Zet op beginscherm" en tik op Voeg toe.

## Zelf steden toevoegen, met automatische backtest

Tik rechtsboven op "+ stad", typ een naam en kies bij het gewenste resultaat de eenheid (°C of °F). De app draait dan vanzelf een backtest van 140 dagen: hij zoekt binnen 80 km het dichtstbijzijnde METAR weerstation (via het IEM archief), haalt de previous runs van de vijf modellen op en leert daar walk forward de modelgewichten, de regressiecorrectie en de gekalibreerde 80% band uit, precies zoals bij de vaste steden. Dat duurt een paar seconden; zolang staat er "backtest loopt" op de kaart, daarna verschijnen de misser en de details vanzelf.

Eerlijk om te weten: het gekozen station is het dichtstbijzijnde, en dat is niet per se het station dat Weather Underground voor die stad hanteert. Onder "model en controles" zie je bij "bron" welk station het werd en op welke afstand. Is er geen station in de buurt of levert het te weinig bruikbare dagen, dan valt de kalibratie terug op de ERA5 reanalyse en staat dat er ook eerlijk bij. Mislukt de backtest door een haperende verbinding, tik dan bovenin op vernieuwen om het opnieuw te proberen. Verwijderen kan onder "model en controles". Toegevoegde steden en hun kalibratie staan alleen op het toestel waarop je ze toevoegde.

## Wat de statistiek doet

* **Modelgewichten**: de vijf modellen worden per stad gewogen naar recente skill. Voor Los Angeles krijgt GEFS bijvoorbeeld 60% en ECMWF maar 4%, omdat dat daar aantoonbaar beter werkt.
* **Regressiecorrectie**: in plaats van een vaste offset geldt verwachting = a + b × modelgemiddelde, met b voorzichtig richting 1 gekrompen. Dat vangt ook fouten die met de temperatuur meegroeien.
* **Vers geheugen**: alles wordt gewogen met een halfwaardetijd van 14 dagen, zodat een seizoenswissel de correctie niet maandenlang vervuilt.
* **Gekalibreerde band**: het 80% interval komt uit de werkelijke restfouten van de walk forward test en dekt gemeten 79,7%. Lopen de modelleden verder uiteen dan normaal, dan wordt de band automatisch breder.
* **NWS bijmenging**: voor New York, Los Angeles en San Francisco telt de officiële NWS verwachting voor 25% mee op vandaag en morgen (het vinkje bij de NWS regel). Dit is het enige onderdeel dat nog niet historisch gevalideerd kon worden, want er bestaat geen archief van NWS verwachtingen; het gewicht is bewust bescheiden gekozen.
* **Dag en datum**: onder vandaag, morgen en overmorgen staat de datum als dag/maand.

Onder "model en controles" op elke kaart zie je de gewichten, de regressie, de bandbreedte met gemeten dekking en de laatste controles tegen het weerstation.

## De kalibratie verversen

De correcties komen uit `kalibratie.py` in de computermap (naast `weer.py`). Draai af en toe, bijvoorbeeld maandelijks:

```
python3 kalibratie.py
```

en upload het nieuwe `app_params.js` naar de repository. De app pakt het automatisch op. Hetzelfde geldt voor `weer_data.js` uit de dagelijkse `python3 weer.py` run, die de WU kolom en de recente controles vers houdt. Doe je dit nooit, dan blijft de app gewoon werken met de cijfers van de laatste keer.

## Goed om te weten

* Zonder internet laat de app de laatst opgehaalde voorspellingen zien met een melding erbij. Tik bovenin op "vernieuwen" voor de nieuwste modelrun.
* De pagina werkt ook op de computer, dubbelklikken op index.html is genoeg.
* De repository is openbaar, maar er staat niets persoonlijks in: alleen voorspellingscijfers.
