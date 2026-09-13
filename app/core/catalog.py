"""Curated catalog mapping installed-app names to their OFFICIAL update sources.

Every app is checked from its own original source:
  - GitHub Releases API            (open-source apps)
  - Official vendor JSON/HTML feeds (Chrome, Edge, Firefox, VLC, ...)
  - download-server directory listings (Blender, Python, LibreOffice, ...)

Apps NOT present here fall back to a GitHub auto-search by name, and
closed-source apps that publish no version feed are explicitly listed in
BLOCKED_GENERIC so the UI can explain why no update can be found instead of
showing a generic "unavailable".
"""

from __future__ import annotations
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Source types
# ---------------------------------------------------------------------------
# github       : {"repo": "owner/repo", "x64"/"x86": asset_regex?, "note": str?}
# json         : {"url", "version_paths": [...], "assets": {"x64":url,"x86":url,"any":url}}
#                or {"url_templates": {"x64": [...], "x86": [...]}}
# plain        : {"url", "version_regex", "take", "url_templates": {...}}
# html         : {"url", "version_regex"? / "url_regex"?, "take", "url_templates"?,
#                 "x64": {"url_regex"}, "x86": {"url_regex"}}
# mozilla      : {"json_url", "version_key", "url64", "url32"}
# videolan     : {}
# edge         : {}
# discord      : {}
# dir_download : {"base", "dir_regex", "file_regex"}   (two-step listing, Blender)

from ..i18n import tr

BLOCKED_GENERIC: dict[str, str] = {
    "steam": "blk.steam",
    "epic games": "blk.epic",
    "battlenet": "blk.battlenet",
    "gog galaxy": "blk.gog",
    "ubisoft connect": "blk.ubisoft",
    "ea app": "blk.ea_app",
    "origin": "blk.origin",
    "microsoft office": "blk.office",
    "microsoft 365": "blk.m365",
    "onedrive": "blk.onedrive",
    "dropbox": "blk.dropbox",
    "google drive": "blk.gdrive",
    "spotify": "blk.spotify",
    "whatsapp": "blk.whatsapp",
    "microsoft teams": "blk.teams",
    "slack": "blk.slack",
    "zoom": "blk.zoom",
    "teamviewer": "blk.teamviewer",
    "anydesk": "blk.anydesk",
    "opera": "blk.opera",
    "vivaldi": "blk.vivaldi",
    "adobe": "blk.adobe",
    "nvidia": "blk.nvidia",
    "geforce": "blk.nvidia",
    "amd radeon": "blk.amd",
    "amd software": "blk.amd",
    "malwarebytes": "blk.malwarebytes",
    "kaspersky": "blk.kaspersky",
    "avast": "blk.avast",
    "avg": "blk.avg",
    "bitdefender": "blk.bitdefender",
    "webview2": "blk.webview2",
    # ---- apps that update themselves / have no public feed ------------
    "termius": "blk.termius",
    "afterburner": "blk.afterburner",
    "rivatuner": "blk.rivatuner",
    "potplayer": "blk.potplayer",
    "windscribe": "blk.windscribe",
    "free download manager": "blk.fdm",
    "capcut": "blk.capcut",
    "canva": "blk.canva",
    "bluestacks": "blk.bluestacks",
    "ldplayer": "blk.ldplayer",
    "driver booster": "blk.driver_booster",
    "iobit": "blk.iobit",
    "allavsoft": "blk.allavsoft",
    "zd soft": "blk.zdsoft",
    "officesuite": "blk.officesuite",
    "maxon": "blk.maxon",
    "icue": "blk.icue",
    "miniconda3": "blk.miniconda",
    "miniconda": "blk.miniconda",
    "python launcher": "blk.python_launcher",
    "android studio": "blk.android_studio",
    "java": "blk.java",
    # ---- hardware vendor drivers / utilities --------------------------
    "intel": "blk.intel",
    "realtek": "blk.realtek",
    "rapoo": "blk.rapoo",
    "asus": "blk.asus",
    "asustek": "blk.asus",
    "rog": "blk.rog",
    "armoury": "blk.armoury",
    "aura": "blk.aura",
    # ---- VPN / network -------------------------------------------------
    "tap windows": "blk.tap_windows",
    "openvpn": "blk.openvpn",
    # ---- Microsoft system components / runtimes ------------------------
    "maintenance service": "blk.maintenance_service",
    "visual c++": "blk.vcredist",
    "net": "blk.dotnet",
    "microsoft windows": "blk.ms_windows",
    "windows software development kit": "blk.winsdk",
    "windows sdk": "blk.winsdk",
    "xna": "blk.xna",
    "visual basic": "blk.vb",
    "update health": "blk.update_health",
    "visio": "blk.visio",
    "microsoft project": "blk.project",
    "powerpoint": "blk.powerpoint",
    "microsoft word": "blk.word",
    "microsoft excel": "blk.excel",
    "microsoft outlook": "blk.outlook",
    "microsoft access": "blk.access",
    "microsoft onenote": "blk.onenote",
    "microsoft publisher": "blk.publisher",
}

