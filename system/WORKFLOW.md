# FAKTENFABRIK – Arbeitsanleitung für die automatischen Aufträge

Diese Anleitung liest jeder geplante Auftrag zuerst. Sie beschreibt, wie ein Video von der Idee bis zum Upload entsteht.
Kanal: TikTok @faktenfabrik.tv und YouTube Shorts „Faktenfabrik“ (@faktenfabrik-tv). Inhaber: Lukas.

## Feste Regeln (immer)

- **Niemals ohne „Ok“ veröffentlichen.** Entwurf erstellen, Lukas zeigen, erst nach seinem „Ok“ (oder gleichwertiger Freigabe) `vidiq_social_post_publish` aufrufen. Keine Antwort = nichts veröffentlichen.
- **Niemals echtes Geld ausgeben** (kein Upgrade, kein Kauf, keine kostenpflichtige Überschreitung). Alles mit Geld läuft über Lukas.
- **TikTok nur auf dieses Konto:** platformAccountId `_000fXCTAmZfvnx5IfFKzfqR0UplcHlEJ1A7` (Anzeigename „faktenfabrik“ = @faktenfabrik.tv).
  NIE auf `_000u7UaNig2p0Vzqokzsj-C822e_VswHob1` („user2843462255635“) oder `_0008e8irFRHGHPPAYuDRs_sgPUytvZPDtYX` („faktenfabrik68“) – das sind falsche Konten. Vor jedem Entwurf `vidiq_social_account_list` prüfen; wenn das richtige Konto fehlt oder canPublish false ist: abbrechen und Lukas benachrichtigen.
- **YouTube:** platformAccountId `UC0w4J7V94dAqJTjgt1PvBoQ`.
- **Master-Prompt** (`Master-Prompt_faktenfabrik.tv.txt` in diesem Ordner) gilt für Inhalt, Stil, Fakten, Engagement (Abschnitt 13a) und Qualität.
- **Länge:** Sprechtext höchstens **1.250 Zeichen inklusive Regieanweisungen**, Ziel 65–72 s Video. Pro Video genau **eine** Sprachversion (`generations_count: 1`).
- **Fakten:** nur belegte Fakten, mind. eine seriöse Quelle pro zentralem Fakt (Universität, Fachjournal, Behörde, seriöses Wissenschaftsmagazin). Unsichere Behauptungen weglassen oder vorsichtig formulieren.
- **Keine Bettel-Aufrufe** („Like für Like“ usw.). Natürliche Kommentarfrage und ehrlicher Teil-Moment sind erwünscht.
- **Musik/Sound:** nur selbst erzeugte Musik aus `pipeline.py audio` (lizenzfrei).

## Pfade (kein Mac nötig)

- GitHub-Repository (öffentlich): `lukashaerle/faktenfabrik-uploads`
  - Branch `main`, Ordner `system/`: Videosystem (lib/, Beispiel-Episoden), `WORKFLOW.md`, `themen.json`, `themen_log.json`.
  - Branch `upload`: nur kurzzeitig für die Video-Übergabe an vidIQ, wird danach gelöscht.
- Zugriff: `add_repo` (owner lukashaerle, repo faktenfabrik-uploads, access push), dann
  `git clone --depth 1 https://github.com/lukashaerle/faktenfabrik-uploads /home/claude/ff-repo` (großzügiges Timeout).
  Commits mit `git -c user.name="FAKTENFABRIK Bot" -c user.email="lukashaerle@users.noreply.github.com" commit ...`, Push mit `git -c push.negotiate=true push`.
- Master-Prompt: liegt privat in Google Drive, Datei-ID `1zDxF186R7zTmeHOyA9c_11fdqs0cyHn_` → mit Google Drive `read_file_content` (oder `download_file_content`) lesen.

## Ablauf pro Video

1. **System laden:** Repository wie unter „Pfade“ verbinden und klonen. Arbeitsordner `/home/claude/ff-repo/system/`, neue Episode in einem Unterordner davon (z. B. `system/ep_<datum>_<slot>/`, wird NICHT committet). Master-Prompt aus Drive lesen.
   `pip install --break-system-packages -q skia-python numpy` ; `ffmpeg` ist vorhanden.
