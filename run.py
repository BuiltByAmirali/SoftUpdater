"""SoftUpdater entry point.

Check installed Windows apps against their official sources.
Copyright (c) 2025 BuiltByAmirali - https://github.com/BuiltByAmirali/SoftUpdater
Released under the MIT License (see LICENSE).

Usage:
  python run.py             - launch the GUI
  python run.py --selftest  - run offline core self-tests (no GUI, no network)
"""
from __future__ import annotations

import sys


def selftest() -> int:
    """Offline self-test of core logic (no network, no GUI)."""
    from app.core.catalog import entries
    from app.core.installed_apps import InstalledApp
    from app.core.update_checker import UpdateChecker
    from app.core.version_utils import compare_versions, normalize_name
    from app.core.win_info import os_bitness, windows_summary

    failures = []

    def check(label, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        if not cond:
            failures.append(label)

    print("Self-test: version comparison")
    check("1.0.0 < 1.0.1", compare_versions("1.0.0", "1.0.1") < 0)
    check("24.08 == 24.08", compare_versions("24.08", "24.08") == 0)
    check("3.0.20 < 3.0.21", compare_versions("3.0.20", "3.0.21") < 0)
    check("10.0.19045 stays < 11-ish string", compare_versions("126.0", "127.0") < 0)
    check("v1.2.3 == 1.2.3", compare_versions("v1.2.3", "1.2.3") == 0)
    check("empty == empty", compare_versions("", "") == 0)

    print("Self-test: name normalization")
    check("7-Zip 24.08 (x64) normalizes like '7-Zip'",
          normalize_name("7-Zip 24.08 (x64)") == normalize_name("7-Zip"))
    check("Notepad++ (64-bit x64) keeps ++", "notepad++" in normalize_name("Notepad++ (64-bit x64)"))
    check("WinRAR 7.01 (64-bit) -> 'winrar'", normalize_name("WinRAR 7.01 (64-bit)") == "winrar")

    print("Self-test: source resolution")
    checker = UpdateChecker(allow_github_search=False)
    cases = [
        ("7-Zip 24.08 (x64)", "7-Zip"),
        ("VLC media player 3.0.20", "VLC media player"),
        ("Notepad++ (64-bit x64)", "Notepad++"),
        ("Google Chrome", "Google Chrome"),
        ("Microsoft Edge", "Microsoft Edge"),
        ("Mozilla Firefox (x64 en-US)", "Mozilla Firefox"),
        ("OBS Studio", "OBS Studio"),
        ("Git 2.45.1", "Git"),
        ("GitHub Desktop", None),  # must NOT match 'Git' (token matching)
        ("Microsoft Edge WebView2 Runtime", None),
        ("qBittorrent 4.6.5", "qBittorrent"),
        ("Microsoft Visual C++ 2015 Redistributable (x64)", None),
    ]
    for name, expected in cases:
        got = checker.resolve_source(normalize_name(name))
        got_name = got["name"] if got else None
        check(f"'{name}' -> {expected}", got_name == expected)

    print("Self-test: blocked apps get an explanation")
    reason = __import__("app.core.catalog", fromlist=["blocked_reason"]).blocked_reason(
        normalize_name("Steam")
    )
    check("Steam blocked with reason", bool(reason))

    print("Self-test: result finalization (status honesty)")
    from app.core.update_checker import CheckResult

    def fin(status, inst, lat, note=""):
        r = CheckResult(app_name="x", status=status, installed_version=inst,
                        latest_version=lat, note=note)
        return UpdateChecker._finalize(r)

    check("no_installer + equal versions -> latest",
          fin("no_installer", "1.22.0", "1.22.0").status == "latest")
    check("update + equal versions -> latest",
          fin("update", "7.2.8", "7.2.8").status == "latest")
    check("no_installer + older installed stays no_installer",
          fin("no_installer", "1.0.0", "2.0").status == "no_installer")
    check("no_installer + newer installed -> latest",
          fin("no_installer", "2.0", "1.9.9").status == "latest")
    check("latest + older installed -> update",
          fin("latest", "3.0.20", "3.0.21").status == "update")
    check("no_installer + unknown latest stays no_installer",
          fin("no_installer", "7.11.0", "").status == "no_installer")

    print("Self-test: GitHub auto-match confidence gate")
    gate = UpdateChecker._auto_match_ok
    check("Organization repo accepted",
          gate({"name": "myapp", "owner": {"type": "Organization"},
                "stargazers_count": 2}, "myapp"))
    check("100+ star user repo accepted",
          gate({"name": "myapp", "owner": {"type": "User"},
                "stargazers_count": 150}, "myapp"))
    check("low-star personal repo rejected",
          not gate({"name": "spotplayer", "owner": {"type": "User"},
                    "stargazers_count": 7}, "spotplayer"))
    check("different repo name rejected",
          not gate({"name": "other-app", "owner": {"type": "Organization"},
                    "stargazers_count": 999}, "myapp"))

    print("Self-test: hotfix/update entry skipping")
    from app.core.installed_apps import _is_update_entry
    check("'Update for  (KB2504637)' skipped (double space)",
          _is_update_entry("Update for  (KB2504637)"))
    check("KB958488 skipped", _is_update_entry("KB958488"))
    check("'Updater Pro' is a real app (kept)", not _is_update_entry("Updater Pro"))

    print("Self-test: URL template tokens")
    tc = UpdateChecker._template_candidates(
        "https://www.rarlab.com/rar/winrar-x64-{vd}.exe", "7.23")
    check("{vd} expands to 723", any(u.endswith("winrar-x64-723.exe") for u in tc))

    print("Self-test: stale asset-name regressions (real release assets)")
    checker.bitness = 64
    tg = next(e for e in entries() if e["name"] == "Telegram Desktop")
    tg_assets = [
        {"name": "td-setup-win-x64-7.2.8.exe",
         "browser_download_url": "https://example.com/td-setup-win-x64-7.2.8.exe"},
        {"name": "td-setup-win-x86-7.2.8.exe",
         "browser_download_url": "https://example.com/td-setup-win-x86-7.2.8.exe"},
        {"name": "td-portable-win-x64-7.2.8.zip",
         "browser_download_url": "https://example.com/td-portable-win-x64-7.2.8.zip"},
    ]
    url = checker._pick_asset(tg["source"], tg_assets,
                              CheckResult(app_name="Telegram Desktop"))
    check("Telegram picks the new td-setup-win-x64 installer",
          url.endswith("td-setup-win-x64-7.2.8.exe"))

    qt = next(e for e in entries() if e["name"] == "Qtum Core")
    qt_assets = [
        {"name": "qtum-30.2-win64-setup-unsigned.exe",
         "browser_download_url": "https://example.com/qtum-setup.exe"},
        {"name": "qtum-30.2-win64-unsigned.zip",
         "browser_download_url": "https://example.com/qtum.zip"},
    ]
    url = checker._pick_asset(qt["source"], qt_assets,
                              CheckResult(app_name="Qtum Core"))
    check("Qtum picks the -unsigned setup exe", url.endswith("qtum-setup.exe"))

    vg = next(e for e in entries() if e["name"] == "ViGEm Bus Driver")
    vg_assets = [{"name": "ViGEmBus_1.22.0_x64_x86_arm64.exe",
                  "browser_download_url": "https://example.com/vigem.exe"}]
    url = checker._pick_asset(vg["source"], vg_assets,
                              CheckResult(app_name="ViGEm Bus Driver"))
    check("ViGEm picks the combined x64 installer", url.endswith("vigem.exe"))
    arm_only = checker._pick_asset(
        {"type": "github", "repo": "x/y"},
        [{"name": "app-1.0-arm64.exe", "browser_download_url": "u-arm"}],
        CheckResult(app_name="x"))
    check("arm64-only asset is NOT offered on x64", arm_only == "")
    arm_plain = checker._pick_asset(
        {"type": "github", "repo": "x/y"},
        [{"name": "app-1.0-arm.exe", "browser_download_url": "u-arm2"}],
        CheckResult(app_name="x"))
    check("plain arm asset is NOT offered on x64", arm_plain == "")

    print("Self-test: WinRAR official source")
    import re as _re
    wr = next(e for e in entries() if e["name"] == "WinRAR")
    sample = ('<b>WinRAR x64 (64 bit) 7.30 beta 1</b></a></td>\n'
              '<b>WinRAR x64 (64 bit) 7.23</b></a></td>')
    ms = _re.findall(wr["source"]["x64"]["version_regex"], sample)
    check("WinRAR stable regex skips the beta", ms == ["7.23"])
    got = checker.resolve_source(normalize_name("WinRAR 7.11 (64-bit)"))
    check("WinRAR resolves to the catalog entry",
          (got or {}).get("name") == "WinRAR")
    check("WinRAR is no longer vendor-blocked",
          __import__("app.core.catalog", fromlist=["blocked_reason"]).blocked_reason(
              "winrar") is None)

    print("Self-test: catalog integrity")
    types_ok = all(
        e["source"]["type"] in
        {"github", "json", "plain", "html", "mozilla", "videolan", "edge", "discord", "dir_download"}
        for e in entries()
    )
    check("all source types known", types_ok)
    repos_ok = all("/" in e["source"]["repo"] for e in entries() if e["source"]["type"] == "github")
    check("all github repos are owner/repo", repos_ok)
    keys = [e["name"] for e in entries()]
    check("no duplicate catalog names", len(keys) == len(set(keys)))

    print("Self-test: download size/speed formatting + pause")
    from app.core.downloader import DownloadPaused, format_size, format_speed

    check("format_size(0) == '0 B'", format_size(0) == "0 B")
    check("format_size(523) == '523 B'", format_size(523) == "523 B")
    check("format_size(20480) == '20 KB'", format_size(20480) == "20 KB")
    check("format_size(78412377) == '74.8 MB'", format_size(78412377) == "74.8 MB")
    check("format_size(1610612736) == '1.5 GB'", format_size(1610612736) == "1.5 GB")
    check("format_speed(0) == ''", format_speed(0) == "")
    check("format_speed(2516582.4) == '2.4 MB/s'", format_speed(2516582.4) == "2.4 MB/s")
    check("DownloadPaused keeps the byte count", DownloadPaused(1234).done_bytes == 1234)

    print("Self-test: platform info")
    check("bitness in (32, 64)", os_bitness() in (32, 64))
    check("windows summary non-empty", bool(windows_summary()))

    print("Self-test: fresh-version matching (per-app re-check after install)")
    from app.core.installed_apps import (
        FreshIndex,
        InstalledApp,
        build_fresh_index,
        match_fresh_version,
    )

    def _idx(entries):
        """entries: (name, version, hive, key) -> a FreshIndex."""
        idx = FreshIndex()
        for n, v, hive, key in entries:
            a = InstalledApp(name=n, version=v, hive=hive, key=key)
            from app.core.version_utils import normalize_name
            norm = normalize_name(n)
            if norm:
                idx.by_name.setdefault(norm, []).append(a)
            if key:
                idx.by_key[(hive, key)] = a
        return idx

    idx = _idx([
        ("Foo 2.0", "2.0", "HKLM64", "{F0}"),
        ("Bar 1.0", "1.0", "HKLM64", "{B1}"),
        ("Bar 3.1", "3.1", "HKLM64", "{B2}"),
        ("Zed", "", "HKCU", "{Z}"),
    ])
    check("exact match refreshes the version",
          match_fresh_version(
              InstalledApp(name="Foo 1.0", version="1.0"), idx) == "2.0")
    check("same version -> no refresh",
          match_fresh_version(
              InstalledApp(name="Foo 1.0", version="2.0"), idx) == "")
    check("ambiguous duplicate entries -> refuse (no guessing)",
          match_fresh_version(
              InstalledApp(name="Bar 1.0", version="1.0"), idx) == "")
    check("unknown app -> no refresh",
          match_fresh_version(
              InstalledApp(name="Whatever", version="1.0"), idx) == "")
    check("version-less fresh entry -> no refresh",
          match_fresh_version(
              InstalledApp(name="Zed", version="1.0"), idx) == "")
    check("empty name -> no refresh",
          match_fresh_version(
              InstalledApp(name="", version="1.0"), idx) == "")
    check("empty index -> no refresh",
          match_fresh_version(
              InstalledApp(name="Foo", version="1.0"), FreshIndex()) == "")

    # Stage 1: registry-key identity (the winget correlation anchor).
    idx2 = _idx([("Foo 2.0", "2.5", "HKLM64", "{F0}")])
    check("same registry key + new version -> refresh",
          match_fresh_version(
              InstalledApp(name="Foo 1.0", version="1.0",
                           hive="HKLM64", key="{F0}"), idx2) == "2.5")
    check("same registry key + same version -> no refresh",
          match_fresh_version(
              InstalledApp(name="Foo 1.0", version="2.5",
                           hive="HKLM64", key="{F0}"), idx2) == "")
    check("vanished key falls back to the name bucket (cross-hive)",
          match_fresh_version(
              InstalledApp(name="Foo 1.0", version="1.0",
                           hive="HKLM32", key="{F0}"), idx2) == "2.5")
    check("key identity wins over a same-name newer app",
          match_fresh_version(
              InstalledApp(name="Foo 1.0", version="1.0",
                           hive="HKLM64", key="{F0}"), idx) == "2.0")

    check("build_fresh_index returns a FreshIndex",
          isinstance(build_fresh_index(), FreshIndex))

    print("Self-test: custom download folder override")
    import os
    import tempfile

    from app.core.downloader import download_dir, set_custom_download_dir

    set_custom_download_dir(None)
    default_dir = download_dir()
    check("default folder ends with SoftUpdater", default_dir.endswith("SoftUpdater"))
    tmp = tempfile.mkdtemp(prefix="su_selftest_")
    set_custom_download_dir(tmp)
    check("custom folder honored", download_dir() == tmp)
    set_custom_download_dir(os.path.join(tmp, "does-not-exist"))
    check("invalid custom folder falls back", download_dir() == default_dir)
    set_custom_download_dir("   ")
    check("blank custom folder resets", download_dir() == default_dir)
    set_custom_download_dir(None)

    print("Self-test: winget-pkgs runtime checking (VC++ / WebView2 / .NET)")
    from app.core.catalog import winget_package_for
    from app.core.update_checker import WINGET_API, WINGET_RAW
    from app.core.version_utils import prefix_equal

    w = winget_package_for(
        "Microsoft Visual C++ 2015-2022 Redistributable (x64) - 14.44.35211", 64)
    check("VC++ 2015-2022 (x64) -> official winget package",
          w == {"package_id": "Microsoft.VCRedist.2015+.x64", "arch": "x64"})
    w = winget_package_for(
        "Microsoft Visual C++ 2012 x86 Minimum Runtime - 11.0.61135", 64)
    check("VC++ 2012 x86 runtime entry -> x86 winget package",
          w == {"package_id": "Microsoft.VCRedist.2012.x86", "arch": "x86"})
    w = winget_package_for("Microsoft Edge WebView2 Runtime", 64)
    check("WebView2 -> official winget package",
          w == {"package_id": "Microsoft.EdgeWebView2Runtime", "arch": "x64"})
    check(".NET Framework is NOT mapped (Windows Update)",
          winget_package_for("Microsoft .NET Framework 4.8.1", 64) is None)
    check("arch-less VC++ is NOT mapped (vendor fallback keeps honesty)",
          winget_package_for("Microsoft Visual C++ 2013 Redistributable", 64) is None)
    check("winget paths are the official microsoft/winget-pkgs repo",
          WINGET_API.startswith("https://api.github.com/repos/microsoft/winget-pkgs")
          and WINGET_RAW.startswith(
              "https://raw.githubusercontent.com/microsoft/winget-pkgs/"))
    check("MSI DisplayVersion truncation counts as the same build",
          prefix_equal("12.0.40664", "12.0.40664.0")
          and prefix_equal("14.44.35211.0", "14.44.35211"))
    check("different versions are not 'prefix equal'",
          not prefix_equal("11.0.61135", "11.0.61030.0")
          and not prefix_equal("8.0.14", "8.0.31"))
    yaml_2015 = (
        "Installers:\n"
        "- Architecture: x64\n"
        "  InstallerUrl: https://download.visualstudio.microsoft.com/download/pr/x/VC_redist.x64.exe\n"
        "- Architecture: x86\n"
        "  InstallerUrl: https://download.visualstudio.microsoft.com/download/pr/x/VC_redist.x64.exe\n"
        "ManifestType: installer\n")
    check("installer manifest parses the official x64 URL",
          UpdateChecker._parse_installer_yaml(yaml_2015, "x64").endswith("VC_redist.x64.exe"))
    check("winget manifest path mirrors the package id",
          UpdateChecker._winget_path("Microsoft.VCRedist.2015+.x64")
          == "manifests/m/Microsoft/VCRedist/2015+/x64")

    print("Self-test: winget bridge (UniGetUI-style name -> package ID)")
    from app.core import winget_bridge as wb

    def wg_table(rows):
        """Build a winget-CLI-shaped table: column start offsets come from
        the header, long names are truncated with '...' like the real CLI."""
        widths = (34, 30, 13, 11)
        header = "".join(c.ljust(w) for c, w in
                         zip(("Name", "Id", "Version", "Available"), widths)).rstrip()
        lines = [header, "-" * (sum(widths) + 6)]
        for name, pkg_id, version, available in rows:
            if len(name) > widths[0] - 1:  # the real CLI truncates with '...'
                name = name[:widths[0] - 4] + "..."
            lines.append(name.ljust(widths[0]) + pkg_id.ljust(widths[1])
                         + version.ljust(widths[2]) + available)
        return "\n" + "\n".join(lines) + "\n\n"

    english_table = wg_table([
        ("Git 2.45.1", "Git.Git", "2.45.1", "2.47.1"),
        ("Microsoft Visual C++ 2015-2022 Redistributable (x64)",
         "Microsoft.VCRedist.2015+.x64", "14.44.35211", "14.51.36247"),
        ("Notepad++ (64-bit x64)", "Notepad++.Notepad++", "8.6.9", "8.7.6"),
        ("Steam", "Valve.Steam", "9.0.15.0", ""),
    ])
    rows = wb.parse_winget_table(english_table)
    check("table parses 4 valid rows", len(rows) == 4)
    check("long name is truncated like the real CLI (visible part kept)",
          any(r["name"].endswith("...")
              and r["id"] == "Microsoft.VCRedist.2015+.x64" for r in rows))
    check("row without Available still parses",
          any(r["id"] == "Valve.Steam" and r["version"] == "9.0.15.0" for r in rows))
    check("multi-word names survive offset slicing",
          any(r["name"] == "Git 2.45.1" for r in rows))

    localized_table = (
        '\n\u0646\u0627\u0645            \u0634\u0646\u0627\u0633\u0647            \u0646\u0633\u062e\u0647      \u062f\u0631 \u062f\u0633\u062a\u0631\u0633  \u0645\u0646\u0628\u0639\n'
        '---------------------------------------------------------------\n'
        'Git 2.45.1       Git.Git        2.45.1    2.47.1     winget\n'
        '\n'
    )
    rows_fa = wb.parse_winget_table(localized_table)
    check("localized header table parses by column OFFSETS",
          len(rows_fa) == 1 and rows_fa[0]["id"] == "Git.Git")

    bad_table = (
        'Name                 Id          Version\n'
        '-----------------------------------------\n'
        'Something Odd        24.08       24.08\n'
        'No Id Row            -           1.0\n'
    )
    check("rows with version-like/missing IDs are dropped",
          wb.parse_winget_table(bad_table) == [])

    fake_rows = [
        {"name": "Git 2.45.1", "id": "Git.Git", "version": "2.45.1"},
        {"name": "Microsoft Visual C++ 2015-2022 Redistributable (x64)",
         "id": "Microsoft.VCRedist.2015+.x64", "version": "14.44"},
        {"name": "Microsoft Visual C++ 2015-2022 Redistributable (x86)",
         "id": "Microsoft.VCRedist.2015+.x86", "version": "14.44"},
        {"name": "Mozilla Firefox (x64 en-US)...",
         "id": "Mozilla.Firefox", "version": "127.0"},
    ]
    check("exact raw name wins",
          wb.lookup("Git 2.45.1", fake_rows) == "Git.Git")
    check("truncated winget name still resolves via normalized match + arch",
          wb.lookup("Microsoft Visual C++ 2015-2022 Redistributable (x64) - 14.44",
                    fake_rows) == "Microsoft.VCRedist.2015+.x64"
          and wb.lookup("Microsoft Visual C++ 2015-2022 Redistributable (x86) - 14.44",
                        fake_rows) == "Microsoft.VCRedist.2015+.x86")
    check("ambiguous arch-less name refuses to guess",
          wb.lookup("Microsoft Visual C++ 2015-2022 Redistributable",
                    fake_rows) == "")
    check("truncated winget name matches as unique prefix",
          wb.lookup("Mozilla Firefox (x64 en-US) 127.0.2", fake_rows)
          == "Mozilla.Firefox")
    check("short/unknown names return empty",
          wb.lookup("Whatever Tool", fake_rows) == "" and
          wb.lookup("", fake_rows) == "")
    check("winget ID grammar rejects version-only cells",
          wb._row_from_cells(["x", "24.08", "24.08"]) is None
          and wb._row_from_cells(["x", "- ", "1.0"]) is None
          and wb._row_from_cells(
              ["Git", "Git.Git", "2.45.1"]) == {"name": "Git", "id": "Git.Git",
                                                "version": "2.45.1",
                                                "available": ""})

    print("Self-test: authless release discovery + winget extras")
    from app.core.update_checker import (
        _assets_from_expanded_html as _afeh,
        _latest_stable_tag_from_atom as _lasta,
    )

    atom_xml = (
        '<feed><entry><link href="https://github.com/o/r/releases/tag/v1.9.9"/>'
        "</entry><entry><link href=\"https://github.com/o/r/releases/tag/v1.10.0\"/>"
        "</entry><entry><link href=\"https://github.com/o/r/releases/tag/v1.10.1-beta\"/>"
        "</entry></feed>")
    check("atom feed picks the newest STABLE tag (1.10 > 1.9)",
          _lasta(atom_xml) == "v1.10.0")
    check("atom feed falls back to prereleases when only they exist",
          _lasta('<feed><entry><link href="https://github.com/o/r/releases/tag/1.0-rc1"/></entry></feed>')
          == "1.0-rc1")
    html_frag = (
        '<a href="/o/r/releases/download/1.2.0/app-1.2.0-win64.exe">'
        "</a>...sha256:" + "ab" * 32 + "...</span> 12.3 MB</span>"
        '<a href="/o/r/releases/download/1.2.0/app-1.2.0.zip"></a> 1 KB<')
    assets = _afeh(html_frag, "o/r")
    check("expanded_assets parses name/url/sha/size",
          len(assets) == 2
          and assets[0]["name"] == "app-1.2.0-win64.exe"
          and assets[0]["digest"] == "sha256:" + "ab" * 32
          and abs(assets[0]["size"] - 12.3 * 1024 * 1024) < 1024
          and assets[1]["size"] == 1024)
    check("expanded_assets ignores archive links",
          _afeh('<a href="/o/r/archive/refs/tags/1.2.0.zip">x</a>', "o/r") == [])

    vtxt = ("Version\n--------\n1.2.3\n1.10.0\nv0.9.1\nLanguage\nen\n")
    check("winget --versions parser keeps only version lines",
          wb._parse_versions_output(vtxt) == ["1.2.3", "1.10.0", "v0.9.1"])

    from app.core.downloader import installer_signature_error as _ise
    import tempfile as _tf

    with _tf.TemporaryDirectory() as _d:
        _p = os.path.join(_d, "x.exe")
        with open(_p, "wb") as _f:
            _f.write(b"MZ" + b"\x00" * 62 + (64).to_bytes(4, "little")
                     + b"PE\x00\x00" + b"\x00" * (80 * 1024 - 68))
        check("signature check accepts a structurally real PE exe",
              _ise(_p) == "")
        with open(_p, "wb") as _f:
            _f.write(b"MZ" + b"\x00" * 4096)
        check("signature check rejects MZ-only junk (no PE header)",
              bool(_ise(_p)))
        with open(_p, "wb") as _f:
            _f.write(b"<!DOCTYPE html>" * 100)
        check("signature check rejects HTML saved as .exe", bool(_ise(_p)))

    print("Self-test: SHA-256 helpers")
    import hashlib as _hl
    import tempfile as _tf

    from app.core.downloader import _sha_matches, file_sha256

    payload = b"SoftUpdater SHA-256 self test payload"
    good = _hl.sha256(payload).hexdigest()
    tf = _tf.NamedTemporaryFile(delete=False, suffix=".bin")
    tf.write(payload)
    tf.close()
    check("file_sha256 streams the right hash",
          file_sha256(tf.name) == good)
    check("_sha_matches accepts the correct hash",
          _sha_matches(tf.name, good.upper()))
    check("_sha_matches rejects a wrong hash",
          not _sha_matches(tf.name, "0" * 64))
    check("_sha_matches refuses malformed hashes",
          not _sha_matches(tf.name, "zz"))
    os.remove(tf.name)

    print("Self-test: installer manifest SHA-256 extraction")
    yaml_sha = (
        "Installers:\n"
        "- InstallerSha256: ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789\n"
        "  InstallerUrl: https://download.visualstudio.microsoft.com/vc_redist.x64.exe\n"
        "  Architecture: x64\n"
        "ManifestType: installer\n")
    url, sha = UpdateChecker._pick_installer(yaml_sha, "x64")
    check("_pick_installer returns url AND sha256",
          url.endswith("vc_redist.x64.exe")
          and sha == "abcdef0123456789" * 4)

    print("Self-test: app log layout")
    from app.core import applog

    check("log dir ends with SoftUpdater/logs",
          applog.log_dir().endswith(os.path.join("SoftUpdater", "logs")))
    check("log file is inside the log dir",
          os.path.dirname(applog.log_file()) == applog.log_dir())
    applog.event("selftest event line")
    applog.error("selftest error line")
    applog.install_crash_hook()
    try:
        raise ValueError("selftest crash hook probe")
    except ValueError:
        import sys as _sys

        applog.get_logger()  # ensure the logger exists
        _sys.excepthook(ValueError, ValueError("probe"), None)
    check("log file exists after events", os.path.exists(applog.log_file()))

    print("Self-test: official-mirror download fallback + icon engine")
    import http.server as _hs
    import shutil as _shutil
    import struct as _st
    import tempfile as _tf
    import threading as _th

    from app.core import downloader as _dl
    from app.core.downloader import download as _download
    from app.ui import app_icons as _ai

    # (a) pure icon helpers
    check("slug candidates: 'LAV Filters' joins to 'lavfilters'",
          "lavfilters" in _ai.slug_candidates("LAV Filters 0.78"))
    check("slug candidates: single distinctive token 'vlc'",
          "vlc" in _ai.slug_candidates("VLC media player"))
    check("icon image magic: PNG yes, HTML no",
          _ai._is_image(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
          and not _ai._is_image(b"<html>"))
    check("icon DB parser tolerates garbage",
          _ai._parse_icon_db(b"{nope") == {})

    def _mini_lnk(icon: str) -> bytes:
        header = bytearray(0x4C)
        header[0:4] = (0x4C).to_bytes(4, "little")
        header[4:20] = _ai._LNK_CLSID
        header[0x14:0x18] = _st.pack("<I", 0x40 | 0x80)  # HasIconLocation+IsUnicode
        data = icon.encode("utf-16-le")
        return (bytes(header) + _st.pack("<H", len(icon) + 1) + data
                + b"\x00\x00" + _st.pack("<II", 0, 0))

    got = _ai._lnk_strings(_mini_lnk("C:\\App\\tool.exe,0"))
    check(".lnk unicode icon string parsed", got["icon"].endswith("tool.exe,0"))

    # (b) the official-mirror chain over a real local server
    pe = bytearray(b"MZ" + b"\x00" * 0x3C)
    pe[0x3C:0x40] = (0x40).to_bytes(4, "little")
    pe += b"PE\x00\x00" + b"\x00" * (64 * 1024)
    pe = bytes(pe)
    hits = {"block": 0, "good": 0}

    class _H(_hs.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/block.exe":
                hits["block"] += 1
                body = b"<html>blocked</html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif self.path == "/good.exe":
                hits["good"] += 1
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(pe)))
                self.end_headers()
                self.wfile.write(pe)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *a):
            pass

    _srv = _hs.ThreadingHTTPServer(("127.0.0.1", 0), _H)
    _port = _srv.server_address[1]
    _th.Thread(target=_srv.serve_forever, daemon=True).start()
    try:
        _tmp_dl = _tf.mkdtemp(prefix="su_selftest_dl_")
        _dl.set_custom_download_dir(_tmp_dl)
        _p = _download(f"http://127.0.0.1:{_port}/block.exe", "SelfTest App",
                       alt_urls=(f"http://127.0.0.1:{_port}/good.exe",))
        check("block-page primary -> alternate official host delivers",
              os.path.isfile(_p) and hits["block"] == 1 and hits["good"] == 1)
        try:
            _download(f"http://127.0.0.1:{_port}/block.exe", "SelfTest App2",
                      alt_urls=(f"http://127.0.0.1:{_port}/block2.exe",))
            check("all mirrors failing raises honestly", False)
        except RuntimeError as _e:
            check("all mirrors failing raises honestly",
                  "official locations" in str(_e))
        _dl.set_custom_download_dir(None)
        _shutil.rmtree(_tmp_dl, ignore_errors=True)
    finally:
        _srv.shutdown()

    print()
    if failures:
        print(f"SELF-TEST FAILED: {len(failures)} failure(s)")
        return 1
    print("Self-test: i18n (6 languages, live switching)")
    from app import i18n as _i18n
    import re as _re

    def _ph(s):
        return sorted(_re.findall(r"{([a-z_]+)}", s))

    _en_msgs = _i18n.messages_for("en")
    check("6 languages registered", len(_i18n.language_codes()) == 6)
    for _code in _i18n.language_codes():
        _msgs = _i18n.messages_for(_code)
        check(f"{_code}: exact key parity with en", set(_msgs) == set(_en_msgs))
        check(f"{_code}: exact placeholder parity with en",
              all(_ph(_en_msgs[k]) == _ph(_msgs[k]) for k in _en_msgs))
    check("unknown key falls back to the key itself",
          _i18n.tr("definitely.not.a.key") == "definitely.not.a.key")
    for _code in ("fa", "ar", "pt", "fr", "de"):
        _i18n.set_language(_code)
        check(f"{_code} translates btn.check_all",
              _i18n.tr("btn.check_all") != "Check for updates")
    _i18n.set_language("fa")
    check("fa is RTL", _i18n.is_rtl())
    _i18n.set_language("ar")
    check("ar is RTL", _i18n.is_rtl())
    _i18n.set_language("de")
    check("de is LTR", not _i18n.is_rtl())
    _i18n.set_language("en")

    print("SELF-TEST PASSED")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()

    from app.core import applog

    applog.install_crash_hook(show_dialog=True)

    # Qt binding compatibility (see app/qt_compat.py) - must run BEFORE
    # the first "from PySide6 ..." import below. Uses the real PySide6
    # when available; on Windows 7 / 32-bit builds it transparently maps
    # PySide6 imports onto PyQt5 5.15.
    from app import qt_compat

    qt_compat.install()

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # UI language (Settings > Appearance) - applied BEFORE any window is
    # created; right-to-left languages (fa/ar) flip the whole app.
    from app import i18n as i18n_pkg
    from app.ui import settings as ui_settings

    i18n_pkg.set_language(ui_settings.load_language())
    app.setLayoutDirection(
        Qt.RightToLeft if i18n_pkg.is_rtl() else Qt.LeftToRight)

    # Apply the user's saved base font size (Settings dialog)
    from app.ui import theme
    from app.ui.settings import load_font_pt

    font_pt = load_font_pt()
    if sys.platform == "win32":
        app.setFont(QFont("Segoe UI", font_pt))
    else:
        font = app.font()
        font.setPointSize(font_pt)
        app.setFont(font)

    from app.ui.main_window import MainWindow

    app.setStyleSheet(theme.build_qss(font_pt, rtl=i18n_pkg.is_rtl()))
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
