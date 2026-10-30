# Senderlisten-Editor (Web)

TV-Senderlisten im Browser sortieren und bereinigen, ähnlich wie mit ChanSort.
Die Datei wird **nicht hochgeladen**: Die Formaterkennung und das Schreiben übernehmen die
originalen ChanSort-Loader, die als WebAssembly direkt im Browser laufen.

```
senderliste-web/
├─ chansort/                 ← Klon von ChanSort (wird in Schritt 2 angelegt, nicht einchecken)
├─ tools/PrepareChanSort/    ← passt ChanSort für den Browser an (Schritt 3)
└─ src/ChanSortWeb/
   ├─ Bridge.cs              ← Verbindung JavaScript ↔ ChanSort-Loader
   ├─ ChanSortWeb.csproj
   └─ wwwroot/               ← Web-Oberfläche (HTML, CSS, JavaScript)
```

---

## Einrichtung (einmalig)

### 1. Werkzeuge installieren

- **.NET 10 SDK**: https://dotnet.microsoft.com/download/dotnet/10.0 (baut auch das .NET-9-Projekt)
- **Git**: https://git-scm.com
- Danach in einem Terminal den WebAssembly-Baukasten installieren
  (unter Windows ggf. als Administrator, unter Linux/macOS ggf. mit `sudo`):

```
dotnet workload install wasm-tools wasm-tools-net9
```

Das Projekt zielt auf **.NET 9**, weil das SQLite-Paket noch keine Browser-Version für .NET 10 enthält
(sonst stürzen Samsung, Panasonic, Hisense usw. mit „Assertion failed“ ab).

### 2. ChanSort in den Projektordner klonen

Im Ordner `senderliste-web`:

```
git clone https://github.com/PredatH0r/ChanSort.git chansort
```

### 3. ChanSort für den Browser vorbereiten

```
dotnet run --project tools/PrepareChanSort -- chansort net9.0
```

Das Programm ändert 16 Dateien in `chansort/` (Zielframework, Pfade zu den `.ini`-Dateien,
optionale LG-Oberfläche). Auf dem Desktop verhält sich ChanSort danach unverändert.
Es kann beliebig oft ausgeführt werden.

### 4. Starten und testen

```
dotnet run --project src/ChanSortWeb
```

Der erste Build dauert einige Minuten (SQLite wird für WebAssembly kompiliert).
Im Terminal erscheint danach eine Adresse wie `http://localhost:5000`, die du im Browser öffnest.

Zum Testen eignen sich die Beispieldateien aus ChanSort, z. B.
`chansort/source/Test.Loader.Sony/TestFiles/android_sdb-sat.xml`
oder die Samsung-Dateien unter `chansort/source/Test.Loader.Samsung/`.

---

## Veröffentlichen

```
dotnet publish src/ChanSortWeb -c Release
```

Der fertige Inhalt liegt in `src/ChanSortWeb/bin/Release/net9.0/publish/wwwroot/`.
Diesen Ordner lädst du auf einen beliebigen statischen Webspace (z. B. Cloudflare Pages,
Netlify, GitHub Pages oder klassischer Webspace). Ein Server-Programm wird nicht gebraucht.

Hinweise:
- Der Server muss `.wasm`-Dateien mit dem Typ `application/wasm` ausliefern. Bei Apache-Webspace
  dafür eine `.htaccess` mit `AddType application/wasm .wasm` in den Ordner legen.
- Vor dem Veröffentlichen ausfüllen: `impressum.html`, `datenschutz.html` und in `index.html`
  den Link `sourceLink` auf dein öffentliches Git-Repository setzen.
- Lizenz: Da ChanSort unter der GPLv3 steht, gilt das auch für dieses Projekt. Lege den
  Lizenztext von https://www.gnu.org/licenses/gpl-3.0.txt als `LICENSE` ins Repository und
  veröffentliche den Quellcode (inklusive der von PrepareChanSort geänderten Dateien).

