# -*- coding: utf-8 -*-
# Inhalte der Marken-Anleitungen. Texte sind HTML-Schnipsel (b, code, kbd, a erlaubt).
# Quellen: ChanSort-Dokumentation (Wiki + fileformats), Hersteller-Support-Seiten, Anleitungen von
# Senderlisten-Anbietern und Erfahrungsberichte aus Foren. Menünamen können je nach Modell und
# Software-Stand leicht abweichen – das steht auch so auf jeder Seite.

BRANDS = [
# ------------------------------------------------------------------ Samsung
{
 "slug": "samsung", "name": "Samsung",
 "title": "Samsung Sender sortieren am PC – Senderliste bearbeiten",
 "description": "Samsung-Senderliste auf USB exportieren, im Browser sortieren, löschen und umbenennen und zurück auf den Fernseher spielen. Anleitung für alle Serien von 2010 bis heute.",
 "h1": "Samsung: Sender sortieren am PC",
 "intro": "Samsung-Fernseher können die Senderliste seit 2010 über das normale Menü auf einen USB-Stick kopieren. Welcher Menüweg gilt, hängt vom Baujahr ab – das findest du am schnellsten über die Modellnummer.",
 "identify_hint": "Die Modellnummer steht auf dem Typenschild hinten am Gerät oder unter <b>Einstellungen › Support › Über dieses TV-Gerät</b>. Die Buchstaben nach der Zollzahl verraten das Baujahr: <code>GU55<b>TU</b>7079</code> = 2020, <code>UE40<b>F</b>6400</code> = 2013, <code>GQ65Q60<b>B</b></code> = 2022.",
 "groups": [
  {"id": "tizen", "title": "Ab 2016 (Tizen)",
   "identify": "Modellnummer mit KU, MU, NU, RU, TU, AU, BU, CU, DU … bzw. QLED/Neo QLED mit Endbuchstabe R, T, A, B, C, D. Startbildschirm mit App-Leiste am unteren Rand.",
   "steps": [
     "USB-Stick (FAT32, am besten leer) an den Fernseher stecken.",
     "<b>Home</b> › <b>Einstellungen</b> (ggf. <b>Alle Einstellungen</b>) › <b>Übertragung</b> bzw. <b>Senderempfang</b> › <b>Experteneinstellungen</b>.",
     "<b>Senderliste übertragen</b> wählen und die PIN eingeben – ab Werk <kbd>0000</kbd>.",
     "<b>Auf USB exportieren</b> wählen und die Meldung mit OK bestätigen."],
   "file": "Eine <code>.zip</code>-Datei, deren Name das Modell enthält, z. B. <code>channel_list_GU55TU7079_1201.zip</code>. <b>Nicht entpacken</b> – lade die .zip-Datei direkt hoch.",
   "notes": ["Bei manchen Geräten heißt der Weg <b>Sendereinstellungen › Experteneinstellungen</b>."]},
  {"id": "2010-2015", "title": "2010 bis 2015 (Serien C, D, E, F, H, J)",
   "identify": "Modellnummer mit C, D, E, F, H oder J nach der Zollzahl, z. B. <code>UE46<b>F</b>6470</code>. Menü über die Taste <b>MENU</b>.",
   "steps": [
     "USB-Stick einstecken.",
     "<b>MENU</b> › <b>Senderempfang</b> bzw. <b>Sender</b> (2011/2012) › <b>Sendereinstellungen</b>.",
     "<b>Senderliste übertragen</b> wählen, PIN <kbd>0000</kbd> eingeben.",
     "<b>Auf USB exportieren</b> wählen."],
   "file": "Eine <code>.scm</code>-Datei (Serien C bis H), bei der J-Serie meist eine <code>.zip</code>. Der Name ist fest vorgegeben; ein vorhandener Export wird ohne Nachfrage überschrieben.",
   "notes": []},
  {"id": "2009", "title": "2009 (B-Serie)",
   "identify": "Modellnummer mit B nach der Zollzahl, z. B. <code>LE40<b>B</b>650</code>.",
   "steps": [
     "Fernseher einschalten, einmal <b>Lautstärke leiser</b> drücken.",
     "Die Taste <b>Enter</b> etwa 10 Sekunden gedrückt halten – ein verstecktes Menü öffnet sich.",
     "Dort die Senderliste auf den USB-Stick kopieren.",
     "Klappt es nicht: im Tonmenü <b>TV-Lautsprecher</b> wählen und <b>Anynet+ (HDMI-CEC)</b> ausschalten."],
   "file": "Ein Ordner mit mehreren Dateien. Diese Dateien (ohne Unterordner) in ein Zip-Archiv packen und die Endung von <code>.zip</code> in <code>.scm</code> ändern; zum Zurückspielen wieder entpacken.",
   "notes": ["Das <code>clone.bin</code>-Format mancher B-Modelle wird nicht unterstützt.", "In der Liste „Air Analog“ sind nicht alle Funktionen verfügbar."]},
 ],
 "stick_files": [
   ("<code>channel_list_….zip</code>", "Ab 2015/2016: direkt hochladen, nicht entpacken."),
   ("<code>channel_list_….scm</code>", "2010–2014: direkt hochladen."),
   ("<code>clone.bin</code>", "Wird nicht unterstützt."),
 ],
 "import": [
   "Gespeicherte Datei aus dem Editor auf den Stick kopieren. <b>Den Dateinamen nicht ändern</b> – der Fernseher sucht genau diesen Namen.",
   "Gleicher Menüweg wie beim Export, dann <b>Von USB importieren</b> wählen.",
   "Nach dem Import startet der Fernseher eventuell neu. Das ist normal."],
 "faq": [
   ("„Senderliste übertragen“ ist ausgegraut oder fehlt.", "Meist steckt kein (erkannter) USB-Stick – FAT32 formatieren und einen Stick bis 32 GB verwenden. Bei Listen, die ein Kabel- oder Sat-Anbieter vorgibt, kann die Funktion außerdem gesperrt sein; dann hilft ein Sendersuchlauf ohne Anbieterauswahl."),
   ("Die PIN 0000 funktioniert nicht.", "Dann wurde die PIN geändert. Sie lässt sich unter <b>Einstellungen › Allgemein › Systemmanager › PIN ändern</b> neu setzen."),
   ("Nach dem Import ist die Reihenfolge wieder durcheinander.", "Prüfe, ob der Fernseher automatisch nach Sendern sucht (z. B. <b>Automatische Senderaktualisierung</b> bzw. Senderlisten-Update des Anbieters) und schalte das aus."),
 ],
},
# ------------------------------------------------------------------ LG
{
 "slug": "lg", "name": "LG",
 "title": "LG Senderliste bearbeiten und Sender sortieren am PC",
 "description": "LG-Senderliste (GlobalClone00001.TLL) auf USB kopieren, im Browser sortieren, löschen und Favoriten setzen. Anleitung für webOS und ältere NetCast-Modelle.",
 "h1": "LG: Senderliste bearbeiten",
 "intro": "Bei LG hängt der Weg vom Betriebssystem ab: Neuere Geräte mit webOS kopieren die Senderliste über das normale Menü, ältere NetCast-Geräte nur über ein verstecktes Menü. Wichtig ist bei LG außerdem, wie die Sender ursprünglich gesucht wurden – siehe Hinweis unten.",
 "identify_hint": "Die webOS-Version steht unter <b>Einstellungen › Allgemein › Über dieses TV-Gerät</b> (bzw. <b>Softwareversion</b>). Grobe Faustregel über die Modellnummer: <code>…UN…</code> = 2020, <code>…UP…</code> = 2021, <code>…UQ…</code> = 2022, <code>…UR…</code> = 2023; bei OLED steht die Ziffer am Ende für das Jahr (<code>OLED55C<b>1</b></code> = 2021).",
 "groups": [
  {"id": "webos-neu", "title": "webOS 22 und neuer (ab 2022)",
   "identify": "Startbildschirm mit großen Kacheln; im Einstellungsmenü gibt es den Bereich <b>Allgemein</b> mit dem Unterpunkt <b>Sender</b> bzw. <b>Programme</b>.",
   "steps": [
     "USB-Stick einstecken (FAT32).",
     "<b>Einstellungen</b> (Zahnrad) › <b>Alle Einstellungen</b> › <b>Allgemein</b> › <b>Sender</b> (bzw. <b>Programme</b>).",
     "<b>Sender kopieren</b> (bzw. <b>Programme kopieren</b>) › <b>TV auf USB</b> wählen."],
   "file": "<code>GlobalClone00001.TLL</code>",
   "notes": []},
  {"id": "webos", "title": "webOS 1 bis 6 (ca. 2014–2021)",
   "identify": "Leiste mit App-Kacheln am unteren Bildschirmrand. Im Einstellungsmenü gibt es einen eigenen Bereich <b>Sender</b> bzw. <b>Programme</b>.",
   "steps": [
     "USB-Stick einstecken.",
     "<b>Einstellungen</b> › <b>Alle Einstellungen</b> › <b>Sender</b> (bzw. <b>Programme</b>), ggf. › <b>Sendereinstellungen</b>.",
     "<b>Sender kopieren</b> › <b>TV auf USB</b>.",
     "Fehlt der Punkt: Taste <b>Einstellungen</b> gedrückt halten, bis das Menü verschwindet und die Senderinfo erscheint, dann schnell <kbd>1105</kbd> + OK. Im Hotel-Menü gibt es die Kopierfunktion ebenfalls."],
   "file": "<code>GlobalClone00001.TLL</code>. Manche Modelle von 2014/2015 schreiben zusätzlich eine Datei wie <code>xxLB….TLL</code>.",
   "notes": ["Liegen beide Dateien auf dem Stick, liest der Fernseher beim Import nur die modellspezifische Datei. Bearbeite in diesem Fall diese Datei – oder lösche sie und bearbeite die GlobalClone-Datei."]},
  {"id": "netcast", "title": "NetCast (bis ca. 2013)",
   "identify": "Ältere Menüoptik ohne App-Leiste, Modellnummern wie <code>…LA…</code>, <code>…LN…</code>, <code>…LM…</code>, <code>…LS…</code>, <code>…CS…</code>, <code>…PM…</code> oder älter.",
   "steps": [
     "USB-Stick einstecken.",
     "Taste <b>Settings</b> bzw. <b>Menu/Home</b> gedrückt halten, bis das Menü wieder verschwindet.",
     "Solange noch die Senderinfo zu sehen ist, schnell <kbd>1105</kbd> + OK eingeben.",
     "Im versteckten Menü <b>TV Link Loader</b> bzw. <b>USB Cloning</b> wählen und auf USB exportieren. Die vorgeschlagene Nummer <code>0001</code> kann bleiben."],
   "file": "Eine Datei wie <code>xxLM620S-ZE00001.TLL</code> (Modellname im Dateinamen).",
   "notes": ["Bei Modellen von 2012/2013 mit sehr alter Software reicht die normale Fernbedienung nicht – dann ist eine programmierbare Universalfernbedienung nötig (z. B. Logitech Harmony mit Gerät „LG 26LE5300-UE“, Taste „In-Start“).", "Einige Modelle (z. B. xxLM640T) können wegen Fehlern in der Software nicht bearbeitet werden. Bei <code>…LP…</code>-Modellen werden nur Satellitensender unterstützt."]},
 ],
 "stick_files": [
   ("<code>GlobalClone00001.TLL</code>", "webOS: direkt hochladen."),
   ("<code>xx<i>Modell</i>….TLL</code>", "NetCast bzw. manche webOS-Geräte 2014/2015: direkt hochladen."),
 ],
 "import": [
   "Bearbeitete Datei unter gleichem Namen auf den Stick kopieren.",
   "Gleicher Menüweg wie beim Export, dann <b>USB auf TV</b> wählen."],
 "warning": "<b>Wichtig bei LG:</b> Die Liste lässt sich nur zuverlässig bearbeiten, wenn bei der Sendersuche <b>kein Anbieter</b> ausgewählt wurde (also „Keiner“, „Andere“ oder „Alle“ bzw. Blindsuche statt z. B. „Astra 19.2 Liste“ oder einem Kabelanbieter). Lade außerdem keine Listen von anderen Modellen oder älteren Software-Ständen und mache nach einem Software-Update erst einen neuen Suchlauf.",
 "faq": [
   ("Nach dem Import springen Sender wieder an andere Plätze.", "Das passiert fast immer bei vorsortierten Anbieterlisten. Sendersuchlauf mit Anbieter „Andere“ bzw. „Keiner“ wiederholen, neu exportieren und erneut sortieren."),
   ("Der Editor meldet „Program #0 assigned to multiple channels“.", "Der Hinweis betrifft gelöschte Sender und ist harmlos – das Desktop-Programm ChanSort meldet ihn genauso."),
   ("Im Menü fehlt „Sender kopieren“.", "Hotel-Menü über langes Drücken der Einstellungstaste und <kbd>1105</kbd> probieren (siehe oben). Bei manchen Modellen ist die Funktion nur dort zu finden."),
 ],
},
# ------------------------------------------------------------------ Sony
{
 "slug": "sony", "name": "Sony",
 "title": "Sony Bravia Senderliste bearbeiten – Sender sortieren am PC",
 "description": "Sony-Bravia-Senderliste (sdb.xml) per USB exportieren, im Browser sortieren, umbenennen und Favoriten bearbeiten. Anleitung für Android TV, Google TV und KDL-Modelle.",
 "h1": "Sony Bravia: Sender sortieren",
 "intro": "Sony-Fernseher nennen die Funktion „Programmlistenübertragung“. Sie steckt etwas versteckt in den technischen Einstellungen, ist aber bei den meisten Modellen ohne Geheimcode erreichbar.",
 "identify_hint": "Modelle mit Android TV oder Google TV erkennst du am Startbildschirm mit Google-Apps (ab etwa 2015, Modellnummern <code>KD-…</code>, <code>XR-…</code>, <code>K-…</code>). Ältere Modelle heißen meist <code>KDL-…</code>.",
 "groups": [
  {"id": "android", "title": "Android TV / Google TV",
   "identify": "Startbildschirm mit Google-Apps, Modellnummer <code>KD-…</code>, <code>XR-…</code> oder <code>K-…</code>.",
   "steps": [
     "USB-Stick einstecken. Andere USB-Geräte vorher abziehen.",
     "<b>Einstellungen</b> › <b>Fernsehen</b> bzw. <b>Kanäle</b> › <b>Kanaleinstellung</b> › <b>Digitale Einstellungen</b> › <b>Technische Einstellungen</b>.",
     "<b>Programmlistenübertragung</b> › <b>Export</b> wählen und mit OK bestätigen."],
   "file": "<code>sdb.xml</code>, je nach Modell in einem Unterordner.",
   "notes": ["Liegen mehrere Dateien im Export, wähle im Editor einfach den ganzen Ordner."]},
  {"id": "kdl", "title": "KDL-Modelle 2012–2014",
   "identify": "Modellnummer <code>KDL-…</code>, Menü mit horizontaler Leiste.",
   "steps": [
     "USB-Stick einstecken.",
     "<b>Home</b> › <b>Einstellungen</b> › <b>Digitale Einstellungen</b> › <b>Programmlistenübertragung</b>.",
     "<b>Export</b> wählen."],
   "file": "<code>sdb.xml</code>",
   "notes": []},
 ],
 "stick_files": [
   ("<code>sdb.xml</code>", "Direkt hochladen."),
   ("mehrere Dateien bzw. Ordner", "Den ganzen Ordner wählen – der Editor findet die richtige Datei."),
 ],
 "import": [
   "Bearbeitete <code>sdb.xml</code> an dieselbe Stelle auf dem Stick kopieren.",
   "Gleicher Menüweg, dann <b>Import</b> wählen.",
   "Wird die neue Liste nicht angezeigt: Fernseher neu starten, dazu die Power-Taste der Fernbedienung etwa 5 Sekunden gedrückt halten."],
 "faq": [
   ("„Programmlistenübertragung“ fehlt.", "Der Punkt erscheint bei manchen Geräten nur, wenn gerade ein Fernsehsender (nicht eine App) läuft und ein Stick erkannt wurde."),
   ("Der Export bricht ab.", "Stick mit FAT32 formatieren und nur einen Stick anschließen."),
 ],
},
# ------------------------------------------------------------------ Philips
{
 "slug": "philips", "name": "Philips",
 "title": "Philips Senderliste bearbeiten – Sender am PC sortieren",
 "description": "Philips-Senderliste mit „Senderliste kopieren“ auf USB übertragen, im Browser sortieren und löschen und zurück auf den Fernseher spielen. Für Android TV, Google TV und ältere Modelle.",
 "h1": "Philips: Senderliste bearbeiten",
 "intro": "Philips verwendet viele verschiedene Dateiformate, der Weg im Menü ist aber fast immer gleich: <b>Senderliste kopieren</b>. Philips schreibt dabei einen ganzen Ordner auf den Stick – lade im Editor deshalb immer den <b>Ordner</b> hoch.",
 "identify_hint": "Philips-Fernseher mit Android TV bzw. Google TV (ca. ab 2015) haben einen Startbildschirm mit Google-Apps. Ältere Modelle (Modellnummern wie <code>…PFL…</code>) haben ein eigenes Philips-Menü.",
 "groups": [
  {"id": "android", "title": "Android TV / Google TV",
   "identify": "Startbildschirm mit Google-Apps, Modellnummern wie <code>55PUS8…</code>, <code>65OLED…</code>, <code>50PML…</code>.",
   "steps": [
     "USB-Stick einstecken (FAT32, möglichst leer).",
     "<b>Einstellungen</b> (ggf. <b>Alle Einstellungen</b>) › <b>Sender</b> bzw. <b>Kanäle</b> › <b>Senderliste kopieren</b>.",
     "<b>Auf USB kopieren</b> wählen. Fragt der Fernseher nach einem Code: ab Werk meist <kbd>1234</kbd>."],
   "file": "Ordner <code>PhilipsChannelMaps</code> mit Unterordnern wie <code>ChannelMap_100</code> oder <code>ChannelMap_110</code>.",
   "notes": ["Im Editor <b>Ordner wählen</b> und den Ordner <code>PhilipsChannelMaps</code> angeben."]},
  {"id": "aelter", "title": "Ältere Modelle (ohne Android)",
   "identify": "Eigenes Philips-Menü, Modellnummern wie <code>42PFL…</code>, <code>47PFL…</code>.",
   "steps": [
     "USB-Stick einstecken.",
     "<b>Menü</b> › <b>Einstellungen</b> › <b>Sendereinstellungen</b> › <b>Senderliste kopieren</b>.",
     "<b>Auf USB kopieren</b> wählen."],
   "file": "Ordner <code>Repair</code> mit Unterordner <code>ChannelList</code> oder einer Datei wie <code>CM_TPM1013E_LA_CK.xml</code>.",
   "notes": ["Die .xml-Datei ist oft <b>versteckt</b>, sichtbar ist nur eine .bin-Datei. Wähle im Editor den ganzen Ordner <code>Repair</code>, dann ist sie automatisch dabei."]},
 ],
 "stick_files": [
   ("<code>PhilipsChannelMaps\\ChannelMap_…</code>", "Android/Google TV: Ordner <code>PhilipsChannelMaps</code> wählen."),
   ("<code>Repair\\…</code>", "Ältere Modelle: Ordner <code>Repair</code> wählen."),
 ],
 "import": [
   "Im Editor speichern. Bei mehreren Dateien bekommst du eine .zip – entpacke sie und ersetze damit die Dateien im Ordner auf dem Stick. <b>Ordnerstruktur und Dateinamen nicht ändern.</b>",
   "Gleicher Menüweg, dann <b>Auf Fernseher kopieren</b>.",
   "Ist danach noch die alte Liste zu sehen: Fernseher ausschalten, Netzstecker ziehen, etwa eine Minute warten und wieder einstecken."],
 "faq": [
   ("Der Editor meldet eine falsche Prüfsumme.", "Das kommt bei manchen Philips-Dateien vor. Der Editor fragt, wie er damit umgehen soll – beim Speichern wird die Prüfsumme neu berechnet."),
   ("„Senderliste kopieren“ fehlt im Menü.", "Bei einigen Modellen erscheint der Punkt erst, wenn ein USB-Stick erkannt wurde. Je nach Ländereinstellung bzw. Anbieterliste kann er auch fehlen."),
 ],
},
# ------------------------------------------------------------------ Panasonic
{
 "slug": "panasonic", "name": "Panasonic",
 "title": "Panasonic Senderliste bearbeiten – Viera Sender sortieren am PC",
 "description": "Panasonic-Senderliste per USB oder SD-Karte exportieren, im Browser sortieren und zurückspielen. Anleitung für Viera, Android-TV und Modelle mit Hotel-Menü.",
 "h1": "Panasonic: Sender sortieren",
 "intro": "Bei Panasonic gibt es besonders viele Varianten: normale Menüfunktion, Hotel-Menü oder einen Code mit vorbereitetem USB-Stick. Nicht jedes Modell lässt sich bearbeiten – unten steht, welche gehen.",
 "identify_hint": "Viera-Modelle ohne Android haben ein eigenes Panasonic-Menü (Startbildschirm „my Home Screen“). Android-TV-Modelle haben Google-Apps auf dem Startbildschirm. Die Serie steht in der Modellnummer, z. B. <code>TX-55<b>LX</b>700E</code>.",
 "groups": [
  {"id": "viera-neu", "title": "Viera (ohne Android) – neuere Software",
   "identify": "Panasonic-Menü mit <b>Setup</b> bzw. <b>Einstellungen</b>, z. B. Serien E, F, G, J (nicht MX/JX/LX).",
   "steps": [
     "USB-Stick einstecken.",
     "<b>Menü</b> › <b>Setup</b> › <b>Andere Einstellungen</b> › <b>Senderliste austauschen</b> (bzw. „Channel List Transfer“).",
     "<b>Senderliste exportieren</b> wählen."],
   "file": "<code>svl.bin</code> oder <code>svl.db</code>",
   "notes": []},
  {"id": "viera-alt", "title": "Viera – ältere Software (Code-Methode)",
   "identify": "Wenn es den Punkt „Senderliste austauschen“ nicht gibt.",
   "steps": [
     "Auf einem USB-Stick bzw. einer SD-Karte (FAT32) eine leere Datei oder einen leeren Ordner mit dem Namen <code>hotel.pwd</code> anlegen.",
     "Stick bzw. Karte in den Fernseher stecken – er fragt nach einem Passwort.",
     "<kbd>4850</kbd> eingeben, um die Liste auf den Stick zu kopieren."],
   "file": "<code>svl.bin</code> oder <code>svl.db</code>",
   "notes": ["Zum Zurückspielen später <kbd>4851</kbd> eingeben."]},
  {"id": "android-lx", "title": "Android TV LS/LX 500–700 (ab 2022)",
   "identify": "Google-Apps auf dem Startbildschirm, Modellnummer mit <code>LS5…</code>, <code>LX5…</code>, <code>LX6…</code>, <code>LX7…</code>.",
   "steps": [
     "<b>MENU</b> › <b>Bild</b> › <b>Bildmodus</b> › <b>Benutzerdefiniert</b> › <b>Kontrast</b> wählen und dann <b>6× OK</b> drücken – ein verstecktes Menü öffnet sich.",
     "<b>Hotel Menu</b> › <b>Hotel Mode Activate</b> wählen.",
     "Weiter unten <b>TV to USB</b> wählen.",
     "<b>Stick nicht abziehen</b>, auch wenn „Upload OK“ erscheint. Stattdessen über <b>HOME › Benachrichtigungen › USB-Gerät › Auswerfen</b> abmelden."],
   "file": "Ordnerstruktur mit <code>mnt/vendor/tvdata/database/tv.db</code> – im Editor den ganzen Ordner wählen.",
   "notes": ["Zum Zurückspielen im selben Menü <b>USB to TV</b> wählen."]},
  {"id": "mx", "title": "MX600 / MX700 / MZ800 und Fire-TV-Modelle",
   "identify": "Modelle wie <code>TX-43MX600E</code>, <code>TX-55MX700E</code>, <code>TX-55MZ800E</code> oder Panasonic mit Fire TV.",
   "steps": [
     "<b>MX600 und ähnliche:</b> <b>Einstellungen</b> › <b>Installation</b> › <b>Satelliten-Einstellungen</b> › <b>Sat-Senderliste</b> › <b>Sat-Senderliste speichern</b> (nur Satellit).",
     "<b>MX700, MZ800:</b> die Senderliste über die Exportfunktion im Sendermenü speichern.",
     "<b>Fire-TV-Modelle (z. B. MXW834):</b> Export über das Sendermenü."],
   "file": "<code>.sdx</code> (MX600, Fire TV) bzw. <code>channellist.txt</code> (MX700, MZ800)",
   "notes": ["Der genaue Menüname weicht bei diesen Modellen stark ab – such im Handbuch nach „Senderliste speichern“ bzw. „exportieren“."]},
 ],
 "stick_files": [
   ("<code>svl.bin</code> / <code>svl.db</code>", "Viera: direkt hochladen."),
   ("<code>…/tv.db</code>", "Android LS/LX 500–700: ganzen Ordner wählen."),
   ("<code>.sdx</code> / <code>channellist.txt</code>", "MX-Serien, Fire TV: direkt hochladen."),
   ("<code>settingsDB_enc.db</code>, <code>channel_list.bin</code>", "JXW600 / JXW800: wird <b>nicht</b> unterstützt (verschlüsselt)."),
 ],
 "import": [
   "Bearbeitete Datei an dieselbe Stelle auf dem Stick kopieren.",
   "Gleicher Weg wie beim Export: <b>Senderliste importieren</b>, Code <kbd>4851</kbd> bzw. <b>USB to TV</b>."],
 "faq": [
   ("Die Sendernamen fehlen im Editor.", "Bei analogen Sendern speichern manche Panasonic-Geräte keine Namen. Digitale Sender sollten Namen haben."),
   ("Mein Android-Modell (vor 2022) wird nicht erkannt.", "Diese Modelle speichern die Liste verschlüsselt. Sie lassen sich leider nicht bearbeiten."),
 ],
},
# ------------------------------------------------------------------ TCL
{
 "slug": "tcl", "name": "TCL / Thomson",
 "title": "TCL Senderliste bearbeiten – Kanalliste sortieren am PC",
 "description": "TCL- und Thomson-Kanalliste (.tar) auf USB exportieren, im Browser sortieren, löschen und zurück auf den Fernseher spielen. Anleitung für Android TV und Google TV.",
 "h1": "TCL & Thomson: Kanalliste sortieren",
 "intro": "TCL-Fernseher mit Android TV oder Google TV (und baugleiche Thomson-Modelle) exportieren die Kanalliste als <code>.tar</code>-Archiv. Das Archiv lädst du unverändert hoch.",
 "identify_hint": "Fast alle aktuellen TCL-Modelle nutzen Android TV oder Google TV. Die Menüpunkte heißen bei TCL „Kanal“ statt „Sender“.",
 "groups": [
  {"id": "google", "title": "Android TV / Google TV",
   "identify": "Google-Apps auf dem Startbildschirm, Einstellungen mit dem Bereich <b>Kanäle & Eingänge</b>.",
   "steps": [
     "USB-Stick einstecken – <b>FAT32, höchstens 32 GB</b>. Manche Modelle erkennen NTFS oder exFAT beim Export nicht.",
     "<b>Einstellungen</b> (bei Google TV über das Dashboard) › <b>Kanäle & Eingänge</b> › <b>Kanal</b>.",
     "<b>Kanalliste übertragen</b> wählen und das Kennwort eingeben – ab Werk meist <kbd>1234</kbd> (manchmal <kbd>0000</kbd>).",
     "<b>Exportieren auf USB</b> wählen."],
   "file": "Eine <code>.tar</code>-Datei. <b>Nicht entpacken</b> – direkt hochladen.",
   "notes": []},
 ],
 "stick_files": [
   ("<code>….tar</code>", "Direkt hochladen, nicht entpacken."),
 ],
 "import": [
   "Bearbeitete .tar-Datei unter gleichem Namen auf den Stick kopieren.",
   "Gleicher Menüweg, dann <b>Importieren von USB</b> und die .tar-Datei auswählen."],
 "faq": [
   ("Der Fernseher findet den Stick nicht.", "Stick mit FAT32 formatieren und einen Stick bis 32 GB nehmen."),
   ("Das Kennwort 1234 stimmt nicht.", "Probiere <kbd>0000</kbd>. Wurde ein eigenes Kennwort für die Kindersicherung vergeben, gilt dieses."),
 ],
},
# ------------------------------------------------------------------ Hisense
{
 "slug": "hisense", "name": "Hisense",
 "title": "Hisense Senderliste bearbeiten – Sender sortieren am PC",
 "description": "Hisense-Senderliste (VIDAA) auf USB exportieren, im Browser sortieren und zurückspielen. Mit Hinweisen zur Anbieterauswahl „Andere“.",
 "h1": "Hisense: Senderliste bearbeiten",
 "intro": "Hisense-Fernseher mit VIDAA exportieren die Senderliste direkt aus dem Menü „Sender bearbeiten“. Entscheidend ist, dass bei der Sendersuche der Anbieter <b>„Andere“</b> gewählt wurde.",
 "identify_hint": "Die meisten Hisense-Smart-TVs ab 2016 nutzen VIDAA (VIDAA U). Ältere oder einfache Modelle exportieren andere Dateien – siehe Tabelle unten.",
 "groups": [
  {"id": "vidaa", "title": "VIDAA / VIDAA U (Smart-TVs ab 2016)",
   "identify": "Hisense-Startbildschirm mit VIDAA-Logo bzw. Hisense-App-Leiste.",
   "steps": [
     "USB-Stick einstecken.",
     "<b>Einstellungen</b> (Zahnrad) › <b>Sender</b> › <b>Sender bearbeiten</b>.",
     "<b>Auf USB exportieren</b> wählen."],
   "file": "<code>servicelist.db</code> (ab 2017) oder <code>channel.db</code> (2016)",
   "notes": []},
  {"id": "aelter", "title": "Ältere und einfache Modelle",
   "identify": "Ohne VIDAA, z. B. <code>LTDN40D50TS</code>.",
   "steps": [
     "Export über das Sendermenü oder ein Hotel-/Servicemenü – das ist je nach Modell verschieden.",
     "Einige Modelle nutzen dieselbe Technik wie Sharp: <a href=\"sharp.html\">Anleitung für Sharp &amp; baugleiche Geräte</a>."],
   "file": "<code>HIS_DVB.BIN</code> oder die drei Dateien <code>HIS_FAV.BIN</code>, <code>HIS_SVL.BIN</code>, <code>HIS_TSL.BIN</code> bzw. .csv-Dateien",
   "notes": ["Bei mehreren Dateien den ganzen Ordner im Editor wählen."]},
 ],
 "stick_files": [
   ("<code>servicelist.db</code> / <code>channel.db</code>", "VIDAA: direkt hochladen."),
   ("<code>HIS_….BIN</code>", "Ältere Modelle: Ordner wählen."),
   ("<code>….csv</code>", "Siehe <a href=\"sharp.html\">Sharp</a>."),
 ],
 "import": [
   "Bearbeitete Datei auf den Stick kopieren.",
   "<b>Sender bearbeiten</b> › <b>Von USB importieren</b>.",
   "Danach <b>Exit</b> drücken – das offene Menü zeigt die neue Liste noch nicht an. Der Fernseher springt auf den ersten Sender der ersten Liste; zur Satellitenliste kommst du über <b>CH.List</b> › Pfeil links › OK › Liste wählen › OK."],
 "warning": "<b>Wichtig bei Hisense:</b> Nur wenn bei der Ersteinrichtung bzw. beim Suchlauf der Anbieter <b>„Andere“</b> gewählt wurde, lässt sich die Liste exportieren und bearbeiten. Anbieterlisten wie „ASTRA_LCN“, „ORS“ oder „SKY Deutschland“ enthalten beim Export keine Senderdaten.",
 "faq": [
   ("Die exportierte Datei ist leer bzw. der Editor findet keine Sender.", "Fast immer wurde eine Anbieterliste verwendet. Suchlauf mit Anbieter „Andere“ wiederholen und neu exportieren."),
   ("Nach dem Import sehe ich nur die Antennen-Sender.", "Über <b>CH.List</b> auf die Satellitenliste umschalten (siehe oben)."),
 ],
},
# ------------------------------------------------------------------ Grundig
{
 "slug": "grundig", "name": "Grundig",
 "title": "Grundig Senderliste bearbeiten – Sender sortieren am PC",
 "description": "Grundig-Senderliste per USB exportieren und im Browser sortieren. Welche Grundig-Modelle unterstützt werden und wo der Export im Menü steckt.",
 "h1": "Grundig: Sender sortieren",
 "intro": "Grundig hat über die Jahre unterschiedliche Technik verbaut. Ob und wie der Export geht, hängt deshalb stark vom Modell ab. Am schnellsten erkennst du es an den Dateien, die der Fernseher auf den Stick schreibt.",
 "identify_hint": "Such im Menü nach „Senderliste“, „Programmliste“ oder „USB“ – bei vielen Modellen gibt es einen Punkt <b>Senderliste exportieren</b>. Andernfalls hilft das Handbuch deines Modells (Suchbegriff „USB“).",
 "groups": [
  {"id": "xml", "title": "Modelle mit dvb…_config.xml",
   "identify": "Der Export schreibt Dateien wie <code>dvbs_config.xml</code>, <code>dvbc_config.xml</code> oder <code>dvbt_config.xml</code>.",
   "steps": [
     "USB-Stick einstecken (FAT32).",
     "<b>Menü</b> › <b>Einstellungen</b> bzw. <b>Installation</b> › <b>Senderliste</b> › <b>Senderliste exportieren</b> (Bezeichnung je nach Modell).",
     "Den Stick als Ziel wählen und warten, bis der Export fertig ist."],
   "file": "<code>dvb…_config.xml</code> – direkt hochladen.",
   "notes": []},
  {"id": "cmdb", "title": "Modelle mit …_cmdb_….bin oder cvt_database.dat",
   "identify": "Der Export schreibt mehrere <code>.bin</code>-Dateien bzw. <code>cvt_database.dat</code> und eine .csv-Datei (z. B. <code>24 GHB 5944</code>).",
   "steps": [
     "Export über das normale Menü oder ein Hotel-/Servicemenü – diese Geräte sind technisch baugleich mit Sharp und anderen Marken.",
     "Alle Schritte und Tastencodes: <a href=\"sharp.html\">Anleitung für Sharp &amp; baugleiche Geräte</a>."],
   "file": "Mehrere Dateien – im Editor den ganzen Ordner wählen.",
   "notes": []},
 ],
 "stick_files": [
   ("<code>dvb…_config.xml</code>", "Direkt hochladen."),
   ("<code>…_cmdb_….bin</code>", "Ordner wählen."),
   ("<code>cvt_database.dat</code> + <code>….csv</code>", "Ordner wählen, siehe <a href=\"sharp.html\">Sharp</a>."),
 ],
 "import": [
   "Bearbeitete Dateien unter gleichem Namen auf den Stick kopieren.",
   "Im selben Menü <b>Senderliste importieren</b> wählen."],
 "faq": [
   ("Mein Grundig mit Fire TV / Google TV bietet keinen Export an.", "Bei diesen Modellen ist uns kein allgemeiner Exportweg bekannt. Wenn du einen findest, schreib uns – wir ergänzen die Anleitung."),
 ],
},
# ------------------------------------------------------------------ Sharp & baugleiche
{
 "slug": "sharp", "name": "Sharp",
 "title": "Sharp Senderliste bearbeiten – auch Blaupunkt, Dyon, Changhong",
 "description": "Senderliste bei Sharp, Blaupunkt, Dyon, Changhong, alphatronics und JTC Genesis per USB exportieren (auch über Hotel- und Servicemenü) und im Browser sortieren.",
 "h1": "Sharp & baugleiche Geräte",
 "intro": "Viele Fernseher von Sharp, Blaupunkt, Dyon, Changhong, alphatronics, JTC Genesis sowie einige Hisense- und Grundig-Modelle haben dieselbe Technik. Sie exportieren .csv-Dateien plus eine oder mehrere Datendateien.",
 "identify_hint": "Typische Modelle: Sharp <code>LC-xxCFE4142E</code>, <code>LC-xxUI7552E</code>, <code>xxBJ1E</code>/<code>xxBJ3E</code>/<code>xxBJ5E</code>; Blaupunkt <code>B40A148TCSFHD</code>; Changhong <code>LED32E2200ST2</code>; Dyon <code>Live 22 Pro</code>, <code>ENTER 32 Pro X</code>; Grundig <code>24 GHB 5944</code>.",
 "groups": [
  {"id": "menue", "title": "Export im normalen Menü",
   "identify": "Viele Modelle haben im Sender- bzw. Installationsmenü einen Punkt zum Export auf USB.",
   "steps": [
     "USB-Stick einstecken.",
     "Im Menü <b>Sender</b> bzw. <b>Installation</b> nach <b>Export</b>, <b>Senderliste kopieren</b> oder <b>USB</b> suchen.",
     "Export starten. Sharp Aquos <code>xxBJ1E</code> und ähnliche haben dafür ein eigenes Untermenü."],
   "file": "Siehe Tabelle unten.",
   "notes": []},
  {"id": "geheim", "title": "Export im Hotel- oder Servicemenü",
   "identify": "Wenn im normalen Menü kein Export zu finden ist.",
   "steps": [
     "<b>Hotelmenü</b>: <kbd>MENU</kbd> und dann <kbd>7906</kbd> – oder <kbd>MENU</kbd> <kbd>4588</kbd>.",
     "<b>Servicemenü</b>: <kbd>MENU</kbd> <kbd>1147</kbd>, <kbd>MENU</kbd> <kbd>11471147</kbd> oder <kbd>SOURCE</kbd> <kbd>2580</kbd>.",
     "Dort nur die Import-/Export-Funktion verwenden."],
   "file": "Siehe Tabelle unten.",
   "notes": ["<b>Ändere im Servicemenü keine anderen Werte</b> – das kann den Fernseher beschädigen."]},
 ],
 "stick_files": [
   ("<code>DVBS_Program.csv</code> + <code>cvt_database.dat</code>", "Ordner wählen."),
   ("<code>DVBS_CHANNEL_TABLE.csv</code> + <code>dtv_cmdb….bin</code>", "Ordner wählen."),
   ("<code>MS…_DVBS_CHANNEL_TABLE.csv</code> + <code>MS…_HOTELMODE_TABLE.json</code>", "Ordner wählen."),
 ],
 "import": [
   "Alle Dateien wieder auf den Stick kopieren – bei manchen Modellen (z. B. Sharp <code>xxBJ1E</code>) sind <b>alle vier Dateien</b> für den Import nötig.",
   "Im selben Menü den Import starten."],
 "faq": [
   ("Welche Datei soll ich hochladen?", "Am einfachsten den ganzen Ordner – der Editor sucht sich die passenden Dateien selbst."),
 ],
},
# ------------------------------------------------------------------ Toshiba
{
 "slug": "toshiba", "name": "Toshiba",
 "title": "Toshiba Senderliste bearbeiten – Sender sortieren am PC",
 "description": "Toshiba-Senderliste auf USB exportieren und im Browser sortieren. Für neuere Modelle (Sat-Senderliste) und ältere Modelle mit verstecktem Menü.",
 "h1": "Toshiba: Sender sortieren",
 "intro": "Neuere Toshiba-Fernseher nutzen dieselbe Technik wie Telefunken und Medion. Ältere Modelle haben ein verstecktes Menü, das über die Tasten am Gerät geöffnet wird.",
 "identify_hint": "Ab etwa 2017 gibt es im Installationsmenü den Punkt <b>Satelliten-Einstellungen</b>. Ältere Modelle haben Modellnummern mit RL, SL, TL, UL, VL, WL, XL oder YL (Serien 8xx/9xx).",
 "groups": [
  {"id": "neu", "title": "Ab ca. 2017",
   "identify": "Menü mit <b>Installation › Satelliten-Einstellungen</b>.",
   "steps": [
     "USB-Stick einstecken.",
     "<b>Menü</b> › <b>Einstellungen</b> › <b>Installation</b> › <b>Satelliten-Einstellungen</b> › <b>Sat-Senderliste</b>.",
     "<b>Sat-Senderliste speichern</b> wählen."],
   "file": "<code>.sdx</code> (nur Satellitensender). Manche Modelle schreiben stattdessen eine <code>settingsDB.db</code>.",
   "notes": ["Mehr dazu: <a href=\"telefunken-medion.html\">Telefunken, Medion &amp; baugleiche Geräte</a>."]},
  {"id": "alt", "title": "Ältere Modelle (Serien 8xx/9xx)",
   "identify": "Modellnummern mit RL, SL, TL, UL, VL, WL, XL oder YL.",
   "steps": [
     "Fernseher einschalten und einen (am besten leeren) USB-Stick einstecken. Die Frage „Mediaplayer starten?“ mit <b>Nein</b> beantworten.",
     "Auf der Fernbedienung einmal <b>Stumm</b> drücken und loslassen.",
     "Dann <b>Stumm</b> gedrückt halten und gleichzeitig am <b>Fernseher selbst</b> (nicht auf der Fernbedienung) die Taste <b>Pfeil nach unten</b> drücken.",
     "Im Menü <b>TV to USB</b> wählen. Danach <b>Exit</b> drücken und den Stick abziehen."],
   "file": "Eine <code>.zip</code> mit <code>chmgt.db</code>, <code>dvbSysData.db</code> und <code>dvbMainData.db</code> – direkt hochladen.",
   "notes": ["Daten auf dem Stick können dabei gelöscht werden."]},
 ],
 "stick_files": [
   ("<code>….sdx</code>", "Neuere Modelle: direkt hochladen."),
   ("<code>settingsDB.db</code>", "Direkt hochladen."),
   ("<code>….zip</code> mit chmgt.db", "Ältere Modelle: direkt hochladen."),
 ],
 "import": [
   "Bearbeitete Datei auf den Stick kopieren.",
   "Neuere Modelle: <b>Sat-Senderliste laden</b>. Ältere: im versteckten Menü <b>USB to TV</b>."],
 "faq": [],
},
# ------------------------------------------------------------------ Telefunken / Medion / Vestel
{
 "slug": "telefunken-medion", "name": "Telefunken, Medion & Co.",
 "title": "Telefunken, Medion, ITT Senderliste bearbeiten (.sdx)",
 "description": "Sat-Senderliste (.sdx) bei Telefunken, Medion, ITT, Nabo, ok., PEAQ, Schaub Lorenz und Silva Schneider exportieren und im Browser sortieren.",
 "h1": "Telefunken, Medion, ITT & Co.",
 "intro": "Telefunken, Medion, ITT, Nabo, ok., PEAQ, Schaub Lorenz, Silva Schneider sowie neuere Toshiba- und einzelne Panasonic-Modelle nutzen dieselbe Technik. Sie können die <b>Satelliten</b>-Senderliste als <code>.sdx</code>-Datei speichern.",
 "identify_hint": "Im Menü gibt es <b>Installation › Satelliten-Einstellungen › Sat-Senderliste</b>.",
 "groups": [
  {"id": "sdx", "title": "Sat-Senderliste (.sdx)",
   "identify": "Die meisten Fernseher der genannten Marken.",
   "steps": [
     "USB-Stick einstecken.",
     "<b>Menü</b> › <b>Einstellungen</b> › <b>Installation</b> › <b>Satelliten-Einstellungen</b> › <b>Sat-Senderliste</b>.",
     "<b>Sat-Senderliste speichern</b> wählen."],
   "file": "Eine <code>.sdx</code>-Datei – direkt hochladen.",
   "notes": ["Das Verfahren gilt nur für Satellitensender, nicht für Kabel oder Antenne."]},
  {"id": "medion-android", "title": "Medion Android-TVs",
   "identify": "Medion mit Android TV, z. B. <code>X15567 (MD 31555)</code>.",
   "steps": [
     "Im Sendermenü nach einer Export- bzw. Sicherungsfunktion auf USB suchen.",
     "Die exportierte Datei hochladen."],
   "file": "<code>senderliste.txt</code>",
   "notes": []},
 ],
 "stick_files": [
   ("<code>….sdx</code>", "Direkt hochladen."),
   ("<code>senderliste.txt</code>", "Medion Android: direkt hochladen."),
 ],
 "import": [
   "Bearbeitete .sdx-Datei auf den Stick kopieren.",
   "<b>Sat-Senderliste</b> › <b>Sat-Senderliste laden</b> wählen und die Datei auswählen."],
 "faq": [
   ("Kann ich auch Kabel- oder Antennensender sortieren?", "Mit diesem Verfahren nicht – die .sdx-Datei enthält nur Satellitensender."),
 ],
},
# ------------------------------------------------------------------ Loewe
{
 "slug": "loewe", "name": "Loewe",
 "title": "Loewe Senderliste bearbeiten – Sender sortieren am PC",
 "description": "Loewe-Senderliste per USB exportieren und im Browser sortieren. Welche Loewe-Modelle unterstützt werden.",
 "h1": "Loewe: Senderliste bearbeiten",
 "intro": "Loewe-Fernseher, die beim Export eine <code>servicelist.xml</code> schreiben, lassen sich mit dem Editor bearbeiten. Einige neuere Modelle nutzen Hisense-Technik und exportieren <code>servicelist.db</code> bzw. <code>channel.db</code> – dann gilt die Hisense-Anleitung.",
 "identify_hint": "Such im Menü nach „Programmliste“, „Senderliste“ oder „USB“. Den genauen Weg nennt das Handbuch deines Modells (Suchbegriff „USB“ oder „exportieren“).",
 "groups": [
  {"id": "xml", "title": "Modelle mit servicelist.xml",
   "identify": "Der Export schreibt eine <code>servicelist.xml</code>.",
   "steps": [
     "USB-Stick einstecken.",
     "Im Menü <b>Einstellungen</b> › <b>Sender</b> bzw. <b>Programme</b> die Funktion zum Export auf USB wählen."],
   "file": "<code>servicelist.xml</code> – direkt hochladen.",
   "notes": []},
  {"id": "hisense", "title": "Modelle mit Hisense-Technik",
   "identify": "Der Export schreibt <code>servicelist.db</code> oder <code>channel.db</code>.",
   "steps": ["Siehe <a href=\"hisense.html\">Anleitung für Hisense</a>."],
   "file": "<code>servicelist.db</code> / <code>channel.db</code>",
   "notes": []},
 ],
 "stick_files": [
   ("<code>servicelist.xml</code>", "Direkt hochladen."),
   ("<code>servicelist.db</code> / <code>channel.db</code>", "Direkt hochladen (Hisense-Technik)."),
 ],
 "import": [
   "Bearbeitete Datei unter gleichem Namen auf den Stick kopieren.",
   "Im selben Menü den Import starten."],
 "faq": [
   ("Mein Loewe schreibt andere Dateien.", "Dann wird das Modell vermutlich nicht unterstützt. Lade die Dateien trotzdem einmal hoch – der Editor sagt dir, ob er das Format kennt."),
 ],
},
# ------------------------------------------------------------------ Receiver
{
 "slug": "receiver", "name": "Receiver & PC",
 "title": "Senderliste für Sat-Receiver bearbeiten – Enigma2, VDR, SAT>IP",
 "description": "Senderlisten von Enigma2-Receivern (Dreambox, VU+), VDR, SAT>IP (.m3u), Xoro, Strong, TechniSat-Receivern und weiteren im Browser sortieren.",
 "h1": "Sat-Receiver & PC-Software",
 "intro": "Neben Fernsehern unterstützt der Editor auch die Senderlisten vieler Receiver und PC-Programme.",
 "identify_hint": "",
 "groups": [
  {"id": "enigma2", "title": "Enigma2 (Dreambox, VU+, Gigablue …)",
   "identify": "Linux-Receiver mit Enigma2-Oberfläche.",
   "steps": [
     "Per FTP (z. B. mit FileZilla) auf den Receiver verbinden und aus <code>/etc/enigma2/</code> die Dateien <code>lamedb</code>, <code>bouquets.*</code> und <code>userbouquet.*</code> auf den PC kopieren.",
     "Im Editor den Ordner mit diesen Dateien wählen.",
     "Nach dem Speichern die Dateien zurückkopieren und den Receiver neu starten bzw. die Senderlisten neu laden."],
   "file": "<code>lamedb</code>, <code>bouquets.tv</code>, <code>userbouquet.*.tv</code> …",
   "notes": []},
  {"id": "weitere", "title": "Weitere Receiver und Programme",
   "identify": "",
   "steps": [
     "<b>VDR</b> (Linux Video Disk Recorder): <code>channels.conf</code>",
     "<b>SAT>IP</b>: <code>.m3u</code>-Listen mit Sendernamen und Programmnummern",
     "<b>Xoro, Strong, TechniSat</b> und baugleiche Receiver: <code>.dbm</code>-Dateien",
     "<b>VISION EDGE 4K</b>: <code>database.db</code>",
     "<b>DVBViewer</b>: Senderliste als <code>.ini</code>"],
   "file": "",
   "notes": []},
 ],
 "stick_files": [],
 "import": ["Die gespeicherte Datei an denselben Ort zurückkopieren, von dem du sie geholt hast."],
 "faq": [],
},
]
