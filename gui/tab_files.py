import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import os
import time
import threading
from PIL import Image
from config import *
from core.file_manager import FileManager
import tempfile
import datetime

class TabFiles:
    def __init__(self, app, parent_tab):
        self.app = app
        self.parent_tab = parent_tab
        
        self.rozbaleni_hraci = set()
        self.cekajici_vykresleni = None
        self.vybrany_soubor_data = None
        self.vybrany_ramecek = None
        self.ukoly_zobrazeny = False
        
        # Ochrana paměti
        if not hasattr(self.app, 'soubory_hracu'): self.app.soubory_hracu = {}
        if not hasattr(self.app, 'mapa_sdilenych_souboru'): self.app.mapa_sdilenych_souboru = {}
        if not hasattr(self.app, 'aktivni_ulohy'): self.app.aktivni_ulohy = {}
        if not hasattr(self.app, 'pool_sdileni'): self.app.pool_sdileni = {}

        # --- ROLETA ÚLOH ---
        self.frame_aktivity = ctk.CTkScrollableFrame(self.parent_tab, height=120, fg_color="#0d0d0d", corner_radius=8, border_width=1, border_color="#333333")

        # --- HLAVNÍ OBAL SDÍLENÍ ---
        self.frame_sdileni_obal = ctk.CTkFrame(self.parent_tab, fg_color="#2b2b2b", corner_radius=10, border_width=1, border_color="#333333")
        self.frame_sdileni_obal.pack(fill="both", expand=True, padx=10, pady=10)

        # --- SPODNÍ TLAČÍTKA ---
        self.spodni_lista_sdileni = ctk.CTkFrame(self.frame_sdileni_obal, fg_color="transparent")
        self.spodni_lista_sdileni.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        self.spodni_lista_sdileni.columnconfigure((0, 1, 2), weight=1, uniform="a")

        self.btn_stahnout_soubor = ctk.CTkButton(self.spodni_lista_sdileni, text=TEXTY["btn_stahnout_soubor"][self.app.jazyk], command=self.stahnout_vybrany_soubor, fg_color="#2ecc71", hover_color="#27ae60", border_color="#1d8348", border_width=3, text_color="white", font=("Arial", 13, "bold"), height=40, corner_radius=8)
        self.btn_stahnout_soubor.grid(row=0, column=0, sticky="ew", padx=5)

        self.btn_ukoly_toggle = ctk.CTkButton(self.spodni_lista_sdileni, text=f"{TEXTY['btn_tasks_show'][self.app.jazyk]} (0)", command=self.toggle_ukoly, fg_color="#7f8c8d", hover_color="#616a6b", border_color="#515a5a", border_width=3, text_color="white", font=("Arial", 13, "bold"), height=40, corner_radius=8)
        self.btn_ukoly_toggle.grid(row=0, column=1, sticky="ew", padx=5)

        self.btn_otevrit_slozku = ctk.CTkButton(self.spodni_lista_sdileni, text=TEXTY["btn_otevrit_slozku"][self.app.jazyk], command=self.otevrit_lokalni_slozku, fg_color="#3498db", hover_color="#2980b9", border_color="#21618c", border_width=3, text_color="white", font=("Arial", 13, "bold"), height=40, corner_radius=8)
        self.btn_otevrit_slozku.grid(row=0, column=2, sticky="ew", padx=5)

        self.frame_list_souboru = ctk.CTkScrollableFrame(self.frame_sdileni_obal, fg_color="#e8e8e8", corner_radius=8)
        self.frame_list_souboru.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Nastartujeme kontrolu místních souborů
        self.app.root.after(1000, self.automaticke_nacitani_souboru)

    def otevrit_lokalni_slozku(self):
        try: os.startfile(SDILENA_SLOZKA)
        except Exception as e: messagebox.showerror(TEXTY["err_title"][self.app.jazyk], f"{TEXTY['err_folder_open'][self.app.jazyk]}: {e}")

    def aktualizuj_moji_slozku_potichu(self):
        with self.app.lock_soubory:
            moje_soubory_list = []
            try:
                for s in os.listdir(SDILENA_SLOZKA):
                    try:
                        velikost_mb = round(os.path.getsize(os.path.join(SDILENA_SLOZKA, s)) / (1024*1024), 2)
                        velikost_text = f"{velikost_mb} MB"
                    except:
                        velikost_text = "Neznámá"
                    moje_soubory_list.append({"nazev": s, "velikost": velikost_text})
            except: pass
            self.app.soubory_hracu["TY"] = {"nick": "TY", "soubory": moje_soubory_list}
            
        self.pozadavek_na_vykresleni_souboru()    

    def obnovit_sdilenou_slozku(self, tichy_rezim=False):
        puvodni_vyber = self.vybrany_soubor_data[0] if self.vybrany_soubor_data else None
        self.vybrany_soubor_data = None
        self.vybrany_ramecek = None
            
        with self.app.lock_soubory:
            klice_ke_smazani = [k for k, v in self.app.mapa_sdilenych_souboru.items() if v['ip'] == "127.0.0.1"]
            for k in klice_ke_smazani: del self.app.mapa_sdilenych_souboru[k]
            
            moje_soubory_list = []
            try:
                for s in os.listdir(SDILENA_SLOZKA):
                    try:
                        velikost_mb = round(os.path.getsize(os.path.join(SDILENA_SLOZKA, s)) / (1024*1024), 2)
                        velikost_text = f"{velikost_mb} MB"
                    except:
                        velikost_text = "Neznámá"
                        
                    moje_soubory_list.append({"nazev": s, "velikost": velikost_text})
                    polozka_klic = f"[TY] {s}"
                    self.app.mapa_sdilenych_souboru[polozka_klic] = {"ip": "127.0.0.1", "soubor": s}
            except: pass
            
            self.app.soubory_hracu["TY"] = {"nick": "TY", "soubory": moje_soubory_list}
            muj_nick = getattr(self.app, 'muj_aktualni_nick', 'Neznámý')
            
            with self.app.lock_hraci:
                ip_seznam = list(self.app.seznam_hracu.keys())
                stare_ipy = list(self.app.soubory_hracu.keys())
                for stara_ip in stare_ipy:
                    if stara_ip != "TY" and stara_ip not in ip_seznam:
                        del self.app.soubory_hracu[stara_ip] 
                        klice_ke_smazani = [k for k, v in self.app.mapa_sdilenych_souboru.items() if v['ip'] == stara_ip]
                        for k in klice_ke_smazani: del self.app.mapa_sdilenych_souboru[k]

                for ip in ip_seznam:
                    nick_hrace = self.app.seznam_hracu[ip].get("jmeno", "Hráč")
                    if ip not in self.app.soubory_hracu:
                        self.app.soubory_hracu[ip] = {"nick": nick_hrace, "soubory": []}
                    else:
                        self.app.soubory_hracu[ip]["nick"] = nick_hrace

        self.pozadavek_na_vykresleni_souboru()

        for ip in ip_seznam:
            self.app.poslat_udp_zpravu(f"__DIR_REQ__:{self.app.ligo_id}:{muj_nick}", ip)
            
        if not tichy_rezim:
            self.app.chat_box.insert("end", TEXTY["msg_dir_req"][self.app.jazyk])

    def vyzadat_aktualizaci_slozky(self, id_skupiny):
        if id_skupiny == "TY":
            self.obnovit_sdilenou_slozku(tichy_rezim=True)
        else:
            muj_nick = self.app.entry_nick.get().strip() or "Neznámý"
            with self.app.lock_soubory:
                if hasattr(self.app, 'buffer_dir_res') and id_skupiny in self.app.buffer_dir_res:
                    del self.app.buffer_dir_res[id_skupiny]
            self.app.poslat_udp_zpravu(f"__DIR_REQ__:{self.app.ligo_id}:{muj_nick}", id_skupiny)
            
        self.app.root.config(cursor="wait")
        self.app.root.after(500, lambda: self.app.root.config(cursor=""))        

    def pozadavek_na_vykresleni_souboru(self):
        if hasattr(self, 'cekajici_vykresleni') and self.cekajici_vykresleni: return
        self.cekajici_vykresleni = self.app.root.after(300, self._spust_vykresleni_souboru_a_vycisti)

    def _spust_vykresleni_souboru_a_vycisti(self):
        self.cekajici_vykresleni = None
        self.vykresli_seznam_souboru()

    def dokoncit_prijem_slozky(self, klic_agendy, ip, nick):
        with self.app.lock_soubory:
            if not hasattr(self.app, 'buffer_dir_res') or klic_agendy not in self.app.buffer_dir_res: return
            nove_soubory = self.app.buffer_dir_res.pop(klic_agendy, [])
            
            klice_ke_smazani = [k for k, v in self.app.mapa_sdilenych_souboru.items() if v['ip'] == ip]
            for k in klice_ke_smazani: del self.app.mapa_sdilenych_souboru[k]
                
            for s_data in nove_soubory:
                polozka_klic = f"[{nick}] {s_data['nazev']}"
                self.app.mapa_sdilenych_souboru[polozka_klic] = {"ip": ip, "soubor": s_data['nazev']}
                
            self.app.soubory_hracu[ip] = {"nick": nick, "soubory": nove_soubory}
        self.pozadavek_na_vykresleni_souboru()     

    def prepni_rozbaleni(self, ip):
        if ip in self.rozbaleni_hraci: self.rozbaleni_hraci.remove(ip)
        else: self.rozbaleni_hraci.add(ip)
        self.pozadavek_na_vykresleni_souboru()

    def ziskej_nebo_vytvor_kategorii_sdileni(self, ip_skupiny):
        if ip_skupiny not in self.app.pool_sdileni:
            kat_frame = ctk.CTkFrame(self.frame_list_souboru, fg_color="transparent")
            hdr_frame = ctk.CTkFrame(kat_frame, fg_color="#bdbdbd", corner_radius=6, cursor="hand2")
            hdr_frame.pack(fill="x", pady=(5, 5), padx=4)
            
            lbl = ctk.CTkLabel(hdr_frame, text="", font=("Arial", 14, "bold"), text_color="#1a1a1a")
            lbl.pack(side="left", padx=10, pady=6)
            
            if getattr(self.app, 'ikona_aktualizovat', None):
                btn_akt = ctk.CTkButton(hdr_frame, text="", image=self.app.ikona_aktualizovat, width=32, height=32, fg_color="transparent", hover_color="#95a5a6", corner_radius=6)
            else:
                btn_akt = ctk.CTkButton(hdr_frame, text="🔄", width=32, height=32, fg_color="transparent", hover_color="#95a5a6", text_color="#1a1a1a", font=("Arial", 16), corner_radius=6)
            btn_akt.pack(side="right", padx=10)
            
            sloty_frame = ctk.CTkFrame(kat_frame, fg_color="transparent")
            
            btn_akt.configure(command=lambda i=ip_skupiny: self.vyzadat_aktualizaci_slozky(i))
            hdr_frame.bind("<Button-1>", lambda e, i=ip_skupiny: self.prepni_rozbaleni(i))
            lbl.bind("<Button-1>", lambda e, i=ip_skupiny: self.prepni_rozbaleni(i))
            
            self.app.pool_sdileni[ip_skupiny] = {
                "kat_frame": kat_frame, "hdr_frame": hdr_frame, "lbl": lbl, 
                "btn_akt": btn_akt, "sloty_frame": sloty_frame, "radky": [], "aktivni": True
            }
        return self.app.pool_sdileni[ip_skupiny]

    def _vytvor_sdileni_radek(self, rodic_frame):
        row = ctk.CTkFrame(rodic_frame, fg_color="#ffffff", corner_radius=6, border_width=1, border_color="#d0d0d0", cursor="hand2")
        
        lbl_nazev = ctk.CTkLabel(row, text="", font=("Arial", 12, "bold"), text_color="#2980b9", anchor="w", width=350)
        lbl_nazev.pack(side="left", padx=(10, 0), pady=2)
        
        lbl_majitel = ctk.CTkLabel(row, text="", font=("Arial", 11), text_color="#7f8c8d", anchor="center", width=150)
        lbl_majitel.pack(side="left", pady=2)
        
        lbl_velikost = ctk.CTkLabel(row, text="", font=("Arial", 11), text_color="#7f8c8d", anchor="center", width=120)
        lbl_velikost.pack(side="left", pady=2)
        
        r_data = {
            "frame": row, "lbl_nazev": lbl_nazev, "lbl_majitel": lbl_majitel, "lbl_velikost": lbl_velikost,
            "meta_nazev": "", "meta_majitel": ""
        }
        
        def on_click(event):
            n = r_data["meta_nazev"]
            m = r_data["meta_majitel"]
            if n and m: self.oznacit_soubor(row, n, m)
                
        row.bind("<Button-1>", on_click)
        lbl_nazev.bind("<Button-1>", on_click)
        lbl_majitel.bind("<Button-1>", on_click)
        lbl_velikost.bind("<Button-1>", on_click)
        
        return r_data
    
    def vykresli_seznam_souboru(self):
        if getattr(self.app, 'uzivatel_manipuluje', False): return

        with self.app.lock_soubory:
            kopie_hracu = dict(self.app.soubory_hracu)

        if hasattr(self.app, 'pool_sdileni'):
            for ip, kat_data in self.app.pool_sdileni.items(): kat_data["aktivni"] = False

        try: scroll_y = self.frame_list_souboru._parent_canvas.yview()[0]
        except: scroll_y = 0

        for ip, data in kopie_hracu.items():
            if not data.get("soubory"): continue
            
            zobrazeny_nazev = TEXTY["lbl_my_folder"][self.app.jazyk] if ip == "TY" else data["nick"]
            is_expanded = ip in self.rozbaleni_hraci
            soubory = data["soubory"]
            
            kat_data = self.ziskej_nebo_vytvor_kategorii_sdileni(ip)
            kat_data["aktivni"] = True
            
            if not kat_data["kat_frame"].winfo_manager(): kat_data["kat_frame"].pack(fill="x", pady=(0, 0))
                
            sipka = "▼" if is_expanded else "▶"
            lbl_text = f"{sipka}  {zobrazeny_nazev} ({len(soubory)} {TEXTY['lbl_files_count'][self.app.jazyk]})"
            
            if not hasattr(self.app, "img_tech_folder"):
                try: self.app.img_tech_folder = ctk.CTkImage(light_image=None, dark_image=Image.open(ziskej_cestu("icons/tech_folder.png")), size=(28, 28))
                except: self.app.img_tech_folder = None

            if self.app.img_tech_folder:
                if kat_data["lbl"].cget("text") != lbl_text:
                    kat_data["lbl"].configure(text=lbl_text, image=self.app.img_tech_folder, compound="left")
            else:
                cely_text = f"{'📂' if is_expanded else '📁'} {lbl_text}"
                if kat_data["lbl"].cget("text") != cely_text:
                    kat_data["lbl"].configure(text=cely_text)
                    
            if is_expanded:
                if not kat_data["sloty_frame"].winfo_manager(): kat_data["sloty_frame"].pack(fill="x")
                    
                while len(kat_data["radky"]) < len(soubory):
                    kat_data["radky"].append(self._vytvor_sdileni_radek(kat_data["sloty_frame"]))

                while len(kat_data["radky"]) > len(soubory):
                    zbytecny_radek = kat_data["radky"].pop()
                    if zbytecny_radek["frame"].winfo_exists(): zbytecny_radek["frame"].destroy() 
                    
                for j, r_data in enumerate(kat_data["radky"]):
                    if j < len(soubory):
                        s_data = soubory[j]
                        nazev = s_data["nazev"]
                        majitel = "TY" if ip == "TY" else zobrazeny_nazev
                        
                        if not r_data["frame"].winfo_manager(): r_data["frame"].pack(fill="x", pady=2, padx=(30, 2))
                            
                        r_data["meta_nazev"] = nazev
                        r_data["meta_majitel"] = majitel
                        
                        if r_data["lbl_nazev"].cget("text") != nazev: r_data["lbl_nazev"].configure(text=nazev)
                        if r_data["lbl_majitel"].cget("text") != majitel: r_data["lbl_majitel"].configure(text=majitel)
                        if r_data["lbl_velikost"].cget("text") != s_data["velikost"]: r_data["lbl_velikost"].configure(text=s_data["velikost"])
                            
                        if self.vybrany_soubor_data and self.vybrany_soubor_data[0] == nazev and self.vybrany_soubor_data[1] == majitel:
                            if r_data["frame"].cget("fg_color") != getattr(self.app, 'aktualni_barva_motivu', "#2ecc71"):
                                self.oznacit_soubor(r_data["frame"], nazev, majitel)
                        else:
                            if r_data["frame"].cget("fg_color") != "#ffffff":
                                r_data["frame"].configure(fg_color="#ffffff")
                                r_data["lbl_nazev"].configure(text_color="#2980b9")
                                r_data["lbl_majitel"].configure(text_color="#7f8c8d")
                                r_data["lbl_velikost"].configure(text_color="#7f8c8d")
                    else:
                        if r_data["frame"].winfo_manager(): r_data["frame"].pack_forget() 
            else:
                if kat_data["sloty_frame"].winfo_manager(): kat_data["sloty_frame"].pack_forget() 
                    
                while len(kat_data["radky"]) > 0:
                    zbytecny_radek = kat_data["radky"].pop()
                    if zbytecny_radek["frame"].winfo_exists(): zbytecny_radek["frame"].destroy() 
                    
        if hasattr(self.app, 'pool_sdileni'):
            for ip, kat_data in self.app.pool_sdileni.items():
                if not kat_data.get("aktivni", False) and kat_data["kat_frame"].winfo_manager():
                    kat_data["kat_frame"].pack_forget()

        try: self.frame_list_souboru._parent_canvas.yview_moveto(scroll_y)
        except: pass

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
        except: docasna_pamet = []
            
        if not hasattr(self.app, 'cached_soubory') or self.app.cached_soubory != docasna_pamet:
            self.app.cached_soubory = docasna_pamet
            try:
                if not self.vybrany_soubor_data: self.obnovit_sdilenou_slozku(tichy_rezim=True)
            except: pass
        
        self.app.root.after(60000, self.automaticke_nacitani_souboru)

    def oznacit_soubor(self, ramecek, nazev, majitel):
        if self.vybrany_ramecek and self.vybrany_ramecek.winfo_exists():
            self.vybrany_ramecek.configure(fg_color="#ffffff")
            for child in self.vybrany_ramecek.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    if child.cget("text") == nazev: child.configure(text_color="#2980b9")
                    else: child.configure(text_color="#7f8c8d")

        barva_vyberu = getattr(self.app, 'aktualni_barva_motivu', "#2ecc71")
        ramecek.configure(fg_color=barva_vyberu)
        for child in ramecek.winfo_children():
            if isinstance(child, ctk.CTkLabel): child.configure(text_color="white")

        self.vybrany_soubor_data = (nazev, majitel)
        self.vybrany_ramecek = ramecek       

    def stahnout_vybrany_soubor(self):
        if not self.vybrany_soubor_data:
            messagebox.showwarning(TEXTY["title_warning"][self.app.jazyk], TEXTY["msg_select_file_first"][self.app.jazyk])
            return
            
        nazev_souboru = self.vybrany_soubor_data[0]
        majitel = self.vybrany_soubor_data[1]
        
        if majitel == "TY":
            messagebox.showinfo(TEXTY["title_info"][self.app.jazyk], TEXTY["msg_already_have_file"][self.app.jazyk])
            return
            
        polozka_klic = f"[{majitel}] {nazev_souboru}"
            
        with self.app.lock_soubory:
            data = self.app.mapa_sdilenych_souboru.get(polozka_klic)
            
        if data:
            ip_majitele = data["ip"]
            nazev_souboru = os.path.basename(data["soubor"].replace("\\", "/"))
            cilova_cesta = os.path.join(SDILENA_SLOZKA, nazev_souboru)
            
            jeho_id = "UNKNOWN"
            with self.app.lock_hraci:
                if ip_majitele not in self.app.seznam_hracu:
                    for hip, hdata in self.app.seznam_hracu.items():
                        if hdata.get("jmeno") == majitel:
                            ip_majitele = hip
                            break
                if ip_majitele in self.app.seznam_hracu: 
                    jeho_id = self.app.seznam_hracu[ip_majitele].get("ligo_id", "UNKNOWN")
            
            klic_agendy = jeho_id if jeho_id != "UNKNOWN" else ip_majitele
            
            with self.app.lock_soubory:
                if klic_agendy in self.app.prave_stahuji_od:
                    if klic_agendy not in self.app.fronta_stahovani: self.app.fronta_stahovani[klic_agendy] = []
                    id_fronty = f"queue|{klic_agendy}|{nazev_souboru}|{time.time()}"
                    self.app.fronta_stahovani[klic_agendy].append({"id": id_fronty, "nazev": nazev_souboru, "cesta": cilova_cesta, "typ": "shared"})
                    
                    txt_fronta = TEXTY["msg_queued"][self.app.jazyk]
                    self.app.root.after(0, lambda idf=id_fronty, n=nazev_souboru, txt=txt_fronta: self.start_ukol(idf, f"{txt}: {n}", is_transfer=False))
                    return
                else:
                    self.app.prave_stahuji_od.add(klic_agendy)
                
                self.app.ocekavane_soubory[klic_agendy] = cilova_cesta
                self.app.ocekavane_velikosti[klic_agendy] = 0
                
            cesta_part = f"{cilova_cesta}_{klic_agendy.replace('.','_')}.ligopart"
            offset = os.path.getsize(cesta_part) if os.path.exists(cesta_part) else 0
            
            self.app.poslat_udp_zpravu(f"__DIR_GET__:{nazev_souboru}:{offset}", ip_majitele)
            messagebox.showinfo(TEXTY["msg_down_start_title"][self.app.jazyk], TEXTY["msg_down_start_text"][self.app.jazyk].format(nazev_souboru))

            def hlidac_startu():
                time.sleep(20.0)
                with self.app.lock_soubory:
                    if klic_agendy in self.app.ocekavane_soubory and self.app.ocekavane_soubory[klic_agendy] == cilova_cesta:
                        self.app.ocekavane_soubory.pop(klic_agendy)
                        if klic_agendy in self.app.prave_stahuji_od: self.app.prave_stahuji_od.remove(klic_agendy)
                        self.app.root.after(0, lambda: self.app._spust_dalsi_z_fronty(klic_agendy))
            threading.Thread(target=hlidac_startu, daemon=True).start()

    def vybrat_a_poslat_soubor(self, cilova_ip):
        volba = messagebox.askquestion(TEXTY["mb_send_folder_title"][self.app.jazyk], TEXTY["mb_send_folder_text"][self.app.jazyk])
        if volba == 'yes':
            cesta = filedialog.askdirectory(title="Vyber složku k odeslání")
            if not cesta: return
            
            id_zip = f"zip_{time.time()}"
            jmeno_slozky = os.path.basename(cesta) or "Slozka"
            txt_balim = TEXTY["prog_packing"][self.app.jazyk]
            self.start_ukol(id_zip, f"{txt_balim} {jmeno_slozky}... 📦", is_transfer=False)
            
            docasna_slozka = tempfile.gettempdir() 
            konecny_zip = os.path.join(docasna_slozka, f"{jmeno_slozky}_sdileni.zip")
            
            def check_zruseno():
                if hasattr(self.app, 'zrusene_prenosy') and id_zip in self.app.zrusene_prenosy:
                    self.app.root.after(0, self.konec_ukol, id_zip, "❌ Zrušeno" if self.app.jazyk == "CZ" else "❌ Canceled", "#e74c3c")
                    return True
                return False

            def on_progress(procenta):
                txt = TEXTY["prog_packing_short"][self.app.jazyk]
                self.app.root.after(0, self.update_ukol, id_zip, f"{txt}: {jmeno_slozky} ({procenta}%)", procenta, "determinate")

            def on_hotovo(vysledny_zip):
                self.app.root.after(0, self.konec_ukol, id_zip, f"✅ Zabaleno: {jmeno_slozky}")
                self.app.root.after(0, lambda: self._dokoncit_pripravu_odeslani(cilova_ip, vysledny_zip))

            def on_chyba(chyba_msg):
                self.app.zapsat_do_logu(f"Chyba balení: {chyba_msg}")
                self.app.root.after(0, self.konec_ukol, id_zip, TEXTY["task_err_pack"][self.app.jazyk], "#e74c3c")

            FileManager.zabalit_slozku_async(cesta, konecny_zip, check_zruseno, on_progress, on_hotovo, on_chyba)
        else:
            cesta = filedialog.askopenfilename(title="Vyber soubor")
            if not cesta: return
            self._dokoncit_pripravu_odeslani(cilova_ip, cesta)

    def _dokoncit_pripravu_odeslani(self, cilova_ip, cesta):
        try: velikost = os.path.getsize(cesta)
        except Exception as e:
            self.app.zapsat_do_logu(f"Nelze přečíst soubor: {e}")
            return
            
        nazev = os.path.basename(cesta)
        req_id = str(int(datetime.datetime.now().timestamp() * 1000))
        
        with self.app.lock_soubory: self.app.sdileni_ceka_na_prijemci[req_id] = cesta
            
        muj_nick = self.app.entry_nick.get().strip() or "Neznámý"
        self.app.poslat_udp_zpravu(f"__FILE_REQ__:{req_id}:{self.app.ligo_id}:{nazev}:{velikost}:{muj_nick}", cilova_ip)
        self.app.chat_box.insert("end", f"{TEXTY['msg_send_req'][self.app.jazyk]} {cilova_ip}.")
        self.app.notebook.set(TEXTY["tab_chat"][self.app.jazyk]) 

    def zpracuj_hozeny_soubor_do_sdileni(self, event):
        cesta = event.data.strip('{}')
        if not os.path.exists(cesta): return

        nazev_polozky = os.path.basename(cesta) or "Slozka"

        if os.path.isdir(cesta):
            id_zip = f"dnd_zip_{time.time()}"
            txt_copy = TEXTY["prog_copying"][self.app.jazyk]
            self.start_ukol(id_zip, f"{txt_copy} {nazev_polozky}... 📦", is_transfer=False)
            konecny_zip = os.path.join(SDILENA_SLOZKA, f"{nazev_polozky}_sdileni.zip")
            
            def check_zruseno():
                if hasattr(self.app, 'zrusene_prenosy') and id_zip in self.app.zrusene_prenosy:
                    self.app.root.after(0, self.konec_ukol, id_zip, TEXTY["task_canceled"][self.app.jazyk], "#e74c3c")
                    return True
                return False

            def on_progress(procenta):
                self.app.root.after(0, self.update_ukol, id_zip, f"Balím: {nazev_polozky} ({procenta}%)", procenta, "determinate")

            def on_hotovo(vysledny_zip):
                self.app.root.after(0, self.konec_ukol, id_zip, f"{TEXTY['task_done'][self.app.jazyk]}: {nazev_polozky}")
                self.app.root.after(0, self.aktualizuj_moji_slozku_potichu)

            def on_chyba(chyba_msg):
                self.app.zapsat_do_logu(f"Chyba DND balení: {chyba_msg}")
                self.app.root.after(0, self.konec_ukol, id_zip, "❌ Chyba balení", "#e74c3c")

            FileManager.zabalit_slozku_async(cesta, konecny_zip, check_zruseno, on_progress, on_hotovo, on_chyba)
        else:
            cilova_cesta = os.path.join(SDILENA_SLOZKA, nazev_polozky)
            id_kopirovani = f"dnd_copy_{time.time()}"
            txt_kopiruji = TEXTY["prog_copying_short"][self.app.jazyk]
            self.start_ukol(id_kopirovani, f"{txt_kopiruji}: {nazev_polozky}... ⏳", is_transfer=False)

            def on_hotovo(vysledna_cesta):
                self.app.root.after(0, self.aktualizuj_moji_slozku_potichu)
                self.app.root.after(0, self.konec_ukol, id_kopirovani, f"✅ Hotovo: {nazev_polozky}")

            def on_chyba(chyba_msg):
                self.app.root.after(0, self.konec_ukol, id_kopirovani, TEXTY["task_err_copy"][self.app.jazyk], "#e74c3c")
                self.app.root.after(0, lambda: messagebox.showerror(TEXTY["err_title"][self.app.jazyk], TEXTY["msg_copy_fail"][self.app.jazyk].format(chyba_msg)))

            FileManager.kopirovat_soubor_async(cesta, cilova_cesta, on_hotovo, on_chyba)

    # --- ROLETA ÚLOH A MULTITASKING ---
    def toggle_ukoly(self):
        pocet = len(self.app.aktivni_ulohy)
        if self.ukoly_zobrazeny:
            self.frame_aktivity.pack_forget() 
            self.btn_ukoly_toggle.configure(text=f"{TEXTY['btn_tasks_show'][self.app.jazyk]} ({pocet})")
            self.ukoly_zobrazeny = False
        else:
            self.frame_aktivity.pack(before=self.frame_sdileni_obal, fill="x", padx=10, pady=(0, 5))
            self.btn_ukoly_toggle.configure(text=f"{TEXTY['btn_tasks_hide'][self.app.jazyk]} ({pocet})")
            self.ukoly_zobrazeny = True
            
    def start_ukol(self, id_ukolu, text, celkem_balicku=0, is_transfer=False):
        row = ctk.CTkFrame(self.frame_aktivity, fg_color="#1e1e1e", height=35, corner_radius=4)
        row.pack(fill="x", pady=2)
        
        lbl = tk.Label(row, text=text, bg="#1e1e1e", fg="#f39c12", font=("Arial", 10, "bold"))
        lbl.pack(side="left", padx=10)
        
        lbl_balicky = None
        btn_pauza = None
        
        txt_zrusit = TEXTY["btn_cancel_task"][self.app.jazyk]
        btn_zrusit = ctk.CTkButton(row, text=txt_zrusit, width=70, height=24, fg_color="#c0392b", hover_color="#922b21", font=("Arial", 11, "bold"))
        btn_zrusit.pack(side="right", padx=(5, 10))
        btn_zrusit.configure(command=lambda id=id_ukolu: self.zrusit_prenos(id))
        
        if is_transfer:
            lbl_balicky = tk.Label(row, text=f"(0 / {celkem_balicku})", bg="#1e1e1e", fg="#bdc3c7", font=("Arial", 9, "bold"))
            lbl_balicky.pack(side="left", padx=5)
            txt_pauza = TEXTY["btn_pause_task"][self.app.jazyk]
            btn_pauza = ctk.CTkButton(row, text=txt_pauza, width=70, height=24, fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 11, "bold"))
            btn_pauza.pack(side="right", padx=(5, 0))
            btn_pauza.configure(command=lambda id=id_ukolu: self.opravdova_pauza_klik(id))
            
        pb = ttk.Progressbar(row, orient="horizontal", mode="determinate" if is_transfer else "indeterminate")
        pb.pack(side="right", fill="x", expand=True, padx=(10, 5) if is_transfer else 10)
        if not is_transfer: pb.start(15) 
        
        self.app.aktivni_ulohy[id_ukolu] = {
            "row": row, "lbl": lbl, "pb": pb, 
            "lbl_balicky": lbl_balicky, "btn_pauza": btn_pauza, "btn_zrusit": btn_zrusit,
            "stav": "bezi" 
        }
        
        pocet = len(self.app.aktivni_ulohy)
        klic = "btn_tasks_hide" if self.ukoly_zobrazeny else "btn_tasks_show"
        try: self.btn_ukoly_toggle.configure(text=f"{TEXTY[klic][self.app.jazyk]} ({pocet})")
        except: pass

    def update_ukol(self, id_ukolu, text=None, procenta=None, mode=None, aktualni_balicek=None, celkem_balicku=None):
        if id_ukolu in self.app.aktivni_ulohy:
            prvek = self.app.aktivni_ulohy[id_ukolu]
            if text: prvek["lbl"].config(text=text)
            if procenta is not None: prvek["pb"].config(value=procenta)
            if mode: prvek["pb"].config(mode=mode)
            if mode == "indeterminate": prvek["pb"].step(5)
            if aktualni_balicek is not None and celkem_balicku is not None and prvek["lbl_balicky"]:
                prvek["lbl_balicky"].config(text=f"({aktualni_balicek} / {celkem_balicku})")

    def konec_ukol(self, id_ukolu, text_hotovo, barva="#2ecc71"):
        if id_ukolu in self.app.aktivni_ulohy:
            prvek = self.app.aktivni_ulohy[id_ukolu]
            prvek["lbl"].config(text=text_hotovo, fg=barva)
            prvek["pb"].config(value=100, mode="determinate")
            
            if prvek.get("btn_pauza"): prvek["btn_pauza"].pack_forget()
            if prvek.get("btn_zrusit"): prvek["btn_zrusit"].pack_forget()
            if prvek.get("lbl_balicky"): prvek["lbl_balicky"].pack_forget()
            
            self.app.root.after(5000, lambda: self._smazat_ukol(id_ukolu))

    def _smazat_ukol(self, id_ukolu):
        if id_ukolu in self.app.aktivni_ulohy:
            try: self.app.aktivni_ulohy[id_ukolu]["row"].destroy()
            except: pass
            del self.app.aktivni_ulohy[id_ukolu]
            
        self.app.root.update_idletasks()
        
        pocet = len(self.app.aktivni_ulohy)
        klic = "btn_tasks_hide" if self.ukoly_zobrazeny else "btn_tasks_show"
        try: self.btn_ukoly_toggle.configure(text=f"{TEXTY[klic][self.app.jazyk]} ({pocet})")
        except: pass
        if pocet == 0 and self.ukoly_zobrazeny: self.toggle_ukoly()

    def nastav_opravdovou_pauzu(self, id_ukolu):
        if id_ukolu in self.app.aktivni_ulohy:
            btn = self.app.aktivni_ulohy[id_ukolu].get("btn_pauza")
            if btn: btn.configure(command=lambda id=id_ukolu: self.opravdova_pauza_klik(id))

    def opravdova_pauza_klik(self, id_ukolu):
        if not hasattr(self.app, 'pauznute_prenosy'): self.app.pauznute_prenosy = set()
        if id_ukolu.startswith("send|"): nazev_souboru = id_ukolu.split("|")[2] if len(id_ukolu.split("|")) > 2 else ""
        else: nazev_souboru = id_ukolu.split("|")[1] if len(id_ukolu.split("|")) > 1 else ""
        
        if id_ukolu in self.app.aktivni_ulohy:
            uloha = self.app.aktivni_ulohy[id_ukolu]
            if uloha["stav"] == "bezi":
                uloha["stav"] = "pauza"
                self.app.pauznute_prenosy.add(id_ukolu) 
                uloha["btn_pauza"].configure(text=TEXTY["btn_resume_task"][self.app.jazyk], fg_color="#e74c3c", hover_color="#c0392b")
                uloha["lbl"].config(fg="#e74c3c") 
                for b in self.app.ziskat_spravne_broadcasty(): self.app.poslat_udp_zpravu(f"__REMOTE_CTRL__:PAUSE:{nazev_souboru}", b, broadcast=True)
            else:
                uloha["stav"] = "bezi"
                if id_ukolu in self.app.pauznute_prenosy: self.app.pauznute_prenosy.remove(id_ukolu) 
                uloha["btn_pauza"].configure(text=TEXTY["btn_pause_task"][self.app.jazyk], fg_color="#2ecc71", hover_color="#27ae60")
                uloha["lbl"].config(fg="#f39c12")
                for b in self.app.ziskat_spravne_broadcasty(): self.app.poslat_udp_zpravu(f"__REMOTE_CTRL__:RESUME:{nazev_souboru}", b, broadcast=True)

    def zrusit_prenos(self, id_ukolu):
        if id_ukolu.startswith("queue|"):
            casti = id_ukolu.split("|")
            klic_fronty = casti[1] if len(casti) > 1 else "" 
            with self.app.lock_soubory:
                if klic_fronty in self.app.fronta_stahovani:
                    self.app.fronta_stahovani[klic_fronty] = [x for x in self.app.fronta_stahovani[klic_fronty] if x["id"] != id_ukolu]
            self._smazat_ukol(id_ukolu)
            return

        if not hasattr(self.app, 'zrusene_prenosy'): self.app.zrusene_prenosy = set()
        self.app.zrusene_prenosy.add(id_ukolu)
        
        if id_ukolu.startswith("send|"): nazev_souboru = id_ukolu.split("|")[2] if len(id_ukolu.split("|")) > 2 else ""
        else: nazev_souboru = id_ukolu.split("|")[1] if len(id_ukolu.split("|")) > 1 else ""
            
        for b in self.app.ziskat_spravne_broadcasty(): self.app.poslat_udp_zpravu(f"__REMOTE_CTRL__:CANCEL:{nazev_souboru}", b, broadcast=True)
        
        if hasattr(self.app, 'pauznute_prenosy') and id_ukolu in self.app.pauznute_prenosy:
            self.app.pauznute_prenosy.remove(id_ukolu)
            
        if id_ukolu in self.app.aktivni_ulohy:
            uloha = self.app.aktivni_ulohy[id_ukolu]
            txt = TEXTY["task_canceling"][self.app.jazyk]
            uloha["lbl"].config(text=txt, fg="#e74c3c")
            if uloha.get("btn_pauza"): uloha["btn_pauza"].configure(state="disabled")
            if uloha.get("btn_zrusit"): uloha["btn_zrusit"].configure(state="disabled")

    def aktualizovat_texty(self):
        j = self.app.jazyk
        self.btn_otevrit_slozku.configure(text=TEXTY["btn_otevrit_slozku"][j])
        self.btn_stahnout_soubor.configure(text=TEXTY["btn_stahnout_soubor"][j])
        pocet_uloh = len(self.app.aktivni_ulohy) if hasattr(self.app, 'aktivni_ulohy') else 0
        klic_uloh = "btn_tasks_hide" if self.ukoly_zobrazeny else "btn_tasks_show"
        try: self.btn_ukoly_toggle.configure(text=f"{TEXTY[klic_uloh][j]} ({pocet_uloh})")
        except: pass
