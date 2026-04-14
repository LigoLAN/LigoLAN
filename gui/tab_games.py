import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import os
import time
import threading
import subprocess
import ctypes
import datetime
from PIL import Image

from config import *
from core.system_utils import SystemUtils

class TabGames:
    def __init__(self, app, parent_tab):
        self.app = app
        self.parent_tab = parent_tab
        self.moje_hry = {}
        
        # --- HORNÍ LIŠTA KARTY HER ---
        self.horni_lista_hry = ctk.CTkFrame(self.parent_tab, fg_color="transparent")
        self.horni_lista_hry.pack(fill="x", pady=5)
        
        self.btn_pridat_hru = ctk.CTkButton(self.horni_lista_hry, text=TEXTY["btn_add_game"][self.app.jazyk], command=self.pridat_hru, width=200, fg_color="#1e8449", hover_color="#145a32", font=("Arial", 13, "bold"), height=45, corner_radius=8)
        self.btn_pridat_hru.pack(side="left", padx=5)
        
        # Moderní kontejner pro karty her
        self.frame_seznam_her = ctk.CTkScrollableFrame(self.parent_tab, fg_color="transparent")
        self.frame_seznam_her.pack(fill="both", expand=True, padx=5, pady=5)

        self.nacti_hry()

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

    def ziskej_ikonu_z_exe(self, cesta_exe, nazev_hry):
        slozka_ikon = ziskej_appdata_cestu("Ikony_Her")
        return SystemUtils.ziskej_ikonu_z_exe(cesta_exe, nazev_hry, slozka_ikon)    

    def zmenit_parametry_hry(self, nazev=None):
        if not nazev or nazev not in self.moje_hry: 
            return
            
        aktualni_param = self.moje_hry[nazev].get("parametry", "")
        
        pamet_modu = {"-window", "-console"}
        for h_data in self.moje_hry.values():
            p = h_data.get("parametry", "").strip()
            if p and len(p) < 500: pamet_modu.add(p)
            
        if os.path.exists(SOUBOR_PARAMETRY):
            try:
                with open(SOUBOR_PARAMETRY, "r", encoding="utf-8") as f:
                    for line in f:
                        l = line.strip()
                        if l and len(l) < 500: pamet_modu.add(l)
            except: pass
            
        seznam_pro_combo = sorted([m for m in pamet_modu if m])
            
        okno = ctk.CTkToplevel(self.app.root)
        okno.title(TEXTY["win_mods_title"][self.app.jazyk])
        okno.geometry("520x220")
        okno.configure(fg_color="#141414")
        okno.attributes('-topmost', 'true') 
        okno.transient(self.app.root)
        okno.grab_set()
        
        ctk.CTkLabel(okno, text=f"{TEXTY['lbl_edit_mods'][self.app.jazyk]} {nazev}", font=("Arial", 16, "bold"), text_color="#3498db").pack(pady=(20,5))
        
        r_kombi = ctk.CTkFrame(okno, fg_color="transparent")
        r_kombi.pack(pady=10)
        
        combo_params = ctk.CTkComboBox(r_kombi, values=seznam_pro_combo, font=("Arial", 14), width=360, height=45, corner_radius=8)
        combo_params.set(aktualni_param)
        combo_params.pack(side="left", padx=(0, 5))
        
        def smazat_z_historie():
            m = combo_params.get().strip()
            if m and m in pamet_modu:
                pamet_modu.remove(m)
                combo_params.configure(values=sorted(list(pamet_modu)))
                combo_params.set("")
                try:
                    with open(SOUBOR_PARAMETRY, "w", encoding="utf-8") as f:
                        for item in pamet_modu:
                            if item not in ["", "-window", "-console"]: f.write(item + "\n")
                except: pass
            else:
                combo_params.set("")

        if getattr(self.app, 'ikona_popelnice', None):
            btn_smazat = ctk.CTkButton(r_kombi, text="", image=self.app.ikona_popelnice, command=smazat_z_historie, fg_color="transparent", hover_color="#c0392b", width=45, height=45, corner_radius=8)
        else:
            btn_smazat = ctk.CTkButton(r_kombi, text="❌", command=smazat_z_historie, fg_color="#c0392b", hover_color="#922b21", width=45, height=45, corner_radius=8)
        btn_smazat.pack(side="left")

        def ulozit():
            novy_param = combo_params.get().strip()
            self.moje_hry[nazev]["parametry"] = novy_param
            self.uloz_hry()
            self.vykresli_seznam_her()
            if novy_param and novy_param not in pamet_modu and len(novy_param) < 300:
                try:
                    with open(SOUBOR_PARAMETRY, "a", encoding="utf-8") as f: f.write(novy_param + "\n")
                except: pass
            okno.destroy()
            
        ctk.CTkButton(okno, text=TEXTY["btn_save_mods"][self.app.jazyk], command=ulozit, fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 14, "bold"), width=250, height=45, corner_radius=8).pack(pady=(20, 20))

    def vykresli_seznam_her(self):
        for widget in self.frame_seznam_her.winfo_children():
            widget.destroy()

        if not hasattr(self, 'ikony_v_pameti'):
            self.ikony_v_pameti = []
        self.ikony_v_pameti.clear()

        for nazev, data in self.moje_hry.items():
            param = data.get("parametry", "").strip()
            port = data.get("port", "Neznámý")
            
            row = ctk.CTkFrame(self.frame_seznam_her, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#333333")
            row.pack(fill="x", pady=4, padx=5)

            icon_frame = ctk.CTkFrame(row, width=50, height=50, corner_radius=8, fg_color="transparent")
            icon_frame.pack(side="left", padx=10, pady=10)
            icon_frame.pack_propagate(False)
            
            cesta_k_ikone = self.ziskej_ikonu_z_exe(data["cesta"], nazev)
            
            ikona_vykreslena = False
            if cesta_k_ikone:
                try:
                    with Image.open(cesta_k_ikone) as img_pil:
                        img_rgba = img_pil.convert("RGBA").copy()
                        
                    img_ctk = ctk.CTkImage(light_image=img_rgba, dark_image=img_rgba, size=(50, 50))
                    self.ikony_v_pameti.append(img_ctk)
                    
                    lbl_img = ctk.CTkLabel(icon_frame, text="", image=img_ctk)
                    lbl_img.place(relx=0.5, rely=0.5, anchor="center")
                    lbl_img.image = img_ctk 
                    ikona_vykreslena = True
                except Exception as e:
                    self.app.zapsat_do_logu(f"[KRESLENÍ IKONY CHYBA] {e}")
            
            if not ikona_vykreslena:
                icon_frame.configure(fg_color="#2c3e50")
                ctk.CTkLabel(icon_frame, text="🎮", font=("Arial", 26)).place(relx=0.5, rely=0.5, anchor="center")

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

            ctk.CTkLabel(info_frame, text=nazev, font=("Arial", 16, "bold"), text_color="white", anchor="w").pack(fill="x")
            
            detaily = f"Port: {port}"
            if param:
                ukazka = (param[:40] + "..") if len(param) > 40 else param
                detaily += f"   |   Mód: {ukazka}"
            ctk.CTkLabel(info_frame, text=detaily, font=("Arial", 12), text_color="#bdc3c7", anchor="w").pack(fill="x")

            txt_start = "▶ START" if self.app.jazyk == "CZ" else "▶ START"
            btn_start = ctk.CTkButton(row, text=txt_start, width=110, height=35, fg_color="#3498db", hover_color="#2980b9", font=("Arial", 12, "bold"), command=lambda n=nazev: self.spustit_hru(n))
            btn_start.pack(side="left", padx=5)

            txt_mod = "⚙️ Mod" if self.app.jazyk == "CZ" else "⚙️ Mod"
            btn_mod = ctk.CTkButton(row, text=txt_mod, width=80, height=35, fg_color="#2a2a2a", hover_color="#4d4d4d", border_width=1, border_color="#555", command=lambda n=nazev: self.zmenit_parametry_hry(n))
            btn_mod.pack(side="left", padx=5)

            if getattr(self.app, 'ikona_popelnice', None):
                btn_del = ctk.CTkButton(row, text="", image=self.app.ikona_popelnice, width=40, height=40, fg_color="transparent", hover_color="#c0392b", corner_radius=8, command=lambda n=nazev: self.odebrat_hru(n))
            else:
                btn_del = ctk.CTkButton(row, text="❌", width=40, height=35, fg_color="#2a2a2a", hover_color="#c0392b", command=lambda n=nazev: self.odebrat_hru(n))
                
            btn_del.pack(side="left", padx=(5, 10))

    def pridat_hru(self):
        cesta = filedialog.askopenfilename(title="Vyber spouštěcí soubor hry (.exe)", filetypes=[("Spustitelné soubory", "*.exe")])
        if not cesta: return
        self.otevrit_okno_pridani_hry(cesta)

    def otevrit_okno_pridani_hry(self, cesta_k_exe):
        vychozi_nazev = os.path.basename(cesta_k_exe).replace(".exe", "")
        
        okno = ctk.CTkToplevel(self.app.root)
        okno.title(TEXTY["win_add_game"][self.app.jazyk])
        okno.geometry("480x420")
        okno.resizable(False, False)
        okno.transient(self.app.root) 
        okno.grab_set() 

        ctk.CTkLabel(okno, text=TEXTY["lbl_game_name"][self.app.jazyk], font=("Arial", 14, "bold"), text_color="white").pack(pady=(20, 5))
        entry_nazev = ctk.CTkEntry(okno, font=("Arial", 14), width=380, justify="center", height=40, corner_radius=8)
        entry_nazev.insert(0, vychozi_nazev)
        entry_nazev.pack()
        
        ctk.CTkLabel(okno, text=TEXTY["lbl_game_port"][self.app.jazyk], text_color="#f39c12", font=("Arial", 14, "bold")).pack(pady=(15, 5))
        hodnoty_portu = [TEXTY["lbl_auto_port"][self.app.jazyk]] + [f"{port} ({nazev})" for port, nazev in ZNAME_HRY.items()]
        combo_port = ctk.CTkComboBox(okno, values=hodnoty_portu, font=("Arial", 14), width=380, height=40, corner_radius=8, button_color="#f39c12", button_hover_color="#d68910")
        combo_port.pack()

        lbl_params_txt = TEXTY["lbl_launch_params"][self.app.jazyk]
        ctk.CTkLabel(okno, text=lbl_params_txt, text_color="#bdc3c7", font=("Arial", 13, "bold")).pack(pady=(15, 5))
        
        pamet_modu = {"-window", "-console"} 
        for h_data in self.moje_hry.values():
            p = h_data.get("parametry", "").strip()
            if p and len(p) < 300: pamet_modu.add(p)
        if os.path.exists(SOUBOR_PARAMETRY):
            try:
                with open(SOUBOR_PARAMETRY, "r", encoding="utf-8") as f:
                    for line in f:
                        l = line.strip()
                        if l and len(l) < 300: pamet_modu.add(l)
            except: pass
            
        seznam_pro_combo = sorted([m for m in pamet_modu if m])
        
        entry_params = ctk.CTkComboBox(okno, values=seznam_pro_combo, font=("Arial", 14), width=380, height=40, corner_radius=8)
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
            
            if zadane_parametry and zadane_parametry not in pamet_modu and len(zadane_parametry) < 300:
                try:
                    with open(SOUBOR_PARAMETRY, "a", encoding="utf-8") as f: f.write(zadane_parametry + "\n")
                except: pass
                
            okno.destroy()

        ramecek_tlacitek = ctk.CTkFrame(okno, fg_color="transparent")
        ramecek_tlacitek.pack(pady=30)
        ctk.CTkButton(ramecek_tlacitek, text=TEXTY["btn_save"][self.app.jazyk], command=potvrdit, fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=("Arial", 14, "bold"), width=150, height=45, corner_radius=8).pack(side="left", padx=15)
        ctk.CTkButton(ramecek_tlacitek, text=TEXTY["btn_cancel"][self.app.jazyk], command=okno.destroy, fg_color="#e74c3c", hover_color="#c0392b", text_color="white", font=("Arial", 14, "bold"), width=150, height=45, corner_radius=8).pack(side="right", padx=15)

    def aktualizuj_nazev_hry_v_seznamu(self, puvodni_nazev, novy_port):
        if puvodni_nazev in self.moje_hry:
            self.moje_hry[puvodni_nazev]["port"] = novy_port
            self.uloz_hry()
            self.vykresli_seznam_her()

    def odebrat_hru(self, nazev=None):
        if nazev in self.moje_hry:
            try:
                slozka_ikon = ziskej_appdata_cestu("Ikony_Her")
                bezpecny_nazev = "".join([c for c in nazev if c.isalnum() or c in " _-"]).strip()
                if bezpecny_nazev:
                    cesta_k_png = os.path.join(slozka_ikon, f"{bezpecny_nazev}.png")
                    if os.path.exists(cesta_k_png):
                        os.remove(cesta_k_png)
            except: pass

            del self.moje_hry[nazev]
            self.uloz_hry()
            self.vykresli_seznam_her()

    def spustit_hru(self, nazev=None):
        if not nazev or nazev not in self.moje_hry: 
            return
        
        data = self.moje_hry.get(nazev)
        
        if data and os.path.exists(data["cesta"]):
            try:
                prikazy = [
                    'netsh advfirewall firewall delete rule name="LAN Party Hra"',
                    'netsh advfirewall firewall delete rule name="LAN Party Hra EXE"'
                ]
                prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra EXE" dir=in action=allow program="{data["cesta"]}" enable=yes profile=any')
                prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra EXE" dir=out action=allow program="{data["cesta"]}" enable=yes profile=any')
                
                port = data.get("port", "")
                if port and port.replace("-", "").isdigit():
                    prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra" dir=in action=allow protocol=TCP localport={port}')
                    prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra" dir=in action=allow protocol=UDP localport={port}')
                    prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra" dir=out action=allow protocol=TCP remoteport={port}')
                    prikazy.append(f'netsh advfirewall firewall add rule name="LAN Party Hra" dir=out action=allow protocol=UDP remoteport={port}')
                
                self.app.vykonat_jako_spravce(prikazy)

                pracovni_slozka = os.path.dirname(data["cesta"])
                parametry_hry = data.get("parametry", "")
                ctypes.windll.shell32.ShellExecuteW(None, "open", data["cesta"], parametry_hry if parametry_hry else None, pracovni_slozka, 1)

                muj_nick = self.app.entry_nick.get().strip() or "Neznámý"
                exe_name = os.path.basename(data["cesta"])
                
                if port.startswith("AUTO"):
                    self.app.chat_box.insert("end", TEXTY["msg_game_track"][self.app.jazyk].format(nazev))
                    self.app.chat_box.itemconfig("end", fg="#f39c12")
                    self.app.notebook.set(TEXTY["tab_chat"][self.app.jazyk]) 

                    def stopar_portu():
                        nalezeny_port = None
                        for _ in range(15):
                            time.sleep(2)
                            nalezeny_port = SystemUtils.najdi_port_procesu(exe_name)
                            if nalezeny_port: break

                        if nalezeny_port:
                            self.app.root.after(0, lambda: self.aktualizuj_nazev_hry_v_seznamu(nazev, nalezeny_port))
                            zprava = TEXTY["msg_invite_broadcast_port"][self.app.jazyk].format(nazev, nalezeny_port, self.app.moje_ip)
                            self.app.root.after(0, lambda: self.app.chat_box.insert("end", TEXTY["msg_radar_success"][self.app.jazyk].format(nazev, nalezeny_port)))
                            self.app.root.after(0, lambda: self.app.chat_box.itemconfig("end", fg="#2ecc71"))
                        else:
                            zprava = TEXTY["msg_invite_broadcast"][self.app.jazyk].format(nazev, self.app.moje_ip)

                        msg_id = str(int(datetime.datetime.now().timestamp() * 1000))
                        for cilova_adresa in self.app.ziskat_spravne_broadcasty():
                            self.app.poslat_udp_zpravu(f"__MSG__:{msg_id}:{muj_nick}:{zprava}", cilova_adresa, broadcast=True)

                    threading.Thread(target=stopar_portu, daemon=True).start()

                else:
                    zprava = TEXTY["msg_invite_broadcast_port"][self.app.jazyk].format(nazev, port, self.app.moje_ip)
                    msg_id = str(int(datetime.datetime.now().timestamp() * 1000))
                    for cilova_adresa in self.app.ziskat_spravne_broadcasty():
                        self.app.poslat_udp_zpravu(f"__MSG__:{msg_id}:{muj_nick}:{zprava}", cilova_adresa, broadcast=True)

                    self.app.chat_box.insert("end", TEXTY["msg_game_started"][self.app.jazyk])
                    self.app.notebook.set(TEXTY["tab_chat"][self.app.jazyk]) 

            except Exception as e:
                titulek = TEXTY["err_title"][self.app.jazyk]
                chyba_txt = TEXTY["err_game_start"][self.app.jazyk]
                messagebox.showerror(titulek, f"{chyba_txt}:\n{e}")
        else:
            titulek = "Chyba" if self.app.jazyk == "CZ" else "Error"
            messagebox.showerror(titulek, TEXTY["msg_game_not_found"][self.app.jazyk])
            self.odebrat_hru()

    def zpracuj_hozenou_hru(self, event):
        cesta = event.data.strip('{}') 
        if not cesta.lower().endswith('.exe'):
            messagebox.showwarning(TEXTY["title_warning"][self.app.jazyk], TEXTY["msg_only_exe"][self.app.jazyk])
            return
        self.otevrit_okno_pridani_hry(cesta)

    def aktualizovat_texty(self):
        try:
            self.btn_pridat_hru.configure(text=TEXTY["btn_add_game"][self.app.jazyk])
        except: pass

    def zmenit_motiv(self, barva_hlavni, barva_hover):
        try:
            self.btn_pridat_hru.configure(fg_color=barva_hlavni, hover_color=barva_hover)
        except: pass
