# Speldosa, så kommer du igång

Speldosa är en speldosa för barn. Lägg ett kort på speldosan så spelas musiken, sagan eller ljudboken som hör
till kortet i en högtalare i rummet. Lyft kortet så pausar det. Lägg tillbaka det så fortsätter det.

In English: [setup-guide.md](setup-guide.md).

## Krav

| | |
|---|---|
| Home Assistant | 2026.10 eller senare, med HACS installerat |
| Music Assistant | Uppsatt i Home Assistant, med din musiktjänst (till exempel Spotify) och dina högtalare |
| En dator | Med Chrome eller Edge, för Wi-Fi-steget. iPhone och iPad fungerar inte för det steget |
| En USB-C-kabel | En som klarar data. Många kablar laddar bara |
| Wi-Fi | Ett 2,4 GHz-nätverk. Speldosan använder inte 5 GHz |

Speldosan kommer med programvaran redan installerad. Det tar ungefär en kvart att komma igång.

## 1. Anslut speldosan till Wi-Fi

1. Koppla speldosan till datorn med USB-C-kabeln.
2. Öppna <https://web.esphome.io> i Chrome eller Edge och välj **Connect**.
3. Välj speldosan i listan. Namnet innehåller "USB JTAG" eller "ESP32".
4. Välj att ställa in Wi-Fi (inte Install: programvaran finns redan), välj ditt 2,4 GHz-nätverk och skriv
   lösenordet.
5. När det står att speldosan är ansluten kopplar du ur den och sätter den i sin USB-laddare i barnets rum.

Lampan pulserar orange så länge speldosan saknar Wi-Fi och pulserar blått medan den väntar på Home Assistant.

## 2. Lägg till speldosan i Home Assistant

1. Home Assistant visar **Nya enheter hittades: Speldosa** under Inställningar, Enheter och tjänster. Välj
   **Lägg till**.
2. Syns inget efter en minut: Inställningar, Enheter och tjänster, **Lägg till integration**, ESPHome, och skriv
   speldosans adress från routern.
3. När speldosan är tillagd lyser lampan grönt.

## 3. Installera Speldosa-integrationen

1. Öppna **HACS** i Home Assistant, menyn uppe till höger, **Anpassade arkiv** (Custom repositories).
2. Lägg till `https://github.com/andreas0480/speldosa-home-assistant` med typen **Integration**.
3. Sök efter **Speldosa** i HACS, välj **Ladda ner** och starta om Home Assistant när det frågar.
4. Inställningar, Enheter och tjänster, **Lägg till integration**, **Speldosa**. Välj speldosan och högtalaren
   den ska spela på.

En sida som heter **Speldosa** dyker upp i sidofältet.

## 4. Koppla korten

1. Lägg ett nytt kort på speldosan och låt det ligga kvar. Lampan blinkar rosa och speldosan ger två korta ljud:
   kortet har ingen musik ännu.
2. Öppna **Speldosa** i sidofältet. En blå ruta säger att ett nytt kort ligger på speldosan. Välj **Koppla
   kortet**.
3. Skriv vad kortet ska spela, till exempel "Bamse" eller "Die drei ???". Träffarna kommer från din musiktjänst.
   Kommer inget tillbaka kan Spotify vara upptaget: vänta en halv minut och försök igen.
4. Välj en träff. Till höger väljer du hur kortet ska spela (se nedan) och sedan **Koppla kortet**. Det börjar
   spela.

Gör likadant för varje kort.

## Spelval

| Val | Passar för | Det här händer |
|---|---|---|
| Ett slumpvis album varje gång | Ljudboksserier där varje album är ett avsnitt (Die drei ???, Bamse, Bibi Blocksberg) | Spelar ett helt album i ordning. Varje valt album hörs en gång innan något upprepas |
| Nästa album varje gång | Serier som lyssnas på i ordning | Spelar albumen efter varandra, i avsnittsordning |
| Från början | Album, spellistor, låtar | Börjar från början varje gång |
| I slumpvis ordning | Spellistor, album, en artists musik | Blandar |
| Fortsätt där det slutade | Ljudböcker | Fortsätter alltid där det var. Hörd till slutet börjar den om |
| Ett slumpvis eller nästa avsnitt | Poddar | Som albumvalen, ett avsnitt i taget |

För de två albumvalen visar sidan artistens album. Adventskalendrar, soundtrack, minis och liknande är inte
ikryssade, och när de flesta album har ett avsnittsnummer är bara de numrerade ikryssade. Kryssa i eller ur som
du vill.

Lyfts kortet mitt i ett album fortsätter det där när kortet kommer tillbaka, hur länge det än dröjer. Kortet går
vidare till ett nytt album först när albumet har hörts till slutet.

## Lyfta och lägga tillbaka

- Lyft kortet: musiken pausar.
- Lägg tillbaka det inom 15 minuter: det fortsätter där det var, oavsett hur kortet är inställt.
- Efter det bestämmer kortets val, som i tabellen ovan.

De 15 minuterna, startvolymen (40 %) och om speldosan först ska lämna en högtalargrupp ställs in per speldosa
under Inställningar, Enheter och tjänster, Speldosa, **Konfigurera**.

## Ljus och ljud

| Lampan | Betyder |
|---|---|
| Lyser grönt | Redo, inget kort på |
| Lyser gult | Ett kort ligger på och spelar |
| Gult, halvt ljus | Pausad |
| Kort vit blink | Ett kort lästes |
| Blinkar rosa, två ljud | Kortet har ingen musik ännu: koppla det på sidan Speldosa |
| Pulserar orange | Inget Wi-Fi |
| Pulserar blått | Ingen kontakt med Home Assistant |
| Blinkar rött | Något gick fel: Home Assistant visar ett meddelande med orsaken |

## Felsökning

| Det här ser du | Gör så här |
|---|---|
| web.esphome.io hittar inte speldosan | Prova en annan USB-C-kabel; många laddar bara. Använd Chrome eller Edge på en dator |
| Pulserar orange efter Wi-Fi-steget | Nätverket är bara 5 GHz, eller lösenordet var fel. Gör om steg 1 |
| Pulserar blått | Home Assistant har inte lagt till speldosan ännu (steg 2) |
| Blinkar rött och "kunde inte spela" | Meddelandet säger varför. Vanliga orsaker: högtalaren är av, eller musiktjänsten spelar på en annan högtalare. Spotify spelar på en högtalare i taget |
| Blinkar rött och "Problem med läsaren" på sidan | Dra ur sladden några sekunder och sätt i den igen |
| Sökningen är långsam eller hittar inget | Spotify begränsar Music Assistants sökningar ("rate limit"; i Music Assistants logg står "Spotify Rate Limiter" eller "asked to wait ... seconds"). Vänta en minut och sök igen. Varaktigt: skapa en egen gratis Spotify developer-app och ange dess Client ID i Music Assistant, Inställningar, Providers, Spotify; med det delade standard-ID:t nås gränsen snabbt. Det löste det hos oss (2026-11-26) |
| Kortet spelar fel sak | Sidan Speldosa, kortet, **Ändra** |

## Uppdateringar

Nya versioner av integrationen syns i HACS. Ny programvara till speldosan syns som en uppdatering på speldosans
enhetssida i Home Assistant.
