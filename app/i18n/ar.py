"""Arabic strings - mirrors en.py 1:1 (self-test verifies parity)."""
from __future__ import annotations

MESSAGES = {
    # ------------------------------------------------------------- meta
    "app.name": "SoftUpdater",
    "win.title": "SoftUpdater - أداة التحقق من التحديثات",
    "bits.64": "64 بت",
    "bits.32": "32 بت",
    "win.summary_build": "{name} - {bits} - الإصدار {build}",
    "win.summary_plain": "{name} - {bits}",
    "win.summary_dev": "{name} - {bits} - (معاينة تطوير)",
    "win.nonwin": "نظام غير ويندوز",
    "win.unknown": "ويندوز (غير معروف)",

    # ---------------------------------------------------------- toolbar
    "search.placeholder": "ابحث في التطبيقات المثبتة...",
    "btn.refresh": "إعادة فحص التطبيقات",
    "btn.open_dir": "فتح مجلد التنزيلات",
    "btn.settings": "الإعدادات",
    "btn.check_all": "التحقق من التحديثات",
    "btn.check_sel": "فحص المحدَّد",
    "btn.download": "تنزيل مثبّتات المحدَّد",
    "chk.open": "فتح المثبّتات بعد التنزيل",
    "btn.pause": "إيقاف مؤقت",
    "btn.resume": "استئناف",
    "btn.cancel": "إلغاء",
    "tip.refresh": "إعادة فحص قائمة التطبيقات المثبتة",
    "tip.settings": "تغيير اللغة وحجم الخط والتفضيلات الأخرى",
    "tip.check_all": "فحص كل تطبيق مثبَّت مقابل مصدره الرسمي",
    "tip.check_sel": (
        "يعيد أولًا فحص التطبيق (التطبيقات) المحددة من السجل (لالتقاط "
        "الإصدارات التي تغيّرت بعد تثبيت جديد)، ثم يفحصها مقابل مصادرها "
        "الرسمية. يمكنك أيضًا النقر بزر الفأرة الأيمن على أي صف واختيار "
        "«إعادة فحص هذا التطبيق»."),
    "tip.download": (
        "تُحفظ الملفات في مجلد التنزيلات (Downloads). إذا كان مربع "
        "الاختيار المجاور مفعّلًا، فسيفتح كل مثبّت تلقائيًا فور انتهاء "
        "تنزيله لتنفّذ التحديث في الحال."),
    "tip.open": (
        "عند التفعيل، تفتح نافذة المثبّت تلقائيًا فور انتهاء التنزيل - "
        "كل ما عليك هو اتباع خطواتها لتحديث التطبيق. تبقى المثبّتات محفوظة "
        "في مجلد Downloads. وبعد إتمام التثبيت يُعاد فحص التطبيق تلقائيًا."),
    "tip.pause": (
        "يوقف التنزيل الحالي مؤقتًا. الاستئناف يكمل من نقطة التوقف - "
        "البيانات المنزّلة لا تُفقد."),
    "tip.cancel": "إلغاء التنزيل الحالي",

    # ----------------------------------------------------------- table
    "col.app": "التطبيق",
    "col.pub": "الناشر",
    "col.installed": "المثبَّت",
    "col.latest": "الأحدث",
    "col.status": "الحالة",
    "col.source": "المصدر",

    # ---------------------------------------------------------- status
    "status.update": "يتوفر تحديث",
    "status.latest": "محدَّث",
    "status.no_installer": "لا مثبّت لهذا النظام",
    "status.vendor": "التحديث عبر الشركة المطوّرة",
    "status.no_source": "لم يُعثر على مصدر",
    "status.failed": "فشل الفحص",
    "status.pending": "لم يُفحص",
    "status.skipped": "نسخة متجاوزة",
    "status.checking": "جارٍ الفحص...",

    # -------------------------------------------------- status messages
    "msg.counts": "{total} تطبيقًا - {checked} مفحوصًا - {updates} تحديثًا",
    "msg.postinstall_updated": "تحديث {name} إلى {version} - أصبح محدَّثًا الآن ✓",
    "msg.postinstall_uptodate": "أصبح {name} محدَّثًا الآن ✓",
    "msg.ready": "جاهز.",
    "msg.found_apps": "عُثر على {n} تطبيق مثبَّت.",
    "msg.checking_n": "جارٍ فحص {n} تطبيقًا مقابل المصادر الرسمية...",
    "msg.select_first": "حدّد صفًّا واحدًا أو أكثر أولًا.",
    "msg.done": "تم - {n} تحديثًا متاحًا",
    "msg.done_failed_tail": " - فشل {n} فحصًا",
    "msg.no_jobs": (
        "لا يملك أي صف من المحدَّد مثبّتًا قابلًا للتنزيل. شغّل فحصًا أولًا."),
    "msg.preparing_n": "جارٍ تجهيز {n} تنزيلًا...",
    "msg.preparing_one": "جارٍ تجهيز التنزيل...",
    "msg.downloading_n": "جارٍ تنزيل {n} مثبّتًا...",
    "msg.of_total": "من {total}",
    "msg.paused_row": "توقف مؤقت: {name}",
    "msg.dl_title_paused": "{name} - متوقف مؤقتًا",
    "msg.saved": "حُفظ: {path}",
    "msg.saved_verified": "حُفظ: {path} - تم التحقق من SHA-256",
    "msg.after_install_open": (
        "فُتح المثبّت. بعد إتمامك التثبيت، يُعاد فحص هذا الصف تلقائيًا "
        "ويتحول إلى «محدَّث»."),
    "msg.after_install": (
        "بعد تثبيته، يُعاد فحص هذا الصف تلقائيًا ويتحول إلى «محدَّث»."),
    "msg.dl_failed": "فشل تنزيل {name}: {info}",
    "msg.dl_finished": "انتهت التنزيلات - نجح {ok}",
    "msg.dl_finished_failed_tail": "، فشل {n}",
    "msg.dl_finished_files_tail": " الملفات في: {path}",
    "msg.dl_finished_none_tail": (
        " لم يُحفظ شيء - تعذّر على الخوادم الرسمية تقديم مثبّت صالح "
        "(للتفاصيل: «فتح مجلد السجل» في الإعدادات). يمكنك النقر بزر "
        "الفأرة الأيمن على الصف واستخدام «فتح الصفحة الرسمية» بدلًا من ذلك."),
    "msg.cancelling": "جارٍ إلغاء التنزيل...",
    "msg.could_not_open": "تعذّر فتح المثبّت: {err} - الملف موجود في: {path}",
    "msgbox.open_fail_text": (
        "حُفظ المثبّت لكن ويندوز تعذّر عليه فتحه\n"
        "({err}).\n\nفُتح مجلده لك - انقر نقرًا مزدوجًا على الملف\n"
        "هناك:\n{path}"),
    "msg.updated_rechecking": (
        "تحديث {name} إلى {version} - يجري إعادة فحصه تلقائيًا..."),
    "msg.auto_interval_on": "الفحص التلقائي كل {hours} ساعة مفعّل.",
    "msg.hidden_restored": "عادت التطبيقات المخفية - أُعيد فحص القائمة.",
    "msg.skipped_restored": (
        "عادت النسخ المتجاوزة - يُعرض {n} تحديثًا من جديد."),
    "msg.hidden_one": "أُخفي {name}. استعده من الإعدادات.",
    "msg.skip_done": (
        "تجاوزت الإصدار {version} من {name}. ما زالت الإصدارات الأحدث "
        "تُعرض."),
    "msg.unskip_done": (
        "يُعرض الإصدار {version} من {name} من جديد كتحديث."),
    "msg.exported": "صُدِّر {n} تطبيقًا إلى {file}",
    "msg.error": "خطأ: {err}",
    "msgbox.error_text": "حدث خطأ ما:\n{err}",

    # ------------------------------------------------------ skip notes
    "note.skipped": (
        "تجاوزت الإصدار {version}. استعد النسخ المتجاوزة من الإعدادات."),
    "msg.last_known_tail": "يُعرض آخر نتيجة معروفة.",

    # ---------------------------------------------------- context menu
    "menu.details": "عرض التفاصيل",
    "tip.menu.details": (
        "الإصدارات والمصدر ورابط المثبّت المباشر (قابل النسخ) وشرح "
        "الفاحص لهذا التطبيق."),
    "menu.recheck": "إعادة فحص هذا التطبيق",
    "tip.menu.recheck": (
        "يفحص السجل عن الإصدار المثبَّت حاليًا لهذا التطبيق (مثلًا بعد "
        "تثبيت تحديث منزَّل مباشرة) ويفحصه مقابل مصدره الرسمي - هذا "
        "التطبيق فقط، لا القائمة كلها."),
    "menu.download": "تنزيل المثبّت",
    "menu.src": "فتح الصفحة الرسمية",
    "menu.skip": "تجاوز هذا الإصدار ({version})",
    "menu.unskip": "إلغاء تجاوز الإصدار ({version})",
    "tip.menu.skip": (
        "يمنع ظهور هذا الإصدار تحديدًا كتحديث (سيُعرض الأحدث منه). "
        "الاستعادة من الإعدادات."),
    "tip.menu.unskip": "يعرض هذا الإصدار من جديد كتحديث.",
    "menu.hide": "إخفاء هذا التطبيق",
    "tip.menu.hide": (
        "يزيله من القائمة (للأدوات التي تحدّثها بنفسك). يمكنك استعادة "
        "التطبيقات المخفية من الإعدادات."),

    # -------------------------------------------------- details dialog
    "det.title": "التفاصيل - {name}",
    "det.publisher": "الناشر",
    "det.installed_version": "الإصدار المثبَّت",
    "det.latest_version": "أحدث إصدار",
    "det.status": "الحالة",
    "det.source": "المصدر",
    "det.size": "حجم التنزيل",
    "det.arch": "المعمارية",
    "det.sha": "SHA-256",
    "det.sha_ok": "منشور من المصدر (يُتحقق منه بعد التنزيل)",
    "det.sha_none": "غير منشور من المصدر",
    "det.placeholder": "شغّل فحصًا لمعرفة رابط المثبّت",
    "btn.copy": "نسخ الرابط",
    "btn.open_page": "فتح الصفحة الرسمية",
    "btn.close": "إغلاق",

    # ------------------------------------------------------- tray/toast
    "tray.open": "فتح SoftUpdater",
    "tray.check": "تحقق من التحديثات الآن",
    "tray.quit": "خروج",
    "tray.tip_updates": "SoftUpdater - {n} تحديثًا متاحًا",
    "tray.tip_ok": "SoftUpdater - كل شيء محدَّث",
    "toast.updates_body": (
        "{n} تحديثًا متاحًا - افتح SoftUpdater لتنزيلها."),
    "toast.installed_title": "ثُبِّت التحديث",
    "toast.installed_body": "أصبح {name} محدَّثًا{tail}",
    "toast.installed_tail": " (الإصدار {version})",

    # ---------------------------------------------------- export/import
    "fd.export_title": "تصدير قائمة التطبيقات",
    "fd.import_title": "استيراد قائمة التطبيقات",
    "fd.choose_dir": "اختيار مجلد التنزيلات",
    "msgbox.import_none_title": "استيراد قائمة التطبيقات",
    "msgbox.import_none_text": (
        "لا يحتوي هذا الملف على قائمة تطبيقات SoftUpdater (صدّر واحدة "
        "أولًا عبر «تصدير قائمة التطبيقات»)."),
    "rep.header": "تحتوي القائمة المستوردة على {n} تطبيقًا.",
    "rep.block": "{title} ({n}):",
    "rep.more": "...و {n} أخرى",
    "rep.row_update": "{name} (هنا: {here}، في التصدير: {export})",
    "rep.missing": "غير موجود على هذا الحاسوب",
    "rep.need_update": "ما زال التحديث متاحًا",
    "rep.up_to_date": "محدَّث هنا أصلًا",
    "rep.plain": "موجود (لا معلومات إصدار في التصدير)",
    "rep.nothing": "لا شيء للتقرير - تبدو القائمة فارغة.",

    # ------------------------------------------------- source labels
    "src.vendor": "التحديث عبر الشركة المطوّرة",
    "src.winget": "بيان Winget الرسمي",
    "src.github": "GitHub - {repo}",
    "src.github_auto": "GitHub (مطابقة تلقائية) - {repo}",
    "src.feed": "تغذية الإصدارات الرسمية",
    "src.website": "الموقع الرسمي",
    "src.mozilla": "تنزيل Mozilla الرسمي",
    "src.vlc": "مرآة VideoLAN الرسمية",
    "src.edge": "تحديثات Microsoft Edge الرسمية",
    "src.discord": "تنزيل Discord الرسمي",
    "src.dl_server": "خادم التنزيل الرسمي",

    # -------------------------------------------------- checker notes
    "note.check_error": "خطأ فحص: {cls}",
    "note.init_error": "خطأ تهيئة: {cls}",
    "note.unexpected_error": "خطأ غير متوقع: {cls}",
    "note.no_source": (
        "لم يُعثر على مصدر رسمي لهذا التطبيق. ربما يكون مغلق المصدر أو "
        "قليل الانتشار."),
    "note.latest": "هو بالفعل على أحدث إصدار.",
    "note.newer_than_latest": "الإصدار المثبَّت أحدث من آخر إصدار عام.",
    "note.version_unknown": "الإصدار المثبَّت غير معروف - تحقق يدويًا.",
    "note.rate_limited": "بلغ الحد المسموح من GitHub API - حاول لاحقًا.",
    "note.no_winget_manifest": "لا يوجد بيان winget لهذه الحزمة.",
    "note.winget_list_error": "خطأ في سرد بيانات winget (HTTP {code}).",
    "note.no_winget_versions": "بيان winget لا يحتوي إصدارات منشورة.",
    "note.winget_installer_missing": "لم يُعثر على بيان مثبّت winget.",
    "note.winget_installer_error": "خطأ في بيان مثبّت winget (HTTP {code}).",
    "note.winget_no_arch": "لم يُنشر أي مثبّت {arch} في أحدث بيان رسمي.",
    "note.repo_not_found": "لم يُعثر على المستودع أو آخر إصدار.",
    "note.github_error": "خطأ في GitHub API (HTTP {code}).",
    "note.auto_match_unrelated": (
        "يبدو المستودع المطابق تلقائيًا غير ذي صلة (مشروع أقدم باسم "
        "مشابه)."),
    "note.matched_by_name": (
        "طوبق بالاسم - تحقق من الناشر قبل التثبيت."),
    "note.github_no_arch": "لا مثبّت ويندوز لهذه المعمارية في آخر إصدار.",
    "note.feed_error": "خطأ في تغذية الإصدارات (HTTP {code}).",
    "note.feed_parse": "تعذّر تحليل تغذية الإصدارات.",
    "note.vendor_arch_installer_missing": "لا تنشر الشركة المطوّرة مثبّتًا لهذه المعمارية.",
    "note.no_installer_url": "لم يُنشر رابط مثبّت لهذه المعمارية.",
    "note.vendor_page_error": "خطأ في صفحة الشركة المطوّرة (HTTP {code}).",
    "note.vendor_no_arch": (
        "وُجد الإصدار لكن لا مثبّت لهذه المعمارية في صفحة المطوّر."),
    "note.vendor_latest_unknown": "لم يُعثر على أحدث إصدار في صفحة المطوّر.",
    "note.mozilla_feed_error": "خطأ في تغذية إصدارات Mozilla (HTTP {code}).",
    "note.mozilla_parse": "تعذّر تحليل تغذية إصدارات Mozilla.",
    "note.vlc_server_error": "خطأ في خادم VideoLAN (HTTP {code}).",
    "note.vlc_no_installer": "لم يُعثر على مثبّت في مرآة VideoLAN.",
    "note.edge_feed_error": "خطأ في تغذية تحديثات Microsoft Edge (HTTP {code}).",
    "note.edge_no_stable": "لم يُعثر على إصدار مستقر لهذه المعمارية.",
    "note.discord_no_version": "أحدث مثبّت مستقر (Discord لا يكشف رقم الإصدار).",
    "note.dl_server_error": "خطأ في خادم التنزيل (HTTP {code}).",
    "note.dl_list_error": "تعذّرت قراءة قائمة مجلدات الإصدارات.",
    "note.blender_64bit_only": "ينشر Blender مثبّتات 64 بت فقط.",
    "note.no_windows_installer_folder": "لا مثبّت ويندوز في مجلد الإصدار الأحدث.",

    # ---------------------------------------------- downloader errors
    "dlerr.http": "أعاد الخادم HTTP {code}.",
    "dlerr.cancelled": "أُلغي التنزيل.",
    "dlerr.no_url": "لم يُقدَّم أي رابط تنزيل.",
    "dlerr.give_up": (
        "تعذّر إكمال التنزيل ({err}) بعد عدة محاولات - لم يُحفظ شيء. "
        "تحقق من الاتصال وحاول مجددًا، أو نزّله بنفسك عبر «فتح الصفحة "
        "الرسمية»."),
    "dlerr.sha_mismatch": (
        "عدم تطابق SHA-256 - الملف المنزَّل لا يطابق المجموع الاختباري "
        "الرسمي وحُذف."),
    "dlerr.not_installer": (
        "لم يصل التنزيل كمثبّت صالح (جاءت بدلًا منه صفحة خطأ أو حجب) - "
        "حُذف. حاول مجددًا، أو نزّله بنفسك عبر «فتح الصفحة الرسمية»."),
    "dlerr.final_validation": (
        "رُفض التحقق النهائي للمثبّت المحفوظ وحُذف - يرجى إعادة التنزيل."),
    "dlerr.all_locations": (
        "فشل التنزيل على جميع المواقع الرسمية الـ{n} (آخر خطأ: {err}). "
        "لم يُحفظ شيء - تحقق من الاتصال وحاول مجددًا، أو نزّله بنفسك عبر "
        "«فتح الصفحة الرسمية»."),
    "dlerr.failed_one": (
        "تعذّر إكمال التنزيل ({err}) - لم يُحفظ شيء. تحقق من الاتصال "
        "وحاول مجددًا، أو نزّله بنفسك عبر «فتح الصفحة الرسمية»."),

    # ------------------------------------------- catalog variant notes
    "vn.calibre": "إن لم يُرفق ملف مثبّت، نزّله من calibre-ebook.com.",
    "vn.telegram": "إصدارات Telegram Desktop الرسمية (tdesktop).",
    "vn.vscode": "خدمة تحديث VS Code الرسمية.",
    "vn.winterminal": "افتح ملف .msixbundle عبر App Installer.",
    "vn.ffmpeg": "ملفات ثنائية مبنية تلقائيًا من BtbN (بناء قياسي معتمد).",
    "vn.inkscape": (
        "مستودع مرآة رسمي؛ إن لم يُنشر مثبّت، نزّله من inkscape.org."),
    "vn.winrar_x86": "ينشر WinRAR 7 لويندوز 64 بت فقط.",
    "vn.winrar": "صفحة إصدارات WinRAR الرسمية (rarlab.com).",
    "vn.nekobox": "إصدار NekoBox for PC الرسمي (nekoray).",
    "vn.qtum": "ينشر Qtum ملفات تثبيت ويندوز غير موقَّعة.",

    # --------------------------------------------- blocked-app reasons
    "blk.steam": "يحدَّث Steam بنفسه عبر عميله الخاص.",
    "blk.epic": "يحدَّث Epic Games Launcher بنفسه.",
    "blk.battlenet": "يحدَّث Battle.net بنفسه.",
    "blk.gog": "يحدَّث GOG Galaxy بنفسه.",
    "blk.ubisoft": "يحدَّث Ubisoft Connect بنفسه.",
    "blk.ea_app": "يحدَّث تطبيق EA بنفسه.",
    "blk.origin": "يحدَّث EA/Origin بنفسه.",
    "blk.office": "يتحدّث Office عبر Microsoft Click-to-Run.",
    "blk.m365": "يتحدّث Microsoft 365 تلقائيًا.",
    "blk.onedrive": "يتحدّث OneDrive تلقائيًا عبر Microsoft Update.",
    "blk.dropbox": "يحدَّث Dropbox بنفسه بصمت.",
    "blk.gdrive": "يحدَّث Google Drive بنفسه.",
    "blk.spotify": "يحدَّث Spotify بنفسه بصمت.",
    "blk.whatsapp": "يتحدّث WhatsApp عبر متجر Microsoft.",
    "blk.teams": "يحدَّث Teams تلقائيًا.",
    "blk.slack": "يحدَّث Slack تلقائيًا.",
    "blk.zoom": "يحدَّث Zoom تلقائيًا.",
    "blk.teamviewer": "يحدَّث TeamViewer تلقائيًا.",
    "blk.anydesk": "يحدَّث AnyDesk تلقائيًا.",
    "blk.opera": "يتحدّث Opera عبر أداة التحديث الخاصة به.",
    "blk.vivaldi": "يتحدّث Vivaldi عبر أداة التحديث الخاصة به.",
    "blk.adobe": "تتحدّث تطبيقات Adobe عبر Creative Cloud / أداة تحديث Acrobat.",
    "blk.nvidia": "تتحدّث تعريفات كرت الشاشة عبر GeForce Experience / NVIDIA App.",
    "blk.amd": "تتحدّث تعريفات AMD عبر AMD Software.",
    "blk.malwarebytes": "يحدَّث Malwarebytes تلقائيًا.",
    "blk.kaspersky": "يحدَّث مضاد الفيروسات نفسه تلقائيًا.",
    "blk.avast": "يحدَّث Avast نفسه تلقائيًا.",
    "blk.avg": "يحدَّث AVG نفسه تلقائيًا.",
    "blk.bitdefender": "يحدَّث Bitdefender نفسه تلقائيًا.",
    "blk.webview2": "يتحدّث WebView2 Runtime عبر Microsoft Update.",
    "blk.termius": "يحدَّث Termius نفسه تلقائيًا.",
    "blk.afterburner": "يتحدّث MSI Afterburner عبر أداة تحديثه / msi.com.",
    "blk.rivatuner": "يأتي RivaTuner مع MSI Afterburner؛ حدِّثه من msi.com.",
    "blk.potplayer": "يحدَّث PotPlayer بنفسه؛ المثبّتات على potplayer.daum.net.",
    "blk.windscribe": "يحدَّث Windscribe نفسه تلقائيًا.",
    "blk.fdm": "يحدَّث FDM بنفسه؛ المثبّتات على freedownloadmanager.com.",
    "blk.capcut": "يحدَّث CapCut نفسه تلقائيًا.",
    "blk.canva": "يحدَّث Canva نفسه تلقائيًا.",
    "blk.bluestacks": "يحدَّث BlueStacks نفسه تلقائيًا.",
    "blk.ldplayer": "يحدَّث LDPlayer نفسه تلقائيًا.",
    "blk.driver_booster": "يتحدّث Driver Booster عبر أداة IObit الخاصة به.",
    "blk.iobit": "تتحدّث تطبيقات IObit عبر أداة التحديث الخاصة بها.",
    "blk.allavsoft": "لا تملك Allavsoft تغذية إصدارات عامة؛ راجع allavsoft.com.",
    "blk.zdsoft": "راجع zdsoft.com لأحدث إصدار من ZD Soft Screen Recorder.",
    "blk.officesuite": "يحدَّث OfficeSuite نفسه.",
    "blk.maxon": "تتحدّث تطبيقات Maxon عبر Maxon App.",
    "blk.icue": "يحدَّث Corsair iCUE نفسه.",
    "blk.miniconda": "حدِّثه عبر «conda update» أو مثبّت جديد من anaconda.com.",
    "blk.python_launcher": "يُثبَّت مع بايثون؛ يتحدّث معه.",
    "blk.android_studio": "يتحدّث Android Studio عبر أداة التحديث الخاصة به.",
    "blk.java": "يتحدّث جافا عبر Java Auto Update من أوراكل؛ حزم JDK من oracle.com/java.",
    "blk.intel": "تتحدّث تعريفات/مكونات إنتل عبر Intel Driver & Support Assistant.",
    "blk.realtek": "توفّر تعريفات Realtek من شركة حاسوبك أو اللوحة الأم.",
    "blk.rapoo": "تأتي تعريفات الملحقات من rapoo.com.",
    "blk.asus": "تتحدّث أدوات ASUS عبر Armoury Crate / MyASUS.",
    "blk.rog": "تتحدّث أدوات ASUS ROG عبر Armoury Crate / MyASUS.",
    "blk.armoury": "تتحدّث مكونات ASUS Armoury Crate معًا.",
    "blk.aura": "تتحدّث مكونات ASUS AURA عبر Armoury Crate.",
    "blk.tap_windows": "يُثبَّت محول TAP مع OpenVPN؛ حدِّث OpenVPN.",
    "blk.openvpn": "يتحدّث OpenVPN من openvpn.net؛ ويحدَّث OpenVPN Connect نفسه.",
    "blk.maintenance_service": "يُثبَّت مع فايرفوكس؛ يتحدّث معه.",
    "blk.vcredist": "تُثبّتها مثبّتات التطبيقات؛ الأحدث على aka.ms/vsredist.",
    "blk.dotnet": "تُثبّتها مثبّتات التطبيقات أو Visual Studio.",
    "blk.ms_windows": "مكوّن نظام ويندوز - يتحدّث عبر Windows Update.",
    "blk.winsdk": "يتحدّث Windows SDK مع Visual Studio.",
    "blk.xna": "مكوّن Microsoft XNA قديم؛ لم يعد يتحدّث.",
    "blk.vb": "وقت تشغيل VB قديم؛ تثبّته مثبّتات التطبيقات.",
    "blk.update_health": "مكوّن نظام يتحدّث عبر Windows Update.",
    "blk.visio": "يتحدّث Visio مع Microsoft Office (Click-to-Run).",
    "blk.project": "يتحدّث Project مع Microsoft Office (Click-to-Run).",
    "blk.powerpoint": "يتحدّث PowerPoint مع Microsoft Office.",
    "blk.word": "يتحدّث Word مع Microsoft Office.",
    "blk.excel": "يتحدّث Excel مع Microsoft Office.",
    "blk.outlook": "يتحدّث Outlook مع Microsoft Office.",
    "blk.access": "يتحدّث Access مع Microsoft Office.",
    "blk.onenote": "يتحدّث OneNote مع Microsoft Office.",
    "blk.publisher": "يتحدّث Publisher مع Microsoft Office.",
    "blk.visual_studio": "تتحدّث مكونات Visual Studio عبر Visual Studio Installer.",

    # ------------------------------------------------------ settings
    "set.title": "الإعدادات",
    "set.nav.checking": "الفحص",
    "set.nav.downloads": "التنزيلات",
    "set.nav.apps": "التطبيقات",
    "set.nav.backup": "النسخ الاحتياطي",
    "set.nav.appearance": "المظهر",
    "set.header.checking": "الفحص",
    "set.header.downloads": "التنزيلات",
    "set.header.apps": "التطبيقات",
    "set.header.backup": "النسخ الاحتياطي والصيانة",
    "set.header.appearance": "المظهر",
    "set.nav.about": "حول",
    "set.header.about": "حول SoftUpdater",
    "set.about.tagline": "تحقّق من تطبيقاتك المثبّتة عبر المصادر الرسمية - مجاني ومفتوح المصدر.",
    "set.about.version": "الإصدار",
    "set.about.dev": "المطوّر",
    "set.about.source": "الشيفرة الرسمية على GitHub",
    "set.about.license": "منشور تحت رخصة MIT - حرّ للاستخدام والدراسة والتعديل والمشاركة.",
    "set.about.official": "احصل على SoftUpdater دائماً من مستودعه الرسمي فقط:",
    "set.chk_auto": "التحقق من التحديثات عند بدء التطبيق",
    "tip.set.chk_auto": (
        "يشغّل فحصًا كاملًا بنفسه مباشرة بعد فتح التطبيق، لترى قائمة "
        "التحديثات دون أي نقرة."),
    "set.lbl_interval": "إعادة الفحص تلقائيًا كل",
    "set.cmb_never": "أبدًا",
    "set.cmb_hours": "{n} ساعة",
    "tip.set.interval": (
        "يشغّل فحصًا كاملًا بنفسه ما دام التطبيق مفتوحًا، حتى لو لم "
        "تلمسه. التحديثات التي يجدها تُصدر إشعارًا."),
    "set.chk_notify": "إظهار إشعار عند العثور على تحديثات",
    "tip.set.notify": (
        "إشعار ويندوز عن التحديثات الجديدة بعد الفحص التلقائي (عند "
        "البدء أو المجدول). الفحوصات اليدوية لا تقاطعك أبدًا."),
    "set.hint.checking": (
        "تغطي الفحوصات التلقائية كل تطبيق مقابل مصدره الرسمي (تُخزَّن "
        "النتائج مؤقتًا، فالتكرار سريع)."),
    "set.lbl_save_to": "حفظ المثبّتات في",
    "set.btn.browse": "استعراض...",
    "set.btn.reset_dir": "المجلد الافتراضي",
    "tip.set.reset_dir": "يعود إلى Downloads\\SoftUpdater",
    "set.dl_default": "Downloads\\SoftUpdater (افتراضي)",
    "set.hint.downloads": (
        "اختر مكان حفظ المثبّتات المنزَّلة. الافتراضي هو مجلد SoftUpdater "
        "داخل مجلد Downloads لديك."),
    "set.btn.restore_hidden": "استعادة التطبيقات المخفية",
    "tip.set.restore_hidden": (
        "يعيد كل تطبيق أخفيته بقائمة النقر الأيمن ويعيد فحص القائمة."),
    "set.lbl_hidden_n": "{n} تطبيقًا مخفيًا من القائمة",
    "set.lbl_hidden_none": "لا شيء مخفي",
    "set.btn.restore_skip": "استعادة النسخ المتجاوزة",
    "tip.set.restore_skip": (
        "يجعل النسخ المتجاوزة تُعرض من جديد كتحديثات (كانت مخفية عبر "
        "«تجاوز هذا الإصدار» بالنقر الأيمن)."),
    "set.lbl_skip_n": "{n} نسخة متجاوزة",
    "set.lbl_skip_none": "لا نسخ متجاوزة",
    "set.hint.apps": (
        "أخفِ تطبيقًا بالنقر الأيمن على صفه في النافذة الرئيسية (مفيد "
        "للأدوات التي تحدّثها بنفسك). ويمكن تجاوز إصدار واحد بنفس الطريقة."),
    "set.btn.export": "تصدير قائمة التطبيقات...",
    "tip.set.export": (
        "يحفظ كل تطبيق في القائمة بإصداراته في ملف JSON - نسخة احتياطية "
        "صغيرة لما كان مثبَّتًا على هذا الحاسوب."),
    "set.btn.import": "استيراد قائمة التطبيقات...",
    "tip.set.import": (
        "يقارن قائمة مصدَّرة سابقًا بما هو مثبَّت على هذا الحاسوب ويعرض "
        "ما هو ناقص أو يحتاج تحديثًا."),
    "set.btn.log": "فتح مجلد السجل",
    "tip.set.log": (
        "يكتب التطبيق سجلًا صغيرًا للفحوصات والتنزيلات والأخطاء - مفيد "
        "عند الحاجة إلى الإبلاغ عن مشكلة."),
    "set.hint.backup": (
        "ملف التصدير قائمة JSON بسيطة - لا يُرفع أي شيء إلى أي مكان."),
    "set.lbl_font": "حجم الخط",
    "set.pt_suffix": " pt",
    "set.btn.reset_font": "إعادة الخط إلى الافتراضي",
    "tip.set.reset_font": "يعيد حجم الخط إلى {default} pt",
    "set.hint.appearance": (
        "اختر الحجم هنا ليعرضه النموذج أدناه. يُطبَّق على التطبيق بالكامل "
        "عند الضغط على \"تم\" ويُحفظ للمرة القادمة."),
    "set.lbl_preview": "معاينة",
    "set.font.sample": (
        "هذا نص تجريبي لمعاينة حجم خط التطبيق - Aa 123"),
    "set.btn.done": "تم",
    "set.lbl_language": "لغة التطبيق",
    "set.hint.language": (
        "يُطبَّق فورًا - كل النوافذ تتبدل دون إعادة تشغيل."),
    "set.btn.tour": "إعادة عرض الجولة السريعة",
    "tip.set.tour": (
        "يعرض تلميحات التشغيل الأول من جديد (يبقى اختيار «لا تعرضها "
        "مرة أخرى» محفوظًا)."),

    # ----------------------------------------------------- onboarding
    "ob.title": "الجولة السريعة في SoftUpdater",
    "ob.page_of": "الصفحة {n} من {total}",
    "ob.btn.next": "التالي",
    "ob.btn.back": "السابق",
    "ob.btn.skip": "تخطي الجولة",
    "ob.btn.finish": "لنبدأ",
    "ob.chk.never": "لا تعرض هذه التلميحات مرة أخرى",
    "ob.welcome.title": "مرحبًا بك في SoftUpdater",
    "ob.welcome.body": (
        "يفحص SoftUpdater تطبيقاتك المثبَّتة مقابل مصادرها الرسمية وينزّل "
        "لك أحدث المثبّتات - بأمان وبالتحقق من SHA-256.\n\n"
        "ابدأ بالزر الأخضر الكبير: «التحقق من التحديثات»."),
    "ob.ctx.title": "انقر بزر الفأرة الأيمن على أي صف",
    "ob.ctx.body": (
        "قائمة النقر الأيمن على كل صف تضم الميزات القوية:\n"
        "- عرض التفاصيل (الإصدارات، المصدر، رابط المثبّت)\n"
        "- إعادة فحص هذا التطبيق وحده\n"
        "- تنزيل مثبّته / فتح صفحته الرسمية\n"
        "- تجاوز إصدار محدد، أو إخفاء تطبيقات تحدّثها بنفسك"),
    "ob.dl.title": "تنزيلات تُكمل المهمة",
    "ob.dl.body": (
        "تُحفظ المثبّتات في Downloads\\SoftUpdater. ويمكنها الفتح تلقائيًا "
        "بعد التنزيل - وحين تثبّت التحديث يتحول ذلك الصف بنفسه إلى "
        "«محدَّث»."),
    "ob.done.title": "اجعله على مقاسك",
    "ob.done.body": (
        "كل شيء في الإعدادات: يتحدث التطبيق بالإنجليزية والفارسية "
        "والعربية والبرتغالية والفرنسية والألمانية (مع دعم كامل للاتجاه "
        "من اليمين إلى اليسار)، ويتكيف حجم الخط مع عينك، وتعمل الفحوصات "
        "التلقائية وفق جدولك. يتواجد SoftUpdater أيضًا في منطقة الإعلام."),
}
