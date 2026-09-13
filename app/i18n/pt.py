"""Brazilian Portuguese strings - mirrors en.py 1:1 (self-test verifies parity)."""
from __future__ import annotations

MESSAGES = {
    # ------------------------------------------------------------- meta
    "app.name": "SoftUpdater",
    "win.title": "SoftUpdater - Verificador de atualizações",
    "bits.64": "64 bits",
    "bits.32": "32 bits",
    "win.summary_build": "{name} - {bits} - Build {build}",
    "win.summary_plain": "{name} - {bits}",
    "win.summary_dev": "{name} - {bits} - (prévia de desenvolvimento)",
    "win.nonwin": "SO não Windows",
    "win.unknown": "Windows (desconhecido)",

    # ---------------------------------------------------------- toolbar
    "search.placeholder": "Pesquisar aplicativos instalados...",
    "btn.refresh": "Atualizar aplicativos",
    "btn.open_dir": "Abrir pasta de downloads",
    "btn.settings": "Configurações",
    "btn.check_all": "Verificar atualizações",
    "btn.check_sel": "Verificar selecionados",
    "btn.download": "Baixar instaladores selecionados",
    "chk.open": "Abrir instaladores após o download",
    "btn.pause": "Pausar",
    "btn.resume": "Retomar",
    "btn.cancel": "Cancelar",
    "tip.refresh": "Reexamina a lista de aplicativos instalados",
    "tip.settings": "Altera o idioma, o tamanho da fonte e outras preferências",
    "tip.check_all": "Verifica cada aplicativo instalado em sua fonte oficial",
    "tip.check_sel": (
        "Reexamina primeiro o(s) aplicativo(s) selecionado(s) no registro "
        "(capturando versões alteradas por uma instalação recente) e depois "
        "os verifica nas fontes oficiais. Você também pode clicar com o "
        "botão direito em uma linha e escolher 'Reverificar este "
        "aplicativo'."),
    "tip.download": (
        "Os arquivos são salvos na sua pasta Downloads. Se a caixa à "
        "direita estiver marcada, cada instalador abre automaticamente "
        "quando o download dele termina, para você executar a atualização "
        "imediatamente."),
    "tip.open": (
        "Quando marcada, a janela do instalador abre sozinha assim que um "
        "download termina - basta seguir as etapas dela para atualizar o "
        "aplicativo. Os instaladores continuam sendo salvos na pasta "
        "Downloads. Depois que você concluir a instalação, o aplicativo é "
        "reverificado automaticamente."),
    "tip.pause": (
        "Pausa o download atual. Ao retomar, ele continua de onde parou "
        "- os dados já baixados não são perdidos."),
    "tip.cancel": "Cancela o download atual",

    # ----------------------------------------------------------- table
    "col.app": "Aplicativo",
    "col.pub": "Publicador",
    "col.installed": "Instalada",
    "col.latest": "Mais recente",
    "col.status": "Status",
    "col.source": "Fonte",

    # ---------------------------------------------------------- status
    "status.update": "Atualização disponível",
    "status.latest": "Atualizado",
    "status.no_installer": "Sem instalador para este SO",
    "status.vendor": "Gerenciado pelo fornecedor",
    "status.no_source": "Fonte não encontrada",
    "status.failed": "Falha na verificação",
    "status.pending": "Não verificado",
    "status.skipped": "Versão ignorada",
    "status.checking": "Verificando...",

    # -------------------------------------------------- status messages
    "msg.counts": "{total} aplicativos - {checked} verificados - {updates} atualizações",
    "msg.postinstall_updated": "{name} atualizado para {version} - agora está em dia ✓",
    "msg.postinstall_uptodate": "{name} está em dia agora ✓",
    "msg.ready": "Pronto.",
    "msg.found_apps": "Foram encontrados {n} aplicativos instalados.",
    "msg.checking_n": "Verificando {n} aplicativo(s) nas fontes oficiais...",
    "msg.select_first": "Selecione primeiro uma ou mais linhas.",
    "msg.done": "Concluído - {n} atualização(ões) disponível(is)",
    "msg.done_failed_tail": " - {n} verificação(ões) com falha",
    "msg.no_jobs": (
        "Nenhuma linha selecionada tem um instalador disponível para "
        "download. Execute uma verificação primeiro."),
    "msg.preparing_n": "Preparando {n} download(s)...",
    "msg.preparing_one": "Preparando download...",
    "msg.downloading_n": "Baixando {n} instalador(es)...",
    "msg.of_total": "de {total}",
    "msg.paused_row": "Pausado: {name}",
    "msg.dl_title_paused": "{name} - pausado",
    "msg.saved": "Salvo: {path}",
    "msg.saved_verified": "Salvo: {path} - verificado por SHA-256",
    "msg.after_install_open": (
        "O instalador foi aberto. Depois que você concluir a instalação, "
        "esta linha é reverificada automaticamente e passa a 'Atualizado'."),
    "msg.after_install": (
        "Depois que você instalar, esta linha é reverificada "
        "automaticamente e passa a 'Atualizado'."),
    "msg.dl_failed": "Falha no download de {name}: {info}",
    "msg.dl_finished": "Downloads concluídos - {ok} com sucesso",
    "msg.dl_finished_failed_tail": ", {n} com falha",
    "msg.dl_finished_files_tail": " Os arquivos estão em: {path}",
    "msg.dl_finished_none_tail": (
        " Nada foi salvo - os servidores oficiais não entregaram um "
        "instalador válido (consulte Abrir pasta de log nas Configurações "
        "para detalhes). Você pode clicar com o botão direito na linha e "
        "usar Abrir página oficial."),
    "msg.cancelling": "Cancelando o download...",
    "msg.could_not_open": "Não foi possível abrir o instalador: {err} - o arquivo está em: {path}",
    "msgbox.open_fail_text": (
        "O instalador foi salvo, mas o Windows não conseguiu abri-lo\n"
        "({err}).\n\n"
        "A pasta dele foi aberta para você - dê um duplo clique\n"
        "no arquivo lá:\n"
        "{path}"),
    "msg.updated_rechecking": (
        "{name} foi atualizado para {version} - reverificando "
        "automaticamente..."),
    "msg.auto_interval_on": "A reverificação automática a cada {hours} hora(s) está ativada.",
    "msg.hidden_restored": "Aplicativos ocultos restaurados - a lista foi reexaminada.",
    "msg.skipped_restored": (
        "Versões ignoradas restauradas - {n} atualização(ões) exibida(s) "
        "novamente."),
    "msg.hidden_one": "{name} ocultado. Restaure-o nas Configurações.",
    "msg.skip_done": (
        "A versão {version} de {name} foi ignorada. Versões mais novas "
        "ainda aparecerão."),
    "msg.unskip_done": (
        "A versão {version} de {name} volta a aparecer como atualização."),
    "msg.exported": "Exportados {n} aplicativo(s) para {file}",
    "msg.error": "Erro: {err}",
    "msgbox.error_text": "Algo deu errado:\n{err}",

    # ------------------------------------------------------ skip notes
    "note.skipped": (
        "Você ignorou a versão {version}. Restaure as versões ignoradas "
        "nas Configurações."),
    "msg.last_known_tail": "exibindo o último resultado conhecido.",

    # ---------------------------------------------------- context menu
    "menu.details": "Ver detalhes",
    "tip.menu.details": (
        "Versões, fonte, o link direto do instalador (copiável) e a "
        "explicação do verificador para este aplicativo."),
    "menu.recheck": "Reverificar este aplicativo",
    "tip.menu.recheck": (
        "Examina o registro para encontrar a versão ATUAL instalada deste "
        "aplicativo (por exemplo, logo depois de instalar uma atualização "
        "baixada) e a verifica na fonte oficial - apenas este aplicativo, "
        "não a lista."),
    "menu.download": "Baixar instalador",
    "menu.src": "Abrir página oficial",
    "menu.skip": "Ignorar esta versão ({version})",
    "menu.unskip": "Restaurar versão ({version})",
    "tip.menu.skip": (
        "Impede que ESTA versão apareça como atualização (uma mais nova "
        "ainda será oferecida). Restaure nas Configurações."),
    "tip.menu.unskip": "Mostra esta versão como atualização novamente.",
    "menu.hide": "Ocultar este aplicativo",
    "tip.menu.hide": (
        "Remove-o da lista (para ferramentas que você atualiza "
        "manualmente). É possível restaurar aplicativos ocultos nas "
        "Configurações."),

    # -------------------------------------------------- details dialog
    "det.title": "Detalhes - {name}",
    "det.publisher": "Publicador",
    "det.installed_version": "Versão instalada",
    "det.latest_version": "Versão mais recente",
    "det.status": "Status",
    "det.source": "Fonte",
    "det.size": "Tamanho do download",
    "det.arch": "Arquitetura",
    "det.sha": "SHA-256",
    "det.sha_ok": "publicado pela fonte (verificado após o download)",
    "det.sha_none": "não publicado pela fonte",
    "det.placeholder": "Execute uma verificação para resolver o link do instalador",
    "btn.copy": "Copiar link",
    "btn.open_page": "Abrir página oficial",
    "btn.close": "Fechar",

    # ------------------------------------------------------- tray/toast
    "tray.open": "Abrir SoftUpdater",
    "tray.check": "Verificar atualizações agora",
    "tray.quit": "Sair",
    "tray.tip_updates": "SoftUpdater - {n} atualização(ões) disponível(is)",
    "tray.tip_ok": "SoftUpdater - tudo atualizado",
    "toast.updates_body": (
        "{n} atualização(ões) disponível(is) - abra o SoftUpdater para "
        "baixá-las."),
    "toast.installed_title": "Atualização instalada",
    "toast.installed_body": "{name} agora está atualizado{tail}",
    "toast.installed_tail": " (versão {version})",

    # ---------------------------------------------------- export/import
    "fd.export_title": "Exportar lista de aplicativos",
    "fd.import_title": "Importar lista de aplicativos",
    "fd.choose_dir": "Escolher pasta de downloads",
    "msgbox.import_none_title": "Importar lista de aplicativos",
    "msgbox.import_none_text": (
        "Este arquivo não contém uma lista de aplicativos do SoftUpdater "
        "(exporte uma primeiro com 'Exportar lista de aplicativos')."),
    "rep.header": "A lista importada tem {n} aplicativo(s).",
    "rep.block": "{title} ({n}):",
    "rep.more": "...e mais {n}",
    "rep.row_update": "{name} (aqui: {here}, a exportação tinha: {export})",
    "rep.missing": "Ausente neste PC",
    "rep.need_update": "Atualização ainda disponível",
    "rep.up_to_date": "Já está atualizado aqui",
    "rep.plain": "Presente (sem informação de versão na exportação)",
    "rep.nothing": "Nada a relatar - a lista parece vazia.",

    # ------------------------------------------------- source labels
    "src.vendor": "Gerenciado pelo fornecedor",
    "src.winget": "Manifesto oficial do Winget",
    "src.github": "GitHub - {repo}",
    "src.github_auto": "GitHub (correspondência automática) - {repo}",
    "src.feed": "Feed oficial de versões",
    "src.website": "Site oficial",
    "src.mozilla": "Download oficial da Mozilla",
    "src.vlc": "Espelho oficial do VideoLAN",
    "src.edge": "Atualizações oficiais do Microsoft Edge",
    "src.discord": "Download oficial do Discord",
    "src.dl_server": "Servidor de download oficial",

    # -------------------------------------------------- checker notes
    "note.check_error": "Erro de verificação: {cls}",
    "note.init_error": "Erro de inicialização: {cls}",
    "note.unexpected_error": "Erro inesperado: {cls}",
    "note.no_source": (
        "Nenhuma fonte oficial encontrada para este aplicativo. Ele pode "
        "ser de código fechado ou muito nichado."),
    "note.latest": "Já está na versão mais recente.",
    "note.newer_than_latest": (
        "A versão instalada é mais nova que o último lançamento público."),
    "note.version_unknown": "Versão instalada desconhecida - verifique manualmente.",
    "note.rate_limited": "Limite de requisições da API do GitHub atingido - tente novamente mais tarde.",
    "note.no_winget_manifest": "Não existe manifesto winget para este pacote.",
    "note.winget_list_error": "Erro ao listar manifestos do winget (HTTP {code}).",
    "note.no_winget_versions": "O manifesto do winget não tem versões publicadas.",
    "note.winget_installer_missing": "O manifesto de instalador do winget não foi encontrado.",
    "note.winget_installer_error": "Erro no manifesto de instalador do winget (HTTP {code}).",
    "note.winget_no_arch": (
        "Nenhum instalador {arch} é publicado no manifesto oficial mais "
        "recente."),
    "note.repo_not_found": "Repositório ou versão mais recente não encontrado.",
    "note.github_error": "Erro da API do GitHub (HTTP {code}).",
    "note.auto_match_unrelated": (
        "O repositório de correspondência automática parece não "
        "relacionado (projeto mais antigo com nome parecido)."),
    "note.matched_by_name": (
        "Correspondente pelo nome - verifique o publicador antes de "
        "instalar."),
    "note.github_no_arch": (
        "Nenhum instalador do Windows para esta arquitetura na versão "
        "mais recente."),
    "note.feed_error": "Erro no feed de versões (HTTP {code}).",
    "note.feed_parse": "Não foi possível interpretar o feed de versões.",
    "note.vendor_arch_installer_missing": "O fabricante não publica um instalador para esta arquitetura.",
    "note.no_installer_url": "Nenhum URL de instalador publicado para esta arquitetura.",
    "note.vendor_page_error": "Erro na página do fornecedor (HTTP {code}).",
    "note.vendor_no_arch": (
        "Versão encontrada, mas sem instalador para esta arquitetura na "
        "página do fornecedor."),
    "note.vendor_latest_unknown": (
        "Não foi possível encontrar a versão mais recente na página do "
        "fornecedor."),
    "note.mozilla_feed_error": "Erro no feed de versões da Mozilla (HTTP {code}).",
    "note.mozilla_parse": "Não foi possível interpretar o feed de versões da Mozilla.",
    "note.vlc_server_error": "Erro no servidor do VideoLAN (HTTP {code}).",
    "note.vlc_no_installer": "Nenhum instalador encontrado no espelho do VideoLAN.",
    "note.edge_feed_error": "Erro no feed de atualizações do Microsoft Edge (HTTP {code}).",
    "note.edge_no_stable": "Nenhum lançamento estável encontrado para esta arquitetura.",
    "note.discord_no_version": (
        "Instalador estável mais recente (versão não divulgada pelo "
        "Discord)."),
    "note.dl_server_error": "Erro no servidor de download (HTTP {code}).",
    "note.dl_list_error": "Não foi possível listar as pastas de lançamentos.",
    "note.blender_64bit_only": "O Blender publica apenas instaladores de 64 bits.",
    "note.no_windows_installer_folder": (
        "Nenhum instalador do Windows na pasta da versão mais recente."),

    # ---------------------------------------------- downloader errors
    "dlerr.http": "O servidor retornou HTTP {code}.",
    "dlerr.cancelled": "Download cancelado.",
    "dlerr.no_url": "Nenhum URL de download fornecido.",
    "dlerr.give_up": (
        "O download não pôde ser concluído ({err}) após várias tentativas "
        "- nada foi salvo. Verifique a conexão e tente novamente, ou use "
        "Abrir página oficial para baixá-lo você mesmo."),
    "dlerr.sha_mismatch": (
        "Checksum SHA-256 não confere - o arquivo baixado não "
        "correspondeu ao checksum oficial e foi excluído."),
    "dlerr.not_installer": (
        "O download não chegou como um instalador válido (veio uma página "
        "de erro ou de bloqueio no lugar) - ele foi excluído. Tente "
        "novamente, ou use Abrir página oficial para baixá-lo você mesmo."),
    "dlerr.final_validation": (
        "O instalador salvo falhou na validação final e foi excluído "
        "- tente baixar novamente."),
    "dlerr.all_locations": (
        "O download falhou em todos os {n} locais oficiais (último erro: "
        "{err}). Nada foi salvo - verifique a conexão e tente novamente, "
        "ou use Abrir página oficial para baixá-lo você mesmo."),
    "dlerr.failed_one": (
        "O download não pôde ser concluído ({err}) - nada foi salvo. "
        "Verifique a conexão e tente novamente, ou use Abrir página "
        "oficial para baixá-lo você mesmo."),

    # ------------------------------------------- catalog variant notes
    "vn.calibre": (
        "Se nenhum instalador estiver anexado à versão, baixe em "
        "calibre-ebook.com."),
    "vn.telegram": "Lançamentos oficiais do Telegram Desktop (tdesktop).",
    "vn.vscode": "Serviço de atualização oficial do VS Code.",
    "vn.winterminal": "Abra o .msixbundle com o App Installer.",
    "vn.ffmpeg": "Binários compilados automaticamente por BtbN (builds padrão da comunidade).",
    "vn.inkscape": (
        "Repositório espelho oficial; se nenhum instalador for publicado, "
        "baixe em inkscape.org."),
    "vn.winrar_x86": "O WinRAR 7 é publicado apenas para Windows de 64 bits.",
    "vn.winrar": "Página oficial de lançamentos do WinRAR (rarlab.com).",
    "vn.nekobox": "Lançamento oficial do NekoBox for PC (nekoray).",
    "vn.qtum": "O Qtum publica binários de instalação do Windows não assinados.",

    # --------------------------------------------- blocked-app reasons
    "blk.steam": "O Steam se atualiza pelo próprio cliente.",
    "blk.epic": "O Epic Games Launcher se atualiza sozinho.",
    "blk.battlenet": "O Battle.net se atualiza sozinho.",
    "blk.gog": "O GOG Galaxy se atualiza sozinho.",
    "blk.ubisoft": "O Ubisoft Connect se atualiza sozinho.",
    "blk.ea_app": "O EA app se atualiza sozinho.",
    "blk.origin": "O EA/Origin se atualiza sozinho.",
    "blk.office": "O Office é atualizado pelo Microsoft Click-to-Run.",
    "blk.m365": "O Microsoft 365 é atualizado automaticamente.",
    "blk.onedrive": "O OneDrive é atualizado automaticamente via Microsoft Update.",
    "blk.dropbox": "O Dropbox se atualiza silenciosamente.",
    "blk.gdrive": "O Google Drive se atualiza sozinho.",
    "blk.spotify": "O Spotify se atualiza silenciosamente.",
    "blk.whatsapp": "O WhatsApp é atualizado pela Microsoft Store.",
    "blk.teams": "O Teams se atualiza automaticamente.",
    "blk.slack": "O Slack se atualiza automaticamente.",
    "blk.zoom": "O Zoom se atualiza automaticamente.",
    "blk.teamviewer": "O TeamViewer se atualiza automaticamente.",
    "blk.anydesk": "O AnyDesk se atualiza automaticamente.",
    "blk.opera": "O Opera é atualizado pelo próprio atualizador.",
    "blk.vivaldi": "O Vivaldi é atualizado pelo próprio atualizador.",
    "blk.adobe": "Os aplicativos Adobe são atualizados pelo Creative Cloud / atualizador do Acrobat.",
    "blk.nvidia": "Os drivers de GPU são atualizados pelo GeForce Experience / NVIDIA App.",
    "blk.amd": "Os drivers da AMD são atualizados pelo AMD Software.",
    "blk.malwarebytes": "O Malwarebytes se atualiza automaticamente.",
    "blk.kaspersky": "O antivírus se atualiza automaticamente.",
    "blk.avast": "O Avast se atualiza automaticamente.",
    "blk.avg": "O AVG se atualiza automaticamente.",
    "blk.bitdefender": "O Bitdefender se atualiza automaticamente.",
    "blk.webview2": "O WebView2 Runtime é atualizado via Microsoft Update.",
    "blk.termius": "O Termius se atualiza automaticamente.",
    "blk.afterburner": "O MSI Afterburner é atualizado via seu próprio atualizador / msi.com.",
    "blk.rivatuner": "O RivaTuner vem com o MSI Afterburner; atualize pelo msi.com.",
    "blk.potplayer": "O PotPlayer se atualiza sozinho; instaladores em potplayer.daum.net.",
    "blk.windscribe": "O Windscribe se atualiza automaticamente.",
    "blk.fdm": "O FDM se atualiza sozinho; instaladores em freedownloadmanager.com.",
    "blk.capcut": "O CapCut se atualiza automaticamente.",
    "blk.canva": "O Canva se atualiza automaticamente.",
    "blk.bluestacks": "O BlueStacks se atualiza automaticamente.",
    "blk.ldplayer": "O LDPlayer se atualiza automaticamente.",
    "blk.driver_booster": "O Driver Booster é atualizado pelo atualizador da própria IObit.",
    "blk.iobit": "Os aplicativos da IObit são atualizados pelo atualizador deles.",
    "blk.allavsoft": "O Allavsoft não tem feed público de versões; confira allavsoft.com.",
    "blk.zdsoft": "Confira zdsoft.com para obter a versão mais recente do ZD Soft Screen Recorder.",
    "blk.officesuite": "O OfficeSuite se atualiza sozinho.",
    "blk.maxon": "Os aplicativos da Maxon são atualizados pelo Maxon App.",
    "blk.icue": "O Corsair iCUE se atualiza sozinho.",
    "blk.miniconda": "Atualize via 'conda update' ou com um novo instalador de anaconda.com.",
    "blk.python_launcher": "Instalado junto com o Python; é atualizado junto com o Python.",
    "blk.android_studio": "O Android Studio é atualizado pelo próprio atualizador.",
    "blk.java": "O Java é atualizado via Java Auto Update da Oracle; JDKs em oracle.com/java.",
    "blk.intel": "Os drivers/componentes da Intel são atualizados via Intel Driver & Support Assistant.",
    "blk.realtek": "Os drivers da Realtek são entregues pelo fabricante do seu PC ou da placa-mãe.",
    "blk.rapoo": "Os drivers de periféricos vêm de rapoo.com.",
    "blk.asus": "Os utilitários da ASUS são atualizados via Armoury Crate / MyASUS.",
    "blk.rog": "Os utilitários da ASUS ROG são atualizados via Armoury Crate / MyASUS.",
    "blk.armoury": "Os componentes do ASUS Armoury Crate são atualizados em conjunto.",
    "blk.aura": "Os componentes ASUS AURA são atualizados via Armoury Crate.",
    "blk.tap_windows": "O adaptador TAP é instalado com o OpenVPN; atualize o OpenVPN.",
    "blk.openvpn": "O OpenVPN é atualizado via openvpn.net; o OpenVPN Connect se atualiza sozinho.",
    "blk.maintenance_service": "Instalado com o Firefox; é atualizado junto com o Firefox.",
    "blk.vcredist": "Os Redistribuíveis do VC++ são instalados por instaladores de aplicativos; a versão mais recente está em aka.ms/vsredist.",
    "blk.dotnet": "Os componentes do .NET são instalados por instaladores de aplicativos ou pelo Visual Studio.",
    "blk.ms_windows": "Componente do sistema Windows - atualizado via Windows Update.",
    "blk.winsdk": "O Windows SDK é atualizado junto com o Visual Studio.",
    "blk.xna": "Componente legado do Microsoft XNA; não é mais atualizado.",
    "blk.vb": "Runtime VB legado; instalado por instaladores de aplicativos.",
    "blk.update_health": "Componente do sistema atualizado via Windows Update.",
    "blk.visio": "O Visio é atualizado com o Microsoft Office (Click-to-Run).",
    "blk.project": "O Project é atualizado com o Microsoft Office (Click-to-Run).",
    "blk.powerpoint": "O PowerPoint é atualizado com o Microsoft Office.",
    "blk.word": "O Word é atualizado com o Microsoft Office.",
    "blk.excel": "O Excel é atualizado com o Microsoft Office.",
    "blk.outlook": "O Outlook é atualizado com o Microsoft Office.",
    "blk.access": "O Access é atualizado com o Microsoft Office.",
    "blk.onenote": "O OneNote é atualizado com o Microsoft Office.",
    "blk.publisher": "O Publisher é atualizado com o Microsoft Office.",
    "blk.visual_studio": "Os componentes do Visual Studio são atualizados via Visual Studio Installer.",

    # ------------------------------------------------------ settings
    "set.title": "Configurações",
    "set.nav.checking": "Verificação",
    "set.nav.downloads": "Downloads",
    "set.nav.apps": "Aplicativos",
    "set.nav.backup": "Backup",
    "set.nav.appearance": "Aparência",
    "set.header.checking": "Verificação",
    "set.header.downloads": "Downloads",
    "set.header.apps": "Aplicativos",
    "set.header.backup": "Backup e manutenção",
    "set.header.appearance": "Aparência",
    "set.nav.about": "Sobre",
    "set.header.about": "Sobre o SoftUpdater",
    "set.about.tagline": "Verifique seus aplicativos instalados junto às fontes oficiais - grátis e de código aberto.",
    "set.about.version": "Versão",
    "set.about.dev": "Desenvolvedor",
    "set.about.source": "Código oficial no GitHub",
    "set.about.license": "Publicado sob a Licença MIT - livre para usar, estudar, modificar e compartilhar.",
    "set.about.official": "Baixe o SoftUpdater sempre apenas do repositório oficial:",
    "set.chk_auto": "Verificar atualizações quando o aplicativo iniciar",
    "tip.set.chk_auto": (
        "Executa uma verificação completa de atualizações sozinho logo "
        "depois que o aplicativo abre, para você ver a lista de "
        "atualizações sem clicar em nada."),
    "set.lbl_interval": "Reverificar automaticamente a cada",
    "set.cmb_never": "Nunca",
    "set.cmb_hours": "{n} hora(s)",
    "tip.set.interval": (
        "Executa uma verificação completa sozinho enquanto o aplicativo "
        "estiver aberto, mesmo quando você não estiver usando. Atualizações "
        "encontradas geram uma notificação."),
    "set.chk_notify": "Mostrar uma notificação quando atualizações forem encontradas",
    "tip.set.notify": (
        "Notificação do Windows sobre novas atualizações após uma "
        "verificação automática (na inicialização ou programada). "
        "Verificações manuais nunca o interrompem."),
    "set.hint.checking": (
        "As verificações automáticas cobrem todos os aplicativos em suas "
        "fontes oficiais (os resultados ficam em cache, então as "
        "repetições são rápidas)."),
    "set.lbl_save_to": "Salvar instaladores em",
    "set.btn.browse": "Procurar...",
    "set.btn.reset_dir": "Usar pasta padrão",
    "tip.set.reset_dir": "Volta para Downloads\\SoftUpdater",
    "set.dl_default": "Downloads\\SoftUpdater (padrão)",
    "set.hint.downloads": (
        "Escolha onde os instaladores baixados são salvos. O padrão é a "
        "pasta SoftUpdater dentro dos seus Downloads."),
    "set.btn.restore_hidden": "Restaurar aplicativos ocultos",
    "tip.set.restore_hidden": (
        "Restaura todos os aplicativos que você ocultou pelo menu de "
        "botão direito e reexamina a lista."),
    "set.lbl_hidden_n": "{n} aplicativo(s) ocultado(s) da lista",
    "set.lbl_hidden_none": "Nada está oculto",
    "set.btn.restore_skip": "Restaurar versões ignoradas",
    "tip.set.restore_skip": (
        "Faz as versões ignoradas voltarem a aparecer como atualizações "
        "(elas foram ocultadas com a ação 'Ignorar esta versão' do botão "
        "direito)."),
    "set.lbl_skip_n": "{n} versão(ões) ignorada(s)",
    "set.lbl_skip_none": "Nenhuma versão ignorada",
    "set.hint.apps": (
        "Oculte um aplicativo clicando com o botão direito na linha dele "
        "na janela principal (útil para ferramentas que você atualiza "
        "manualmente). Uma única versão pode ser ignorada da mesma forma."),
    "set.btn.export": "Exportar lista de aplicativos...",
    "tip.set.export": (
        "Salva todos os aplicativos listados com as versões deles em um "
        "arquivo JSON - um pequeno backup do que este PC tinha instalado."),
    "set.btn.import": "Importar lista de aplicativos...",
    "tip.set.import": (
        "Compara uma lista exportada anteriormente com o que está "
        "instalado neste PC e informa o que está ausente ou precisa de "
        "atualização."),
    "set.btn.log": "Abrir pasta de log",
    "tip.set.log": (
        "O aplicativo grava um pequeno log de verificações, downloads e "
        "erros - útil quando algo precisa ser relatado."),
    "set.hint.backup": (
        "O arquivo de exportação é uma lista JSON simples - nada é enviado "
        "para lugar nenhum."),
    "set.lbl_font": "Tamanho da fonte",
    "set.pt_suffix": " pt",
    "set.btn.reset_font": "Restaurar fonte padrão",
    "tip.set.reset_font": "Devolve o tamanho da fonte para {default} pt",
    "set.hint.appearance": (
        "Escolha um tamanho - a amostra abaixo mostra-o. Todo o aplicativo "
        "muda ao premir Concluir, e fica guardado para a próxima vez."),
    "set.lbl_preview": "Pré-visualização",
    "set.font.sample": (
        "Este é um texto de exemplo para pré-visualizar o tamanho da "
        "fonte - Aa 123"),
    "set.btn.done": "Concluir",
    "set.lbl_language": "Idioma",
    "set.hint.language": (
        "Aplicado instantaneamente - todas as janelas mudam sem reiniciar."),
    "set.btn.tour": "Mostrar o tour rápido novamente",
    "tip.set.tour": (
        "Reapresenta as dicas da primeira execução (sua escolha de 'não "
        "mostrar novamente' é mantida)."),

    # ----------------------------------------------------- onboarding
    "ob.title": "Tour rápido do SoftUpdater",
    "ob.page_of": "Página {n} de {total}",
    "ob.btn.next": "Avançar",
    "ob.btn.back": "Voltar",
    "ob.btn.skip": "Pular tour",
    "ob.btn.finish": "Começar",
    "ob.chk.never": "Não mostrar estas dicas novamente",
    "ob.welcome.title": "Boas-vindas ao SoftUpdater",
    "ob.welcome.body": (
        "O SoftUpdater verifica seus aplicativos instalados em suas "
        "fontes oficiais e baixa os instaladores mais recentes para você "
        "- com segurança, com verificação SHA-256.\n\n"
        "Comece pelo grande botão verde: Verificar atualizações."),
    "ob.ctx.title": "Clique com o botão direito em qualquer linha",
    "ob.ctx.body": (
        "O menu de botão direito em cada linha de aplicativo guarda os "
        "recursos avançados:\n"
        "- Ver detalhes (versões, fonte, link do instalador)\n"
        "- Reverificar apenas esse aplicativo\n"
        "- Baixar o instalador / abrir a página oficial\n"
        "- Ignorar uma versão específica ou ocultar aplicativos que você "
        "mesmo atualiza"),
    "ob.dl.title": "Downloads que completam o trabalho",
    "ob.dl.body": (
        "Os instaladores são salvos em Downloads\\SoftUpdater. Eles podem "
        "abrir automaticamente após o download - e, depois que você "
        "instala uma atualização, a linha passa a 'Atualizado' sozinha."),
    "ob.done.title": "Deixe com a sua cara",
    "ob.done.body": (
        "As Configurações têm tudo: este aplicativo fala inglês, persa, "
        "árabe, português, francês e alemão (escrita da direita para a "
        "esquerda incluída), o tamanho da fonte se adapta aos seus olhos "
        "e as verificações automáticas seguem o seu horário. O SoftUpdater "
        "também fica na bandeja do sistema."),
}