# Names that need regex logic (token matching is not enough).
# "Visual Studio" family must be blocked WITHOUT catching "Visual Studio Code".
_BLOCKED_EXTRA = [
    (re.compile(r"visual studio(?!.*\bcode\b)"),
     "blk.visual_studio"),
]

_CATALOG: list[dict] = [
    # ------------------------------------------------------------------
    # Vendor feeds (proprietary, official version endpoints)
    # ------------------------------------------------------------------
    {
        "name": "Google Chrome",
        "match": ["google chrome", "chrome"],
        "exclude_match": ["remote desktop", "canary"],
        "source": {
            "type": "json",
            "url": "https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/stable/versions",
            "version_paths": ["versions.0.version"],
            "assets": {
                "x64": "https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise64.msi",
                "x86": "https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise.msi",
            },
        },
    },
    {
        "name": "Microsoft Edge",
        "match": ["microsoft edge", "edge"],
        "exclude_match": ["webview2", "canary", "beta", "dev"],
        "source": {"type": "edge"},
    },
    {
        "name": "Mozilla Firefox",
        "match": ["firefox"],
        "exclude_match": ["developer", "nightly", "esr", "pale moon", "waterfox"],
        "source": {
            "type": "mozilla",
            "json_url": "https://product-details.mozilla.org/1.0/firefox_versions.json",
            "version_key": "LATEST_FIREFOX_VERSION",
            "url64": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=en-US",
            "url32": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win&lang=en-US",
        },
    },
    {
        "name": "Mozilla Thunderbird",
        "match": ["thunderbird"],
        "source": {
            "type": "mozilla",
            "json_url": "https://product-details.mozilla.org/1.0/thunderbird_versions.json",
            "version_key": "LATEST_THUNDERBIRD_VERSION",
            "url64": "https://download.mozilla.org/?product=thunderbird-latest&os=win64&lang=en-US",
            "url32": "https://download.mozilla.org/?product=thunderbird-latest&os=win&lang=en-US",
        },
    },
    {
        "name": "VLC media player",
        "match": ["vlc"],
        "source": {"type": "videolan"},
    },
    {
        "name": "Discord",
        "match": ["discord"],
        "source": {"type": "discord"},
    },
    {
        "name": "GIMP",
        "match": ["gimp"],
        "source": {
            "type": "html",
            "url": "https://www.gimp.org/downloads/",
            "url_regex": r"((?:https?:)?//download\.gimp\.org/gimp/v[^\"']+/windows/gimp-([0-9.]+)-setup\.exe)",
            "take": "first",
        },
    },
    {
        "name": "Blender",
        "match": ["blender"],
        "source": {
            "type": "dir_download",
            "base": "https://download.blender.org/release/",
            "dir_regex": r"href=\"Blender(\d+\.\d+)/\"",
            "file_regex": r"(blender-{d}[0-9.]*-windows-x64\.msi)",
        },
    },
    {
        "name": "LibreOffice",
        "match": ["libreoffice"],
        "source": {
            "type": "html",
            "url": "https://download.documentfoundation.org/libreoffice/stable/",
            "version_regex": r"href=\"(\d+\.\d+\.\d+)/\"",
            "take": "max",
            "url_templates": {
                "x64": ["https://download.documentfoundation.org/libreoffice/stable/{v}/win/x86_64/LibreOffice_{v}_Win_x86-64.msi"],
                "x86": [],
            },
        },
    },
    {
        "name": "Python 3",
        "match": ["python"],
        "exclude_match": ["launcher"],
        "source": {
            "type": "json",
            "url": "https://www.python.org/api/v2/downloads/release/?is_published=true",
            "items_path": "",
            "version_path": "name",
            "version_extract_regex": r"(3\.[0-9]+\.[0-9]+)$",
            "filter_name_prefix": "Python 3",
            "filter_pre_release": True,
            "url_templates": {
                "x64": ["https://www.python.org/ftp/python/{v}/python-{v}-amd64.exe"],
                "x86": ["https://www.python.org/ftp/python/{v}/python-{v}.exe"],
            },
        },
    },
    {
        "name": "Node.js",
        "match": ["nodejs", "node js"],
        "source": {
            "type": "json",
            "url": "https://nodejs.org/dist/index.json",
            "items_path": "",
            "version_path": "version",
            "url_templates": {
                "x64": ["https://nodejs.org/dist/{vv}/node-{vv}-x64.msi"],
                "x86": ["https://nodejs.org/dist/{vv}/node-{vv}-x86.msi"],
            },
        },
    },
    {
        "name": "KeePass",
        "match": ["keepass"],
        "source": {
            "type": "html",
            "url": "https://keepass.info/download.html",
            "version_regex": r"KeePass-(2\.[0-9.]+)-Setup\.exe",
            "take": "first",
            "verify": False,  # sourceforge blocks HEAD from datacenter IPs
            "url_templates": {
                "x64": ["https://sourceforge.net/projects/keepass/files/KeePass%202.x/{v}/KeePass-{v}-Setup.exe/download"],
                "x86": ["https://sourceforge.net/projects/keepass/files/KeePass%202.x/{v}/KeePass-{v}-Setup.exe/download"],
            },
        },
    },
    {
        "name": "foobar2000",
        "match": ["foobar2000"],
        "source": {
            "type": "html",
            "url": "https://www.foobar2000.org/download",
            "url_regex": r"([/\w.:-]*foobar2000_v([0-9.]+)\.exe)",
            "take": "first",
        },
    },
    {
        "name": "Everything",
        "match": ["everything"],
        "source": {
            "type": "html",
            "url": "https://www.voidtools.com/downloads/",
            "version_regex": r"Everything-([0-9.]+)\.x64\.Installer\.exe",
            "take": "first",
            "url_templates": {
                "x64": ["https://www.voidtools.com/Everything-{v}.x64.Installer.exe"],
                "x86": ["https://www.voidtools.com/Everything-{v}.x86.Installer.exe"],
            },
        },
    },
    {
        "name": "Oracle VirtualBox",
        "match": ["virtualbox"],
        "source": {
            "type": "html",
            "url": "https://www.virtualbox.org/wiki/Downloads",
            "url_regex": r"(https://download\.virtualbox\.org/virtualbox/([0-9.]+)/VirtualBox-[0-9.]+-[0-9]+-Win\.exe)",
            "take": "first",
        },
    },
    {
        "name": "Calibre",
        "match": ["calibre"],
        "source": {
            "type": "github",
            "repo": "kovidgoyal/calibre",
            "x64": r"(?i)calibre-64bit-[0-9.]+\.msi$",
            "note": "vn.calibre",
        },
    },
    # ------------------------------------------------------------------
    # GitHub releases (open source, official repos)
    # ------------------------------------------------------------------
    {"name": "7-Zip", "match": ["7 zip"], "source": {"type": "github", "repo": "ip7z/7zip", "x64": r"7z\d+-(win-)?x64\.(exe|msi)$", "x86": r"7z\d+-(win-)?x32\.exe$"}},
    {"name": "Notepad++", "match": ["notepad++"], "source": {"type": "github", "repo": "Notepad-plus-plus/notepad-plus-plus", "x64": r"npp\.[0-9.]+\.Installer\.x64\.exe$", "x86": r"npp\.[0-9.]+\.Installer\.exe$"}},
    {"name": "qBittorrent", "match": ["qbittorrent"], "source": {"type": "github", "repo": "qbittorrent/qBittorrent", "x64": r"qbittorrent_[0-9.]+_x64_setup\.exe$", "x86": r"qbittorrent_[0-9.]+_setup\.exe$"}},
    {"name": "OBS Studio", "match": ["obs studio", "open broadcaster software"], "source": {"type": "github", "repo": "obsproject/obs-studio", "x64": r"(?i)obs-studio-.*windows.*installer\.exe$"}},
    {"name": "Audacity", "match": ["audacity"], "source": {"type": "github", "repo": "audacity/audacity"}},
    {"name": "HandBrake", "match": ["handbrake"], "source": {"type": "github", "repo": "HandBrake/HandBrake", "x64": r"HandBrake-[0-9.]+-x86_64-Win_GUI\.exe$", "x86": r"HandBrake-[0-9.]+-i686-Win_GUI\.exe$"}},
    {"name": "SumatraPDF", "match": ["sumatrapdf", "sumatra pdf"], "source": {"type": "github", "repo": "sumatrapdfreader/sumatrapdf", "x64": r"SumatraPDF-[0-9.]+-64-install\.exe$", "x86": r"SumatraPDF-[0-9.]+-install\.exe$"}},
    {"name": "ShareX", "match": ["sharex"], "source": {"type": "github", "repo": "ShareX/ShareX", "x64": r"(?i)sharex-[0-9.]+-setup(-x64)?\.exe$"}},
    {"name": "Telegram Desktop", "match": ["telegram"], "source": {"type": "github", "repo": "telegramdesktop/tdesktop", "x64": r"(?i)(td-setup-win-x64-[0-9.]+\.exe|td-portable-win-x64-[0-9.]+\.zip|tsetup[.-][0-9.]+\.exe)$", "x86": r"(?i)(td-setup-win-x86-[0-9.]+\.exe|td-portable-win-x86-[0-9.]+\.zip|tsetup[.-][0-9.]+\.exe)$", "note": "vn.telegram"}},
    {"name": "Signal Desktop", "match": ["signal"], "source": {"type": "github", "repo": "signalapp/Signal-Desktop", "x64": r"(?i)signal-desktop-win-[0-9.]+\.exe$"}},
    {"name": "Visual Studio Code", "match": ["visual studio code", "vscode"], "source": {"type": "json", "url": "https://update.code.visualstudio.com/api/releases/stable", "items_path": "", "version_path": "", "take": "first", "url_templates": {"x64": ["https://update.code.visualstudio.com/{v}/win32-x64-user/stable", "https://update.code.visualstudio.com/{v}/win32-x64/stable"], "x86": ["https://update.code.visualstudio.com/{v}/win32-x86-user/stable", "https://update.code.visualstudio.com/{v}/win32-x86/stable"]}, "note": "vn.vscode"}},
    {"name": "Git", "match": ["git"], "source": {"type": "github", "repo": "git-for-windows/git", "x64": r"Git-[0-9.]+-64-bit\.exe$", "x86": r"Git-[0-9.]+-32-bit\.exe$"}},
    {"name": "PowerShell", "match": ["powershell"], "source": {"type": "github", "repo": "PowerShell/PowerShell", "x64": r"PowerShell-[0-9.]+-win-x64\.msi$", "x86": r"PowerShell-[0-9.]+-win-x86\.msi$"}},
    {"name": "Windows Terminal", "match": ["windows terminal"], "source": {"type": "github", "repo": "microsoft/terminal", "x64": r"(?i)msixbundle$", "note": "vn.winterminal"}},
    {"name": "PowerToys", "match": ["powertoys", "microsoft powertoys"], "source": {"type": "github", "repo": "microsoft/PowerToys", "x64": r"PowerToys(User|Machine)Setup-[0-9.]+-x64\.exe$"}},
    {"name": "Windows Subsystem for Linux", "match": ["windows subsystem for linux", "wsl"], "source": {"type": "github", "repo": "microsoft/WSL", "x64": r"\.x64\.msi$"}},
    {"name": "RustDesk", "match": ["rustdesk"], "source": {"type": "github", "repo": "rustdesk/rustdesk"}},
    {"name": "Tailscale", "match": ["tailscale"], "source": {"type": "github", "repo": "tailscale/tailscale", "x64": r"tailscale-setup-[0-9.]+\.exe$"}},
    {"name": "Brave Browser", "match": ["brave"], "source": {"type": "github", "repo": "brave/brave-browser", "x64": r"BraveBrowserStandaloneSetup\.exe$", "x86": r"BraveBrowserStandaloneSetup32\.exe$"}},
    {"name": "KeePassXC", "match": ["keepassxc"], "source": {"type": "github", "repo": "keepassxreboot/keepassxc", "x64": r"(?i)keepassxc-[0-9.]+-win64\.msi$"}},
    {"name": "Bitwarden", "match": ["bitwarden"], "source": {"type": "github", "repo": "bitwarden/clients", "x64": r"Bitwarden-Installer-[0-9.]+\.exe$"}},
    {"name": "Obsidian", "match": ["obsidian"], "source": {"type": "github", "repo": "obsidianmd/obsidian-releases", "x64": r"(?i)obsidian-[0-9.]+\.exe$"}},
    {"name": "Joplin", "match": ["joplin"], "source": {"type": "github", "repo": "laurent22/joplin", "x64": r"(?i)joplin-setup-[0-9.]+\.exe$"}},
    {"name": "Zotero", "match": ["zotero"], "source": {"type": "github", "repo": "zotero/zotero", "x64": r"Zotero-[0-9.]+_x64_setup\.exe$", "x86": r"Zotero-[0-9.]+_setup\.exe$"}},
    {"name": "MuseScore", "match": ["musescore"], "source": {"type": "github", "repo": "musescore/MuseScore", "x64": r"(?i)musescore.*x86_64\.msi$"}},
    {"name": "Krita", "match": ["krita"], "source": {"type": "github", "repo": "KDE/krita", "x64": r"krita-x64-[0-9.]+-setup\.exe$", "x86": r"krita-x86-[0-9.]+-setup\.exe$"}},
    {"name": "ImageGlass", "match": ["imageglass"], "source": {"type": "github", "repo": "d2phap/ImageGlass", "x64": r"(?i)imageglass.*win-x64\.(msi|zip)$"}},
    {"name": "nomacs", "match": ["nomacs"], "source": {"type": "github", "repo": "nomacs/nomacs", "x64": r"(?i)nomacs-setup-x64\.msi$"}},
    {"name": "Greenshot", "match": ["greenshot"], "source": {"type": "github", "repo": "greenshot/greenshot", "x64": r"(?i)greenshot-installer.*\.exe$"}},
    {"name": "Flameshot", "match": ["flameshot"], "source": {"type": "github", "repo": "flameshot-org/flameshot", "x64": r"(?i)flameshot-[0-9.]+-win64\.(exe|msi)$"}},
    {"name": "WinMerge", "match": ["winmerge"], "source": {"type": "github", "repo": "WinMerge/winmerge", "x64": r"WinMerge-[0-9.]+-x64-Setup\.exe$", "x86": r"WinMerge-[0-9.]+-Setup\.exe$"}},
    {"name": "Duplicati", "match": ["duplicati"], "source": {"type": "github", "repo": "duplicati/duplicati", "x64": r"(?i)duplicati-.*win-x64-(gui|agent)\.(msi|exe)$"}},
    {"name": "rclone", "match": ["rclone"], "source": {"type": "github", "repo": "rclone/rclone", "x64": r"rclone-v[0-9.]+-windows-amd64\.zip$", "x86": r"rclone-v[0-9.]+-windows-386\.zip$"}},
    {"name": "Syncthing", "match": ["syncthing"], "source": {"type": "github", "repo": "syncthing/syncthing", "x64": r"syncthing-windows-amd64-.*\.zip$", "x86": r"syncthing-windows-386-.*\.zip$"}},
    {"name": "Nextcloud Desktop", "match": ["nextcloud"], "source": {"type": "github", "repo": "nextcloud/desktop", "x64": r"Nextcloud-[0-9.]+-setup-x64\.exe$"}},
    {"name": "WinSCP", "match": ["winscp"], "source": {"type": "github", "repo": "winscp/winscp", "x64": r"WinSCP-[0-9.]+-Setup\.exe$"}},
    {"name": "Cyberduck", "match": ["cyberduck"], "source": {"type": "github", "repo": "iterate-ch/cyberduck", "x64": r"(?i)cyberduck-installer-[0-9.]+\.exe$"}},
    {"name": "Transmission", "match": ["transmission"], "source": {"type": "github", "repo": "transmission/transmission", "x64": r"transmission-[0-9.]+-x64\.msi$"}},
    {"name": "yt-dlp", "match": ["yt-dlp", "ytdlp"], "source": {"type": "github", "repo": "yt-dlp/yt-dlp"}},
    {"name": "MPC-HC", "match": ["mpc-hc", "media player classic"], "source": {"type": "github", "repo": "clsid2/mpc-hc", "x64": r"(?i)mpc-hc\.[0-9.]+\.x64\.exe$"}},
    {"name": "FFmpeg", "match": ["ffmpeg"], "source": {"type": "github", "repo": "BtbN/FFmpeg-Builds", "x64": r"ffmpeg-master-latest-win64-gpl\.zip$", "x86": r"ffmpeg-master-latest-win32-gpl\.zip$", "note": "vn.ffmpeg"}},
    {"name": "Jellyfin Server", "match": ["jellyfin"], "source": {"type": "github", "repo": "jellyfin/jellyfin", "x64": r"(?i)jellyfin_[0-9.]+_windows-x64\.exe$"}},
    {"name": "Rufus", "match": ["rufus"], "source": {"type": "github", "repo": "pbatard/rufus", "x64": r"rufus-[0-9.]+\.exe$"}},
    {"name": "Ventoy", "match": ["ventoy"], "source": {"type": "github", "repo": "ventoy/Ventoy", "x64": r"ventoy-[0-9.]+-windows\.zip$"}},
    {"name": "balenaEtcher", "match": ["balena etcher", "etcher"], "source": {"type": "github", "repo": "balena-io/etcher", "x64": r"(?i)balenaetcher-[0-9.]+\.setup\.exe$"}},
    {"name": "CMake", "match": ["cmake"], "source": {"type": "github", "repo": "Kitware/CMake", "x64": r"cmake-[0-9.]+-windows-x86_64\.msi$"}},
    {"name": "Ninja", "match": ["ninja"], "source": {"type": "github", "repo": "ninja-build/ninja", "x64": r"ninja-win\.zip$", "x86": r"ninja-win\.zip$"}},
    {"name": "Neovim", "match": ["neovim"], "source": {"type": "github", "repo": "neovim/neovim", "x64": r"nvim-win64\.msi$", "x86": r"nvim-win32\.zip$"}},
    {"name": "Vim", "match": ["vim", "gvim"], "source": {"type": "github", "repo": "vim/vim-win32-installer", "x64": r"gvim_[0-9.]+_x64\.exe$", "x86": r"gvim_[0-9.]+\.exe$"}},
    {"name": "Arduino IDE", "match": ["arduino"], "source": {"type": "github", "repo": "arduino/arduino-ide", "x64": r"arduino-ide_[0-9.]+_Windows_64bit\.exe$"}},
    {"name": "Godot Engine", "match": ["godot"], "source": {"type": "github", "repo": "godotengine/godot", "x64": r"(?i)godot_v.*_win64\.exe\.zip$"}},
    {"name": "KiCad", "match": ["kicad"], "source": {"type": "github", "repo": "KiCad/kicad-source-mirror"}},
    {"name": "AutoHotkey", "match": ["autohotkey"], "source": {"type": "github", "repo": "AutoHotkey/AutoHotkey", "x64": r"(?i)autohotkey_[0-9._]*setup\.exe$"}},
    {"name": "Rainmeter", "match": ["rainmeter"], "source": {"type": "github", "repo": "rainmeter/rainmeter", "x64": r"Rainmeter-[0-9.]+\.exe$"}},
    {"name": "ExplorerPatcher", "match": ["explorerpatcher"], "source": {"type": "github", "repo": "valleyofdoom/ExplorerPatcher", "x64": r"ep_setup\.exe$"}},
    {"name": "CrystalDiskInfo", "match": ["crystaldiskinfo"], "source": {"type": "github", "repo": "hiyohiyo/CrystalDiskInfo", "x64": r"CrystalDiskInfo[0-9_]+\.exe$", "exclude": ["shizuku"]}},
    {"name": "CrystalDiskMark", "match": ["crystaldiskmark"], "source": {"type": "github", "repo": "hiyohiyo/CrystalDiskMark", "x64": r"CrystalDiskMark[0-9_]+\.exe$"}},
    {"name": "LibreHardwareMonitor", "match": ["libre hardware monitor", "librehardwaremonitor"], "source": {"type": "github", "repo": "LibreHardwareMonitor/LibreHardwareMonitor", "x64": r"(?i)librehardwaremonitor.*\.zip$"}},
    {"name": "FanControl", "match": ["fancontrol", "fan control"], "source": {"type": "github", "repo": "Rem0o/FanControl.Releases", "x64": r"(?i)fancontrol.*installer.*\.exe$"}},
    {"name": "PeaZip", "match": ["peazip"], "source": {"type": "github", "repo": "peazip/PeaZip", "x64": r"(?i)peazip.*\.exe$"}},
    {"name": "SMPlayer", "match": ["smplayer"], "source": {"type": "github", "repo": "smplayer-dev/smplayer", "x64": r"(?i)smplayer-[0-9.]+-x64(-noyt|-unsigned)?\.exe$"}},
    {"name": "Shotcut", "match": ["shotcut"], "source": {"type": "github", "repo": "mltframework/shotcut", "x64": r"(?i)shotcut-win64-[0-9.]+\.exe$"}},
    {"name": "OpenShot Video Editor", "match": ["openshot"], "source": {"type": "github", "repo": "OpenShot/openshot-qt", "x64": r"(?i)openshot.*x86_64.*\.exe$"}},
    {"name": "LosslessCut", "match": ["losslesscut"], "source": {"type": "github", "repo": "mifi/lossless-cut", "x64": r"(?i)losslesscut-win.*\.exe$"}},
    {"name": "LMMS", "match": ["lmms"], "source": {"type": "github", "repo": "LMMS/lmms"}},
    {"name": "Mixxx", "match": ["mixxx"], "source": {"type": "github", "repo": "mixxxdj/mixxx", "x64": r"(?i)mixxx-.*win64.*(msi|exe)$"}},
    {"name": "DBeaver CE", "match": ["dbeaver"], "source": {"type": "github", "repo": "dbeaver/dbeaver", "x64": r"(?i)dbeaver-ce-[0-9.]+-windows-x86_64\.exe$"}},
    {"name": "MarkText", "match": ["marktext"], "source": {"type": "github", "repo": "marktext/marktext", "x64": r"(?i)marktext-win-x64-[0-9.]+-setup\.exe$"}},
    {"name": "Anki", "match": ["anki"], "source": {"type": "github", "repo": "ankitects/anki", "x64": r"(?i)anki-[0-9.]+-win-x64\.(msi|exe)$"}},
    {"name": "PDFsam Basic", "match": ["pdfsam"], "source": {"type": "github", "repo": "torakiki/pdfsam", "x64": r"(?i)pdfsam-basic-[0-9.]+-windows-x64\.msi$"}},
    {"name": "Inkscape", "match": ["inkscape"], "source": {"type": "github", "repo": "inkscape/inkscape", "note": "vn.inkscape"}},
    # ------------------------------------------------------------------
    # Extra GitHub apps (seen on real machines)
    # ------------------------------------------------------------------
    {"name": "WinRAR", "match": ["winrar"], "source": {"type": "html", "url": "https://www.rarlab.com/download.htm", "x64": {"version_regex": r"WinRAR x64 \(64 bit\) ([0-9][0-9.]*)</b>", "take": "first"}, "x86": {"no_installer": True, "note": "vn.winrar_x86"}, "url_templates": {"x64": ["https://www.rarlab.com/rar/winrar-x64-{vd}.exe"], "x86": []}, "verify": False, "note": "vn.winrar"}},
    {"name": "Proton VPN", "match": ["proton vpn", "protonvpn"], "source": {"type": "github", "repo": "ProtonVPN/win-app", "x64": r"(?i)protonvpn_v[0-9.]+_x64\.exe$"}},
    {"name": "NekoBox", "match": ["nekobox", "neko box"], "source": {"type": "github", "repo": "MatsuriDayo/nekoray", "x64": r"(?i)nekoray-.*windows64\.zip$", "x86": r"(?i)nekoray-.*windows32\.zip$", "note": "vn.nekobox"}},
    {"name": "MyTonWallet", "match": ["mytonwallet"], "source": {"type": "github", "repo": "mytonwalletorg/mytonwallet", "x64": r"(?i)mytonwallet[ ._\-]setup[ ._\-]?[0-9.]+\.exe$"}},
    {"name": "Qtum Core", "match": ["qtum"], "source": {"type": "github", "repo": "qtumproject/qtum", "x64": r"qtum-[0-9.]+-win64-setup-unsigned\.exe$", "x86": r"qtum-[0-9.]+-win32-setup-unsigned\.exe$", "note": "vn.qtum"}},
    {"name": "LAV Filters", "match": ["lav filters"], "source": {"type": "github", "repo": "Nevcairiel/LAVFilters", "x64": r"(?i)lavfilters-[0-9.]+-installer\.exe$", "x86": r"(?i)lavfilters-[0-9.]+-installer\.exe$"}},
    {"name": "HidHide", "match": ["hidhide"], "source": {"type": "github", "repo": "nefarius/HidHide", "x64": r"(?i)hidhide_[0-9.]+_x64\.exe$"}},
    {"name": "ViGEm Bus Driver", "match": ["vigem bus driver", "vigembus"], "source": {"type": "github", "repo": "nefarius/ViGEmBus", "x64": r"(?i)vigembus(_setup)?_[0-9.]+_x64(_x86)?(_arm64)?\.exe$"}},
    {"name": "DS4Windows", "match": ["ds4windows", "d4windows"], "source": {"type": "github", "repo": "Ryochan7/DS4Windows", "x64": r"(?i)ds4windows(_v[0-9.]+)?_x64\.zip$"}},
    {"name": "AmneziaVPN", "match": ["amneziavpn", "amnezia vpn"], "source": {"type": "github", "repo": "AmneziaVPN/AmneziaVPN", "x64": r"(?i)amneziavpn[_.]?[0-9.]+[_.]?windows[_.]?x64\.exe$"}},
]

