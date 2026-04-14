import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import datetime
import subprocess
from config import *
from network.voice_chat import VoiceChat

class TabSquad:
    def __init__(self, app, parent_tab):
        self.app = app
        self.parent_tab = parent_tab
        
        # --- Vykreslení obsahu záložky v hlavním okně ---
        self.lbl_squad_info = ctk.CTkLabel(self.parent_tab, text=TEXTY["lbl_squad_info"][self.app.jazyk], font=("Arial", 14), text_color="#bdc3c7")
        self.lbl_squad_info.pack(pady=(30, 15))
        
        self.btn_vytvorit_tym = ctk.CTkButton(self.parent_tab, text=TEXTY["btn_create_squad"][self.app.jazyk], command=self.zalozit_tym, fg_color="#3498db", hover_color="#2980b9", font=("Arial", 16, "bold"), height=50, corner_radius=8)
        self.btn_vytvorit_tym.pack(fill="x", padx=60, pady=10)

    def zalozit_tym(self):
        if hasattr(self.app, 'tymove_okno') and self.app.tymove_okno is not None and self.app.tymove_okno.winfo_exists():
            self.app.tymove_okno.deiconify()
            self.app.tymove_okno.focus()
            return
        
        vybrane_ip = []
        jmena = []
        with self.app.lock_hraci:
            for ip, data in self.app.seznam_hracu.items():
                try:
                    if data.get("chk_tym") and str(data["chk_tym"].get()) == "1":
                        vybrane_ip.append(ip)
                        jmena.append(data.get("jmeno", "Hráč"))
                except: pass
                    
        if not vybrane_ip:
            messagebox.showwarning(TEXTY["win_empty_squad"][self.app.jazyk], TEXTY["msg_empty_squad"][self.app.jazyk])
            return
            
        if len(vybrane_ip) > 5: # 5 cizích hráčů + ty = 6 maximálně
            messagebox.showwarning(TEXTY["win_big_squad"][self.app.jazyk], TEXTY["msg_big_squad"][self.app.jazyk])
            return
            
        self.otevrit_tymovou_mistnost(vybrane_ip, jmena)
        
        muj_nick = self.app.entry_nick.get().strip() or "Neznámý"
        
        vsechny_ip = vybrane_ip + [self.app.moje_ip]
        vsechna_jmena = jmena + [muj_nick]
        
        seznam_ip_str = ",".join(vsechny_ip)
        seznam_jmen_str = ",".join(vsechna_jmena)
        
        for ip in vybrane_ip:
            self.app.poslat_udp_zpravu(f"__SQUAD_INVITE__:{seznam_ip_str}:{seznam_jmen_str}", ip)

    def otevrit_tymovou_mistnost(self, hraci_ip_seznam, jmena_hracu):
        if hasattr(self.app, 'tymove_okno') and self.app.tymove_okno is not None and self.app.tymove_okno.winfo_exists():
            self.app.tymove_okno.focus()
            if hasattr(self.app, 'hlasovy_klient'):
                self.app.hlasovy_klient.nastav_tym(hraci_ip_seznam)
            return

        def vypis_chybu(err):
            try: self.app.root.after(0, lambda: self.app.tymovy_chat.insert("end", err))
            except: pass

        self.app.hlasovy_klient = VoiceChat(VOICE_PORT, callback_chyba=vypis_chybu)
        if not self.app.hlasovy_klient.pyaudio_dostupne:
            messagebox.showerror(TEXTY["err_title"][self.app.jazyk], TEXTY["msg_pyaudio_err"][self.app.jazyk])
            return

        self.app.hlasovy_klient.nastav_tym(hraci_ip_seznam)
        self.app.hlasovy_klient.start()

        self.app.tym_ip_adresy = hraci_ip_seznam 
        self.app.tym_jmena_hracu = jmena_hracu 
        self.app.tymove_okno_aktivni = True

        self.app.tymove_okno = ctk.CTkToplevel(self.app.root)
        self.app.tymove_okno.title(f"{TEXTY['win_squad_title'][self.app.jazyk]} {', '.join(jmena_hracu)}")
        self.app.tymove_okno.geometry("650x450")
        self.app.tymove_okno.configure(fg_color="#141414") 
        self.app.tymove_okno.protocol("WM_DELETE_WINDOW", self.definitivne_opustit_tym)

        lbl_nadpis = ctk.CTkLabel(self.app.tymove_okno, text=TEXTY["lbl_squad_comms"][self.app.jazyk], font=("Arial", 16, "bold"), text_color="#2ecc71")
        lbl_nadpis.pack(pady=(15, 5))

        self.app.tymovy_chat = tk.Listbox(self.app.tymove_okno, bg="#1e1e1e", fg="#ffffff", font=("Arial", 12), selectbackground="#3498db", bd=1, relief="solid")
        self.app.tymovy_chat.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.app.tymovy_chat.insert("end", f"{TEXTY['msg_squad_welcome'][self.app.jazyk]} {', '.join(jmena_hracu)}")
        self.app.tymovy_chat.itemconfig("end", fg="#f1c40f")

        ramecek_dole = ctk.CTkFrame(self.app.tymove_okno, fg_color="transparent")
        ramecek_dole.pack(fill="x", padx=15, pady=15)

        self.app.btn_mikrofon = ctk.CTkButton(ramecek_dole, text=TEXTY["btn_mic_on"][self.app.jazyk], fg_color="#e74c3c", hover_color="#c0392b", font=("Arial", 13, "bold"), height=45, width=170, command=self.prepni_mikrofon)
        self.app.btn_mikrofon.pack(side="left", padx=(0, 5))

        self.app.btn_nastaveni_mic = ctk.CTkButton(ramecek_dole, text=TEXTY["btn_settings"][self.app.jazyk], fg_color="#7f8c8d", hover_color="#95a5a6", font=("Arial", 12, "bold"), height=45, width=100, command=self.otevrit_nastaveni_mikrofonu)
        self.app.btn_nastaveni_mic.pack(side="left", padx=(0, 10))

        txt_zavesit = TEXTY["btn_hangup"][self.app.jazyk]
        self.btn_zavesit = ctk.CTkButton(ramecek_dole, text=txt_zavesit, fg_color="#c0392b", hover_color="#922b21", font=("Arial", 12, "bold"), height=45, width=100, command=self.definitivne_opustit_tym)
        self.btn_zavesit.pack(side="left", padx=(0, 10))

        self.app.vstup_tym_chat = ctk.CTkEntry(ramecek_dole, font=("Arial", 14), height=45, placeholder_text=TEXTY["ph_squad_chat"][self.app.jazyk])
        self.app.vstup_tym_chat.pack(side="left", fill="x", expand=True)

        def poslat_do_tymu(event=None):
            txt = self.app.vstup_tym_chat.get().strip()
            if txt:
                muj_nick = self.app.entry_nick.get().strip() or "Neznámý"
                self.app.tymovy_chat.insert("end", f"{TEXTY['msg_you'][self.app.jazyk]}: {txt}")
                self.app.tymovy_chat.itemconfig("end", fg="#3498db")
                self.app.tymovy_chat.yview("end")
                self.app.vstup_tym_chat.delete(0, tk.END)
                
                msg_id = str(int(datetime.datetime.now().timestamp() * 1000))
                for ip in getattr(self.app, 'tym_ip_adresy', []):
                    self.app.poslat_udp_zpravu(f"__SQUAD__:{msg_id}:{muj_nick}:{txt}", ip)

        self.app.vstup_tym_chat.bind("<Return>", poslat_do_tymu)

    def prepni_mikrofon(self):
        if not hasattr(self.app, 'hlasovy_klient'): return
        
        if not self.app.hlasovy_klient.mikrofon_zapnuty:
            self.app.hlasovy_klient.zapni_mikrofon()
            self.app.btn_mikrofon.configure(text=TEXTY["btn_mic_active"][self.app.jazyk], fg_color="#2ecc71", hover_color="#27ae60")
            self.app.tymovy_chat.insert("end", TEXTY["msg_mic_connecting"][self.app.jazyk])
            self.app.tymovy_chat.itemconfig("end", fg="#2ecc71")
        else:
            self.app.hlasovy_klient.vypni_mikrofon()
            self.app.btn_mikrofon.configure(text=TEXTY["btn_mic_on"][self.app.jazyk], fg_color="#e74c3c", hover_color="#c0392b")
            self.app.tymovy_chat.insert("end", TEXTY["msg_mic_muted"][self.app.jazyk])
            self.app.tymovy_chat.itemconfig("end", fg="#e74c3c")
            
        self.app.tymovy_chat.yview("end")

    def definitivne_opustit_tym(self):
        self.app.tymove_okno_aktivni = False
        if hasattr(self.app, 'hlasovy_klient'):
            self.app.hlasovy_klient.stop()
            
        try: 
            if hasattr(self.app, 'tymove_okno') and self.app.tymove_okno.winfo_exists():
                self.app.tymove_okno.destroy()
        except: pass

    def otevrit_nastaveni_mikrofonu(self):
        try:
            subprocess.Popen("control mmsys.cpl,,1", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            self.app.zapsat_do_logu(f"[CHYBA] Nelze otevřít nastavení mikrofonu: {e}")

    def aktualizovat_texty(self):
        j = self.app.jazyk
        try:
            self.lbl_squad_info.configure(text=TEXTY["lbl_squad_info"][j])
            self.btn_vytvorit_tym.configure(text=TEXTY["btn_create_squad"][j])
            
            if hasattr(self.app, 'tymove_okno_aktivni') and self.app.tymove_okno_aktivni:
                self.app.tymove_okno.title(f"{TEXTY['win_squad_title'][j]} {', '.join(getattr(self.app, 'tym_jmena_hracu', []))}")
                if self.app.hlasovy_klient.mikrofon_zapnuty:
                    self.app.btn_mikrofon.configure(text=TEXTY["btn_mic_active"][j])
                else:
                    self.app.btn_mikrofon.configure(text=TEXTY["btn_mic_on"][j])
                self.app.btn_nastaveni_mic.configure(text=TEXTY["btn_settings"][j])
                self.app.vstup_tym_chat.configure(placeholder_text=TEXTY["ph_squad_chat"][j])
        except: pass
