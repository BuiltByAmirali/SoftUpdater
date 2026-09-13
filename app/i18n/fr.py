"""French strings — mirrors en.py 1:1 (self-test verifies parity)."""
from __future__ import annotations

MESSAGES = {
    # ------------------------------------------------------------- meta
    "app.name": "SoftUpdater",
    "win.title": "SoftUpdater — Vérificateur de mises à jour",
    "bits.64": "64 bits",
    "bits.32": "32 bits",
    "win.summary_build": "{name} — {bits} — Build {build}",
    "win.summary_plain": "{name} — {bits}",
    "win.summary_dev": "{name} — {bits} — (aperçu de développement)",
    "win.nonwin": "OS non Windows",
    "win.unknown": "Windows (inconnu)",

    # ---------------------------------------------------------- toolbar
    "search.placeholder": "Rechercher des applications installées...",
    "btn.refresh": "Actualiser les applications",
    "btn.open_dir": "Ouvrir le dossier de téléchargement",
    "btn.settings": "Paramètres",
    "btn.check_all": "Rechercher des mises à jour",
    "btn.check_sel": "Vérifier la sélection",
    "btn.download": "Télécharger les installateurs sélectionnés",
    "chk.open": "Ouvrir les installateurs après le téléchargement",
    "btn.pause": "Pause",
    "btn.resume": "Reprendre",
    "btn.cancel": "Annuler",
    "tip.refresh": "Réanalyse la liste des applications installées",
    "tip.settings": "Modifie la langue, la taille de police et les autres préférences",
    "tip.check_all": "Vérifie chaque application installée auprès de sa source officielle",
    "tip.check_sel": (
        "Réanalyse d'abord la ou les applications sélectionnées dans le "
        "registre (pour prendre en compte les versions modifiées par une "
        "installation récente), puis les vérifie auprès de leurs sources "
        "officielles. Vous pouvez aussi faire un clic droit sur une ligne "
        "et choisir « Revérifier cette application »."),
    "tip.download": (
        "Les fichiers sont enregistrés dans votre dossier Downloads. Si la "
        "case à droite est activée, chaque installateur s'ouvre "
        "automatiquement à la fin de son téléchargement, pour que vous "
        "puissiez lancer la mise à jour immédiatement."),
    "tip.open": (
        "Quand la case est cochée, la fenêtre de l'installateur s'ouvre "
        "toute seule dès qu'un téléchargement se termine — vous n'avez "
        "qu'à suivre ses étapes pour mettre l'application à jour. Les "
        "installateurs restent enregistrés dans le dossier Downloads. Une "
        "fois l'installation terminée, l'application est revérifiée "
        "automatiquement."),
    "tip.pause": (
        "Met en pause le téléchargement en cours. La reprise continue là "
        "où il s'est arrêté — les données déjà téléchargées ne sont pas "
        "perdues."),
    "tip.cancel": "Annule le téléchargement en cours",

    # ----------------------------------------------------------- table
    "col.app": "Application",
    "col.pub": "Éditeur",
    "col.installed": "Installée",
    "col.latest": "Dernière",
    "col.status": "Statut",
    "col.source": "Source",

    # ---------------------------------------------------------- status
    "status.update": "Mise à jour disponible",
    "status.latest": "À jour",
    "status.no_installer": "Aucun installateur pour cet OS",
    "status.vendor": "Géré par l'éditeur",
    "status.no_source": "Aucune source trouvée",
    "status.failed": "Échec de la vérification",
    "status.pending": "Non vérifiée",
    "status.skipped": "Version ignorée",
    "status.checking": "Vérification...",

    # -------------------------------------------------- status messages
    "msg.counts": "{total} applications - {checked} vérifiées - {updates} mises à jour",
    "msg.postinstall_updated": "{name} mis à jour vers {version} - désormais à jour ✓",
    "msg.postinstall_uptodate": "{name} est désormais à jour ✓",
    "msg.ready": "Prêt.",
    "msg.found_apps": "{n} applications installées trouvées.",
    "msg.checking_n": "Vérification de {n} application(s) auprès des sources officielles...",
    "msg.select_first": "Sélectionnez d'abord une ou plusieurs lignes.",
    "msg.done": "Terminé — {n} mise(s) à jour disponible(s)",
    "msg.done_failed_tail": " — {n} vérification(s) en échec",
    "msg.no_jobs": (
        "Aucune ligne sélectionnée n'a d'installateur téléchargeable. "
        "Lancez d'abord une vérification."),
    "msg.preparing_n": "Préparation de {n} téléchargement(s)...",
    "msg.preparing_one": "Préparation du téléchargement...",
    "msg.downloading_n": "Téléchargement de {n} installateur(s)...",
    "msg.of_total": "sur {total}",
    "msg.paused_row": "En pause : {name}",
    "msg.dl_title_paused": "{name} — en pause",
    "msg.saved": "Enregistré : {path}",
    "msg.saved_verified": "Enregistré : {path} — vérifié par SHA-256",
    "msg.after_install_open": (
        "L'installateur a été ouvert. Une fois votre installation "
        "terminée, cette ligne est revérifiée automatiquement et passe à "
        "« À jour »."),
    "msg.after_install": (
        "Après votre installation, cette ligne est revérifiée "
        "automatiquement et passe à « À jour »."),
    "msg.dl_failed": "Échec du téléchargement de {name} : {info}",
    "msg.dl_finished": "Téléchargements terminés — {ok} réussi(s)",
    "msg.dl_finished_failed_tail": ", {n} en échec",
    "msg.dl_finished_files_tail": " Les fichiers sont dans : {path}",
    "msg.dl_finished_none_tail": (
        " Rien n'a été enregistré — les serveurs officiels n'ont pas pu "
        "fournir un installateur valide (voir « Ouvrir le dossier des "
        "journaux » dans les Paramètres pour plus de détails). Vous pouvez "
        "faire un clic droit sur la ligne et utiliser « Ouvrir la page "
        "officielle » à la place."),
    "msg.cancelling": "Annulation du téléchargement...",
    "msg.could_not_open": "Impossible d'ouvrir l'installateur : {err} — le fichier se trouve dans : {path}",
    "msgbox.open_fail_text": (
        "L'installateur a été enregistré mais Windows n'a pas pu "
        "l'ouvrir\n"
        "({err}).\n\n"
        "Son dossier a été ouvert pour vous — double-cliquez\n"
        "sur le fichier à cet endroit :\n"
        "{path}"),
    "msg.updated_rechecking": (
        "{name} a été mis à jour vers {version} — revérification "
        "automatique..."),
    "msg.auto_interval_on": "La revérification automatique toutes les {hours} heure(s) est activée.",
    "msg.hidden_restored": "Applications masquées restaurées — la liste a été réanalysée.",
    "msg.skipped_restored": (
        "Versions ignorées restaurées — {n} mise(s) à jour affichée(s) à "
        "nouveau."),
    "msg.hidden_one": "{name} masquée. Restaurez-la dans les Paramètres.",
    "msg.skip_done": (
        "La version {version} de {name} est ignorée. Les versions plus "
        "récentes continueront d'apparaître."),
    "msg.unskip_done": (
        "La version {version} de {name} réapparaît comme mise à jour."),
    "msg.exported": "{n} application(s) exportée(s) vers {file}",
    "msg.error": "Erreur : {err}",
    "msgbox.error_text": "Une erreur est survenue :\n{err}",

    # ------------------------------------------------------ skip notes
    "note.skipped": (
        "Vous avez ignoré la version {version}. Restaurez les versions "
        "ignorées dans les Paramètres."),
    "msg.last_known_tail": "affichage du dernier résultat connu.",

    # ---------------------------------------------------- context menu
    "menu.details": "Voir les détails",
    "tip.menu.details": (
        "Versions, source, le lien direct de l'installateur (copiable) et "
        "l'explication du vérificateur pour cette application."),
    "menu.recheck": "Revérifier cette application",
    "tip.menu.recheck": (
        "Interroge le registre pour connaître la version ACTUELLEMENT "
        "installée de cette application (par exemple juste après "
        "l'installation d'une mise à jour téléchargée) et la vérifie "
        "auprès de sa source officielle — pour cette application "
        "seulement, pas la liste."),
    "menu.download": "Télécharger l'installateur",
    "menu.src": "Ouvrir la page officielle",
    "menu.skip": "Ignorer cette version ({version})",
    "menu.unskip": "Rétablir la version ({version})",
    "tip.menu.skip": (
        "Empêche CETTE version d'apparaître comme mise à jour (une version "
        "plus récente restera proposée). À restaurer dans les Paramètres."),
    "tip.menu.unskip": "Réaffiche cette version comme mise à jour.",
    "menu.hide": "Masquer cette application",
    "tip.menu.hide": (
        "La retire de la liste (pour les outils que vous mettez à jour "
        "manuellement). Vous pouvez restaurer les applications masquées "
        "dans les Paramètres."),

    # -------------------------------------------------- details dialog
    "det.title": "Détails — {name}",
    "det.publisher": "Éditeur",
    "det.installed_version": "Version installée",
    "det.latest_version": "Dernière version",
    "det.status": "Statut",
    "det.source": "Source",
    "det.size": "Taille du téléchargement",
    "det.arch": "Architecture",
    "det.sha": "SHA-256",
    "det.sha_ok": "publié par la source (vérifié après le téléchargement)",
    "det.sha_none": "non publié par la source",
    "det.placeholder": "Lancez une vérification pour résoudre le lien de l'installateur",
    "btn.copy": "Copier le lien",
    "btn.open_page": "Ouvrir la page officielle",
    "btn.close": "Fermer",

    # ------------------------------------------------------- tray/toast
    "tray.open": "Ouvrir SoftUpdater",
    "tray.check": "Rechercher des mises à jour maintenant",
    "tray.quit": "Quitter",
    "tray.tip_updates": "SoftUpdater — {n} mise(s) à jour disponible(s)",
    "tray.tip_ok": "SoftUpdater — tout est à jour",
    "toast.updates_body": (
        "{n} mise(s) à jour disponible(s) — ouvrez SoftUpdater pour les "
        "télécharger."),
    "toast.installed_title": "Mise à jour installée",
    "toast.installed_body": "{name} est maintenant à jour{tail}",
    "toast.installed_tail": " (version {version})",

    # ---------------------------------------------------- export/import
    "fd.export_title": "Exporter la liste des applications",
    "fd.import_title": "Importer la liste des applications",
    "fd.choose_dir": "Choisir le dossier de téléchargement",
    "msgbox.import_none_title": "Importer la liste des applications",
    "msgbox.import_none_text": (
        "Ce fichier ne contient pas de liste d'applications SoftUpdater "
        "(exportez-en d'abord une avec « Exporter la liste des "
        "applications »)."),
    "rep.header": "La liste importée contient {n} application(s).",
    "rep.block": "{title} ({n}):",
    "rep.more": "...et {n} de plus",
    "rep.row_update": "{name} (ici : {here}, l'export contenait : {export})",
    "rep.missing": "Absente de ce PC",
    "rep.need_update": "Mise à jour toujours disponible",
    "rep.up_to_date": "Déjà à jour ici",
    "rep.plain": "Présente (pas d'information de version dans l'export)",
    "rep.nothing": "Rien à signaler — la liste semble vide.",

    # ------------------------------------------------- source labels
    "src.vendor": "Géré par l'éditeur",
    "src.winget": "Manifeste officiel Winget",
    "src.github": "GitHub — {repo}",
    "src.github_auto": "GitHub (appariement automatique) — {repo}",
    "src.feed": "Flux de versions officiel",
    "src.website": "Site officiel",
    "src.mozilla": "Téléchargement officiel Mozilla",
    "src.vlc": "Miroir officiel VideoLAN",
    "src.edge": "Mises à jour officielles de Microsoft Edge",
    "src.discord": "Téléchargement officiel Discord",
    "src.dl_server": "Serveur de téléchargement officiel",

    # -------------------------------------------------- checker notes
    "note.check_error": "Erreur de vérification : {cls}",
    "note.init_error": "Erreur d'initialisation : {cls}",
    "note.unexpected_error": "Erreur inattendue : {cls}",
    "note.no_source": (
        "Aucune source officielle trouvée pour cette application. Elle est "
        "peut-être à source fermée ou trop confidentielle."),
    "note.latest": "Déjà à la dernière version.",
    "note.newer_than_latest": (
        "La version installée est plus récente que la dernière version "
        "publique."),
    "note.version_unknown": "Version installée inconnue — vérifiez manuellement.",
    "note.rate_limited": "Limite de requêtes de l'API GitHub atteinte — réessayez plus tard.",
    "note.no_winget_manifest": "Aucun manifeste winget n'existe pour ce paquet.",
    "note.winget_list_error": "Erreur de listage des manifestes winget (HTTP {code}).",
    "note.no_winget_versions": "Le manifeste winget ne contient aucune version publiée.",
    "note.winget_installer_missing": "Le manifeste d'installateur winget n'a pas été trouvé.",
    "note.winget_installer_error": "Erreur du manifeste d'installateur winget (HTTP {code}).",
    "note.winget_no_arch": (
        "Aucun installateur {arch} n'est publié dans le dernier manifeste "
        "officiel."),
    "note.repo_not_found": "Dépôt ou dernière version introuvable.",
    "note.github_error": "Erreur de l'API GitHub (HTTP {code}).",
    "note.auto_match_unrelated": (
        "Le dépôt apparié automatiquement semble sans rapport (projet plus "
        "ancien au nom similaire)."),
    "note.matched_by_name": (
        "Apparié par le nom — vérifiez l'éditeur avant d'installer."),
    "note.github_no_arch": (
        "Aucun installateur Windows pour cette architecture dans la "
        "dernière version."),
    "note.feed_error": "Erreur du flux de versions (HTTP {code}).",
    "note.feed_parse": "Impossible d'analyser le flux de versions.",
    "note.vendor_arch_installer_missing": "L'éditeur ne publie pas d'installateur pour cette architecture.",
    "note.no_installer_url": "Aucune URL d'installateur publiée pour cette architecture.",
    "note.vendor_page_error": "Erreur de la page de l'éditeur (HTTP {code}).",
    "note.vendor_no_arch": (
        "Version trouvée, mais aucun installateur pour cette architecture "
        "sur la page de l'éditeur."),
    "note.vendor_latest_unknown": (
        "Impossible de trouver la dernière version sur la page de "
        "l'éditeur."),
    "note.mozilla_feed_error": "Erreur du flux de versions Mozilla (HTTP {code}).",
    "note.mozilla_parse": "Impossible d'analyser le flux de versions Mozilla.",
    "note.vlc_server_error": "Erreur du serveur VideoLAN (HTTP {code}).",
    "note.vlc_no_installer": "Aucun installateur trouvé sur le miroir VideoLAN.",
    "note.edge_feed_error": "Erreur du flux de mises à jour de Microsoft Edge (HTTP {code}).",
    "note.edge_no_stable": "Aucune version stable trouvée pour cette architecture.",
    "note.discord_no_version": (
        "Dernier installateur stable (version non exposée par Discord)."),
    "note.dl_server_error": "Erreur du serveur de téléchargement (HTTP {code}).",
    "note.dl_list_error": "Impossible de lister les dossiers de versions.",
    "note.blender_64bit_only": "Blender ne publie que des installateurs 64 bits.",
    "note.no_windows_installer_folder": (
        "Aucun installateur Windows dans le dossier de la dernière "
        "version."),

    # ---------------------------------------------- downloader errors
    "dlerr.http": "Le serveur a renvoyé HTTP {code}.",
    "dlerr.cancelled": "Téléchargement annulé.",
    "dlerr.no_url": "Aucune URL de téléchargement fournie.",
    "dlerr.give_up": (
        "Le téléchargement n'a pas pu aboutir ({err}) après plusieurs "
        "tentatives — rien n'a été enregistré. Vérifiez la connexion et "
        "réessayez, ou utilisez « Ouvrir la page officielle » pour le "
        "télécharger vous-même."),
    "dlerr.sha_mismatch": (
        "Somme de contrôle SHA-256 incorrecte — le fichier téléchargé ne "
        "correspondait pas à la somme de contrôle officielle et a été "
        "supprimé."),
    "dlerr.not_installer": (
        "Le téléchargement n'est pas arrivé sous forme d'installateur "
        "valide (une page d'erreur ou de blocage est arrivée à la place) "
        "— il a été supprimé. Réessayez, ou utilisez « Ouvrir la page "
        "officielle » pour le télécharger vous-même."),
    "dlerr.final_validation": (
        "L'installateur enregistré a échoué à sa validation finale et a "
        "été supprimé — veuillez relancer le téléchargement."),
    "dlerr.all_locations": (
        "Le téléchargement a échoué sur les {n} emplacements officiels "
        "(dernière erreur : {err}). Rien n'a été enregistré — vérifiez la "
        "connexion et réessayez, ou utilisez « Ouvrir la page officielle » "
        "pour le télécharger vous-même."),
    "dlerr.failed_one": (
        "Le téléchargement n'a pas pu aboutir ({err}) — rien n'a été "
        "enregistré. Vérifiez la connexion et réessayez, ou utilisez "
        "« Ouvrir la page officielle » pour le télécharger vous-même."),

    # ------------------------------------------- catalog variant notes
    "vn.calibre": (
        "Si aucun installateur n'est joint, téléchargez-le depuis "
        "calibre-ebook.com."),
    "vn.telegram": "Versions officielles de Telegram Desktop (tdesktop).",
    "vn.vscode": "Service de mise à jour officiel de VS Code.",
    "vn.winterminal": "Ouvrez le .msixbundle avec App Installer.",
    "vn.ffmpeg": "Binaires compilés automatiquement par BtbN (builds de référence de la communauté).",
    "vn.inkscape": (
        "Dépôt miroir officiel ; si aucun installateur n'est publié, "
        "téléchargez-le depuis inkscape.org."),
    "vn.winrar_x86": "WinRAR 7 est publié uniquement pour Windows 64 bits.",
    "vn.winrar": "Page officielle des versions de WinRAR (rarlab.com).",
    "vn.nekobox": "Version officielle de NekoBox for PC (nekoray).",
    "vn.qtum": "Qtum publie des binaires d'installation Windows non signés.",

    # --------------------------------------------- blocked-app reasons
    "blk.steam": "Steam se met à jour via son propre client.",
    "blk.epic": "Epic Games Launcher se met à jour tout seul.",
    "blk.battlenet": "Battle.net se met à jour tout seul.",
    "blk.gog": "GOG Galaxy se met à jour tout seul.",
    "blk.ubisoft": "Ubisoft Connect se met à jour tout seul.",
    "blk.ea_app": "L'application EA se met à jour toute seule.",
    "blk.origin": "EA/Origin se met à jour tout seul.",
    "blk.office": "Office est mis à jour via Microsoft Click-to-Run.",
    "blk.m365": "Microsoft 365 se met à jour automatiquement.",
    "blk.onedrive": "OneDrive se met à jour automatiquement via Microsoft Update.",
    "blk.dropbox": "Dropbox se met à jour silencieusement.",
    "blk.gdrive": "Google Drive se met à jour tout seul.",
    "blk.spotify": "Spotify se met à jour silencieusement.",
    "blk.whatsapp": "WhatsApp est mis à jour via le Microsoft Store.",
    "blk.teams": "Teams se met à jour automatiquement.",
    "blk.slack": "Slack se met à jour automatiquement.",
    "blk.zoom": "Zoom se met à jour automatiquement.",
    "blk.teamviewer": "TeamViewer se met à jour automatiquement.",
    "blk.anydesk": "AnyDesk se met à jour automatiquement.",
    "blk.opera": "Opera est mis à jour via son propre programme de mise à jour.",
    "blk.vivaldi": "Vivaldi est mis à jour via son propre programme de mise à jour.",
    "blk.adobe": "Les applications Adobe sont mises à jour via Creative Cloud / le programme de mise à jour d'Acrobat.",
    "blk.nvidia": "Les pilotes GPU sont mis à jour via GeForce Experience / NVIDIA App.",
    "blk.amd": "Les pilotes AMD sont mis à jour via AMD Software.",
    "blk.malwarebytes": "Malwarebytes se met à jour automatiquement.",
    "blk.kaspersky": "L'antivirus se met à jour automatiquement.",
    "blk.avast": "Avast se met à jour automatiquement.",
    "blk.avg": "AVG se met à jour automatiquement.",
    "blk.bitdefender": "Bitdefender se met à jour automatiquement.",
    "blk.webview2": "Le Runtime WebView2 est mis à jour via Microsoft Update.",
    "blk.termius": "Termius se met à jour automatiquement.",
    "blk.afterburner": "MSI Afterburner est mis à jour via son propre programme / msi.com.",
    "blk.rivatuner": "RivaTuner est livré avec MSI Afterburner ; mettez-le à jour depuis msi.com.",
    "blk.potplayer": "PotPlayer se met à jour tout seul ; installateurs sur potplayer.daum.net.",
    "blk.windscribe": "Windscribe se met à jour automatiquement.",
    "blk.fdm": "FDM se met à jour tout seul ; installateurs sur freedownloadmanager.com.",
    "blk.capcut": "CapCut se met à jour automatiquement.",
    "blk.canva": "Canva se met à jour automatiquement.",
    "blk.bluestacks": "BlueStacks se met à jour automatiquement.",
    "blk.ldplayer": "LDPlayer se met à jour automatiquement.",
    "blk.driver_booster": "Driver Booster est mis à jour via le programme de mise à jour propre à IObit.",
    "blk.iobit": "Les applications IObit sont mises à jour via leur propre programme de mise à jour.",
    "blk.allavsoft": "Allavsoft n'a pas de flux de versions public ; consultez allavsoft.com.",
    "blk.zdsoft": "Consultez zdsoft.com pour la dernière version de ZD Soft Screen Recorder.",
    "blk.officesuite": "OfficeSuite se met à jour tout seul.",
    "blk.maxon": "Les applications Maxon sont mises à jour via Maxon App.",
    "blk.icue": "Corsair iCUE se met à jour tout seul.",
    "blk.miniconda": "Mettez à jour via « conda update » ou un nouvel installateur depuis anaconda.com.",
    "blk.python_launcher": "Installé avec Python ; se met à jour avec Python.",
    "blk.android_studio": "Android Studio se met à jour via son propre programme de mise à jour.",
    "blk.java": "Java se met à jour via Java Auto Update d'Oracle ; JDK depuis oracle.com/java.",
    "blk.intel": "Les pilotes/composants Intel sont mis à jour via Intel Driver & Support Assistant.",
    "blk.realtek": "Les pilotes Realtek sont fournis par le fabricant de votre PC ou de votre carte mère.",
    "blk.rapoo": "Les pilotes de périphériques proviennent de rapoo.com.",
    "blk.asus": "Les utilitaires ASUS sont mis à jour via Armoury Crate / MyASUS.",
    "blk.rog": "Les utilitaires ASUS ROG sont mis à jour via Armoury Crate / MyASUS.",
    "blk.armoury": "Les composants d'ASUS Armoury Crate sont mis à jour ensemble.",
    "blk.aura": "Les composants ASUS AURA sont mis à jour via Armoury Crate.",
    "blk.tap_windows": "La carte TAP est installée avec OpenVPN ; mettez OpenVPN à jour.",
    "blk.openvpn": "OpenVPN se met à jour via openvpn.net ; OpenVPN Connect se met à jour tout seul.",
    "blk.maintenance_service": "Installé avec Firefox ; se met à jour en même temps que Firefox.",
    "blk.vcredist": "Les redistribuables VC++ sont installés par les installateurs d'applications ; dernière version sur aka.ms/vsredist.",
    "blk.dotnet": "Les composants .NET sont installés par les installateurs d'applications ou par Visual Studio.",
    "blk.ms_windows": "Composant système de Windows — mis à jour via Windows Update.",
    "blk.winsdk": "Le SDK Windows se met à jour avec Visual Studio.",
    "blk.xna": "Composant Microsoft XNA hérité ; n'est plus mis à jour.",
    "blk.vb": "Runtime VB hérité ; installé par les installateurs d'applications.",
    "blk.update_health": "Composant système mis à jour via Windows Update.",
    "blk.visio": "Visio est mis à jour avec Microsoft Office (Click-to-Run).",
    "blk.project": "Project est mis à jour avec Microsoft Office (Click-to-Run).",
    "blk.powerpoint": "PowerPoint est mis à jour avec Microsoft Office.",
    "blk.word": "Word est mis à jour avec Microsoft Office.",
    "blk.excel": "Excel est mis à jour avec Microsoft Office.",
    "blk.outlook": "Outlook est mis à jour avec Microsoft Office.",
    "blk.access": "Access est mis à jour avec Microsoft Office.",
    "blk.onenote": "OneNote est mis à jour avec Microsoft Office.",
    "blk.publisher": "Publisher est mis à jour avec Microsoft Office.",
    "blk.visual_studio": "Les composants de Visual Studio sont mis à jour via Visual Studio Installer.",

    # ------------------------------------------------------ settings
    "set.title": "Paramètres",
    "set.nav.checking": "Vérification",
    "set.nav.downloads": "Téléchargements",
    "set.nav.apps": "Applications",
    "set.nav.backup": "Sauvegarde",
    "set.nav.appearance": "Apparence",
    "set.header.checking": "Vérification",
    "set.header.downloads": "Téléchargements",
    "set.header.apps": "Applications",
    "set.header.backup": "Sauvegarde et maintenance",
    "set.header.appearance": "Apparence",
    "set.nav.about": "À propos",
    "set.header.about": "À propos de SoftUpdater",
    "set.about.tagline": "Vérifiez vos applications installées auprès de leurs sources officielles - gratuit et open source.",
    "set.about.version": "Version",
    "set.about.dev": "Développeur",
    "set.about.source": "Code source officiel sur GitHub",
    "set.about.license": "Publié sous licence MIT - libre d'utiliser, d'étudier, de modifier et de partager.",
    "set.about.official": "Téléchargez toujours SoftUpdater uniquement depuis son dépôt officiel :",
    "set.chk_auto": "Rechercher des mises à jour au démarrage de l'application",
    "tip.set.chk_auto": (
        "Lance tout seul une vérification complète des mises à jour juste "
        "après l'ouverture de l'application, pour que vous voyiez la "
        "liste des mises à jour sans rien cliquer."),
    "set.lbl_interval": "Revérifier automatiquement toutes les",
    "set.cmb_never": "Jamais",
    "set.cmb_hours": "{n} heure(s)",
    "tip.set.interval": (
        "Lance tout seul une vérification complète tant que l'application "
        "est ouverte, même si vous ne l'avez pas touchée. Les mises à jour "
        "trouvées déclenchent une notification."),
    "set.chk_notify": "Afficher une notification lorsque des mises à jour sont trouvées",
    "tip.set.notify": (
        "Notification toast Windows au sujet des nouvelles mises à jour "
        "après une vérification automatique (au démarrage ou planifiée). "
        "Les vérifications manuelles ne vous interrompent jamais."),
    "set.hint.checking": (
        "Les vérifications automatiques couvrent chaque application auprès "
        "de sa source officielle (les résultats sont mis en cache, les "
        "répétitions sont donc rapides)."),
    "set.lbl_save_to": "Enregistrer les installateurs dans",
    "set.btn.browse": "Parcourir...",
    "set.btn.reset_dir": "Utiliser le dossier par défaut",
    "tip.set.reset_dir": "Revient à Downloads\\SoftUpdater",
    "set.dl_default": "Downloads\\SoftUpdater (par défaut)",
    "set.hint.downloads": (
        "Choisissez où les installateurs téléchargés sont enregistrés. Par "
        "défaut, il s'agit du dossier SoftUpdater dans vos Downloads."),
    "set.btn.restore_hidden": "Restaurer les applications masquées",
    "tip.set.restore_hidden": (
        "Remet chaque application que vous avez masquée via le menu "
        "contextuel et réanalyse la liste."),
    "set.lbl_hidden_n": "{n} application(s) masquée(s) de la liste",
    "set.lbl_hidden_none": "Rien n'est masqué",
    "set.btn.restore_skip": "Restaurer les versions ignorées",
    "tip.set.restore_skip": (
        "Permet aux versions ignorées de réapparaître comme mises à jour "
        "(elles avaient été masquées avec l'action « Ignorer cette "
        "version » du clic droit)."),
    "set.lbl_skip_n": "{n} version(s) ignorée(s)",
    "set.lbl_skip_none": "Aucune version ignorée",
    "set.hint.apps": (
        "Masquez une application en cliquant droit sur sa ligne dans la "
        "fenêtre principale (utile pour les outils que vous mettez à jour "
        "manuellement). Une version précise peut être ignorée de la même "
        "façon."),
    "set.btn.export": "Exporter la liste des applications...",
    "tip.set.export": (
        "Enregistre chaque application listée avec ses versions dans un "
        "fichier JSON — une petite sauvegarde de ce que ce PC avait "
        "installé."),
    "set.btn.import": "Importer la liste des applications...",
    "tip.set.import": (
        "Compare une liste précédemment exportée avec ce qui est installé "
        "sur ce PC et signale ce qui manque ou a besoin d'une mise à "
        "jour."),
    "set.btn.log": "Ouvrir le dossier des journaux",
    "tip.set.log": (
        "L'application écrit un petit journal des vérifications, "
        "téléchargements et erreurs — pratique quand quelque chose doit "
        "être signalé."),
    "set.hint.backup": (
        "Le fichier d'export est une simple liste JSON — rien n'est envoyé "
        "nulle part."),
    "set.lbl_font": "Taille de police",
    "set.pt_suffix": " pt",
    "set.btn.reset_font": "Réinitialiser la police",
    "tip.set.reset_font": "Remet la taille de police à {default} pt",
    "set.hint.appearance": (
        "Choisissez une taille - l'exemple ci-dessous l'affiche. Toute "
        "l'application change lorsque vous cliquez sur « Terminé », et le "
        "réglage est conservé pour la prochaine fois."),
    "set.lbl_preview": "Aperçu",
    "set.font.sample": (
        "Voici un exemple de texte pour prévisualiser la taille de la "
        "police - Aa 123"),
    "set.btn.done": "Terminé",
    "set.lbl_language": "Langue",
    "set.hint.language": (
        "Appliqué instantanément — toutes les fenêtres basculent sans "
        "redémarrage."),
    "set.btn.tour": "Revoir la visite rapide",
    "tip.set.tour": (
        "Rejoue les astuces du premier lancement (votre choix « ne plus "
        "afficher » est conservé)."),

    # ----------------------------------------------------- onboarding
    "ob.title": "Visite rapide de SoftUpdater",
    "ob.page_of": "Page {n} sur {total}",
    "ob.btn.next": "Suivant",
    "ob.btn.back": "Précédent",
    "ob.btn.skip": "Ignorer la visite",
    "ob.btn.finish": "Commencer",
    "ob.chk.never": "Ne plus afficher ces astuces",
    "ob.welcome.title": "Bienvenue dans SoftUpdater",
    "ob.welcome.body": (
        "SoftUpdater vérifie vos applications installées auprès de leurs "
        "sources officielles et télécharge les derniers installateurs "
        "pour vous — en toute sécurité, avec vérification SHA-256.\n\n"
        "Commencez par le grand bouton vert : Rechercher des mises à "
        "jour."),
    "ob.ctx.title": "Cliquez droit sur n'importe quelle ligne",
    "ob.ctx.body": (
        "Le menu contextuel de chaque ligne d'application regroupe les "
        "fonctions avancées :\n"
        "- Voir les détails (versions, source, lien de l'installateur)\n"
        "- Revérifier uniquement cette application\n"
        "- Télécharger son installateur / ouvrir la page officielle\n"
        "- Ignorer une version précise, ou masquer les applications que "
        "vous mettez à jour vous-même"),
    "ob.dl.title": "Des téléchargements qui vont au bout",
    "ob.dl.body": (
        "Les installateurs sont enregistrés dans Downloads\\SoftUpdater. "
        "Ils peuvent s'ouvrir automatiquement après le téléchargement "
        "— et une fois une mise à jour installée, la ligne passe toute "
        "seule à « À jour »."),
    "ob.done.title": "Personnalisez-le",
    "ob.done.body": (
        "Les Paramètres rassemblent tout : cette application parle "
        "anglais, persan, arabe, portugais, français et allemand (écriture "
        "de droite à gauche incluse), la taille de police s'adapte à vos "
        "yeux et les vérifications automatiques suivent votre planning. "
        "SoftUpdater vit aussi dans la zone de notification."),
}
