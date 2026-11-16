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
- **Länge:** Sprechtext **Ziel 1.100–1.150 Zeichen**, höchstens 1.250 inklusive Regieanweisungen (ElevenLabs-Kontingent schonen: rund 128.000 Zeichen/Monat für ~90 Videos). Video 61–72 s; ist die Stimme kürzer als 59 s, verlängert `pipeline.py timing` die Logo-Karte automatisch (max. 6 s), sodass das Video über 61 s bleibt. Pro Video genau **eine** Sprachversion (`generations_count: 1`) – keine zweite Aufnahme bei kleinen Fehlern, stattdessen Szenen/Untertitel an die Aufnahme anpassen. Eine Neuaufnahme nur bei echtem Fehler (falsches Wort, falscher Fakt), und dann nur den betroffenen Text kürzen.
- **Fakten:** nur belegte Fakten, mind. eine seriöse Quelle pro zentralem Fakt (Universität, Fachjournal, Behörde, seriöses Wissenschaftsmagazin). Unsichere Behauptungen weglassen oder vorsichtig formulieren.
- **Keine Bettel-Aufrufe** („Like für Like“ usw.). Natürliche Kommentarfrage und ehrlicher Teil-Moment sind erwünscht.
- **Rechte- und Regel-Check vor JEDEM Upload (Pflicht, Schritt 9c):** Nichts hochladen, was Urheberrecht, Markenrecht, Persönlichkeitsrechte oder Plattformregeln verletzen könnte. Im Zweifel weglassen oder Lukas fragen. Ziel: keine Kosten, keine Abmahnung, keine Sperre, kein Strike.
- **Musik/Sound:** nur selbst erzeugte Musik aus `pipeline.py audio` (lizenzfrei).

## Pfade (kein Mac nötig)

- GitHub-Repository (öffentlich): `lukashaerle/faktenfabrik-uploads`
  - Branch `main`, Ordner `system/`: Videosystem (lib/, Beispiel-Episoden), `WORKFLOW.md`, `themen.json`, `themen_log.json`.
  - Branch `upload`: nur kurzzeitig für die Video-Übergabe an vidIQ, wird danach gelöscht.
- Zugriff: `add_repo` (owner lukashaerle, repo faktenfabrik-uploads, access push), dann
  `git clone --depth 1 https://github.com/lukashaerle/faktenfabrik-uploads /home/claude/ff-repo` (großzügiges Timeout).
  Commits mit `git -c user.name="FAKTENFABRIK Bot" -c user.email="lukashaerle@users.noreply.github.com" commit ...`, Push mit `git -c push.negotiate=true push`.
- Master-Prompt: liegt privat in Google Drive, Datei-ID `1yHHlbAhqDGzdDpzfaYB6z9aPvyamEtPs` → mit Google Drive `read_file_content` (oder `download_file_content`) lesen.

## Ablauf pro Video

1. **System laden:** Repository wie unter „Pfade“ verbinden und klonen. Arbeitsordner `/home/claude/ff-repo/system/`, neue Episode in einem Unterordner davon (z. B. `system/ep_<datum>_<slot>/`, wird NICHT committet). Master-Prompt aus Drive lesen.
   `pip install --break-system-packages -q skia-python numpy` ; `ffmpeg` ist vorhanden.
