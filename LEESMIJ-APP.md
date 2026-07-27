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

## De 51 steden

De misser is de gemeten gemiddelde fout uit de walk forward backtest over 150 dagen, voor vandaag, morgen en overmorgen, in de eenheid van die stad.

### Verenigde Staten (°F)

| Stad | Station | Bron | Misser vd/mo/ov |
|---|---|---|---|
| New York | LGA | METAR archief | ±1,09 / 1,58 / 1,87° |
| Chicago | ORD | METAR archief | ±0,9 / 1,5 / 1,9° |
| Miami | MIA | METAR archief | ±0,77 / 1,1 / 1,12° |
| Los Angeles | LAX | METAR archief | ±0,63 / 1,36 / 1,61° |
| San Francisco | SFO | METAR archief | ±1,48 / 2,09 / 2,43° |
| Seattle | SEA | METAR archief | ±0,98 / 2,07 / 2,43° |
| Denver | BKF | METAR archief | ±0,94 / 1,66 / 1,92° |
| Dallas | DAL | METAR archief | ±1,07 / 1,91 / 2,21° |
| Houston | HOU | METAR archief | ±0,98 / 1,61 / 1,9° |
| Austin | AUS | METAR archief | ±0,92 / 1,63 / 2,02° |
| Atlanta | ATL | METAR archief | ±0,83 / 1,79 / 2,12° |

### Europa (°C)

| Stad | Station | Bron | Misser vd/mo/ov |
|---|---|---|---|
| Londen | EGLC | METAR archief | ±0,57 / 0,88 / 0,99° |
| Parijs | LFPB | METAR archief | ±0,49 / 0,69 / 0,72° |
| Amsterdam | EHAM | METAR archief | ±0,53 / 0,83 / 0,87° |
| Madrid | LEMD | METAR archief | ±0,46 / 0,54 / 0,6° |
| Milaan | LIMC | METAR archief | ±0,48 / 0,67 / 0,73° |
| München | EDDM | METAR archief | ±0,47 / 0,74 / 0,92° |
| Warschau | EPWA | METAR archief | ±0,47 / 0,68 / 0,86° |
| Helsinki | EFHK | METAR archief | ±0,67 / 0,99 / 1,26° |
| Ankara | LTAC | METAR archief | ±0,59 / 0,7 / 0,81° |
| Istanbul | LTFM | METAR archief | ±0,73 / 0,97 / 0,88° |
| Moskou | UUWW | METAR archief | ±0,67 / 0,89 / 1,06° |

### Azië en Midden-Oosten (°C)

| Stad | Station | Bron | Misser vd/mo/ov |
|---|---|---|---|
| Tokio | RJTT | METAR archief | ±0,78 / 0,98 / 1,11° |
| Seoul | RKSI | METAR archief | ±0,79 / 1,01 / 1,12° |
| Busan | RKPK | METAR archief | ±0,7 / 0,97 / 1,03° |
| Taipei | RCSS | METAR archief | ±0,87 / 1,07 / 1,09° |
| Peking | ZBAA | METAR archief | ±0,98 / 1,3 / 1,43° |
| Shanghai | ZSPD | METAR archief | ±0,76 / 0,99 / 1,1° |
| Guangzhou | ZGGG | METAR archief | ±0,81 / 1,07 / 1,15° |
| Shenzhen | ZGSZ | METAR archief | ±0,78 / 0,93 / 1,07° |
| Chengdu | ZUUU | METAR archief | ±0,97 / 1,49 / 1,69° |
| Chongqing | ZUCK | METAR archief | ±0,78 / 0,99 / 1,2° |
| Wuhan | ZHHH | METAR archief | ±0,74 / 0,94 / 1,14° |
| Qingdao | ZSQD | METAR archief | ±1,11 / 1,3 / 1,39° |
| Jinan | ZSJN | ERA5 raster | ±0,44 / 0,79 / 0,99° |
| Zhengzhou | ZHCC | METAR archief | ±0,78 / 0,96 / 1,07° |
| Hongkong | VHHH | HKO Daily Extract | ±0,75 / 0,92 / 0,92° |
| Manila | RPLL | METAR archief | ±0,82 / 0,89 / 0,93° |
| Kuala Lumpur | WMKK | METAR archief | ±0,73 / 0,91 / 0,98° |
| Singapore | WSSS | METAR archief | ±0,52 / 0,73 / 0,85° |
| Karachi | OPKC | METAR archief | ±0,65 / 0,7 / 0,74° |
| Lucknow | VILK | METAR archief | ±0,74 / 1,21 / 1,5° |
| Jeddah | OEJN | METAR archief | ±1,0 / 1,08 / 1,1° |
| Tel Aviv | LLBG | METAR archief | ±0,43 / 0,53 / 0,54° |

