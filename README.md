# Plex Zufalls-Playlist Generator

Dieses Python-Skript wurde entwickelt, um eine wiederkehrende Herausforderung bei der Nutzung von Plex-Playlists über Amazon Alexa zu lösen, insbesondere bei älteren Echo-Geräten. Es generiert dynamisch eine Plex-Playlist, deren Titel in einer zufälligen Reihenfolge angeordnet sind, um eine "Pseudo-Zufallswiedergabe" zu ermöglichen.

-----

## Inhaltsverzeichnis

1.  [Das Problem: Alexa und Plex Shuffle](#1-das-problem-alexa-und-plex-shuffle)
    * [Einschränkungen der Alexa 1. Generation](#einschraenkungen-der-alexa-1-generation)
    * [Plex Skill und Kontextverlust](#plex-skill-und-kontextverlust)
    * [Das "Client-Profil"-Problem](#das-client-profil-problem)
2.  [Die Lösung: "Pseudo-Zufalls-Playlist" per API](#2-die-loesung-pseudo-zufalls-playlist-per-api)
    * [Wie es funktioniert](#wie-es-funktioniert)
    * [Vorteile dieser Methode](#vorteile-dieser-methode)
    * [Einschränkungen dieser Methode](#einschraenkungen-dieser-methode)
3.  [Voraussetzungen](#3-voraussetzungen)
4.  [Installation](#4-installation)
5.  [Konfiguration des Skripts](#5-konfiguration-des-skripts)
6.  [Ausführung des Skripts](#6-ausfuehrung-des-skripts)
7.  [Nutzung mit Alexa](#7-nutzung-mit-alexa)
8.  [Automatisierung mit Cron (Linux) / Aufgabenplanung (Windows)](#8-automatisierung-mit-cron-linux--aufgabenplanung-windows)
    * [Wichtiger Hinweis zur laufenden Wiedergabe bei Automatisierung](#wichtiger-hinweis-zur-laufenden-wiedergabe-bei-automatisierung)
9.  [Fehlerbehebung](#9-fehlerbehebung)
10. [Beitrag](#10-beitrag)
11. [Lizenz](#11-lizenz)

-----

## 1\. Das Problem: Alexa und Plex Shuffle

Nutzer von Plex in Verbindung mit Amazon Alexa stehen oft vor der Herausforderung, Playlists im Zufallsmodus (Shuffle) wiederzugeben. Obwohl Plex eine native Shuffle-Funktion bietet und Alexa generische Befehle dafür kennt, scheitert die Kombination in bestimmten Szenarien.

### Einschränkungen der Alexa 1. Generation

Ein Hauptgrund für die Schwierigkeiten liegt in der Verwendung von **Amazon Echo Geräten der 1. Generation**. Diese Geräte erhalten keine neuen Funktions-Updates mehr und sind oft nicht vollständig kompatibel mit den neuesten APIs und Kommunikationsprotokollen moderner Dienste wie Plex. Dies führt zu einem grundlegenden Problem bei der Verständigung zwischen dem Echo und dem Plex Media Server.

### Plex Skill und Kontextverlust

Beim Versuch, den Zufallsmodus über Sprachbefehle wie `"Alexa, sage Plex, spiele die Playlist [Name] im Zufallsmodus"` oder "`Alexa, sage Plex, aktiviere den Zufallsmodus"` zu aktivieren, antwortet Alexa oft mit Fehlermeldungen wie "Ich habe nicht verstanden, was du abspielen möchtest" oder ignoriert den Befehl schlichtweg und spielt die Playlist linear ab. Dies deutet darauf hin, dass der Plex Skill den Kontext der laufenden Wiedergabe verliert oder den Shuffle-Befehl nicht korrekt interpretieren und an den Server weiterleiten kann.

### Das "Client-Profil"-Problem

Im Debug-Log des Plex Media Servers findet sich häufig die Meldung:
`[Now] Unable to find client profile for device platform=Alexa, platformVersion=, device=Alexa, model=`

Diese Meldung ist ein starkes Indiz für das Kernproblem:

  * **Fehlende Geräte-Informationen:** Das Echo-Gerät der 1. Generation übermittelt dem Plex Media Server keine vollständigen Identifikationsinformationen (wie `platformVersion` und `model`).
  * **Gestörte Kommunikation:** Ohne ein korrektes "Client-Profil" weiß der Plex Server nicht, wie er optimal mit dem Echo kommunizieren oder erweiterte Wiedergabefunktionen wie den Zufallsmodus bereitstellen soll. Der Server fällt auf eine generische Wiedergabemethode zurück, die den Shuffle-Modus nicht berücksichtigt.
  * **Dauerhaftes Problem:** Da diese Meldung oft permanent im Log auftaucht, selbst während der Wiedergabe ohne aktive Sprachbefehle, ist es ein tief sitzendes Kompatibilitätsproblem auf Protokollebene, das mit einfachen Skill-Reinstallationen oder Sprachbefehlen nicht zu lösen ist.

-----

## 2\. Die Lösung: "Pseudo-Zufalls-Playlist" per API

Da Alexa Schwierigkeiten hat, die Shuffle-Funktion von Plex dynamisch zu steuern, umgehen wir das Problem, indem wir die Playlist bereits **vorab in einer zufälligen Reihenfolge** auf dem Plex Media Server erstellen.

### Wie es funktioniert

1.  **API-Zugriff:** Das Python-Skript nutzt die `plexapi`-Bibliothek, um sich direkt mit deinem Plex Media Server zu verbinden.
2.  **Künstler-Auswahl:** Du gibst eine Liste deiner gewünschten Künstler im Skript an.
3.  **Titel sammeln und mischen:** Das Skript durchsucht deine Musikbibliothek nach Titeln dieser Künstler, sammelt sie und **mischt** sie dann in einer zufälligen Reihenfolge.
4.  **Playlist-Erstellung:** Eine neue Plex-Playlist wird mit dem von dir angegebenen Namen erstellt. Die Besonderheit ist, dass die Titel in dieser Playlist bereits in der zufälligen Reihenfolge hinzugefügt werden.
5.  **Alexa-Abruf:** Wenn du Alexa dann anweist, diese Playlist abzuspielen, muss sie keinen "Shuffle"-Modus aktivieren. Sie spielt die Playlist einfach in der Reihenfolge ab, in der die Titel bereits enthalten sind – also in der festen, zufälligen Reihenfolge.

### Vorteile dieser Methode

  * **Umgeht Alexa-Kompatibilitätsprobleme:** Alexa muss keinen komplexen "Shuffle"-Befehl interpretieren oder mit einem unvollständigen Client-Profil umgehen. Sie spielt lediglich eine vorgefertigte Liste ab.
  * **Zuverlässige "Zufallswiedergabe":** Die Reihenfolge der Titel ist garantiert zufällig, da sie vom Skript auf Server-Ebene festgelegt wird.
  * **Dauerhaft:** Die erstellte Playlist existiert dauerhaft auf deinem Plex Media Server, bis sie gelöscht oder vom Skript überschrieben wird.

### Einschränkungen dieser Methode

  * **"Pseudo-Shuffle":** Die Reihenfolge ist nur zum Zeitpunkt der Playlist-Erstellung zufällig. Wenn du die Playlist erneut abspielst, wird sie immer in **derselben festen, zufälligen Reihenfolge** abgespielt, nicht in einer *neuen* zufälligen Reihenfolge.
  * **Manuelle Aktualisierung für neue Zufallsreihenfolge:** Um eine neue, frische Zufallsreihenfolge zu erhalten, musst du das Skript erneut ausführen. Dies löscht die alte Playlist und erstellt eine neue mit denselben Titeln in einer neu gemischten Reihenfolge.
  * **Wiedergabeunterbrechung bei Automatisierung:** Wenn das Skript während einer laufenden Wiedergabe über Alexa ausgeführt wird, wird die alte Playlist gelöscht und eine neue erstellt. Alexa wird das aktuell spielende Lied beenden, aber beim Versuch, zum nächsten Lied zu wechseln, die Wiedergabe einstellen (da ihre interne Warteschlange auf die alte, gelöschte Playlist verweist). Um die neu generierte Playlist zu nutzen, muss die Wiedergabe anschließend manuell neu gestartet werden.

-----

## 3\. Voraussetzungen

  * **Plex Media Server:** Muss installiert und ausgeführt werden.
  * **Python:** Version 3.x sollte auf dem System installiert sein, auf dem du das Skript ausführst.
  * **`plexapi` Bibliothek:** Eine Python-Bibliothek zur Interaktion mit der Plex API.

-----

## 4\. Installation

1.  **Python installieren:** Falls noch nicht geschehen, lade Python 3.x von [python.org](https://www.python.org/downloads/) herunter und installiere es. Stelle sicher, dass du die Option "Add Python to PATH" während der Installation auswählst.
2.  **`plexapi` installieren:** Öffne ein Terminal oder eine Eingabeaufforderung und führe den folgenden Befehl aus:
    ```bash
    pip install plexapi
    ```

-----

## 5\. Konfiguration des Skripts

Öffne die Skriptdatei (`playlist.py`) mit einem Texteditor und passe die folgenden Variablen im Bereich `--- KONFIGURATION ---` an:

  * **`PLEX_URL`**:

      * Dies ist die vollständige Adresse deines Plex Media Servers, einschließlich des Ports (standardmäßig `32400`).
      * Beispiel: `'http://192.168.1.100:32400'` (für lokale Netzwerke) oder `'https://deinserver.dyndns.net:32400'` (wenn du eine Dyndns-Adresse verwendest).
      * **Wichtig:** Verwende `http://` oder `https://` je nachdem, wie dein Server konfiguriert ist.

  * **`PLEX_TOKEN`**:

      * Dein persönlicher Plex X-Plex-Token. Dieser authentifiziert dich gegenüber deinem Server.
      * **Anleitung zum Finden deines Tokens:** [How to get your X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

  * **`MUSIC_LIBRARY_NAME`**:

      * Der **EXAKTE Name** deiner Musikbibliothek in Plex. Achte auf Groß-/Kleinschreibung und Leerzeichen.
      * Beispiel: `'Musik'`, `'Meine Songs'`, `'Audio'`.

  * **`NEW_PLAYLIST_NAME`**:

      * Der Name, den die neu erstellte Playlist in Plex erhalten soll.
      * Beispiel: `'Meine Zufalls-Playlist'`, `'Rock Hits Gemischt'`.

  * **`ARTISTS_TO_INCLUDE`**:

      * Eine Liste von Künstlern (Strings), deren Titel in die Playlist aufgenommen werden sollen.
      * Die Namen müssen **EXAKT** so sein, wie sie in deiner Plex-Bibliothek angezeigt werden (Groß-/Kleinschreibung beachten\!).
      * Beispiel: `['Artist A', 'Artist B', 'Artist C']`

  * **`MAX_SONGS_PER_ARTIST`**:

      * (Optional) Eine maximale Anzahl von Titeln, die pro Künstler in die Playlist aufgenommen werden. Dies verhindert, dass ein einzelner Künstler die Playlist dominiert.
      * Setze diesen Wert auf `None`, wenn du **alle** Titel jedes angegebenen Künstlers einbeziehen möchtest.

-----

## 6\. Ausführung des Skripts

1.  Speichere das Skript als `.py`-Datei (z.B. `playlist_generator.py`).
2.  Öffne ein Terminal oder eine Eingabeaufforderung.
3.  Navigiere zu dem Verzeichnis, in dem du die Skriptdatei gespeichert hast.
4.  Führe das Skript mit folgendem Befehl aus:
    ```bash
    python playlist_generator.py
    ```
5.  Das Skript gibt Informationen über den Fortschritt aus und zeigt am Ende den Befehl an, den du Alexa geben musst.

-----

## 7\. Nutzung mit Alexa

Nachdem das Skript erfolgreich ausgeführt wurde und die Playlist in Plex erstellt ist, kannst du sie über Alexa abspielen.

  * **Gib den Befehl an dein Echo-Gerät:**
    ```
    "Alexa, sage Plex, spiele die Playlist [NEW_PLAYLIST_NAME]"
    ```
    (Ersetze `[NEW_PLAYLIST_NAME]` durch den Namen, den du in der Skriptkonfiguration festgelegt hast, z.B. `"Alexa, sage Plex, spiele die Playlist Meine Zufalls-Playlist"`)

Die Playlist wird nun in der vom Skript einmalig gemischten Reihenfolge abgespielt.

-----

## 8\. Automatisierung mit Cron (Linux) / Aufgabenplanung (Windows)

Du kannst das Skript automatisieren, um die Playlist regelmäßig zu aktualisieren und so eine "frische" Zufallsreihenfolge zu gewährleisten.

### Wichtiger Hinweis zur laufenden Wiedergabe bei Automatisierung

**Das Skript löscht und erstellt die Playlist neu.** Wenn das Skript läuft, während Alexa diese Playlist abspielt, wird die Wiedergabe **unterbrochen**, sobald der aktuell spielende Titel endet. Alexa wird die Wiedergabe einstellen, da ihre interne Wiedergabewarteschlange auf die alte, nicht mehr existierende Playlist verweist.

**Das bedeutet:** Um die neu gemischte Reihenfolge zu hören, musst du die Wiedergabe **manuell stoppen und dann erneut starten** (mit dem oben genannten Befehl), nachdem das Skript im Hintergrund gelaufen ist.

**Beispiel für Cron (Linux):**

1.  Speichere das Skript an einem festen Ort, z.B. `/home/user/plex_scripts/playlist_generator.py`.
2.  Öffne den Cron-Editor: `crontab -e`
3.  Füge eine Zeile hinzu, um das Skript z.B. alle 2 Stunden auszuführen:
    ```cron
    0 */2 * * * /usr/bin/python3 /home/user/plex_scripts/playlist_generator.py >> /home/user/plex_scripts/playlist_log.log 2>&1
    ```
    (Passe den Pfad zu Python und dem Skript an dein System an.)

**Beispiel für Aufgabenplanung (Windows):**

1.  Speichere das Skript an einem festen Ort, z.B. `C:\PlexScripts\playlist_generator.py`.
2.  Öffne die "Aufgabenplanung" (Task Scheduler).
3.  Erstelle eine neue Aufgabe (Basisaufgabe oder Aufgabe erstellen...).
4.  **Trigger:** Wähle "Täglich" und stelle die Uhrzeit ein, oder wähle "Bei bestimmten Ereignissen", "Beim Start" usw., um eine regelmäßige Ausführung zu definieren.
5.  **Aktion:** Wähle "Programm starten".
      * **Programm/Skript:** `C:\Users\DeinBenutzername\AppData\Local\Programs\Python\Python3X\python.exe` (Passe den Pfad zu deiner Python-Installation an)
      * **Argumente hinzufügen (optional):** `C:\PlexScripts\playlist_generator.py` (Pfad zu deinem Skript)
      * **Starten in:** `C:\PlexScripts\` (Das Verzeichnis, in dem dein Skript liegt)

-----

## 9\. Fehlerbehebung

  * **"Fehler: Musikbibliothek mit dem Namen '[Name]' nicht gefunden."**: Überprüfe den Wert von `MUSIC_LIBRARY_NAME` im Skript. Er muss exakt mit dem Namen deiner Musikbibliothek in Plex übereinstimmen (Groß-/Kleinschreibung, Leerzeichen beachten\!).
  * **"Warnung: Künstler '[Name]' nicht in der Bibliothek gefunden."**: Überprüfe die Schreibweise des Künstlernamens in `ARTISTS_TO_INCLUDE`. Er muss exakt mit dem Künstlernamen in deiner Plex-Bibliothek übereinstimmen.
  * **"Ein unerwarteter Fehler ist aufgetreten:..."**: Überprüfe `PLEX_URL` und `PLEX_TOKEN`. Stelle sicher, dass dein Plex Media Server läuft und vom Skript-Rechner aus erreichbar ist (z.B. indem du die `PLEX_URL` in einem Browser öffnest). Dein Token sollte korrekt sein.
  * **Playlist wird erstellt, aber Alexa spielt nicht im Zufallsmodus:** Dies ist das Kernproblem, das dieses Skript löst. Stelle sicher, dass du die Playlist mit dem in Schritt 7 angegebenen Befehl neu startest, nachdem das Skript gelaufen ist.

-----

## 10\. Beitrag

Vorschläge zur Verbesserung oder Fehlerberichte sind willkommen\!

-----

## 11\. Lizenz

Dieses Skript wird unter der MIT-Lizenz bereitgestellt.

-----