2. **Kontingent prüfen:** `account_get_usage` (ElevenLabs). Weniger als 1.500 Zeichen übrig → abbrechen, Lukas benachrichtigen.
3. **Thema wählen:** Eintrag für heute und diesen Slot aus `themen.json`. Fehlt er, ein passendes neues Thema für den Slot wählen, das nicht in `themen_log.json` steht.
   Slots: 11:30 WISSEN (Körper, Wissenschaft, Alltag) · 17:30 STAUNEN (Tiere, Natur, Geschichte, Universum) · 20:00 UNTERHALTUNG (kurios, lustig, Quiz, Mythen).
4. **Recherche:** WebSearch/WebFetch, Quellen öffnen, Fakten prüfen. Quellen notieren (für die YouTube-Beschreibung).
5. **Skript:** Genau 10 Absätze (= 10 Szenen). **Neugier-Schleifen (Pflicht):** In Absatz 1 oder 2 ein Versprechen, das erst am Ende eingelöst wird (z. B. „Und der verrückteste Teil kommt ganz am Schluss.“) und in Absatz 5 oder 6 eine zweite Schleife (z. B. „Aber warte – es wird noch seltsamer.“). Das Versprechen muss wirklich eingelöst werden, keine leeren Ankündigungen. Hook mit offener Frage in Absatz 1, Wendung, Teil-Moment, Kommentarfrage am Ende (Absatz 10). Regieanweisungen für ElevenLabs v4 auf Englisch in eckigen Klammern: [dramatically], [excited], [curious], [surprised], [pause], [seriously], [warmly], [tense], [urgent]. Großbuchstaben für Betonung sparsam. Zahlen ausschreiben, wenn die Aussprache sonst unsicher ist.
   **Wunsch von Lukas (16.11.2026): mehr Spannung, weniger Flüstern.** [whispers] höchstens einmal pro Video, besser gar nicht. Spannung stattdessen über: kurze, harte Sätze; eine Schätz- oder offene Frage im Hook, die erst spät aufgelöst wird; Mini-Cliffhanger am Ende einzelner Absätze („Doch dann …“, „Und genau hier wird es seltsam.“); [pause] direkt vor der Pointe; [tense]/[dramatically] beim Aufbau, [surprised]/[excited] bei der Auflösung; klare Steigerung bis zum Höhepunkt in Absatz 7–9.
   Zeichen zählen (inkl. Tags): höchstens 1.250. `paras.json` = Liste der 10 Absätze **ohne** Tags (für das Untertitel-Timing).
6. **Stimme:** `creative_create_flow` (Name „FAKTENFABRIK <Datum> <Slot>“), dann `creative_generate_speech` mit
   `voice_id: PrIzXjAjNWO7Dj0sG14D` (Jesco – Epic Trailer), `model_id: eleven_v4`, `generations_count: 1`, `flow_id`.
   Nicht wiederholen (kostet erneut). Status mit `creative_get_flow_run_status` abfragen, `content_url` mit `curl -o voice.mp3` laden (Domain ist freigegeben).