### Amerika buiten de VS, Afrika, Oceanië (°C)

| Stad | Station | Bron | Misser vd/mo/ov |
|---|---|---|---|
| Toronto | CYYZ | METAR archief | ±0,49 / 0,92 / 1,11° |
| Mexico-Stad | MMMX | METAR archief | ±0,71 / 0,89 / 0,97° |
| Panama-Stad | MPMG | METAR archief | ±0,66 / 0,69 / 0,77° |
| Buenos Aires | SAEZ | METAR archief | ±0,62 / 0,93 / 1,1° |
| São Paulo | SBGR | METAR archief | ±0,76 / 0,92 / 0,88° |
| Kaapstad | FACT | METAR archief | ±0,73 / 0,92 / 0,96° |
| Wellington | NZWN | METAR archief | ±0,47 / 0,51 / 0,53° |

Drie steden wijken af van het METAR archief. **Hongkong** rekent af op het hoofdstation van het Hong Kong Observatory, want dat is de bron waarop de markt afrekent; die publiceert per maand, dus de kalibratie loopt tot ongeveer een maand terug. **Jinan** heeft geen bruikbaar METAR archief en valt terug op het ERA5 raster. Voor deze twee is de dagelijkse zelfcontrole in de app alleen indicatief (die loopt op ERA5) en is de automatische driftherijking uitgezet; zij worden wekelijks via de kalibratie bijgewerkt. **Istanbul, Moskou en Tel Aviv** gebruiken hetzelfde METAR archief als de rest: dat bevat dezelfde waarnemingen als de NOAA reeks en heeft wel historie, wat een backtest mogelijk maakt. Voor de elf Amerikaanse steden telt de NWS verwachting voor 25% mee op vandaag en morgen.

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
* **Vandaag is nu ook echt gekalibreerd**: via het forecastarchief van Open-Meteo, dat de voorspelling bewaart zoals die op de dag zelf gold. Getoetst: de bekende modelafwijking van Los Angeles staat op dag 0 nog steeds op 3,6 van de 4,1 °F, dus dit is een echte voorspelling en niet stiekem de analyse achteraf.

## Dagelijkse zelfcontrole

Onder "model en controles" staat een tabel met de laatste 4 dagen: per dag de afwijking (echt min voorspeld) voor de horizon vandaag, morgen en overmorgen, plus het gemiddelde eronder. De app rekent dit zelf uit, elke dag opnieuw, door de werkelijke stationsmeting op te halen en de voorspelling van toen na te rekenen met dezelfde gekalibreerde formule. Dat werkt ook voor zelf toegevoegde steden.

Positief betekent dat het warmer werd dan voorspeld, negatief kouder. Vier dagen is te weinig om conclusies uit te trekken, het is een steekproef; de betrouwbare cijfers staan op de regel "backtest vd/mo/ov", gebaseerd op ruim 80 gemeten dagen. Voor New York, Los Angeles en San Francisco rekent de controle zonder de NWS bijmenging, dat staat er ook bij.

## Automatische herijking

De app controleert per stad of het model uit de pas loopt en herijkt zichzelf als dat zo is. Dat gebeurt op de achtergrond, in de app zelf, met dezelfde backtest van 140 dagen die ook nieuwe steden krijgen.

**Waarom dit nodig is.** Gemeten op 220 dagen echte data verouderen gekalibreerde parameters gemiddeld met 5% na een week, 15% na drie weken en 30% na twee maanden. Maar dat verschilt enorm per stad: Los Angeles verliest na twee maanden 81% nauwkeurigheid, terwijl Hong Kong en Peking vrijwel niets verliezen. Een vaste maandelijkse herijking voor iedereen is dus zowel te veel als te weinig.

**Wanneer hij vuurt.** Twee voorwaarden, met minstens 7 dagen rust tussen twee herijkingen van dezelfde stad:

* **Drift**: de gemiddelde afwijking over de laatste 24 dagen wijkt statistisch significant af van nul (z ≥ 2,5), of de recente misser is 1,6 keer groter dan de backtest belooft.
* **Ouderdom**: de parameters zijn 45 dagen of ouder.