# Normalized lookup table built once at import
_ENTRIES: list[dict] = []
for _e in _CATALOG:
    from .version_utils import normalize_name

    _ENTRIES.append(
        {
            "name": _e["name"],
            "match": tuple(normalize_name(m) for m in _e["match"]),
            "exclude_match": tuple(normalize_name(m) for m in _e.get("exclude_match", [])),
            "source": _e["source"],
        }
    )


def entries() -> list[dict]:
    return _ENTRIES


def blocked_reason_key(normalized_name: str,
                       normalized_publisher: str = "") -> str | None:
    """Canonical (untranslated) reason KEY - the re-translatable form the
    checker stores on results so notes follow the UI language live."""
    tokens = set(normalized_name.split()) | set((normalized_publisher or "").split())
    for pattern, reason in BLOCKED_GENERIC.items():
        pat = set(pattern.split())
        if pat and pat.issubset(tokens):
            return reason
    for rx, reason in _BLOCKED_EXTRA:
        if rx.search(normalized_name):
            return reason
    return None


def blocked_reason(normalized_name: str, normalized_publisher: str = "") -> str | None:
    """Return an explanation when the app is known to be vendor-updated.

    Patterns are matched against the app name AND its publisher tokens, so
    e.g. anything published by ASUS/Intel/Adobe gets an honest explanation
    even when the product name itself does not contain the vendor name.
    """
    key = blocked_reason_key(normalized_name, normalized_publisher)
    return tr(key) if key else None


