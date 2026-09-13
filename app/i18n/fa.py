"""Persian (Farsi) strings - mirrors en.py 1:1 (self-test verifies parity)."""
from __future__ import annotations

MESSAGES = {
    # ------------------------------------------------------------- meta
    "app.name": "SoftUpdater",
    "win.title": "SoftUpdater - بررسی به‌روزرسانی",
    "bits.64": "64 بیتی",
    "bits.32": "32 بیتی",
    "win.summary_build": "{name} - {bits} - بیلد {build}",
    "win.summary_plain": "{name} - {bits}",
    "win.summary_dev": "{name} - {bits} - (پیش‌نمایش توسعه)",
    "win.nonwin": "سیستمی غیر از ویندوز",
    "win.unknown": "ویندوز (نامشخص)",

    # ---------------------------------------------------------- toolbar
    "search.placeholder": "جستجوی برنامه‌های نصب‌شده...",
    "btn.refresh": "بازخوانی برنامه‌ها",
    "btn.open_dir": "باز کردن پوشه دانلود",
    "btn.settings": "تنظیمات",
    "btn.check_all": "بررسی به‌روزرسانی‌ها",
    "btn.check_sel": "بررسی موارد انتخاب‌شده",
    "btn.download": "دانلود نصاب‌های انتخاب‌شده",
    "chk.open": "باز کردن نصاب‌ها بعد از دانلود",
    "btn.pause": "توقف موقت",
    "btn.resume": "ادامه",
    "btn.cancel": "انصراف",
    "tip.refresh": "اسکن دوباره فهرست برنامه‌های نصب‌شده",
    "tip.settings": "تغییر زبان، اندازه فونت و سایر ترجیحات",
    "tip.check_all": "بررسی همه برنامه‌های نصب‌شده از منبع رسمی آن‌ها",
    "tip.check_sel": (
        "اول برنامه(های) انتخاب‌شده را دوباره از رجیستری اسکن می‌کند "
        "(نسخه‌های تغییرکرده بعد از نصب تازه را می‌گیرد) و بعد آن‌ها را "
        "از منابع رسمی‌شان بررسی می‌کند. همچنین می‌توانید روی یک ردیف "
        "راست‌کلیک کنید و «بررسی دوباره همین برنامه» را بزنید."),
    "tip.download": (
        "فایل‌ها در پوشه Downloads ذخیره می‌شوند. اگر چک‌باکس کناری فعال "
        "باشد، هر نصاب به محض پایان دانلود خودش باز می‌شود تا همان لحظه "
        "به‌روزرسانی را اجرا کنید."),
    "tip.open": (
        "وقتی فعال باشد، پنجره نصاب به محض پایان دانلود خودش باز می‌شود - "
        "شما فقط مراحلش را دنبال می‌کنید تا برنامه به‌روز شود. نصاب‌ها "
        "همچنان در پوشه Downloads ذخیره می‌شوند. بعد از پایان نصب، برنامه "
        "به‌صورت خودکار دوباره بررسی می‌شود."),
    "tip.pause": (
        "دانلود فعلی را موقتاً متوقف می‌کند. ادامه دادن از همان‌جا شروع "
        "می‌شود - داده‌های دانلودشده از دست نمی‌رود."),
    "tip.cancel": "لغو دانلود فعلی",

    # ----------------------------------------------------------- table
    "col.app": "برنامه",
    "col.pub": "انتشاردهنده",
    "col.installed": "نصب‌شده",
    "col.latest": "آخرین نسخه",
    "col.status": "وضعیت",
    "col.source": "منبع",

    # ---------------------------------------------------------- status
    "status.update": "به‌روزرسانی موجود است",
    "status.latest": "به‌روز است",
    "status.no_installer": "نصابی برای این سیستم منتشر نشده",
    "status.vendor": "به‌روزرسانی با سازنده",
    "status.no_source": "منبعی پیدا نشد",
    "status.failed": "بررسی شکست خورد",
    "status.pending": "بررسی نشده",
    "status.skipped": "نسخه رد شد",
    "status.checking": "در حال بررسی...",

    # -------------------------------------------------- status messages
    "msg.counts": "{total} برنامه - {checked} بررسی‌شده - {updates} به‌روزرسانی",
    "msg.postinstall_updated": "{name} به {version} به‌روز شد - حالا به‌روز است ✓",
    "msg.postinstall_uptodate": "{name} حالا به‌روز است ✓",
    "msg.ready": "آماده.",
    "msg.found_apps": "{n} برنامه نصب‌شده پیدا شد.",
    "msg.checking_n": "بررسی {n} برنامه از منابع رسمی...",
    "msg.select_first": "اول یک یا چند ردیف را انتخاب کنید.",
    "msg.done": "انجام شد - {n} به‌روزرسانی موجود است",
    "msg.done_failed_tail": " - {n} بررسی شکست خورد",
    "msg.no_jobs": (
        "هیچ‌کدام از ردیف‌های انتخاب‌شده نصاب قابل دانلود ندارند. اول یک "
        "بررسی اجرا کنید."),
    "msg.preparing_n": "آماده‌سازی {n} دانلود...",
    "msg.preparing_one": "آماده‌سازی دانلود...",
    "msg.downloading_n": "دانلود {n} نصاب...",
    "msg.of_total": "از {total}",
    "msg.paused_row": "متوقف شد: {name}",
    "msg.dl_title_paused": "{name} - متوقف",
    "msg.saved": "ذخیره شد: {path}",
    "msg.saved_verified": "ذخیره شد: {path} - SHA-256 تأیید شد",
    "msg.after_install_open": (
        "نصاب باز شد. بعد از اینکه نصب را تمام کنید، این ردیف خودکار دوباره "
        "بررسی می‌شود و «به‌روز است» می‌شود."),
    "msg.after_install": (
        "بعد از نصبش، این ردیف خودکار دوباره بررسی می‌شود و «به‌روز است» "
        "می‌شود."),
    "msg.dl_failed": "دانلود {name} شکست خورد: {info}",
    "msg.dl_finished": "دانلودها تمام شد - {ok} موفق",
    "msg.dl_finished_failed_tail": "، {n} شکست خورد",
    "msg.dl_finished_files_tail": " فایل‌ها اینجا هستند: {path}",
    "msg.dl_finished_none_tail": (
        " هیچ چیزی ذخیره نشد - سرورهای رسمی نتوانستند نصاب معتبری بدهند "
        "(جزئیات: «باز کردن پوشه لاگ» در تنظیمات). می‌توانید روی ردیف "
        "راست‌کلیک کنید و از «باز کردن صفحه رسمی» استفاده کنید."),
    "msg.cancelling": "در حال لغو دانلود...",
    "msg.could_not_open": "باز کردن نصاب ممکن نشد: {err} - فایل اینجاست: {path}",
    "msgbox.open_fail_text": (
        "نصاب ذخیره شد ولی ویندوز نتوانست آن را باز کند\n"
        "({err}).\n\nپوشه‌اش برایتان باز شد - فایل را همان‌جا\n"
        "دابل‌کلیک کنید:\n{path}"),
    "msg.updated_rechecking": (
        "{name} به {version} به‌روز شد - خودکار دوباره بررسی می‌شود..."),
    "msg.auto_interval_on": "بررسی خودکار هر {hours} ساعت روشن است.",
    "msg.hidden_restored": "برنامه‌های پنهان برگشتند - فهرست دوباره اسکن شد.",
    "msg.skipped_restored": (
        "نسخه‌های ردشده برگشتند - {n} به‌روزرسانی دوباره نمایش داده می‌شود."),
    "msg.hidden_one": "{name} پنهان شد. از تنظیمات برگردانید.",
    "msg.skip_done": (
        "نسخه {version} از {name} رد شد. نسخه‌های جدیدتر همچنان نشان "
        "داده می‌شوند."),
    "msg.unskip_done": (
        "نسخه {version} از {name} دوباره به‌عنوان به‌روزرسانی نشان داده "
        "می‌شود."),
    "msg.exported": "{n} برنامه در {file} خروجی گرفته شد",
    "msg.error": "خطا: {err}",
    "msgbox.error_text": "مشکلی پیش آمد:\n{err}",

    # ------------------------------------------------------ skip notes
    "note.skipped": (
        "نسخه {version} را رد کردید. نسخه‌های ردشده را در تنظیمات "
        "برگردانید."),
    "msg.last_known_tail": "آخرین نتیجه معتبر نمایش داده می‌شود.",

    # ---------------------------------------------------- context menu
    "menu.details": "مشاهده جزئیات",
    "tip.menu.details": (
        "نسخه‌ها، منبع، لینک مستقیم نصاب (قابل کپی) و توضیح بررسی‌کننده "
        "برای همین برنامه."),
    "menu.recheck": "بررسی دوباره همین برنامه",
    "tip.menu.recheck": (
        "نسخه فعلی نصب‌شده این برنامه را از رجیستری اسکن می‌کند (مثلاً "
        "درست بعد از نصب یک به‌روزرسانی دانلودشده) و آن را از منبع رسمی‌اش "
        "بررسی می‌کند - فقط همین برنامه، نه کل فهرست."),
    "menu.download": "دانلود نصاب",
    "menu.src": "باز کردن صفحه رسمی",
    "menu.skip": "رد کردن این نسخه ({version})",
    "menu.unskip": "برگرداندن نسخه ({version})",
    "tip.menu.skip": (
        "جلوی نمایش همین نسخه به‌عنوان به‌روزرسانی را می‌گیرد (نسخه "
        "جدیدتر همچنان پیشنهاد می‌شود). برگرداندن از تنظیمات."),
    "tip.menu.unskip": "این نسخه را دوباره به‌عنوان به‌روزرسانی نشان می‌دهد.",
    "menu.hide": "پنهان کردن این برنامه",
    "tip.menu.hide": (
        "از فهرست حذفش می‌کند (برای ابزارهایی که خودتان به‌روز می‌کنید). "
        "برنامه‌های پنهان را در تنظیمات می‌توانید برگردانید."),

    # -------------------------------------------------- details dialog
    "det.title": "جزئیات - {name}",
    "det.publisher": "انتشاردهنده",
    "det.installed_version": "نسخه نصب‌شده",
    "det.latest_version": "آخرین نسخه",
    "det.status": "وضعیت",
    "det.source": "منبع",
    "det.size": "حجم دانلود",
    "det.arch": "معماری",
    "det.sha": "SHA-256",
    "det.sha_ok": "توسط منبع منتشر شده (بعد از دانلود راستی‌آزمایی می‌شود)",
    "det.sha_none": "توسط منبع منتشر نشده",
    "det.placeholder": "برای پیدا شدن لینک نصاب، یک بررسی اجرا کنید",
    "btn.copy": "کپی لینک",
    "btn.open_page": "باز کردن صفحه رسمی",
    "btn.close": "بستن",

    # ------------------------------------------------------- tray/toast
    "tray.open": "باز کردن SoftUpdater",
    "tray.check": "همین حالا بررسی به‌روزرسانی",
    "tray.quit": "خروج",
    "tray.tip_updates": "SoftUpdater - {n} به‌روزرسانی موجود است",
    "tray.tip_ok": "SoftUpdater - همه‌چیز به‌روز است",
    "toast.updates_body": (
        "{n} به‌روزرسانی موجود است - برای دانلود، SoftUpdater را باز کنید."),
    "toast.installed_title": "به‌روزرسانی نصب شد",
    "toast.installed_body": "{name} حالا به‌روز است{tail}",
    "toast.installed_tail": " (نسخه {version})",

    # ---------------------------------------------------- export/import
    "fd.export_title": "خروجی گرفتن از فهرست برنامه‌ها",
    "fd.import_title": "ورود فهرست برنامه‌ها",
    "fd.choose_dir": "انتخاب پوشه دانلود",
    "msgbox.import_none_title": "ورود فهرست برنامه‌ها",
    "msgbox.import_none_text": (
        "این فایل فهرست برنامه‌های SoftUpdater را ندارد (اول با «خروجی "
        "گرفتن از فهرست برنامه‌ها» یک خروجی بسازید)."),
    "rep.header": "فهرست واردشده {n} برنامه دارد.",
    "rep.block": "{title} ({n}):",
    "rep.more": "...و {n} مورد دیگر",
    "rep.row_update": "{name} (اینجا: {here}، در خروجی: {export})",
    "rep.missing": "در این رایانه غایب است",
    "rep.need_update": "هنوز به‌روزرسانی دارد",
    "rep.up_to_date": "اینجا از قبل به‌روز است",
    "rep.plain": "موجود است (در خروجی نسخه‌ای نبود)",
    "rep.nothing": "چیزی برای گزارش نیست - فهرست خالی به نظر می‌رسد.",

    # ------------------------------------------------- source labels
    "src.vendor": "به‌روزرسانی با سازنده",
    "src.winget": "مانیفست رسمی Winget",
    "src.github": "GitHub - {repo}",
    "src.github_auto": "GitHub (تطبیق خودکار) - {repo}",
    "src.feed": "فید رسمی نسخه‌ها",
    "src.website": "وب‌سایت رسمی",
    "src.mozilla": "دانلود رسمی Mozilla",
    "src.vlc": "آینه رسمی VideoLAN",
    "src.edge": "به‌روزرسانی‌های رسمی Microsoft Edge",
    "src.discord": "دانلود رسمی Discord",
    "src.dl_server": "سرور رسمی دانلود",

    # -------------------------------------------------- checker notes
    "note.check_error": "خطای بررسی: {cls}",
    "note.init_error": "خطای راه‌اندازی: {cls}",
    "note.unexpected_error": "خطای غیرمنتظره: {cls}",
    "note.no_source": (
        "منبع رسمی برای این برنامه پیدا نشد. شاید متن‌بسته یا کم‌کاربرد "
        "باشد."),
    "note.latest": "همین حالا روی آخرین نسخه است.",
    "note.newer_than_latest": "نسخه نصب‌شده از آخرین انتشار عمومی جدیدتر است.",
    "note.version_unknown": "نسخه نصب‌شده نامشخص است - دستی راستی‌آزمایی کنید.",
    "note.rate_limited": "سقف GitHub API پر شد - بعداً دوباره امتحان کنید.",
    "note.no_winget_manifest": "برای این بسته مانیفست winget وجود ندارد.",
    "note.winget_list_error": "خطای فهرست مانیفست‌های winget (HTTP {code}).",
    "note.no_winget_versions": "مانیفست winget نسخه منتشرشده‌ای ندارد.",
    "note.winget_installer_missing": "مانیفست نصاب winget پیدا نشد.",
    "note.winget_installer_error": "خطای مانیفست نصاب winget (HTTP {code}).",
    "note.winget_no_arch": "هیچ نصابِ {arch} در آخرین مانیفست رسمی منتشر نشده است.",
    "note.repo_not_found": "مخزن یا آخرین انتشار پیدا نشد.",
    "note.github_error": "خطای GitHub API (HTTP {code}).",
    "note.auto_match_unrelated": (
        "مخزن تطبیق‌خودکار بی‌ربط به نظر می‌رسد (پروژه قدیمی‌تر با نامی "
        "مشابه)."),
    "note.matched_by_name": (
        "با نام تطبیق داده شد - قبل از نصب، سازنده را راستی‌آزمایی کنید."),
    "note.github_no_arch": "در آخرین انتشار، نصاب ویندوزی برای این معماری نیست.",
    "note.feed_error": "خطای فید نسخه‌ها (HTTP {code}).",
    "note.feed_parse": "فید نسخه‌ها قابل خواندن نبود.",
    "note.vendor_arch_installer_missing": "سازنده برای این معماری نصابی منتشر نمی‌کند.",
    "note.no_installer_url": "برای این معماری لینک نصابی منتشر نشده است.",
    "note.vendor_page_error": "خطای صفحه سازنده (HTTP {code}).",
    "note.vendor_no_arch": (
        "نسخه پیدا شد ولی روی صفحه سازنده نصابی برای این معماری نیست."),
    "note.vendor_latest_unknown": "آخرین نسخه روی صفحه سازنده پیدا نشد.",
    "note.mozilla_feed_error": "خطای فید نسخه Mozilla (HTTP {code}).",
    "note.mozilla_parse": "فید نسخه Mozilla قابل خواندن نبود.",
    "note.vlc_server_error": "خطای سرور VideoLAN (HTTP {code}).",
    "note.vlc_no_installer": "روی آینه VideoLAN نصابی پیدا نشد.",
    "note.edge_feed_error": "خطای فید به‌روزرسانی Microsoft Edge (HTTP {code}).",
    "note.edge_no_stable": "انتشار پایداری برای این معماری پیدا نشد.",
    "note.discord_no_version": "آخرین نصاب پایدار (Discord شماره نسخه را اعلام نمی‌کند).",
    "note.dl_server_error": "خطای سرور دانلود (HTTP {code}).",
    "note.dl_list_error": "فهرست پوشه‌های انتشار خوانده نشد.",
    "note.blender_64bit_only": "Blender فقط نصاب 64 بیتی منتشر می‌کند.",
    "note.no_windows_installer_folder": "در آخرین پوشه انتشار، نصاب ویندوزی نیست.",

    # ---------------------------------------------- downloader errors
    "dlerr.http": "سرور HTTP {code} برگرداند.",
    "dlerr.cancelled": "دانلود لغو شد.",
    "dlerr.no_url": "هیچ لینک دانلودی داده نشده است.",
    "dlerr.give_up": (
        "دانلود بعد از چند تلاش ({err}) کامل نشد - چیزی ذخیره نشد. اتصال "
        "را بررسی کنید و دوباره امتحان کنید، یا با «باز کردن صفحه رسمی» "
        "خودتان دانلودش کنید."),
    "dlerr.sha_mismatch": (
        "عدم تطابق SHA-256 - فایل دانلودشده با چک‌سام رسمی نمی‌خواند و "
        "حذف شد."),
    "dlerr.not_installer": (
        "دانلود یک نصاب معتبر نبود (به‌جایش صفحه خطا یا مسدودسازی آمده "
        "بود) - حذف شد. دوباره امتحان کنید یا با «باز کردن صفحه رسمی» "
        "خودتان دانلودش کنید."),
    "dlerr.final_validation": (
        "نصاب ذخیره‌شده اعتبارسنجی نهایی را رد کرد و حذف شد - لطفاً دوباره "
        "دانلود کنید."),
    "dlerr.all_locations": (
        "دانلود روی هر {n} آدرس رسمی شکست خورد (آخرین خطا: {err}). چیزی "
        "ذخیره نشد - اتصال را بررسی کنید و دوباره امتحان کنید، یا با «باز "
        "کردن صفحه رسمی» خودتان دانلودش کنید."),
    "dlerr.failed_one": (
        "دانلود کامل نشد ({err}) - چیزی ذخیره نشد. اتصال را بررسی کنید و "
        "دوباره امتحان کنید، یا با «باز کردن صفحه رسمی» خودتان دانلودش "
        "کنید."),

    # ------------------------------------------- catalog variant notes
    "vn.calibre": "اگر فایل نصاب ضمیمه نشده باشد، از calibre-ebook.com دانلود کنید.",
    "vn.telegram": "انتشارهای رسمی Telegram Desktop (tdesktop).",
    "vn.vscode": "سرویس رسمی به‌روزرسانی VS Code.",
    "vn.winterminal": "فایل .msixbundle را با App Installer باز کنید.",
    "vn.ffmpeg": "باینری‌های خودساز BtbN (بیلدهای استاندارد جامعه).",
    "vn.inkscape": (
        "مخزن آینه رسمی؛ اگر نصابی منتشر نشده باشد، از inkscape.org "
        "دانلود کنید."),
    "vn.winrar_x86": "WinRAR 7 فقط برای ویندوز 64 بیتی منتشر می‌شود.",
    "vn.winrar": "صفحه انتشار رسمی WinRAR (rarlab.com).",
    "vn.nekobox": "انتشار رسمی NekoBox for PC (nekoray).",
    "vn.qtum": "Qtum باینری‌های نصب ویندوز را بدون امضا منتشر می‌کند.",

    # --------------------------------------------- blocked-app reasons
    "blk.steam": "Steam خودش با کلاینت خودش به‌روز می‌شود.",
    "blk.epic": "Epic Games Launcher خودش را به‌روز می‌کند.",
    "blk.battlenet": "Battle.net خودش را به‌روز می‌کند.",
    "blk.gog": "GOG Galaxy خودش را به‌روز می‌کند.",
    "blk.ubisoft": "Ubisoft Connect خودش را به‌روز می‌کند.",
    "blk.ea_app": "برنامه EA خودش را به‌روز می‌کند.",
    "blk.origin": "EA/Origin خودش را به‌روز می‌کند.",
    "blk.office": "Office از طریق Microsoft Click-to-Run به‌روز می‌شود.",
    "blk.m365": "Microsoft 365 خودکار به‌روز می‌شود.",
    "blk.onedrive": "OneDrive خودکار از طریق Microsoft Update به‌روز می‌شود.",
    "blk.dropbox": "Dropbox بی‌صدا خودش را به‌روز می‌کند.",
    "blk.gdrive": "Google Drive خودش را به‌روز می‌کند.",
    "blk.spotify": "Spotify بی‌صدا خودش را به‌روز می‌کند.",
    "blk.whatsapp": "WhatsApp از طریق Microsoft Store به‌روز می‌شود.",
    "blk.teams": "Teams خودکار خودش را به‌روز می‌کند.",
    "blk.slack": "Slack خودکار خودش را به‌روز می‌کند.",
    "blk.zoom": "Zoom خودکار خودش را به‌روز می‌کند.",
    "blk.teamviewer": "TeamViewer خودکار خودش را به‌روز می‌کند.",
    "blk.anydesk": "AnyDesk خودکار خودش را به‌روز می‌کند.",
    "blk.opera": "Opera با به‌روزرسان خودش به‌روز می‌شود.",
    "blk.vivaldi": "Vivaldi با به‌روزرسان خودش به‌روز می‌شود.",
    "blk.adobe": "برنامه‌های Adobe از طریق Creative Cloud / به‌روزرسان Acrobat به‌روز می‌شوند.",
    "blk.nvidia": "درایورهای گرافیک از طریق GeForce Experience / NVIDIA App به‌روز می‌شوند.",
    "blk.amd": "درایورهای AMD از طریق AMD Software به‌روز می‌شوند.",
    "blk.malwarebytes": "Malwarebytes خودکار خودش را به‌روز می‌کند.",
    "blk.kaspersky": "آنتی‌ویروس خودکار خودش را به‌روز می‌کند.",
    "blk.avast": "Avast خودکار خودش را به‌روز می‌کند.",
    "blk.avg": "AVG خودکار خودش را به‌روز می‌کند.",
    "blk.bitdefender": "Bitdefender خودکار خودش را به‌روز می‌کند.",
    "blk.webview2": "WebView2 Runtime از طریق Microsoft Update به‌روز می‌شود.",
    "blk.termius": "Termius خودکار خودش را به‌روز می‌کند.",
    "blk.afterburner": "MSI Afterburner با به‌روزرسان خودش / msi.com به‌روز می‌شود.",
    "blk.rivatuner": "RivaTuner همراه MSI Afterburner می‌آید؛ از msi.com به‌روز کنید.",
    "blk.potplayer": "PotPlayer خودش را به‌روز می‌کند؛ نصاب‌ها در potplayer.daum.net هستند.",
    "blk.windscribe": "Windscribe خودکار خودش را به‌روز می‌کند.",
    "blk.fdm": "FDM خودش را به‌روز می‌کند؛ نصاب‌ها در freedownloadmanager.com هستند.",
    "blk.capcut": "CapCut خودکار خودش را به‌روز می‌کند.",
    "blk.canva": "Canva خودکار خودش را به‌روز می‌کند.",
    "blk.bluestacks": "BlueStacks خودکار خودش را به‌روز می‌کند.",
    "blk.ldplayer": "LDPlayer خودکار خودش را به‌روز می‌کند.",
    "blk.driver_booster": "Driver Booster با به‌روزرسان خود IObit به‌روز می‌شود.",
    "blk.iobit": "برنامه‌های IObit با به‌روزرسان خودشان به‌روز می‌شوند.",
    "blk.allavsoft": "Allavsoft فید عمومی نسخه ندارد؛ allavsoft.com را ببینید.",
    "blk.zdsoft": "آخرین ZD Soft Screen Recorder را از zdsoft.com بررسی کنید.",
    "blk.officesuite": "OfficeSuite خودش را به‌روز می‌کند.",
    "blk.maxon": "برنامه‌های Maxon از طریق Maxon App به‌روز می‌شوند.",
    "blk.icue": "Corsair iCUE خودش را به‌روز می‌کند.",
    "blk.miniconda": "با «conda update» یا نصاب جدید از anaconda.com به‌روز کنید.",
    "blk.python_launcher": "همراه پایتون نصب می‌شود؛ با پایتون به‌روز می‌شود.",
    "blk.android_studio": "Android Studio با به‌روزرسان خودش به‌روز می‌شود.",
    "blk.java": "جاوا با Java Auto Update اوراکل به‌روز می‌شود؛ JDKها از oracle.com/java.",
    "blk.intel": "درایور/قطعات اینتل از طریق Intel Driver & Support Assistant به‌روز می‌شوند.",
    "blk.realtek": "درایورهای Realtek را سازنده رایانه یا مادربرد شما می‌دهد.",
    "blk.rapoo": "درایورهای جانبی از rapoo.com می‌آیند.",
    "blk.asus": "ابزارهای ASUS از طریق Armoury Crate / MyASUS به‌روز می‌شوند.",
    "blk.rog": "ابزارهای ASUS ROG از طریق Armoury Crate / MyASUS به‌روز می‌شوند.",
    "blk.armoury": "قطعات ASUS Armoury Crate با هم به‌روز می‌شوند.",
    "blk.aura": "قطعات ASUS AURA از طریق Armoury Crate به‌روز می‌شوند.",
    "blk.tap_windows": "آداپتور TAP همراه OpenVPN نصب می‌شود؛ OpenVPN را به‌روز کنید.",
    "blk.openvpn": "OpenVPN از openvpn.net به‌روز می‌شود؛ OpenVPN Connect خودش را به‌روز می‌کند.",
    "blk.maintenance_service": "همراه فایرفاکس نصب می‌شود؛ با فایرفاکس به‌روز می‌شود.",
    "blk.vcredist": "VC++ Redistributable را نصاب‌های برنامه‌ها نصب می‌کنند؛ آخرین نسخه در aka.ms/vsredist.",
    "blk.dotnet": "قطعات .NET را نصاب‌های برنامه‌ها یا Visual Studio نصب می‌کنند.",
    "blk.ms_windows": "قطعه سیستمی ویندوز - با Windows Update به‌روز می‌شود.",
    "blk.winsdk": "Windows SDK با Visual Studio به‌روز می‌شود.",
    "blk.xna": "قطعه قدیمی Microsoft XNA؛ دیگر به‌روز نمی‌شود.",
    "blk.vb": "رانتایم قدیمی VB؛ نصاب‌های برنامه‌ها نصبش می‌کنند.",
    "blk.update_health": "قطعه سیستمی که با Windows Update به‌روز می‌شود.",
    "blk.visio": "Visio با Microsoft Office به‌روز می‌شود (Click-to-Run).",
    "blk.project": "Project با Microsoft Office به‌روز می‌شود (Click-to-Run).",
    "blk.powerpoint": "PowerPoint با Microsoft Office به‌روز می‌شود.",
    "blk.word": "Word با Microsoft Office به‌روز می‌شود.",
    "blk.excel": "Excel با Microsoft Office به‌روز می‌شود.",
    "blk.outlook": "Outlook با Microsoft Office به‌روز می‌شود.",
    "blk.access": "Access با Microsoft Office به‌روز می‌شود.",
    "blk.onenote": "OneNote با Microsoft Office به‌روز می‌شود.",
    "blk.publisher": "Publisher با Microsoft Office به‌روز می‌شود.",
    "blk.visual_studio": "قطعات Visual Studio از طریق Visual Studio Installer به‌روز می‌شوند.",

    # ------------------------------------------------------ settings
    "set.title": "تنظیمات",
    "set.nav.checking": "بررسی",
    "set.nav.downloads": "دانلود",
    "set.nav.apps": "برنامه‌ها",
    "set.nav.backup": "پشتیبان",
    "set.nav.appearance": "ظاهر",
    "set.header.checking": "بررسی",
    "set.header.downloads": "دانلود",
    "set.header.apps": "برنامه‌ها",
    "set.header.backup": "پشتیبان و نگهداشت",
    "set.header.appearance": "ظاهر",
    "set.nav.about": "درباره",
    "set.header.about": "درباره SoftUpdater",
    "set.about.tagline": "بررسی برنامه‌های نصب‌شده از منابع رسمی - رایگان و متن‌باز.",
    "set.about.version": "نسخه",
    "set.about.dev": "توسعه‌دهنده",
    "set.about.source": "کد رسمی در گیت‌هاب",
    "set.about.license": "تحت مجوز MIT منتشر شده - آزاد برای استفاده، مطالعه، تغییر و بازنشر.",
    "set.about.official": "همیشه SoftUpdater را فقط از مخزن رسمی آن دریافت کنید:",
    "set.chk_auto": "بررسی به‌روزرسانی موقع باز شدن برنامه",
    "tip.set.chk_auto": (
        "درست بعد از باز شدن برنامه، خودش یک بررسی کامل اجرا می‌کند تا "
        "بدون کلیک، فهرست به‌روزرسانی‌ها را ببینید."),
    "set.lbl_interval": "بررسی خودکار هر",
    "set.cmb_never": "هرگز",
    "set.cmb_hours": "{n} ساعت",
    "tip.set.interval": (
        "تا وقتی برنامه باز است، حتی اگر دست نزنید خودش بررسی کامل اجرا "
        "می‌کند. به‌روزرسانی‌های پیدا شده اعلان می‌دهند."),
    "set.chk_notify": "وقتی به‌روزرسانی پیدا شد اعلان نشان بده",
    "tip.set.notify": (
        "بعد از بررسی خودکار (موقع شروع یا زمان‌بندی‌شده) توست ویندوز "
        "درباره به‌روزرسانی‌های جدید می‌آید. بررسی‌های دستی هیچ‌وقت مزاحم "
        "نمی‌شوند."),
    "set.hint.checking": (
        "بررسی‌های خودکار همه برنامه‌ها را از منبع رسمی پوشش می‌دهند "
        "(نتیجه‌ها کش می‌شوند، پس تکرارها سریع‌اند)."),
    "set.lbl_save_to": "ذخیره نصاب‌ها در",
    "set.btn.browse": "مرور...",
    "set.btn.reset_dir": "پوشه پیش‌فرض",
    "tip.set.reset_dir": "به Downloads\\SoftUpdater برمی‌گردد",
    "set.dl_default": "Downloads\\SoftUpdater (پیش‌فرض)",
    "set.hint.downloads": (
        "محل ذخیره نصاب‌های دانلودشده را انتخاب کنید. پیش‌فرض، پوشه "
        "SoftUpdater داخل Downloads شماست."),
    "set.btn.restore_hidden": "برگرداندن برنامه‌های پنهان",
    "tip.set.restore_hidden": (
        "همه برنامه‌هایی که با منوی راست‌کلیک پنهان کرده بودید را "
        "برمی‌گرداند و فهرست را دوباره اسکن می‌کند."),
    "set.lbl_hidden_n": "{n} برنامه از فهرست پنهان شده",
    "set.lbl_hidden_none": "چیزی پنهان نشده است",
    "set.btn.restore_skip": "برگرداندن نسخه‌های ردشده",
    "tip.set.restore_skip": (
        "نسخه‌های ردشده دوباره به‌عنوان به‌روزرسانی نشان داده می‌شوند "
        "(با راست‌کلیک و «رد کردن این نسخه» پنهان شده بودند)."),
    "set.lbl_skip_n": "{n} نسخه ردشده",
    "set.lbl_skip_none": "نسخه ردشده‌ای نیست",
    "set.hint.apps": (
        "برنامه را با راست‌کلیک روی ردیفش در پنجره اصلی پنهان کنید "
        "(برای ابزارهایی که خودتان به‌روز می‌کنید). یک نسخه خاص هم به "
        "همین شکل قابل رد کردن است."),
    "set.btn.export": "خروجی از فهرست برنامه‌ها...",
    "tip.set.export": (
        "همه برنامه‌های فهرست با نسخه‌هایشان در یک فایل JSON ذخیره "
        "می‌شود - یک پشتیبان کوچک از نصب‌های این رایانه."),
    "set.btn.import": "ورود فهرست برنامه‌ها...",
    "tip.set.import": (
        "فهرست خروجی گرفته‌شده را با نصب‌های همین رایانه مقایسه می‌کند و "
        "گزارش می‌دهد چه چیزی غایب است یا به‌روزرسانی دارد."),
    "set.btn.log": "باز کردن پوشه لاگ",
    "tip.set.log": (
        "برنامه لاگ کوچکی از بررسی‌ها، دانلودها و خطاها می‌نویسد - برای "
        "گزارش مشکل به کار می‌آید."),
    "set.hint.backup": (
        "فایل خروجی یک فهرست ساده JSON است - هیچ چیزی جایی آپلود نمی‌شود."),
    "set.lbl_font": "اندازه فونت",
    "set.pt_suffix": " pt",
    "set.btn.reset_font": "برگرداندن فونت به پیش‌فرض",
    "tip.set.reset_font": "اندازه فونت را به {default} pt برمی‌گرداند",
    "set.hint.appearance": (
        "اندازه را اینجا انتخاب کنید تا نمونهٔ پایین همان اندازه را نشان "
        "دهد. با زدن «تمام» روی کل برنامه اعمال و برای دفعه بعد ذخیره "
        "می‌شود."),
    "set.lbl_preview": "پیش‌نمایش",
    "set.font.sample": (
        "این یک متن نمونه برای پیش‌نمایش اندازهٔ فونت برنامه است - Aa 123"),
    "set.btn.done": "تمام",
    "set.lbl_language": "زبان برنامه",
    "set.hint.language": (
        "فوراً اعمال می‌شود - همه پنجره‌ها بدون ری‌استارت عوض می‌شوند."),
    "set.btn.tour": "نمایش دوباره راهنمای سریع",
    "tip.set.tour": (
        "راهنمای اولین اجرا را دوباره نشان می‌دهد (انتخاب «دیگر نشان "
        "نده» حفظ می‌شود)."),

    # ----------------------------------------------------- onboarding
    "ob.title": "راهنمای سریع SoftUpdater",
    "ob.page_of": "صفحه {n} از {total}",
    "ob.btn.next": "بعدی",
    "ob.btn.back": "قبلی",
    "ob.btn.skip": "رد کردن راهنما",
    "ob.btn.finish": "شروع کنید",
    "ob.chk.never": "این راهنما دیگر نشان داده نشود",
    "ob.welcome.title": "به SoftUpdater خوش آمدید",
    "ob.welcome.body": (
        "SoftUpdater برنامه‌های نصب‌شده شما را از منابع رسمی‌شان بررسی "
        "می‌کند و آخرین نصاب‌ها را برایتان دانلود می‌کند - با خیال راحت "
        "و با راستی‌آزمایی SHA-256.\n\n"
        "با دکمه سبز بزرگ شروع کنید: «بررسی به‌روزرسانی‌ها»."),
    "ob.ctx.title": "روی هر ردیف راست‌کلیک کنید",
    "ob.ctx.body": (
        "منوی راست‌کلیک هر ردیف، قابلیت‌های اصلی را دارد:\n"
        "- مشاهده جزئیات (نسخه‌ها، منبع، لینک نصاب)\n"
        "- بررسی دوباره فقط همان برنامه\n"
        "- دانلود نصاب / باز کردن صفحه رسمی\n"
        "- رد کردن یک نسخه خاص، یا پنهان کردن برنامه‌هایی که خودتان "
        "به‌روز می‌کنید"),
    "ob.dl.title": "دانلودی که کار را تمام می‌کند",
    "ob.dl.body": (
        "نصاب‌ها در Downloads\\SoftUpdater ذخیره می‌شوند. می‌توانند بعد "
        "از دانلود خودکار باز شوند - و وقتی شما به‌روزرسانی را نصب کردید، "
        "همان ردیف خودش «به‌روز است» می‌شود."),
    "ob.done.title": "شخصی‌سازی کنید",
    "ob.done.body": (
        "همه‌چیز در تنظیمات است: این برنامه به انگلیسی، فارسی، عربی، "
        "پرتغالی، فرانسه و آلمانی صحبت می‌کند (راست‌به‌چپ هم کامل)، "
        "اندازه فونت با چشم شما تنظیم می‌شود و بررسی‌های خودکار طبق برنامه "
        "شما اجرا می‌شوند. SoftUpdater در system tray هم حاضر است."),
}