**Waarom die drempel.** Getest op 306 situaties: als de detector vuurt levert herijken gemiddeld 0,169 °C betere voorspellingen op, als hij stil blijft slechts 0,011 °C. Hij vangt daarmee ongeveer 86% van de te behalen winst terwijl hij maar 29% van de tijd hoeft te herijken. Met verse parameters vuurt hij bij geen enkele stad, dus valse alarmen zijn zeldzaam.

Onder "model en controles" zie je de regel "drifttoets" met de actuele z en ratio, of de toets binnen de marge blijft, hoe oud de parameters zijn en wanneer er voor het laatst herijkt is. Wil je niet wachten, dan staat er een link "nu herijken". Na een herijking wordt de controletabel opnieuw doorgerekend, want de oude afwijkingen golden voor de oude parameters.

De herijking gebeurt lokaal op je toestel en overschrijft `app_params.js` niet. Upload je een nieuwe `app_params.js` vanaf je computer, dan gaat de app de eerstvolgende keer weer van die verse cijfers uit.

## Sorteren

Boven de kaarten staat een balk. Je kunt sorteren op **nauwkeurig** (de kleinste gemiddelde misser eerst), **warmst**, **naam** of **standaard**. Bij nauwkeurig en warmst kies je er de horizon bij: vandaag, morgen of overmorgen. Op elke kaart verschijnt dan een chip met de waarde waarop gesorteerd wordt.

Naast **standaard**, **nauwkeurig**, **warmst** en **naam** is er **eigen**: je handmatige volgorde. Die ontstaat vanzelf zodra je gaat slepen.

Belangrijk detail: bij het sorteren worden Fahrenheit steden omgerekend naar Celsius, anders zouden New York, Los Angeles en San Francisco altijd onderaan bengelen puur omdat een graad Fahrenheit kleiner is. De chip toont daarom de omgerekende waarde, terwijl de kaart zelf in de eigen eenheid blijft. Rechts in de balk staat een filterveld om snel een stad te zoeken. Je keuze wordt onthouden.

Onder "model en controles" op elke kaart zie je de gewichten, de regressie, de bandbreedte met gemeten dekking en de laatste controles tegen het weerstation.

## Automatisch laten herkalibreren door GitHub

In de map zit `.github/workflows/kalibratie.yml`. Zodra je die meeuploadt naar je repository draait GitHub elke maandagochtend zelf de kalibratie en zet het resultaat terug in de repository. Je hoeft er niets voor te installeren en het is gratis voor een openbare repository.

Wat je daarvoor moet doen:

1. Upload ook de map `bot` (met `weer.py` en `kalibratie.py`) en de map `.github`. Let op: de webinterface van GitHub verbergt mappen die met een punt beginnen soms bij het slepen. Lukt het niet, maak dan op github.com het bestand handmatig aan via "Add file", dan "Create new file", en typ als naam `.github/workflows/kalibratie.yml`. Plak daarna de inhoud erin.
2. Ga naar Settings, dan Actions, dan General, en zet onderaan bij "Workflow permissions" de optie op "Read and write permissions". Zonder dat mag de workflow het resultaat niet terugschrijven.
3. Wil je niet wachten tot maandag: ga naar het tabblad Actions, kies "Wekelijkse herkalibratie" en klik op "Run workflow".

De workflow doet meer dan alleen draaien. Hij controleert het resultaat voordat er iets wordt vastgelegd (minstens tien steden, een plausibele richtingscoëfficiënt, een band die nul insluit, geldige JavaScript), en hij hoogt automatisch het versienummer van de service worker op zodat je telefoon de nieuwe cijfers ook echt ophaalt in plaats van de oude uit zijn cache. Mislukt een stad door een haperende API, dan blijven voor die stad de vorige parameters staan in plaats van te verdwijnen. Verandert er niets, dan wordt er ook niets vastgelegd.

Twee dingen om te weten. GitHub schakelt geplande workflows uit als er zestig dagen lang geen activiteit in de repository is; de wekelijkse commit van de workflow zelf houdt dat normaal gesproken in stand, en je krijgt een waarschuwingsmail voordat het gebeurt. En geplande tijden zijn bij GitHub een streven, geen garantie: een run kan een uur later beginnen als het druk is. Voor een wekelijkse kalibratie maakt dat niets uit.

