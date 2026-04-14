import os
import sys

# ==========================================
# 1. CESTY K SOUBORŮM A MAGICKÉ FUNKCE
# ==========================================
def ziskej_appdata_cestu(nazev_souboru):
    appdata_cesta = os.getenv('APPDATA')
    moje_slozka = os.path.join(appdata_cesta, "LigoLAN") 
    os.makedirs(moje_slozka, exist_ok=True)
    return os.path.join(moje_slozka, nazev_souboru)

def ziskej_cestu(relativni_cesta):
    """Získá absolutní cestu k souboru, funguje pro čistý Python i Nuitku"""
    if hasattr(sys, '_MEIPASS'):
        zakladni_cesta = sys._MEIPASS
    elif "__compiled__" in globals():
        zakladni_cesta = os.path.dirname(__file__)
    else:
        zakladni_cesta = os.path.abspath(".")
    return os.path.join(zakladni_cesta, relativni_cesta)

# ==========================================
# 2. SÍŤOVÉ PORTY A ZÁKLADNÍ NASTAVENÍ
# ==========================================
UDP_PORT = 12345
TCP_PORT = 12346
VOICE_PORT = 12347

VERZE_PROGRAMU = "1.1"
URL_VERZE = "https://raw.githubusercontent.com/LigoLAN/LigoLAN/main/verze.txt" 
URL_STAZENI = "https://github.com/LigoLAN/LigoLAN/releases/latest"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SDILENA_SLOZKA = os.path.join(BASE_DIR, "LAN_Sdilení")

# ==========================================
# 3. ULOŽENÁ DATA (APPDATA)
# ==========================================
SOUBOR_HISTORIE = ziskej_appdata_cestu("lan_historie.txt")
SOUBOR_NICK = ziskej_appdata_cestu("lan_nick.txt")
SOUBOR_HRY = ziskej_appdata_cestu("lan_hry.txt")
SOUBOR_JAZYK = ziskej_appdata_cestu("lan_jazyk.txt")
SOUBOR_ID = ziskej_appdata_cestu("lan_id.txt")
SOUBOR_PARAMETRY = ziskej_appdata_cestu("lan_parametry.txt")
SOUBOR_MOTIVU = ziskej_appdata_cestu("lan_motiv.txt")

PREDNASTAVENE_IP = [f"192.168.0.{i}" for i in range(1, 255)]

# ==========================================
# 4. GRAFIKA A MOTIVY
# ==========================================
MOTIVY = {
    "Zelena": {"main": "#2ecc71", "hover": "#27ae60", "border": "#1d8348"},
    "Modra": {"main": "#3498db", "hover": "#2980b9", "border": "#1a5276"},
    "Fialova": {"main": "#9b59b6", "hover": "#8e44ad", "border": "#512e5f"},
    "Ruzova": {"main": "#e91e63", "hover": "#c2185b", "border": "#880e4f"},
    "Zluta": {"main": "#f1c40f", "hover": "#f39c12", "border": "#9c640c"},
    "Tyrkysova": {"main": "#00bcd4", "hover": "#0097a6", "border": "#006064"}
}

# ==========================================
# 5. DATABÁZE HER A PROCESŮ
# ==========================================
ZNAME_HRY = {
    "6112-6119": "Warcraft 3 / Reforged / D2",
    "47624": "Age of Empires II / HoMM 3",
    "2300-2310": "Age of Mythology",
    "27900": "C&C Generals / Zero Hour",
    "6120-6125": "Company of Heroes",
    "1119": "StarCraft II",
    "27015-27030": "CS 1.6 / CS:GO / L4D / Source",
    "27960": "Quake 3",
    "12203": "Medal of Honor: AA",
    "14567": "Battlefield 1942",
    "28960-28965": "Call of Duty 1/2/4",
    "2302-2305": "Arma 3 / Halo CE",
    "7777-7780": "Terraria / ARK / UT99",
    "25600-25605": "Serious Sam",
    "10480-10482": "SWAT 4",
    "25565": "Minecraft",
    "34197": "Factorio",
    "2456-2458": "Valheim",
    "28015": "Rust",
    "16261-16262": "Project Zomboid",
    "10999": "Don't Starve Together",
    "15000-15777": "Satisfactory",
    "27016": "Garry's Mod / Space Engineers",
    "1042": "Need for Speed",
    "23073": "FlatOut 2 / Soldat",
    "61111": "Farming Simulator",
    "2350": "TrackMania",
    "30120": "FiveM (GTA V)",
    "42750": "Titan Quest",
    "51215": "Grim Dawn",
    "9987": "TeamSpeak 3 Server",
    "33540": "Wreckfest"
}

