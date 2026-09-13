"""German strings - mirrors en.py 1:1 (self-test verifies parity).

app/i18n/de.py must define EXACTLY the same keys as en.py (the
self-test verifies key parity and {placeholder} parity). Brand names
(SoftUpdater, SHA-256, winget, GitHub, JSON) and paths stay as-is.
"""
from __future__ import annotations

MESSAGES = {
    # ------------------------------------------------------------- meta
    "app.name": "SoftUpdater",
    "win.title": "SoftUpdater – Update-Prüfung",
    "bits.64": "64-Bit",
    "bits.32": "32-Bit",
    "win.summary_build": "{name} – {bits} – Build {build}",
    "win.summary_plain": "{name} – {bits}",
    "win.summary_dev": "{name} – {bits} – (Entwicklervorschau)",
    "win.nonwin": "Kein Windows-Betriebssystem",
    "win.unknown": "Windows (unbekannt)",

    # ---------------------------------------------------------- toolbar
    "search.placeholder": "Installierte Anwendungen suchen...",
    "btn.refresh": "Anwendungen neu laden",
    "btn.open_dir": "Download-Ordner öffnen",
    "btn.settings": "Einstellungen",
    "btn.check_all": "Nach Updates suchen",
    "btn.check_sel": "Auswahl prüfen",
    "btn.download": "Ausgewählte Installer herunterladen",
    "chk.open": "Installer nach dem Download öffnen",
    "btn.pause": "Pause",
    "btn.resume": "Fortsetzen",
    "btn.cancel": "Abbrechen",
    "tip.refresh": "Liste der installierten Anwendungen neu einlesen",
    "tip.settings": "Sprache, Schriftgröße und weitere Einstellungen ändern",
    "tip.check_all": "Jede installierte Anwendung gegen ihre offizielle Quelle prüfen",
    "tip.check_sel": (
        "Liest die ausgewählten Anwendungen zunächst erneut aus der "
        "Registrierung ein (und erfasst so Versionen, die sich durch eine "
        "frische Installation geändert haben) und prüft sie anschließend "
        "gegen ihre offiziellen Quellen. Sie können auch mit der rechten "
        "Maustaste auf eine Zeile klicken und 'Diese Anwendung neu prüfen' "
        "wählen."),
    "tip.download": (
        "Die Dateien werden in Ihrem Downloads-Ordner gespeichert. Ist das "
        "Kontrollkästchen rechts aktiviert, öffnet sich jeder Installer "
        "automatisch, sobald sein Download abgeschlossen ist, damit Sie das "
        "Update sofort durchführen können."),
    "tip.open": (
        "Bei Aktivierung öffnet sich das Installer-Fenster von selbst, "
        "sobald ein Download abgeschlossen ist – Sie folgen einfach den "
        "Schritten, um die Anwendung zu aktualisieren. Die Installer werden "
        "weiterhin im Downloads-Ordner gespeichert. Nach Abschluss der "
        "Installation wird die Anwendung automatisch neu geprüft."),
    "tip.pause": (
        "Hält den aktuellen Download an. 'Fortsetzen' macht genau dort "
        "weiter – bereits heruntergeladene Daten gehen nicht verloren."),
    "tip.cancel": "Bricht den aktuellen Download ab",

    # ----------------------------------------------------------- table
    "col.app": "Anwendung",
    "col.pub": "Herausgeber",
    "col.installed": "Installiert",
    "col.latest": "Neueste",
    "col.status": "Status",
    "col.source": "Quelle",

    # ---------------------------------------------------------- status
    "status.update": "Update verfügbar",
    "status.latest": "Aktuell",
    "status.no_installer": "Kein Installer für dieses Betriebssystem",
    "status.vendor": "Vom Hersteller verwaltet",
    "status.no_source": "Keine Quelle gefunden",
    "status.failed": "Prüfung fehlgeschlagen",
    "status.pending": "Nicht geprüft",
    "status.skipped": "Version übersprungen",
    "status.checking": "Wird geprüft...",

    # -------------------------------------------------- status messages
    "msg.counts": "{total} Anwendungen - {checked} geprüft - {updates} Updates",
    "msg.postinstall_updated": "{name} auf {version} aktualisiert - jetzt auf dem neuesten Stand ✓",
    "msg.postinstall_uptodate": "{name} ist jetzt auf dem neuesten Stand ✓",
    "msg.ready": "Bereit.",
    "msg.found_apps": "{n} installierte Anwendungen gefunden.",
    "msg.checking_n": "{n} Anwendung(en) werden gegen offizielle Quellen geprüft...",
    "msg.select_first": "Wählen Sie zuerst eine oder mehrere Zeilen aus.",
    "msg.done": "Fertig – {n} Update(s) verfügbar",
    "msg.done_failed_tail": " – {n} Prüfung(en) fehlgeschlagen",
    "msg.no_jobs": (
        "Keine der ausgewählten Zeilen hat einen herunterladbaren Installer. "
        "Führen Sie zuerst eine Prüfung durch."),
    "msg.preparing_n": "{n} Download(s) werden vorbereitet...",
    "msg.preparing_one": "Download wird vorbereitet...",
    "msg.downloading_n": "{n} Installer werden heruntergeladen...",
    "msg.of_total": "von {total}",
    "msg.paused_row": "Pausiert: {name}",
    "msg.dl_title_paused": "{name} – pausiert",
    "msg.saved": "Gespeichert: {path}",
    "msg.saved_verified": "Gespeichert: {path} – SHA-256 verifiziert",
    "msg.after_install_open": (
        "Der Installer wurde geöffnet. Nachdem Sie die Installation "
        "abgeschlossen haben, wird diese Zeile automatisch neu geprüft und "
        "wechselt zu 'Aktuell'."),
    "msg.after_install": (
        "Nachdem Sie die Anwendung installiert haben, wird diese Zeile "
        "automatisch neu geprüft und wechselt zu 'Aktuell'."),
    "msg.dl_failed": "Download fehlgeschlagen für {name}: {info}",
    "msg.dl_finished": "Downloads abgeschlossen – {ok} erfolgreich",
    "msg.dl_finished_failed_tail": ", {n} fehlgeschlagen",
    "msg.dl_finished_files_tail": " Die Dateien liegen in: {path}",
    "msg.dl_finished_none_tail": (
        " Nichts wurde gespeichert – die offiziellen Server konnten keinen "
        "gültigen Installer liefern (Details siehe 'Log-Ordner öffnen' in "
        "den Einstellungen). Sie können mit der rechten Maustaste auf die "
        "Zeile klicken und stattdessen 'Offizielle Seite öffnen' verwenden."),
    "msg.cancelling": "Download wird abgebrochen...",
    "msg.could_not_open": "Installer konnte nicht geöffnet werden: {err} – Datei liegt unter: {path}",
    "msgbox.open_fail_text": (
        "Der Installer wurde gespeichert, aber Windows konnte ihn nicht öffnen\n"
        "({err}).\n\n"
        "Der Ordner wurde für Sie geöffnet – doppelklicken Sie\n"
        "dort auf die Datei:\n"
        "{path}"),
    "msg.updated_rechecking": (
        "{name} wurde auf {version} aktualisiert – wird automatisch neu geprüft..."),
    "msg.auto_interval_on": "Die automatische Neuprüfung alle {hours} Stunde(n) ist aktiviert.",
    "msg.hidden_restored": "Ausgeblendete Anwendungen wiederhergestellt – die Liste wurde neu eingelesen.",
    "msg.skipped_restored": (
        "Übersprungene Versionen wiederhergestellt – {n} Update(s) werden "
        "wieder angezeigt."),
    "msg.hidden_one": "{name} ausgeblendet. In den Einstellungen wiederherstellbar.",
    "msg.skip_done": (
        "Version {version} von {name} wird übersprungen. Neuere Versionen "
        "werden weiterhin angezeigt."),
    "msg.unskip_done": (
        "Version {version} von {name} wird wieder als Update angezeigt."),
    "msg.exported": "{n} Anwendung(en) in {file} exportiert",
    "msg.error": "Fehler: {err}",
    "msgbox.error_text": "Etwas ist schiefgelaufen:\n{err}",

    # ------------------------------------------------------ skip notes
    "note.skipped": (
        "Sie haben Version {version} übersprungen. Übersprungene Versionen "
        "können Sie in den Einstellungen wiederherstellen."),
    "msg.last_known_tail": "das zuletzt bekannte Ergebnis wird angezeigt.",

    # ---------------------------------------------------- context menu
    "menu.details": "Details anzeigen",
    "tip.menu.details": (
        "Versionen, Quelle, den direkten Installer-Link (zum Kopieren) und "
        "die Erklärung der Prüfung für diese Anwendung."),
    "menu.recheck": "Diese Anwendung neu prüfen",
    "tip.menu.recheck": (
        "Liest die DERZEIT installierte Version dieser Anwendung aus der "
        "Registrierung (z. B. direkt nach der Installation eines "
        "heruntergeladenen Updates) und prüft sie gegen ihre offizielle "
        "Quelle – nur diese Anwendung, nicht die gesamte Liste."),
    "menu.download": "Installer herunterladen",
    "menu.src": "Offizielle Seite öffnen",
    "menu.skip": "Diese Version überspringen ({version})",
    "menu.unskip": "Version nicht mehr überspringen ({version})",
    "tip.menu.skip": (
        "Verhindert, dass DIESE Version als Update angezeigt wird (eine "
        "neuere wird weiterhin angeboten). In den Einstellungen "
        "wiederherstellen."),
    "tip.menu.unskip": "Zeigt diese Version wieder als Update an.",
    "menu.hide": "Diese Anwendung ausblenden",
    "tip.menu.hide": (
        "Entfernt die Anwendung aus der Liste (für Tools, die Sie manuell "
        "aktualisieren). Ausgeblendete Anwendungen können Sie in den "
        "Einstellungen wiederherstellen."),

    # -------------------------------------------------- details dialog
    "det.title": "Details – {name}",
    "det.publisher": "Herausgeber",
    "det.installed_version": "Installierte Version",
    "det.latest_version": "Neueste Version",
    "det.status": "Status",
    "det.source": "Quelle",
    "det.size": "Download-Größe",
    "det.arch": "Architektur",
    "det.sha": "SHA-256",
    "det.sha_ok": "von der Quelle veröffentlicht (nach dem Download verifiziert)",
    "det.sha_none": "von der Quelle nicht veröffentlicht",
    "det.placeholder": "Führen Sie eine Prüfung aus, um den Installer-Link aufzulösen",
    "btn.copy": "Link kopieren",
    "btn.open_page": "Offizielle Seite öffnen",
    "btn.close": "Schließen",

    # ------------------------------------------------------- tray/toast
    "tray.open": "SoftUpdater öffnen",
    "tray.check": "Jetzt nach Updates suchen",
    "tray.quit": "Beenden",
    "tray.tip_updates": "SoftUpdater – {n} Update(s) verfügbar",
    "tray.tip_ok": "SoftUpdater – alles auf dem neuesten Stand",
    "toast.updates_body": (
        "{n} Update(s) verfügbar – öffnen Sie SoftUpdater, um sie "
        "herunterzuladen."),
    "toast.installed_title": "Update installiert",
    "toast.installed_body": "{name} ist jetzt auf dem neuesten Stand{tail}",
    "toast.installed_tail": " (Version {version})",

    # ---------------------------------------------------- export/import
    "fd.export_title": "Anwendungsliste exportieren",
    "fd.import_title": "Anwendungsliste importieren",
    "fd.choose_dir": "Download-Ordner wählen",
    "msgbox.import_none_title": "Anwendungsliste importieren",
    "msgbox.import_none_text": (
        "Diese Datei enthält keine SoftUpdater-Anwendungsliste "
        "(exportieren Sie zuerst eine über 'Anwendungsliste exportieren')."),
    "rep.header": "Die importierte Liste enthält {n} Anwendung(en).",
    "rep.block": "{title} ({n}):",
    "rep.more": "...und {n} weitere",
    "rep.row_update": "{name} (hier: {here}, Export enthielt: {export})",
    "rep.missing": "Auf diesem PC nicht vorhanden",
    "rep.need_update": "Update weiterhin verfügbar",
    "rep.up_to_date": "Hier bereits auf dem neuesten Stand",
    "rep.plain": "Vorhanden (keine Versionsangabe im Export)",
    "rep.nothing": "Nichts zu berichten – die Liste scheint leer zu sein.",

    # ------------------------------------------------- source labels
    "src.vendor": "Vom Hersteller verwaltet",
    "src.winget": "Offizielles Winget-Manifest",
    "src.github": "GitHub – {repo}",
    "src.github_auto": "GitHub (automatisch zugeordnet) – {repo}",
    "src.feed": "Offizieller Versions-Feed",
    "src.website": "Offizielle Website",
    "src.mozilla": "Offizieller Mozilla-Download",
    "src.vlc": "Offizieller VideoLAN-Mirror",
    "src.edge": "Offizielle Microsoft-Edge-Updates",
    "src.discord": "Offizieller Discord-Download",
    "src.dl_server": "Offizieller Download-Server",

    # -------------------------------------------------- checker notes
    "note.check_error": "Prüffehler: {cls}",
    "note.init_error": "Initialisierungsfehler: {cls}",
    "note.unexpected_error": "Unerwarteter Fehler: {cls}",
    "note.no_source": (
        "Keine offizielle Quelle für diese Anwendung gefunden. Sie ist "
        "möglicherweise Closed Source oder zu sehr ein Nischenprodukt."),
    "note.latest": "Bereits auf der neuesten Version.",
    "note.newer_than_latest": (
        "Die installierte Version ist neuer als die neueste öffentliche "
        "Veröffentlichung."),
    "note.version_unknown": "Installierte Version unbekannt – bitte manuell überprüfen.",
    "note.rate_limited": "GitHub-API-Ratenlimit erreicht – versuchen Sie es später erneut.",
    "note.no_winget_manifest": "Für dieses Paket existiert kein winget-Manifest.",
    "note.winget_list_error": "Fehler beim Auflisten des winget-Manifests (HTTP {code}).",
    "note.no_winget_versions": "Das winget-Manifest enthält keine veröffentlichten Versionen.",
    "note.winget_installer_missing": "Das winget-Installer-Manifest wurde nicht gefunden.",
    "note.winget_installer_error": "Fehler im winget-Installer-Manifest (HTTP {code}).",
    "note.winget_no_arch": (
        "Im neuesten offiziellen Manifest ist kein {arch}-Installer "
        "veröffentlicht."),
    "note.repo_not_found": "Repository oder neuester Release nicht gefunden.",
    "note.github_error": "GitHub-API-Fehler (HTTP {code}).",
    "note.auto_match_unrelated": (
        "Das automatisch zugeordnete Repository scheint nicht zu passen "
        "(älteres Projekt mit einem ähnlichen Namen)."),
    "note.matched_by_name": (
        "Über den Namen zugeordnet – prüfen Sie den Herausgeber, bevor Sie "
        "installieren."),
    "note.github_no_arch": (
        "Kein Windows-Installer für diese Architektur im neuesten Release."),
    "note.feed_error": "Fehler im Versions-Feed (HTTP {code}).",
    "note.feed_parse": "Der Versions-Feed konnte nicht ausgewertet werden.",
    "note.vendor_arch_installer_missing": "Der Hersteller veröffentlicht keinen Installer für diese Architektur.",
    "note.no_installer_url": "Für diese Architektur ist keine Installer-URL veröffentlicht.",
    "note.vendor_page_error": "Fehler auf der Herstellerseite (HTTP {code}).",
    "note.vendor_no_arch": (
        "Version gefunden, aber kein Installer für diese Architektur auf "
        "der Herstellerseite."),
    "note.vendor_latest_unknown": (
        "Die neueste Version konnte auf der Herstellerseite nicht ermittelt "
        "werden."),
    "note.mozilla_feed_error": "Fehler im Versions-Feed von Mozilla (HTTP {code}).",
    "note.mozilla_parse": "Der Versions-Feed von Mozilla konnte nicht ausgewertet werden.",
    "note.vlc_server_error": "Fehler des VideoLAN-Servers (HTTP {code}).",
    "note.vlc_no_installer": "Kein Installer auf dem VideoLAN-Mirror gefunden.",
    "note.edge_feed_error": "Fehler im Update-Feed von Microsoft Edge (HTTP {code}).",
    "note.edge_no_stable": "Kein stabiles Release für diese Architektur gefunden.",
    "note.discord_no_version": (
        "Neuester stabiler Installer (Version wird von Discord nicht "
        "offengelegt)."),
    "note.dl_server_error": "Fehler des Download-Servers (HTTP {code}).",
    "note.dl_list_error": "Release-Ordner konnten nicht aufgelistet werden.",
    "note.blender_64bit_only": "Blender veröffentlicht ausschließlich 64-Bit-Installer.",
    "note.no_windows_installer_folder": (
        "Kein Windows-Installer im Ordner des neuesten Releases."),

    # ---------------------------------------------- downloader errors
    "dlerr.http": "Server gab HTTP {code} zurück.",
    "dlerr.cancelled": "Download abgebrochen.",
    "dlerr.no_url": "Keine Download-URL angegeben.",
    "dlerr.give_up": (
        "Der Download konnte nach mehreren Versuchen nicht abgeschlossen "
        "werden ({err}) – nichts wurde gespeichert. Prüfen Sie die "
        "Verbindung und versuchen Sie es erneut, oder laden Sie die Datei "
        "über 'Offizielle Seite öffnen' selbst herunter."),
    "dlerr.sha_mismatch": (
        "SHA-256-Prüfsumme stimmt nicht überein – die heruntergeladene "
        "Datei entsprach nicht der offiziellen Prüfsumme und wurde "
        "gelöscht."),
    "dlerr.not_installer": (
        "Der Download kam nicht als gültiger Installer an (stattdessen "
        "wurde eine Fehler- oder Sperrseite geliefert) – er wurde gelöscht. "
        "Versuchen Sie es erneut, oder laden Sie die Datei über 'Offizielle "
        "Seite öffnen' selbst herunter."),
    "dlerr.final_validation": (
        "Der gespeicherte Installer bestand die abschließende Prüfung "
        "nicht und wurde gelöscht – bitte versuchen Sie den Download "
        "erneut."),
    "dlerr.all_locations": (
        "Der Download ist bei allen {n} offiziellen Serverstandorten "
        "fehlgeschlagen (letzter Fehler: {err}). Nichts wurde gespeichert "
        "– prüfen Sie die Verbindung und versuchen Sie es erneut, oder "
        "laden Sie die Datei über 'Offizielle Seite öffnen' selbst "
        "herunter."),
    "dlerr.failed_one": (
        "Der Download konnte nicht abgeschlossen werden ({err}) – nichts "
        "wurde gespeichert. Prüfen Sie die Verbindung und versuchen Sie es "
        "erneut, oder laden Sie die Datei über 'Offizielle Seite öffnen' "
        "selbst herunter."),

    # ------------------------------------------- catalog variant notes
    "vn.calibre": (
        "Wenn kein Installer beigefügt ist, laden Sie von calibre-ebook.com "
        "herunter."),
    "vn.telegram": "Offizielle Releases von Telegram Desktop (tdesktop).",
    "vn.vscode": "Offizieller Update-Dienst von VS Code.",
    "vn.winterminal": "Öffnen Sie die .msixbundle mit dem App Installer.",
    "vn.ffmpeg": "Automatisch erstellte Binärdateien von BtbN (gängige Community-Builds).",
    "vn.inkscape": (
        "Offizielles Mirror-Repository; ist kein Installer veröffentlicht, "
        "laden Sie von inkscape.org herunter."),
    "vn.winrar_x86": "WinRAR 7 wird nur für 64-Bit-Windows veröffentlicht.",
    "vn.winrar": "Offizielle WinRAR-Release-Seite (rarlab.com).",
    "vn.nekobox": "Offizielles Release von NekoBox for PC (nekoray).",
    "vn.qtum": "Qtum veröffentlicht nicht signierte Windows-Setup-Binärdateien.",

    # --------------------------------------------- blocked-app reasons
    "blk.steam": "Steam aktualisiert sich über seinen eigenen Client.",
    "blk.epic": "Der Epic Games Launcher aktualisiert sich selbst.",
    "blk.battlenet": "Battle.net aktualisiert sich selbst.",
    "blk.gog": "GOG Galaxy aktualisiert sich selbst.",
    "blk.ubisoft": "Ubisoft Connect aktualisiert sich selbst.",
    "blk.ea_app": "Die EA app aktualisiert sich selbst.",
    "blk.origin": "EA/Origin aktualisiert sich selbst.",
    "blk.office": "Office wird über Microsoft Click-to-Run aktualisiert.",
    "blk.m365": "Microsoft 365 wird automatisch aktualisiert.",
    "blk.onedrive": "OneDrive wird automatisch über Microsoft Update aktualisiert.",
    "blk.dropbox": "Dropbox aktualisiert sich selbst im Hintergrund.",
    "blk.gdrive": "Google Drive aktualisiert sich selbst.",
    "blk.spotify": "Spotify aktualisiert sich selbst im Hintergrund.",
    "blk.whatsapp": "WhatsApp wird über den Microsoft Store aktualisiert.",
    "blk.teams": "Teams aktualisiert sich automatisch.",
    "blk.slack": "Slack aktualisiert sich automatisch.",
    "blk.zoom": "Zoom aktualisiert sich automatisch.",
    "blk.teamviewer": "TeamViewer aktualisiert sich automatisch.",
    "blk.anydesk": "AnyDesk aktualisiert sich automatisch.",
    "blk.opera": "Opera wird über seinen eigenen Updater aktualisiert.",
    "blk.vivaldi": "Vivaldi wird über seinen eigenen Updater aktualisiert.",
    "blk.adobe": "Adobe-Apps werden über Creative Cloud / den Acrobat-Updater aktualisiert.",
    "blk.nvidia": "GPU-Treiber werden über GeForce Experience / die NVIDIA App aktualisiert.",
    "blk.amd": "AMD-Treiber werden über AMD Software aktualisiert.",
    "blk.malwarebytes": "Malwarebytes aktualisiert sich automatisch.",
    "blk.kaspersky": "Die Antivirus-Software aktualisiert sich automatisch.",
    "blk.avast": "Avast aktualisiert sich automatisch.",
    "blk.avg": "AVG aktualisiert sich automatisch.",
    "blk.bitdefender": "Bitdefender aktualisiert sich automatisch.",
    "blk.webview2": "Die WebView2-Runtime wird über Microsoft Update aktualisiert.",
    "blk.termius": "Termius aktualisiert sich automatisch.",
    "blk.afterburner": "MSI Afterburner wird über den eigenen Updater bzw. msi.com aktualisiert.",
    "blk.rivatuner": "RivaTuner wird mit MSI Afterburner mitgeliefert; Updates über msi.com.",
    "blk.potplayer": "PotPlayer aktualisiert sich selbst; Installer unter potplayer.daum.net.",
    "blk.windscribe": "Windscribe aktualisiert sich automatisch.",
    "blk.fdm": "FDM aktualisiert sich selbst; Installer unter freedownloadmanager.com.",
    "blk.capcut": "CapCut aktualisiert sich automatisch.",
    "blk.canva": "Canva aktualisiert sich automatisch.",
    "blk.bluestacks": "BlueStacks aktualisiert sich automatisch.",
    "blk.ldplayer": "LDPlayer aktualisiert sich automatisch.",
    "blk.driver_booster": "Driver Booster wird über den eigenen IObit-Updater aktualisiert.",
    "blk.iobit": "IObit-Anwendungen werden über ihren eigenen Updater aktualisiert.",
    "blk.allavsoft": "Allavsoft hat keinen öffentlichen Versions-Feed; siehe allavsoft.com.",
    "blk.zdsoft": "Die neueste Version des ZD Soft Screen Recorder finden Sie auf zdsoft.com.",
    "blk.officesuite": "OfficeSuite aktualisiert sich selbst.",
    "blk.maxon": "Maxon-Anwendungen werden über die Maxon App aktualisiert.",
    "blk.icue": "Corsair iCUE aktualisiert sich selbst.",
    "blk.miniconda": "Aktualisierung über 'conda update' oder einen neuen Installer von anaconda.com.",
    "blk.python_launcher": "Wird zusammen mit Python installiert und mit Python aktualisiert.",
    "blk.android_studio": "Android Studio aktualisiert sich über seinen eigenen Updater.",
    "blk.java": "Java wird über Oracles Java Auto Update aktualisiert; JDKs über oracle.com/java.",
    "blk.intel": "Intel-Treiber/-Komponenten werden über den Intel Driver & Support Assistant aktualisiert.",
    "blk.realtek": "Realtek-Treiber werden vom Hersteller Ihres PCs oder Mainboards bereitgestellt.",
    "blk.rapoo": "Treiber für Peripheriegeräte stammen von rapoo.com.",
    "blk.asus": "ASUS-Dienstprogramme werden über Armoury Crate / MyASUS aktualisiert.",
    "blk.rog": "ASUS-ROG-Dienstprogramme werden über Armoury Crate / MyASUS aktualisiert.",
    "blk.armoury": "Komponenten von ASUS Armoury Crate werden gemeinsam aktualisiert.",
    "blk.aura": "ASUS-AURA-Komponenten werden über Armoury Crate aktualisiert.",
    "blk.tap_windows": "Der TAP-Adapter wird zusammen mit OpenVPN installiert; aktualisieren Sie OpenVPN.",
    "blk.openvpn": "OpenVPN wird über openvpn.net aktualisiert; OpenVPN Connect aktualisiert sich selbst.",
    "blk.maintenance_service": "Wird zusammen mit Firefox installiert und gemeinsam mit Firefox aktualisiert.",
    "blk.vcredist": "VC++ Redistributables werden von Anwendungs-Installern installiert; die neueste Version finden Sie unter aka.ms/vsredist.",
    "blk.dotnet": ".NET-Komponenten werden von Anwendungs-Installern oder Visual Studio installiert.",
    "blk.ms_windows": "Windows-Systemkomponente – aktualisiert über Windows Update.",
    "blk.winsdk": "Das Windows SDK wird zusammen mit Visual Studio aktualisiert.",
    "blk.xna": "Ältere Microsoft-XNA-Komponente; wird nicht mehr aktualisiert.",
    "blk.vb": "Ältere VB-Runtime; wird von Anwendungs-Installern installiert.",
    "blk.update_health": "Systemkomponente, aktualisiert über Windows Update.",
    "blk.visio": "Visio wird mit Microsoft Office aktualisiert (Click-to-Run).",
    "blk.project": "Project wird mit Microsoft Office aktualisiert (Click-to-Run).",
    "blk.powerpoint": "PowerPoint wird mit Microsoft Office aktualisiert.",
    "blk.word": "Word wird mit Microsoft Office aktualisiert.",
    "blk.excel": "Excel wird mit Microsoft Office aktualisiert.",
    "blk.outlook": "Outlook wird mit Microsoft Office aktualisiert.",
    "blk.access": "Access wird mit Microsoft Office aktualisiert.",
    "blk.onenote": "OneNote wird mit Microsoft Office aktualisiert.",
    "blk.publisher": "Publisher wird mit Microsoft Office aktualisiert.",
    "blk.visual_studio": "Visual Studio-Komponenten werden über den Visual Studio Installer aktualisiert.",

    # ------------------------------------------------------ settings
    "set.title": "Einstellungen",
    "set.nav.checking": "Prüfung",
    "set.nav.downloads": "Downloads",
    "set.nav.apps": "Anwendungen",
    "set.nav.backup": "Backup",
    "set.nav.appearance": "Darstellung",
    "set.header.checking": "Prüfung",
    "set.header.downloads": "Downloads",
    "set.header.apps": "Anwendungen",
    "set.header.backup": "Backup & Wartung",
    "set.header.appearance": "Darstellung",
    "set.nav.about": "Über",
    "set.header.about": "Über SoftUpdater",
    "set.about.tagline": "Prüft installierte Programme gegen ihre offiziellen Quellen - kostenlos & open source.",
    "set.about.version": "Version",
    "set.about.dev": "Entwickler",
    "set.about.source": "Offizieller Quellcode auf GitHub",
    "set.about.license": "Veröffentlicht unter der MIT-Lizenz - frei zum Verwenden, Studieren, Ändern und Teilen.",
    "set.about.official": "Laden Sie SoftUpdater immer nur aus dem offiziellen Repository herunter:",
    "set.chk_auto": "Beim Start der Anwendung nach Updates suchen",
    "tip.set.chk_auto": (
        "Führt unmittelbar nach dem Öffnen der Anwendung von selbst eine "
        "vollständige Update-Prüfung durch, sodass Sie die Update-Liste "
        "ohne einen Klick sehen."),
    "set.lbl_interval": "Automatisch neu prüfen alle",
    "set.cmb_never": "Nie",
    "set.cmb_hours": "{n} Stunde(n)",
    "tip.set.interval": (
        "Führt automatisch eine vollständige Prüfung durch, solange die "
        "Anwendung geöffnet ist – auch wenn Sie sie nicht bedienen. "
        "Gefundene Updates lösen eine Benachrichtigung aus."),
    "set.chk_notify": "Benachrichtigung anzeigen, wenn Updates gefunden werden",
    "tip.set.notify": (
        "Windows-Toast über neue Updates nach einer automatischen Prüfung "
        "(Beim Start oder nach Zeitplan). Manuelle Prüfungen unterbrechen "
        "Sie nie."),
    "set.hint.checking": (
        "Automatische Prüfungen decken jede Anwendung mit ihrer "
        "offiziellen Quelle ab (Ergebnisse werden zwischengespeichert, "
        "daher sind Wiederholungen schnell)."),
    "set.lbl_save_to": "Installer speichern in",
    "set.btn.browse": "Durchsuchen...",
    "set.btn.reset_dir": "Standardordner verwenden",
    "tip.set.reset_dir": "Setzt zurück auf Downloads\\SoftUpdater",
    "set.dl_default": "Downloads\\SoftUpdater (Standard)",
    "set.hint.downloads": (
        "Wählen Sie, wo heruntergeladene Installer gespeichert werden. Der "
        "Standard ist der SoftUpdater-Ordner in Ihren Downloads."),
    "set.btn.restore_hidden": "Ausgeblendete Anwendungen wiederherstellen",
    "tip.set.restore_hidden": (
        "Stellt alle Anwendungen wieder her, die Sie über das "
        "Rechtsklick-Menü ausgeblendet haben, und liest die Liste neu ein."),
    "set.lbl_hidden_n": "{n} Anwendung(en) sind aus der Liste ausgeblendet",
    "set.lbl_hidden_none": "Nichts ausgeblendet",
    "set.btn.restore_skip": "Übersprungene Versionen wiederherstellen",
    "tip.set.restore_skip": (
        "Lässt übersprungene Versionen wieder als Updates erscheinen (sie "
        "wurden über die Rechtsklick-Aktion 'Diese Version überspringen' "
        "versteckt)."),
    "set.lbl_skip_n": "{n} übersprungene Version(en)",
    "set.lbl_skip_none": "Keine übersprungenen Versionen",
    "set.hint.apps": (
        "Sie blenden eine Anwendung aus, indem Sie im Hauptfenster mit der "
        "rechten Maustaste auf ihre Zeile klicken (nützlich für Tools, die "
        "Sie manuell aktualisieren). Eine einzelne Version lässt sich auf "
        "dieselbe Weise überspringen."),
    "set.btn.export": "Anwendungsliste exportieren...",
    "tip.set.export": (
        "Speichert alle gelisteten Anwendungen mit ihren Versionen in "
        "einer JSON-Datei – ein kleines Backup der auf diesem PC "
        "installierten Software."),
    "set.btn.import": "Anwendungsliste importieren...",
    "tip.set.import": (
        "Vergleicht eine zuvor exportierte Liste mit den Installationen "
        "auf diesem PC und berichtet, was fehlt oder ein Update braucht."),
    "set.btn.log": "Log-Ordner öffnen",
    "tip.set.log": (
        "Die Anwendung schreibt ein kleines Protokoll über Prüfungen, "
        "Downloads und Fehler – praktisch, wenn etwas gemeldet werden "
        "muss."),
    "set.hint.backup": (
        "Die Exportdatei ist eine einfache JSON-Liste – nichts wird "
        "irgendwo hochgeladen."),
    "set.lbl_font": "Schriftgröße",
    "set.pt_suffix": " pt",
    "set.btn.reset_font": "Schriftgröße auf Standard zurücksetzen",
    "tip.set.reset_font": "Setzt die Schriftgröße auf {default} pt zurück",
    "set.hint.appearance": (
        "Wählen Sie hier eine Größe - das Beispiel unten zeigt sie. Mit "
        "\"Fertig\" wird sie auf die ganze Anwendung angewendet und für "
        "das nächste Mal gespeichert."),
    "set.lbl_preview": "Vorschau",
    "set.font.sample": (
        "Dies ist ein Beispieltext zur Vorschau der Schriftgröße der "
        "Anwendung - Aa 123"),
    "set.btn.done": "Fertig",
    "set.lbl_language": "Sprache",
    "set.hint.language": (
        "Wird sofort angewendet – jedes Fenster wechselt ohne Neustart."),
    "set.btn.tour": "Kurze Einführung erneut anzeigen",
    "tip.set.tour": (
        "Zeigt die Tipps des ersten Starts erneut (Ihre Auswahl 'Nicht "
        "mehr anzeigen' bleibt erhalten)."),

    # ----------------------------------------------------- onboarding
    "ob.title": "SoftUpdater-Kurzeinführung",
    "ob.page_of": "Seite {n} von {total}",
    "ob.btn.next": "Weiter",
    "ob.btn.back": "Zurück",
    "ob.btn.skip": "Einführung überspringen",
    "ob.btn.finish": "Jetzt starten",
    "ob.chk.never": "Diese Tipps nicht mehr anzeigen",
    "ob.welcome.title": "Willkommen bei SoftUpdater",
    "ob.welcome.body": (
        "SoftUpdater gleicht Ihre installierten Anwendungen mit ihren "
        "offiziellen Quellen ab und lädt die neuesten Installer für Sie "
        "herunter – sicher, mit SHA-256-Verifizierung.\n\n"
        "Beginnen Sie mit der großen grünen Schaltfläche: Nach Updates "
        "suchen."),
    "ob.ctx.title": "Rechtsklick auf eine beliebige Zeile",
    "ob.ctx.body": (
        "Das Rechtsklick-Menü jeder Anwendungszeile enthält die "
        "erweiterten Funktionen:\n"
        "- Details anzeigen (Versionen, Quelle, Installer-Link)\n"
        "- Nur diese Anwendung neu prüfen\n"
        "- Installer herunterladen / offizielle Seite öffnen\n"
        "- Eine bestimmte Version überspringen oder Anwendungen "
        "ausblenden, die Sie selbst aktualisieren"),
    "ob.dl.title": "Downloads, die die Arbeit zu Ende bringen",
    "ob.dl.body": (
        "Installer werden unter Downloads\\SoftUpdater gespeichert. Sie "
        "können sich nach dem Download automatisch öffnen – und sobald "
        "Sie ein Update installieren, wechselt die Zeile von selbst zu "
        "'Aktuell'."),
    "ob.done.title": "Passen Sie es an",
    "ob.done.body": (
        "Die Einstellungen bieten alles: Diese Anwendung spricht "
        "Englisch, Persisch, Arabisch, Portugiesisch, Französisch und "
        "Deutsch (Rechts-nach-links inklusive), die Schriftgröße passt "
        "sich Ihren Augen an, und automatische Prüfungen folgen Ihrem "
        "Zeitplan. SoftUpdater ist außerdem im Systemtray vertreten."),
}