7. **Wort-Zeitstempel:** `creative_add_flow_asset_node` (modality audio, generation_id der Aufnahme, gleicher flow) → `creative_transcribe_audio` (model eleven_scribe_v1, connect_from = Node) → Status abfragen → `words_download_url` mit curl als `words.json` laden. Kostet nichts.
8. **Szenen:** `episode.py` im Episodenordner schreiben, nach Vorlagen in `system/beispiele/` (episode_gaehnen.py ist die aktuellste):
   `from render import ...` (finn, draw_banner, draw_text_c, vgrad, bubbles, rays, rock, pop, ease, lerp, mixc, col, P, skia, W, H ...).
   10 Funktionen s1..s10(c, t, d), `SCENES`, `FADE_COL` (10 Farben), `HIGHLIGHT` (Schlüsselwörter, gelb).
   FINN immer mit `finn(...)` zeichnen (Aussehen nie ändern). Szene 10 = Logo-Karte: „FAKTENFABRIK“, darunter „@faktenfabrik.tv“ und „Wissen. Staunen. Verstehen.“ (wie in der Vorlage). Oben je Szene eine kurze Einblendung mit `draw_banner`.
   Poppins enthält keine Zeichen wie → ≠ ₂: umschreiben.
   **Text-Hook (Pflicht):** In episode.py `HOOK_TEXT = "ZEILE 1\nZEILE 2"` setzen – 2–5 Wörter, provokant, Großbuchstaben, passend zum gesprochenen Hook (z. B. "DU GÄHNST\nGLEICH!", "DIESER FAKT\nIST FALSCH"). pipeline.py zeigt ihn ab Bild 1 für 2,6 s groß in der Bildmitte oben (y≈380–700); diesen Bereich in Szene 1 in den ersten 2,6 s nicht mit wichtigem Inhalt belegen.
   **Tempo (Pflicht):** In jeder Szene alle 2–3 s eine sichtbare Änderung (neues Element taucht auf, Zahl zählt hoch, Objekt bewegt sich, Einblendung wechselt). pipeline.py setzt zusätzlich automatisch alle 2,2 s einen kleinen Kamera-Ruck. Keine Szene darf mehrere Sekunden statisch wirken.
   Folgen/Abo-Einblendungen kommen automatisch aus pipeline.py (nicht selbst zeichnen): kleiner Hinweis „Mehr Fakten? Folgen!“ bei ca. 45 % der Laufzeit (rechts, y≈1100–1200) und animierte Abo-Karte (Plus → Haken) in Szene 10 rechts (x≈620–1040, y≈760–1160). Diese Bereiche in den Szenen möglichst frei lassen. Keine zusätzlichen gesprochenen Folgen-Aufforderungen und keine Bettel-Aufrufe.
   Optional `pops.json`: Liste [szene, sekunde] für Pop-Sounds.
9. **Bauen:** im Episodenordner
   `python3 ../lib/pipeline.py timing` → `python3 ../lib/pipeline.py audio` →
   Standbilder prüfen: `python3 ../lib/pipeline.py still <szene> <sek>` für mind. 4 Momente, Bilder ansehen (Text lesbar, nichts verdeckt, FINN korrekt) und Fehler beheben →
   `python3 ../lib/pipeline.py render <Kurzname>` → `FAKTENFABRIK_<Kurzname>.mp4`. Länge prüfen (61–75 s).
9b. **Titelbild und Startbild (Pflicht, jedes Video):** Lukas will KEIN eingeschobenes Standbild am Anfang (beim Scrollen soll man direkt das Video sehen). Daher zwei Teile:
    **a) Startbild im Video (Cover für TikTok und Instagram):** TikTok und Instagram nehmen über vidIQ das erste Bild als Cover. Szene 1 so bauen, dass schon Bild 0 (t = 0) wie ein gutes Titelbild aussieht: Hauptfigur/Hauptobjekt groß und voll sichtbar, FINN sichtbar, HOOK_TEXT steht (kommt aus pipeline.py), heller, themenpassender Hintergrund. Bei t = 0 nichts ausblenden, nichts mit Deckkraft 0 starten, kein Schwarz. Prüfen mit `python3 ../lib/pipeline.py still 0 0` und Bild ansehen. Dann läuft die Szene ganz normal animiert weiter.
    **b) Titelbild-Datei `thumb.png` (YouTube und Freigabe):** Stil von Lukas freigegeben, Vorlage `system/beispiele/thumb_baertierchen.py`, Baukasten `system/lib/thumbnail.py`. **Videobezug (Pflicht):** Hauptobjekt und FINN aus Standbildern DIESES Videos ausschneiden (`cutout(still, box)`), Hintergrund passend zum Thema, Headline greift den Hook auf (2 Zeilen, Zeile 1 weiß / Zeile 2 gelb, Navy-Kontur, + Nachsatz-Pill), FINN unten links mit Sprechblase. `thumb.py` im Episodenordner schreiben und ausführen → `thumb.png` + `thumb_vorschau.png`, Vorschau ansehen und nachbessern.
    `thumbnail.py prepend` NICHT verwenden (Lukas will das nicht).
