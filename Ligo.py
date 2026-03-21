import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
import customtkinter as ctk
import subprocess
import threading
import socket
import datetime
import ipaddress
import os
import winsound
import shutil
import time
import tempfile
import re
import zipfile
import platform
import base64
import concurrent.futures
import sys
import ctypes
import urllib.request
import webbrowser

def ziskej_appdata_cestu(nazev_souboru):
    appdata_cesta = os.getenv('APPDATA')
    # Změněno na LigoLAN
    moje_slozka = os.path.join(appdata_cesta, "LigoLAN") 
    os.makedirs(moje_slozka, exist_ok=True)
    return os.path.join(moje_slozka, nazev_souboru)

# --- NOVÁ MAGICKÁ FUNKCE ---
def ziskej_cestu(relativni_cesta):
    """Získá absolutní cestu k souboru, funguje pro čistý Python, PyInstaller i Nuitku"""
    if hasattr(sys, '_MEIPASS'):
        # Rozpozná, že program zabalil PyInstaller
        zakladni_cesta = sys._MEIPASS
    elif "__compiled__" in globals():
        # Rozpozná, že program zkompilovala Nuitka
        zakladni_cesta = os.path.dirname(__file__)
    else:
        # Rozpozná, že program spouštíš klasicky přes IDE nebo příkazový řádek
        zakladni_cesta = os.path.abspath(".")
    
    return os.path.join(zakladni_cesta, relativni_cesta)

UDP_PORT = 12345
TCP_PORT = 12346
VOICE_PORT = 12347

# Nyní už Python zná funkci 'ziskej_appdata_cestu', takže ji můžeme bezpečně zavolat
SOUBOR_HISTORIE = ziskej_appdata_cestu("lan_historie.txt")
SOUBOR_NICK = ziskej_appdata_cestu("lan_nick.txt")
SOUBOR_HRY = ziskej_appdata_cestu("lan_hry.txt")
SOUBOR_JAZYK = ziskej_appdata_cestu("lan_jazyk.txt")
SDILENA_SLOZKA = "LAN_Sdilení"

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
    "btn_chat_player": {"CZ": "💬 Chat", "EN": "💬 Chat"},
    "btn_auto_connect": {"CZ": "🔗 Připojit na LAN (Automaticky)", "EN": "🔗 Connect to LAN (Auto)"},
    "btn_adv_net": {"CZ": "⚙️ Pokročilé sítě", "EN": "⚙️ Adv. Network"},
    "lbl_connected": {"CZ": "🟢 Připojen", "EN": "🟢 Connected"},
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
    "win_exit_title": {"CZ": "Ukončení a Úklid sítě", "EN": "Exit & Network Cleanup"},
    "win_exit_text": {"CZ": "LAN Párty končí?\n\nPřeješ si před vypnutím programu zamést stopy?\n1. Uzavře díry ve Windows Firewallu.\n2. Vrátí IP adresu na automatiku (DHCP pro domácí internet).", "EN": "Is the LAN Party over?\n\nDo you want to clean up before exiting?\n1. Closes holes in Windows Firewall.\n2. Reverts IP to automatic (DHCP for home internet)."},
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
    
    # --- NOVÉ PŘEKLADY PRO SQUAD A CHYBY ---
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

PREDNASTAVENE_IP = [f"192.168.0.{i}" for i in range(1, 255)]

MOTIVY = {
    "Zelena": {"main": "#2ecc71", "hover": "#27ae60", "border": "#1d8348"},
    "Modra": {"main": "#3498db", "hover": "#2980b9", "border": "#1a5276"},
    "Fialova": {"main": "#9b59b6", "hover": "#8e44ad", "border": "#512e5f"},
    "Ruzova": {"main": "#e91e63", "hover": "#c2185b", "border": "#880e4f"},
    "Zluta": {"main": "#f1c40f", "hover": "#f39c12", "border": "#9c640c"},
    "Tyrkysova": {"main": "#00bcd4", "hover": "#0097a6", "border": "#006064"}
}

ZNAME_HRY = {
    # Klasiky a RTS
    "6112-6119": "Warcraft 3 / Reforged / D2",
    "47624": "Age of Empires II / HoMM 3",
    "2300-2310": "Age of Mythology",
    "27900": "C&C Generals / Zero Hour",
    "6120-6125": "Company of Heroes",
    "1119": "StarCraft II",
    
    # Střílečky a FPS
    "27015-27030": "CS 1.6 / CS:GO / L4D / Source",
    "27960": "Quake 3",
    "12203": "Medal of Honor: AA",
    "14567": "Battlefield 1942",
    "28960-28965": "Call of Duty 1/2/4",
    "2302-2305": "Arma 3 / Halo CE",
    "7777-7780": "Terraria / ARK / UT99",
    "25600-25605": "Serious Sam",
    "10480-10482": "SWAT 4",
    
    # Survival, Crafting a Sandbox
    "25565": "Minecraft",
    "34197": "Factorio",
    "2456-2458": "Valheim",
    "28015": "Rust",
    "16261-16262": "Project Zomboid",
    "10999": "Don't Starve Together",
    "15000-15777": "Satisfactory",
    "27016": "Garry's Mod / Space Engineers",
    
    # Závody a ostatní
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
    # RPG a ARPG
    "Warcraft III.exe": "Warcraft 3 / Reforged",
    "D2R.exe": "Diablo II: Resurrected",
    "Torchlight2.exe": "Torchlight II",
    "Titan Quest.exe": "Titan Quest",
    "Grim Dawn.exe": "Grim Dawn",
    
    # FPS a Střílečky
    "csgo.exe": "CS:GO",
    "cs2.exe": "Counter-Strike 2",
    "hl.exe": "CS 1.6 / Half-Life",
    "hl2.exe": "Team Fortress 2 / GMod",
    "left4dead.exe": "Left 4 Dead",
    "left4dead2.exe": "Left 4 Dead 2",
    "mohaa.exe": "Medal of Honor: AA",
    "bf1942.exe": "Battlefield 1942",
    "bf2.exe": "Battlefield 2",
    "iw3mp.exe": "Call of Duty 4 (Multiplayer)",
    "iw2mp.exe": "Call of Duty 2 (Multiplayer)",
    "quake3.exe": "Quake 3 Arena",
    "UT2004.exe": "Unreal Tournament 2004",
    "UnrealTournament.exe": "Unreal Tournament 99",
    "SamHD.exe": "Serious Sam HD",
    "Sam2017.exe": "Serious Sam",
    "swat4.exe": "SWAT 4",
    "haloce.exe": "Halo: Combat Evolved",
    "arma3_x64.exe": "Arma 3",
    "arma3.exe": "Arma 3",
    "payday2_win32_release.exe": "Payday 2",
    "Borderlands.exe": "Borderlands",
    "Borderlands2.exe": "Borderlands 2",
    "Borderlands3.exe": "Borderlands 3",
    
    # Survival a Crafting
    "minecraft.exe": "Minecraft",
    "valheim.exe": "Valheim",
    "Terraria.exe": "Terraria",
    "RustClient.exe": "Rust",
    "ProjectZomboid64.exe": "Project Zomboid",
    "dontstarve.exe": "Don't Starve Together",
    "FactoryGame-Win64-Shipping.exe": "Satisfactory",
    "TheForest.exe": "The Forest",
    "SpaceEngineers.exe": "Space Engineers",
    "ConanSandbox.exe": "Conan Exiles",
    "7DaysToDie.exe": "7 Days to Die",
    "ShooterGame.exe": "ARK: Survival Evolved",
    "Raft.exe": "Raft",
    
    # Strategie a Simulatory
    "factorio.exe": "Factorio",
    "age2_x1.exe": "Age of Empires II",
    "AoE2DE_s.exe": "Age of Empires II: DE",
    "Heroes3.exe": "HoMM 3",
    "h3ota.exe": "HoMM 3: Horn of the Abyss",
    "starcraft.exe": "StarCraft",
    "SC2_x64.exe": "StarCraft II",
    "generals.exe": "C&C Generals / Zero Hour",
    "game.exe": "Red Alert 2",
    "ra2.exe": "Red Alert 2",
    "RelicCOH.exe": "Company of Heroes",
    "Stronghold Crusader.exe": "Stronghold Crusader",
    "CivilizationVI.exe": "Civilization VI",
    "stellaris.exe": "Stellaris",
    "eurotrucks2.exe": "Euro Truck Sim 2",
    "FarmingSimulator2022Game.exe": "Farming Simulator 22",
    
    # Party, Závody a Zábava
    "FlatOut2.exe": "FlatOut 2",
    "Wreckfest.exe": "Wreckfest",
    "speed2.exe": "NFS: Underground 2",
    "speed.exe": "NFS: Most Wanted",
    "TmForever.exe": "TrackMania Nations Forever",
    "revolt.exe": "Re-Volt",
    "Blur.exe": "Blur",
    "FiveM.exe": "FiveM (GTA V)",
    "RocketLeague.exe": "Rocket League",
    "Among Us.exe": "Among Us",
    "Overcooked2.exe": "Overcooked! 2",
    "Human.exe": "Human: Fall Flat",
    "FallGuys_client.exe": "Fall Guys",
    "Stardew Valley.exe": "Stardew Valley",
    "soldat.exe": "Soldat",
    "WA.exe": "Worms Armageddon",
    "Worms W.M.D.exe": "Worms W.M.D",
    
    # MOBA
    "dota2.exe": "Dota 2"
}

VERZE_PROGRAMU = "1.0"
URL_VERZE = "https://raw.githubusercontent.com/LigoLAN/LigoLAN/main/verze.txt" 
URL_STAZENI = "https://github.com/LigoLAN/LigoLAN/releases/latest"

def zkontroluj_aktualizace(okno_root, tichy_rezim=True):
    """Zkontroluje nejnovější verzi na serveru ve vedlejším vlákně."""
    def proces_kontroly():
        try:
            odpoved = urllib.request.urlopen(URL_VERZE, timeout=3)
            nejnovejsi_verze = odpoved.read().decode('utf-8').strip()
            
            if nejnovejsi_verze > VERZE_PROGRAMU:
                okno_root.after(0, zeptej_se_na_update, nejnovejsi_verze)
        except Exception as e:
            pass # V tichém režimu chyby bez internetu ignorujeme

    def zeptej_se_na_update(nova_verze):
        import tkinter.messagebox as mb
        if mb.askyesno("Nová verze!", f"Je dostupná verze {nova_verze}.\nChceš otevřít stránku pro stažení?"):
            webbrowser.open(URL_STAZENI)

    import threading
    threading.Thread(target=proces_kontroly, daemon=True).start()

