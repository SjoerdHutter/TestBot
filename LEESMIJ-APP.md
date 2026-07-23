# Weerbot als app op je iPhone

Deze map is een installeerbare webapp. Hij haalt de ensemblevoorspellingen zelf live op bij Open‑Meteo, dus je computer hoeft niet aan te staan. De correcties en de fouthistorie uit de backtest zitten ingebouwd.

## Eenmalig online zetten (gratis, een minuut of vijf)

1. Maak een gratis account op github.com als je dat nog niet hebt.
2. Klik rechtsboven op het plusje en kies "New repository". Naam bijvoorbeeld `weerbot`, zet hem op Public en klik "Create repository".
3. Klik op de link "uploading an existing file" en sleep alle bestanden uit deze map erin (index.html, manifest.webmanifest, sw.js, weer_data.js en de drie iconen). Klik onderaan op "Commit changes".
4. Ga naar Settings, dan Pages in het linkermenu. Kies bij Branch `main`, laat de map op `/ (root)` staan en klik Save.
5. Na een minuut staat je app op `https://jouwgebruikersnaam.github.io/weerbot/`.

## Installeren op de iPhone

1. Open dat adres in Safari.
2. Tik op de deelknop (het vierkantje met de pijl omhoog).
3. Kies "Zet op beginscherm" en tik op Voeg toe.

Je hebt nu een Weerbot icoon op je beginscherm. Hij opent volledig scherm, zonder adresbalk, en ververst zichzelf als je hem opent. Tik bovenin op "vernieuwen" om tussendoor de nieuwste modelrun op te halen. Zonder internet laat hij de laatst opgehaalde voorspellingen zien met een melding erbij.

## Hoe de fouthistorie actueel blijft

De app rekent live, maar de correcties en de misserkolom komen uit de backtest op je computer. Wil je die verversen, draai dan af en toe `python3 weer.py` op de computer en upload het nieuwe `weer_data.js` naar de repository (op github.com: open het bestand, klik het potlood of upload het opnieuw, commit). De app pakt het automatisch op. Doe je dit nooit, dan blijft de app gewoon werken met de cijfers van de laatste keer.

## Goed om te weten

* De WU regel (de tweede mening van Weather Underground) verschijnt alleen voor datums die in het meegeleverde `weer_data.js` staan, want die bron laat zich niet rechtstreeks vanuit de browser uitlezen. Vers te houden via dezelfde upload als hierboven.
* De pagina werkt ook gewoon op de computer, dubbelklikken op index.html is genoeg.
* De repository is openbaar, maar er staat niets persoonlijks in: alleen de voorspellingscijfers.
