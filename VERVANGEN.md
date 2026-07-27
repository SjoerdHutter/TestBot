# De bestaande weerbot vervangen door de vernieuwde versie

Je hebt al een werkende repository staan. Deze vervanging is dus geen nieuwe installatie: je hoeft alleen bestanden te overschrijven, één bestand weg te gooien en twee mappen toe te voegen. Reken op tien minuten.

Alle instellingen die je eerder gemaakt hebt (Pages, en zo nodig de schrijfrechten) blijven staan. Het adres van je app verandert niet en het icoon op je beginscherm hoeft er niet af.

---

## Wat er verandert

* De stedenlijst gaat van 15 naar **51 steden**, met andere meetstations.
* `weer_data.js` **vervalt**. De app doet de dagelijkse controle nu zelf, dus dat bestand is overbodig geworden.
* Er komen twee mappen bij: **`bot`** (de kalibratie) en **`.github`** (het weekschema), als je die nog niet had.
* `app_params.js` bevat nu de cijfers van alle 51 steden.

---

## Stap 1: het vervallen bestand verwijderen

Dit is de enige stap die je niet mag overslaan, want een achtergebleven `weer_data.js` bevat de oude 15 steden.

1. Open je repository op github.com.
2. Klik in de bestandenlijst op **`weer_data.js`**.
3. Klik rechtsboven op het **prullenbakje** (of op de drie puntjes, dan **Delete file**).
4. Scrol naar beneden en klik op **Commit changes**, en nog eens op **Commit changes**.

Staat er ook nog een `weer_data.json` of `weer_forecasts.csv`? Die mogen op dezelfde manier weg.

---

## Stap 2: de gewone bestanden overschrijven

1. Klik op **Add file**, dan **Upload files**.
2. Sleep vanuit de nieuwe uitgepakte map deze bestanden erin:
   * `index.html`
   * `app_params.js`
   * `sw.js`
   * `manifest.webmanifest`
   * de map `bot`
   * `LEESMIJ-APP.md`, `GITHUB-STAPPENPLAN.md`, `VERVANGEN.md`
3. De iconen mag je overslaan, die zijn niet veranderd.
4. Klik onderaan op **Commit changes**.

GitHub overschrijft bestanden met dezelfde naam vanzelf. Je krijgt geen waarschuwing, dat is normaal.

---

## Stap 2b: Jekyll uitzetten

Krijg je bij het publiceren een foutmelding zoals *"The source text contains invalid characters for the used encoding UTF-8"*, dan komt dat hierdoor: GitHub Pages haalt je bestanden door Jekyll, een blogsysteem dat over de markdown-bestanden struikelt. Voor deze app is Jekyll nergens voor nodig.

1. Klik op **Add file**, dan **Create new file**.
2. Typ als naam precies `.nojekyll` en laat het veld eronder leeg. Weigert GitHub een leeg bestand, typ dan één spatie.
3. Klik op **Commit changes**.

De volgende publicatie slaagt dan zonder verdere aanpassing.

## Stap 3: het weekschema, alleen als je dat nog niet had

Had je de wekelijkse herkalibratie al draaien, sla deze stap dan over. Zo niet:

1. Klik op **Add file**, dan **Create new file**.
2. Typ als naam precies dit, inclusief de schuine strepen:

   ```
   .github/workflows/kalibratie.yml
   ```

3. Open op je computer `.github/workflows/kalibratie.yml` uit de nieuwe map met een tekstverwerker, kopieer alles en plak het in het grote veld.
4. Klik op **Commit changes**.

Ga daarna naar **Settings**, dan **Actions**, dan **General**, en zet bij *Workflow permissions* het bolletje op **Read and write permissions**. Klik op **Save**. Zonder dat mag de workflow zijn resultaat niet opslaan.

---

## Stap 4: controleren

Je bestandenlijst hoort er nu zo uit te zien:

```
.github/workflows/kalibratie.yml
bot/kalibratie.py
bot/weer.py
app_params.js
apple-touch-icon.png
icon-192.png
icon-512.png
index.html
manifest.webmanifest
sw.js
LEESMIJ-APP.md
GITHUB-STAPPENPLAN.md
VERVANGEN.md
```

Geen `weer_data.js` meer, wel de mappen `bot` en `.github`.

---

## Stap 5: je telefoon laten vernieuwen

De app bewaart bestanden lokaal zodat hij ook zonder internet opent. In de nieuwe versie is het interne versienummer opgehoogd, dus normaal gesproken pakt je telefoon de nieuwe versie vanzelf op zodra je de app opent en even wacht.

Gaat dat niet meteen goed:

1. Sluit de app helemaal af: veeg hem weg uit de app-wisselaar (dubbel op de thuisknop, of van onderen omhoog vegen en vasthouden).
2. Open hem opnieuw en wacht tot de temperaturen verschijnen.
3. Zie je nog steeds vijftien steden, herhaal stap 1 dan nog één keer. De service worker vernieuwt bij de tweede start.

Je hoeft het icoon niet opnieuw op je beginscherm te zetten.

---

## Wat er met je opgeslagen gegevens gebeurt

Dit regelt de app zelf en het is goed om te weten waarom.

Drie steden houden dezelfde interne sleutel maar krijgen een **ander meetstation**: Londen gaat van Heathrow naar London City, Parijs van Charles de Gaulle naar Le Bourget en Seoul van Gimpo naar Incheon. Hongkong wisselt bovendien van meetdienst naar het Observatorium. Opgeslagen controles en herijkingen van de oude versie hoorden bij de oude stations en zouden op de nieuwe stations verkeerde uitkomsten geven.

De app merkt daarom bij de eerste start dat de stedenlijst gewisseld is en wist precies die drie dingen: de opgeslagen voorspellingen, de controlegeschiedenis en de eerder uitgevoerde herijkingen. In het logboek verschijnt de regel *"nieuwe stedenlijst geladen, opgeslagen controles en herijkingen gewist"*.

Wat **blijft** staan: de steden die je zelf had toegevoegd, je sorteerkeuze, je gekozen weergave, je handmatige volgorde en je logboek. Zelf toegevoegde steden draaien binnen een paar minuten vanzelf een nieuwe backtest.

De eerste dag zijn de foutgrafiekjes leeg, want de app moet de controle van de afgelopen dagen opnieuw opbouwen. Dat vult zich binnen een minuut of twee vanzelf, zolang je de app openhoudt.

---

## Nog even dit

Je hoeft niets te doen aan **Pages**: die instelling blijft staan en je adres verandert niet.

Wil je meteen verse cijfers in plaats van tot maandag te wachten, ga dan naar het tabblad **Actions**, kies **Wekelijkse herkalibratie** en klik op **Run workflow**. De meegeleverde `app_params.js` is al vers, dus strikt nodig is het niet.
