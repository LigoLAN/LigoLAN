import tkinter as tk
import customtkinter as ctk
import time
from config import *

class TabRadar:
    def __init__(self, app, rodic_frame):
        self.app = app
        self.frame_seznam_hracu = rodic_frame
        
        self.staticky_radar = {}
        self.prekresluji_radar = False
        self.timer_radar = None
        
        # Fronty pro plynulé připojování a odpojování (multitasking)
        self.fronta_pripojovani = []
        self.pripojovani_bezi = False
        self.fronta_odpojovani = []
        self.odpojovani_bezi = False

        # Tichý zabiják mrtvých slotů se spustí sám za 10 vteřin
        self.app.root.after(10000, self.spustit_uklizece_radaru)

    def automaticky_pridat_do_gui(self, ip, jmeno, hra_z_procesu="", ligo_id="UNKNOWN"):
        je_znamy = False
        with self.app.lock_hraci:
            if ip in self.app.seznam_hracu:
                je_znamy = True

        if je_znamy:
            zmena_k_prekresleni = False
            with self.app.lock_hraci:
                self.app.seznam_hracu[ip]["ligo_id"] = ligo_id
                if self.app.seznam_hracu[ip]["jmeno"] != jmeno:
                    self.app.seznam_hracu[ip]["jmeno"] = jmeno
                    if ip in self.app.okna_chatu and self.app.okna_chatu[ip].winfo_exists():
                        self.app.okna_chatu[ip].master.title(f"{TEXTY['win_priv_chat'][self.app.jazyk]}: {jmeno} ({ip})")
                    zmena_k_prekresleni = True
                if self.app.seznam_hracu[ip].get("hra_z_procesu", "") != hra_z_procesu:
                    self.app.seznam_hracu[ip]["hra_z_procesu"] = hra_z_procesu
                    zmena_k_prekresleni = True
            
            if zmena_k_prekresleni:
                self.pozadavek_na_vykresleni_radaru()
        else:
            ceka_uz = any(item['ip'] == ip for item in self.fronta_pripojovani)
            if not ceka_uz:
                self.fronta_pripojovani.append({
                    'ip': ip, 'jmeno': jmeno, 'hra_z_procesu': hra_z_procesu, 'ligo_id': ligo_id
                })
                
            if not self.pripojovani_bezi:
                self.pripojovani_bezi = True
                self.app.root.after(150, self._postupne_pridavat_z_fronty)

    def _postupne_pridavat_z_fronty(self):
        if not hasattr(self, 'fronta_pripojovani') or not self.fronta_pripojovani:
            self.pripojovani_bezi = False
            return
            
        pocet_k_zpracovani = min(5, len(self.fronta_pripojovani))
        nutne_prekreslit = False 
        
        for _ in range(pocet_k_zpracovani):
            novy_hrac = self.fronta_pripojovani.pop(0)
            ip = novy_hrac['ip']
            
            with self.app.lock_hraci:
                if ip not in self.app.seznam_hracu:
                    prazdny_klic = None
                    for k, v in self.app.seznam_hracu.items():
                        if v.get("je_prazdny") and v.get("zobrazena_hra", "") == novy_hrac['hra_z_procesu']:
                            prazdny_klic = k
                            break
                    if not prazdny_klic:
                        for k, v in self.app.seznam_hracu.items():
                            if v.get("je_prazdny"):
                                prazdny_klic = k
                                break
                            
                    if prazdny_klic:
                        hrac = self.app.seznam_hracu.pop(prazdny_klic)
                        if hrac.get("zobrazena_hra", "") != novy_hrac['hra_z_procesu']:
                            nutne_prekreslit = True
                            
                        hrac["jmeno"] = novy_hrac['jmeno']
                        hrac["ligo_id"] = novy_hrac['ligo_id']
                        hrac["hra_z_procesu"] = novy_hrac['hra_z_procesu']
                        hrac["posledni_aktivita"] = time.time()
                        hrac["zobrazena_hra"] = novy_hrac['hra_z_procesu'] 
                        hrac["je_prazdny"] = False
                        
                        try:
                            if hrac.get("label") and hrac["label"].winfo_exists():
                                hrac["label"].configure(text=f"{hrac['jmeno']} ({ip}) - Připojuje se...", text_color="white")
                            hlavni_barva = getattr(self.app, 'aktualni_barva_motivu', "#2ecc71")
                            if hrac.get("canvas") and hrac["canvas"].winfo_exists():
                                hrac["canvas"].itemconfig(hrac["dot"], fill=hlavni_barva)
                            if hrac.get("btn_msg") and hrac["btn_msg"].winfo_exists():
                                hrac["btn_msg"].configure(state="normal", fg_color="#2a2a2a", text_color="#bdc3c7")
                        except: pass
                        
                        self.app.seznam_hracu[ip] = hrac
                    else:
                        nutne_prekreslit = True 
                        self.app.seznam_hracu[ip] = {
                            "jmeno": novy_hrac['jmeno'], "ligo_id": novy_hrac['ligo_id'], 
                            "hra_z_procesu": novy_hrac['hra_z_procesu'], "posledni_aktivita": time.time(), 
                            "zobrazena_hra": novy_hrac['hra_z_procesu'], "odeslano": 0, "prijato": 0,
                            "je_prazdny": False, "canvas": None, "dot": None, "label": None, "chk_tym": None, "btn_msg": None
                        }
        
        if nutne_prekreslit:
            self.pozadavek_na_vykresleni_radaru()
            
        self.app.root.after(200, self._postupne_pridavat_z_fronty)

    def aktualizuj_tecku_a_hru(self, ip, barva, text_hry, ping_ms=""):
        with self.app.lock_hraci:
            if ip in self.app.seznam_hracu:
                self.app.seznam_hracu[ip]["zobrazena_hra"] = text_hry
                self.app.seznam_hracu[ip]["posledni_ping_text"] = ping_ms
                self.app.seznam_hracu[ip]["aktualni_barva"] = barva
                
        self.pozadavek_na_vykresleni_radaru()

    def pozadavek_na_vykresleni_radaru(self):
        if self.timer_radar: return
        self.timer_radar = self.app.root.after(250, self._spust_vykresleni_a_vycisti_timer)

    def _spust_vykresleni_a_vycisti_timer(self):
        self.timer_radar = None  
        self.vykresli_radar()    

    def ziskej_nebo_vytvor_kategorii(self, nazev_hry):
        if nazev_hry not in self.staticky_radar:
            kat_frame = ctk.CTkFrame(self.frame_seznam_hracu, fg_color="transparent")
            kat_frame.pack(fill="x", pady=(5, 0))

            hdr_frame = ctk.CTkFrame(kat_frame, fg_color="#2b2b2b", corner_radius=6)
            hdr_frame.pack(fill="x", padx=2)
            
            lbl_nadpis = ctk.CTkLabel(hdr_frame, text=f"▶  {nazev_hry}", font=("Arial", 13, "bold"), text_color="#ecf0f1", cursor="hand2")
            lbl_nadpis.pack(side="left", padx=10, pady=6)

            sloty_frame = ctk.CTkFrame(kat_frame, fg_color="transparent")

            self.staticky_radar[nazev_hry] = {
                "kat_frame": kat_frame, "lbl_nadpis": lbl_nadpis, "sloty_frame": sloty_frame,
                "rozbaleno": False, "sloty": [] 
            }
            
            hdr_frame.bind("<Button-1>", lambda e, n=nazev_hry: self.prepnout_zobrazeni_kategorie(e, n))
            lbl_nadpis.bind("<Button-1>", lambda e, n=nazev_hry: self.prepnout_zobrazeni_kategorie(e, n))

            for _ in range(5):
                self.pridat_jeden_prazdny_slot(nazev_hry, sloty_frame)

        return self.staticky_radar[nazev_hry]

    def prepnout_zobrazeni_kategorie(self, event, nazev_hry):
        kat_data = self.staticky_radar[nazev_hry]
        kat_data["rozbaleno"] = not kat_data.get("rozbaleno", True)
        
        if kat_data["rozbaleno"]: kat_data["sloty_frame"].pack(fill="x")
        else: kat_data["sloty_frame"].pack_forget()
            
        self.pozadavek_na_vykresleni_radaru()

    def pridat_jeden_prazdny_slot(self, nazev_hry, rodic_frame):
        row = ctk.CTkFrame(rodic_frame, fg_color="#1e1e1e", corner_radius=6)
        row.pack(fill="x", pady=2, padx=(20, 2))

        chk_tym = ctk.CTkCheckBox(row, text="", width=24, checkbox_width=24, checkbox_height=24, fg_color="#3498db", hover_color="#2980b9")
        chk_tym.pack(side="left", padx=(10, 5), pady=4)

        btn_msg = ctk.CTkButton(row, text="Chat", fg_color="#141414", text_color="#333333", state="disabled", font=("Arial", 12, "bold"), width=70, height=28, corner_radius=6)
        btn_msg.pack(side="left", padx=(0, 10), pady=4)

        canvas = tk.Canvas(row, width=20, height=20, bg="#1e1e1e", highlightthickness=0)
        dot = canvas.create_oval(5, 5, 15, 15, fill="#2a2a2a") 
        canvas.pack(side="left", padx=(0, 5), pady=4)

        lbl_jmeno = ctk.CTkLabel(row, text="", anchor="w", text_color="white", font=("Arial", 12))
        lbl_jmeno.pack(side="left", fill="x", expand=True)

        self.staticky_radar[nazev_hry]["sloty"].append({
            "frame": row, "chk": chk_tym, "btn": btn_msg, "canvas": canvas, "dot": dot, "lbl": lbl_jmeno
        })    

    def vykresli_radar(self):
        if getattr(self.app, 'uzivatel_manipuluje', False): return
        if getattr(self, 'prekresluji_radar', False): return
        self.prekresluji_radar = True

        txt_lobby = TEXTY["lbl_lobby"][self.app.jazyk]
        hraci_podle_her = {txt_lobby: []}

        with self.app.lock_hraci:
            for ip, hrac in self.app.seznam_hracu.items():
                hra = hrac.get("zobrazena_hra", "").replace("🎮 ", "").strip()
                if not hra: hraci_podle_her[txt_lobby].append((ip, hrac))
                else:
                    nazev_hry = f"🎮 {hra}"
                    if nazev_hry not in hraci_podle_her: hraci_podle_her[nazev_hry] = []
                    hraci_podle_her[nazev_hry].append((ip, hrac))

        hlavni_barva = getattr(self.app, 'aktualni_barva_motivu', "#2ecc71")

        for nazev_hry, seznam_lidi in hraci_podle_her.items():
            kat_data = self.ziskej_nebo_vytvor_kategorii(nazev_hry)

            if not kat_data["kat_frame"].winfo_manager():
                kat_data["kat_frame"].pack(fill="x", pady=(5, 0))

            text_hracu = TEXTY["lbl_players_count"][self.app.jazyk] if len(seznam_lidi) != 1 else TEXTY["lbl_player_single"][self.app.jazyk]
            symbol = "▼" if kat_data.get("rozbaleno", True) else "▶"
            kat_data["lbl_nadpis"].configure(text=f"{symbol}  {nazev_hry} ({len(seznam_lidi)} {text_hracu})")

            sloty = kat_data["sloty"]

            if kat_data.get("rozbaleno", True): cilovy_pocet_slotu = max(5, len(seznam_lidi))
            else: cilovy_pocet_slotu = 0 

            while len(sloty) < cilovy_pocet_slotu:
                self.pridat_jeden_prazdny_slot(nazev_hry, kat_data["sloty_frame"])
                
            while len(sloty) > cilovy_pocet_slotu:
                zbytecny_slot = sloty.pop() 
                if zbytecny_slot["frame"].winfo_exists(): zbytecny_slot["frame"].destroy() 

            if kat_data.get("rozbaleno", True):
                for i in range(len(sloty)):
                    slot = sloty[i]
                    if i < len(seznam_lidi):
                        ip, hrac = seznam_lidi[i]
                        hrac["chk_tym"] = slot["chk"]
                        
                        jmeno = hrac.get("jmeno", "Neznámý")
                        moje_sit = ".".join(self.app.moje_ip.split(".")[:3])
                        jeho_sit = ".".join(ip.split(".")[:3])
                        typ_site = "🔌" if moje_sit == jeho_sit else "📶"

                        ping_ms = hrac.get("posledni_ping_text", "")
                        barva = hrac.get("aktualni_barva", hlavni_barva)

                        text_vizitky = f"{jmeno} ({ip}) {typ_site} {ping_ms}"
                        if ip in getattr(self.app, 'aktivni_stahovaci', set()):
                            text_vizitky += f"   |   💾 {TEXTY['msg_radar_down'][self.app.jazyk]}"

                        if slot["lbl"].cget("text") != text_vizitky:
                            slot["lbl"].configure(text=text_vizitky)
                            slot["canvas"].itemconfig(slot["dot"], fill=barva)
                            slot["btn"].configure(state="normal", fg_color="#2a2a2a", text_color="#bdc3c7", command=lambda cil=ip, n=jmeno: self.app.otevrit_okno_chatu(cil, n))
                    else:
                        if slot["lbl"].cget("text") != "": 
                            slot["lbl"].configure(text="")
                            slot["canvas"].itemconfig(slot["dot"], fill="#2a2a2a")
                            slot["btn"].configure(state="disabled", fg_color="#141414", text_color="#333333")
                            slot["chk"].deselect()
            else:
                for ip, hrac in seznam_lidi:
                    hrac["chk_tym"] = None

        if hasattr(self, 'staticky_radar'):
            klice_ke_smazani = []
            for nazev_hry, kat_data in self.staticky_radar.items():
                if nazev_hry not in hraci_podle_her: klice_ke_smazani.append(nazev_hry)
            for klic in klice_ke_smazani:
                kat_data = self.staticky_radar.pop(klic) 
                if kat_data["kat_frame"].winfo_exists(): kat_data["kat_frame"].destroy() 

        self.prekresluji_radar = False    

    def odstranit_hrace(self, ip):
        if not hasattr(self, 'fronta_odpojovani'):
            self.fronta_odpojovani = []
            self.odpojovani_bezi = False
            
        if ip not in self.fronta_odpojovani:
            self.fronta_odpojovani.append(ip)
            
        if not self.odpojovani_bezi:
            self.odpojovani_bezi = True
            self.app.root.after(250, self._postupne_mazat_z_fronty)

    def _postupne_mazat_z_fronty(self):
        if not hasattr(self, 'fronta_odpojovani') or not self.fronta_odpojovani:
            self.odpojovani_bezi = False
            return
            
        ip = self.fronta_odpojovani.pop(0)
        
        with self.app.lock_hraci:
            if ip in self.app.seznam_hracu:
                del self.app.seznam_hracu[ip] 
                try:
                    self.app.root.after(0, lambda i=ip: self.app.chat_box.insert("end", f"{TEXTY['msg_player_removed'][self.app.jazyk]} {i}"))
                    self.app.chat_box.yview("end")
                except: pass
            
        with self.app.lock_soubory:
            if hasattr(self.app, 'soubory_hracu') and ip in self.app.soubory_hracu:
                del self.app.soubory_hracu[ip]
            if hasattr(self.app, 'mapa_sdilenych_souboru'):
                klice_ke_smazani = [k for k, v in self.app.mapa_sdilenych_souboru.items() if v['ip'] == ip]
                for k in klice_ke_smazani: del self.app.mapa_sdilenych_souboru[k]
            if hasattr(self.app, 'pool_sdileni') and ip in self.app.pool_sdileni:
                try:
                    kat_data = self.app.pool_sdileni.pop(ip)
                    if kat_data["kat_frame"].winfo_exists(): kat_data["kat_frame"].destroy()
                except: pass

        self.app.pozadavek_na_vykresleni_souboru()
        self.pozadavek_na_vykresleni_radaru()
        self.app.root.after(50, self._postupne_mazat_z_fronty)    

    def spustit_uklizece_radaru(self):
        nyni = time.time()
        smazano_neco = False
        
        with self.app.lock_hraci:
            klice_k_smazani = []
            for ip, hrac in self.app.seznam_hracu.items():
                if hrac.get("je_prazdny") and (nyni - hrac.get("posledni_aktivita", 0)) > 180:
                    klice_k_smazani.append(ip)
                    
            for klic in klice_k_smazani:
                hrac = self.app.seznam_hracu.pop(klic)
                if hrac.get("frame") and hrac["frame"].winfo_exists():
                    hrac["frame"].destroy()
                smazano_neco = True
                
        if smazano_neco:
            self.pozadavek_na_vykresleni_radaru()
            
        self.app.root.after(10000, self.spustit_uklizece_radaru)