2. **Kontingent prüfen:** `account_get_usage` (ElevenLabs). Weniger als 1.500 Zeichen übrig → abbrechen, Lukas benachrichtigen.
3. **Thema wählen:** Eintrag für heute und diesen Slot aus `themen.json`. Fehlt er, ein passendes neues Thema für den Slot wählen.
   **Originalitäts-Check (Pflicht, Master-Prompt Abschnitt 5a), auch für Themen aus `themen.json`:** (a) `themen_log.json` komplett lesen – gleicher Kernfakt, gleiches Tier/Phänomen/Mythos unter anderem Titel zählt als Wiederholung → anderes Thema. (b) Per WebSearch prüfen, ob es ein bekanntes Video anderer Creator zu genau diesem Thema/Hook gibt („<Thema> TikTok“, „<Thema> Shorts“, Hook-Satz). Dann eigenen Blickwinkel, eigenen Hook und eigenen Aufbau wählen oder Thema verwerfen. Nie Skript, Hook, Titel, Bildideen oder Formulierungen anderer übernehmen; Recherche nur aus Primärquellen. Ergebnis in der Freigabe-Nachricht an Lukas in einer Zeile nennen („Originalität: geprüft, …“).
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
9c. **Rechte- und Regel-Check (Pflicht, vor der Übergabe an vidIQ):** Jeden Punkt prüfen. Fällt einer durch: beheben und neu rendern; geht das nicht, NICHT hochladen, Lukas informieren und über den Bot in #fehler melden.
    - **Musik/Ton:** nur die selbst erzeugte Musik und Effekte aus `pipeline.py audio`. Keine Songs, keine TikTok-/Instagram-Sounds, keine fremden Samples.
    - **Stimme:** nur ElevenLabs-Stimme aus Lukas' Konto. Beim Kontingent-Check (Schritt 2) prüfen, dass ein bezahlter Plan aktiv ist (Creator oder höher, kommerzielle Nutzung erlaubt). Ist es der Gratis-Plan: abbrechen und Lukas melden (Gratis-Plan erlaubt keine kommerzielle Nutzung). Keine Stimmen, die echte Personen nachahmen.
    - **Bilder/Video:** alles selbst gezeichnet (render.py/episode.py, thumbnail.py aus eigenen Standbildern). Keine Fotos, Clips, Screenshots, Grafiken oder Logos aus dem Internet, keine Stock-Bilder.
    - **Figuren und Marken:** keine bekannten Figuren (Disney, Pokémon, Comics, Serien, Spiele), keine Markenlogos oder Produktverpackungen, keine Nachbildungen. Markennamen nur, wenn für den Fakt nötig, sachlich und ohne Logo.
    - **Personen:** keine echten Personen abbilden oder nachahmen. Forscher nur namentlich und sachlich nennen. Keine erfundenen Zitate. Zitate nur kurz, wörtlich und mit Quelle.
    - **Texte:** Skript, Titel, Caption und Einblendungen komplett selbst formuliert (siehe Originalitäts-Check Schritt 3). Keine übernommenen Sätze aus Artikeln oder anderen Videos, auch nicht übersetzt.
    - **Schrift:** nur Poppins (Open Font License, kommerziell frei).
    - **Fakten und Inhalt:** belegte Fakten mit Quellen in der Beschreibung. Keine Gesundheits-, Heil- oder Finanzversprechen, keine gefährlichen Nachmach-Anleitungen, nichts Verletzendes oder Diskriminierendes, keine Werbung oder Affiliate-Links ohne Kennzeichnung (aktuell keine Werbung).
    - **KI-Kennzeichnung:** TikTok `isAiGenerated: true`, Instagram `isAiGenerated: true`, YouTube-Beschreibung mit „Dieses Video wurde mit KI-Unterstützung erstellt.“
    - **Plattformregeln:** keine Bettel-Aufrufe, kein irreführender Hook oder Titel, kein Doppel-Upload eines schon veröffentlichten Videos auf demselben Konto.
    - **Kosten:** kein Tool-Aufruf, der echtes Geld kostet. Keine kostenpflichtigen Funktionen oder Upgrades.
    In der Freigabe-Nachricht an Lukas eine Zeile „Rechte-Check: bestanden (Musik eigen, Bilder eigen, Stimme ElevenLabs bezahlt, keine fremden Marken/Figuren, KI gekennzeichnet)“ bzw. was auffiel.
10. **Übergabe an vidIQ (über GitHub):** Video und `thumb.png` nach `/mnt/user-data/outputs/` kopieren und beide mit `SendUserFile` an Lukas senden. Dann in einem frischen Ordner:
    `git init -q up && cd up && git checkout -q --orphan upload && cp <video> . && git add . && git commit -qm upload && git remote add origin https://github.com/lukashaerle/faktenfabrik-uploads && git push -q -f origin upload`
    → `vidiq_video_upload` mit `https://raw.githubusercontent.com/lukashaerle/faktenfabrik-uploads/upload/<dateiname>.mp4`. Mit curl die vidIQ-`videoUrl` laden und per `cmp` mit dem Original vergleichen. Danach Branch löschen: `git push -q origin --delete upload`.
