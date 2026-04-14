import socket
import threading
import time
import os
import shutil
from config import *
import tkinter.messagebox as messagebox

class TcpTransfer:
    def __init__(self, app):
        self.app = app
        self.tcp_sock = None

    def start_server(self):
        threading.Thread(target=self._vlakno_tcp_naslouchani, daemon=True).start()

    def close_server(self):
        try:
            if self.tcp_sock: self.tcp_sock.close()
        except: pass

    def _vlakno_tcp_naslouchani(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                server.bind(("0.0.0.0", TCP_PORT))
            except OSError:
                self.app.zapsat_do_logu("[CHYBA] TCP Port je obsazen.")
                self.app.root.after(0, lambda: messagebox.showerror(TEXTY["err_tcp_in_use_title"][self.app.jazyk], TEXTY["err_tcp_in_use_text"][self.app.jazyk]))
                return 
                
            server.listen(5)
            self.tcp_sock = server 
            while True:
                try:
                    conn, addr = server.accept()
                except OSError:
                    break 

                ip = addr[0]
                
                with self.app.lock_soubory:
                    jeho_id = "UNKNOWN"
                    with self.app.lock_hraci:
                        if ip in self.app.seznam_hracu:
                            jeho_id = self.app.seznam_hracu[ip].get("ligo_id", "UNKNOWN")
                    
                    klic_agendy = jeho_id if jeho_id != "UNKNOWN" else ip

                    if klic_agendy in self.app.ocekavane_soubory:
                        opravdovy_klic = klic_agendy
                    elif ip in self.app.ocekavane_soubory:
                        opravdovy_klic = ip
                    else:
                        opravdovy_klic = None

                    if opravdovy_klic:
                        cesta = self.app.ocekavane_soubory.pop(opravdovy_klic)
                        velikost = self.app.ocekavane_velikosti.get(opravdovy_klic, 0)
                        
                        threading.Thread(target=self.prijmout_soubor_tcp, args=(conn, cesta, ip, velikost, opravdovy_klic), daemon=True).start()
                    else: 
                        self.app.zapsat_do_logu(f"[BEZPEČNOST] Odmítnuto neznámé TCP spojení z IP: {ip}")
                        conn.close() 
        except Exception as e: 
            self.app.zapsat_do_logu(f"[TCP SERVER CHYBA]: {e}")

    def prijmout_soubor_tcp(self, conn, cesta, ip, celkova_velikost=0, klic_agendy=""):
        if not klic_agendy: klic_agendy = ip 
            
        uspesne = False
        nazev_souboru = os.path.basename(cesta)
        conn.settimeout(15.0)
        
        cesta_part = f"{cesta}_{klic_agendy.replace('.','_')}.ligopart"
        id_ukolu = f"recv|{nazev_souboru}|{time.time()}"
        
        try:
            volne_misto = shutil.disk_usage(SDILENA_SLOZKA).free
            if celkova_velikost > volne_misto:
                err_msg = TEXTY["err_disk_space"][self.app.jazyk].format(nazev_souboru)
                self.app.root.after(0, messagebox.showerror, TEXTY["err_title"][self.app.jazyk], err_msg)
                self.app.poslat_udp_zpravu(f"__REMOTE_CTRL__:CANCEL:{nazev_souboru}", ip)
                conn.close()
                self.app.root.after(500, lambda: self._spust_dalsi_z_fronty(klic_agendy))
                return
        except: pass
        
        if not hasattr(self.app, 'pauznute_prenosy'): self.app.pauznute_prenosy = set()
        
        velikost_balicku = 1048576
        celkem_balicku = (celkova_velikost // velikost_balicku) + (1 if celkova_velikost % velikost_balicku > 0 else 0) if celkova_velikost > 0 else 0
        
        txt_stahuji = TEXTY["prog_downloading"][self.app.jazyk]
        txt_start = f"⬇️ {txt_stahuji}: {nazev_souboru}" + (" (0%)" if celkova_velikost > 0 else "")
        self.app.root.after(0, self.app.start_ukol, id_ukolu, txt_start, celkem_balicku, True)
        self.app.root.after(100, lambda: self.app.nastav_opravdovou_pauzu(id_ukolu))

        def vlakno_prijmu():
            uspesne = False
            aktualni_velikost = celkova_velikost
            try:
                prijato_bajtu = os.path.getsize(cesta_part) if os.path.exists(cesta_part) else 0
                aktualni_balicek = prijato_bajtu // velikost_balicku
                posledni_aktualizace = time.time()
                bajty_od_posledni = 0
                
                with open(cesta_part, 'ab') as f: 
                    while True:
                        if hasattr(self.app, 'zrusene_prenosy') and id_ukolu in self.app.zrusene_prenosy:
                            raise InterruptedError("Zrušeno uživatelem")

                        while id_ukolu in self.app.pauznute_prenosy:
                            if hasattr(self.app, 'zrusene_prenosy') and id_ukolu in self.app.zrusene_prenosy:
                                raise InterruptedError("Zrušeno uživatelem")
                            time.sleep(0.5)
                            posledni_aktualizace = time.time()
                            bajty_od_posledni = 0

                        if aktualni_velikost <= 0:
                            with self.app.lock_soubory:
                                aktualni_velikost = self.app.ocekavane_velikosti.get(klic_agendy, 0)
                                if aktualni_velikost > 0:
                                    nonlocal celkem_balicku
                                    celkem_balicku = (aktualni_velikost // velikost_balicku) + (1 if aktualni_velikost % velikost_balicku > 0 else 0)

                        if aktualni_velikost > 0:
                            chunk_size = min(velikost_balicku, aktualni_velikost - prijato_bajtu)
                            if chunk_size <= 0: break 
                        else:
                            chunk_size = velikost_balicku

                        data = conn.recv(chunk_size) 
                        if not data: break
                        
                        f.write(data)
                        prijato_bajtu += len(data)
                        bajty_od_posledni += len(data)
                        aktualni_balicek = prijato_bajtu // velikost_balicku
                        
                        nyni = time.time()
                        rozdil_casu = nyni - posledni_aktualizace
                        
                        if rozdil_casu > 0.5 or (aktualni_velikost > 0 and prijato_bajtu >= aktualni_velikost): 
                            rychlost_mb = (bajty_od_posledni / rozdil_casu) / (1024*1024) if rozdil_casu > 0 else 0
                            txt_stahuji = TEXTY["prog_downloading"][self.app.jazyk]
                            
                            if aktualni_velikost > 0:
                                procenta = int((prijato_bajtu / aktualni_velikost) * 100)
                                txt = f"⬇️ {txt_stahuji}: {nazev_souboru} ({procenta}%)  [{rychlost_mb:.1f} MB/s]"
                                self.app.root.after(0, self.app.update_ukol, id_ukolu, txt, procenta, "determinate", aktualni_balicek, celkem_balicku)
                            else:
                                mb = round(prijato_bajtu / (1024*1024), 1)
                                txt = f"⬇️ {txt_stahuji}: {nazev_souboru} ({mb} MB)  [{rychlost_mb:.1f} MB/s]"
                                self.app.root.after(0, self.app.update_ukol, id_ukolu, txt, None, "indeterminate")
                                
                            posledni_aktualizace = nyni
                            bajty_od_posledni = 0
                        
                        if aktualni_velikost > 0 and prijato_bajtu >= aktualni_velikost:
                            break
                            
                try:
                    if os.path.exists(cesta): os.remove(cesta) 
                    os.rename(cesta_part, cesta) 
                except Exception as e:
                    self.app.zapsat_do_logu(f"Chyba při přejmenování .ligopart: {e}")
                            
                uspesne = True
                self.app.root.after(0, self.app.konec_ukol, id_ukolu, f"{TEXTY['task_down'][self.app.jazyk]}: {nazev_souboru}")
                self.app.root.after(0, self.app.aktualizuj_moji_slozku_potichu)
                if getattr(self.app, 'zvuky_zapnuty', False):
                    try:
                        import winsound
                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                    except: pass
                
                with self.app.lock_soubory:
                    if klic_agendy in self.app.prave_stahuji_od: self.app.prave_stahuji_od.remove(klic_agendy)
                self.app.root.after(1000, lambda: self._spust_dalsi_z_fronty(klic_agendy))
                    
            except InterruptedError:
                self.app.root.after(0, self.app.konec_ukol, id_ukolu, TEXTY["task_canceled"][self.app.jazyk], "#e74c3c")
                with self.app.lock_soubory:
                    if klic_agendy in self.app.prave_stahuji_od: self.app.prave_stahuji_od.remove(klic_agendy)
                self.app.root.after(1000, lambda: self._spust_dalsi_z_fronty(klic_agendy))
                
            except (Exception, socket.timeout) as e: 
                def nastav_chybu():
                    if id_ukolu in self.app.aktivni_ulohy:
                        ul = self.app.aktivni_ulohy[id_ukolu]
                        txt_chyba = TEXTY["task_err_drop"][self.app.jazyk]
                        ul["lbl"].config(text=f"{txt_chyba} {nazev_souboru}", fg="#e74c3c")
                        
                        if ul.get("btn_pauza"):
                            ul["btn_pauza"].configure(text=TEXTY["btn_retry_task"][self.app.jazyk], fg_color="#3498db", hover_color="#2980b9", command=lambda: self.restartovat_stahovani(id_ukolu, klic_agendy, nazev_souboru))
                            ul["btn_pauza"].configure(state="normal")
                            
                        if ul.get("btn_zrusit"):
                            def uklid_mrtvoly():
                                try: os.remove(cesta_part) 
                                except: pass
                                self.app._smazat_ukol(id_ukolu)
                            ul["btn_zrusit"].configure(command=uklid_mrtvoly)
                            ul["btn_zrusit"].configure(state="normal")
                self.app.root.after(0, nastav_chybu)
                        
                with self.app.lock_soubory:
                    if klic_agendy in self.app.ocekavane_velikosti: self.app.ocekavane_velikosti.pop(klic_agendy, None)
                    if klic_agendy in self.app.prave_stahuji_od: self.app.prave_stahuji_od.remove(klic_agendy)
                    
                if id_ukolu in getattr(self.app, 'pauznute_prenosy', set()): self.app.pauznute_prenosy.remove(id_ukolu)
                self.app.root.after(1000, lambda: self._spust_dalsi_z_fronty(klic_agendy))

        threading.Thread(target=vlakno_prijmu, daemon=True).start()

    def odeslat_soubor_tcp(self, ip, cesta, offset=0, klic_agendy=""):
        if not klic_agendy: klic_agendy = ip 
            
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nazev_souboru = os.path.basename(cesta)
        id_ukolu = f"send|{ip}|{nazev_souboru}|{time.time()}"
        
        if not hasattr(self.app, 'aktivni_stahovaci'): self.app.aktivni_stahovaci = set()
        if not hasattr(self.app, 'pauznute_prenosy'): self.app.pauznute_prenosy = set()
        if not hasattr(self.app, 'prave_odesilam_na'): self.app.prave_odesilam_na = set()
        
        def uvolni_a_spust_dalsi():
            with self.app.lock_soubory:
                if klic_agendy in self.app.prave_odesilam_na: self.app.prave_odesilam_na.remove(klic_agendy)
                if hasattr(self.app, 'fronta_odesilani') and klic_agendy in self.app.fronta_odesilani and len(self.app.fronta_odesilani[klic_agendy]) > 0:
                    dalsi = self.app.fronta_odesilani[klic_agendy].pop(0)
                    self.app.prave_odesilam_na.add(klic_agendy)
                    self.app.root.after(0, lambda: self.app._smazat_ukol(dalsi["id"]))
                    
                    aktualni_ip = ip
                    with self.app.lock_hraci:
                        for hip, hdata in self.app.seznam_hracu.items():
                            if hdata.get("ligo_id") == klic_agendy or hip == klic_agendy:
                                aktualni_ip = hip
                                break
                    threading.Thread(target=self.odeslat_soubor_tcp, args=(aktualni_ip, dalsi["cesta"], 0, klic_agendy), daemon=True).start()

        try:
            self.app.aktivni_stahovaci.add(ip) 
            velikost = os.path.getsize(cesta)
            velikost_balicku = 1048576 
            celkem_balicku = (velikost // velikost_balicku) + (1 if velikost % velikost_balicku > 0 else 0)
            
            s.settimeout(3) 
            try: s.connect((ip, TCP_PORT))
            except:
                s.close()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((self.app.moje_ip, 0)) 
                s.settimeout(3)
                s.connect((ip, TCP_PORT))
            s.settimeout(None) 
            
            try: self.app.root.after(0, lambda: self.app.notebook.set(TEXTY["tab_files"][self.app.jazyk]))
            except: pass
            
            self.app.root.after(0, self.app.start_ukol, id_ukolu, f"Odesílám: {nazev_souboru} (0%)", celkem_balicku, True)
            self.app.root.after(100, lambda: self.app.nastav_opravdovou_pauzu(id_ukolu))
            
            odeslano_bajtu = offset 
            aktualni_balicek = offset // velikost_balicku
            posledni_aktualizace = time.time()
            bajty_od_posledni = 0 
            
            with open(cesta, 'rb') as f:
                if offset > 0: f.seek(offset)
                    
                while True: 
                    if hasattr(self.app, 'zrusene_prenosy') and id_ukolu in self.app.zrusene_prenosy:
                        raise InterruptedError("Zrušeno uživatelem")

                    while id_ukolu in self.app.pauznute_prenosy:
                        if hasattr(self.app, 'zrusene_prenosy') and id_ukolu in self.app.zrusene_prenosy:
                            raise InterruptedError("Zrušeno uživatelem")
                        time.sleep(0.5) 
                        posledni_aktualizace = time.time()
                        bajty_od_posledni = 0

                    data = f.read(velikost_balicku) 
                    if not data: break 
                    
                    s.sendall(data)
                    odeslano_bajtu += len(data)
                    bajty_od_posledni += len(data)
                    aktualni_balicek += 1
                    
                    time.sleep(0.005) # Traffic Shaping
                    
                    nyni = time.time()
                    rozdil_casu = nyni - posledni_aktualizace
                    
                    if rozdil_casu > 0.5 or aktualni_balicek == celkem_balicku: 
                        procenta = int((odeslano_bajtu / velikost) * 100) if velikost > 0 else 0
                        rychlost_mb = (bajty_od_posledni / rozdil_casu) / (1024*1024) if rozdil_casu > 0 else 0
                        txt_odesilam = TEXTY["prog_sending"][self.app.jazyk]
                        txt = f"{txt_odesilam}: {nazev_souboru} ({procenta}%)  [{rychlost_mb:.1f} MB/s]"    
                        self.app.root.after(0, self.app.update_ukol, id_ukolu, txt, procenta, "determinate", aktualni_balicek, celkem_balicku)
                        posledni_aktualizace = nyni
                        bajty_od_posledni = 0

            self.app.root.after(0, self.app.konec_ukol, id_ukolu, f"{TEXTY['task_sent'][self.app.jazyk]}: {nazev_souboru}")
            
        except (ConnectionResetError, BrokenPipeError): 
            self.app.root.after(0, self.app.konec_ukol, id_ukolu, TEXTY["task_err_lost"][self.app.jazyk], "#e74c3c")
        except InterruptedError:
            self.app.root.after(0, self.app.konec_ukol, id_ukolu, TEXTY["task_canceled"][self.app.jazyk], "#e74c3c")
        except Exception: 
            self.app.root.after(0, self.app.konec_ukol, id_ukolu, TEXTY["task_err_net"][self.app.jazyk], "#e74c3c")
        finally:
            if ip in self.app.aktivni_stahovaci: self.app.aktivni_stahovaci.remove(ip) 
            if id_ukolu in getattr(self.app, 'pauznute_prenosy', set()): self.app.pauznute_prenosy.remove(id_ukolu)
            s.close()
            self.app.root.after(1000, uvolni_a_spust_dalsi)

    def restartovat_stahovani(self, id_ukolu, klic_agendy, nazev_souboru):
        self.app._smazat_ukol(id_ukolu)
        cilova_cesta = os.path.join(SDILENA_SLOZKA, nazev_souboru)
        
        with self.app.lock_soubory:
            if klic_agendy in self.app.prave_stahuji_od:
                if klic_agendy not in self.app.fronta_stahovani:
                    self.app.fronta_stahovani[klic_agendy] = []
                
                id_fronty = f"queue|{klic_agendy}|{nazev_souboru}|{time.time()}"
                self.app.fronta_stahovani[klic_agendy].append({"id": id_fronty, "nazev": nazev_souboru, "cesta": cilova_cesta, "typ": "shared"})
                
                txt_fronta = TEXTY["msg_queued"][self.app.jazyk]
                self.app.start_ukol(id_fronty, f"{txt_fronta}: {nazev_souboru}", is_transfer=False)
                return
            else:
                self.app.prave_stahuji_od.add(klic_agendy)
            
            self.app.ocekavane_soubory[klic_agendy] = cilova_cesta
            self.app.ocekavane_velikosti[klic_agendy] = 0
            
        cesta_part = f"{cilova_cesta}_{klic_agendy.replace('.','_')}.ligopart"
        offset = os.path.getsize(cesta_part) if os.path.exists(cesta_part) else 0
        
        aktualni_ip = klic_agendy
        with self.app.lock_hraci:
            for hip, hdata in self.app.seznam_hracu.items():
                if hdata.get("ligo_id") == klic_agendy or hip == klic_agendy:
                    aktualni_ip = hip
                    break
                    
        self.app.poslat_udp_zpravu(f"__DIR_GET__:{nazev_souboru}:{offset}", aktualni_ip)        

    def _spust_dalsi_z_fronty(self, klic_agendy):
        dalsi = None
        
        with self.app.lock_soubory:
            if klic_agendy in self.app.prave_stahuji_od:
                self.app.prave_stahuji_od.remove(klic_agendy)
                
            if klic_agendy in self.app.fronta_stahovani and len(self.app.fronta_stahovani[klic_agendy]) > 0:
                dalsi = self.app.fronta_stahovani[klic_agendy].pop(0) 
                self.app.prave_stahuji_od.add(klic_agendy)
                self.app.ocekavane_soubory[klic_agendy] = dalsi["cesta"]
                self.app.ocekavane_velikosti[klic_agendy] = 0

        if dalsi:
            nazev = dalsi["nazev"]
            cesta = dalsi["cesta"]
            id_fronty = dalsi["id"]
            typ_prenosu = dalsi.get("typ", "shared") 
            req_id = dalsi.get("req_id", "")
            
            self.app._smazat_ukol(id_fronty) 
            
            aktualni_ip = None
            with self.app.lock_hraci:
                for hip, hdata in self.app.seznam_hracu.items():
                    if hdata.get("ligo_id") == klic_agendy or hip == klic_agendy:
                        aktualni_ip = hip
                        break
            
            if not aktualni_ip:
                with self.app.lock_soubory:
                    self.app.ocekavane_soubory.pop(klic_agendy, None)
                    if klic_agendy in self.app.prave_stahuji_od: self.app.prave_stahuji_od.remove(klic_agendy)
                    self.app.fronta_stahovani[klic_agendy].insert(0, dalsi)
                self.app.root.after(5000, lambda: self._spust_dalsi_z_fronty(klic_agendy))
                return
            
            cesta_part = f"{cesta}_{klic_agendy.replace('.','_')}.ligopart"
            offset = os.path.getsize(cesta_part) if os.path.exists(cesta_part) else 0
            
            if typ_prenosu == "private":
                self.app.poslat_udp_zpravu(f"__FILE_ACCEPT__:{req_id}", aktualni_ip)
            else:
                self.app.poslat_udp_zpravu(f"__DIR_GET__:{nazev}:{offset}", aktualni_ip)

            def hlidac_fronty():
                time.sleep(30.0)
                with self.app.lock_soubory:
                    if klic_agendy in self.app.ocekavane_soubory and self.app.ocekavane_soubory[klic_agendy] == cesta:
                        self.app.ocekavane_soubory.pop(klic_agendy)
                        if klic_agendy in self.app.prave_stahuji_od: self.app.prave_stahuji_od.remove(klic_agendy)
                        self.app.root.after(0, lambda: self._spust_dalsi_z_fronty(klic_agendy))
            threading.Thread(target=hlidac_fronty, daemon=True).start()
