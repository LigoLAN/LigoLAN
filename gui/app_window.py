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
import uuid
from core.system_utils import SystemUtils
from core.file_manager import FileManager
from network.udp_server import UdpServer
from network.tcp_transfer import TcpTransfer
from gui.tab_squad import TabSquad
from gui.tab_files import TabFiles
from gui.tab_radar import TabRadar
from gui.tab_games import TabGames

from config import *

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

VERZE_PROGRAMU = "1.1"
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
        if mb.askyesno("Update / Aktualizace", f"Dostupná nová verze / New version available: {nova_verze}.\nChceš otevřít stránku pro stažení / Open download page?"):
            webbrowser.open(URL_STAZENI)

    import threading
    threading.Thread(target=proces_kontroly, daemon=True).start()

class LANPartyTool:
    def __init__(self, root):
        self.root = root
        self.root.title("LigoLAN v.1.1")    
        
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

        # Zvýšeno z 5 na 20 pracovníků pro plynulý chod i při masivních výpadcích desítek PC
        self.radar_executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)

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
        self.udp_server = UdpServer(self)
        self.tcp_server = TcpTransfer(self)

        # --- NOVÉ: FRONTA STAHOVÁNÍ ---
        self.prave_stahuji_od = set() # Pamatuje si IP adresy, od kterých už něco stahujeme
        self.fronta_stahovani = {}    # Zde budou čekat soubory, než na ně přijde řada
        
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

        # --- LIGO ID (Bezpečnost a stabilita sítě) ---
        if os.path.exists(SOUBOR_ID):
            try:
                with open(SOUBOR_ID, "r", encoding="utf-8") as f:
                    self.ligo_id = f.read().strip()
            except: self.ligo_id = ""
        else:
            self.ligo_id = ""
            
        if not self.ligo_id or len(self.ligo_id) < 8:
            # Generování bezpečného a nezměnitelného ID
            self.ligo_id = "LIGO-" + str(uuid.uuid4()).split("-")[1].upper() + "-" + str(uuid.uuid4()).split("-")[2].upper()
            try:
                with open(SOUBOR_ID, "w", encoding="utf-8") as f:
                    f.write(self.ligo_id)
                # Zamčení souboru proti přepsání (Bezpečnost: Read-Only)
                os.chmod(SOUBOR_ID, 0o444) 
            except: pass

        self.root.title(f"LigoLAN v1.1  |  {TEXTY['win_title_pc_code'][self.jazyk]}: {self.ligo_id}")    

        self.btn_jazyk = ctk.CTkButton(frame_user, text=self.jazyk, command=self.prepni_jazyk, fg_color="#1a1a1a", hover_color="#2ecc71", text_color="#bdc3c7", font=("Arial", 13, "bold"), width=60, corner_radius=6, border_width=1, border_color="#333333")
        self.btn_jazyk.pack(side="right", padx=10, pady=10)
        
        self.btn_about = ctk.CTkButton(frame_user, text=TEXTY["btn_about"][self.jazyk], command=self.zobrazit_o_programu, fg_color="#1a1a1a", hover_color="#2ecc71", text_color="#bdc3c7", font=("Arial", 13, "bold"), width=100, corner_radius=6, border_width=1, border_color="#333333")
        self.btn_about.pack(side="right", padx=5)
        
        self.btn_donate = ctk.CTkButton(frame_user, text=TEXTY["btn_donate"][self.jazyk], command=self.zobrazit_podporu, fg_color="#1a1a1a", hover_color="#2ecc71", text_color="#bdc3c7", font=("Arial", 13, "bold"), width=100, corner_radius=6, border_width=1, border_color="#333333")
        self.btn_donate.pack(side="right", padx=5)

        # --- NOVÉ TLAČÍTKO: POKROČILÉ SÍTĚ (v horní liště) ---
        self.btn_pokrocile = ctk.CTkButton(frame_user, text="⚙ Pokročilé sítě", command=self.prepnout_zobrazeni_pokrocilych_ip, fg_color="#1a1a1a", hover_color="#2ecc71", text_color="#bdc3c7", font=("Arial", 13, "bold"), width=100, corner_radius=6, border_width=1, border_color="#333333")
        self.btn_pokrocile.pack(side="right", padx=5)

        self.lbl_tvoje_prezdivka = ctk.CTkLabel(frame_user, text=TEXTY["lbl_nick"][self.jazyk], font=("Arial", 15, "bold"), text_color="#f1c40f")
        self.lbl_tvoje_prezdivka.pack(side="left", padx=10)
        
        self.entry_nick = ctk.CTkEntry(frame_user, font=("Arial", 14), width=180, corner_radius=8, border_color="#34495e")
        
        ulozeny_nick = "Hráč" if self.jazyk == "CZ" else "Player"
        if os.path.exists(SOUBOR_NICK):
            try:
                with open(SOUBOR_NICK, "r", encoding="utf-8") as f:
                    ulozeny_nick = f.read().strip() or "Hráč"
            except: pass
            
        self.entry_nick.insert(0, ulozeny_nick)
        self.entry_nick.pack(side="left", padx=10)
        self.entry_nick.bind("<KeyRelease>", self.aktualizuj_vizitku)

        # Vytvoření hlavního rámečku (Zpět na průhledné kvůli tapetě)
        self.frame_moje_pc = ctk.CTkFrame(root, fg_color="transparent", height=160, corner_radius=10, border_width=1, border_color="#333333")
        self.frame_moje_pc.pack(fill="x", padx=10, pady=(5, 10))
        self.frame_moje_pc.pack_propagate(False)

        # --- NAČTENÍ IKONY GPU ---
        cesta_k_gpu = ziskej_cestu("icons/gpu.png")
        if not os.path.exists(cesta_k_gpu):
            self.ikona_gpu = None
            self.zapsat_do_logu("[CHYBA] Soubor gpu.png nebyl nalezen ve složce aplikace.")
        else:
            try:
                img_gpu = Image.open(cesta_k_gpu)
                # Použijeme stejnou zvětšenou velikost jako u procesoru (30x30)
                self.ikona_gpu = ctk.CTkImage(light_image=img_gpu, dark_image=img_gpu, size=(30, 30))
            except Exception as e:
                self.zapsat_do_logu(f"[CHYBA] Nepodařilo se načíst ikonu GPU: {e}")
                self.ikona_gpu = None

        # --- NAČTENÍ IKONY RAM ---
        cesta_k_ram = ziskej_cestu("icons/ram.png")
        if not os.path.exists(cesta_k_ram):
            self.ikona_ram = None
        else:
            try:
                img_ram = Image.open(cesta_k_ram)
                self.ikona_ram = ctk.CTkImage(light_image=img_ram, dark_image=img_ram, size=(30, 30))
            except Exception: self.ikona_ram = None

        # --- NAČTENÍ IKONY PC a IP ---
        cesta_k_pc = ziskej_cestu("icons/pc.png")
        if not os.path.exists(cesta_k_pc):
            self.ikona_pc = None
        else:
            try: self.ikona_pc = ctk.CTkImage(light_image=Image.open(cesta_k_pc), size=(24, 24))
            except: self.ikona_pc = None

        cesta_k_ip = ziskej_cestu("icons/ip.png")
        if not os.path.exists(cesta_k_ip):
            self.ikona_ip = None
        else:
            try: self.ikona_ip = ctk.CTkImage(light_image=Image.open(cesta_k_ip), size=(24, 24))
            except: self.ikona_ip = None

        # --- NAČTENÍ IKONY PŘIPOJENO ---
        cesta_k_connected = ziskej_cestu("icons/connected.png")
        if not os.path.exists(cesta_k_connected):
            self.ikona_connected = None
        else:
            try: self.ikona_connected = ctk.CTkImage(light_image=Image.open(cesta_k_connected), size=(24, 24))
            except: self.ikona_connected = None    

        # --- NAČTENÍ IKONY PROCESORU ---
        cesta_k_procesoru = ziskej_cestu("icons/procesor.png")
        if not os.path.exists(cesta_k_procesoru):
            self.ikona_procesoru = None 
        else:
            try:
                img_procesor = Image.open(cesta_k_procesoru)
                # Nastavíme velikost na 20x20, aby to ladilo s textem
                self.ikona_procesoru = ctk.CTkImage(light_image=img_procesor, dark_image=img_procesor, size=(30, 30))
            except Exception as e:
                self.zapsat_do_logu(f"[CHYBA] Nepodařilo se načíst ikonu procesoru: {e}")
                self.ikona_procesoru = None

        # --- NAČTENÍ IKONY POPELNICE ---
        cesta_k_popelnici = ziskej_cestu("icons/popelnice.png")
        if not os.path.exists(cesta_k_popelnici):
            self.zapsat_do_logu(f"[CHYBA] Soubor popelnice.png nebyl nalezen na cestě: {cesta_k_popelnici}")
            # Fallback (pro jistotu): vytvoříme prázdnou ikonu, aby kód nespadl
            self.ikona_popelnice = None 
        else:
            try:
                img_popelnice = Image.open(cesta_k_popelnici)
                # Nastavíme velikost na 28x28 pro tlačítko
                self.ikona_popelnice = ctk.CTkImage(light_image=img_popelnice, dark_image=img_popelnice, size=(28, 28))
            except Exception as e:
                self.zapsat_do_logu(f"[CHYBA] Nepodařilo se načíst ikonu popelnice: {e}")
                self.ikona_popelnice = None
     
        # --- NAČTENÍ IKONY DISKETY PRO CHAT ---
        cesta_k_diskete = ziskej_cestu("icons/disketa.png")
        if not os.path.exists(cesta_k_diskete):
            self.zapsat_do_logu(f"[CHYBA] Soubor disketa.png nebyl nalezen na cestě: {cesta_k_diskete}")
            self.ikona_disketa = None 
        else:
            try:
                img_disketa = Image.open(cesta_k_diskete)
                # Velikost 24x24 bude v tom 45px tlačítku vypadat akorát
                self.ikona_disketa = ctk.CTkImage(light_image=img_disketa, dark_image=img_disketa, size=(40, 40))
            except Exception as e:
                self.zapsat_do_logu(f"[CHYBA] Nepodařilo se načíst ikonu diskety: {e}")
                self.ikona_disketa = None

        # --- NAČTENÍ IKONY AKTUALIZACE PRO SDÍLENÍ ---
        cesta_k_aktualizaci = ziskej_cestu("icons/aktualizovat.png")
        if not os.path.exists(cesta_k_aktualizaci):
            self.zapsat_do_logu(f"[CHYBA] Soubor aktualizovat.png nebyl nalezen na cestě: {cesta_k_aktualizaci}")
            self.ikona_aktualizovat = None 
        else:
            try:
                img_akt = Image.open(cesta_k_aktualizaci)
                # Zvětšeno z 24x24 na 28x28 px
                self.ikona_aktualizovat = ctk.CTkImage(light_image=img_akt, dark_image=img_akt, size=(28, 28))
            except Exception as e:
                self.zapsat_do_logu(f"[CHYBA] Nepodařilo se načíst ikonu aktualizovat: {e}")
                self.ikona_aktualizovat = None

        # --- NAČTĚNÍ OBRÁZKU NA POZADÍ (ULTIMÁTNÍ FIX - OŘEZ MÍSTO ZMĚNY VELIKOSTI) ---
        try:
            cesta_pozadi = ziskej_cestu("icons/pozadi.jpg") 
            obrazek_pil = Image.open(cesta_pozadi)
            
            # 1. Vytvoříme jeden OBŘÍ obrázek (2500px na šířku). Výška zůstává 160.
            self.pozadi_img = ctk.CTkImage(light_image=obrazek_pil, dark_image=obrazek_pil, size=(2500, 160))
            self.lbl_pozadi = ctk.CTkLabel(self.frame_moje_pc, text="", image=self.pozadi_img)
            
            # 2. Vložíme ho doprostřed rámečku. C++ jádro Tkinteru samo skryje přečuhující okraje!
            # Není potřeba žádný Python kód, žádné události, žádná zátěž na procesor.
            self.lbl_pozadi.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor="center")
            
        except Exception as e:
            self.zapsat_do_logu(f"Nepodařilo se načíst obrázek pozadí: {e}")
            
        # --- PŘIDÁNO: Napojení kliknutí na profi přesun ---
        self.frame_moje_pc.bind("<Button-1>", self.presun_okna_windows)
        # Obrázek leží přes rámeček, takže musíme kliknutí chytat i na něm!
        if hasattr(self, 'lbl_pozadi'):
            self.lbl_pozadi.bind("<Button-1>", self.presun_okna_windows)
        # --------------------------------------------------
        
        # ----------------------------------------     
        
        self.zvuky_zapnuty = True
        # Zvuk: Stealth tlačítko
        self.btn_zvuk = ctk.CTkButton(self.frame_moje_pc, text="🔊", command=self.prepni_zvuky, bg_color="transparent", fg_color="#1a1a1a", hover_color="#333333", border_width=1, border_color="#2ecc71", text_color="#2ecc71", font=("Arial", 15), width=40, height=40, corner_radius=20)
        self.btn_zvuk.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10) 

        # --- NOVÉ: Tajné mini-tlačítko v hlavičce, které čeká na připojení k síti ---
        self.btn_auto_ip_mini = ctk.CTkButton(self.frame_moje_pc, text="", command=self.automaticky_nastavit_ip_kabel, font=("Arial", 10, "bold"), height=40, width=170) 
        
        # 1. Vytvoříme zaoblenou kapsli pro Nick (úplně stejnou jako má IP a HW)
        self.ramecek_nick = ctk.CTkFrame(self.frame_moje_pc, bg_color="transparent", fg_color="#141414", border_width=1, border_color="#333333", corner_radius=15)
        self.ramecek_nick.place(relx=0.5, rely=0.22, anchor="center")

        # 2. Samotný text. VŠIMNI SI, ŽE ZMIZELO padx A pady Z TOHOTO ŘÁDKU!
        self.lbl_velky_nick = ctk.CTkLabel(self.ramecek_nick, text=ulozeny_nick, bg_color="transparent", fg_color="transparent", font=("Impact", 40), text_color="#f1c40f")
        
        # 3. Místo toho jsme padx a pady dali sem. Tím vznikne mezera a okraj konečně vyleze na světlo!
        self.lbl_velky_nick.pack(padx=30, pady=5)

        # IP Rámeček: Plovoucí Tech panel s jemným okrajem
        self.ramecek_ip_info = ctk.CTkFrame(self.frame_moje_pc, bg_color="transparent", fg_color="#141414", border_width=1, border_color="#333333", corner_radius=15, height=35)
        self.ramecek_ip_info.place(relx=0.5, rely=0.52, anchor="center")
        
        # Sekce PC
        self.lbl_pc_icon = ctk.CTkLabel(self.ramecek_ip_info, text="", image=self.ikona_pc)
        self.lbl_pc_icon.pack(side="left", padx=(10, 5), pady=4)
        self.lbl_pc_text = ctk.CTkLabel(self.ramecek_ip_info, text=f"PC: {self.muj_hostname}", font=("Arial", 13, "bold"), text_color="white")
        self.lbl_pc_text.pack(side="left", padx=(0, 10), pady=4)

        ctk.CTkLabel(self.ramecek_ip_info, text="|", font=("Arial", 13), text_color="#555555").pack(side="left", padx=5)

        # Sekce IP
        self.lbl_ip_icon = ctk.CTkLabel(self.ramecek_ip_info, text="", image=self.ikona_ip)
        self.lbl_ip_icon.pack(side="left", padx=10, pady=4)
        self.lbl_ip_text = ctk.CTkLabel(self.ramecek_ip_info, text=f"IP: {self.moje_ip}", font=("Arial", 13, "bold"), text_color="white")
        self.lbl_ip_text.pack(side="left", padx=(0, 10), pady=4)

        ctk.CTkLabel(self.ramecek_ip_info, text="|", font=("Arial", 13), text_color="#555555").pack(side="left", padx=5)

        # Sekce Status (Připojeno)
        self.lbl_status_icon = ctk.CTkLabel(self.ramecek_ip_info, text="", image=self.ikona_connected)
        self.lbl_status_icon.pack(side="left", padx=(10, 0), pady=4)
        
        self.lbl_status_text = ctk.CTkLabel(self.ramecek_ip_info, text=f" {TEXTY['lbl_connected'][self.jazyk]} ", font=("Arial", 13, "bold"), text_color="white")
        self.lbl_status_text.pack(side="left", padx=(5, 10), pady=4)

        # HW Kontejner: Plovoucí Tech panel s jemným okrajem
        self.frame_hw_container = ctk.CTkFrame(self.frame_moje_pc, bg_color="transparent", fg_color="#141414", border_width=1, border_color="#333333", corner_radius=15, height=45)
        self.frame_hw_container.place(relx=0.5, rely=0.82, anchor="center")

        # 1. Sekce Procesor (Ikona + Text)
        self.lbl_cpu_icon = ctk.CTkLabel(self.frame_hw_container, text="", image=self.ikona_procesoru)
        self.lbl_cpu_icon.pack(side="left", padx=(15, 5), pady=6)
        self.lbl_cpu_text = ctk.CTkLabel(self.frame_hw_container, text=TEXTY["lbl_hw_detect"][self.jazyk], font=("Arial", 14, "bold"), text_color="#ecf0f1")
        self.lbl_cpu_text.pack(side="left", padx=(0, 10), pady=6)

        # Separátor (hezká svislá čára)
        self.lbl_sep1 = ctk.CTkLabel(self.frame_hw_container, text="|", font=("Arial", 14), text_color="#555555")
        self.lbl_sep1.pack(side="left", padx=10, pady=6)

        # 2. Sekce Grafika (Ikona + Text)
        self.lbl_gpu_icon = ctk.CTkLabel(self.frame_hw_container, text="", image=self.ikona_gpu)
        self.lbl_gpu_icon.pack(side="left", padx=10, pady=6)
        # Počáteční text čekající na detekci
        text_gpu_waiting = TEXTY["lbl_gpu_detect"][self.jazyk]
        self.lbl_gpu_text = ctk.CTkLabel(self.frame_hw_container, text=text_gpu_waiting, font=("Arial", 14, "bold"), text_color="#ecf0f1")
        self.lbl_gpu_text.pack(side="left", padx=(0, 10), pady=6)

        # Separátor 2
        self.lbl_sep2 = ctk.CTkLabel(self.frame_hw_container, text="|", font=("Arial", 14), text_color="#555555")
        self.lbl_sep2.pack(side="left", padx=10, pady=6)

        # 3. Sekce RAM (Ikona + Text)
        self.lbl_ram_icon = ctk.CTkLabel(self.frame_hw_container, text="", image=self.ikona_ram)
        self.lbl_ram_icon.pack(side="left", padx=10, pady=6)
        
        text_ram_waiting = TEXTY["lbl_ram_detect"][self.jazyk]
        self.lbl_ram_text = ctk.CTkLabel(self.frame_hw_container, text=text_ram_waiting, font=("Arial", 14, "bold"), text_color="#ecf0f1")
        self.lbl_ram_text.pack(side="left", padx=(0, 10), pady=6)
        
        # Odložíme start zjišťování hardwaru o přesně 15 vteřin (15000 milisekund).
        # Díky tomu má pomalejší PC dostatek času vykreslit okno a připojit se k síti, než začneme číst paměť a registry.
        self.root.after(15000, lambda: threading.Thread(target=self._zjistit_hw_na_pozadi, daemon=True).start())

        self.frame_jednoduche_ip = ctk.CTkFrame(root, fg_color="transparent")
        self.frame_jednoduche_ip.pack(fill="x", padx=10, pady=(0, 10))
        
        self.btn_auto_ip = ctk.CTkButton(self.frame_jednoduche_ip, text=TEXTY["btn_auto_connect"][self.jazyk], command=self.automaticky_nastavit_ip_kabel, fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=("Arial", 16, "bold"), height=50, corner_radius=8, border_width=3, border_color="#1d8348")
        self.btn_auto_ip.pack(fill="x", side="left", expand=True, padx=(0, 10))
        
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
        # --- ODDĚLOVAČ A NOVÝ RÁMEČEK PRO MOTIVY A KOPÍROVÁNÍ IP ---
        ttk.Separator(self.frame_ip, orient="horizontal").grid(row=5, column=0, columnspan=3, sticky="ew", pady=15)
        
        r_doplnky = tk.Frame(self.frame_ip, bg="#2c3e50")
        r_doplnky.grid(row=6, column=0, columnspan=3, pady=(0, 5))

        # Tlačítko Kopírovat IP (nyní elegantně tmavé)
        self.btn_kopirovat_ip = ctk.CTkButton(r_doplnky, text=TEXTY["btn_copy_ip"][self.jazyk], command=self.zkopirovat_moji_ip, fg_color="#34495e", hover_color="#2c3e50", text_color="white", font=("Arial", 12, "bold"), height=30, corner_radius=6)
        self.btn_kopirovat_ip.pack(side="left", padx=(0, 30))

        # Barevné tečky
        self.lbl_theme = tk.Label(r_doplnky, text=TEXTY["lbl_theme"][self.jazyk], bg="#2c3e50", fg="white", font=("Arial", 11))
        self.lbl_theme.pack(side="left", padx=(10, 5))

        for nazev, barvy in MOTIVY.items():
            btn_b = ctk.CTkButton(r_doplnky, text="", width=20, height=20, corner_radius=10, fg_color=barvy["main"], hover_color=barvy["hover"], command=lambda n=nazev: self.zmenit_motiv(n))
            btn_b.pack(side="left", padx=3)

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
        self.paned_window = tk.PanedWindow(root, orient="vertical", bg="#0a0a0a", bd=0, sashwidth=8, sashcursor="sb_v_double_arrow", opaqueresize=False)
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

        # --- PAMĚŤ PRO HERNÍ LOBBY ---
        self.rozbaleni_radaru = set()
        self.prekresluji_radar = False       

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

        # --- ZAPOJENÍ ZÁLOŽKY SQUAD ---
        self.squad_manager = TabSquad(self, self.tab_squad)

        r_rozhlas = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        r_rozhlas.pack(side="bottom", fill="x", padx=5, pady=(5, 10))
        
        self.btn_rozhlas = ctk.CTkButton(r_rozhlas, text=TEXTY["btn_rozhlas"][self.jazyk], command=self.poslat_rozhlas, fg_color="#e67e22", hover_color="#d35400", font=("Arial", 14, "bold"), width=150, height=40, corner_radius=8, border_width=2, border_color="#a04000")
        self.btn_rozhlas.pack(side="right", padx=(10, 0))
        
        self.entry_rozhlas = ctk.CTkEntry(r_rozhlas, font=("Arial", 14), placeholder_text=TEXTY["ph_rozhlas"][self.jazyk], height=40, corner_radius=8, fg_color="#ffffff", text_color="#000000", placeholder_text_color="#888888", border_color="#cccccc")
        self.entry_rozhlas.pack(side="left", fill="x", expand=True)
        
        self.entry_rozhlas.bind("<Return>", lambda e: self.poslat_rozhlas())

        self.chat_box = tk.Listbox(self.tab_chat, bg="#ffffff", fg="#000000", font=("Arial", 12), selectbackground="#16a085", selectforeground="#ffffff", bd=1, relief="solid")
        self.chat_box.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # --- ZAPOJENÍ ZÁLOŽKY SDÍLENÍ ---
        self.files_manager = TabFiles(self, self.tab_slozka)

       # --- ZAPOJENÍ ZÁLOŽKY HER ---
        self.games_manager = TabGames(self, self.tab_hry)
        
        self.zapsat_do_logu(TEXTY["log_started"][self.jazyk])
        self.spustit_kontrolu_smycka() 
        self.start_naslouchani()
        self.aktualizuj_tlacitko_zvuku()
        self.inicializuj_drag_and_drop()

        zkontroluj_aktualizace(self.root, tichy_rezim=True)
        
        self.aktualni_nazev_motivu = "Zelena"
        self.aktualni_barva_motivu = "#2ecc71"
        if os.path.exists(SOUBOR_MOTIVU): 
            try:
                with open(SOUBOR_MOTIVU, "r", encoding="utf-8") as f: 
                    ulozeny = f.read().strip()
                    if ulozeny in MOTIVY: self.zmenit_motiv(ulozeny)
            except: pass

        self.aktualizovat_texty_gui()
        self.radar_manager = TabRadar(self, self.frame_seznam_hracu)

        # --- NOVÉ: ELEGANTNÍ ZMRAZENÍ GRAFIKY PŘI MANIPULACI (ŠTÍT) ---
        self.uzivatel_manipuluje = False
        self.timer_manipulace = None
        
        # Sledujeme změnu velikosti/pohybu okna a scrollování kolečkem
        self.root.bind("<Configure>", self._aktivuj_stit_manipulace)
        # -------------------------------------------------------------

    def _aktivuj_stit_manipulace(self, event=None):
        """Zapne štít proti překreslování, když uživatel hýbe oknem."""
        # Nejpřísnější pojistka: Reagujeme JEN když se hýbe úplně celým hlavním oknem (self.root)
        if event and event.widget != self.root:
            return

        self.uzivatel_manipuluje = True

        # Pokud už nějaký odpočet běží, zrušíme ho (uživatel stále táhne okno)
        if self.timer_manipulace:
            self.root.after_cancel(self.timer_manipulace)

        # Odjistíme štít přesně 300 milisekund POTÉ, co uživatel s oknem zastaví
        self.timer_manipulace = self.root.after(300, self._deaktivuj_stit_manipulace)

    def _deaktivuj_stit_manipulace(self):
        """Vypne štít a dožene zameškanou práci."""
        self.uzivatel_manipuluje = False
        self.timer_manipulace = None
        
        # Okno je v klidu, doženeme překreslení grafiky
        self.pozadavek_na_vykresleni_radaru()
        self.pozadavek_na_vykresleni_souboru()

    def odeslat_soubor_tcp(self, ip, cesta, offset=0, klic_agendy=""):
        self.tcp_server.odeslat_soubor_tcp(ip, cesta, offset, klic_agendy)

    def restartovat_stahovani(self, id_ukolu, klic_agendy, nazev_souboru):
        self.tcp_server.restartovat_stahovani(id_ukolu, klic_agendy, nazev_souboru)

    def _spust_dalsi_z_fronty(self, klic_agendy):
        self.tcp_server._spust_dalsi_z_fronty(klic_agendy)    

    # --- PŘIDÁNO: Profi přesouvání okna přes Windows jádro ---
    def presun_okna_windows(self, event):
        """Tato funkce se spustí jen při KLIKNUTÍ, samotný tah už řeší Windows"""
        try:
            import ctypes
            # Uvolníme zaměření myši z našeho Python programu
            ctypes.windll.user32.ReleaseCapture()
            
            # Získáme systémové ID našeho hlavního okna (HWND)
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            
            # Pošleme Windows zprávu: 0x00A1 (WM_NCLBUTTONDOWN) a 2 (HTCAPTION - titulek okna)
            ctypes.windll.user32.SendMessageW(hwnd, 0x00A1, 2, 0)
        except Exception as e:
            self.zapsat_do_logu(f"Chyba při přesunu: {e}")
    # ---------------------------------------------------------

    def vykonat_jako_spravce(self, prikazy):
        return SystemUtils.vykonat_jako_spravce(prikazy)

    def _dostat_prikazy_firewall_povolit(self):
        return SystemUtils.dostat_prikazy_firewall_povolit(UDP_PORT, TCP_PORT)

    def _dostat_prikazy_firewall_uklid(self):
        return SystemUtils.dostat_prikazy_firewall_uklid()

    def poslat_udp_zpravu(self, zprava, ip, port=UDP_PORT, broadcast=False):
        self.udp_server.poslat_udp_zpravu(zprava, ip, port, broadcast)

    def opravit_firewall(self):
        prikazy = self._dostat_prikazy_firewall_uklid() + self._dostat_prikazy_firewall_povolit()
        if self.vykonat_jako_spravce(prikazy):
            messagebox.showinfo("Hotovo", TEXTY["msg_fw_done"][self.jazyk])
        else:
            messagebox.showerror("Chyba", "Oprávnění správce bylo zrušeno, firewall nebyl nastaven.")

    def vratit_firewall(self, tichy_rezim=False):
        self.vykonat_jako_spravce(self._dostat_prikazy_firewall_uklid())
        if not tichy_rezim: messagebox.showinfo("Úklid hotov", TEXTY["msg_fw_clean_txt"][self.jazyk])                

    def pri_prepuj_zalozky(self):
        if self.notebook.get() == TEXTY["tab_files"][self.jazyk]:
            self.obnovit_sdilenou_slozku(tichy_rezim=True) 

    def dotaz_prijmout_soubor(self, ip, req_id, nazev, velikost, jeho_nick, jeho_id="UNKNOWN"):
        if self.zobrazena_zadost_o_soubor:
            self._odmitnout_soubor(ip, req_id) 
            return
            
        self.zobrazena_zadost_o_soubor = True
        velikost_mb = round(int(velikost) / (1024*1024), 2)
        
        msg = f"{jeho_nick} (z IP: {ip})\n{TEXTY['mb_receive_text'][self.jazyk]}\n📄 {nazev}\n💾 {velikost_mb} MB\n\n{TEXTY['mb_accept'][self.jazyk]}"
        titulek = f"{TEXTY['mb_receive_title'][self.jazyk]} ⚠️"
        
        if messagebox.askyesno(titulek, msg):
            ulozit_jako = filedialog.asksaveasfilename(initialfile=nazev)
            if ulozit_jako:
                # --- UPRAVENO: Použijeme rovnou předané ID, a pokud chybí, zkusíme najít v radaru ---
                if jeho_id == "UNKNOWN":
                    with self.lock_hraci:
                        if ip in self.seznam_hracu:
                            jeho_id = self.seznam_hracu[ip].get("ligo_id", "UNKNOWN")
                
                klic_agendy = jeho_id if jeho_id != "UNKNOWN" else ip
                
                cesta_part_nova = f"{ulozit_jako}_{klic_agendy.replace('.','_')}.ligopart"
                try: os.remove(cesta_part_nova)
                except: pass
                
                with self.lock_soubory:
                    if klic_agendy in self.prave_stahuji_od:
                        if klic_agendy not in self.fronta_stahovani:
                            self.fronta_stahovani[klic_agendy] = []
                        
                        id_fronty = f"queue|{klic_agendy}|{nazev}|{time.time()}"
                        self.fronta_stahovani[klic_agendy].append({"id": id_fronty, "nazev": nazev, "cesta": ulozit_jako, "typ": "private", "req_id": req_id})
                        
                        txt_fronta = TEXTY["msg_queued"][self.jazyk]
                        self.start_ukol(id_fronty, f"{txt_fronta} (Soukromý): {nazev}", is_transfer=False)
                    else:
                        self.prave_stahuji_od.add(klic_agendy)
                        self.ocekavane_soubory[klic_agendy] = ulozit_jako
                        self.ocekavane_velikosti[klic_agendy] = int(velikost)
                        self.poslat_udp_zpravu(f"__FILE_ACCEPT__:{req_id}", ip)
                        
                        # --- CHYBĚJÍCÍ HLÍDAČ (Odsekne to, pokud odesílatel selže) ---
                        def hlidac_privatni_fronty():
                            time.sleep(20.0)
                            with self.lock_soubory:
                                if klic_agendy in self.ocekavane_soubory and self.ocekavane_soubory[klic_agendy] == ulozit_jako:
                                    self.ocekavane_soubory.pop(klic_agendy)
                                    if klic_agendy in self.prave_stahuji_od: self.prave_stahuji_od.remove(klic_agendy)
                                    self.root.after(0, lambda: self._spust_dalsi_z_fronty(klic_agendy))
                        threading.Thread(target=hlidac_privatni_fronty, daemon=True).start()
                        # --------------------------------------------------------------
            else: self._odmitnout_soubor(ip, req_id)
        else: self._odmitnout_soubor(ip, req_id)
        
        self.zobrazena_zadost_o_soubor = False
        
    def _odmitnout_soubor(self, ip, req_id):
        self.poslat_udp_zpravu(f"__FILE_REJECT__:{req_id}", ip)          

    def start_naslouchani(self):
        self.udp_server.start()
        self.tcp_server.start_server()

    def otevrit_okno_chatu(self, ip, jmeno):
        if ip in self.okna_chatu and self.okna_chatu[ip].winfo_exists():
            self.okna_chatu[ip].master.deiconify() # Vytáhne okno ze stínu zpět na obrazovku
            self.okna_chatu[ip].master.focus()
            return
            
        okno = ctk.CTkToplevel(self.root)
        okno.protocol("WM_DELETE_WINDOW", okno.withdraw) # Křížek už okno neničí, jen ho schová!
        
        okno.title(f"{TEXTY['win_priv_chat'][self.jazyk]}: {jmeno} ({ip})")
        okno.geometry("500x420")
        okno.configure(fg_color="#141414")
        
        historie = tk.Listbox(okno, bg="#ffffff", fg="#000000", font=("Arial", 12), selectbackground="#e0e0e0", bd=1, relief="solid")
        historie.pack(fill="both", expand=True, padx=10, pady=10)
        
        ramecek_dole = ctk.CTkFrame(okno, fg_color="transparent")
        ramecek_dole.pack(fill="x", padx=10, pady=(0, 10))
        
        # --- TLAČÍTKO PRO SOUBOR (Vlastní ikona disketa.png) ---
        if getattr(self, 'ikona_disketa', None):
            btn_poslat_soubor = ctk.CTkButton(ramecek_dole, text="", image=self.ikona_disketa, command=lambda: self.vybrat_a_poslat_soubor(ip), fg_color="transparent", hover_color="#2980b9", width=45, height=45, corner_radius=8)
        else:
            # Záchrana, kdyby se obrázek nenašel (např. překlep v názvu souboru)
            btn_poslat_soubor = ctk.CTkButton(ramecek_dole, text="💾", command=lambda: self.vybrat_a_poslat_soubor(ip), fg_color="#3498db", hover_color="#2980b9", text_color="white", font=("Arial", 18), width=45, height=45, corner_radius=8)
            
        btn_poslat_soubor.pack(side="left", padx=(0, 10))
        
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
        self.poslat_udp_zpravu(f"__MSG__:{msg_id}:{self.ligo_id}:{muj_nick}:{zprava}", cilova_ip)
        
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
                # --- OPRAVA: Vyskakuje jen okno zavřené křížkem. Minimalizované zůstane v liště! ---
                if okno_master.state() == "withdrawn":
                    okno_master.deiconify()
                # -----------------------------------------------------------------------------
            except: pass

        self.aktualizuj_statistiky()

    def ziskat_spravne_broadcasty(self):
        return self.udp_server.ziskat_spravne_broadcasty()

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
            self.poslat_udp_zpravu(f"__MSG__:{msg_id}:{self.ligo_id}:{muj_nick}:📢 {zprava}", cilova_ip)
            
        # 2. Klasický plošný výkřik (Broadcast) pro jistotu, kdyby někdo zrovna program zapínal a nebyl na radaru
        for cilova_adresa in self.ziskat_spravne_broadcasty():
            self.poslat_udp_zpravu(f"__MSG__:{msg_id}:{self.ligo_id}:{muj_nick}:📢 {zprava}", cilova_adresa, broadcast=True)
            
        cas = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_box.insert("end", f"[{cas}] [{TEXTY['msg_broadcast_me'][self.jazyk]}]: 📢 {zprava}")
        # Bezpečný zápis barvy pro všechny verze Windows
        self.chat_box.itemconfig(self.chat_box.size() - 1, fg="#e67e22") 
        self.chat_box.yview("end")
        
        self.entry_rozhlas.delete(0, tk.END)

    def otevrit_firewall_windows(self):
        try:
            prikaz = "control /name Microsoft.WindowsFirewall /page pageConfigureApps"
            subprocess.Popen(prikaz, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e: self.zapsat_do_logu(f"[FIREWALL CMD CHYBA]: {e}")   

    def zalozit_tym(self):
        self.squad_manager.zalozit_tym()

    def otevrit_tymovou_mistnost(self, hraci_ip_seznam, jmena_hracu):
        self.squad_manager.otevrit_tymovou_mistnost(hraci_ip_seznam, jmena_hracu)

    def prepni_mikrofon(self):
        self.squad_manager.prepni_mikrofon()

    def definitivne_opustit_tym(self):
        self.squad_manager.definitivne_opustit_tym()

    def otevrit_nastaveni_mikrofonu(self):
        self.squad_manager.otevrit_nastaveni_mikrofonu()

    # --- MŮSTKY PRO SDÍLENOU SLOŽKU A SOUBORY ---
    def aktualizuj_moji_slozku_potichu(self): self.files_manager.aktualizuj_moji_slozku_potichu()
    def pozadavek_na_vykresleni_souboru(self): self.files_manager.pozadavek_na_vykresleni_souboru()
    def dokoncit_prijem_slozky(self, klic_agendy, ip, nick): self.files_manager.dokoncit_prijem_slozky(klic_agendy, ip, nick)
    def start_ukol(self, id_ukolu, text, celkem_balicku=0, is_transfer=False): self.files_manager.start_ukol(id_ukolu, text, celkem_balicku, is_transfer)
    def update_ukol(self, id_ukolu, text=None, procenta=None, mode=None, aktualni_balicek=None, celkem_balicku=None): self.files_manager.update_ukol(id_ukolu, text, procenta, mode, aktualni_balicek, celkem_balicku)
    def konec_ukol(self, id_ukolu, text_hotovo, barva="#2ecc71"): self.files_manager.konec_ukol(id_ukolu, text_hotovo, barva)
    def _smazat_ukol(self, id_ukolu): self.files_manager._smazat_ukol(id_ukolu)
    def nastav_opravdovou_pauzu(self, id_ukolu): self.files_manager.nastav_opravdovou_pauzu(id_ukolu)
    def zpracuj_hozeny_soubor_do_sdileni(self, event): self.files_manager.zpracuj_hozeny_soubor_do_sdileni(event)
    def vybrat_a_poslat_soubor(self, ip): self.files_manager.vybrat_a_poslat_soubor(ip)
    def obnovit_sdilenou_slozku(self, tichy_rezim=False): self.files_manager.obnovit_sdilenou_slozku(tichy_rezim)

    # --- MŮSTKY PRO RADAR ---
    def automaticky_pridat_do_gui(self, ip, jmeno, hra_z_procesu="", ligo_id="UNKNOWN"): self.radar_manager.automaticky_pridat_do_gui(ip, jmeno, hra_z_procesu, ligo_id)
    def pozadavek_na_vykresleni_radaru(self): self.radar_manager.pozadavek_na_vykresleni_radaru()
    def aktualizuj_tecku_a_hru(self, ip, barva, text_hry, ping_ms=""): self.radar_manager.aktualizuj_tecku_a_hru(ip, barva, text_hry, ping_ms)
    def odstranit_hrace(self, ip): self.radar_manager.odstranit_hrace(ip)

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
        zprava = f"__HEARTBEAT__:{self.ligo_id}:{muj_nick}:{moje_hra}"
        
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
        nyni = time.time()
        if hasattr(self, 'posledni_kontrola_her') and (nyni - self.posledni_kontrola_her < 15):
            return getattr(self, 'posledni_nalezena_hra', "")
        self.posledni_kontrola_her = nyni
        self.posledni_nalezena_hra = SystemUtils.zjisti_spustenou_hru(ZNAME_PROCESY)
        return self.posledni_nalezena_hra

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
                    # ZMĚNA: Program křičí do sítě jen každých 15 až 20 vteřin!
                    time.sleep(random.uniform(15.0, 20.0)) 

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
            
            if cas_ticha > 45:
                vystup = subprocess.run(["ping", "-n", "1", "-w", "500", ip], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                vystup_ok = (vystup.returncode == 0)
                if vystup_ok:
                    match = re.search(r'(?:čas|time|zeit|czas)[=<](\d+)', vystup.stdout, re.IGNORECASE)
                    if match: ping_ms = f"  [{match.group(1)} ms]"
            else:
                # Hráč před chviličkou poslal UDP balíček, stoprocentně víme, že žije a ping je výborný!
                vystup_ok = True
                ping_ms = f"  {TEXTY['status_fast_ok'][self.jazyk]}"
                
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
            ping_ms = f"  {TEXTY['status_app_off'][self.jazyk]}"
            with self.lock_hraci:
                if ip in self.seznam_hracu:
                    doba_smrti = time.time() - self.seznam_hracu[ip]["posledni_aktivita"]
                    # Když o něm neuslyšíme CELOU MINUTU (90s), teprve pak ho vymažeme z radaru
                    if doba_smrti > 90: 
                        self.root.after(0, lambda ip_ke_smazani=ip: self.odstranit_hrace(ip_ke_smazani))
                        return  
        
        self.root.after(0, self.aktualizuj_tecku_a_hru, ip, barva, text_hry, ping_ms)
        
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
        return SystemUtils.ziskat_lokalni_ip()

    def zkopirovat_moji_ip(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.moje_ip)
        messagebox.showinfo(TEXTY["msg_copy_title"][self.jazyk], TEXTY["msg_ip_copied"][self.jazyk].format(self.moje_ip))

    def ziskat_vsechny_moje_ip(self):
        return SystemUtils.ziskat_vsechny_moje_ip()

    def pridat_hrace_rucne(self):
        ip = self.novy_ip.get().strip()
        if not ip: return
        try: ipaddress.ip_address(ip)
        except ValueError: return messagebox.showerror(TEXTY["err_title"][self.jazyk], TEXTY["err_invalid_ip"][self.jazyk])
        
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
        return SystemUtils.ziskat_aktivni_adaptery()

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
                    self.chat_box.insert("end", TEXTY["msg_lan_detected"][self.jazyk])
                    self.chat_box.itemconfig("end", fg="#2ecc71")
                    self.chat_box.yview("end")
                except: pass
                
                # Vybere v roletce kabel, odemkne automatiku a odpálí ji za tebe
                self.combo_adapter.set(kabel_adapter)
                self.tlacitko_uzamceno = False
                self.root.after(500, lambda: self.automaticky_nastavit_ip_kabel(auto_z_pozadi=True))
                return

            # --- INTELIGENCE 2: UŽIVATEL VYTRHL AKTUÁLNÍ SÍŤ (Výpadek) ---
            if aktualni_vyber and aktualni_vyber not in nove_adaptery:
                self.zapsat_do_logu(f"[SÍŤ] Adaptér {aktualni_vyber} ztratil signál/byl odpojen!")
                novy_vyber = kabel_adapter or wifi_adapter or (nove_adaptery[0] if nove_adaptery else "")
                
                if novy_vyber:
                    self.combo_adapter.set(novy_vyber)
                    self.zapsat_do_logu(f"[SÍŤ] Záchrana: Přepnuto na adaptér: {novy_vyber}")
                    try:
                        self.chat_box.insert("end", TEXTY["msg_net_outage"][self.jazyk].format(novy_vyber))
                        self.chat_box.itemconfig("end", fg="#f39c12")
                        self.chat_box.yview("end")
                    except: pass
                    
                    # Odpálí automatiku pro záložní síť (např. nahodí modré tlačítko Wi-Fi)
                    self.tlacitko_uzamceno = False
                    self.root.after(500, lambda: self.automaticky_nastavit_ip_kabel(auto_z_pozadi=True))
                    
            elif aktualni_vyber in nove_adaptery:
                self.combo_adapter.set(aktualni_vyber)
            elif nove_adaptery:
                self.combo_adapter.set(kabel_adapter if kabel_adapter else nove_adaptery[0])
                self.aktualizovat_zobrazenou_ip()

    def ziskat_ip_podle_adapteru(self, nazev_adapteru):
        return SystemUtils.ziskat_ip_podle_adapteru(nazev_adapteru)

    def aktualizovat_zobrazenou_ip(self, event=None):
        adapter = self.combo_adapter.get().strip()
        if adapter:
            nova_ip = self.ziskat_ip_podle_adapteru(adapter)
            if self.moje_ip != nova_ip:
                self.moje_ip = nova_ip
                self.lbl_ip_text.configure(text=f"IP: {self.moje_ip}")
                
                self.tlacitko_uzamceno = False
                self.root.after(0, self.vrat_tlacitko_zpet)

                try: self.tcp_server.close()
                except: pass
                
                self.udp_server.zavrit_socket()
                
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
        except ValueError: return messagebox.showerror(TEXTY["err_title"][self.jazyk], TEXTY["err_invalid_ip"][self.jazyk])
        
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
            if not hasattr(self, 'upravene_adaptery'): self.upravene_adaptery = set()
            self.upravene_adaptery.add(adapter) # <--- PAMĚŤ PRO ÚKLID
            self.moje_ip = nova_ip
            self.lbl_ip_text.configure(text=f"IP: {self.moje_ip}")
            try: self.tcp_server.close()
            except: pass
            self.udp_server.zavrit_socket()
            self.root.after(500, self.start_naslouchani)
            text_uspech = TEXTY["msg_ip_success"][self.jazyk].format(nova_ip)
            self.chat_box.insert("end", text_uspech)
            self.chat_box.itemconfig("end", fg="#2ecc71")
        else:
            self.root.config(cursor="")
            messagebox.showerror(TEXTY["err_admin_title"][self.jazyk], TEXTY["msg_admin_req"][self.jazyk])

    def prepnout_zobrazeni_pokrocilych_ip(self):
        if self.pokrocile_ip_zobrazeno:
            self.frame_ip.pack_forget() 
            self.frame_pokrocile_hledani.pack_forget() 
            self.pokrocile_ip_zobrazeno = False
        else:
            # --- OPRAVA: Zkontrolujeme, jestli velký rámeček vůbec existuje na ploše ---
            if self.frame_jednoduche_ip.winfo_ismapped():
                # Pokud je velké tlačítko dole, zařadíme pokročilé sítě pod něj
                self.frame_ip.pack(fill="x", padx=10, pady=5, after=self.frame_jednoduche_ip)
            else:
                # Pokud je schované v rohu (jsme připojeni), zařadíme to rovnou pod hlavičku
                self.frame_ip.pack(fill="x", padx=10, pady=5, after=self.frame_moje_pc)
                
            self.frame_pokrocile_hledani.pack(fill="x", padx=10, after=self.frame_ip)
            self.pokrocile_ip_zobrazeno = True

    def presun_tlacitko_do_rohu(self, text, barva):
        """Po úspěšném připojení zmenší tlačítko a schová ho do rohu hlavičky."""
        self.tlacitko_v_rohu = True
        
        # OPRAVA 1: Žádné podmínky. Prostě ho skryjeme natvrdo!
        self.frame_jednoduche_ip.pack_forget()

        # 2. Nastavíme barvu a text našemu novému mini-tlačítku a ukážeme ho
        self.btn_auto_ip_mini.configure(text=text, fg_color=barva)
        self.btn_auto_ip_mini.place(relx=0.0, rely=0.0, x=10, y=10, anchor="nw")
        
        # OPRAVA 2: Vytáhneme tlačítko zespodu nahoru, aby nebylo schované pod obrázkem!
        self.btn_auto_ip_mini.lift()

    def vrat_tlacitko_zpet(self):
        """Vrátí tlačítko z rohu zpět na hlavní plochu (při výpadku sítě)."""
        self.tlacitko_v_rohu = False
        
        # 1. Schováme mini-tlačítko v rohu
        self.btn_auto_ip_mini.place_forget()

        # 2. Vrátíme zpět ten velký rámeček na hlavní plochu
        self.frame_jednoduche_ip.pack(fill="x", padx=10, pady=(0, 10), after=self.frame_moje_pc)

        puvodni_barva = getattr(self, 'aktualni_barva_motivu', "#2ecc71")
        try:
            self.btn_auto_ip.configure(
                fg_color=puvodni_barva,
                text=TEXTY["btn_auto_connect"][self.jazyk],
                font=("Arial", 16, "bold"),
                height=50
            )
        except: pass        

    def automaticky_nastavit_ip_kabel(self, auto_z_pozadi=False):
        # 1. ZÁCHRANA PROTI SPAMU S OKNEM SPRÁVCE
        if auto_z_pozadi and getattr(self, 'blokovat_auto_uac', False): return
        if not auto_z_pozadi: self.blokovat_auto_uac = False # Tlačítko to odblokuje

        if hasattr(self, 'tlacitko_uzamceno') and self.tlacitko_uzamceno: return
        self.tlacitko_uzamceno = True
        self.root.config(cursor="wait")
        
        # --- NOVÉ: Při hledání sítě vrátíme tlačítko zpět dolů, aby bylo vidět ---
        self.root.after(0, self.vrat_tlacitko_zpet)
        
        # Informujeme uživatele, že se něco děje, aby neměl pocit, že to zamrzlo
        self.root.after(0, lambda: self.btn_auto_ip.configure(text=TEXTY["msg_detecting_net"][self.jazyk]))

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
                            self.root.after(0, lambda ip=self.moje_ip: self.lbl_ip_text.configure(text=f"IP: {ip}"))
                            
                            try: self.tcp_server.close()
                            except: pass
                            self.udp_server.zavrit_socket()
                            
                            self.root.after(500, self.start_naslouchani)
                            txt_uspech = TEXTY["msg_lan_router_ok"][self.jazyk].format(aktualni_ip)
                            self.root.after(0, lambda t=txt_uspech: self.presun_tlacitko_do_rohu(t, "#27ae60"))
                            return
                        else:
                            self.root.after(0, lambda: messagebox.showerror(TEXTY["err_title"][self.jazyk], TEXTY["err_admin_denied"][self.jazyk]))
                            self.tlacitko_uzamceno = False
                            self.blokovat_auto_uac = True
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
                                    if not hasattr(self, 'upravene_adaptery'): self.upravene_adaptery = set()
                                    self.upravene_adaptery.add(kabel_adapter) # <--- PAMĚŤ PRO ÚKLID KABELU
                                    self.moje_ip = nova_ip
                                    self.root.after(0, lambda ip=self.moje_ip: self.lbl_ip_text.configure(text=f"IP: {ip}"))
                                    
                                    try: self.tcp_server.close()
                                    except: pass
                                    self.udp_server.zavrit_socket()                                    
                                    self.root.after(500, self.start_naslouchani)
                                    txt_uspech = TEXTY["msg_lan_direct_ok"][self.jazyk].format(nova_ip)
                                    self.root.after(0, lambda t=txt_uspech: self.presun_tlacitko_do_rohu(t, "#27ae60"))
                                    return
                                else:
                                    self.root.after(0, lambda: messagebox.showerror(TEXTY["err_title"][self.jazyk], TEXTY["err_admin_denied"][self.jazyk]))
                                    self.tlacitko_uzamceno = False
                                    self.blokovat_auto_uac = True # <--- ZÁMEK PROTI DALŠÍMU SPAMU!
                                    self.root.after(0, self.aktualizovat_texty_gui)
                                    return

                # Pokud kabel není fyzicky zapojený, zkusíme najít připojenou Wi-Fi
                wifi_adapter = next((a for a in zapojene_adaptery if "wi-fi" in a.lower() or "wifi" in a.lower() or "wlan" in a.lower()), None)
                
                if wifi_adapter:
                    self.root.after(0, lambda: self.combo_adapter.set(wifi_adapter))
                    self.root.after(0, self.aktualizovat_zobrazenou_ip) 
                    
                    if self.vykonat_jako_spravce(self._dostat_prikazy_firewall_povolit()):
                        def nastav_tlacitko_wifi():
                            txt_uspech = TEXTY["msg_wifi_ok"][self.jazyk].format(self.moje_ip)
                            self.presun_tlacitko_do_rohu(txt_uspech, "#2980b9")
                            self.tlacitko_uzamceno = True
                        self.root.after(1000, nastav_tlacitko_wifi)
                        return
                    else:
                        self.root.after(0, lambda: messagebox.showerror(TEXTY["err_title"][self.jazyk], TEXTY["err_admin_denied"][self.jazyk]))
                        self.tlacitko_uzamceno = False
                        self.blokovat_auto_uac = True
                        self.root.after(0, self.aktualizovat_texty_gui)
                        return

                # OPRAVA: Zde je ta chybová hláška vložená bezpečně do hlavního vlákna
                self.root.after(0, lambda: messagebox.showerror(TEXTY["err_title"][self.jazyk], TEXTY["msg_no_adapter"][self.jazyk]))
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

    def inicializuj_drag_and_drop(self):
        try:
            # Napojení na rámeček z herního manažera
            self.games_manager.frame_seznam_her.drop_target_register(DND_FILES)
            self.games_manager.frame_seznam_her.dnd_bind('<<Drop>>', self.games_manager.zpracuj_hozenou_hru)
            
            # Nastavení Drag & Drop pro obal složky (přes manažera)
            self.files_manager.frame_sdileni_obal.drop_target_register(DND_FILES)
            self.files_manager.frame_sdileni_obal.dnd_bind('<<Drop>>', self.files_manager.zpracuj_hozeny_soubor_do_sdileni)
        except Exception as e: self.zapsat_do_logu(f"[DND CHYBA] {e}")

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
        if not getattr(self, 'tlacitko_v_rohu', False):
            self.btn_auto_ip.configure(text=TEXTY["btn_auto_connect"][j])
        self.btn_pokrocile.configure(text=TEXTY["btn_adv_net"][j])
        
        # NOVÉ: Překlad pouze stavu
        self.lbl_status_text.configure(text=f" {TEXTY['lbl_connected'][j]} ")
        
        self.frame_ip.config(text=TEXTY["frame_ip"][j])
        self.lbl_sitovy_adapter.config(text=TEXTY["lbl_sitovy_adapter"][j])
        self.lbl_nova_ip.config(text=TEXTY["lbl_nova_ip"][j])
        self.lbl_maska.config(text=TEXTY["lbl_maska"][j])
        self.btn_nastavit_ip.configure(text=TEXTY["btn_nastavit_ip"][j])
        self.btn_nastavit_rucne.configure(text=TEXTY["btn_nastavit_rucne"][j])
        try: self.lbl_theme.config(text=TEXTY["lbl_theme"][j])
        except: pass

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

        if hasattr(self, 'squad_manager'): self.squad_manager.aktualizovat_texty()
        if hasattr(self, 'files_manager'): self.files_manager.aktualizovat_texty()
        if hasattr(self, 'games_manager'): self.games_manager.aktualizovat_texty()
        
        self.btn_rozhlas.configure(text=TEXTY["btn_rozhlas"][j])
        self.entry_rozhlas.configure(placeholder_text=TEXTY["ph_rozhlas"][j])
        self.btn_kopirovat_ip.configure(text=TEXTY["btn_copy_ip"][j])
        
        try:
            if "0%" not in self.lbl_progress.cget("text") and "%" not in self.lbl_progress.cget("text"):
                self.lbl_progress.config(text=TEXTY["msg_ready"][j])
        except: pass

        for ip, hr_data in self.seznam_hracu.items():
            if "btn_file" in hr_data and hr_data["btn_file"] and hr_data["btn_file"].winfo_exists():
                hr_data["btn_file"].configure(text=TEXTY["btn_file_player"][j])
            if "btn_msg" in hr_data and hr_data["btn_msg"] and hr_data["btn_msg"].winfo_exists():
                hr_data["btn_msg"].configure(text=TEXTY["btn_chat_player"][j])

        # Překlad roletky úloh za běhu
        pocet_uloh = len(self.aktivni_ulohy) if hasattr(self, 'aktivni_ulohy') else 0
        klic_uloh = "btn_tasks_hide" if hasattr(self, 'ukoly_zobrazeny') and self.ukoly_zobrazeny else "btn_tasks_show"

        self.aktualizuj_statistiky()
        self.aktualizuj_vizitku()
        self.aktualizuj_tlacitko_zvuku()
        self.inicializuj_drag_and_drop()
        
    def aktualizuj_tlacitko_zvuku(self):
        hlavni = getattr(self, 'aktualni_barva_motivu', "#2ecc71")
        if hasattr(self, 'btn_zvuk'):
            if self.zvuky_zapnuty:
                self.btn_zvuk.configure(text="🔊", fg_color="#1a1a1a", text_color=hlavni, border_color=hlavni)
            else:
                self.btn_zvuk.configure(text="🔇", fg_color="#1a1a1a", text_color="#e74c3c", border_color="#e74c3c")

    def zmenit_motiv(self, nazev_motivu):
        if nazev_motivu not in MOTIVY: return
        barvy = MOTIVY[nazev_motivu]
        hlavni = barvy["main"]
        hover = barvy["hover"]
        okraj = barvy["border"]
        
        self.aktualni_nazev_motivu = nazev_motivu
        self.aktualni_barva_motivu = hlavni

        try:
            with open(SOUBOR_MOTIVU, "w", encoding="utf-8") as f: f.write(nazev_motivu) # <--- TADY ZMĚNA
        except: pass

        try:
            self.btn_auto_ip.configure(fg_color=hlavni, hover_color=hover, border_color=okraj)
            self.btn_jazyk.configure(hover_color=hover)
            self.btn_about.configure(hover_color=hover)
            self.btn_donate.configure(hover_color=hover)
            self.btn_pridat.configure(fg_color=hlavni, hover_color=hover)
            self.btn_stahnout_soubor.configure(fg_color=hlavni, hover_color=hover, border_color=okraj)
            self.btn_najit_hrace.configure(fg_color=hlavni, hover_color=hover, border_color=okraj)
            self.notebook.configure(segmented_button_selected_color=hlavni, segmented_button_selected_hover_color=hover)            
            self.chat_box.config(selectbackground=hlavni)
            self.list_souboru.config(selectbackground=hlavni)            
            self.aktualizuj_tlacitko_zvuku()
            if hasattr(self, 'games_manager'): self.games_manager.zmenit_motiv(hlavni, hover)
            
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
        ctk.CTkLabel(okno, text="Verze 1.1 (Upgradovaná)", font=("Arial", 13), text_color="#bdc3c7").pack(pady=(0, 15))

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

        def kopirovat_email():
            self.root.clipboard_clear()
            self.root.clipboard_append(email_autora)
            btn_email.configure(text=TEXTY["btn_copied"][self.jazyk], fg_color="#2ecc71")
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
                cesta_zvuku = ziskej_cestu("icons/doom.wav")
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
        titulek = TEXTY["win_exit_title"][self.jazyk]
        dotaz = TEXTY["win_exit_text"][self.jazyk]
        
        # Místo askyesno (Ano/Ne) použijeme askokcancel (OK/Zrušit)
        if not messagebox.askokcancel(titulek, dotaz):
            return
            
        prikazy_uklid = self._dostat_prikazy_firewall_uklid()
        
        # Vrácení všech upravených adaptérů na DHCP
        if hasattr(self, 'upravene_adaptery'):
            for adapter in self.upravene_adaptery:
                prikazy_uklid.append(f'netsh interface ipv4 set address name="{adapter}" source=dhcp')
                prikazy_uklid.append(f'netsh interface ipv4 set dnsservers name="{adapter}" source=dhcp')
        
        # Pro jistotu uklidíme i ten, co svítí v roletce
        try:
            adapter_k_uklidu = self.combo_adapter.get().strip()
            if adapter_k_uklidu and (not hasattr(self, 'upravene_adaptery') or adapter_k_uklidu not in self.upravene_adaptery):
                prikazy_uklid.append(f'netsh interface ipv4 set address name="{adapter_k_uklidu}" source=dhcp')
                prikazy_uklid.append(f'netsh interface ipv4 set dnsservers name="{adapter_k_uklidu}" source=dhcp')
        except: pass
        
        # Odpálení administrátorského CMD na pozadí, které vše vyčistí
        self.vykonat_jako_spravce(prikazy_uklid)
        
        # Krátká pauza, aby měl Windows čas ty příkazy schroustat
        time.sleep(3) 
        
        # --- ODPOJENÍ GRAFIKY A SÍTĚ ---
        try: self.root.unbind_all("<MouseWheel>")
        except: pass
        try: self.root.unbind_all("<Button-4>")
        except: pass
        try: self.root.unbind_all("<Button-5>")
        except: pass
        
        try:
            if hasattr(self, 'udp_server') and self.udp_server: self.udp_server.zavrit_socket()
            if hasattr(self, 'tcp_server') and self.tcp_server: self.tcp_server.close_server()
        except: pass

        # Nešetrné, ale 100% spolehlivé zabití celého procesu (zabrání chybám při zavírání vláken)
        import os
        self.root.quit()
        os._exit(0)

    def _zjistit_hw_na_pozadi(self):
        import time
        time.sleep(15.0) 
        try:
            hw = SystemUtils.ziskej_hw_info()
            txt_cpu = f"CPU: {hw['cpu']}"
            txt_gpu = f"GPU: {hw['gpu']}"
            txt_ram = f"RAM: {hw['ram']} GB"

            self.root.after(0, lambda t=txt_cpu: self.lbl_cpu_text.configure(text=t))
            self.root.after(0, lambda t=txt_gpu: self.lbl_gpu_text.configure(text=t))
            self.root.after(0, lambda t=txt_ram: self.lbl_ram_text.configure(text=t))
        except Exception as celkova_chyba:
            self.zapsat_do_logu(f"[Kritická HW chyba vlákna]: {celkova_chyba}")
            try: 
                err_txt = "Chyba HW"
                self.root.after(0, lambda: self.lbl_cpu_text.configure(text=err_txt))
                self.root.after(0, lambda: self.lbl_gpu_text.configure(text=err_txt))
                self.root.after(0, lambda: self.lbl_ram_text.configure(text=err_txt))
            except: pass
        
class ModerniAppka(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
        self.temna_hladicka()
        self.zakazat_uspani() # NOVÉ: Voláme ochranu BMAXu
        
        # --- NASTAVENÍ IKONY OKNA ---
        try:
            cesta_k_ikone = ziskej_cestu("icons/ikona.ico")
            self.iconbitmap(cesta_k_ikone)
        except Exception:
            pass # Pokud ikona chybí, program tiše pokračuje bez ní
        # ----------------------------

    def presun_okna_windows(self, event):
        # Tato funkce se spustí jen při KLIKNUTÍ, samotný tah už řeší Windows
        try:
            import ctypes
            # Uvolníme zaměření myši z našeho Python programu
            ctypes.windll.user32.ReleaseCapture()
            
            # Získáme systémové ID našeho okna (HWND)
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            
            # Pošleme Windows zprávu: 0x00A1 (WM_NCLBUTTONDOWN) a 2 (HTCAPTION - titulek okna)
            ctypes.windll.user32.SendMessageW(hwnd, 0x00A1, 2, 0)
        except Exception as e:
            print(f"Chyba při přesunu: {e}")    

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
            
            # --- NOVÉ: Vynucení zakulacených rohů hlavního okna (Funguje na Windows 11) ---
            # 33 = DWMWA_WINDOW_CORNER_PREFERENCE, 2 = DWMWCP_ROUND
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(ctypes.c_int(2)), 4)
        except: pass