11. **Entwurf:** `vidiq_social_post_draft_create`, media = uploadId,
    TikTok: privacyLevel PUBLIC_TO_EVERYONE, allowComment true, isAiGenerated true, musicUsageConfirmed true.
    YouTube: thumbnailImageId = `thumb.png` (vorher mit `vidiq_upload_image` hochladen; Kanal ist seit 17.11. per Telefon verifiziert; wird es trotzdem abgelehnt, bricht das den Upload nicht ab – dann in der Erfolgsmeldung „YouTube-Titelbild abgelehnt“ erwähnen, sonst „YouTube-Titelbild gesetzt“), title (≤100 Zeichen, endet mit „#shorts“), privacyStatus public, categoryId 27, tags (6–10), text = Beschreibung mit Quellenlinks, „Dieses Video wurde mit KI-Unterstützung erstellt.“ und Hashtags.
    Gemeinsamer Text (TikTok-Caption): 1–2 Sätze Hook + „Quellen: …“ + genau 5 Hashtags inkl. #faktenfabrik.
    publishAt = Slot-Zeit heute (Europe/Berlin, mit Zeitzone), nur wenn sie mehr als 5 Minuten in der Zukunft liegt; sonst ohne publishAt (sofort nach Ok).
12. **Angepinnter Kommentar:** Den im Produktionspaket vorbereiteten Kanal-Kommentar (Frage oder Zusatzfakt, max. 150 Zeichen) in der Erfolgsmeldung in #uploads mitschicken als „📌 Zum Anpinnen: <Text>“ – Lukas postet und pinnt ihn selbst (über vidIQ kann man keine eigenen Kommentare posten).
12b. **Benachrichtigen:** Mit `SendUserMessage` (und PushNotification, falls vorhanden) Lukas schreiben: Thema, Titel, Caption, Zeitpunkt, alle drei Konten (TikTok, YouTube, Instagram), Titelbild, Link/Datei zum Ansehen, „Antworte mit Ok, dann plane ich es ein.“
13. **Nach „Ok“:** `vidiq_social_post_publish` (postId + revision). Status prüfen, Links melden. Instagram-Reel mit demselben Video wie in der Aufgabe beschrieben veröffentlichen. Instagram-Cover ist das erste Bild des Videos (siehe 9b a). Kommt das Ok nach der Slot-Zeit: Entwurf ohne publishAt aktualisieren (`vidiq_social_post_draft_update`), Lukas den neuen Stand zeigen, nach Ok sofort veröffentlichen.
14. **Protokoll:** `system/themen_log.json` ergänzen ({datum, slot, thema, titel, tiktok_url, youtube_url}), committen und auf `main` pushen (vorher `git pull --rebase --depth=1` falls nötig).

## Wochenauftrag (Themenliste)

Jeden Sonntag: 21 Themen für Montag–Sonntag der Folgewoche (3 pro Tag, passend zu den Slots), abwechslungsreich, gut belegbar, keine Wiederholung aus `themen_log.json` (auch nicht unter anderem Titel) und nicht von anderen Creatorn übernommen (Originalitäts-Check wie in Schritt 3). Für jedes Thema: Titelidee, Kernfakt, geplante Quelle(n), Hook-Idee, Teil-Moment. Als `system/themen.json` ins Repository (Branch main) committen und pushen (alte Datei vorher als `system/themen_<alte woche>.json` sichern) und Lukas die Liste als Dokument schicken.
`themen.json`-Format: {"woche": "JJJJ-MM-TT bis JJJJ-MM-TT", "tage": [{"datum": "JJJJ-MM-TT", "11:30": {...}, "17:30": {...}, "20:00": {...}}]}
