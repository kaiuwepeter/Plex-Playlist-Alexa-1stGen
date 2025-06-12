from plexapi.server import PlexServer
import random
import sys

# --- KONFIGURATION ---
# Die vollständige URL zu deinem Plex Media Server (inkl. Port)
# Beispiel: 'http://192.168.1.100:32400' oder 'https://meinserver.dyndns.org:32400'
PLEX_URL = '' 

# Dein Plex X-Plex-Token zur Authentifizierung
# Anleitung zum Finden deines Tokens: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
PLEX_TOKEN = ''  # Ersetze dies durch deinen Plex API Token

# Der EXAKTE Name deiner Musikbibliothek in Plex (Groß-/Kleinschreibung beachten!)
# Beispiel: 'Musik', 'Meine Musik', 'Songs', etc.
MUSIC_LIBRARY_NAME = ''

# Der Name der neuen Playlist, die im "Pseudo-Zufallsmodus" erstellt werden soll
# Wenn eine Playlist mit diesem Namen bereits existiert, wird sie gelöscht und neu erstellt.
NEW_PLAYLIST_NAME = ''

# Liste der Künstler, von denen du Titel in der Playlist haben möchtest
# Die Namen müssen EXAKT so sein, wie sie in deiner Plex-Bibliothek angezeigt werden (Groß-/Kleinschreibung beachten!)
ARTISTS_TO_INCLUDE = ['Electric Callboy', 'Volbeat'] # <--- KÜNSTLER ANPASSEN!

# Maximale Anzahl an Titeln pro Künstler (optional)
# Setze auf None, um alle Titel jedes Künstlers aufzunehmen.
MAX_SONGS_PER_ARTIST = 100 # Setze auf None, um diese Begrenzung zu ignorieren

# --- SKRIPT-LOGIK ---
def create_shuffled_static_playlist(playlist_name, music_lib_name, artists, max_songs_per_artist=None):
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        print(f"Verbindung zu Plex Server {PLEX_URL} hergestellt.")

        # Stelle sicher, dass die spezifische Musikbibliothek verfügbar ist
        music_library = plex.library.section(music_lib_name)
        if not music_library:
            print(f"Fehler: Musikbibliothek mit dem Namen '{music_lib_name}' nicht gefunden.")
            print("Bitte überprüfe 'MUSIC_LIBRARY_NAME' in der Konfiguration.")
            sys.exit(1)
        print(f"Musikbibliothek '{music_library.title}' gefunden.")

        # Sammle alle Titel der gewünschten Künstler
        all_songs_for_playlist = []
        for artist_name in artists:
            # Suche nach dem Künstler in der spezifizierten Musikbibliothek
            artist_results = music_library.search(artist_name, libtype='artist')
            
            if artist_results:
                artist = artist_results[0] # Nehme den ersten Treffer, falls es mehrere gibt
                print(f"Sammle Titel von Künstler: {artist.title}")
                songs_from_artist = artist.tracks()
                
                # Mische die Songs dieses spezifischen Künstlers, um eine zufällige Auswahl zu treffen
                random.shuffle(songs_from_artist) 

                if max_songs_per_artist is not None and len(songs_from_artist) > max_songs_per_artist:
                    all_songs_for_playlist.extend(songs_from_artist[:max_songs_per_artist])
                else:
                    all_songs_for_playlist.extend(songs_from_artist)
            else:
                print(f"Warnung: Künstler '{artist_name}' nicht in der Bibliothek '{music_lib_name}' gefunden.")

        if not all_songs_for_playlist:
            print("Fehler: Keine Titel von den angegebenen Künstlern gefunden. Playlist kann nicht erstellt werden.")
            sys.exit(1)

        # Mische die gesammelten Titel endgültig, um die Reihenfolge der gesamten Playlist zu randomisieren
        random.shuffle(all_songs_for_playlist)
        print(f"Insgesamt {len(all_songs_for_playlist)} Titel für die Playlist gesammelt und gemischt.")

        # Versuche, eine bestehende Playlist mit dem gleichen Namen zu löschen
        try:
            existing_playlist = plex.playlist(playlist_name)
            if existing_playlist:
                print(f"Bestehende Playlist '{playlist_name}' wird gelöscht.")
                existing_playlist.delete()
        except Exception as e:
            # plexapi.exceptions.NotFound ist der typische Fehler, wenn die Playlist nicht existiert
            # Wir fangen aber allgemein ab, um robust zu sein
            # print(f"Hinweis: Playlist '{playlist_name}' existiert nicht oder konnte nicht gelöscht werden: {e}")
            pass # Ignoriere Fehler beim Löschen, wenn die Playlist nicht existiert

        # Erstelle die neue Playlist mit den gemischten Titeln
        # Die Methode createPlaylist benötigt eine Liste von Medienobjekten
        new_playlist = plex.createPlaylist(playlist_name, items=all_songs_for_playlist)
        print(f"Playlist '{new_playlist.title}' mit {new_playlist.leafCount} Titeln erfolgreich erstellt.")
        
        print(f"\n--- NÄCHSTER SCHRITT FÜR ALEXA ---")
        print(f"Sage zu Alexa auf dem entsprechenden Echo-Gerät:")
        print(f"\"Alexa, sage Plex, spiele die Playlist {new_playlist.title}\"")
        print(f"\nDiese Playlist wird jetzt in der (einmalig beim Erstellen) zufälligen Reihenfolge abgespielt.")
        print("Um eine NEUE zufällige Reihenfolge zu erhalten, müssen Sie dieses Skript erneut ausführen.")

    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        print("Bitte überprüfe deine PLEX_URL, PLEX_TOKEN und MUSIC_LIBRARY_NAME in der Konfiguration.")
        sys.exit(1)

if __name__ == "__main__":
    create_shuffled_static_playlist(NEW_PLAYLIST_NAME, MUSIC_LIBRARY_NAME, ARTISTS_TO_INCLUDE, MAX_SONGS_PER_ARTIST)

# --- ENDE DES SKRIPTS ---

# Dieses Skript ist für den einmaligen Gebrauch gedacht, um eine zufällige Playlist zu erstellen.
# Die Playlist wird nicht automatisch aktualisiert.
# Um eine NEUE zufällige Reihenfolge zu erhalten, müssen Sie dieses Skript erneut ausführen.