class LANPartyTool:
    def __init__(self, root):
        self.root = root
        self.root.title("LigoLAN v.1.0")
        
        # --- CHYTRÉ PŘIZPŮSOBENÍ MONITORU A PROPORCÍ ---
        vyska_monitoru = self.root.winfo_screenheight()
        
        if vyska_monitoru > 900:
            # Velké monitory (FullHD, 4K) -> Otevře se v plné kráse
            self.root.geometry("950x900")
            self.vyska_radaru = 150 # Plná velikost radaru
        else:
            # Malé notebooky (1366x768 atd.) -> Kompaktní start
            self.root.geometry("850x750")
            self.vyska_radaru = 110  # Proporčně zmenšený radar
            
        self.root.minsize(800, 600)
        # -----------------------------------------------
        
        self.root.configure(fg_color="#0a0a0a")
        self.root.protocol("WM_DELETE_WINDOW", self.pri_ukonceni)
        
        # --- DETEKCE MINIMALIZACE (Záchrana paměti pro BMAX) ---
        self.okno_minimalizovano = False
        self.root.bind("<Unmap>", lambda e: setattr(self, 'okno_minimalizovano', True) if str(self.root.state()) == 'iconic' else None)
        self.root.bind("<Map>", lambda e: setattr(self, 'okno_minimalizovano', False))

        self.lock_hraci = threading.Lock()
        self.lock_soubory = threading.Lock()
        self.lock_statistiky = threading.Lock()

        self.radar_executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

        self.odeslano = 0
        self.prijato = 0
        self.seznam_hracu = {} 
        self.cekajici_zpravy = set()
        
        self.spam_ochrana_soubory = {} 
        self.spam_ochrana_dir = {} 
        
        self.sdileni_ceka_na_prijemci = {}
        self.ocekavane_soubory = {}
        self.ocekavane_velikosti = {}
        self.mapa_sdilenych_souboru = {}
        self.okna_chatu = {} 
        
        self.zobrazena_zadost_o_soubor = False 
        self.cached_soubory = []

        os.makedirs(SDILENA_SLOZKA, exist_ok=True)
        self.muj_hostname = socket.gethostname()
        self.moje_ip = self.ziskat_lokalni_ip()

        ctk.set_appearance_mode("dark")

        frame_user = ctk.CTkFrame(root, fg_color="#141414", corner_radius=0)
        frame_user.pack(fill="x", padx=10, pady=10)
        
        self.jazyk = "CZ" 
        if os.path.exists(SOUBOR_JAZYK):
            try:
                with open(SOUBOR_JAZYK, "r", encoding="utf-8") as f:
                    self.jazyk = f.read().strip()
            except: pass

        self.btn_jazyk = ctk.CTkButton(frame_user, text=self.jazyk, command=self.prepni_jazyk, fg_color="#f39c12", hover_color="#d68910", text_color="white", font=("Arial", 13, "bold"), width=60, corner_radius=8)
        self.btn_jazyk.pack(side="right", padx=10, pady=10)
        
        frame_barvy = ctk.CTkFrame(frame_user, fg_color="transparent")
        frame_barvy.pack(side="right", padx=(5, 10))
        for nazev, barvy in MOTIVY.items():
            btn_b = ctk.CTkButton(frame_barvy, text="", width=20, height=20, corner_radius=10, fg_color=barvy["main"], hover_color=barvy["hover"], command=lambda n=nazev: self.zmenit_motiv(n))
            btn_b.pack(side="left", padx=3)
        
        self.btn_about = ctk.CTkButton(frame_user, text=TEXTY["btn_about"][self.jazyk], command=self.zobrazit_o_programu, fg_color="#8e44ad", hover_color="#732d91", text_color="white", font=("Arial", 13, "bold"), width=100, corner_radius=8)
        self.btn_about.pack(side="right", padx=5)
        
        self.btn_donate = ctk.CTkButton(frame_user, text=TEXTY["btn_donate"][self.jazyk], command=self.zobrazit_podporu, fg_color="#e67e22", hover_color="#ca6f1e", text_color="white", font=("Arial", 13, "bold"), width=100, corner_radius=8)
        self.btn_donate.pack(side="right", padx=5)

        self.lbl_tvoje_prezdivka = ctk.CTkLabel(frame_user, text=TEXTY["lbl_nick"][self.jazyk], font=("Arial", 15, "bold"), text_color="#f1c40f")
        self.lbl_tvoje_prezdivka.pack(side="left", padx=10)
        
        self.entry_nick = ctk.CTkEntry(frame_user, font=("Arial", 14), width=180, corner_radius=8, border_color="#34495e")
        
        ulozeny_nick = "Hráč"
        if os.path.exists(SOUBOR_NICK):
            try:
                with open(SOUBOR_NICK, "r", encoding="utf-8") as f:
                    ulozeny_nick = f.read().strip() or "Hráč"
            except: pass
            
        self.entry_nick.insert(0, ulozeny_nick)
        self.entry_nick.pack(side="left", padx=10)
        self.entry_nick.bind("<KeyRelease>", self.aktualizuj_vizitku)

        # Vytvoření hlavního rámečku (Změněno na průhledné, aby zelená zmizela úplně)
        self.frame_moje_pc = ctk.CTkFrame(root, fg_color="transparent", height=130)
        self.frame_moje_pc.pack(fill="x", padx=10, pady=(5, 10))
        self.frame_moje_pc.pack_propagate(False) 

        # --- NAČTĚNÍ OBRÁZKU NA POZADÍ ---
        try:
            cesta_pozadi = ziskej_cestu("pozadi.jpg")
            obrazek_pil = Image.open(cesta_pozadi)
            pozadi_img = ctk.CTkImage(light_image=obrazek_pil, dark_image=obrazek_pil, size=(850, 130))
            self.lbl_pozadi = ctk.CTkLabel(self.frame_moje_pc, text="", image=pozadi_img)
            self.lbl_pozadi.place(relx=0, rely=0, relwidth=1, relheight=1)
        except Exception as e:
            self.zapsat_do_logu(f"Nepodařilo se načíst obrázek pozadí: {e}")
        # ----------------------------------------
        
        self.zvuky_zapnuty = True
        # Zvuk: Tmavé tlačítko se zeleným okrajem, aby ladilo
        self.btn_zvuk = ctk.CTkButton(self.frame_moje_pc, text="🔊", command=self.prepni_zvuky, bg_color="transparent", fg_color="#141414", hover_color="#2a2a2a", border_width=2, border_color="#2ecc71", text_color="white", font=("Arial", 15), width=40, height=40, corner_radius=20)
        self.btn_zvuk.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10) 
        
        # --- PLOVOUCÍ TMAVÉ ŠTÍTKY (BADGES) ---
        
        # Nick: Tmavé pozadí (fg_color="#141414"), zakulacené rohy, odsazení uvnitř
        self.lbl_velky_nick = ctk.CTkLabel(self.frame_moje_pc, text=ulozeny_nick, bg_color="transparent", fg_color="#141414", font=("Arial", 26, "bold"), text_color="white", corner_radius=8, padx=20, pady=2)
        self.lbl_velky_nick.place(relx=0.5, rely=0.25, anchor="center")

        # IP Rámeček: Tmavé zakulacené pozadí
        ramecek_ip_info = ctk.CTkFrame(self.frame_moje_pc, fg_color="#141414", bg_color="transparent", corner_radius=8)
        ramecek_ip_info.place(relx=0.5, rely=0.55, anchor="center")
        
        info_text = f" 🖥️ PC: {self.muj_hostname}   |   🌐 IP: {self.moje_ip}   |   {TEXTY['lbl_connected'][self.jazyk]} "
        self.lbl_moje_info = ctk.CTkLabel(ramecek_ip_info, text=info_text, bg_color="transparent", font=("Arial", 13, "bold"), text_color="white", padx=10, pady=4)
        self.lbl_moje_info.pack(side="left", padx=(0, 5))
        
        self.btn_kopirovat_ip = ctk.CTkButton(ramecek_ip_info, text=TEXTY["btn_copy_ip"][self.jazyk], command=self.zkopirovat_moji_ip, fg_color="#f39c12", hover_color="#d68910", text_color="white", font=("Arial", 12, "bold"), height=25, corner_radius=5)
        self.btn_kopirovat_ip.pack(side="left", padx=(0, 5), pady=4)

       # --- HW DETEKCE (BLESKOVÝ START) ---
        # Vykreslíme štítek okamžitě, ale samotné těžké zjišťování odsuneme na pozadí!
        self.lbl_hw_info = ctk.CTkLabel(self.frame_moje_pc, text=TEXTY["lbl_hw_detect"][self.jazyk], bg_color="transparent", fg_color="#141414", font=("Arial", 11, "bold"), text_color="#ecf0f1", corner_radius=8, padx=10, pady=2)
        self.lbl_hw_info.place(relx=0.5, rely=0.85, anchor="center")
        
        # Odložíme start zjišťování hardwaru o přesně 15 vteřin (15000 milisekund).
        # Díky tomu má pomalejší PC dostatek času vykreslit okno a připojit se k síti, než začneme číst paměť a registry.
        self.root.after(15000, lambda: threading.Thread(target=self._zjistit_hw_na_pozadi, daemon=True).start())

        self.frame_jednoduche_ip = ctk.CTkFrame(root, fg_color="transparent")
        self.frame_jednoduche_ip.pack(fill="x", padx=10, pady=(0, 10))
        
        self.btn_auto_ip = ctk.CTkButton(self.frame_jednoduche_ip, text=TEXTY["btn_auto_connect"][self.jazyk], command=self.automaticky_nastavit_ip_kabel, fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=("Arial", 16, "bold"), height=50, corner_radius=8, border_width=3, border_color="#1d8348")
        self.btn_auto_ip.pack(fill="x", side="left", expand=True, padx=(0, 10))
        
        self.btn_pokrocile = ctk.CTkButton(self.frame_jednoduche_ip, text=TEXTY["btn_adv_net"][self.jazyk], command=self.prepnout_zobrazeni_pokrocilych_ip, fg_color="#7f8c8d", hover_color="#95a5a6", text_color="white", font=("Arial", 12, "bold"), width=120, height=50, corner_radius=8)
        self.btn_pokrocile.pack(side="right")

        self.pokrocile_ip_zobrazeno = False
        self.frame_ip = tk.LabelFrame(root, text=TEXTY["frame_ip"][self.jazyk], bg="#2c3e50", fg="white", padx=10, pady=10, bd=1)

        self.lbl_sitovy_adapter = tk.Label(self.frame_ip, text=TEXTY["lbl_sitovy_adapter"][self.jazyk], bg="#2c3e50", fg="white")
        self.lbl_sitovy_adapter.grid(row=0, column=0, sticky="w", pady=2)
        self.combo_adapter = ttk.Combobox(self.frame_ip, width=22)
        self.combo_adapter['values'] = self.ziskat_aktivni_adaptery()
        if self.combo_adapter['values']: 
            self.combo_adapter.current(0)
            self.root.after(500, self.aktualizovat_zobrazenou_ip)
        self.combo_adapter.grid(row=0, column=1, padx=10, pady=2)
        self.combo_adapter.bind("<<ComboboxSelected>>", self.aktualizovat_zobrazenou_ip)

        self.lbl_nova_ip = tk.Label(self.frame_ip, text=TEXTY["lbl_nova_ip"][self.jazyk], bg="#2c3e50", fg="white")
        self.lbl_nova_ip.grid(row=1, column=0, sticky="w", pady=2)
        self.entry_ip = ttk.Combobox(self.frame_ip, width=22, values=PREDNASTAVENE_IP)
        self.entry_ip.insert(0, "192.168.0.10")
        self.entry_ip.grid(row=1, column=1, padx=10, pady=2)

        self.lbl_maska = tk.Label(self.frame_ip, text=TEXTY["lbl_maska"][self.jazyk], bg="#2c3e50", fg="white")
        self.lbl_maska.grid(row=2, column=0, sticky="w", pady=2)
        self.entry_mask = tk.Entry(self.frame_ip, width=25)
        self.entry_mask.insert(0, "255.255.255.0")
        self.entry_mask.grid(row=2, column=1, padx=10, pady=2)

        self.btn_nastavit_ip = ctk.CTkButton(self.frame_ip, text=TEXTY["btn_nastavit_ip"][self.jazyk], command=self.zmenit_ip, fg_color="#e67e22", hover_color="#d35400", width=180, corner_radius=6)
        self.btn_nastavit_ip.grid(row=0, column=2, padx=15, pady=2)
        self.btn_nastavit_rucne = ctk.CTkButton(self.frame_ip, text=TEXTY["btn_nastavit_rucne"][self.jazyk], command=self.otevrit_sitova_pripojeni, fg_color="#7f8c8d", hover_color="#95a5a6", width=180, corner_radius=6)
        self.btn_nastavit_rucne.grid(row=1, column=2, padx=15, pady=2)
        self.btn_aktualizovat_ip = ctk.CTkButton(self.frame_ip, text=TEXTY["btn_aktualizovat_ip"][self.jazyk], command=self.aktualizovat_zobrazenou_ip, fg_color="#3498db", hover_color="#2980b9", width=180, corner_radius=6)
        self.btn_aktualizovat_ip.grid(row=2, column=2, padx=15, pady=2)

        ttk.Separator(self.frame_ip, orient="horizontal").grid(row=3, column=0, columnspan=3, sticky="ew", pady=15)
        
        r_firewall = tk.Frame(self.frame_ip, bg="#2c3e50")
        r_firewall.grid(row=4, column=0, columnspan=3)
        self.btn_firewall = ctk.CTkButton(r_firewall, text=TEXTY["btn_firewall"][self.jazyk], command=self.opravit_firewall, fg_color="#e74c3c", hover_color="#c0392b", font=("Arial", 12, "bold"), width=150, corner_radius=6)
        self.btn_firewall.pack(side="left", padx=5)
        self.btn_firewall_vratit = ctk.CTkButton(r_firewall, text=TEXTY["btn_firewall_vratit"][self.jazyk], command=self.vratit_firewall, fg_color="#7f8c8d", hover_color="#95a5a6", font=("Arial", 12), width=120, corner_radius=6)
        self.btn_firewall_vratit.pack(side="left", padx=5)
        self.btn_firewall_rucne = ctk.CTkButton(r_firewall, text=TEXTY["btn_firewall_rucne"][self.jazyk], command=self.otevrit_firewall_windows, fg_color="#f39c12", hover_color="#d68910", font=("Arial", 12, "bold"), width=120, corner_radius=6)
        self.btn_firewall_rucne.pack(side="left", padx=5)

        self.frame_pokrocile_hledani = tk.Frame(root, bg="#141414") 
        self.btn_najit_hrace = ctk.CTkButton(self.frame_pokrocile_hledani, text=TEXTY["btn_najit_hrace"][self.jazyk], command=self.prohledat_sit, fg_color="#8e44ad", hover_color="#732d91", font=("Arial", 13, "bold"), height=35, corner_radius=6, border_width=2, border_color="#5b2c6f")
        self.btn_najit_hrace.pack(fill="x", pady=(5, 10))
        
        frame_pridat = tk.Frame(self.frame_pokrocile_hledani, bg="#141414")
        frame_pridat.pack(fill="x", pady=5)
        self.lbl_nebo_rucne = tk.Label(frame_pridat, text=TEXTY["lbl_nebo_rucne"][self.jazyk], bg="#141414", fg="white", font=("Arial", 11))
        self.lbl_nebo_rucne.pack(side="left")
        self.novy_ip = ttk.Combobox(frame_pridat, width=18, font=("Arial", 11), values=PREDNASTAVENE_IP)
        self.novy_ip.pack(side="left", padx=10)
        self.btn_pridat = ctk.CTkButton(frame_pridat, text=TEXTY["btn_pridat"][self.jazyk], command=self.pridat_hrace_rucne, fg_color="#2ecc71", hover_color="#27ae60", width=80, corner_radius=6)
        self.btn_pridat.pack(side="left")
        
        tk.Button(frame_pridat, text="🔄", command=self.spustit_kontrolu_ihned, bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=3, bd=0, cursor="hand2").pack(side="right")

        # --- ELASTICKÝ POSUVNÍK (PanedWindow) ---
        self.paned_window = tk.PanedWindow(root, orient="vertical", bg="#0a0a0a", bd=0, sashwidth=8, sashcursor="sb_v_double_arrow")
        self.paned_window.pack(fill="both", expand=True, padx=10, pady=(5, 5))

        # HORNÍ ČÁST: Radar
        self.frame_hraci_hlavni = ctk.CTkFrame(self.paned_window, fg_color="#141414", corner_radius=10, border_width=1, border_color="#333333")
        
        # OPRAVA: Přidali jsme 'height=220'. Radar tak při startu zabere přesně tolik místa, kolik potřebuje!
        self.paned_window.add(self.frame_hraci_hlavni, minsize=100, height=220) 
        
        self.lbl_radar_title = ctk.CTkLabel(self.frame_hraci_hlavni, text=TEXTY["frame_hraci_hlavni"][self.jazyk], font=("Arial", 14, "bold"), text_color="#ecf0f1")
        self.lbl_radar_title.pack(pady=(10, 0), anchor="center")

        self.frame_seznam_hracu = ctk.CTkScrollableFrame(self.frame_hraci_hlavni, fg_color="#0a0a0a", height=130, corner_radius=8)
        # Zde jsme dali pady=10 (bez toho tlačítka už to nepotřebuje spodní mezeru navíc)
        self.frame_seznam_hracu.pack(fill="both", expand=True, padx=10, pady=10)

        # SPODNÍ ČÁST: Záložky (Chat, Sdílení, Hry, Voice)
        self.notebook = ctk.CTkTabview(self.paned_window, fg_color="transparent", segmented_button_fg_color="#1a1a1a", segmented_button_selected_color="#2ecc71", segmented_button_selected_hover_color="#27ae60", text_color="white", corner_radius=10, command=self.pri_prepuj_zalozky)
        self.paned_window.add(self.notebook, minsize=150, stretch="always") 
        
        tab_chat_name = TEXTY["tab_chat"][self.jazyk]
        tab_files_name = TEXTY["tab_files"][self.jazyk]
        tab_games_name = TEXTY["tab_games"][self.jazyk]
        tab_squad_name = TEXTY["tab_squad"][self.jazyk]
        
        self.tab_chat = self.notebook.add(tab_chat_name)
        self.tab_slozka = self.notebook.add(tab_files_name)
        self.tab_hry = self.notebook.add(tab_games_name)
        self.tab_squad = self.notebook.add(tab_squad_name) # Přidání do GUI
        
        # --- OBSAH NOVÉ ZÁLOŽKY (Tlačítko na tým) ---
        self.lbl_squad_info = ctk.CTkLabel(self.tab_squad, text=TEXTY["lbl_squad_info"][self.jazyk], font=("Arial", 14), text_color="#bdc3c7")
        self.lbl_squad_info.pack(pady=(30, 15))
        
        self.btn_vytvorit_tym = ctk.CTkButton(self.tab_squad, text=TEXTY["btn_create_squad"][self.jazyk], command=self.zalozit_tym, fg_color="#3498db", hover_color="#2980b9", font=("Arial", 16, "bold"), height=50, corner_radius=8)
        self.btn_vytvorit_tym.pack(fill="x", padx=60, pady=10)

        r_rozhlas = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        r_rozhlas.pack(side="bottom", fill="x", padx=5, pady=(5, 10))
        
        self.btn_rozhlas = ctk.CTkButton(r_rozhlas, text=TEXTY["btn_rozhlas"][self.jazyk], command=self.poslat_rozhlas, fg_color="#e67e22", hover_color="#d35400", font=("Arial", 14, "bold"), width=150, height=40, corner_radius=8, border_width=2, border_color="#a04000")
        self.btn_rozhlas.pack(side="right", padx=(10, 0))
        
        self.entry_rozhlas = ctk.CTkEntry(r_rozhlas, font=("Arial", 14), placeholder_text=TEXTY["ph_rozhlas"][self.jazyk], height=40, corner_radius=8, fg_color="#ffffff", text_color="#000000", placeholder_text_color="#888888", border_color="#cccccc")
        self.entry_rozhlas.pack(side="left", fill="x", expand=True)
        
        self.entry_rozhlas.bind("<Return>", lambda e: self.poslat_rozhlas())

        self.chat_box = tk.Listbox(self.tab_chat, bg="#ffffff", fg="#000000", font=("Arial", 12), selectbackground="#16a085", selectforeground="#ffffff", bd=1, relief="solid")
        self.chat_box.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        horni_lista = ctk.CTkFrame(self.tab_slozka, fg_color="transparent")
        horni_lista.pack(fill="x", padx=5, pady=(0, 5))
        
        self.btn_stahnout_soubor = ctk.CTkButton(horni_lista, text=TEXTY["btn_stahnout_soubor"][self.jazyk], command=self.stahnout_vybrany_soubor, fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 12, "bold"), width=160, height=35, corner_radius=6, border_width=2, border_color="#1d8348")
        self.btn_stahnout_soubor.pack(side="left", padx=2)
        
        self.btn_otevrit_slozku = ctk.CTkButton(horni_lista, text=TEXTY["btn_otevrit_slozku"][self.jazyk], command=self.otevrit_lokalni_slozku, fg_color="#e67e22", hover_color="#d35400", font=("Arial", 11, "bold"), width=150, height=35, corner_radius=6)
        self.btn_otevrit_slozku.pack(side="right", padx=2)
        
        # --- ROLETA ÚLOH UMÍSTĚNÁ PŘESNĚ DO MEZERY ---
        self.aktivni_ulohy = {}
        self.ukoly_zobrazeny = False
        
        self.btn_ukoly_toggle = ctk.CTkButton(horni_lista, text=f"{TEXTY['btn_tasks_show'][self.jazyk]} (0)", command=self.toggle_ukoly, fg_color="#34495e", hover_color="#2c3e50", font=("Arial", 12, "bold"), height=35, corner_radius=6)
        self.btn_ukoly_toggle.pack(side="left", fill="x", expand=True, padx=10) # fill="x" a expand=True to roztáhne na celou mezeru!
        
        # Samotná roletka (Zatím neviditelná)
        self.frame_aktivity = ctk.CTkScrollableFrame(self.tab_slozka, height=120, fg_color="#141414", corner_radius=6)
        
        # Vytvoření moderního stylu pro tabulku
        styl_tabulky = ttk.Style()
        styl_tabulky.theme_use("default")
        styl_tabulky.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", borderwidth=0, font=("Arial", 11))
        styl_tabulky.map('Treeview', background=[('selected', '#3498db')])
        styl_tabulky.configure("Treeview.Heading", background="#2c3e50", foreground="white", font=("Arial", 11, "bold"), borderwidth=1)

        sloupce = ("soubor", "majitel", "velikost")
        self.list_souboru = ttk.Treeview(self.tab_slozka, columns=sloupce, show="headings", style="Treeview")
        self.list_souboru.heading("soubor", text="📄 Název souboru")
        self.list_souboru.heading("majitel", text="👤 Majitel")
        self.list_souboru.heading("velikost", text="💾 Velikost")

        self.list_souboru.column("soubor", width=350, anchor="w")
        self.list_souboru.column("majitel", width=150, anchor="center")
        self.list_souboru.column("velikost", width=100, anchor="center")

        self.list_souboru.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        horni_lista_hry = ctk.CTkFrame(self.tab_hry, fg_color="transparent")
        horni_lista_hry.pack(fill="x", padx=5, pady=(0, 5))
        
        self.btn_pridat_hru = ctk.CTkButton(horni_lista_hry, text=TEXTY["btn_add_game"][self.jazyk], command=self.pridat_hru, fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 11, "bold"), width=120, height=35, corner_radius=6)
        self.btn_pridat_hru.pack(side="left", padx=2)
        
        self.btn_odebrat_hru = ctk.CTkButton(horni_lista_hry, text=TEXTY["btn_remove_game"][self.jazyk], command=self.odebrat_hru, fg_color="#e74c3c", hover_color="#c0392b", font=("Arial", 11, "bold"), width=120, height=35, corner_radius=6)
        self.btn_odebrat_hru.pack(side="right", padx=2)
        
        self.btn_spustit_hru = ctk.CTkButton(horni_lista_hry, text=TEXTY["btn_start_game"][self.jazyk], command=self.spustit_hru, fg_color="#8e44ad", hover_color="#732d91", font=("Arial", 13, "bold"), height=35, corner_radius=6, border_width=2, border_color="#5b2c6f")
        self.btn_spustit_hru.pack(side="left", fill="x", expand=True, padx=10)
        
        self.list_her = tk.Listbox(self.tab_hry, bg="#ffffff", fg="#000000", font=("Arial", 13, "bold"), selectbackground="#8e44ad", selectforeground="#ffffff", bd=1, relief="solid")
        self.list_her.pack(fill="both", expand=True, padx=5, pady=5)
        self.list_her.bind("<Double-1>", lambda e: self.spustit_hru()) 
        
        self.moje_hry = {}
        self.nacti_hry()

        self.zapsat_do_logu("=== Aplikace spuštěna ===")
        self.spustit_kontrolu_smycka()
        self.automaticke_nacitani_souboru() 
        self.start_naslouchani()
        self.aktualizuj_tlacitko_zvuku()
        self.inicializuj_drag_and_drop()

        zkontroluj_aktualizace(self.root, tichy_rezim=True)
        
        self.aktualni_nazev_motivu = "Zelena"
        self.aktualni_barva_motivu = "#2ecc71"
        if os.path.exists("lan_motiv.txt"):
            try:
                with open("lan_motiv.txt", "r", encoding="utf-8") as f:
                    ulozeny = f.read().strip()
                    if ulozeny in MOTIVY: self.zmenit_motiv(ulozeny)
            except: pass 

    def vykonat_jako_spravce(self, prikazy):
        if not prikazy: return True
        spojene_prikazy = " & ".join(prikazy)
        try:
            # Použijeme cmd.exe /c ke spuštění více příkazů za sebou přes ShellExecuteW. Tohle Defender nechápe jako malware.
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c {spojene_prikazy}", None, 0)
            return ret > 32
        except Exception as e: 
            self.zapsat_do_logu(f"[CHYBA] Práva správce selhala nebo byla zrušena: {e}")
            return False

    def _dostat_prikazy_firewall_povolit(self):
        cesta_k_nam = sys.executable
        return [
            f'netsh advfirewall firewall add rule name="LAN Party APP" dir=in action=allow program="{cesta_k_nam}" enable=yes profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party APP" dir=out action=allow program="{cesta_k_nam}" enable=yes profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party Ping" protocol=icmpv4:8,any dir=in action=allow profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party Chat IN" protocol=UDP dir=in localport={UDP_PORT} action=allow profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party Chat OUT" protocol=UDP dir=out remoteport={UDP_PORT} action=allow profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party File IN" protocol=TCP dir=in localport={TCP_PORT} action=allow profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party File OUT" protocol=TCP dir=out remoteport={TCP_PORT} action=allow profile=any'
        ]

    def _dostat_prikazy_firewall_uklid(self):
        return [
            'netsh advfirewall firewall delete rule name="LAN Party APP"',
            'netsh advfirewall firewall delete rule name="LAN Party Ping"',
            'netsh advfirewall firewall delete rule name="LAN Party Chat IN"',
            'netsh advfirewall firewall delete rule name="LAN Party Chat OUT"',
            'netsh advfirewall firewall delete rule name="LAN Party Chat"',
            'netsh advfirewall firewall delete rule name="LAN Party File IN"',
            'netsh advfirewall firewall delete rule name="LAN Party File OUT"',
            'netsh advfirewall firewall delete rule name="LAN Party Hra"',
            'netsh advfirewall firewall delete rule name="LAN Party Hra EXE"'
        ]

    def poslat_udp_zpravu(self, zprava, ip, port=UDP_PORT, broadcast=False):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if broadcast:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
            # OPRAVA: Váže se na IP POUZE u specifických adres, globální broadcast necháme na Windows, jinak ho zablokují!
            if ip != '255.255.255.255':
                try: sock.bind((self.moje_ip, 0))
                except: pass
                
            sock.sendto(zprava.encode('utf-8'), (ip, port))
        except OSError as e:
            self.zapsat_do_logu(f"[UDP CHYBA] Nelze odeslat na {ip}: {e}")
        finally:
            try: sock.close()
            except: pass

    def opravit_firewall(self):
        prikazy = self._dostat_prikazy_firewall_uklid() + self._dostat_prikazy_firewall_povolit()
        if self.vykonat_jako_spravce(prikazy):
            messagebox.showinfo("Hotovo", TEXTY["msg_fw_done"][self.jazyk])
        else:
            messagebox.showerror("Chyba", "Oprávnění správce bylo zrušeno, firewall nebyl nastaven.")

    def vratit_firewall(self, tichy_rezim=False):
        self.vykonat_jako_spravce(self._dostat_prikazy_firewall_uklid())
        if not tichy_rezim: messagebox.showinfo("Úklid hotov", TEXTY["msg_fw_clean_txt"][self.jazyk])

    def otevrit_lokalni_slozku(self):
        try: os.startfile(SDILENA_SLOZKA)
        except Exception as e: messagebox.showerror("Chyba", f"Nepodařilo se otevřít složku: {e}")

    def obnovit_sdilenou_slozku(self, tichy_rezim=False):
        # 1. ZÁCHRANA POZICE pro tabulku
        vyber = self.list_souboru.selection()
        vybrana_polozka_hodnoty = self.list_souboru.item(vyber[0])['values'] if vyber else None

        for polozka in self.list_souboru.get_children():
            self.list_souboru.delete(polozka)
            
        with self.lock_soubory:
            self.mapa_sdilenych_souboru.clear()
            
        moje_soubory = os.listdir(SDILENA_SLOZKA)
        for s in moje_soubory:
            try:
                velikost_mb = round(os.path.getsize(os.path.join(SDILENA_SLOZKA, s)) / (1024*1024), 2)
                velikost_text = f"{velikost_mb} MB"
            except:
                velikost_text = "Neznámá"
            
            # Vložíme naše soubory do tabulky šedou barvou, abychom je odlišili
            item_id = self.list_souboru.insert("", "end", values=(s, "TY", velikost_text))
            self.list_souboru.item(item_id, tags=('mujsoubor',))
            
        self.list_souboru.tag_configure('mujsoubor', foreground='#7f8c8d')

        muj_nick = self.entry_nick.get().strip() or "Neznámý"
        dotaz = f"__DIR_REQ__:{muj_nick}"
        
        with self.lock_hraci:
            ip_seznam = list(self.seznam_hracu.keys())
            
        for ip in ip_seznam:
            self.poslat_udp_zpravu(dotaz, ip)
            
        if not tichy_rezim:
            self.chat_box.insert("end", TEXTY["msg_dir_req"][self.jazyk])

        # 2. OBNOVA POHLEDU (najde to původní výběr a znovu ho označí)
        def vratit_pohled():
            try:
                if vybrana_polozka_hodnoty:
                    for child in self.list_souboru.get_children():
                        if self.list_souboru.item(child)['values'] == vybrana_polozka_hodnoty:
                            self.list_souboru.selection_set(child)
                            break
            except: pass

        self.root.after(200, vratit_pohled)

    def automaticke_nacitani_souboru(self):
        try:
            docasna_pamet = []
            for s in os.listdir(SDILENA_SLOZKA):
                try:
                    velikost = os.path.getsize(os.path.join(SDILENA_SLOZKA, s))
                    velikost_mb = round(velikost / (1024*1024), 2)
                    docasna_pamet.append(f"{s}|{velikost_mb}")
                except:
                    docasna_pamet.append(f"{s}|?")
            self.cached_soubory = docasna_pamet
        except:
            self.cached_soubory = []
            
        # OPRAVA PRO TREEVIEW: Místo curselection() používáme selection()
        try:
            if not self.list_souboru.selection():
                self.obnovit_sdilenou_slozku(tichy_rezim=True)
        except: pass
        
        self.root.after(15000, self.automaticke_nacitani_souboru)

    def pri_prepuj_zalozky(self):
        if self.notebook.get() == TEXTY["tab_files"][self.jazyk]:
            self.obnovit_sdilenou_slozku(tichy_rezim=True)  

    def stahnout_vybrany_soubor(self):
        vyber = self.list_souboru.selection()
        if not vyber:
            messagebox.showwarning("Upozornění", "Musíš nejprve kliknutím vybrat soubor ze seznamu.")
            return
            
        hodnoty = self.list_souboru.item(vyber[0])['values']
        nazev_souboru = hodnoty[0]
        majitel = hodnoty[1]
        
        if majitel == "TY":
            messagebox.showinfo("Info", "Tento soubor už máš u sebe ve složce.")
            return
            
        # Zrekonstruujeme náš tajný klíč k mapě souborů
        polozka_klic = f"[{majitel}] {nazev_souboru}"
            
        with self.lock_soubory:
            data = self.mapa_sdilenych_souboru.get(polozka_klic)
            
        if data:
            ip_majitele = data["ip"]
            nazev_souboru = data["soubor"]
            cilova_cesta = os.path.join(SDILENA_SLOZKA, nazev_souboru)
            
            with self.lock_soubory:
                self.ocekavane_soubory[ip_majitele] = cilova_cesta
                self.ocekavane_velikosti[ip_majitele] = 0
                
            self.poslat_udp_zpravu(f"__DIR_GET__:{nazev_souboru}", ip_majitele)
            messagebox.showinfo("Stahování", f"Požadavek odeslán.\nSoubor '{nazev_souboru}' se za chvíli objeví ve tvé složce.")

    def vybrat_a_poslat_soubor(self, cilova_ip):
        volba = messagebox.askquestion(TEXTY["mb_send_folder_title"][self.jazyk], TEXTY["mb_send_folder_text"][self.jazyk])
        cesta = ""
        if volba == 'yes':
            cesta = filedialog.askdirectory(title="Vyber složku k odeslání")
            if not cesta: return
            
            id_zip = f"zip_{time.time()}"
            jmeno_slozky = os.path.basename(cesta)
            self.start_ukol(id_zip, f"Balím do ZIPu: {jmeno_slozky}... 📦")
            
            def zabalit_a_odeslat():
                složka_rodic = os.path.dirname(cesta)
                cesta_zip_bez_pripony = os.path.join(složka_rodic, f"{jmeno_slozky}_sdileni")
                konecny_zip = cesta_zip_bez_pripony + ".zip"
                
                # --- PŘESNÉ MĚŘENÍ PROGRESSBARU PŘI BALENÍ ---
                try:
                    celkova_velikost = sum(os.path.getsize(os.path.join(r, f)) for r, d, files in os.walk(cesta) for f in files)
                    zabaleno_bajtu = 0
                    
                    with zipfile.ZipFile(konecny_zip, 'w', zipfile.ZIP_STORED) as zipf:
                        for root_dir, dirs, files in os.walk(cesta):
                            for file in files:
                                file_path = os.path.join(root_dir, file)
                                arcname = os.path.relpath(file_path, start=cesta)
                                zipf.write(file_path, arcname)
                                
                                zabaleno_bajtu += os.path.getsize(file_path)
                                if celkova_velikost > 0:
                                    procenta = int((zabaleno_bajtu / celkova_velikost) * 100)
                                    self.root.after(0, self.update_ukol, id_zip, f"Balím do ZIPu: {jmeno_slozky} ({procenta}%)", procenta, "determinate")
                except Exception as e:
                    self.zapsat_do_logu(f"Chyba při přesném balení: {e}")
                    shutil.make_archive(cesta_zip_bez_pripony, 'zip', cesta) # Záložní plán, kdyby něco selhalo
                # ---------------------------------------------
                
                self.root.after(0, self.konec_ukol, id_zip, f"✅ Zabaleno: {jmeno_slozky}")
                self.root.after(0, lambda: self._dokoncit_pripravu_odeslani(cilova_ip, konecny_zip))
            
            threading.Thread(target=zabalit_a_odeslat, daemon=True).start()
            
        else:
            cesta = filedialog.askopenfilename(title="Vyber soubor")
            if not cesta: return
            self._dokoncit_pripravu_odeslani(cilova_ip, cesta)

    def _dokoncit_pripravu_odeslani(self, cilova_ip, cesta):
        velikost = os.path.getsize(cesta)
        nazev = os.path.basename(cesta)
        req_id = str(int(datetime.datetime.now().timestamp() * 1000))
        
        with self.lock_soubory:
            self.sdileni_ceka_na_prijemci[req_id] = cesta
            
        muj_nick = self.entry_nick.get().strip() or "Neznámý"
        self.poslat_udp_zpravu(f"__FILE_REQ__:{req_id}:{nazev}:{velikost}:{muj_nick}", cilova_ip)
        self.chat_box.insert("end", f"{TEXTY['msg_send_req'][self.jazyk]} {cilova_ip}.")
        self.notebook.set(TEXTY["tab_chat"][self.jazyk]) 

    def dotaz_prijmout_soubor(self, ip, req_id, nazev, velikost, jeho_nick):
        if self.zobrazena_zadost_o_soubor:
            self._odmitnout_soubor(ip, req_id) 
            return
            
        self.zobrazena_zadost_o_soubor = True
        velikost_mb = round(int(velikost) / (1024*1024), 2)
        
        # BEZPEČNOSTNÍ OPRAVA: Viditelně přidáme IP adresu do varování proti krádeži identity!
        msg = f"{jeho_nick} (z IP: {ip})\n{TEXTY['mb_receive_text'][self.jazyk]}\n📄 {nazev}\n💾 {velikost_mb} MB\n\n{TEXTY['mb_accept'][self.jazyk]}"
        
        titulek = f"{TEXTY['mb_receive_title'][self.jazyk]} ⚠️"
        
        if messagebox.askyesno(titulek, msg):
            ulozit_jako = filedialog.asksaveasfilename(initialfile=nazev)
            if ulozit_jako:
                with self.lock_soubory:
                    self.ocekavane_soubory[ip] = ulozit_jako
                    self.ocekavane_velikosti[ip] = int(velikost)
                self.poslat_udp_zpravu(f"__FILE_ACCEPT__:{req_id}", ip)
            else: self._odmitnout_soubor(ip, req_id)
        else: self._odmitnout_soubor(ip, req_id)
        
        self.zobrazena_zadost_o_soubor = False
        
    def _odmitnout_soubor(self, ip, req_id):
        self.poslat_udp_zpravu(f"__FILE_REJECT__:{req_id}", ip)

    # ==========================================
    # MOZEK SPRÁVCE ÚLOH (MULTITASKING)
    # ==========================================
    def toggle_ukoly(self):
        pocet = len(self.aktivni_ulohy)
        if self.ukoly_zobrazeny:
            self.frame_aktivity.pack_forget() # Schová rámeček
            self.btn_ukoly_toggle.configure(text=f"{TEXTY['btn_tasks_show'][self.jazyk]} ({pocet})")
            self.ukoly_zobrazeny = False
        else:
            # ROZBALENÍ SHORA: Zasuneme roletu přesně PŘED bílý seznam souborů!
            self.frame_aktivity.pack(before=self.list_souboru, fill="x", padx=5, pady=(0, 5))
            self.btn_ukoly_toggle.configure(text=f"{TEXTY['btn_tasks_hide'][self.jazyk]} ({pocet})")
            self.ukoly_zobrazeny = True
            
    def start_ukol(self, id_ukolu, text):
        row = ctk.CTkFrame(self.frame_aktivity, fg_color="#1e1e1e", height=30, corner_radius=4)
        row.pack(fill="x", pady=2)
        lbl = tk.Label(row, text=text, bg="#1e1e1e", fg="#f39c12", font=("Arial", 10, "bold"))
        lbl.pack(side="left", padx=10)
        pb = ttk.Progressbar(row, orient="horizontal", mode="determinate")
        pb.pack(side="right", fill="x", expand=True, padx=10)
        self.aktivni_ulohy[id_ukolu] = {"row": row, "lbl": lbl, "pb": pb}
        
        # Aktualizujeme číslo a překlad na tlačítku
        pocet = len(self.aktivni_ulohy)
        klic = "btn_tasks_hide" if self.ukoly_zobrazeny else "btn_tasks_show"
        self.btn_ukoly_toggle.configure(text=f"{TEXTY[klic][self.jazyk]} ({pocet})")
        
        # Pokud roletka není otevřená, sama se vysune, aby uživatel viděl progres
        if not self.ukoly_zobrazeny and pocet > 0:
            self.toggle_ukoly()

    def update_ukol(self, id_ukolu, text=None, procenta=None, mode=None):
        if id_ukolu in self.aktivni_ulohy:
            prvek = self.aktivni_ulohy[id_ukolu]
            if text: prvek["lbl"].config(text=text)
            if procenta is not None: prvek["pb"].config(value=procenta)
            if mode: prvek["pb"].config(mode=mode)
            if mode == "indeterminate": prvek["pb"].step(5)

    def konec_ukol(self, id_ukolu, text_hotovo, barva="#2ecc71"):
        if id_ukolu in self.aktivni_ulohy:
            prvek = self.aktivni_ulohy[id_ukolu]
            prvek["lbl"].config(text=text_hotovo, fg=barva)
            prvek["pb"].config(value=100, mode="determinate")
            # Úkol po 5 vteřinách sám potichu zmizí, aby nedělal bordel na obrazovce
            self.root.after(5000, lambda: self._smazat_ukol(id_ukolu))

    def _smazat_ukol(self, id_ukolu):
        if id_ukolu in self.aktivni_ulohy:
            try: self.aktivni_ulohy[id_ukolu]["row"].destroy()
            except: pass
            del self.aktivni_ulohy[id_ukolu]
            
        # Aktualizujeme číslo a překlad na tlačítku
        pocet = len(self.aktivni_ulohy)
        klic = "btn_tasks_hide" if self.ukoly_zobrazeny else "btn_tasks_show"
        try: self.btn_ukoly_toggle.configure(text=f"{TEXTY[klic][self.jazyk]} ({pocet})")
        except: pass
        
        # Pokud se smazal poslední úkol a jsme na nule, roletku potichu sama zavře
        if pocet == 0 and self.ukoly_zobrazeny:
            self.toggle_ukoly()
    # ==========================================    

    def odeslat_soubor_tcp(self, ip, cesta):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nazev_souboru = os.path.basename(cesta)
        # Vygenerujeme unikátní ID pro tento konkrétní přenos
        id_ukolu = f"send_{ip}_{nazev_souboru}_{time.time()}"
        
        # BEZPEČNÁ POJISTKA: Vytvoříme seznam stahujících, pokud ještě neexistuje
        if not hasattr(self, 'aktivni_stahovaci'): self.aktivni_stahovaci = set()
        
        try:
            self.aktivni_stahovaci.add(ip) # Přidáme IP do seznamu "žroutů linky"
            
            velikost = os.path.getsize(cesta)
            odeslano_bajtu = 0
            s.settimeout(3) 
            try:
                s.connect((ip, TCP_PORT))
            except:
                s.close()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((self.moje_ip, 0)) 
                s.settimeout(3)
                s.connect((ip, TCP_PORT))
            s.settimeout(None) 
            
            try: self.root.after(0, lambda: self.notebook.set(TEXTY["tab_files"][self.jazyk]))
            except: pass
            
            # Zapíšeme nový úkol do UI
            self.root.after(0, self.start_ukol, id_ukolu, f"Odesílám: {nazev_souboru} (0%)")
            
            posledni_aktualizace = time.time()
            bajty_od_posledni = 0 
            
            with open(cesta, 'rb') as f:
                while True:
                    data = f.read(1048576) 
                    if not data: break
                    s.sendall(data)
                    odeslano_bajtu += len(data)
                    bajty_od_posledni += len(data)
                    
                    nyni = time.time()
                    rozdil_casu = nyni - posledni_aktualizace
                    
                    if rozdil_casu > 0.5: 
                        procenta = int((odeslano_bajtu / velikost) * 100) if velikost > 0 else 0
                        rychlost_mb = (bajty_od_posledni / rozdil_casu) / (1024*1024)
                        txt = f"Odesílám: {nazev_souboru} ({procenta}%)  [{rychlost_mb:.1f} MB/s]"
                        # Aktualizujeme JEN tento konkrétní úkol
                        self.root.after(0, self.update_ukol, id_ukolu, txt, procenta)
                        
                        posledni_aktualizace = nyni
                        bajty_od_posledni = 0

            self.root.after(0, self.konec_ukol, id_ukolu, f"✅ Odesláno: {nazev_souboru}", "#2ecc71")
            
        except (ConnectionResetError, BrokenPipeError) as e:
            self.zapsat_do_logu(f"[TCP CHYBA] Spojení s {ip} bylo nečekaně přerušeno: {e}")
            self.root.after(0, self.konec_ukol, id_ukolu, f"❌ Zrušeno: {nazev_souboru}", "#e74c3c")
        except Exception as e: 
            self.root.after(0, self.konec_ukol, id_ukolu, f"❌ Chyba: {nazev_souboru}", "#e74c3c")
        finally:
            if ip in self.aktivni_stahovaci: self.aktivni_stahovaci.remove(ip) # Bezpečně odebere IP, i kdyby to spadlo!
            s.close()

    def _vlakno_tcp_naslouchani(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                server.bind(("0.0.0.0", TCP_PORT))
            except OSError:
                self.zapsat_do_logu("[CHYBA] TCP Port je obsazen. Nejspíš běží program dvakrát.")
                self.root.after(0, lambda: messagebox.showerror("Chyba spuštění", "Program už běží (TCP port je obsazen)! Zavři ostatní instance AutoLAN."))
                return 
                
            server.listen(5)
            self.tcp_server = server 
            while True:
                try:
                    conn, addr = server.accept()
                except OSError:
                    break 

                ip = addr[0]
                
                with self.lock_soubory:
                    # BEZPEČNOSTNÍ OPRAVA: Přijmeme soubor POUZE od té IP adresy, 
                    # se kterou jsme se dohodli přes žádost. Žádná slepá důvěra!
                    if ip in self.ocekavane_soubory:
                        cesta = self.ocekavane_soubory.pop(ip)
                        # OPRAVA: NEPOPUJEME velikost, pouze čteme, aby se mohla načíst za běhu.
                        velikost = self.ocekavane_velikosti.get(ip, 0)
                        # Přidáno 'ip' do argumentů
                        threading.Thread(target=self.prijmout_soubor_tcp, args=(conn, cesta, ip, velikost), daemon=True).start()
                    else: 
                        # Pokud se připojí neznámý útočník, okamžitě mu zabouchneme dveře
                        self.zapsat_do_logu(f"[BEZPEČNOST] Odmítnuto neznámé TCP spojení z IP: {ip}")
                        conn.close() 
        except Exception as e: self.zapsat_do_logu(f"[TCP SERVER CHYBA]: {e}")

    def prijmout_soubor_tcp(self, conn, cesta, ip, celkova_velikost=0):
        uspesne = False
        nazev_souboru = os.path.basename(cesta)
        id_ukolu = f"recv_{nazev_souboru}_{time.time()}"
        
        # Start úlohy v GUI
        txt_start = f"⬇️ Stahuji: {nazev_souboru}"
        if celkova_velikost > 0:
            txt_start += " (0%)"
        self.root.after(0, self.start_ukol, id_ukolu, txt_start)

        def vlakno_prijmu():
            uspesne = False
            aktualni_velikost = celkova_velikost
            try:
                prijato_bajtu = 0
                posledni_aktualizace = time.time()
                bajty_od_posledni = 0
                
                with open(cesta, 'wb') as f:
                    while True:
                        # OPRAVA: Dynamické načtení velikosti, pokud přišla zpožděně přes UDP
                        if aktualni_velikost <= 0:
                            with self.lock_soubory:
                                aktualni_velikost = self.ocekavane_velikosti.get(ip, 0)

                        if aktualni_velikost > 0:
                            chunk_size = min(524288, aktualni_velikost - prijato_bajtu)
                            if chunk_size <= 0: break 
                        else:
                            chunk_size = 524288

                        data = conn.recv(chunk_size) 
                        if not data: break
                        f.write(data)
                        prijato_bajtu += len(data)
                        bajty_od_posledni += len(data)
                        
                        nyni = time.time()
                        rozdil_casu = nyni - posledni_aktualizace
                        
                        if rozdil_casu > 0.5: 
                            rychlost_mb = (bajty_od_posledni / rozdil_casu) / (1024*1024)
                            if aktualni_velikost > 0:
                                procenta = int((prijato_bajtu / aktualni_velikost) * 100)
                                txt = f"⬇️ Stahuji: {nazev_souboru} ({procenta}%)  [{rychlost_mb:.1f} MB/s]"
                                self.root.after(0, self.update_ukol, id_ukolu, txt, procenta, "determinate")
                            else:
                                mb = round(prijato_bajtu / (1024*1024), 1)
                                txt = f"⬇️ Stahuji: {nazev_souboru} ({mb} MB)  [{rychlost_mb:.1f} MB/s]"
                                self.root.after(0, self.update_ukol, id_ukolu, txt, None, "indeterminate")
                                
                            posledni_aktualizace = nyni
                            bajty_od_posledni = 0
                        
                        if aktualni_velikost > 0 and prijato_bajtu >= aktualni_velikost:
                            break
                            
                uspesne = True
                self.root.after(0, self.konec_ukol, id_ukolu, f"✅ Staženo: {nazev_souboru}", "#3498db")
                self.root.after(0, self.obnovit_sdilenou_slozku)
                if self.zvuky_zapnuty:
                    try: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                    except: pass
            except Exception as e: 
                self.zapsat_do_logu(f"[TCP CHYBA]: {e}")
                self.root.after(0, self.konec_ukol, id_ukolu, f"❌ Chyba stahování: {nazev_souboru}", "#e74c3c")
            finally:
                conn.close()
                if not uspesne and os.path.exists(cesta):
                    try: os.remove(cesta)
                    except: pass
                # Úklid velikosti z paměti na samém konci
                with self.lock_soubory:
                    if ip in self.ocekavane_velikosti:
                        self.ocekavane_velikosti.pop(ip, None)

        threading.Thread(target=vlakno_prijmu, daemon=True).start()

    def start_naslouchani(self):
        threading.Thread(target=self._vlakno_naslouchani, daemon=True).start()
        threading.Thread(target=self._vlakno_tcp_naslouchani, daemon=True).start()

    def _vlakno_naslouchani(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("0.0.0.0", UDP_PORT))
            except OSError:
                self.zapsat_do_logu("[CHYBA] UDP Port je obsazen.")
                return 
            
            self.udp_sock = sock 
            while True:
                try:
                    data, adresa = sock.recvfrom(2048) 
                except OSError:
                    break 
                    
                text_zpravy = data.decode('utf-8', errors='ignore').strip()
                if not text_zpravy: continue
                
                ip_odesilatele = adresa[0]
                
                vsechny_moje_ip = self.ziskat_vsechny_moje_ip()
                if ip_odesilatele in vsechny_moje_ip or ip_odesilatele == self.moje_ip: 
                    continue
                
                # --- BEZPEČNOSTNÍ FILTR PRIVÁTNÍCH SÍTÍ ---
                try:
                    ip_obj = ipaddress.ip_address(ip_odesilatele)
                    # Propustí POUZE lokální LAN adresy (10.x.x.x, 172.16.x.x-172.31.x.x, 192.168.x.x) a localhost
                    if not (ip_obj.is_private or ip_obj.is_loopback):
                        continue
                except ValueError:
                    # Pokud by přišel nesmyslný formát IP adresy, ignorujeme
                    continue
                # -----------------------------------------
                
                if text_zpravy.startswith("__DIR_REQ__:"):
                    nyni = time.time()
                    if nyni - self.spam_ochrana_dir.get(ip_odesilatele, 0) < 2:
                        continue
                    self.spam_ochrana_dir[ip_odesilatele] = nyni
                    
                    muj_nick = self.entry_nick.get().strip() or "Neznámý"
                    
                    if self.cached_soubory:
                        # CHYTRÉ PORCOVÁNÍ: Zabrání zahození paketu routerem!
                        aktualni_balik = []
                        delka_baliku = 0
                        
                        for polozka in self.cached_soubory:
                            # Pokud by další soubor přetekl 1000 bajtů, odešleme to co máme a jedeme nanovo
                            if delka_baliku + len(polozka) > 1000:
                                seznam = "*".join(aktualni_balik)
                                self.poslat_udp_zpravu(f"__DIR_RES__:{muj_nick}:{seznam}", ip_odesilatele)
                                aktualni_balik = []
                                delka_baliku = 0
                                time.sleep(0.05) # Mikropauza, ať nezahltíme router
                            
                            aktualni_balik.append(polozka)
                            delka_baliku += len(polozka) + 1
                            
                        # Odešleme zbytek souborů
                        if aktualni_balik:
                            seznam = "*".join(aktualni_balik)
                            self.poslat_udp_zpravu(f"__DIR_RES__:{muj_nick}:{seznam}", ip_odesilatele)
                    continue

                if text_zpravy.startswith("__FILE_REQ__:"):
                    _, req_id, nazev, velikost, jeho_nick = text_zpravy.split(":", 4)
                    nyni = time.time()
                    if nyni - self.spam_ochrana_soubory.get(ip_odesilatele, 0) < 5:
                        continue 
                    self.spam_ochrana_soubory[ip_odesilatele] = nyni
                    self.root.after(0, self.dotaz_prijmout_soubor, ip_odesilatele, req_id, nazev, velikost, jeho_nick)
                    continue

                if text_zpravy.startswith("__DIR_RES__:"):
                    _, jeho_nick, seznam_hvezdicky = text_zpravy.split(":", 2)
                    soubory = seznam_hvezdicky.split("*")
                    with self.lock_soubory:
                        for polozka in soubory:
                            if "|" in polozka:
                                s, vel = polozka.split("|", 1)
                                text_velikosti = f"{vel} MB" if vel != "?" else "? MB"
                            else:
                                s = polozka
                                text_velikosti = "? MB"

                            polozka_klic = f"[{jeho_nick}] {s}" # Bezpečný tajný klíč
                            self.mapa_sdilenych_souboru[polozka_klic] = {"ip": ip_odesilatele, "soubor": s}
                            
                            def vloz_do_tabulky(soubor=s, nick=jeho_nick, velikost=text_velikosti):
                                try:
                                    # Přidáme do třetího sloupce skutečnou velikost!
                                    item_id = self.list_souboru.insert("", "end", values=(soubor, nick, velikost))
                                    self.list_souboru.item(item_id, tags=('cizisoubor',))
                                    self.list_souboru.tag_configure('cizisoubor', foreground='#3498db')
                                except: pass
                                
                            self.root.after(0, vloz_do_tabulky)
                    continue

                if text_zpravy.startswith("__DIR_GET__:"):
                    nazev_souboru = text_zpravy.split(":", 1)[1]
                    nazev_souboru = os.path.basename(nazev_souboru) 
                    cesta_k_souboru = os.path.join(SDILENA_SLOZKA, nazev_souboru)
                    if os.path.exists(cesta_k_souboru):
                        # --- PŘENOS VELIKOSTI (Oprava Progressbaru pro Stahování) ---
                        try:
                            velikost = os.path.getsize(cesta_k_souboru)
                            self.poslat_udp_zpravu(f"__FILE_SIZE_INFO__:{velikost}", ip_odesilatele)
                        except: pass
                        
                        # Dáme počítači stahovatele přesně půl vteřiny na to, aby zpracoval 
                        # UDP informaci o velikosti, a pak na něj rovnou vypálíme TCP spojení.
                        def zpozdene_odeslani():
                            time.sleep(0.5)
                            self.odeslat_soubor_tcp(ip_odesilatele, cesta_k_souboru)
                            
                        threading.Thread(target=zpozdene_odeslani, daemon=True).start()
                        # -----------------------------------------------------------
                    continue
                    
                # Zachytávač informace o velikosti souboru od odesílatele
                if text_zpravy.startswith("__FILE_SIZE_INFO__:"):
                    try:
                        velikost = int(text_zpravy.split(":", 1)[1])
                        with self.lock_soubory:
                            if ip_odesilatele in self.ocekavane_velikosti:
                                self.ocekavane_velikosti[ip_odesilatele] = velikost
                    except: pass
                    continue

                if text_zpravy.startswith("__FILE_ACCEPT__:"):
                    req_id = text_zpravy.split(":")[1]
                    with self.lock_soubory:
                        if req_id in self.sdileni_ceka_na_prijemci:
                            cesta = self.sdileni_ceka_na_prijemci.pop(req_id)
                            threading.Thread(target=self.odeslat_soubor_tcp, args=(ip_odesilatele, cesta), daemon=True).start()
                    continue

                if text_zpravy.startswith("__FILE_REJECT__:"):
                    req_id = text_zpravy.split(":")[1]
                    with self.lock_soubory:
                        if req_id in self.sdileni_ceka_na_prijemci: self.sdileni_ceka_na_prijemci.pop(req_id)
                    continue

                if text_zpravy == "__DISCOVER__":
                    muj_nick = self.entry_nick.get().strip() or "Neznámý"
                    moje_hra = self.zjisti_moji_hru() 
                    self.poslat_udp_zpravu(f"__IAM__:{muj_nick}:{moje_hra}", ip_odesilatele)
                    continue
                
                if text_zpravy.startswith("__IAM__:") or text_zpravy.startswith("__HEARTBEAT__:"):
                    casti = text_zpravy.split(":", 2)
                    jeho_nick = casti[1]
                    jeho_hra = casti[2] if len(casti) > 2 else "" 
                    self.root.after(0, self.automaticky_pridat_do_gui, ip_odesilatele, jeho_nick, jeho_hra)
                    with self.lock_hraci:
                        if ip_odesilatele in self.seznam_hracu:
                            self.seznam_hracu[ip_odesilatele]["posledni_aktivita"] = time.time()
                    continue

                if text_zpravy.startswith("__ACK__:"):
                    msg_id = text_zpravy.split(":")[1]
                    with self.lock_statistiky:
                        if msg_id in self.cekajici_zpravy: self.cekajici_zpravy.remove(msg_id)
                    continue

                if text_zpravy.startswith("__MSG__:"):
                    casti = text_zpravy.split(":", 3)
                    if len(casti) == 4:
                        prefix, msg_id, jeho_nick, samotny_text = casti
                        
                        # --- OCHRANA PROTI OZVĚNĚ (Filtrování trojitých paketů) ---
                        if not hasattr(self, 'prijata_id_zprav'):
                            self.prijata_id_zprav = set()
                            
                        # Pokud už jsme zprávu s tímto ID před milisekundou dostali, zahodíme ji
                        if msg_id in self.prijata_id_zprav:
                            self.poslat_udp_zpravu(f"__ACK__:{msg_id}", ip_odesilatele)
                            continue
                            
                        self.prijata_id_zprav.add(msg_id)
                        # Pokud by paměť nabobtnala, promažeme ji (500 zpráv na LANku stačí)
                        if len(self.prijata_id_zprav) > 500:
                            self.prijata_id_zprav.clear()
                        # ---------------------------------------------------------

                        self.poslat_udp_zpravu(f"__ACK__:{msg_id}", ip_odesilatele)
                        with self.lock_statistiky:
                            self.prijato += 1
                        self.root.after(0, self.zobrazit_prijatou_zpravu, ip_odesilatele, f"{jeho_nick}: {samotny_text}")
                    continue

                # --- PŘÍJEM POZVÁNKY DO TÝMU (AUTO-OTEVŘENÍ OKNA) ---
                if text_zpravy.startswith("__SQUAD_INVITE__:"):
                    casti = text_zpravy.split(":", 2)
                    if len(casti) == 3:
                        seznam_ip_str = casti[1]
                        seznam_jmen_str = casti[2]
                        
                        vsechny_ip = seznam_ip_str.split(",")
                        vsechna_jmena = seznam_jmen_str.split(",")
                        
                        # Vyfiltrujeme z toho balíku sami sebe (sami sobě hlas posílat nepotřebujeme)
                        cizi_ip = []
                        cizi_jmena = []
                        for ip_kolegy, jmeno_kolegy in zip(vsechny_ip, vsechna_jmena):
                            if ip_kolegy != self.moje_ip and ip_kolegy != "127.0.0.1":
                                cizi_ip.append(ip_kolegy)
                                cizi_jmena.append(jmeno_kolegy)
                        
                        if not (hasattr(self, 'tymove_okno_aktivni') and self.tymove_okno_aktivni):
                            if self.zvuky_zapnuty:
                                try: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                                except: pass
                            # Otevřeme Týmové okno rovnou s kompletním seznamem VŠECH hráčů!
                            self.root.after(0, self.otevrit_tymovou_mistnost, cizi_ip, cizi_jmena)
                        else:
                            # Pokud už běží, zkontrolujeme, jestli nepřibyl někdo nový
                            for ip_kolegy, jm in zip(cizi_ip, cizi_jmena):
                                if ip_kolegy not in getattr(self, 'tym_ip_adresy', []):
                                    self.tym_ip_adresy.append(ip_kolegy)
                                    self.root.after(0, lambda n=jm: self.tymovy_chat.insert("end", TEXTY["msg_squad_joined"][self.jazyk].format(n)))
                    continue

                # --- PŘÍJEM TAJNÝCH ZPRÁV JEN PRO TÝMOVÝ CHAT ---
                if text_zpravy.startswith("__SQUAD__:"):
                    casti = text_zpravy.split(":", 3)
                    if len(casti) == 4:
                        _, msg_id, jeho_nick, samotny_text = casti
                        
                        # Záchrana: Pokud ještě nemáme okno (pozvánka se někde ztratila), otevřeme ho hned teď
                        if not (hasattr(self, 'tymove_okno_aktivni') and self.tymove_okno_aktivni):
                            self.root.after(0, self.otevrit_tymovou_mistnost, [ip_odesilatele], [jeho_nick])
                            time.sleep(0.3) # Malá pauza na vykreslení nového okna
                            
                        # Přidáme tě k němu do povolených IP adres (tzv. Voice Whitelist)
                        if ip_odesilatele not in getattr(self, 'tym_ip_adresy', []):
                            self.tym_ip_adresy.append(ip_odesilatele)
                            
                        # Vypíšeme text do toho černého chatboxu
                        if hasattr(self, 'tymove_okno_aktivni') and self.tymove_okno_aktivni:
                            def pridej_squad_msg(n=jeho_nick, t=samotny_text):
                                try:
                                    self.tymovy_chat.insert("end", f"{n}: {t}")
                                    self.tymovy_chat.itemconfig("end", fg="#3498db") # Obarvíme jméno a zprávu modře
                                    self.tymovy_chat.yview("end")
                                except: pass
                            self.root.after(0, pridej_squad_msg)
                    continue
                # ------------------------------------------------
                
                if not text_zpravy.startswith("__"):
                    continue 
                    
        except Exception as e: 
            self.zapsat_do_logu(f"[UDP NASLOUCHÁNÍ CHYBA]: {e}")

    def otevrit_okno_chatu(self, ip, jmeno):
        if ip in self.okna_chatu and self.okna_chatu[ip].winfo_exists():
            self.okna_chatu[ip].master.focus()
            return
            
        okno = ctk.CTkToplevel(self.root)
        okno.title(f"{TEXTY['win_priv_chat'][self.jazyk]}: {jmeno} ({ip})")
        okno.geometry("500x420")
        okno.configure(fg_color="#141414")
        okno.attributes('-topmost', 'true')
        
        historie = tk.Listbox(okno, bg="#ffffff", fg="#000000", font=("Arial", 12), selectbackground="#e0e0e0", bd=1, relief="solid")
        historie.pack(fill="both", expand=True, padx=10, pady=10)
        
        ramecek_dole = ctk.CTkFrame(okno, fg_color="transparent")
        ramecek_dole.pack(fill="x", padx=10, pady=(0, 10))
        
        vstup = ctk.CTkEntry(ramecek_dole, font=("Arial", 14), height=45, corner_radius=8, fg_color="#ffffff", text_color="#000000", border_color="#cccccc")
        vstup.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def odeslat(event=None):
            text = vstup.get().strip()
            if text:
                self.poslat_zpravu_na_pozadi(ip, text, historie)
                vstup.delete(0, tk.END)
                
        vstup.bind("<Return>", odeslat) 
        btn_odeslat = ctk.CTkButton(ramecek_dole, text=TEXTY["btn_send"][self.jazyk], command=odeslat, fg_color="#3498db", hover_color="#2980b9", font=("Arial", 13, "bold"), width=110, height=45, corner_radius=8)
        btn_odeslat.pack(side="right")
        self.okna_chatu[ip] = historie 

    def poslat_zpravu_na_pozadi(self, cilova_ip, zprava, okno_historie):
        muj_nick = self.entry_nick.get().strip() or "Neznámý"
        msg_id = str(int(datetime.datetime.now().timestamp() * 1000))
        cas = datetime.datetime.now().strftime("%H:%M:%S")
        self.poslat_udp_zpravu(f"__MSG__:{msg_id}:{muj_nick}:{zprava}", cilova_ip)
        
        with self.lock_statistiky:
            self.odeslano += 1
            self.cekajici_zpravy.add(msg_id)
        okno_historie.insert("end", f"[{cas}] {TEXTY['msg_you'][self.jazyk]}: {zprava}")
        okno_historie.itemconfig("end", fg="#2980b9") 
        okno_historie.yview("end")
        self.aktualizuj_statistiky()
        self.root.after(2000, lambda: self.zkontroluj_doruceni(msg_id, cilova_ip, okno_historie))

    def zkontroluj_doruceni(self, msg_id, ip, okno_historie):
        with self.lock_statistiky:
            je_cekajici = msg_id in self.cekajici_zpravy
            if je_cekajici:
                self.cekajici_zpravy.remove(msg_id)
                
        if je_cekajici and okno_historie.winfo_exists():
            okno_historie.insert("end", TEXTY["msg_not_delivered"][self.jazyk])
            okno_historie.itemconfig("end", fg="#e67e22") 

    def zobrazit_prijatou_zpravu(self, ip, text):
        cas = datetime.datetime.now().strftime("%H:%M:%S")
        jmeno_odesilatele = text.split(":")[0].strip() if ":" in text else ip
        
        # 1. Zjistíme, jestli to je náš tajný kód
        je_tajny_kod = "IDKFA" in text.upper()
        
        if je_tajny_kod:
            self.root.after(0, self.spustit_duhove_silenstvi)
        elif self.zvuky_zapnuty:  # <--- OPRAVA: Normální "cinknutí" zahrajeme JEN KDYŽ to není Doom!
            try: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
            except: pass
        
        self.chat_box.insert("end", f"[{cas}] [{ip}] {text}")
        
        # --- OPRAVA: Pokud je to hromadná zpráva (obsahuje tlampač), neotevíráme soukromé okno! ---
        if "📢" in text:
            # Obarvíme to v hlavním chatu oranžově, ať to vynikne (Nyní 100% bezpečně)
            self.chat_box.itemconfig(self.chat_box.size() - 1, fg="#e67e22") 
            self.chat_box.yview("end")
            self.aktualizuj_statistiky()
            return # <--- Tady funkci ukončíme. Nevyvolá se tak to otravné okno!
        # -----------------------------------------------------------------------------------------
        
        self.chat_box.yview("end")

        if not (ip in self.okna_chatu and self.okna_chatu[ip].winfo_exists()):
            self.otevrit_okno_chatu(ip, jmeno_odesilatele)
            
        if ip in self.okna_chatu and self.okna_chatu[ip].winfo_exists():
            self.okna_chatu[ip].insert("end", f"[{cas}] {text}")
            self.okna_chatu[ip].yview("end")
            try:
                okno_master = self.okna_chatu[ip].master
                okno_master.deiconify()
                okno_master.lift()
                okno_master.focus_force()
            except: pass

        self.aktualizuj_statistiky()

    def ziskat_spravne_broadcasty(self):
        # LÍNÁ PAMĚŤ (CACHE): Nezatěžujeme procesor neustálým zjišťováním hardwaru.
        # Výsledek si zapamatujeme a znovu se Windows zeptáme až za 15 vteřin!
        nyni = time.time()
        if hasattr(self, 'posledni_broadcasty') and hasattr(self, 'cas_poslednich_broadcastu'):
            if nyni - self.cas_poslednich_broadcastu < 15:
                return self.posledni_broadcasty

        broadcasty = set(['255.255.255.255'])
        
        # OPRAVA: 100% spolehlivý matematický fallback, i když chybí speciální knihovny
        if self.moje_ip and self.moje_ip != "127.0.0.1":
            casti = self.moje_ip.split('.')
            if len(casti) == 4:
                # Z 192.168.0.15 udělá 192.168.0.255
                cilova_adresa = f"{casti[0]}.{casti[1]}.{casti[2]}.255"
                broadcasty.add(cilova_adresa)
                
        try:
            import psutil
            sitova_rozhrani = psutil.net_if_addrs()
            for nazev_adapteru, adresy in sitova_rozhrani.items():
                for addr in adresy:
                    if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                        if addr.netmask:
                            sit = ipaddress.IPv4Network(f"{addr.address}/{addr.netmask}", strict=False)
                            broadcasty.add(str(sit.broadcast_address))
        except Exception as e:
            self.zapsat_do_logu(f"Nepodařilo se zjistit přesné broadcasty: {e}")
            
        vysledek = list(broadcasty)
        
        # Uložíme výsledek do paměti pro příštích 15 vteřin
        self.posledni_broadcasty = vysledek
        self.cas_poslednich_broadcastu = nyni
        
        return vysledek

    def poslat_rozhlas(self):
        zprava = self.entry_rozhlas.get().strip()
        if not zprava: return
        if "IDKFA" in zprava.upper():
            self.spustit_duhove_silenstvi()
        
        muj_nick = self.entry_nick.get().strip() or "Neznámý"
        msg_id = str(int(datetime.datetime.now().timestamp() * 1000))
        
        # 1. GIGANTICKÁ OPRAVA: Přímé doručení všem na radaru (Unicast) - 100% spolehlivost!
        with self.lock_hraci:
            vsichni_hraci = list(self.seznam_hracu.keys())
            
        for cilova_ip in vsichni_hraci:
            self.poslat_udp_zpravu(f"__MSG__:{msg_id}:{muj_nick}:📢 {zprava}", cilova_ip)
            
        # 2. Klasický plošný výkřik (Broadcast) pro jistotu, kdyby někdo zrovna program zapínal a nebyl na radaru
        for cilova_adresa in self.ziskat_spravne_broadcasty():
            self.poslat_udp_zpravu(f"__MSG__:{msg_id}:{muj_nick}:📢 {zprava}", cilova_adresa, broadcast=True)
            
        cas = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_box.insert("end", f"[{cas}] [TY - ROZHLAS]: 📢 {zprava}")
        # Bezpečný zápis barvy pro všechny verze Windows
        self.chat_box.itemconfig(self.chat_box.size() - 1, fg="#e67e22") 
        self.chat_box.yview("end")
        
        self.entry_rozhlas.delete(0, tk.END)

    def otevrit_firewall_windows(self):
        try:
            prikaz = "control /name Microsoft.WindowsFirewall /page pageConfigureApps"
            subprocess.Popen(prikaz, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e: self.zapsat_do_logu(f"[FIREWALL CMD CHYBA]: {e}")

    def automaticky_pridat_do_gui(self, ip, jmeno, hra_z_procesu=""):
        with self.lock_hraci:
            if ip in self.seznam_hracu:
                if self.seznam_hracu[ip]["jmeno"] != jmeno:
                    self.seznam_hracu[ip]["jmeno"] = jmeno
                    self.seznam_hracu[ip]["label"].configure(text=f"{jmeno} ({ip})")
                    if ip in self.okna_chatu and self.okna_chatu[ip].winfo_exists():
                        self.okna_chatu[ip].master.title(f"{TEXTY['win_priv_chat'][self.jazyk]}: {jmeno} ({ip})")
                self.seznam_hracu[ip]["hra_z_procesu"] = hra_z_procesu
                return
                
            row = ctk.CTkFrame(self.frame_seznam_hracu, fg_color="#1e1e1e", corner_radius=6)
            row.pack(fill="x", pady=2)
            
            # --- NOVÉ: Zaškrtávátko pro výběr do týmu ---
            chk_tým = ctk.CTkCheckBox(row, text="", width=24, checkbox_width=24, checkbox_height=24, fg_color="#3498db", hover_color="#2980b9")
            chk_tým.pack(side="left", padx=(10, 0), pady=4)
            # --------------------------------------------

            btn_del = ctk.CTkButton(row, text="❌", command=lambda cil_ip=ip: self.odstranit_hrace(cil_ip), fg_color="#c0392b", hover_color="#922b21", font=("Arial", 12), width=30, height=28, corner_radius=4)
            btn_del.pack(side="right", padx=5, pady=4)
            
            btn_file = ctk.CTkButton(row, text=TEXTY["btn_file_player"][self.jazyk], command=lambda cil_ip=ip: self.vybrat_a_poslat_soubor(cil_ip), fg_color="#e67e22", hover_color="#ca6f1e", text_color="white", font=("Arial", 12, "bold"), width=70, height=28, corner_radius=4)
            btn_file.pack(side="right", padx=2, pady=4)
            
            btn_msg = ctk.CTkButton(row, text=TEXTY["btn_chat_player"][self.jazyk], command=lambda cil_ip=ip: self.otevrit_okno_chatu(cil_ip, self.seznam_hracu[cil_ip]["jmeno"] if cil_ip in self.seznam_hracu else jmeno), fg_color="#9b59b6", hover_color="#732d91", text_color="white", font=("Arial", 12, "bold"), width=70, height=28, corner_radius=4)
            btn_msg.pack(side="right", padx=2, pady=4)
            
            canvas = tk.Canvas(row, width=20, height=20, bg="#1e1e1e", highlightthickness=0)
            dot = canvas.create_oval(5, 5, 15, 15, fill="gray")
            canvas.pack(side="left", padx=10, pady=4)
            
            lbl = ctk.CTkLabel(row, text=f"{jmeno} ({ip})", anchor="w", text_color="white", font=("Arial", 12))
            lbl.pack(side="left", fill="x", expand=True)
            
            lbl_hra = ctk.CTkLabel(row, text="", width=150, anchor="w", text_color="#f1c40f", font=("Arial", 11, "bold"))
            lbl_hra.pack(side="left", padx=5)
            
            self.seznam_hracu[ip] = {"jmeno": jmeno, "dot": dot, "canvas": canvas, "frame": row, "label": lbl, "label_hra": lbl_hra, "odeslano": 0, "prijato": 0, "btn_file": btn_file, "btn_msg": btn_msg, "hra_z_procesu": hra_z_procesu, "posledni_aktivita": time.time(), "chk_tym": chk_tým}
        
        self.spustit_kontrolu_ihned()

    def zalozit_tym(self):
        vybrane_ip = []
        jmena = []
        with self.lock_hraci:
            for ip, data in self.seznam_hracu.items():
                try:
                    if data.get("chk_tym") and str(data["chk_tym"].get()) == "1":
                        vybrane_ip.append(ip)
                        jmena.append(data.get("jmeno", "Hráč"))
                except: pass
                    
        if not vybrane_ip:
            messagebox.showwarning("Prázdný tým" if self.jazyk == "CZ" else "Empty Squad", TEXTY["msg_empty_squad"][self.jazyk])
            return
            
        # --- NOVÝ OCHRANNÝ LIMIT SÍTĚ ---
        if len(vybrane_ip) > 5: # 5 cizích hráčů + ty = 6 maximálně
            varovani_cz = "Maximální velikost týmu pro čistý zvuk je 6 hráčů (Ty + 5 dalších).\n\nOdškrtni pár lidí na radaru a zkus to znovu."
            varovani_en = "Maximum squad size for clear audio is 6 players (You + 5 others).\n\nUncheck a few people and try again."
            messagebox.showwarning("Příliš velký tým" if self.jazyk == "CZ" else "Squad too big", varovani_cz if self.jazyk == "CZ" else varovani_en)
            return
        # --------------------------------
            
        self.otevrit_tymovou_mistnost(vybrane_ip, jmena)
        
        muj_nick = self.entry_nick.get().strip() or "Neznámý"
        
        # --- OPRAVA: SÍŤOVÁ PAVUČINA (MESH) ---
        # Zabalíme VŠECHNY IP adresy a VŠECHNA jména do jednoho obřího balíku,
        # aby se kluci znali navzájem a mohli si posílat hlas i mezi sebou!
        vsechny_ip = vybrane_ip + [self.moje_ip]
        vsechna_jmena = jmena + [muj_nick]
        
        seznam_ip_str = ",".join(vsechny_ip)
        seznam_jmen_str = ",".join(vsechna_jmena)
        
        for ip in vybrane_ip:
            # Pošleme novou pozvánku: __SQUAD_INVITE__ : IP1,IP2,IP3 : Jmeno1,Jmeno2,Jmeno3
            self.poslat_udp_zpravu(f"__SQUAD_INVITE__:{seznam_ip_str}:{seznam_jmen_str}", ip)

    def otevrit_tymovou_mistnost(self, hraci_ip_seznam, jmena_hracu):
        if hasattr(self, 'tymove_okno') and self.tymove_okno is not None and self.tymove_okno.winfo_exists():
            self.tymove_okno.focus()
            return

        try:
            import pyaudio
            self.audio_modul = pyaudio.PyAudio()
        except ImportError:
            messagebox.showerror("Chyba" if self.jazyk == "CZ" else "Error", TEXTY["msg_pyaudio_err"][self.jazyk])
            return

        self.tym_ip_adresy = hraci_ip_seznam 
        self.tym_jmena_hracu = jmena_hracu # Uložíme jména pro překlady
        self.tymove_okno_aktivni = True

        self.tymove_okno = ctk.CTkToplevel(self.root)
        self.tymove_okno.title(f"{TEXTY['win_squad_title'][self.jazyk]} {', '.join(jmena_hracu)}")
        self.tymove_okno.geometry("650x450")
        self.tymove_okno.configure(fg_color="#141414")
        self.tymove_okno.attributes('-topmost', 'true') 
        
        self.tymove_okno.protocol("WM_DELETE_WINDOW", self.zavrit_tymovou_mistnost)

        lbl_nadpis = ctk.CTkLabel(self.tymove_okno, text=TEXTY["lbl_squad_comms"][self.jazyk], font=("Arial", 16, "bold"), text_color="#2ecc71")
        lbl_nadpis.pack(pady=(15, 5))

        self.tymovy_chat = tk.Listbox(self.tymove_okno, bg="#1e1e1e", fg="#ffffff", font=("Arial", 12), selectbackground="#3498db", bd=1, relief="solid")
        self.tymovy_chat.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.tymovy_chat.insert("end", f"{TEXTY['msg_squad_welcome'][self.jazyk]} {', '.join(jmena_hracu)}")
        self.tymovy_chat.itemconfig("end", fg="#f1c40f")

        ramecek_dole = ctk.CTkFrame(self.tymove_okno, fg_color="transparent")
        ramecek_dole.pack(fill="x", padx=15, pady=15)

        self.mikrofon_zapnuty = False
        self.btn_mikrofon = ctk.CTkButton(ramecek_dole, text=TEXTY["btn_mic_on"][self.jazyk], fg_color="#e74c3c", hover_color="#c0392b", font=("Arial", 13, "bold"), height=45, width=170, command=self.prepni_mikrofon)
        self.btn_mikrofon.pack(side="left", padx=(0, 5))

        self.btn_nastaveni_mic = ctk.CTkButton(ramecek_dole, text=TEXTY["btn_settings"][self.jazyk], fg_color="#7f8c8d", hover_color="#95a5a6", font=("Arial", 12, "bold"), height=45, width=100, command=self.otevrit_nastaveni_mikrofonu)
        self.btn_nastaveni_mic.pack(side="left", padx=(0, 10))

        self.vstup_tym_chat = ctk.CTkEntry(ramecek_dole, font=("Arial", 14), height=45, placeholder_text=TEXTY["ph_squad_chat"][self.jazyk])
        self.vstup_tym_chat.pack(side="left", fill="x", expand=True)

        def poslat_do_tymu(event=None):
            txt = self.vstup_tym_chat.get().strip()
            if txt:
                muj_nick = self.entry_nick.get().strip() or "Neznámý"
                self.tymovy_chat.insert("end", f"{TEXTY['msg_you'][self.jazyk]}: {txt}")
                self.tymovy_chat.itemconfig("end", fg="#3498db")
                self.tymovy_chat.yview("end")
                self.vstup_tym_chat.delete(0, tk.END)
                
                msg_id = str(int(datetime.datetime.now().timestamp() * 1000))
                for ip in self.tym_ip_adresy:
                    self.poslat_udp_zpravu(f"__SQUAD__:{msg_id}:{muj_nick}:{txt}", ip)

        self.vstup_tym_chat.bind("<Return>", poslat_do_tymu)
        threading.Thread(target=self._prijimat_hlas, daemon=True).start()

    def prepni_mikrofon(self):
        self.mikrofon_zapnuty = not self.mikrofon_zapnuty
        if self.mikrofon_zapnuty:
            self.btn_mikrofon.configure(text=TEXTY["btn_mic_active"][self.jazyk], fg_color="#2ecc71", hover_color="#27ae60")
            self.tymovy_chat.insert("end", TEXTY["msg_mic_connecting"][self.jazyk])
            self.tymovy_chat.itemconfig("end", fg="#2ecc71")
            threading.Thread(target=self._vysilat_mikrofon, daemon=True).start()
        else:
            self.btn_mikrofon.configure(text=TEXTY["btn_mic_on"][self.jazyk], fg_color="#e74c3c", hover_color="#c0392b")
            self.tymovy_chat.insert("end", TEXTY["msg_mic_muted"][self.jazyk])
            self.tymovy_chat.itemconfig("end", fg="#e74c3c")
        self.tymovy_chat.yview("end")
        
    def zavrit_tymovou_mistnost(self):
        # Okamžitě deaktivujeme smyčky, ať se zastaví nahrávání
        self.tymove_okno_aktivni = False
        self.mikrofon_zapnuty = False
        
        # OPRAVA BMAX: Vůbec nevoláme self.audio_modul.terminate()! 
        # C-čkové ovladače zvuku na slabých PC při tom zamrzají (Deadlock).
        # Necháme sokety a streamy dožít a zavřít se přirozeně ve svých vláknech.
        
        # Okamžitě zničíme grafické okno, ať uživatel nečeká
        try: 
            if hasattr(self, 'tymove_okno') and self.tymove_okno.winfo_exists():
                self.tymove_okno.destroy()
        except: pass

    def otevrit_nastaveni_mikrofonu(self):
        try:
            # Magický příkaz, který ve Windows otevře přesně záložku "Záznam" s mikrofony!
            subprocess.Popen("control mmsys.cpl,,1", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            self.zapsat_do_logu(f"[CHYBA] Nelze otevřít nastavení mikrofonu: {e}")   

    def _vysilat_mikrofon(self):
        import pyaudio
        CHUNK = 512 # Malé balíčky (512 bajtů) = menší zpoždění a plynulejší LAN síť
        FORMAT = pyaudio.paInt16
        CHANNELS = 1 # Mono (pro lidský hlas to bohatě stačí a šetří to 50% dat)
        RATE = 16000 # Širokopásmový VoIP standard (16 kHz zní hezky čistě a neničí síť)
        
        stream = None
        sock = None
        try:
            stream = self.audio_modul.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            while self.mikrofon_zapnuty and self.tymove_okno_aktivni:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    for ip in self.tym_ip_adresy:
                        sock.sendto(data, (ip, VOICE_PORT))
                except: break
        except Exception as e:
            try: self.root.after(0, lambda: self.tymovy_chat.insert("end", f"[CHYBA MIKROFONU]: {e}"))
            except: pass
        finally:
            # 100% BEZPEČNÝ ÚKLID
            try: 
                if stream:
                    stream.stop_stream()
                    stream.close()
            except: pass
            try: 
                if sock: sock.close()
            except: pass

    def _prijimat_hlas(self):
        import pyaudio
        CHUNK = 512
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        stream = None
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Nastavíme krátký timeout, aby soket nečekal věčně, když uživatel zavírá okno
            sock.settimeout(0.5) 
            sock.bind(("0.0.0.0", VOICE_PORT))

            stream = self.audio_modul.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
            
            while self.tymove_okno_aktivni:
                try:
                    data, addr = sock.recvfrom(4096) 
                    ip_odesilatele = addr[0]
                    if ip_odesilatele in self.tym_ip_adresy:
                        stream.write(data)
                except socket.timeout:
                    # Timeout zafunguje jako "nádech", umožní while cyklu zkontrolovat, jestli už okno není zavřené
                    continue
                except:
                    break
        except OSError:
            try: self.root.after(0, lambda: self.tymovy_chat.insert("end", TEXTY["msg_voice_port_err"][self.jazyk]))
            except: pass
        finally:
            # 100% BEZPEČNÝ ÚKLID
            try:
                if stream:
                    stream.stop_stream()
                    stream.close()
            except: pass
            try:
                if sock: sock.close()
            except: pass   

    def odstranit_hrace(self, ip):
        frame_k_smazani = None
        with self.lock_hraci:
            if ip in self.seznam_hracu:
                frame_k_smazani = self.seznam_hracu[ip].get("frame", None)
                del self.seznam_hracu[ip]
                
        if frame_k_smazani:
            try:
                # Kontrola existence a bezpečné zničení
                self.root.after(0, lambda f=frame_k_smazani: f.destroy() if f and f.winfo_exists() else None)
                self.root.after(0, lambda i=ip: self.chat_box.insert("end", f"{TEXTY['msg_player_removed'][self.jazyk]} {i}"))
            except: pass

    def prohledat_sit(self):
        self.root.config(cursor="wait")
        self.chat_box.insert("end", TEXTY["msg_scan_start"][self.jazyk])
        self.chat_box.itemconfig("end", fg="#8e44ad")
        
        def skenovat():
            self._odeslat_discover_broadcast()
            self.root.after(2000, lambda: self.root.config(cursor=""))
            self.root.after(2000, lambda: self.chat_box.insert("end", TEXTY["msg_scan_done"][self.jazyk]))
            self.root.after(2000, lambda: self.chat_box.itemconfig("end", fg="#8e44ad"))
        threading.Thread(target=skenovat, daemon=True).start()

    def _odeslat_discover_broadcast(self):
        # 1. Agresivní výkřik na celou síť (starý způsob)
        self.poslat_udp_zpravu("__DISCOVER__", '255.255.255.255', broadcast=True)
        # 2. Přesně mířený výkřik do konkrétních pod-sítí (nový způsob)
        for cilovy_broadcast in self.ziskat_spravne_broadcasty():
            self.poslat_udp_zpravu("__DISCOVER__", cilovy_broadcast, broadcast=True)

    def _odeslat_heartbeat(self):
        muj_nick = self.entry_nick.get().strip() or "Neznámý"
        moje_hra = self.zjisti_moji_hru()
        zprava = f"__HEARTBEAT__:{muj_nick}:{moje_hra}"
        
        self.poslat_udp_zpravu(zprava, '255.255.255.255', broadcast=True)
        for cilova_adresa in self.ziskat_spravne_broadcasty():
            self.poslat_udp_zpravu(zprava, cilova_adresa, broadcast=True)

    def zkontrolovat_hry(self, ip):
        nalezene_hry = set() 
        for port_str, nazev in ZNAME_HRY.items():
            if "-" in str(port_str):
                start, konec = map(int, str(port_str).split("-"))
                # KRIZOVÁ OPRAVA: Skenujeme POUZE první 3 porty z každého rozsahu.
                # Jinak by obří rozsahy (např. 778 portů) program úplně udusily!
                konec = min(konec, start + 2) 
                porty_ke_kontrole = range(start, konec + 1)
            else:
                porty_ke_kontrole = [int(port_str)]
                
            for p in porty_ke_kontrole:
                nalezeno = False
                
                # 1. ZKOUŠKA TCP (Klasické spojení)
                s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_tcp.settimeout(0.05) 
                try:
                    if s_tcp.connect_ex((ip, p)) == 0: 
                        nalezene_hry.add(f"{nazev} (TCP: {p})")
                        nalezeno = True
                except: pass
                finally: s_tcp.close()
                
                if nalezeno:
                    break # Hru jsme našli, nemusíme zkoušet UDP a jdeme na další hru v seznamu
                    
                # 2. ZKOUŠKA UDP (Pro střílečky a dedikované servery)
                s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s_udp.settimeout(0.05)
                try:
                    # Pošleme prázdný "ťukanec"
                    s_udp.sendto(b'\x00', (ip, p))
                    # Zkusíme si poslechnout odpověď.
                    # Pokud je port mrtvý, Windows Firewall to často shodí chybou.
                    data, _ = s_udp.recvfrom(1024)
                    nalezene_hry.add(f"{nazev} (UDP: {p})")
                    break
                except socket.timeout:
                    # Timeout u UDP je zrádný (může to být hra, nebo jen přísný firewall).
                    # Raději ignorujeme, abychom neměli falešné poplachy.
                    pass
                except ConnectionResetError:
                    # Port je 100% zavřený, nic tam neběží.
                    pass
                except: pass
                finally: s_udp.close()
                
        return list(nalezene_hry)       

    def zjisti_moji_hru(self):
        # LÍNÝ ŠPION: Nezatěžujeme procesor neustálým spouštěním 'tasklist.exe'.
        # Kontrolujeme spuštěné hry jen jednou za 15 vteřin. Zabrání to mikrozásekům ve hrách!
        nyni = time.time()
        if hasattr(self, 'posledni_kontrola_her') and (nyni - self.posledni_kontrola_her < 15):
            return getattr(self, 'posledni_nalezena_hra', "")
            
        self.posledni_kontrola_her = nyni
        self.posledni_nalezena_hra = ""
        
        try:
            vystup = subprocess.check_output(["tasklist", "/NH", "/FO", "CSV"], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            vystup_mala_pismena = vystup.lower()
            for exe, nazev in ZNAME_PROCESY.items():
                if exe.lower() in vystup_mala_pismena:
                    nalezeny_port = self.najdi_port_procesu(exe)
                    if nalezeny_port:
                        self.posledni_nalezena_hra = f"{nazev} (Port: {nalezeny_port})"
                        return self.posledni_nalezena_hra
                    self.posledni_nalezena_hra = nazev
                    return nazev
        except: pass
        return ""

    def spustit_kontrolu_smycka(self):
        threading.Thread(target=self._vlakno_kontroly_loop, daemon=True).start()

    def _vlakno_kontroly_loop(self):
        self.cyklus_skenu = 0
        while True:
            try:
                self._odeslat_heartbeat() 
                self._proved_kontrolu()
            except Exception as e:
                self.zapsat_do_logu(f"[LOOP CHYBA]: {e}")
            finally:
                import random
                # ZÁCHRANA BMAXU A EKO-MÓDŮ:
                if getattr(self, 'okno_minimalizovano', False):
                    # Pokud je okno dole na liště, zpomalíme radar na 15 vteřin.
                    # Přestane se zahlcovat grafická paměť a procesor si odpočine!
                    time.sleep(15.0) 
                else:
                    # Okno je nahoře: Normální svižný běh radaru (3 až 5 vteřin)
                    time.sleep(random.uniform(3.0, 5.0)) 

    def _proved_kontrolu(self):
        # OPRAVA: Líná kontrola kabelu. PowerShell žere strašně moc CPU.
        # Ptáme se ho jen jednou za 15 vteřin, abychom zbytečně netočili větráky notebooků!
        nyni = time.time()
        if not hasattr(self, 'posledni_kontrola_site') or (nyni - self.posledni_kontrola_site > 15):
            self.posledni_kontrola_site = nyni
            try:
                nove_adaptery = self.ziskat_aktivni_adaptery()
                self.root.after(0, self._aktualizuj_roletu_pokud_zmena, nove_adaptery)
            except Exception as e: self.zapsat_do_logu(f"[KONTROLA SÍTĚ CHYBA]: {e}")
            
        hraci_k_pingnuti = []
        with self.lock_hraci:
            for ip in self.seznam_hracu.keys():
                hra = self.seznam_hracu[ip].get("hra_z_procesu", "")
                hraci_k_pingnuti.append((ip, hra))
                
        if hraci_k_pingnuti:
            # BEZPEČNÉ ODESLÁNÍ DO POZADÍ:
            for ip, hra in hraci_k_pingnuti:
                self.radar_executor.submit(self._ping_a_porty_hrace, ip, hra)

    def _ping_a_porty_hrace(self, ip, hra_proces):
        jmeno = ""
        with self.lock_hraci:
            if ip in self.seznam_hracu:
                jmeno = self.seznam_hracu[ip]["jmeno"]
                self.seznam_hracu[ip]["odeslano"] += 1

        if jmeno == "Neznámý Hráč" or jmeno == "Neznámý":
            try:
                skutecne_jmeno = socket.gethostbyaddr(ip)[0]
                jmeno = skutecne_jmeno 
                with self.lock_hraci:
                    if ip in self.seznam_hracu:
                        self.seznam_hracu[ip]["jmeno"] = jmeno
            except: pass

        # OPRAVA RADARU: Hráč musí komunikovat přes appku. Ping samotný už nestačí!
        zije_pres_aplikaci = False
        with self.lock_hraci:
            if ip in self.seznam_hracu:
                # ZVÝŠENÁ TOLERANCE: Dáme mu 30 vteřin. Když se stahují gigabajty, 
                # síť je ucpaná a kontrolní UDP pakety se občas zpozdí.
                if time.time() - self.seznam_hracu[ip].get("posledni_aktivita", 0) < 30:
                    zije_pres_aplikaci = True

        text_hry = ""
        ping_ms = "" 

        if zije_pres_aplikaci: 
            vystup_ok = False
            ping_ms = ""
            
            # LÍNÝ PING: Skutečný 'ping.exe' uděláme jen tehdy, když je hráč víc jak 8 vteřin potichu.
            # Tím ušetříme klidně i 90 % zátěže procesoru a routeru!
            cas_ticha = time.time() - self.seznam_hracu[ip].get("posledni_aktivita", 0)
            
            if cas_ticha > 8:
                vystup = subprocess.run(["ping", "-n", "1", "-w", "500", ip], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                vystup_ok = (vystup.returncode == 0)
                if vystup_ok:
                    match = re.search(r'(?:čas|time|zeit|czas)[=<](\d+)', vystup.stdout, re.IGNORECASE)
                    if match: ping_ms = f"  [{match.group(1)} ms]"
            else:
                # Hráč před chviličkou poslal UDP balíček, stoprocentně víme, že žije a ping je výborný!
                vystup_ok = True
                ping_ms = "  [LAN Bleskově OK]"
                
            with self.lock_hraci:
                if ip in self.seznam_hracu and vystup_ok:
                    self.seznam_hracu[ip]["prijato"] += 1
                    
            barva = getattr(self, 'aktualni_barva_motivu', "#2ecc71")
            
            # KOMPROMIS: Líné skenování portů S THREAD-SAFE ZÁMKEM!
            nyni = time.time()
            proved_sken = False
            
            with self.lock_hraci:
                if ip in self.seznam_hracu:
                    if "posledni_sken_portu" not in self.seznam_hracu[ip]:
                        self.seznam_hracu[ip]["posledni_sken_portu"] = 0
                        self.seznam_hracu[ip]["nalezene_porty"] = []
                        
                    if nyni - self.seznam_hracu[ip]["posledni_sken_portu"] > 20:
                        proved_sken = True

            if proved_sken:
                nove_porty = self.zkontrolovat_hry(ip)
                with self.lock_hraci:
                    if ip in self.seznam_hracu:
                        self.seznam_hracu[ip]["nalezene_porty"] = nove_porty
                        self.seznam_hracu[ip]["posledni_sken_portu"] = nyni
                        
            with self.lock_hraci:
                if ip in self.seznam_hracu:
                    hry = list(self.seznam_hracu[ip]["nalezene_porty"])
                else:
                    hry = []
            
            if hra_proces and hra_proces not in hry:
                hry.append(hra_proces)   
            if hry: text_hry = "🎮 " + ", ".join(hry)
            
        else: 
            # Aplikace neodpovídá...
            barva = "#e74c3c" 
            ping_ms = "  [Aplikace vypnuta]"
            with self.lock_hraci:
                if ip in self.seznam_hracu:
                    doba_smrti = time.time() - self.seznam_hracu[ip]["posledni_aktivita"]
                    # Když o něm neuslyšíme CELOU MINUTU (60s), teprve pak ho vymažeme z radaru
                    if doba_smrti > 60: 
                        self.root.after(0, lambda ip_ke_smazani=ip: self.odstranit_hrace(ip_ke_smazani))
                        return  
        
        self.root.after(0, self.aktualizuj_tecku_a_hru, ip, barva, text_hry, ping_ms)

    def aktualizuj_tecku_a_hru(self, ip, barva, text_hry, ping_ms=""):
        with self.lock_hraci:
            if ip in self.seznam_hracu:
                try:
                    hrac = self.seznam_hracu[ip]
                    # KRIZOVÁ OPRAVA: Kontrola, že grafické prvky opravdu ještě existují
                    if not hrac["canvas"].winfo_exists() or not hrac["label"].winfo_exists():
                        return

                    hrac["canvas"].itemconfig(hrac["dot"], fill=barva)
                    jmeno = hrac["jmeno"]
                    odeslano = hrac.get("odeslano", 0)
                    prijato = hrac.get("prijato", 0)
                    
                    kvalita = 100 
                    if odeslano > 0:
                        kvalita = int((prijato / odeslano) * 100)
                    if kvalita >= 85: ikona = "📶"
                    elif kvalita >= 40: ikona = "⚠️"
                    else: ikona = "❌"
                    
                    moje_sit = ".".join(self.moje_ip.split(".")[:3])
                    jeho_sit = ".".join(ip.split(".")[:3])
                    typ_site_ikona = "🔌" if moje_sit == jeho_sit else "📶"
                    text_vizitky = f"{jmeno} ({ip}) {typ_site_ikona} {ping_ms}   |   {ikona} {kvalita}%   |   [↑ {odeslano} | ↓ {prijato}]"
                    
                    # UKAZATEL STAHOVÁNÍ: Pokud je IP v seznamu žroutů, ukážeme disketu
                    if ip in getattr(self, 'aktivni_stahovaci', set()):
                        text_vizitky += "   |   💾 [STAHAHUJE OD TEBE]"
                    if text_hry: 
                        text_vizitky += f"   |   {text_hry}"
                        
                    hrac["label"].configure(text=text_vizitky)
                    
                    if "label_hra" in hrac and hrac["label_hra"]:
                        if hrac["label_hra"].winfo_exists():
                            hrac["label_hra"].configure(text="")
                except Exception as e:
                    pass # Tichý chod, pokud se grafika během zápisu ztratí

    def otevrit_sitova_pripojeni(self):
        try: os.startfile("ncpa.cpl")
        except: pass

    def aktualizuj_vizitku(self, event=None):
        aktualni_nick = self.entry_nick.get().strip() or "Neznámý Hráč"
        self.lbl_velky_nick.configure(text=aktualni_nick)
        try:
            with open(SOUBOR_NICK, "w", encoding="utf-8") as f: f.write(aktualni_nick)
        except: pass

    def ziskat_lokalni_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except: IP = '127.0.0.1'
        finally: s.close()
        return IP

    def zkopirovat_moji_ip(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.moje_ip)
        messagebox.showinfo("Kopírování", f"Tvoje IP adresa {self.moje_ip} byla zkopírována do schránky!")

    def ziskat_vsechny_moje_ip(self):
        moje_adresy = ["127.0.0.1"]
        try:
            for interface in socket.getaddrinfo(socket.gethostname(), None):
                ip = interface[4][0]
                if ip not in moje_adresy and not ":" in ip: 
                    moje_adresy.append(ip)
        except: pass
        return moje_adresy

    def pridat_hrace_rucne(self):
        ip = self.novy_ip.get().strip()
        if not ip: return
        try: ipaddress.ip_address(ip)
        except ValueError: return messagebox.showerror("Chyba", "Neplatná IP adresa!")
        
        with self.lock_hraci:
            if ip in self.seznam_hracu: return
            
        self.automaticky_pridat_do_gui(ip, "Neznámý Hráč")
        self.novy_ip.set('')
        self.poslat_udp_zpravu("__DISCOVER__", ip)

    def zapsat_do_logu(self, text):
        cas = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            with open(SOUBOR_HISTORIE, "a", encoding="utf-8") as soubor: soubor.write(f"[{cas}] {text}\n")
        except: pass

    def ziskat_aktivni_adaptery(self):
        try:
            # Vrátíme filtr 'Up' - díky tomu program přesně pozná ten moment, KDY se kabel fyzicky zapojí
            prikaz = "Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -ExpandProperty Name"
            vystup = subprocess.check_output(["powershell", "-command", prikaz], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            adaptery = [linka.strip() for linka in vystup.split('\n') if linka.strip()]
            return adaptery if adaptery else ["Ethernet", "Wi-Fi"]
        except: return ["Ethernet", "Wi-Fi"]

    def _aktualizuj_roletu_pokud_zmena(self, nove_adaptery):
        stare_adaptery = list(self.combo_adapter['values'])
        aktualni_vyber = self.combo_adapter.get()
        
        if stare_adaptery != nove_adaptery:
            self.combo_adapter['values'] = nove_adaptery
            
            # Najdeme, jestli je k dispozici kabel nebo wifi
            kabel_adapter = next((a for a in nove_adaptery if "ethernet" in a.lower() or "síť" in a.lower()), None)
            wifi_adapter = next((a for a in nove_adaptery if "wi-fi" in a.lower() or "wifi" in a.lower() or "wlan" in a.lower()), None)
            
            byl_tu_kabel_predtim = any("ethernet" in a.lower() or "síť" in a.lower() for a in stare_adaptery)
            
            # --- INTELIGENCE 1: UŽIVATEL PRÁVĚ ZAPOJIL KABEL ---
            if kabel_adapter and not byl_tu_kabel_predtim:
                self.zapsat_do_logu(f"[SÍŤ] Fyzicky připojen kabel: {kabel_adapter}! Přepínám...")
                try:
                    self.chat_box.insert("end", f"[SYSTÉM] 🔌 Detekován LAN kabel! Automaticky na něj přepínám...")
                    self.chat_box.itemconfig("end", fg="#2ecc71")
                    self.chat_box.yview("end")
                except: pass
                
                # Vybere v roletce kabel, odemkne automatiku a odpálí ji za tebe
                self.combo_adapter.set(kabel_adapter)
                self.tlacitko_uzamceno = False
                self.root.after(500, self.automaticky_nastavit_ip_kabel)
                return

            # --- INTELIGENCE 2: UŽIVATEL VYTRHL AKTUÁLNÍ SÍŤ (Výpadek) ---
            if aktualni_vyber and aktualni_vyber not in nove_adaptery:
                self.zapsat_do_logu(f"[SÍŤ] Adaptér {aktualni_vyber} ztratil signál/byl odpojen!")
                novy_vyber = kabel_adapter or wifi_adapter or (nove_adaptery[0] if nove_adaptery else "")
                
                if novy_vyber:
                    self.combo_adapter.set(novy_vyber)
                    self.zapsat_do_logu(f"[SÍŤ] Záchrana: Přepnuto na adaptér: {novy_vyber}")
                    try:
                        self.chat_box.insert("end", f"[SYSTÉM] Výpadek! Přepojuji se na záložní síť: {novy_vyber}")
                        self.chat_box.itemconfig("end", fg="#f39c12")
                        self.chat_box.yview("end")
                    except: pass
                    
                    # Odpálí automatiku pro záložní síť (např. nahodí modré tlačítko Wi-Fi)
                    self.tlacitko_uzamceno = False
                    self.root.after(500, self.automaticky_nastavit_ip_kabel)
                    
            elif aktualni_vyber in nove_adaptery:
                self.combo_adapter.set(aktualni_vyber)
            elif nove_adaptery:
                self.combo_adapter.set(kabel_adapter if kabel_adapter else nove_adaptery[0])
                self.aktualizovat_zobrazenou_ip()

    def ziskat_ip_podle_adapteru(self, nazev_adapteru):
        try:
            prikaz = f"(Get-NetIPAddress -InterfaceAlias '{nazev_adapteru}' -AddressFamily IPv4).IPAddress"
            vystup = subprocess.check_output(["powershell", "-command", prikaz], text=True, creationflags=subprocess.CREATE_NO_WINDOW).strip()
            if vystup: return vystup.split('\n')[0].strip()
        except: pass
        return self.ziskat_lokalni_ip()

    def aktualizovat_zobrazenou_ip(self, event=None):
        adapter = self.combo_adapter.get().strip()
        if adapter:
            nova_ip = self.ziskat_ip_podle_adapteru(adapter)
            if self.moje_ip != nova_ip:
                self.moje_ip = nova_ip
                info_text = f"🖥️ PC: {self.muj_hostname}  |  🌐 IP: {self.moje_ip}  |  {TEXTY['lbl_connected'][self.jazyk]}"
                self.lbl_moje_info.configure(text=info_text)
                
                self.tlacitko_uzamceno = False
                puvodni_barva = getattr(self, 'aktualni_barva_motivu', "#2ecc71")
                try:
                    self.btn_auto_ip.configure(
                        fg_color=puvodni_barva, 
                        text=TEXTY["btn_auto_connect"][self.jazyk], 
                        font=("Arial", 16, "bold")
                    )
                except: pass

                try: self.tcp_server.close()
                except: pass
                try: self.udp_sock.close()
                except: pass
                
                self.root.after(500, self.start_naslouchani) 
                try:
                    self.chat_box.insert("end", f"{TEXTY['msg_ip_updated'][self.jazyk]} '{adapter}': {nova_ip}")
                    self.chat_box.see("end")
                except: pass
                
        # --- OPRAVA: Ignorování 169.254 pro roletky ---
        sitovy_zaklad = "192.168.0" # Výchozí jistota, když Windows zlobí
        
        if self.moje_ip and self.moje_ip != "127.0.0.1" and not self.moje_ip.startswith("169.254."):
            casti = self.moje_ip.split('.')
            if len(casti) == 4:
                sitovy_zaklad = f"{casti[0]}.{casti[1]}.{casti[2]}"
                
        nove_hodnoty = [f"{sitovy_zaklad}.{i}" for i in range(1, 255)]
        
        self.root.after(0, lambda: self.entry_ip.configure(values=nove_hodnoty))
        self.root.after(0, lambda: self.novy_ip.configure(values=nove_hodnoty))

    def zmenit_ip(self):
        adapter = self.combo_adapter.get().strip()
        nova_ip = self.entry_ip.get().strip()
        maska = self.entry_mask.get().strip()
        try:
            ipaddress.ip_address(nova_ip)
            ipaddress.ip_address(maska)
        except ValueError: return messagebox.showerror("Chyba", "Neplatná IP adresa!")
        
        if nova_ip != self.moje_ip:
            self.root.config(cursor="wait")
            self.root.update()
            vystup = subprocess.run(["ping", "-n", "1", "-w", "300", nova_ip], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.root.config(cursor="")
            if vystup.returncode == 0:
                titulek = TEXTY.get("msg_ip_conflict_title", {"CZ": "❌ Kolize IP adresy", "EN": "❌ IP Conflict"})[self.jazyk]
                text_sablon = TEXTY.get("msg_ip_conflict_text", {
                    "CZ": "Tuto IP adresu ({}) už v síti používá jiné zařízení (PC, mobil nebo router)!\n\nZvol prosím jiné číslo na konci (např. 11-50), ať nedojde ke zhroucení sítě.", 
                    "EN": "This IP address ({}) is already used by another device (PC, phone or router)!\n\nPlease choose a different number at the end (e.g. 11-50) to prevent network crashes."
                })[self.jazyk]
                messagebox.showerror(titulek, text_sablon.format(nova_ip))
                return 

        prikaz_ip = f'netsh interface ipv4 set address name="{adapter}" static {nova_ip} {maska}'
        if self.vykonat_jako_spravce([prikaz_ip]):
            self.moje_ip = nova_ip
            self.lbl_moje_info.configure(text=f"🖥️ PC: {self.muj_hostname}   |   🌐 IP: {self.moje_ip}   |   🟢 Připojen")
            try: self.tcp_server.close()
            except: pass
            try: self.udp_sock.close()
            except: pass
            self.root.after(500, self.start_naslouchani)
            text_uspech = f"[SYSTÉM] IP úspěšně změněna na: {nova_ip}" if self.jazyk == "CZ" else f"[SYSTEM] IP successfully changed to: {nova_ip}"
            self.chat_box.insert("end", text_uspech)
            self.chat_box.itemconfig("end", fg="#2ecc71")
        else:
            self.root.config(cursor="")
            messagebox.showerror("Chyba oprávnění", "Pro úpravu sítě jsou nutná práva správce!")

    def prepnout_zobrazeni_pokrocilych_ip(self):
        if self.pokrocile_ip_zobrazeno:
            self.frame_ip.pack_forget() 
            self.frame_pokrocile_hledani.pack_forget() 
            self.pokrocile_ip_zobrazeno = False
        else:
            self.frame_ip.pack(fill="x", padx=10, pady=5, after=self.frame_jednoduche_ip)
            self.frame_pokrocile_hledani.pack(fill="x", padx=10, after=self.frame_ip)
            self.pokrocile_ip_zobrazeno = True

    def automaticky_nastavit_ip_kabel(self):
        if hasattr(self, 'tlacitko_uzamceno') and self.tlacitko_uzamceno: return
        self.tlacitko_uzamceno = True
        self.root.config(cursor="wait")
        # Informujeme uživatele, že se něco děje, aby neměl pocit, že to zamrzlo
        self.btn_auto_ip.configure(text="Zjišťuji síťové připojení... ⏳" if self.jazyk == "CZ" else "Detecting network... ⏳")

        def proces_nastaveni():
            import random
            try:
                # Zjistíme, které adaptéry jsou FYZICKY AKTIVNÍ (běží už na pozadí, nezatěžuje grafiku)
                try:
                    prikaz = "Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -ExpandProperty Name"
                    vystup = subprocess.check_output(["powershell", "-command", prikaz], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    zapojene_adaptery = [linka.strip() for linka in vystup.split('\n') if linka.strip()]
                except:
                    zapojene_adaptery = self.ziskat_aktivni_adaptery()

                kabel_adapter = next((a for a in zapojene_adaptery if "ethernet" in a.lower() or "síť" in a.lower()), None)
                
                if kabel_adapter:
                    self.root.after(0, lambda: self.combo_adapter.set(kabel_adapter))
                    aktualni_ip = self.ziskat_ip_podle_adapteru(kabel_adapter)
                    
                    # --- SCÉNÁŘ 1: Jsme zapojení do ROUTERU (Máme zdravou IP a internet) ---
                    if aktualni_ip and not aktualni_ip.startswith("169.254.") and aktualni_ip != "127.0.0.1":
                        # IP adresu neměníme na statickou! Zachováme tak připojení k internetu.
                        prikazy = self._dostat_prikazy_firewall_povolit() # Jen propíchneme firewall
                        
                        if self.vykonat_jako_spravce(prikazy):
                            self.moje_ip = aktualni_ip
                            info_txt = f"🖥️ PC: {self.muj_hostname}   |   🌐 IP: {self.moje_ip}   |   {TEXTY['lbl_connected'][self.jazyk]}"
                            self.root.after(0, lambda txt=info_txt: self.lbl_moje_info.configure(text=txt))
                            
                            try: self.tcp_server.close()
                            except: pass
                            try: self.udp_sock.close()
                            except: pass
                            
                            self.root.after(500, self.start_naslouchani)
                            txt_uspech = f"🔌 LAN (ROUTER) PŘIPRAVEN!\nTVOJE IP: {aktualni_ip}" if self.jazyk == "CZ" else f"🔌 LAN (ROUTER) READY!\nYOUR IP: {aktualni_ip}"
                            self.root.after(0, lambda: self.btn_auto_ip.configure(fg_color="#27ae60", text=txt_uspech, font=("Arial", 12, "bold")))
                            return
                        else:
                            self.root.after(0, lambda: messagebox.showerror("Chyba", "Práva správce byla zamítnuta!"))
                            self.tlacitko_uzamceno = False
                            self.root.after(0, self.aktualizovat_texty_gui)
                            return
                            
                    # --- SCÉNÁŘ 2: Jsme propojení NAPŘÍMO (Máme 169.254.x.x, chybí router) ---
                    else:
                        sitovy_zaklad = "192.168.0" 
                        for _ in range(5): 
                            nahodne_cislo = random.randint(11, 250)
                            nova_ip = f"{sitovy_zaklad}.{nahodne_cislo}"
                            if nova_ip == self.moje_ip: continue
                            
                            vystup = subprocess.run(["ping", "-n", "1", "-w", "150", nova_ip], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                            if vystup.returncode != 0: 
                                self.root.after(0, lambda nip=nova_ip: self.entry_ip.set(nip))
                                
                                # Tady natvrdo nastavujeme IP, protože router tu není a internet stejně nemáme
                                prikazy = [f'netsh interface ipv4 set address name="{kabel_adapter}" static {nova_ip} 255.255.255.0']
                                prikazy.extend(self._dostat_prikazy_firewall_povolit())
                                
                                if self.vykonat_jako_spravce(prikazy):
                                    self.moje_ip = nova_ip
                                    info_txt = f"🖥️ PC: {self.muj_hostname}   |   🌐 IP: {self.moje_ip}   |   {TEXTY['lbl_connected'][self.jazyk]}"
                                    self.root.after(0, lambda txt=info_txt: self.lbl_moje_info.configure(text=txt))
                                    
                                    try: self.tcp_server.close()
                                    except: pass
                                    try: self.udp_sock.close()
                                    except: pass
                                    
                                    self.root.after(500, self.start_naslouchani)
                                    txt_uspech = f"🔌 LAN (PŘÍMÁ) PŘIPRAVENA!\nTVOJE IP: {nova_ip}" if self.jazyk == "CZ" else f"🔌 LAN (DIRECT) READY!\nYOUR IP: {nova_ip}"
                                    self.root.after(0, lambda: self.btn_auto_ip.configure(fg_color="#27ae60", text=txt_uspech, font=("Arial", 12, "bold")))
                                    return
                                else:
                                    self.root.after(0, lambda: messagebox.showerror("Chyba", "Práva správce byla zamítnuta!"))
                                    self.tlacitko_uzamceno = False
                                    self.root.after(0, self.aktualizovat_texty_gui)
                                    return

                # Pokud kabel není fyzicky zapojený, zkusíme najít připojenou Wi-Fi
                wifi_adapter = next((a for a in zapojene_adaptery if "wi-fi" in a.lower() or "wifi" in a.lower() or "wlan" in a.lower()), None)
                
                if wifi_adapter:
                    self.root.after(0, lambda: self.combo_adapter.set(wifi_adapter))
                    self.root.after(0, self.aktualizovat_zobrazenou_ip) 
                    
                    if self.vykonat_jako_spravce(self._dostat_prikazy_firewall_povolit()):
                        def nastav_tlacitko_wifi():
                            txt_uspech = f"📶 WI-FI PŘIPRAVENA!\nTVOJE IP: {self.moje_ip}" if self.jazyk == "CZ" else f"📶 WI-FI READY!\nYOUR IP: {self.moje_ip}"
                            self.btn_auto_ip.configure(fg_color="#2980b9", text=txt_uspech, font=("Arial", 12, "bold"))
                            self.tlacitko_uzamceno = True
                        self.root.after(1000, nastav_tlacitko_wifi)
                        return
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Chyba", "Práva správce byla zamítnuta!"))
                        self.tlacitko_uzamceno = False
                        self.root.after(0, self.aktualizovat_texty_gui)
                        return

                # OPRAVA: Zde je ta chybová hláška vložená bezpečně do hlavního vlákna
                self.root.after(0, lambda: messagebox.showerror("Chyba", TEXTY["msg_no_adapter"][self.jazyk]))
                self.tlacitko_uzamceno = False
                self.root.after(0, self.aktualizovat_texty_gui)
                
            finally:
                # OPRAVA: Zde se kurzor vrací bezpečně z pozadí zpět do normálu
                self.root.after(0, lambda: self.root.config(cursor=""))

        # Spustí celý proces na pozadí, takže grafika už nikdy neztuhne
        threading.Thread(target=proces_nastaveni, daemon=True).start()   

    def spustit_kontrolu_ihned(self):
        threading.Thread(target=self._odeslat_discover_broadcast, daemon=True).start()

    def aktualizuj_statistiky(self):
        pass

    def nacti_hry(self):
        self.moje_hry.clear()
        if os.path.exists(SOUBOR_HRY):
            try:
                with open(SOUBOR_HRY, "r", encoding="utf-8") as f:
                    for radek in f:
                        casti = radek.strip().split("|")
                        if len(casti) >= 2:
                            nazev = casti[0]
                            cesta = casti[1]
                            port = casti[2] if len(casti) > 2 else "Neznámý"
                            parametry = casti[3] if len(casti) > 3 else ""
                            self.moje_hry[nazev] = {"cesta": cesta, "port": port, "parametry": parametry}
            except: pass
        self.vykresli_seznam_her()

    def uloz_hry(self):
        try:
            with open(SOUBOR_HRY, "w", encoding="utf-8") as f:
                for nazev, data in self.moje_hry.items():
                    param = data.get("parametry", "")
                    f.write(f"{nazev}|{data['cesta']}|{data['port']}|{param}\n")
        except: pass

    def vykresli_seznam_her(self):
        self.list_her.delete(0, tk.END)
        for nazev in self.moje_hry.keys():
            self.list_her.insert("end", f"🎮 {nazev}")

    def pridat_hru(self):
        cesta = filedialog.askopenfilename(title="Vyber spouštěcí soubor hry (.exe)", filetypes=[("Spustitelné soubory", "*.exe")])
        if not cesta: return
        self.otevrit_okno_pridani_hry(cesta)

    def otevrit_okno_pridani_hry(self, cesta_k_exe):
        vychozi_nazev = os.path.basename(cesta_k_exe).replace(".exe", "")
        
        okno = ctk.CTkToplevel(self.root)
        okno.title(TEXTY["win_add_game"][self.jazyk])
        okno.geometry("480x420")
        okno.resizable(False, False)
        okno.transient(self.root) 
        okno.grab_set() 

        ctk.CTkLabel(okno, text=TEXTY["lbl_game_name"][self.jazyk], font=("Arial", 14, "bold"), text_color="white").pack(pady=(20, 5))
        entry_nazev = ctk.CTkEntry(okno, font=("Arial", 14), width=380, justify="center", height=40, corner_radius=8)
        entry_nazev.insert(0, vychozi_nazev)
        entry_nazev.pack()
        
        ctk.CTkLabel(okno, text=TEXTY["lbl_game_port"][self.jazyk], text_color="#f39c12", font=("Arial", 14, "bold")).pack(pady=(15, 5))
        hodnoty_portu = [TEXTY["lbl_auto_port"][self.jazyk]] + [f"{port} ({nazev})" for port, nazev in ZNAME_HRY.items()]
        combo_port = ctk.CTkComboBox(okno, values=hodnoty_portu, font=("Arial", 14), width=380, height=40, corner_radius=8, button_color="#f39c12", button_hover_color="#d68910")
        combo_port.pack()

        lbl_params_txt = "Spouštěcí parametry (Vyber nebo napiš vlastní):" if self.jazyk == "CZ" else "Launch params (Choose or type your own):"
        ctk.CTkLabel(okno, text=lbl_params_txt, text_color="#bdc3c7", font=("Arial", 13, "bold")).pack(pady=(15, 5))
        
        bezne_parametry = ["", "-game cstrike", "-windowed", "-opengl", "-noborder -windowed", "-console", "-novid", "-dxlevel 81"]
        entry_params = ctk.CTkComboBox(okno, values=bezne_parametry, font=("Arial", 14), width=380, height=40, corner_radius=8)
        entry_params.set("")
        entry_params.pack()

        def potvrdit():
            nazev = entry_nazev.get().strip()
            vybrany_port = combo_port.get().strip()
            zadane_parametry = entry_params.get().strip()
            if not nazev: return
            port_cislo = vybrany_port.split(" ")[0] if vybrany_port else "Neznámý"
            for spravny_port in ZNAME_HRY.keys():
                prvni_cislo = str(spravny_port).split("-")[0]
                if port_cislo == prvni_cislo:
                    port_cislo = str(spravny_port)
                    break
            self.moje_hry[nazev] = {"cesta": cesta_k_exe, "port": port_cislo, "parametry": zadane_parametry}
            self.uloz_hry()
            self.vykresli_seznam_her()
            okno.destroy()

        ramecek_tlacitek = ctk.CTkFrame(okno, fg_color="transparent")
        ramecek_tlacitek.pack(pady=30)
        ctk.CTkButton(ramecek_tlacitek, text=TEXTY["btn_save"][self.jazyk], command=potvrdit, fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=("Arial", 14, "bold"), width=150, height=45, corner_radius=8).pack(side="left", padx=15)
        ctk.CTkButton(ramecek_tlacitek, text=TEXTY["btn_cancel"][self.jazyk], command=okno.destroy, fg_color="#e74c3c", hover_color="#c0392b", text_color="white", font=("Arial", 14, "bold"), width=150, height=45, corner_radius=8).pack(side="right", padx=15)            

    def najdi_port_procesu(self, nazev_exe):
        try:
            vystup_task = subprocess.check_output(f'tasklist /fi "imagename eq {nazev_exe}" /nh', shell=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            match = re.search(rf'{nazev_exe}\s+(\d+)', vystup_task, re.IGNORECASE)
            if not match: return None
            pid = match.group(1)
            vystup_net = subprocess.check_output(f'netstat -ano | findstr {pid}', shell=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            for radek in vystup_net.splitlines():
                if "LISTENING" in radek or "NASLOUCHÁNÍ" in radek:
                    port_match = re.search(r'TCP\s+\S+:(\d+)', radek)
                    if port_match: return port_match.group(1)
        except: pass
        return None

    def aktualizuj_nazev_hry_v_seznamu(self, puvodni_nazev, novy_port):
        for i in range(self.list_her.size()):
            if puvodni_nazev in self.list_her.get(i):
                self.list_her.delete(i)
                self.list_her.insert(i, f"🎮 {puvodni_nazev}   [Běží na portu: {novy_port}]")
                self.list_her.itemconfig(i, fg="#2ecc71")
                break

    def odebrat_hru(self):
        vyber = self.list_her.curselection()
        if not vyber: return
        hodnota = self.list_her.get(vyber[0])
        nazev = hodnota.replace("🎮 ", "") 
        if nazev in self.moje_hry:
            del self.moje_hry[nazev]
            self.uloz_hry()
            self.vykresli_seznam_her()

    def spustit_hru(self):
        vyber = self.list_her.curselection()
        if not vyber: 
            messagebox.showwarning("Upozornění", "Nejprve kliknutím vyber hru ze seznamu!")
            return
        hodnota = self.list_her.get(vyber[0])
        nazev = hodnota.replace("🎮 ", "")
        data = self.moje_hry.get(nazev)
        if data and os.path.exists(data["cesta"]):
            try:
                prikazy = [
                    'netsh advfirewall firewall delete rule name="LAN Party Hra"',
                    'netsh advfirewall firewall delete rule name="LAN Party Hra EXE"'
                ]
                cesta_k_exe = data["cesta"]
                prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra EXE" dir=in action=allow program="{cesta_k_exe}" enable=yes profile=any')
                prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra EXE" dir=out action=allow program="{cesta_k_exe}" enable=yes profile=any')

                port = data.get("port", "")
                if port and port.replace("-", "").isdigit():
                    prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra" dir=in action=allow protocol=TCP localport={port}')
                    prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra" dir=in action=allow protocol=UDP localport={port}')
                    prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra" dir=out action=allow protocol=TCP remoteport={port}')
                    prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra" dir=out action=allow protocol=UDP remoteport={port}')
                
                if not self.vykonat_jako_spravce(prikazy):
                    titulek = "Upozornění" if self.jazyk == "CZ" else "Warning"
                    messagebox.showwarning(titulek, TEXTY["msg_admin_denied_game"][self.jazyk])
                
                pracovni_slozka = os.path.dirname(data["cesta"])
                
                parametry_hry = data.get("parametry", "")
                if parametry_hry:
                    import shlex
                    prikaz_spusteni = [data["cesta"]] + shlex.split(parametry_hry)
                    subprocess.Popen(prikaz_spusteni, cwd=pracovni_slozka)
                else:
                    puvodni_slozka = os.getcwd() 
                    try:
                        os.chdir(pracovni_slozka) 
                        os.startfile(data["cesta"]) 
                    finally:
                        os.chdir(puvodni_slozka) 
                
                muj_nick = self.entry_nick.get().strip() or "Neznámý"
                exe_name = os.path.basename(data["cesta"])

                if port.startswith("AUTO"):
                    self.chat_box.insert("end", f"[SYSTÉM] Sleduji hru {nazev}... Čekám na otevření sítě (může to trvat i 20 vteřin).")
                    self.chat_box.itemconfig("end", fg="#f39c12")
                    self.notebook.set(TEXTY["tab_chat"][self.jazyk]) 

                    def stopar_portu():
                        nalezeny_port = None
                        for _ in range(15):
                            time.sleep(2)
                            nalezeny_port = self.najdi_port_procesu(exe_name)
                            if nalezeny_port: break

                        if nalezeny_port:
                            self.root.after(0, lambda: self.aktualizuj_nazev_hry_v_seznamu(nazev, nalezeny_port))
                            zprava = f"📢 🚀 PRÁVĚ ZAKLÁDÁM HRU: {nazev} (Port: {nalezeny_port})! Moje IP: {self.moje_ip}"
                            self.root.after(0, lambda: self.chat_box.insert("end", f"[RADAR] Úspěch! {nazev} běží na portu {nalezeny_port}."))
                            self.root.after(0, lambda: self.chat_box.itemconfig("end", fg="#2ecc71"))
                        else:
                            zprava = f"📢 🚀 PRÁVĚ ZAKLÁDÁM HRU: {nazev}! Moje IP: {self.moje_ip}"

                        msg_id = str(int(datetime.datetime.now().timestamp() * 1000))
                        for cilova_adresa in self.ziskat_spravne_broadcasty():
                            self.poslat_udp_zpravu(f"__MSG__:{msg_id}:{muj_nick}:{zprava}", cilova_adresa, broadcast=True)

                    threading.Thread(target=stopar_portu, daemon=True).start()

                else:
                    # Přidán tlampač 📢, aby to nevyhazovalo soukromé okno ostatním!
                    zprava = f"📢 🚀 PRÁVĚ ZAKLÁDÁM HRU: {nazev} (Port: {port})! Moje IP je: {self.moje_ip}"
                    msg_id = str(int(datetime.datetime.now().timestamp() * 1000))
                    for cilova_adresa in self.ziskat_spravne_broadcasty():
                        self.poslat_udp_zpravu(f"__MSG__:{msg_id}:{muj_nick}:{zprava}", cilova_adresa, broadcast=True)

                    self.chat_box.insert("end", f"[LAUCHER] Hra spuštěna. Firewall otevřen. Pozvánka odeslána!")
                    self.notebook.set(TEXTY["tab_chat"][self.jazyk]) 

            except Exception as e:
                titulek = "Chyba" if self.jazyk == "CZ" else "Error"
                chyba_txt = "Nepodařilo se spustit hru" if self.jazyk == "CZ" else "Failed to start game"
                messagebox.showerror(titulek, f"{chyba_txt}:\n{e}")
        else:
            titulek = "Chyba" if self.jazyk == "CZ" else "Error"
            messagebox.showerror(titulek, TEXTY["msg_game_not_found"][self.jazyk])
            self.odebrat_hru()

    def inicializuj_drag_and_drop(self):
        try:
            self.list_her.drop_target_register(DND_FILES)
            self.list_her.dnd_bind('<<Drop>>', self.zpracuj_hozenou_hru)
            
            self.list_souboru.drop_target_register(DND_FILES)
            self.list_souboru.dnd_bind('<<Drop>>', self.zpracuj_hozeny_soubor_do_sdileni)
        except Exception as e: self.zapsat_do_logu(f"[DND CHYBA] {e}")

    def zpracuj_hozenou_hru(self, event):
        cesta = event.data.strip('{}') 
        if not cesta.lower().endswith('.exe'):
            messagebox.showwarning("Pozor", TEXTY["msg_only_exe"][self.jazyk])
            return
        self.otevrit_okno_pridani_hry(cesta)

    def zpracuj_hozeny_soubor_do_sdileni(self, event):
        cesta = event.data.strip('{}')
        if not os.path.exists(cesta): return

        cilova_cesta = ""
        nazev_polozky = os.path.basename(cesta)

        if os.path.isdir(cesta):
            id_zip = f"dnd_zip_{time.time()}"
            self.start_ukol(id_zip, f"Kopíruji a balím: {nazev_polozky}... 📦")
            cilova_cesta_bez_pripony = os.path.join(SDILENA_SLOZKA, f"{nazev_polozky}_sdileni")
            
            def zabalit():                
                konecny_zip = cilova_cesta_bez_pripony + ".zip"
                try:
                    celkova_velikost = sum(os.path.getsize(os.path.join(r, f)) for r, d, files in os.walk(cesta) for f in files)
                    zabaleno_bajtu = 0
                    
                    with zipfile.ZipFile(konecny_zip, 'w', zipfile.ZIP_STORED) as zipf:
                        for root_dir, dirs, files in os.walk(cesta):
                            for file in files:
                                file_path = os.path.join(root_dir, file)
                                arcname = os.path.relpath(file_path, start=cesta)
                                zipf.write(file_path, arcname)
                                
                                zabaleno_bajtu += os.path.getsize(file_path)
                                if celkova_velikost > 0:
                                    procenta = int((zabaleno_bajtu / celkova_velikost) * 100)
                                    self.root.after(0, self.update_ukol, id_zip, f"Kopíruji a balím: {nazev_polozky} ({procenta}%)", procenta, "determinate")
                except Exception as e:
                    self.zapsat_do_logu(f"Chyba při drag and drop balení: {e}")
                
                self.root.after(0, self.konec_ukol, id_zip, f"✅ Práce dokončena: {nazev_polozky}")
                self.root.after(0, self.obnovit_sdilenou_slozku)

            threading.Thread(target=zabalit, daemon=True).start()
            
        else:
            cilova_cesta = os.path.join(SDILENA_SLOZKA, nazev_polozky)
            try:
                shutil.copy2(cesta, cilova_cesta)
                self.obnovit_sdilenou_slozku()
            except Exception as e:
                messagebox.showerror("Chyba", TEXTY["msg_copy_fail"][self.jazyk].format(e))

    def prepni_jazyk(self):
        self.jazyk = "EN" if self.jazyk == "CZ" else "CZ"
        try:
            with open(SOUBOR_JAZYK, "w", encoding="utf-8") as f: f.write(self.jazyk)
        except: pass
        self.btn_jazyk.configure(text=self.jazyk)
        try:
            self.chat_box.insert("end", f"\n{TEXTY['msg_lang_switched'][self.jazyk]} {self.jazyk}\n")
            self.chat_box.see("end")
        except: pass
        self.aktualizovat_texty_gui()

    def aktualizovat_texty_gui(self):
        j = self.jazyk
        self.lbl_tvoje_prezdivka.configure(text=TEXTY["lbl_nick"][j])
        self.btn_firewall.configure(text=TEXTY["btn_firewall"][j])
        self.btn_firewall_vratit.configure(text=TEXTY["btn_firewall_vratit"][j])
        self.btn_firewall_rucne.configure(text=TEXTY["btn_firewall_rucne"][j])
        self.btn_about.configure(text=TEXTY["btn_about"][j])
        self.btn_donate.configure(text=TEXTY["btn_donate"][j])
        self.btn_aktualizovat_ip.configure(text=TEXTY["btn_aktualizovat_ip"][j])
        self.btn_auto_ip.configure(text=TEXTY["btn_auto_connect"][j])
        self.btn_pokrocile.configure(text=TEXTY["btn_adv_net"][j])
        
        info_text = f"🖥️ PC: {self.muj_hostname}  |  🌐 IP: {self.moje_ip}  |  {TEXTY['lbl_connected'][j]}"
        self.lbl_moje_info.configure(text=info_text)
        
        self.frame_ip.config(text=TEXTY["frame_ip"][j])
        self.lbl_sitovy_adapter.config(text=TEXTY["lbl_sitovy_adapter"][j])
        self.lbl_nova_ip.config(text=TEXTY["lbl_nova_ip"][j])
        self.lbl_maska.config(text=TEXTY["lbl_maska"][j])
        self.btn_nastavit_ip.configure(text=TEXTY["btn_nastavit_ip"][j])
        self.btn_nastavit_rucne.configure(text=TEXTY["btn_nastavit_rucne"][j])

        self.lbl_radar_title.configure(text=TEXTY["frame_hraci_hlavni"][j])
        self.btn_najit_hrace.configure(text=TEXTY["btn_najit_hrace"][j])
        self.lbl_nebo_rucne.config(text=TEXTY["lbl_nebo_rucne"][j])
        self.btn_pridat.configure(text=TEXTY["btn_pridat"][j])

        try:
            aktualni_tab = self.notebook.get()
            
            staro_chat = TEXTY["tab_chat"]["CZ"] if j == "EN" else TEXTY["tab_chat"]["EN"]
            novy_chat = TEXTY["tab_chat"][j]
            self.notebook.rename(staro_chat, novy_chat)
            if aktualni_tab == staro_chat: self.notebook.set(novy_chat)

            staro_files = TEXTY["tab_files"]["CZ"] if j == "EN" else TEXTY["tab_files"]["EN"]
            novy_files = TEXTY["tab_files"][j]
            self.notebook.rename(staro_files, novy_files)
            if aktualni_tab == staro_files: self.notebook.set(novy_files)

            staro_games = TEXTY["tab_games"]["CZ"] if j == "EN" else TEXTY["tab_games"]["EN"]
            novy_games = TEXTY["tab_games"][j]
            self.notebook.rename(staro_games, novy_games)
            if aktualni_tab == staro_games: self.notebook.set(novy_games)
        except: pass

        try:
            staro_squad = TEXTY["tab_squad"]["CZ"] if j == "EN" else TEXTY["tab_squad"]["EN"]
            novy_squad = TEXTY["tab_squad"][j]
            self.notebook.rename(staro_squad, novy_squad)
            if aktualni_tab == staro_squad: self.notebook.set(novy_squad)
        except: pass

        try:
            # Aktualizace Squad tlačítka a textu, pokud už je načtené
            self.lbl_squad_info.configure(text=TEXTY["lbl_squad_info"][j])
            self.btn_vytvorit_tym.configure(text=TEXTY["btn_create_squad"][j])
            
            # Aktualizace přímo uvnitř vyskočeného týmového okna
            if hasattr(self, 'tymove_okno_aktivni') and self.tymove_okno_aktivni:
                self.tymove_okno.title(f"{TEXTY['win_squad_title'][j]} {', '.join(getattr(self, 'tym_jmena_hracu', []))}")
                if self.mikrofon_zapnuty:
                    self.btn_mikrofon.configure(text=TEXTY["btn_mic_active"][j])
                else:
                    self.btn_mikrofon.configure(text=TEXTY["btn_mic_on"][j])
                self.btn_nastaveni_mic.configure(text=TEXTY["btn_settings"][j])
                self.vstup_tym_chat.configure(placeholder_text=TEXTY["ph_squad_chat"][j])
        except: pass

        self.btn_otevrit_slozku.configure(text=TEXTY["btn_otevrit_slozku"][j])
        self.btn_stahnout_soubor.configure(text=TEXTY["btn_stahnout_soubor"][j])
        self.btn_pridat_hru.configure(text=TEXTY["btn_add_game"][j])
        self.btn_odebrat_hru.configure(text=TEXTY["btn_remove_game"][j])
        self.btn_spustit_hru.configure(text=TEXTY["btn_start_game"][j])
        
        self.btn_rozhlas.configure(text=TEXTY["btn_rozhlas"][j])
        self.entry_rozhlas.configure(placeholder_text=TEXTY["ph_rozhlas"][j])
        self.btn_kopirovat_ip.configure(text=TEXTY["btn_copy_ip"][j])
        
        try:
            if "0%" not in self.lbl_progress.cget("text") and "%" not in self.lbl_progress.cget("text"):
                self.lbl_progress.config(text=TEXTY["msg_ready"][j])
        except: pass

        for ip, hr_data in self.seznam_hracu.items():
            if "btn_file" in hr_data:
                hr_data["btn_file"].configure(text=TEXTY["btn_file_player"][j])
            if "btn_msg" in hr_data:
                hr_data["btn_msg"].configure(text=TEXTY["btn_chat_player"][j])

        # Překlad roletky úloh za běhu
        pocet_uloh = len(self.aktivni_ulohy) if hasattr(self, 'aktivni_ulohy') else 0
        klic_uloh = "btn_tasks_hide" if hasattr(self, 'ukoly_zobrazeny') and self.ukoly_zobrazeny else "btn_tasks_show"
        try: self.btn_ukoly_toggle.configure(text=f"{TEXTY[klic_uloh][j]} ({pocet_uloh})")
        except: pass

        self.aktualizuj_statistiky()
        self.aktualizuj_vizitku()
        self.aktualizuj_tlacitko_zvuku()
        self.inicializuj_drag_and_drop() 
        
    def aktualizuj_tlacitko_zvuku(self):
        hlavni = getattr(self, 'aktualni_barva_motivu', "#2ecc71")
        if hasattr(self, 'btn_zvuk'):
            if self.zvuky_zapnuty:
                self.btn_zvuk.configure(text="🔊", fg_color=hlavni)
            else:
                self.btn_zvuk.configure(text="🔇", fg_color="#e74c3c")

    def zmenit_motiv(self, nazev_motivu):
        if nazev_motivu not in MOTIVY: return
        barvy = MOTIVY[nazev_motivu]
        hlavni = barvy["main"]
        hover = barvy["hover"]
        okraj = barvy["border"]
        
        self.aktualni_nazev_motivu = nazev_motivu
        self.aktualni_barva_motivu = hlavni

        try:
            with open("lan_motiv.txt", "w", encoding="utf-8") as f: f.write(nazev_motivu)
        except: pass

        try:
            self.btn_auto_ip.configure(fg_color=hlavni, hover_color=hover, border_color=okraj)
            self.btn_pridat.configure(fg_color=hlavni, hover_color=hover)
            self.btn_stahnout_soubor.configure(fg_color=hlavni, hover_color=hover, border_color=okraj)
            self.btn_pridat_hru.configure(fg_color=hlavni, hover_color=hover)
            self.btn_najit_hrace.configure(fg_color=hlavni, hover_color=hover, border_color=okraj)
            self.btn_spustit_hru.configure(fg_color=hlavni, hover_color=hover, border_color=okraj)
            
            self.notebook.configure(segmented_button_selected_color=hlavni, segmented_button_selected_hover_color=hover)
            
            self.chat_box.config(selectbackground=hlavni)
            self.list_souboru.config(selectbackground=hlavni)
            self.list_her.config(selectbackground=hlavni)
            
            self.aktualizuj_tlacitko_zvuku()
            
            for ip, hr_data in self.seznam_hracu.items():
                soucasna = hr_data["canvas"].itemcget(hr_data["dot"], "fill")
                if soucasna not in ["#e74c3c", "gray"]: 
                    hr_data["canvas"].itemconfig(hr_data["dot"], fill=hlavni)
        except: pass

    def zobrazit_o_programu(self):
        import webbrowser
        
        # Zvětšení celého okna na výšku (650 -> 800)
        okno = ctk.CTkToplevel(self.root)
        okno.title(TEXTY["btn_about"][self.jazyk])
        okno.geometry("600x800") 
        okno.configure(fg_color="#141414")
        okno.resizable(False, False)
        
        # Zabrání klikání do hlavního okna, dokud se toto nezavře
        okno.transient(self.root)
        okno.grab_set()

        # Hlavní nadpis
        ctk.CTkLabel(okno, text="LigoLAN 🚀", font=("Arial", 26, "bold"), text_color="#f1c40f").pack(pady=(20, 5))
        ctk.CTkLabel(okno, text="Verze 1.0 (Upgradovaná)", font=("Arial", 13), text_color="#bdc3c7").pack(pady=(0, 15))

        # --- SEKCE KONTAKTŮ A SOCIÁLNÍCH SÍTÍ ---
        ramecek_autor = ctk.CTkFrame(okno, fg_color="#1e1e1e", corner_radius=10)
        # Trochu jsme zmenšili okraje (padx=20 místo 40), aby se tlačítka pohodlně vešla
        ramecek_autor.pack(fill="x", padx=20, pady=10)

        jmeno_autora = "Radek Straka"
        email_autora = "lazy.dota1988@gmail.com"
        odkaz_youtube = "https://youtube.com/@radekstraka3045"
        odkaz_ig = "https://instagram.com/3d_craft88cz" 
        odkaz_github = "https://github.com/LigoLAN/LigoLAN" # <-- NOVÝ ODKAZ

        ctk.CTkLabel(ramecek_autor, text=f"Autor: {jmeno_autora}", font=("Arial", 16, "bold"), text_color="white").pack(pady=(15, 10))

        # Rámeček pro uspořádání tlačítek vedle sebe
        ramecek_odkazy = ctk.CTkFrame(ramecek_autor, fg_color="transparent")
        ramecek_odkazy.pack(pady=(0, 15))

        # Vylepšené tlačítko e-mailu (kopírování do schránky)
        def kopirovat_email():
            self.root.clipboard_clear()
            self.root.clipboard_append(email_autora)
            btn_email.configure(text="Zkopírováno ✔️", fg_color="#2ecc71")
            self.root.after(1500, lambda: btn_email.configure(text="📧 E-mail", fg_color="#3498db"))

        # VŠECHNA TLAČÍTKA JSOU NYNÍ ŠIROKÁ 110px (aby se jich vešlo 4 vedle sebe)
        btn_email = ctk.CTkButton(ramecek_odkazy, text="📧 E-mail", width=110, height=35, fg_color="#3498db", hover_color="#2980b9", font=("Arial", 12, "bold"), command=kopirovat_email)
        btn_email.grid(row=0, column=0, padx=6)

        yt_text = "📺 YouTube" if self.jazyk == "CZ" else "📺 YouTube"
        btn_yt = ctk.CTkButton(ramecek_odkazy, text=yt_text, width=110, height=35, fg_color="#e74c3c", hover_color="#c0392b", font=("Arial", 12, "bold"), command=lambda: webbrowser.open(odkaz_youtube))
        btn_yt.grid(row=0, column=1, padx=6)

        btn_ig = ctk.CTkButton(ramecek_odkazy, text="📸 Instagram", width=110, height=35, fg_color="#9b59b6", hover_color="#8e44ad", font=("Arial", 12, "bold"), command=lambda: webbrowser.open(odkaz_ig))
        btn_ig.grid(row=0, column=2, padx=6)
        
        # --- NOVÉ TLAČÍTKO GITHUB ---
        btn_gh = ctk.CTkButton(ramecek_odkazy, text="🐙 GitHub", width=110, height=35, fg_color="#2c3e50", hover_color="#1a252f", font=("Arial", 12, "bold"), command=lambda: webbrowser.open(odkaz_github))
        btn_gh.grid(row=0, column=3, padx=6)
        # ----------------------------------------

        # --- NOVÝ SPOJENÝ TEXT (POPIS PROGRAMU + LICENCE) ---
        if self.jazyk == "CZ":
            uvod = "Vytvořeno hráčem pro hráče.\nCílem je zachránit LAN párty a ušetřit nervy s nastavováním sítě!"
            
            kompletni_text = (
                "🎯 O PROGRAMU LigoLAN:\n"
                "Tento nástroj byl stvořen pro záchranu každé LAN párty. Už žádné hodiny "
                "ztracené nefunkčním spojením a blokováním ve Windows Firewallu.\n\n"
                "Hlavní funkce:\n"
                "• Automatické a bezpečné nastavení Firewallu pro hladké spojení.\n"
                "• Chytrá správa IP adres (funguje napřímo přes kabel i přes router).\n"
                "• Herní radar, který automaticky detekuje běžící hry ostatních hráčů.\n"
                "• Bleskové sdílení souborů a složek bez nutnosti USB flashek.\n"
                "• Integrovaný textový chat a šifrovaný hlasový kanál (Voice Squad).\n\n"
                "---------------------------------------------------------------------------------\n\n"
                "Licence a Právní ujednání (MIT License):\n\n"
                "Tento software je poskytován jako Open Source a zcela zdarma. "
                "Kopírování, úpravy a distribuce jsou povoleny za těchto 3 podmínek:\n"
                "1. Uvedení jména původního autora.\n"
                "2. Uvedení odkazu na oficiální zdroj.\n"
                "3. Zachování tohoto znění licence.\n\n"
                "Software je poskytován „tak, jak je“, bez jakýchkoli záruk. Autor nenese "
                "odpovědnost za škody či ztráty dat vzniklé jeho používáním."
            )
            zavrit_text = "Zavřít"
        else:
            uvod = "Created by a gamer for gamers.\nThe goal is to save LAN parties and eliminate network setup headaches!"
            
            kompletni_text = (
                "🎯 ABOUT LigoLAN:\n"
                "This tool was created to save every LAN party. No more hours lost "
                "due to broken connections and Windows Firewall blocks.\n\n"
                "Key Features:\n"
                "• Automatic & secure Firewall setup for smooth connections.\n"
                "• Smart IP address management (works with direct cables and routers).\n"
                "• Game radar that automatically detects running games of other players.\n"
                "• Lightning-fast file and folder sharing without USB drives.\n"
                "• Integrated text chat and private voice channel (Voice Squad).\n\n"
                "---------------------------------------------------------------------------------\n\n"
                "License and Legal Disclaimer (MIT License):\n\n"
                "This software is provided as Open Source and completely free of charge. "
                "Copying, modification, and distribution are permitted under 3 conditions:\n"
                "1. Include the original author's name.\n"
                "2. Provide a link to the official source.\n"
                "3. Keep this exact license text intact.\n\n"
                "The software is provided 'as is', without any warranties. The author "
                "is not liable for any damages or data loss resulting from its use."
            )
            zavrit_text = "Close"

        ctk.CTkLabel(okno, text=uvod, font=("Arial", 13), text_color="white", justify="center").pack(pady=10)

        # Zvětšené Profesionální tmavé textové pole (Výška 300 místo 140)
        text_box = ctk.CTkTextbox(okno, height=300, width=520, fg_color="#1a1a1a", text_color="#ecf0f1", corner_radius=8, border_width=1, border_color="#333333")
        text_box.pack(pady=10)
        text_box.insert("0.0", kompletni_text)
        text_box.configure(state="disabled") # Zamkne text proti úpravám

        # Velké a jasné zavírací tlačítko
        ctk.CTkButton(okno, text=zavrit_text, command=okno.destroy, fg_color="#c0392b", hover_color="#922b21", text_color="white", font=("Arial", 14, "bold"), width=150, height=45, corner_radius=8).pack(pady=(15, 20))

    def prepni_zvuky(self):
        self.zvuky_zapnuty = not self.zvuky_zapnuty 
        self.aktualizuj_tlacitko_zvuku()

    def zobrazit_podporu(self):
        import webbrowser
        odkaz_kofi = "https://ko-fi.com/goodgames88"
        adresa_btc = "bc1qw8utm3daspa5qvnnxc8eznvdtc7xpa8stjndp5"
        adresa_eth = "0x7E453349678ea7e164c2A2e78D2590815F7FB9c8"
        adresa_xrp = "r9k73sycGk8uKzbH26jxxYMPbKYcMkQGHX"
        adresa_ltc = "LRaTRP4sGGJQXJ1CZpkjovpYNRHZCZFoUq"
        
        # Moderní temné okno s uzamčením (modální okno)
        okno = ctk.CTkToplevel(self.root)
        okno.title(TEXTY["btn_donate"][self.jazyk])
        okno.geometry("550x520")
        okno.configure(fg_color="#141414")
        okno.resizable(False, False)
        okno.transient(self.root)
        okno.grab_set()
        
        if self.jazyk == "CZ":
            titulek = "Podpora autora 🍻"
            text = "Pokud ti tento nástroj zachránil LAN párty\nnebo ušetřil nervy, budu vděčný za jakoukoliv podporu!"
            kofi_text = "☕ Podpořit přes Ko-fi (Karta / PayPal)"
            kopi_text = "Kopírovat"
            zavrit = "Zavřít"
        else:
            titulek = "Support the Author 🍻"
            text = "If this tool saved your LAN party or your sanity,\nI'd highly appreciate any support!"
            kofi_text = "☕ Support via Ko-fi (Card / PayPal)"
            kopi_text = "Copy"
            zavrit = "Close"
            
        ctk.CTkLabel(okno, text=titulek, font=("Arial", 22, "bold"), text_color="#f1c40f").pack(pady=(20, 5))
        ctk.CTkLabel(okno, text=text, font=("Arial", 13), text_color="#bdc3c7", justify="center").pack(pady=(0, 20))
        
        ctk.CTkButton(okno, text=kofi_text, command=lambda: webbrowser.open(odkaz_kofi), fg_color="#e74c3c", hover_color="#c0392b", text_color="white", font=("Arial", 14, "bold"), height=45, corner_radius=8).pack(pady=(0, 20))
        
        # Hlavní tmavý rámeček pro kryptoměny
        frame_crypto = ctk.CTkFrame(okno, fg_color="#1e1e1e", corner_radius=10)
        frame_crypto.pack(fill="x", padx=30, pady=5)
        
        def kopirovat(text_k_ulozeni, tlacitko):
            self.root.clipboard_clear()
            self.root.clipboard_append(text_k_ulozeni)
            
            # Přečteme původní hodnoty pro pozdější návrat (u CTk používáme cget)
            puvodni_text = tlacitko.cget("text")
            puvodni_barva = tlacitko.cget("fg_color")
            
            text_ok = "Zkopírováno ✔️" if self.jazyk == "CZ" else "Copied ✔️"
            tlacitko.configure(text=text_ok, fg_color="#2ecc71")
            self.root.after(1500, lambda: tlacitko.configure(text=puvodni_text, fg_color=puvodni_barva))

        # Naše nová, chytrá DRY (Don't Repeat Yourself) funkce
        def vytvor_crypto_radek(rodic, mena, adresa):
            radek = ctk.CTkFrame(rodic, fg_color="transparent")
            radek.pack(fill="x", pady=8, padx=15)
            
            ctk.CTkLabel(radek, text=mena, font=("Arial", 13, "bold"), text_color="#f39c12", width=45, anchor="w").pack(side="left")
            
            # Moderní čtecí políčko
            vstup = ctk.CTkEntry(radek, font=("Arial", 12), fg_color="#2a2a2a", text_color="white", border_color="#333333", height=35)
            vstup.insert(0, adresa)
            vstup.configure(state="readonly")
            vstup.pack(side="left", fill="x", expand=True, padx=10)
            
            # Dynamické předání parametrů přes lambdu (a=adresa, b=btn_copy)
            btn_copy = ctk.CTkButton(radek, text=kopi_text, fg_color="#3498db", hover_color="#2980b9", font=("Arial", 12, "bold"), width=90, height=35, corner_radius=6)
            btn_copy.configure(command=lambda a=adresa, b=btn_copy: kopirovat(a, b))
            btn_copy.pack(side="right")

        # Samotné vykreslení je teď krásně čisté
        vytvor_crypto_radek(frame_crypto, "BTC:", adresa_btc)
        vytvor_crypto_radek(frame_crypto, "ETH:", adresa_eth)
        vytvor_crypto_radek(frame_crypto, "XRP:", adresa_xrp)
        vytvor_crypto_radek(frame_crypto, "LTC:", adresa_ltc)
        
        # Zavírací tlačítko dole
        ctk.CTkButton(okno, text=zavrit, command=okno.destroy, fg_color="#7f8c8d", hover_color="#95a5a6", text_color="white", font=("Arial", 14, "bold"), width=150, height=45, corner_radius=8).pack(pady=(20, 10))

    def spustit_duhove_silenstvi(self):
        # Aby se to nespustilo 10x přes sebe a nespadlo to
        if getattr(self, 'duha_bezi', False): return
        self.duha_bezi = True
        
        # --- PŘEHRÁNÍ SKUTEČNÉHO ZVUKU (doom.wav) ---
        if self.zvuky_zapnuty:
            try:
                # Použijeme tu naši magickou funkci na hledání souborů
                cesta_zvuku = ziskej_cestu("doom.wav")
                if os.path.exists(cesta_zvuku):
                    # SND_FILENAME říká, že je to soubor. SND_ASYNC říká, ať hraje na pozadí a neseká grafiku!
                    winsound.PlaySound(cesta_zvuku, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except: pass
            
        puvodni_motiv = self.aktualni_nazev_motivu
        barvy = ["#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#0000ff", "#4b0082", "#9400d3"]
        
        def blikni(krok):
            # 530 kroků á 200ms = přesně 106 vteřin (1 min 46 sec)
            if krok < 530: 
                barva = barvy[krok % len(barvy)]
                try:
                    self.btn_auto_ip.configure(fg_color=barva)
                    self.chat_box.config(selectbackground=barva)
                except: pass
                # Za 200 ms zavolá samo sebe pro další barvu
                self.root.after(200, lambda: blikni(krok + 1))
            else:
                # KONEC PÁRTY: Vracíme barvy do normálu
                self.duha_bezi = False
                self.zmenit_motiv(puvodni_motiv)
                
                # Pro jistotu hudbu natvrdo vypneme, kdyby o pár milisekund přesahovala
                if self.zvuky_zapnuty:
                    try: winsound.PlaySound(None, winsound.SND_PURGE)
                    except: pass
                
        blikni(0) # Odpálíme první bliknutí    

    def pri_ukonceni(self):
        titulek = "Ukončení a Úklid sítě" if self.jazyk == "CZ" else "Exit & Network Cleanup"
        dotaz = "LAN Párty končí?\n\nPřeješ si před vypnutím programu zamést stopy?\n1. Uzavře díry ve Windows Firewallu.\n2. Vrátí IP adresu na automatiku (DHCP pro domácí internet)." if self.jazyk == "CZ" else "Is the LAN Party over?\n\nDo you want to clean up before exiting?\n1. Closes holes in Windows Firewall.\n2. Reverts IP to automatic (DHCP for home internet)."
        
        if messagebox.askyesno(titulek, dotaz):
            prikazy_uklid = self._dostat_prikazy_firewall_uklid()
            try:
                adapter_k_uklidu = self.combo_adapter.get().strip()
                if adapter_k_uklidu:
                    prikazy_uklid.append(f'netsh interface ipv4 set address name="{adapter_k_uklidu}" source=dhcp')
            except: pass
            self.vykonat_jako_spravce(prikazy_uklid)
            
        # 1. Odvážeme události pohybu myší a kolečka napříč celou aplikací, ať na nás při umírání nekřičí chyby
        try: self.root.unbind_all("<MouseWheel>")
        except: pass
        try: self.root.unbind_all("<Button-4>")
        except: pass
        try: self.root.unbind_all("<Button-5>")
        except: pass
        
        # --- ZAVŘENÍ PORTŮ PŘED UKONČENÍM ---
        try:
            if hasattr(self, 'udp_sock') and self.udp_sock: self.udp_sock.close()
            if hasattr(self, 'tcp_server') and self.tcp_server: self.tcp_server.close()
        except: pass

        # 2. Vynutíme rychlé ukončení všeho - radaru, sítě, chatu
        import os
        self.root.quit() # Odpojí grafiku
        os._exit(0) # Okamžitě ustřihne hlavní Python vlákno (žádní duchové, žádné chybové výpisy z umírajícího okna)

    def _zjistit_hw_na_pozadi(self):
        import time
        # ZÁCHRANA: Necháme grafické okno nejdřív v klidu 15 vteřinu vykreslit!
        time.sleep(15.0) 

        try:
            # 1. Výchozí záchranné hodnoty
            cpu_name = "Neznámý CPU"
            ram_gb = 0
            gpu_name = "Neznámá GPU"
            
            # 2. Bezpečné zjištění CPU (Registry)
            try:
                import winreg
                klicek = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu, _ = winreg.QueryValueEx(klicek, "ProcessorNameString")
                cpu_name = cpu.replace("Intel(R) Core(TM) ", "").replace("AMD Ryzen ", "Ryzen ").replace(" CPU", "").replace(" @", " |").strip()
            except:
                import platform
                try: cpu_name = platform.processor()
                except: pass

            # 3. Nativní zjištění paměti RAM
            try:
                import ctypes
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_uint), ("dwMemoryLoad", ctypes.c_uint),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong)
                    ]
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                ram_gb = round(stat.ullTotalPhys / (1024**3))
            except: pass

            # 4. Zjištění grafiky (Bleskové přes registry, hledá VŠECHNY a vybere tu herní!)
            try:
                import winreg
                klicek_gpu_base = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}")
                nalezene_grafiky = []
                
                # Projdeme prvních 5 možných záznamů, abychom našli všechny grafiky v PC
                for i in range(5):
                    try:
                        sub_key_name = f"{i:04d}" # Složí čísla "0000", "0001", "0002"...
                        sub_key = winreg.OpenKey(klicek_gpu_base, sub_key_name)
                        gpu, _ = winreg.QueryValueEx(sub_key, "DriverDesc")
                        
                        # Vyfiltrujeme základní Windows ovladače, které nás nezajímají
                        if gpu and "Basic Display" not in gpu:
                            cisty_nazev = gpu.replace("NVIDIA GeForce ", "NVIDIA ").replace("AMD Radeon ", "AMD ").strip()
                            nalezene_grafiky.append(cisty_nazev)
                    except:
                        pass # Pokud klíč neexistuje, prostě jede dál
                
                if nalezene_grafiky:
                    # Chytrý filtr: Hledá klíčová slova opravdových herních grafik
                    herni_gpu = [g for g in nalezene_grafiky if "NVIDIA" in g.upper() or "RTX" in g.upper() or "GTX" in g.upper() or "RX " in g.upper()]
                    
                    if herni_gpu:
                        gpu_name = herni_gpu[0] # Našli jsme herní dělo!
                    else:
                        gpu_name = nalezene_grafiky[-1] # Pokud nemá jasně herní název, vezmeme tu poslední nalezenou
            except:
                pass

            # 5. Sestavení textu
            hw_text = f"⚙️ CPU: {cpu_name}   |   🧠 RAM: {ram_gb} GB   |   🎮 GPU: {gpu_name}"
            
            # 6. Bleskový a 100% bezpečný zápis do okna
            def prepis_stitku():
                try: 
                    self.lbl_hw_info.configure(text=hw_text)
                except Exception as e: 
                    self.zapsat_do_logu(f"[Chyba zápisu do GUI]: {e}")

            self.root.after(0, prepis_stitku)

        # 7. Absolutní záchranná síť: Kdyby vlákno havarovalo, vypíše se to aspoň sem
        except Exception as celkova_chyba:
            self.zapsat_do_logu(f"[Kritická HW chyba vlákna]: {celkova_chyba}")
            try: 
                self.root.after(0, lambda: self.lbl_hw_info.configure(text="⚙️ HW Info: Skryto (Chyba čtení z Windows)"))
            except: pass
        
class ModerniAppka(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
        self.temna_hladicka()
        self.zakazat_uspani() # NOVÉ: Voláme ochranu BMAXu
        
        # --- NASTAVENÍ IKONY OKNA ---
        try:
            cesta_k_ikone = ziskej_cestu("ikona.ico")
            self.iconbitmap(cesta_k_ikone)
        except Exception:
            pass # Pokud ikona chybí, program tiše pokračuje bez ní
        # ----------------------------

    def zakazat_uspani(self):
        # Magický příkaz: Řekne Windows, ať neuspává vlákno, když je okno na liště
        try:
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
        except: pass

    def temna_hladicka(self):
        try:
            import ctypes
            self.update()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(ctypes.c_int(2)), 4)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(2)), 4)
        except: pass

if __name__ == "__main__":
    try:
        root = ModerniAppka() 
    except Exception as e:
        root = ctk.CTk() 
        root.withdraw() 
        import tkinter.messagebox as mb
        mb.showerror("Kritická chyba", f"Knihovna tkinterdnd2 chybí!\nSpusťte cmd a zadejte:\npip install tkinterdnd2\n\nDetail: {e}")
        root.destroy()
        root = ctk.CTk() 
        
    app = LANPartyTool(root)
    
    try:
        root.mainloop()
    except Exception:
        # Pokud se po kliknutí na křížek (během smrti okna) objeví výše zmíněná chyba ctk_scrollable_frame, 
        # tento blok ji potichu ignoruje a natvrdo program zařízne.
        import os
        os._exit(0)