# ---------------------------------------------------------------------------
# winget-pkgs tracked system runtimes.
#
# `winget upgrade` resolves Microsoft Visual C++ Redistributables, WebView2
# and .NET runtimes from the microsoft/winget-pkgs manifest repository.
# Every manifest's InstallerUrl points at Microsoft's own download servers,
# so these runtimes can be checked and downloaded honestly instead of being
# reported as "Managed by vendor". The mapping below mirrors exactly the
# package IDs winget itself uses.
# ---------------------------------------------------------------------------

_VCREDIST_YEARS = {"2005", "2008", "2010", "2012", "2013"}

_VC_YEAR_RE = re.compile(r"(?i)visual\s*c\+\+\s*((?:\d{4})(?:-\d{4})?)")
_DOTNET_MAJOR_RE = re.compile(r"(?i)(?:desktop|\.net)\s*runtime\s*-\s*(\d+)\.")
_ARCH_X64_RE = re.compile(r"(?<![0-9a-z])(x64|win64|amd64)(?![0-9a-z])")
_ARCH_X86_RE = re.compile(r"(?<![0-9a-z])(x86|win32|ia32)(?![0-9a-z])")


def _name_arch(name_low: str) -> str:
    """The architecture token in a display name ('' when none)."""
    if _ARCH_X64_RE.search(name_low):
        return "x64"
    if _ARCH_X86_RE.search(name_low):
        return "x86"
    return ""