ZNAME_PROCESY = {
    "Warcraft III.exe": "Warcraft 3 / Reforged", "D2R.exe": "Diablo II: Resurrected",
    "Torchlight2.exe": "Torchlight II", "Titan Quest.exe": "Titan Quest",
    "Grim Dawn.exe": "Grim Dawn", "csgo.exe": "CS:GO", "cs2.exe": "Counter-Strike 2",
    "hl.exe": "CS 1.6 / Half-Life", "hl2.exe": "Team Fortress 2 / GMod",
    "left4dead.exe": "Left 4 Dead", "left4dead2.exe": "Left 4 Dead 2",
    "mohaa.exe": "Medal of Honor: AA", "bf1942.exe": "Battlefield 1942",
    "bf2.exe": "Battlefield 2", "iw3mp.exe": "Call of Duty 4 (Multiplayer)",
    "iw2mp.exe": "Call of Duty 2 (Multiplayer)", "quake3.exe": "Quake 3 Arena",
    "UT2004.exe": "Unreal Tournament 2004", "UnrealTournament.exe": "Unreal Tournament 99",
    "SamHD.exe": "Serious Sam HD", "Sam2017.exe": "Serious Sam", "swat4.exe": "SWAT 4",
    "haloce.exe": "Halo: Combat Evolved", "arma3_x64.exe": "Arma 3", "arma3.exe": "Arma 3",
    "payday2_win32_release.exe": "Payday 2", "Borderlands.exe": "Borderlands",
    "Borderlands2.exe": "Borderlands 2", "Borderlands3.exe": "Borderlands 3",
    "minecraft.exe": "Minecraft", "valheim.exe": "Valheim", "Terraria.exe": "Terraria",
    "RustClient.exe": "Rust", "ProjectZomboid64.exe": "Project Zomboid",
    "dontstarve.exe": "Don't Starve Together", "FactoryGame-Win64-Shipping.exe": "Satisfactory",
    "TheForest.exe": "The Forest", "SpaceEngineers.exe": "Space Engineers",
    "ConanSandbox.exe": "Conan Exiles", "7DaysToDie.exe": "7 Days to Die",
    "ShooterGame.exe": "ARK: Survival Evolved", "Raft.exe": "Raft", "factorio.exe": "Factorio",
    "age2_x1.exe": "Age of Empires II", "AoE2DE_s.exe": "Age of Empires II: DE",
    "Heroes3.exe": "HoMM 3", "h3ota.exe": "HoMM 3: Horn of the Abyss",
    "starcraft.exe": "StarCraft", "SC2_x64.exe": "StarCraft II",
    "generals.exe": "C&C Generals / Zero Hour", "game.exe": "Red Alert 2",
    "ra2.exe": "Red Alert 2", "RelicCOH.exe": "Company of Heroes",
    "Stronghold Crusader.exe": "Stronghold Crusader", "CivilizationVI.exe": "Civilization VI",
    "stellaris.exe": "Stellaris", "eurotrucks2.exe": "Euro Truck Sim 2",
    "FarmingSimulator2022Game.exe": "Farming Simulator 22", "FlatOut2.exe": "FlatOut 2",
    "Wreckfest.exe": "Wreckfest", "speed2.exe": "NFS: Underground 2",
    "speed.exe": "NFS: Most Wanted", "TmForever.exe": "TrackMania Nations Forever",
    "revolt.exe": "Re-Volt", "Blur.exe": "Blur", "FiveM.exe": "FiveM (GTA V)",
    "RocketLeague.exe": "Rocket League", "Among Us.exe": "Among Us",
    "Overcooked2.exe": "Overcooked! 2", "Human.exe": "Human: Fall Flat",
    "FallGuys_client.exe": "Fall Guys", "Stardew Valley.exe": "Stardew Valley",
    "soldat.exe": "Soldat", "WA.exe": "Worms Armageddon", "Worms W.M.D.exe": "Worms W.M.D",
    "dota2.exe": "Dota 2"
}