10. **Übergabe an vidIQ (über GitHub):** Video und `thumb.png` nach `/mnt/user-data/outputs/` kopieren und beide mit `SendUserFile` an Lukas senden. Dann in einem frischen Ordner:
    `git init -q up && cd up && git checkout -q --orphan upload && cp <video> . && git add . && git commit -qm upload && git remote add origin https://github.com/lukashaerle/faktenfabrik-uploads && git push -q -f origin upload`
    → `vidiq_video_upload` mit `https://raw.githubusercontent.com/lukashaerle/faktenfabrik-uploads/upload/<dateiname>.mp4`. Mit curl die vidIQ-`videoUrl` laden und per `cmp` mit dem Original vergleichen. Danach Branch löschen: `git push -q origin --delete upload`.
11. **Entwurf:** `vidiq_social_post_draft_create`, media = uploadId,
    TikTok: privacyLevel PUBLIC_TO_EVERYONE, allowComment true, isAiGenerated true, musicUsageConfirmed true.
    YouTube: thumbnailImageId = `thumb.png` (vorher mit `vidiq_upload_image` hochladen; wird abgelehnt, solange der Kanal nicht verifiziert ist – das bricht den Upload nicht ab), title (≤100 Zeichen, endet mit „#shorts“), privacyStatus public, categoryId 27, tags (6–10), text = Beschreibung mit Quellenlinks, „Dieses Video wurde mit KI-Unterstützung erstellt.“ und Hashtags.
    Gemeinsamer Text (TikTok-Caption): 1–2 Sätze Hook + „Quellen: …“ + genau 5 Hashtags inkl. #faktenfabrik.
    publishAt = Slot-Zeit heute (Europe/Berlin, mit Zeitzone), nur wenn sie mehr als 5 Minuten in der Zukunft liegt; sonst ohne publishAt (sofort nach Ok).
12. **Benachrichtigen:** Mit `SendUserMessage` (und PushNotification, falls vorhanden) Lukas schreiben: Thema, Titel, Caption, Zeitpunkt, alle drei Konten (TikTok, YouTube, Instagram), Titelbild, Link/Datei zum Ansehen, „Antworte mit Ok, dann plane ich es ein.“
13. **Nach „Ok“:** `vidiq_social_post_publish` (postId + revision). Status prüfen, Links melden. Instagram-Reel mit demselben Video (enthält das Titelbild) wie in der Aufgabe beschrieben veröffentlichen. Instagram-Cover ist das erste Bild des Videos (siehe 9b a). Kommt das Ok nach der Slot-Zeit: Entwurf ohne publishAt aktualisieren (`vidiq_social_post_draft_update`), Lukas den neuen Stand zeigen, nach Ok sofort veröffentlichen.
14. **Protokoll:** `system/themen_log.json` ergänzen ({datum, slot, thema, titel, tiktok_url, youtube_url}), committen und auf `main` pushen (vorher `git pull --rebase --depth=1` falls nötig).

## Wochenauftrag (Themenliste)

Jeden Sonntag: 21 Themen für Montag–Sonntag der Folgewoche (3 pro Tag, passend zu den Slots), abwechslungsreich, gut belegbar, nicht in `themen_log.json`. Für jedes Thema: Titelidee, Kernfakt, geplante Quelle(n), Hook-Idee, Teil-Moment. Als `system/themen.json` ins Repository (Branch main) committen und pushen (alte Datei vorher als `system/themen_<alte woche>.json` sichern) und Lukas die Liste als Dokument schicken.
`themen.json`-Format: {"woche": "JJJJ-MM-TT bis JJJJ-MM-TT", "tage": [{"datum": "JJJJ-MM-TT", "11:30": {...}, "17:30": {...}, "20:00": {...}}]}