---

## ChanSort aktualisieren

Neue ChanSort-Versionen bringen oft neue Formate oder Fehlerkorrekturen:

```
git -C chansort checkout .
git -C chansort pull
dotnet run --project tools/PrepareChanSort -- chansort net9.0
```

---

## Wenn etwas nicht klappt

| Meldung | Lösung |
|---|---|
| `NETSDK1147` oder Hinweis auf fehlenden Workload | `dotnet workload install wasm-tools` ausführen |
| Projekt `chansort/...` nicht gefunden | Schritt 2 im richtigen Ordner ausführen, der Klon muss `chansort` heißen |
| Samsung/Panasonic/Hisense/TCL-Dateien: „Assertion failed“ | SQLite-Browser-Version passt nicht zum Zielframework. Prüfen mit `ls ~/.nuget/packages/sqlitepclraw.lib.e_sqlite3/*/runtimes/browser-wasm/nativeassets/`; das Zielframework (Schritt 3 und `ChanSortWeb.csproj`) darf nicht neuer sein als der neueste Ordner dort |
| Ein einzelner Loader kompiliert nicht | Seine Zeile in `ChanSortWeb.csproj` und in `Bridge.cs` (`CreatePlugins`) auskommentieren, den Rest weiter nutzen und mir die Fehlermeldung schicken |
| Editor bleibt beim Laden hängen | Browser-Konsole öffnen (F12) und die Fehlermeldung kopieren |

---

## Stand und bekannte Grenzen

**Getestet** (in einer Testumgebung, mit den Beispieldateien aus ChanSort):
- ChanSort-Kernbibliothek plus 13 Loader und die Brücke kompilieren fehlerfrei.
- Laden → Umsortieren → Löschen → Speichern → Wiedereinlesen funktioniert für **Sony**
  (Android- und KDL-Format), **Grundig**, **Linux VDR** und **M3U**.
- Die Oberfläche (Auswahl, Ziehen, Verschieben, Löschen, Suche, Rückgängig, Download) wurde
  im Browser mit einer echten Sony-Liste geprüft, auch in der Handy-Ansicht.

**Noch nicht getestet** (in meiner Umgebung fehlte der Zugriff auf NuGet):
- Der eigentliche WebAssembly-Build und die Loader mit SQLite oder Newtonsoft.Json
  (Samsung, LG, Philips, Panasonic, Hisense, TCL, Toshiba, Android, Chmax, Medion, SdxJson, Amdb, VisionEdge).

**Bekannte Grenzen dieser ersten Version:**
- Favoritenlisten werden angezeigt, sind aber noch nicht bearbeitbar. Formate, bei denen die
  Sortierung nur über Favoriten läuft (z. B. Enigma2), sind daher vorerst nur lesbar.
- TechniSat ist nicht enthalten (altes Projektformat in ChanSort).
- Referenzlisten (Sortierung einer Liste auf eine andere übertragen) fehlen noch.
- Gelöschte Sender: Kann ein Format nicht löschen, werden sie ausgeblendet und ans Ende gesetzt.
- Nach dem Sortieren wird jede geänderte Liste lückenlos neu nummeriert, beginnend bei der
  bisher kleinsten Nummer der Liste.

## Anleitungsseiten (Marken)

Die Seiten unter `src/ChanSortWeb/wwwroot/anleitung/` werden aus `tools/BuildGuides/guides_data.py` erzeugt.
Nach einer inhaltlichen Änderung:

```
python tools/BuildGuides/build_guides.py
```

(Python 3 nötig, keine Zusatzpakete.) Die Adresse für Rückmeldungen steht oben in `build_guides.py`
(`FEEDBACK_MAIL`) und muss vor der Veröffentlichung angepasst werden. Danach wie immer den Server neu
starten (`dotnet run`), damit die geänderten Dateien ausgeliefert werden.
