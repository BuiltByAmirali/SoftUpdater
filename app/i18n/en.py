"""English strings - the MASTER key set of SoftUpdater.

app/i18n/{fa,ar,pt,fr,de}.py must define EXACTLY the same keys (the
self-test verifies key parity and {placeholder} parity). Brand names
(SoftUpdater, SHA-256, winget, GitHub, JSON) and paths stay as-is.
"""
from __future__ import annotations

MESSAGES = {
    # ------------------------------------------------------------- meta
    "app.name": "SoftUpdater",
    "win.title": "SoftUpdater - Update Checker",
    "bits.64": "64-bit",
    "bits.32": "32-bit",
    "win.summary_build": "{name} - {bits} - Build {build}",
    "win.summary_plain": "{name} - {bits}",
    "win.summary_dev": "{name} - {bits} - (dev preview)",
    "win.nonwin": "Non-Windows OS",
    "win.unknown": "Windows (unknown)",

    # ---------------------------------------------------------- toolbar
    "search.placeholder": "Search installed apps...",
    "btn.refresh": "Refresh apps",
    "btn.open_dir": "Open download folder",
    "btn.settings": "Settings",
    "btn.check_all": "Check for updates",
    "btn.check_sel": "Check selected",
    "btn.download": "Download selected installers",
    "chk.open": "Open installers after download",
    "btn.pause": "Pause",
    "btn.resume": "Resume",
    "btn.cancel": "Cancel",
    "tip.refresh": "Re-scan the list of installed applications",
    "tip.settings": "Change the language, font size and other preferences",
    "tip.check_all": "Check every installed app against its official source",
    "tip.check_sel": (
        "Re-scans the selected app(s) from the registry first (picking up "
        "versions changed by a fresh install), then checks them against "
        "their official sources. You can also right-click a row and "
        "choose 'Re-check this app'."),
    "tip.download": (
        "Files are saved to your Downloads folder. If the checkbox on the "
        "right is enabled, each installer opens automatically when its "
        "download finishes so you can run the update right away."),
    "tip.open": (
        "When checked, the installer window opens by itself as soon as a "
        "download finishes - you just follow its steps to update the app. "
        "The installers are still saved in the Downloads folder. After "
        "you finish installing, the app is re-checked automatically."),
    "tip.pause": (
        "Pause the current download. Resuming continues where it stopped "
        "- already downloaded data is not lost."),
    "tip.cancel": "Cancel the current download",

    # ----------------------------------------------------------- table
    "col.app": "Application",
    "col.pub": "Publisher",
    "col.installed": "Installed",
    "col.latest": "Latest",
    "col.status": "Status",
    "col.source": "Source",

    # ---------------------------------------------------------- status
    "status.update": "Update available",
    "status.latest": "Up to date",
    "status.no_installer": "No installer for this OS",
    "status.vendor": "Managed by vendor",
    "status.no_source": "No source found",
    "status.failed": "Check failed",
    "status.pending": "Not checked",
    "status.skipped": "Version skipped",
    "status.checking": "Checking...",

    # -------------------------------------------------- status messages
    "msg.counts": "{total} apps - {checked} checked - {updates} updates",
    "msg.postinstall_updated": "{name} updated to {version} - now up to date ✓",
    "msg.postinstall_uptodate": "{name} is now up to date ✓",
    "msg.ready": "Ready.",
    "msg.found_apps": "Found {n} installed applications.",
    "msg.checking_n": "Checking {n} app(s) against official sources...",
    "msg.select_first": "Select one or more rows first.",
    "msg.done": "Done - {n} update(s) available",
    "msg.done_failed_tail": " - {n} check(s) failed",
    "msg.no_jobs": (
        "No selected row has a downloadable installer. Run a check first."),
    "msg.preparing_n": "Preparing {n} download(s)...",
    "msg.preparing_one": "Preparing download...",
    "msg.downloading_n": "Downloading {n} installer(s)...",
    "msg.of_total": "of {total}",
    "msg.paused_row": "Paused: {name}",
    "msg.dl_title_paused": "{name} - paused",
    "msg.saved": "Saved: {path}",
    "msg.saved_verified": "Saved: {path} - SHA-256 verified",
    "msg.after_install_open": (
        "The installer was opened. After you finish installing, this row "
        "is re-checked automatically and turns 'Up to date'."),
    "msg.after_install": (
        "After you install it, this row is re-checked automatically and "
        "turns 'Up to date'."),
    "msg.dl_failed": "Download failed for {name}: {info}",
    "msg.dl_finished": "Downloads finished - {ok} succeeded",
    "msg.dl_finished_failed_tail": ", {n} failed",
    "msg.dl_finished_files_tail": " Files are in: {path}",
    "msg.dl_finished_none_tail": (
        " Nothing was saved - the official servers could not deliver a "
        "valid installer (see Open log folder in Settings for details). "
        "You can right-click the row and use Open official page instead."),
    "msg.cancelling": "Cancelling download...",
    "msg.could_not_open": "Could not open installer: {err} - file is at: {path}",
    "msgbox.open_fail_text": (
        "The installer was saved but Windows could not open it\n"
        "({err}).\n\nIts folder was opened for you - double-click\n"
        "the file there:\n{path}"),
    "msg.updated_rechecking": (
        "{name} was updated to {version} - re-checking it automatically..."),
    "msg.auto_interval_on": "Automatic re-check every {hours} hour(s) is on.",
    "msg.hidden_restored": "Hidden apps restored - the list was re-scanned.",
    "msg.skipped_restored": (
        "Skipped versions restored - {n} update(s) shown again."),
    "msg.hidden_one": "Hidden {name}. Restore it in Settings.",
    "msg.skip_done": (
        "Version {version} of {name} is skipped. Newer versions still "
        "show up."),
    "msg.unskip_done": (
        "Version {version} of {name} shows as an update again."),
    "msg.exported": "Exported {n} app(s) to {file}",
    "msg.error": "Error: {err}",
    "msgbox.error_text": "Something went wrong:\n{err}",

    # ------------------------------------------------------ skip notes
    "note.skipped": (
        "You skipped version {version}. Restore skipped versions in "
        "Settings."),
    "msg.last_known_tail": "showing the last known result.",

    # ---------------------------------------------------- context menu
    "menu.details": "View details",
    "tip.menu.details": (
        "Versions, source, the direct installer link (copyable) and the "
        "checker's explanation for this app."),
    "menu.recheck": "Re-check this app",
    "tip.menu.recheck": (
        "Scans the registry for this app's CURRENT installed version "
        "(e.g. right after you installed a downloaded update) and checks "
        "it against its official source - only this app, not the list."),
    "menu.download": "Download installer",
    "menu.src": "Open official page",
    "menu.skip": "Skip this version ({version})",
    "menu.unskip": "Un-skip version ({version})",
    "tip.menu.skip": (
        "Stops THIS version from showing as an update (a newer one will "
        "still be offered). Restore in Settings."),
    "tip.menu.unskip": "Shows this version as an update again.",
    "menu.hide": "Hide this app",
    "tip.menu.hide": (
        "Removes it from the list (for tools you update manually). You "
        "can restore hidden apps in Settings."),

    # -------------------------------------------------- details dialog
    "det.title": "Details - {name}",
    "det.publisher": "Publisher",
    "det.installed_version": "Installed version",
    "det.latest_version": "Latest version",
    "det.status": "Status",
    "det.source": "Source",
    "det.size": "Download size",
    "det.arch": "Architecture",
    "det.sha": "SHA-256",
    "det.sha_ok": "published by the source (verified after download)",
    "det.sha_none": "not published by the source",
    "det.placeholder": "Run a check to resolve the installer link",
    "btn.copy": "Copy link",
    "btn.open_page": "Open official page",
    "btn.close": "Close",

    # ------------------------------------------------------- tray/toast
    "tray.open": "Open SoftUpdater",
    "tray.check": "Check for updates now",
    "tray.quit": "Quit",
    "tray.tip_updates": "SoftUpdater - {n} update(s) available",
    "tray.tip_ok": "SoftUpdater - everything up to date",
    "toast.updates_body": (
        "{n} update(s) available - open SoftUpdater to download them."),
    "toast.installed_title": "Update installed",
    "toast.installed_body": "{name} is now up to date{tail}",
    "toast.installed_tail": " (version {version})",

    # ---------------------------------------------------- export/import
    "fd.export_title": "Export app list",
    "fd.import_title": "Import app list",
    "fd.choose_dir": "Choose download folder",
    "msgbox.import_none_title": "Import app list",
    "msgbox.import_none_text": (
        "This file does not contain a SoftUpdater app list (export one "
        "first with 'Export app list')."),
    "rep.header": "The imported list has {n} app(s).",
    "rep.block": "{title} ({n}):",
    "rep.more": "...and {n} more",
    "rep.row_update": "{name} (here: {here}, export had: {export})",
    "rep.missing": "Missing on this PC",
    "rep.need_update": "Update still available",
    "rep.up_to_date": "Already up to date here",
    "rep.plain": "Present (no version info in the export)",
    "rep.nothing": "Nothing to report - the list looks empty.",

    # ------------------------------------------------- source labels
    "src.vendor": "Vendor-managed",
    "src.winget": "Winget official manifest",
    "src.github": "GitHub - {repo}",
    "src.github_auto": "GitHub (auto-matched) - {repo}",
    "src.feed": "Official version feed",
    "src.website": "Official website",
    "src.mozilla": "Mozilla official download",
    "src.vlc": "VideoLAN official mirror",
    "src.edge": "Microsoft Edge official updates",
    "src.discord": "Discord official download",
    "src.dl_server": "Official download server",

    # -------------------------------------------------- checker notes
    "note.check_error": "Check error: {cls}",
    "note.init_error": "Init error: {cls}",
    "note.unexpected_error": "Unexpected error: {cls}",
    "note.no_source": (
        "No official source found for this app. It may be closed-source "
        "or too niche."),
    "note.latest": "Already on the latest version.",
    "note.newer_than_latest": (
        "Installed version is newer than the latest public release."),
    "note.version_unknown": "Installed version unknown - verify manually.",
    "note.rate_limited": "GitHub API rate limit reached - try again later.",
    "note.no_winget_manifest": "No winget manifest exists for this package.",
    "note.winget_list_error": "winget manifest listing error (HTTP {code}).",
    "note.no_winget_versions": "The winget manifest has no published versions.",
    "note.winget_installer_missing": "The winget installer manifest was not found.",
    "note.winget_installer_error": "winget installer manifest error (HTTP {code}).",
    "note.winget_no_arch": (
        "No {arch} installer is published in the latest official manifest."),
    "note.repo_not_found": "Repository or latest release not found.",
    "note.github_error": "GitHub API error (HTTP {code}).",
    "note.auto_match_unrelated": (
        "Auto-matched repository looks unrelated (older project with a "
        "similar name)."),
    "note.matched_by_name": (
        "Matched by name - verify the publisher before installing."),
    "note.github_no_arch": (
        "No Windows installer for this architecture in the latest release."),
    "note.feed_error": "Version feed error (HTTP {code}).",
    "note.feed_parse": "Could not parse the version feed.",
    "note.vendor_arch_installer_missing": "The vendor does not publish an installer for this architecture.",
    "note.no_installer_url": "No installer URL published for this architecture.",
    "note.vendor_page_error": "Vendor page error (HTTP {code}).",
    "note.vendor_no_arch": (
        "Version found but no installer for this architecture on the "
        "vendor page."),
    "note.vendor_latest_unknown": (
        "Could not find the latest version on the vendor page."),
    "note.mozilla_feed_error": "Mozilla version feed error (HTTP {code}).",
    "note.mozilla_parse": "Could not parse the Mozilla version feed.",
    "note.vlc_server_error": "VideoLAN server error (HTTP {code}).",
    "note.vlc_no_installer": "No installer found on the VideoLAN mirror.",
    "note.edge_feed_error": "Microsoft Edge update feed error (HTTP {code}).",
    "note.edge_no_stable": "No stable release found for this architecture.",
    "note.discord_no_version": (
        "Latest stable installer (version not exposed by Discord)."),
    "note.dl_server_error": "Download server error (HTTP {code}).",
    "note.dl_list_error": "Could not list release folders.",
    "note.blender_64bit_only": "Blender publishes 64-bit installers only.",
    "note.no_windows_installer_folder": (
        "No Windows installer in the latest release folder."),

    # ---------------------------------------------- downloader errors
    "dlerr.http": "Server returned HTTP {code}.",
    "dlerr.cancelled": "Download cancelled.",
    "dlerr.no_url": "No download URL provided.",
    "dlerr.give_up": (
        "The download could not be completed ({err}) after several tries "
        "- nothing was saved. Check the connection and try again, or use "
        "Open official page to download it yourself."),
    "dlerr.sha_mismatch": (
        "SHA-256 checksum mismatch - the downloaded file did not match "
        "the official checksum and was deleted."),
    "dlerr.not_installer": (
        "The download did not arrive as a valid installer (an error or "
        "block page came instead) - it was deleted. Try again, or use "
        "Open official page to download it yourself."),
    "dlerr.final_validation": (
        "The saved installer failed its final validation and was deleted "
        "- please try the download again."),
    "dlerr.all_locations": (
        "The download failed on all {n} official locations (last error: "
        "{err}). Nothing was saved - check the connection and try again, "
        "or use Open official page to download it yourself."),
    "dlerr.failed_one": (
        "The download could not be completed ({err}) - nothing was "
        "saved. Check the connection and try again, or use Open official "
        "page to download it yourself."),

    # ------------------------------------------- catalog variant notes
    "vn.calibre": (
        "If no installer asset is attached, download from calibre-ebook.com."),
    "vn.telegram": "Official Telegram Desktop releases (tdesktop).",
    "vn.vscode": "Official VS Code update service.",
    "vn.winterminal": "Open the .msixbundle with the App Installer.",
    "vn.ffmpeg": "Auto-built binaries by BtbN (community standard builds).",
    "vn.inkscape": (
        "Official mirror repo; if no installer asset is published, "
        "download from inkscape.org."),
    "vn.winrar_x86": "WinRAR 7 is published for 64-bit Windows only.",
    "vn.winrar": "Official WinRAR release page (rarlab.com).",
    "vn.nekobox": "Official NekoBox for PC (nekoray) release.",
    "vn.qtum": "Qtum publishes unsigned Windows setup binaries.",

    # --------------------------------------------- blocked-app reasons
    "blk.steam": "Steam updates itself through its own client.",
    "blk.epic": "Epic Games Launcher updates itself.",
    "blk.battlenet": "Battle.net updates itself.",
    "blk.gog": "GOG Galaxy updates itself.",
    "blk.ubisoft": "Ubisoft Connect updates itself.",
    "blk.ea_app": "EA app updates itself.",
    "blk.origin": "EA/Origin updates itself.",
    "blk.office": "Office updates through Microsoft Click-to-Run.",
    "blk.m365": "Microsoft 365 updates automatically.",
    "blk.onedrive": "OneDrive updates automatically via Microsoft Update.",
    "blk.dropbox": "Dropbox updates itself silently.",
    "blk.gdrive": "Google Drive updates itself.",
    "blk.spotify": "Spotify updates itself silently.",
    "blk.whatsapp": "WhatsApp updates through the Microsoft Store.",
    "blk.teams": "Teams updates itself automatically.",
    "blk.slack": "Slack updates itself automatically.",
    "blk.zoom": "Zoom updates itself automatically.",
    "blk.teamviewer": "TeamViewer updates itself automatically.",
    "blk.anydesk": "AnyDesk updates itself automatically.",
    "blk.opera": "Opera updates through its own updater.",
    "blk.vivaldi": "Vivaldi updates through its own updater.",
    "blk.adobe": "Adobe apps update through Creative Cloud / Acrobat updater.",
    "blk.nvidia": "GPU drivers update through GeForce Experience / NVIDIA App.",
    "blk.amd": "AMD drivers update through AMD Software.",
    "blk.malwarebytes": "Malwarebytes updates itself automatically.",
    "blk.kaspersky": "Antivirus updates itself automatically.",
    "blk.avast": "Avast updates itself automatically.",
    "blk.avg": "AVG updates itself automatically.",
    "blk.bitdefender": "Bitdefender updates itself automatically.",
    "blk.webview2": "WebView2 Runtime updates via Microsoft Update.",
    "blk.termius": "Termius updates itself automatically.",
    "blk.afterburner": "MSI Afterburner updates via its own updater / msi.com.",
    "blk.rivatuner": "RivaTuner ships with MSI Afterburner; update from msi.com.",
    "blk.potplayer": "PotPlayer updates itself; installers at potplayer.daum.net.",
    "blk.windscribe": "Windscribe updates itself automatically.",
    "blk.fdm": "FDM updates itself; installers at freedownloadmanager.com.",
    "blk.capcut": "CapCut updates itself automatically.",
    "blk.canva": "Canva updates itself automatically.",
    "blk.bluestacks": "BlueStacks updates itself automatically.",
    "blk.ldplayer": "LDPlayer updates itself automatically.",
    "blk.driver_booster": "Driver Booster updates through IObit's own updater.",
    "blk.iobit": "IObit apps update through their own updater.",
    "blk.allavsoft": "Allavsoft has no public version feed; check allavsoft.com.",
    "blk.zdsoft": "Check zdsoft.com for the latest ZD Soft Screen Recorder.",
    "blk.officesuite": "OfficeSuite updates itself.",
    "blk.maxon": "Maxon apps update through the Maxon App.",
    "blk.icue": "Corsair iCUE updates itself.",
    "blk.miniconda": "Update via 'conda update' or a new installer from anaconda.com.",
    "blk.python_launcher": "Installed together with Python; updates with Python.",
    "blk.android_studio": "Android Studio updates through its own updater.",
    "blk.java": "Java updates via Oracle's Java Auto Update; JDKs from oracle.com/java.",
    "blk.intel": "Intel drivers/components update via Intel Driver & Support Assistant.",
    "blk.realtek": "Realtek drivers are delivered by your PC or motherboard vendor.",
    "blk.rapoo": "Peripheral drivers come from rapoo.com.",
    "blk.asus": "ASUS utilities update via Armoury Crate / MyASUS.",
    "blk.rog": "ASUS ROG utilities update via Armoury Crate / MyASUS.",
    "blk.armoury": "ASUS Armoury Crate components update together.",
    "blk.aura": "ASUS AURA components update via Armoury Crate.",
    "blk.tap_windows": "The TAP adapter is installed with OpenVPN; update OpenVPN.",
    "blk.openvpn": "OpenVPN updates via openvpn.net; OpenVPN Connect updates itself.",
    "blk.maintenance_service": "Installed with Firefox; updates together with Firefox.",
    "blk.vcredist": "VC++ Redistributables are installed by app installers; latest at aka.ms/vsredist.",
    "blk.dotnet": ".NET components are installed by app installers or Visual Studio.",
    "blk.ms_windows": "Windows system component - updated via Windows Update.",
    "blk.winsdk": "The Windows SDK updates with Visual Studio.",
    "blk.xna": "Legacy Microsoft XNA component; no longer updated.",
    "blk.vb": "Legacy VB runtime; installed by app installers.",
    "blk.update_health": "System component updated via Windows Update.",
    "blk.visio": "Visio updates with Microsoft Office (Click-to-Run).",
    "blk.project": "Project updates with Microsoft Office (Click-to-Run).",
    "blk.powerpoint": "PowerPoint updates with Microsoft Office.",
    "blk.word": "Word updates with Microsoft Office.",
    "blk.excel": "Excel updates with Microsoft Office.",
    "blk.outlook": "Outlook updates with Microsoft Office.",
    "blk.access": "Access updates with Microsoft Office.",
    "blk.onenote": "OneNote updates with Microsoft Office.",
    "blk.publisher": "Publisher updates with Microsoft Office.",
    "blk.visual_studio": "Visual Studio components update via the Visual Studio Installer.",

    # ------------------------------------------------------ settings
    "set.title": "Settings",
    "set.nav.checking": "Checking",
    "set.nav.downloads": "Downloads",
    "set.nav.apps": "Applications",
    "set.nav.backup": "Backup",
    "set.nav.appearance": "Appearance",
    "set.header.checking": "Checking",
    "set.header.downloads": "Downloads",
    "set.header.apps": "Applications",
    "set.header.backup": "Backup & Maintenance",
    "set.header.appearance": "Appearance",
    "set.nav.about": "About",
    "set.header.about": "About SoftUpdater",
    "set.about.tagline": "Check your installed apps against their official sources - free & open source.",
    "set.about.version": "Version",
    "set.about.dev": "Developer",
    "set.about.source": "Official source code on GitHub",
    "set.about.license": "Released under the MIT License - free to use, study, modify and share.",
    "set.about.official": "Always download SoftUpdater only from its official repository:",
    "set.chk_auto": "Check for updates when the app starts",
    "tip.set.chk_auto": (
        "Runs a full update check by itself right after the app opens, so "
        "you see the update list without clicking anything."),
    "set.lbl_interval": "Re-check automatically every",
    "set.cmb_never": "Never",
    "set.cmb_hours": "{n} hour(s)",
    "tip.set.interval": (
        "Runs a full check by itself while the app is open, even when you "
        "have not touched it. Found updates raise a notification."),
    "set.chk_notify": "Show a notification when updates are found",
    "tip.set.notify": (
        "Windows toast about new updates after an automatic check "
        "(startup or scheduled). Manual checks never interrupt you."),
    "set.hint.checking": (
        "Automatic checks cover every app against its official source "
        "(results are cached, so repeats are fast)."),
    "set.lbl_save_to": "Save installers to",
    "set.btn.browse": "Browse...",
    "set.btn.reset_dir": "Use default folder",
    "tip.set.reset_dir": "Goes back to Downloads\\SoftUpdater",
    "set.dl_default": "Downloads\\SoftUpdater (default)",
    "set.hint.downloads": (
        "Choose where downloaded installers are saved. The default is the "
        "SoftUpdater folder inside your Downloads."),
    "set.btn.restore_hidden": "Restore hidden apps",
    "tip.set.restore_hidden": (
        "Puts back every app you hid with the right-click menu and "
        "re-scans the list."),
    "set.lbl_hidden_n": "{n} app(s) hidden from the list",
    "set.lbl_hidden_none": "Nothing is hidden",
    "set.btn.restore_skip": "Restore skipped versions",
    "tip.set.restore_skip": (
        "Lets the skipped versions show up as updates again (they were "
        "hidden with the right-click 'Skip this version' action)."),
    "set.lbl_skip_n": "{n} skipped version(s)",
    "set.lbl_skip_none": "No skipped versions",
    "set.hint.apps": (
        "Hide an app by right-clicking its row in the main window (useful "
        "for tools you update manually). A single version can be skipped "
        "the same way."),
    "set.btn.export": "Export app list...",
    "tip.set.export": (
        "Saves every listed app with its versions to a JSON file - a "
        "small backup of what this PC had installed."),
    "set.btn.import": "Import app list...",
    "tip.set.import": (
        "Compares a previously exported list with what is installed on "
        "this PC and reports what is missing or needs an update."),
    "set.btn.log": "Open log folder",
    "tip.set.log": (
        "The app writes a small log of checks, downloads and errors - "
        "handy when something needs reporting."),
    "set.hint.backup": (
        "The export file is a plain JSON list - nothing is uploaded "
        "anywhere."),
    "set.lbl_font": "Font size",
    "set.pt_suffix": " pt",
    "set.btn.reset_font": "Reset font to default",
    "tip.set.reset_font": "Puts the font size back to {default} pt",
    "set.hint.appearance": (
        "Drag to choose a size - the sample below shows it. The whole "
        "app changes when you press Done, and it is saved for the next "
        "time."),
    "set.lbl_preview": "Preview",
    "set.font.sample": (
        "The quick brown fox jumps over the lazy dog - Aa Bb 123"),
    "set.btn.done": "Done",
    "set.lbl_language": "Language",
    "set.hint.language": (
        "Applies instantly - every window switches without restarting."),
    "set.btn.tour": "Show the quick tour again",
    "tip.set.tour": (
        "Replays the first-run tips (your 'don't show again' choice is "
        "kept)."),

    # ----------------------------------------------------- onboarding
    "ob.title": "SoftUpdater quick tour",
    "ob.page_of": "Page {n} of {total}",
    "ob.btn.next": "Next",
    "ob.btn.back": "Back",
    "ob.btn.skip": "Skip tour",
    "ob.btn.finish": "Get started",
    "ob.chk.never": "Don't show these tips again",
    "ob.welcome.title": "Welcome to SoftUpdater",
    "ob.welcome.body": (
        "SoftUpdater checks your installed applications against their "
        "official sources and downloads the latest installers for you - "
        "safely, with SHA-256 verification.\n\n"
        "Start with the big green button: Check for updates."),
    "ob.ctx.title": "Right-click any row",
    "ob.ctx.body": (
        "The right-click menu on every app row holds the power features:\n"
        "- View details (versions, source, installer link)\n"
        "- Re-check just that app\n"
        "- Download its installer / open the official page\n"
        "- Skip one specific version, or hide apps you update yourself"),
    "ob.dl.title": "Downloads that finish the job",
    "ob.dl.body": (
        "Installers are saved to Downloads\\SoftUpdater. They can open "
        "automatically after the download - and once you install an "
        "update, that row flips to 'Up to date' by itself."),
    "ob.done.title": "Make it yours",
    "ob.done.body": (
        "Settings holds everything: this app speaks English, Persian, "
        "Arabic, Portuguese, French and German (right-to-left included), "
        "the font size adapts to your eyes, and automatic checks run on "
        "your schedule. SoftUpdater also lives in the system tray."),
}