Nodig is dit niet, want de app herijkt zichzelf al bij drift. Het is een bodem: een nieuwe telefoon of een verse installatie begint dan meteen met actuele parameters in plaats van te moeten wachten tot de drift zich meldt.

## Zelf ordenen, lijstweergave en de foutgrafiek

**Slepen.** Links op elke kaart staat een greepje. Houd het vast en sleep de kaart naar de plek waar je hem wilt hebben. De volgorde wordt onthouden en het sorteren springt automatisch naar de stand "eigen". Wil je terug naar een automatische ordening, kies dan gewoon weer nauwkeurig, warmst of naam; je eigen volgorde blijft bewaard en je kunt er altijd op terugklikken.

**Lijstweergave.** Rechts in de balk kun je wisselen tussen **kaarten** en **lijst**. De lijst toont per stad één regel met de drie temperaturen naast elkaar, wat een stuk sneller scrollen is zodra je veel steden hebt. Boven de twintig steden kiest de app die weergave vanzelf de eerste keer. Alles wat op de kaart staat zit er nog steeds in, onder het uitklapbare "model en controles".

**Foutgrafiek.** De vier tekstregels met afwijkingen zijn vervangen door drie grafiekjes, één per horizon (vd, mo, ov). Je ziet in één oogopslag de laatste 24 dagen. De middenlijn is nul, de blauwe band eromheen is de misser die de backtest belooft. Groene puntjes vallen binnen die band, rode of blauwe puntjes erbuiten (rood = het werd warmer dan voorspeld, blauw = kouder). Rechts staat de gemeten gemiddelde misser; die kleurt rood zodra hij structureel groter is dan beloofd.

## Zes statistische verbeteringen (v10)

**Eerlijkere metingen in de VS.** De dagmaxima van de elf Amerikaanse stations komen nu uit de 1 minuut reeks in plaats van de uurlijkse METAR (63 tot 119 dagen per station verfijnd; Buckley/Denver heeft geen 1 minuut data en blijft uurlijks). De doelwaarde ligt daarmee dichter bij het echte continue maximum. Let op: de gemeten missers zijn daardoor een fractie groter geworden, want het doel is scherper, niet het model slechter.

**Lagterm.** De fout van eergisteren telt mee via een geleerde coefficient g (gekrompen richting nul). Op deze 150 dagen leverde dat gemiddeld 0,0% op: het mechanisme staat aan, maar activeert alleen als er echt autocorrelatie in de fouten zit.

**Spreidingsband.** De onzekerheidsband schaalt nu met de actuele spreiding tussen de vijf modelsystemen (σ = c + d × spreiding). Deze variant won de out of sample validatie nipt van de vaste band (dekking 81,5% tegen 82,6%, doel 80%, CRPS gelijk) en staat daarom aan; verliest hij bij een latere kalibratie, dan valt de app automatisch terug op de vaste band.

**Dagelijkse voorspellingslog.** Een tweede workflow logt elke ochtend wat de app echt toont (ledengemiddelden per ensemblesysteem) plus de NWS dagverwachting. Na 75 logdagen kalibreert de wekelijkse run rechtstreeks op die reeks, waarmee het verschil tussen trainen en tonen verdwijnt. Na 40 dagen wordt het NWS gewicht per stad geleerd in plaats van vast 25%.

**Out of sample bandfactor.** De verbredingsfactor wordt op de eerste helft van de evaluatie gekozen en op de tweede helft gemeten, dus het dekkingscijfer is niet langer licht geflatteerd.

**CUSUM getest en afgewezen.** De voorgestelde CUSUM driftdetector is op 220 dagen echte data vergeleken met de bestaande z toets en verloor duidelijk (vangt 65% van de herijkwinst tegen 86%). De z toets blijft.

## Logboek

Boven de kaarten zit een uitklapbaar logboek. Daarin komt alles te staan wat de app op de achtergrond doet of tegenkomt, met de nieuwste melding bovenaan. Drie soorten:

* **Grijs, een melding**: een herijking is klaar, een backtest van een nieuwe stad is gelukt, er is een verse kalibratie van GitHub geladen, een stad is toegevoegd of verwijderd, of een controle liep op het ERA5 raster omdat er geen bruikbaar weerstation was.
* **Oranje, een waarschuwing**: een stad loopt uit de pas (met de gemeten z en hoeveel keer groter de misser is dan de backtest belooft), parameters zijn te oud geworden, of er kon geen verse voorspelling worden opgehaald.
* **Rood, een fout**: geen verbinding, een mislukte herijking of een backtest die niet lukte.