def winget_package_for(app_name: str, os_bitness: int = 64) -> dict | None:
    """Map a system-runtime display name to its official winget package.

    Returns {"package_id": str, "arch": str} or None when the name is not a
    known winget-tracked runtime. Deliberately conservative:

    * VC++ entries MUST carry an architecture token (x64/x86 coexist on the
      same machine, so guessing from the OS bitness would be wrong); entries
      without one keep the honest vendor explanation as a fallback.
    * ".NET Framework" is NOT mapped (it is served by Windows Update, not
      winget) and keeps its vendor explanation.
    """
    low = (app_name or "").strip().lower()
    if not low:
        return None
    fallback_arch = "x64" if os_bitness == 64 else "x86"

    if "visual c++" in low:
        m = _VC_YEAR_RE.search(low)
        if not m:
            return None
        year = m.group(1)
        if year.startswith("2015"):        # "2015" or "2015-2022"
            year = "2015+"
        elif year not in _VCREDIST_YEARS:
            return None
        arch = _name_arch(low)
        if not arch:
            return None                    # ambiguous -> vendor fallback
        return {"package_id": f"Microsoft.VCRedist.{year}.{arch}", "arch": arch}

    if "webview2 runtime" in low:
        # WebView2 has no architecture in its display name; the installed
        # runtime always matches the OS bitness (same rule winget uses).
        return {"package_id": "Microsoft.EdgeWebView2Runtime",
                "arch": _name_arch(low) or fallback_arch}

    if "desktop runtime" in low or ".net runtime" in low:
        m = _DOTNET_MAJOR_RE.search(low)
        if not m:
            return None
        family = ("Microsoft.DotNet.DesktopRuntime." if "desktop runtime" in low
                  else "Microsoft.DotNet.Runtime.")
        return {"package_id": family + m.group(1),
                "arch": _name_arch(low) or fallback_arch}

    return None