# ==========================================
# 6. JAZYKOVÉ PŘEKLADY (TEXTY)
# ==========================================
TEXTY = {
    "lbl_nick": {"CZ": "Tvoje přezdívka:", "EN": "Your Nickname:"},
    "btn_firewall": {"CZ": "🛡️ Povolit komunikaci", "EN": "🛡️ Allow Comms"},
    "btn_firewall_vratit": {"CZ": "🧹 Vrátit změny", "EN": "🧹 Revert Changes"},
    "btn_firewall_rucne": {"CZ": "⚙️ Ruční oprava", "EN": "⚙️ Manual Fix"},
    "frame_ip": {"CZ": "Nastavení IP (Práva správce se vyžádají automaticky)", "EN": "IP Setup (Admin prompt automatic)"},
    "lbl_sitovy_adapter": {"CZ": "Síťový adaptér:", "EN": "Network Adapter:"},
    "lbl_nova_ip": {"CZ": "Nová IP:", "EN": "New IP:"},
    "lbl_maska": {"CZ": "Maska:", "EN": "Subnet Mask:"},
    "btn_nastavit_ip": {"CZ": "Nastavit IP přes program", "EN": "Set IP via App"},
    "btn_nastavit_rucne": {"CZ": "⚙️ Nastavit ručně ve Windows", "EN": "⚙️ Set Manually in Windows"},
    "frame_hraci_hlavni": {"CZ": "Sledování sítě a Herní Radar", "EN": "Network Monitor & Game Radar"},
    "btn_najit_hrace": {"CZ": "🔍 Automaticky najít hráče a hry v síti", "EN": "🔍 Auto-find players and games"},
    "lbl_nebo_rucne": {"CZ": "Nebo ručně:", "EN": "Or manually:"},
    "btn_pridat": {"CZ": "+ Přidat", "EN": "+ Add"},
    "tab_chat": {"CZ": "💬 Lokální Chat", "EN": "💬 Local Chat"},
    "tab_files": {"CZ": "📁 Sdílená LAN složka", "EN": "📁 Shared LAN Folder"},
    "tab_games": {"CZ": "🎮 Moje Hry", "EN": "🎮 My Games"},
    "tab_squad": {"CZ": "🎧 Voice Squad", "EN": "🎧 Voice Squad"},
    "btn_otevrit_slozku": {"CZ": "📂 Otevřít moji složku ve Windows", "EN": "📂 Open my folder in Windows"},
    "btn_stahnout_soubor": {"CZ": "⬇️ Stáhnout vybraný soubor k sobě", "EN": "⬇️ Download selected file"},
    "btn_add_game": {"CZ": "+ Přidat hru (.exe)", "EN": "+ Add Game (.exe)"},
    "btn_remove_game": {"CZ": "❌ Odebrat ze seznamu", "EN": "❌ Remove from list"},
    "btn_start_game": {"CZ": "▶️ SPUSTIT VYBRANOU HRU", "EN": "▶️ START SELECTED GAME"},
    "btn_about": {"CZ": "ℹ️ O programu", "EN": "ℹ️ About"},
    "btn_donate": {"CZ": "☕ Podpořit", "EN": "☕ Donate"},
    "btn_aktualizovat_ip": {"CZ": "🔄 Aktualizovat IP nahoře", "EN": "🔄 Refresh Top IP"},
    "btn_sound_on": {"CZ": "🔊 Zvuk: ZAP", "EN": "🔊 Sound: ON"},
    "btn_sound_off": {"CZ": "🔇 Zvuk: VYP", "EN": "🔇 Sound: OFF"},
    "btn_refresh_files": {"CZ": "🔄 Načíst soubory ostatních", "EN": "🔄 Load Others' Files"},
    "msg_ready": {"CZ": "Připraveno ke sdílení...", "EN": "Ready to share..."},
    "msg_pack_zip": {"CZ": "[SYSTÉM] Bleskově balím složku do ZIPu...", "EN": "[SYSTEM] Lightning packing folder into ZIP..."},
    "msg_send_req": {"CZ": "[SOUBOR] Žádost odeslána na", "EN": "[FILE] Request sent to"},
    "msg_sending": {"CZ": "Odesílám soubor...", "EN": "Sending file..."},
    "msg_downloading": {"CZ": "Stahuji soubor...", "EN": "Downloading file..."},
    "msg_unknown_size": {"CZ": "neznámá celková velikost", "EN": "unknown total size"},
    "msg_success_send": {"CZ": "✅ Úspěšně odesláno!", "EN": "✅ Successfully sent!"},
    "msg_success_down": {"CZ": "✅ Úspěšně staženo!", "EN": "✅ Successfully downloaded!"},
    "msg_error_send": {"CZ": "❌ Chyba při odesílání!", "EN": "❌ Error sending!"},
    "msg_error_down": {"CZ": "❌ Chyba při stahování!", "EN": "❌ Error downloading!"},
    "msg_ip_updated": {"CZ": "[SYSTÉM] IP adresa aktualizována podle", "EN": "[SYSTEM] IP address updated from"},
    "msg_lang_switched": {"CZ": "[SYSTÉM] Jazyk přepnut na:", "EN": "[SYSTEM] Language switched to:"},
    "msg_scan_start": {"CZ": "[SYSTÉM] Vystřeluji chytrou světlici do sítě...", "EN": "[SYSTEM] Firing smart flare into network..."},
    "msg_scan_done": {"CZ": "[SYSTÉM] Skenování dokončeno.", "EN": "[SYSTEM] Scanning complete."},
    "msg_player_removed": {"CZ": "[SYSTÉM] Hráč byl odebrán:", "EN": "[SYSTEM] Player removed:"},
    "msg_dir_req": {"CZ": "[SÍŤ] Odeslán dotaz na sdílené soubory ostatních...", "EN": "[NETWORK] Request sent for others' shared files..."},
    "win_priv_chat": {"CZ": "Soukromý Chat", "EN": "Private Chat"},
    "btn_send": {"CZ": "Odeslat 🚀", "EN": "Send 🚀"},
    "msg_you": {"CZ": "Ty", "EN": "You"},
    "msg_not_delivered": {"CZ": "[INFO] ⚠️ Zpráva odeslána, ale PC nepotvrdilo přijetí.", "EN": "[INFO] ⚠️ Message sent, but PC didn't confirm receipt."},
    "mb_send_folder_title": {"CZ": "Soukromé sdílení", "EN": "Private Sharing"},
    "mb_send_folder_text": {"CZ": "Chceš poslat celou SLOŽKU?\n\n(Klikni na NE pro jeden soubor)", "EN": "Do you want to send a whole FOLDER?\n\n(Click NO for a single file)"},
    "mb_receive_title": {"CZ": "Soukromý soubor", "EN": "Private File"},
    "mb_receive_text": {"CZ": "ti posílá:", "EN": "is sending you:"},
    "mb_accept": {"CZ": "Přijmout?", "EN": "Accept?"},
    "btn_file_player": {"CZ": "📁 Soubor", "EN": "📁 File"},
    "btn_chat_player": {"CZ": "Chat", "EN": "Chat"},
    "btn_auto_connect": {"CZ": "🔗 Připojit na LAN (Automaticky)", "EN": "🔗 Connect to LAN (Auto)"},
    "btn_adv_net": {"CZ": "⚙️ Pokročilé sítě", "EN": "⚙️ Adv. Network"},
    "lbl_connected": {"CZ": "Připojen", "EN": "Connected"},
    "lbl_hw_detect": {"CZ": "Zjišťuji hardware...", "EN": "Detecting hardware..."},
    "lbl_hw_fail": {"CZ": "⚙️ HW Info: Nedostupné (nainstaluj si přes příkazový řádek: pip install psutil)", "EN": "⚙️ HW Info: Unavailable (install via cmd: pip install psutil)"},
    "msg_no_adapter": {"CZ": "Nebyl nalezen žádný síťový adaptér (kabel)!", "EN": "No network adapter (cable) found!"},
    "msg_ip_fail": {"CZ": "Nepodařilo se najít volnou IP adresu. Zkus to ručně.", "EN": "Failed to find a free IP. Try manually."},
    "msg_ip_ready": {"CZ": "✅ JSI PŘIPRAVEN! TVOJE IP:", "EN": "✅ READY! YOUR IP:"},
    "msg_ip_conflict_title": {"CZ": "❌ Kolize IP adresy", "EN": "❌ IP Conflict"},
    "msg_ip_conflict_text": {"CZ": "Tuto IP adresu ({}) už v síti používá jiné zařízení (PC, mobil nebo router)!\n\nZvol prosím jiné číslo na konci (např. 11-50), ať nedojde ke zhroucení sítě.", "EN": "This IP address ({}) is already used by another device (PC, phone or router)!\n\nPlease choose a different number at the end (e.g. 11-50) to prevent network crashes."},
    "msg_fw_done": {"CZ": "Hotovo, Firewall propíchnut! Chat i přenos souborů jsou volné.", "EN": "Done! Firewall pierced! Chat and file transfers are free."},
    "msg_fw_clean": {"CZ": "Úklid hotov", "EN": "Cleanup done"},
    "msg_fw_clean_txt": {"CZ": "Pravidla smazána.", "EN": "Rules deleted."},
    "win_exit_title": {"CZ": "Ukončení LigoLAN", "EN": "Exit LigoLAN"},
    "win_exit_text": {"CZ": "Opravdu chceš ukončit LigoLAN?\n\nProgram nyní nekompromisně zamete stopy:\n1. Uzavře díry ve Windows Firewallu.\n2. Vrátí IP a DNS na automatiku (DHCP).", "EN": "Do you really want to exit LigoLAN?\n\nThe program will now automatically clean up:\n1. Close holes in Windows Firewall.\n2. Revert IP and DNS to automatic (DHCP)."},
    "lbl_game_name": {"CZ": "Název hry:", "EN": "Game Name:"},
    "lbl_game_port": {"CZ": "Síťový Port (Vyber z rolety NEBO napiš ručně):", "EN": "Network Port (Choose OR type manually):"},
    "btn_save": {"CZ": "Uložit ✔️", "EN": "Save ✔️"},
    "btn_cancel": {"CZ": "Zrušit ❌", "EN": "Cancel ❌"},
    "win_add_game": {"CZ": "Přidat novou hru", "EN": "Add New Game"},
    "msg_only_exe": {"CZ": "Do her můžeš přetáhnout pouze spustitelný soubor (.exe)!", "EN": "You can only drag and drop executable files (.exe) into games!"},
    "msg_copy_fail": {"CZ": "Nepodařilo se zkopírovat soubor: {}", "EN": "Failed to copy file: {}"},
    "btn_clear_folder": {"CZ": "🗑️ Vyčistit složku", "EN": "🗑️ Clear Folder"},
    "ph_rozhlas": {"CZ": "Napiš hromadnou zprávu...", "EN": "Type a broadcast message..."},
    "btn_rozhlas": {"CZ": "📢 Poslat všem", "EN": "📢 Broadcast"},
    "btn_copy_ip": {"CZ": "📋 Kopírovat IP", "EN": "📋 Copy IP"},
    "btn_tasks_show": {"CZ": "⬇️ Zobrazit probíhající úlohy", "EN": "⬇️ Show ongoing tasks"},
    "btn_tasks_hide": {"CZ": "⬆️ Skrýt probíhající úlohy", "EN": "⬆️ Hide ongoing tasks"},
    "msg_queued": {"CZ": "⏳ Čeká ve frontě", "EN": "⏳ Queued"},
    "lbl_theme": {"CZ": "Barevný motiv:", "EN": "Color Theme:"},
    "win_mods_title": {"CZ": "Mody a Parametry", "EN": "Mods & Parameters"},
    "lbl_edit_mods": {"CZ": "Upravit mody pro:", "EN": "Edit mods for:"},
    "btn_clear_mod": {"CZ": "❌ VYMAZAT MÓD (Spustit hru čistou)", "EN": "❌ CLEAR MOD (Run clean game)"},
    "btn_save_mods": {"CZ": "Uložit úpravy ✔️", "EN": "Save changes ✔️"},
    "title_error": {"CZ": "Chyba ❌", "EN": "Error ❌"},
    "title_warning": {"CZ": "Upozornění ⚠️", "EN": "Warning ⚠️"},
    "title_info": {"CZ": "Informace ℹ️", "EN": "Information ℹ️"},
    "fd_select_file": {"CZ": "Vyber soubor", "EN": "Select file"},
    "fd_select_folder": {"CZ": "Vyber složku k odeslání", "EN": "Select folder to send"},
    "status_app_off": {"CZ": "[Aplikace vypnuta]", "EN": "[App Closed]"},
    "status_fast_ok": {"CZ": "[LAN Bleskově OK]", "EN": "[LAN Lightning Fast]"},
    "log_started": {"CZ": "=== Aplikace spuštěna ===", "EN": "=== Application started ==="},
    "prog_packing": {"CZ": "Balím do ZIPu:", "EN": "Packing to ZIP:"},
    "prog_copying": {"CZ": "Kopíruji a balím:", "EN": "Copying & packing:"},
    "msg_down_start_title": {"CZ": "Stahování", "EN": "Downloading"},
    "msg_down_start_text": {"CZ": "Požadavek odeslán.\nSoubor '{}' se začne stahovat.", "EN": "Request sent.\nFile '{}' will start downloading."},
    "btn_mod": {"CZ": "⚙️ Mód", "EN": "⚙️ Mod"},
    "win_title_pc_code": {"CZ": "Kód PC", "EN": "PC Code"},
    "err_tcp_in_use_title": {"CZ": "Chyba spuštění", "EN": "Startup Error"},
    "err_tcp_in_use_text": {"CZ": "Program už běží (TCP port je obsazen)! Zavři ostatní instance LigoLAN.", "EN": "Program is already running (TCP port in use)! Close other LigoLAN instances."},
    "err_folder_open": {"CZ": "Nepodařilo se otevřít složku", "EN": "Failed to open folder"},
    "btn_copied": {"CZ": "Zkopírováno ✔️", "EN": "Copied ✔️"},
    "err_invalid_ip": {"CZ": "Neplatná IP adresa!", "EN": "Invalid IP address!"},
    "err_title": {"CZ": "Chyba", "EN": "Error"},
    "err_admin_title": {"CZ": "Chyba oprávnění", "EN": "Permission Error"},
    "msg_copy_title": {"CZ": "Kopírování", "EN": "Copied"},
    "task_done": {"CZ": "✅ Hotovo", "EN": "✅ Done"},
    "task_packed": {"CZ": "✅ Zabaleno", "EN": "✅ Packed"},
    "task_sent": {"CZ": "✅ Odesláno", "EN": "✅ Sent"},
    "task_down": {"CZ": "✅ Staženo", "EN": "✅ Downloaded"},
    "task_canceled": {"CZ": "❌ Zrušeno", "EN": "❌ Canceled"},
    "task_err_pack": {"CZ": "❌ Chyba balení", "EN": "❌ Packing error"},
    "task_err_copy": {"CZ": "❌ Chyba kopírování", "EN": "❌ Copy error"},
    "task_err_net": {"CZ": "❌ Chyba sítě", "EN": "❌ Network error"},
    "task_err_lost": {"CZ": "❌ Spojení ztraceno", "EN": "❌ Connection lost"},
    "task_err_drop": {"CZ": "❌ Výpadek:", "EN": "❌ Error:"},
    "task_canceling": {"CZ": "Ruším...", "EN": "Canceling..."},
    "btn_cancel_task": {"CZ": "Zrušit ❌", "EN": "Cancel ❌"},
    "btn_pause_task": {"CZ": "Pauza ⏸", "EN": "Pause ⏸"},
    "btn_resume_task": {"CZ": "Obnovit ▶", "EN": "Resume ▶"},
    "btn_retry_task": {"CZ": "Znovu ▶", "EN": "Retry ▶"},
    "prog_packing_short": {"CZ": "Balím", "EN": "Packing"},
    "prog_sending": {"CZ": "Odesílám", "EN": "Sending"},
    "prog_downloading": {"CZ": "Stahuji", "EN": "Downloading"},
    "prog_copying_short": {"CZ": "Kopíruji", "EN": "Copying"},
    "err_admin_denied": {"CZ": "Práva správce byla zamítnuta!", "EN": "Admin rights were denied!"},
    "lbl_gpu_detect": {"CZ": "Zjišťuji GPU...", "EN": "Detecting GPU..."},
    "lbl_ram_detect": {"CZ": "Zjišťuji RAM...", "EN": "Detecting RAM..."},
    "err_game_start": {"CZ": "Nepodařilo se spustit hru", "EN": "Failed to start game"},
    "msg_ip_success": {"CZ": "[SYSTÉM] IP úspěšně změněna na: {}", "EN": "[SYSTEM] IP successfully changed to: {}"},
    "msg_broadcast_me": {"CZ": "TY - ROZHLAS", "EN": "YOU - BROADCAST"},
    "err_disk_space": {"CZ": "Nemáš dostatek místa na disku pro {}!", "EN": "Not enough disk space for {}!"},
    "win_empty_squad": {"CZ": "Prázdný tým", "EN": "Empty Squad"},
    "win_big_squad": {"CZ": "Příliš velký tým", "EN": "Squad too big"},
    "msg_big_squad": {"CZ": "Maximální velikost týmu pro čistý zvuk je 6 hráčů (Ty + 5 dalších).\n\nOdškrtni pár lidí na radaru a zkus to znovu.", "EN": "Maximum squad size for clear audio is 6 players (You + 5 others).\n\nUncheck a few people and try again."},
    "lbl_my_folder": {"CZ": "MOJE SLOŽKA (TY)", "EN": "MY FOLDER (YOU)"},
    "lbl_files_count": {"CZ": "souborů", "EN": "files"},
    "lbl_players_count": {"CZ": "hráčů", "EN": "players"},
    "lbl_player_single": {"CZ": "hráč", "EN": "player"},
    "lbl_lobby": {"CZ": "💤 Lobby (Zevlují)", "EN": "💤 Lobby (Idle)"},
    "btn_hangup": {"CZ": "Zavěsit ❌", "EN": "Disconnect ❌"},
    "msg_radar_down": {"CZ": "[STAHAHUJE]", "EN": "[DOWNLOADING]"},
    "lbl_squad_info": {"CZ": "Zaškrtni hráče na radaru nahoře a vytvoř soukromý hlasový kanál!", "EN": "Check players on the radar above and create a private voice channel!"},
    "btn_create_squad": {"CZ": "🎧 Vytvořit Tým z vybraných hráčů", "EN": "🎧 Create Squad from selected"},
    "win_squad_title": {"CZ": "🎧 Týmový kanál (Squad):", "EN": "🎧 Squad Channel:"},
    "lbl_squad_comms": {"CZ": "🎙️ Soukromá Týmová Komunikace", "EN": "🎙️ Private Squad Comms"},
    "msg_squad_welcome": {"CZ": "[SYSTÉM] Vítej v týmu! Jsou tu s tebou:", "EN": "[SYSTEM] Welcome to the squad! With you:"},
    "btn_mic_on": {"CZ": "🎤 ZAPNOUT MIKROFON", "EN": "🎤 ENABLE MIC"},
    "btn_mic_active": {"CZ": "🔴 MIKROFON VYSÍLÁ", "EN": "🔴 MIC LIVE"},
    "btn_settings": {"CZ": "⚙️ Nastavení", "EN": "⚙️ Settings"},
    "ph_squad_chat": {"CZ": "Zpráva jen pro tým...", "EN": "Message to squad only..."},
    "msg_mic_connecting": {"CZ": "[SYSTÉM] Otevírám mikrofon a vysílám do týmu...", "EN": "[SYSTEM] Opening mic and transmitting to squad..."},
    "msg_mic_muted": {"CZ": "[SYSTÉM] Mikrofon ztlumen.", "EN": "[SYSTEM] Mic muted."},
    "msg_squad_joined": {"CZ": "[SYSTÉM] {} se připojil k vaší místnosti!", "EN": "[SYSTEM] {} joined your room!"},
    "msg_empty_squad": {"CZ": "Musíš na radaru zaškrtnout alespoň jednoho spoluhráče!", "EN": "You must select at least one teammate on the radar!"},
    "msg_pyaudio_err": {"CZ": "Pro hlasový chat si musíš nainstalovat knihovnu PyAudio!", "EN": "You must install the PyAudio library for voice chat!"},
    "msg_mic_err": {"CZ": "[CHYBA MIKROFONU]:", "EN": "[MIC ERROR]:"},
    "msg_voice_port_err": {"CZ": "[SÍŤOVÁ CHYBA] Zvukový port 12347 je již obsazen jiným programem!", "EN": "[NETWORK ERROR] Voice port 12347 is already in use by another program!"},
    "msg_ip_copied": {"CZ": "Tvoje IP adresa {} byla zkopírována do schránky!", "EN": "Your IP address {} has been copied to clipboard!"},
    "msg_select_file_first": {"CZ": "Musíš nejprve kliknutím vybrat soubor ze seznamu.", "EN": "You must first click to select a file from the list."},
    "msg_already_have_file": {"CZ": "Tento soubor už máš u sebe ve složce.", "EN": "You already have this file in your folder."},
    "msg_download_req_sent": {"CZ": "Požadavek odeslán.\nSoubor '{}' se za chvíli objeví ve tvé složce.", "EN": "Request sent.\nThe file '{}' will appear in your folder shortly."},
    "msg_admin_req": {"CZ": "Pro úpravu sítě jsou nutná práva správce!", "EN": "Admin rights are required to modify network!"},
    "lbl_auto_port": {"CZ": "AUTO (Automaticky detekovat port)", "EN": "AUTO (Detect port automatically)"},
    "lbl_launch_params": {"CZ": "Spouštěcí parametry (Vyber nebo napiš vlastní):", "EN": "Launch params (Choose or type your own):"},
    "msg_select_game_first": {"CZ": "Nejprve kliknutím vyber hru ze seznamu!", "EN": "First click to select a game from the list!"},
    "msg_game_not_found": {"CZ": "Soubor s hrou nebyl nalezen. Možná byl smazán nebo přesunut.", "EN": "Game file not found. It might have been deleted or moved."},
    "msg_admin_denied_game": {"CZ": "Práva správce byla zamítnuta! Hra se spustí, ale ostatní se pravděpodobně nebudou moci připojit kvůli Firewallu.", "EN": "Admin rights denied! The game will start, but others might not be able to connect due to Firewall."},
    "msg_game_started": {"CZ": "[LAUCHER] Hra spuštěna. Firewall otevřen. Pozvánka odeslána!", "EN": "[LAUNCHER] Game started. Firewall opened. Invite sent!"},
    "msg_radar_success": {"CZ": "[RADAR] Úspěch! {} běží na portu {}.", "EN": "[RADAR] Success! {} is running on port {}."},
    "msg_game_track": {"CZ": "[SYSTÉM] Sleduji hru {}... Čekám na otevření sítě (může to trvat i 20 vteřin).", "EN": "[SYSTEM] Tracking game {}... Waiting for network open (can take up to 20 seconds)."},
    "msg_invite_broadcast": {"CZ": "📢 🚀 PRÁVĚ ZAKLÁDÁM HRU: {}! Moje IP: {}", "EN": "📢 🚀 HOSTING GAME NOW: {}! My IP: {}"},
    "msg_invite_broadcast_port": {"CZ": "📢 🚀 PRÁVĚ ZAKLÁDÁM HRU: {} (Port: {})! Moje IP: {}", "EN": "📢 🚀 HOSTING GAME NOW: {} (Port: {})! My IP: {}"},
    "msg_detecting_net": {"CZ": "Zjišťuji síťové připojení... ⏳", "EN": "Detecting network connection... ⏳"},
    "msg_lan_detected": {"CZ": "[SYSTÉM] 🔌 Detekován LAN kabel! Automaticky na něj přepínám...", "EN": "[SYSTEM] 🔌 LAN cable detected! Switching automatically..."},
    "msg_net_outage": {"CZ": "[SYSTÉM] Výpadek! Přepojuji se na záložní síť: {}", "EN": "[SYSTEM] Outage! Switching to backup network: {}"},
    "msg_lan_router_ok": {"CZ": "🔌 LAN (ROUTER) PŘIPRAVEN!\nTVOJE IP: {}", "EN": "🔌 LAN (ROUTER) READY!\nYOUR IP: {}"},
    "msg_lan_direct_ok": {"CZ": "🔌 LAN (PŘÍMÁ) PŘIPRAVENA!\nTVOJE IP: {}", "EN": "🔌 LAN (DIRECT) READY!\nYOUR IP: {}"},
    "msg_wifi_ok": {"CZ": "📶 WI-FI PŘIPRAVENA!\nTVOJE IP: {}", "EN": "📶 WI-FI READY!\nYOUR IP: {}"}
}