Het bolletje naast "logboek" telt hoeveel nieuwe waarschuwingen en fouten er zijn sinds je het paneel voor het laatst opende. Open je het, dan verdwijnt de teller en blijven de regels gewoon staan. Met "wissen" gooi je de geschiedenis weg.

Twee dingen die voorkomen dat het logboek dichtslibt: dezelfde melding voor dezelfde stad wordt binnen twaalf uur niet herhaald, en als de verbinding helemaal wegvalt krijg je één regel in plaats van een regel per stad. Er worden maximaal 200 regels bewaard, alleen op je eigen toestel.

## Waarschuwing als het model uit de pas loopt

Zodra de drifttoets aanslaat verschijnt er een oranje chipje **drift** naast de stadsnaam, in beide weergaven. Dat betekent: de afwijkingen van de afgelopen 24 dagen passen niet meer bij wat de backtest belooft. De app zet die stad dan meteen in de wachtrij voor een herijking; tijdens het rekenen verandert het chipje in **herijken** en daarna in een groen **herijkt**.

Blijft de chip na een herijking terugkomen, dan is er iets structurelers aan de hand. De meest waarschijnlijke oorzaak bij een zelf toegevoegde stad is dat het gekozen weerstation niet representatief is, bijvoorbeeld een kuststation voor een stad in het binnenland. Kijk dan onder "model en controles" bij "bron" welk station het is en op welke afstand.

## De zes verbeteringen van v10

**1. Fijnere afrekenwaarden voor de VS.** De dagmaxima van de elf Amerikaanse stations worden verrijkt met de 1 minuut ASOS reeks, dezelfde continue meting waar de officiële dagwaarde op stoelt. In de laatste kalibratie werden per stad 63 tot 119 dagen een fractie naar boven bijgesteld. Denver is de uitzondering: Buckley is militair en levert geen 1 minuut data, dus daar blijft de uurwaarde gelden.

**2. Lagterm.** De voorspelling leert van de fout van eergisteren: verwachting = a + b × modelgemiddelde + g × recente fout. De g wordt per stad geschat met krimp naar nul, zodat hij alleen meedoet waar foutpersistentie echt bestaat (bij 23 van de 51 steden is hij exact nul). Eerlijk gezegd: over de backtest is de gemiddelde winst 0,0%, met Amsterdam als sterkste geval (g ≈ 0,2 tot 0,25). De term is gratis waar hij niets doet en helpt wanneer een regime verschuift.

**3. Spreidingsband.** De onzekerheidsband schaalt mee met de actuele spreiding tussen de vijf modelsystemen: σ = c + d × spreiding, met gestandaardiseerde kwantielen. Deze variant gaat alleen live als hij de validatie wint; deze week won hij nipt (dekking 81,5% tegen 82,6% bij een doel van 80%, gelijke CRPS). Verliest hij bij een toekomstige kalibratie, dan valt de app automatisch terug op de vaste band.

**4. Dagelijkse voorspellingslog.** De workflow `logboek.yml` legt elke ochtend vast wat de app daadwerkelijk toont: het ledengemiddelde per ensemblesysteem per stad en doeldag, plus de NWS dagverwachting voor de VS. Vanaf 75 gelogde dagen kalibreert de wekelijkse run rechtstreeks op die reeks, waarmee het verschil tussen trainen (deterministisch archief) en tonen (ensemblegemiddelden, gemeten ~0,35 °C) verdwijnt. Vanaf 40 dagen wordt per Amerikaanse stad het NWS gewicht geleerd in plaats van de vaste 25%.

**5. Eerlijke bandfactor.** De verbredingsfactor wordt op de eerste helft van de evaluatieperiode gekozen en de dekking op de tweede helft gemeten, dus het gerapporteerde cijfer is out of sample.

**6. CUSUM getest en afgewezen.** De voorgestelde CUSUM driftdetector is op 220 dagen echte data vergeleken met de bestaande z toets: de z toets vangt 86% van de haalbare herijkingswinst bij 29% vuren, de beste CUSUM haalde 65% bij 35% vuren. De z toets blijft dus, nu met cijfers onderbouwd.

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
