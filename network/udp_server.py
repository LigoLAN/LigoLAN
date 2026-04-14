import socket
import threading
import time
import datetime
import ipaddress
import os
from config import *

class UdpServer:
    def __init__(self, app):
        self.app = app # Odkaz na hlavní třídu GUI (LANPartyTool)
        self.udp_sock = None
        self.posledni_broadcasty = []
        self.cas_poslednich_broadcastu = 0
        self.prijata_id_zprav = set()

    def start(self):
        threading.Thread(target=self._vlakno_naslouchani, daemon=True).start()

    def zavrit_socket(self):
        try:
            if self.udp_sock:
                self.udp_sock.close()
        except: pass

    def poslat_udp_zpravu(self, zprava, ip, port=UDP_PORT, broadcast=False):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if broadcast:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(zprava.encode('utf-8'), (ip, port))
        except OSError as e:
            self.app.zapsat_do_logu(f"[UDP CHYBA] Nelze odeslat na {ip}: {e}")
        finally:
            try: sock.close()
            except: pass

    def ziskat_spravne_broadcasty(self):
        nyni = time.time()
        if nyni - self.cas_poslednich_broadcastu < 15 and self.posledni_broadcasty:
            return self.posledni_broadcasty

        broadcasty = set(['255.255.255.255'])
        if self.app.moje_ip and self.app.moje_ip != "127.0.0.1" and not self.app.moje_ip.startswith("169.254."):
            casti = self.app.moje_ip.split('.')
            if len(casti) == 4:
                cilova_adresa = f"{casti[0]}.{casti[1]}.{casti[2]}.255"
                broadcasty.add(cilova_adresa)
                
        self.posledni_broadcasty = list(broadcasty)
        self.cas_poslednich_broadcastu = nyni
        return self.posledni_broadcasty

    def _vlakno_naslouchani(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("0.0.0.0", UDP_PORT))
            except OSError:
                self.app.zapsat_do_logu("[CHYBA] UDP Port je obsazen.")
                return 
            
            self.udp_sock = sock 
            while True:
                try:
                    data, adresa = sock.recvfrom(16384) 
                except OSError:
                    break
                    
                text_zpravy = data.decode('utf-8', errors='ignore').strip()
                if not text_zpravy: continue
                
                try:
                    ip_odesilatele = adresa[0]
                    vsechny_moje_ip = self.app.ziskat_vsechny_moje_ip()
                    if ip_odesilatele in vsechny_moje_ip or ip_odesilatele == self.app.moje_ip: 
                        continue
                    
                    try:
                        ip_obj = ipaddress.ip_address(ip_odesilatele)
                        if not (ip_obj.is_private or ip_obj.is_loopback):
                            continue
                    except ValueError:
                        continue

                    if text_zpravy.startswith("__DIR_REQ__:"):
                        casti = text_zpravy.split(":", 2)
                        jeho_id = casti[1] if len(casti) > 2 else ip_odesilatele
                        jeho_nick = casti[-1]
                        
                        muj_nick = self.app.entry_nick.get().strip() or "Neznámý"
                        soubory_k_odeslani = []
                        try:
                            for s in os.listdir(SDILENA_SLOZKA):
                                cesta_s = os.path.join(SDILENA_SLOZKA, s)
                                if os.path.isfile(cesta_s):
                                    try: velikost_mb = round(os.path.getsize(cesta_s) / (1024*1024), 2)
                                    except: velikost_mb = "?"
                                    soubory_k_odeslani.append(f"{s}|{velikost_mb}")
                        except Exception as e:
                            self.app.zapsat_do_logu(f"[SDÍLENÍ CHYBA] {e}")

                        seznam_str = "*".join(soubory_k_odeslani)
                        self.poslat_udp_zpravu(f"__DIR_RES__:{self.app.ligo_id}:{muj_nick}:{seznam_str}", ip_odesilatele)
                        continue

                    if text_zpravy.startswith("__FILE_REQ__:"):
                        casti = text_zpravy.split(":", 5)
                        if len(casti) == 6:
                            _, req_id, jeho_id, nazev, velikost, jeho_nick = casti
                        else:
                            _, req_id, nazev, velikost, jeho_nick = text_zpravy.split(":", 4)
                            jeho_id = "UNKNOWN"
                            
                        nyni = time.time()
                        if nyni - self.app.spam_ochrana_soubory.get(ip_odesilatele, 0) < 0.5:
                            continue 
                        self.app.spam_ochrana_soubory[ip_odesilatele] = nyni
                        
                        self.app.root.after(0, self.app.dotaz_prijmout_soubor, ip_odesilatele, req_id, nazev, velikost, jeho_nick, jeho_id)
                        continue

                    if text_zpravy.startswith("__DIR_RES__:"):
                        casti_hlavni = text_zpravy.split(":", 3)
                        if len(casti_hlavni) < 4: continue
                        
                        jeho_id = casti_hlavni[1]
                        jeho_nick = casti_hlavni[2]
                        seznam_hvezdicky = casti_hlavni[3]
                        soubory = seznam_hvezdicky.split("*")
                        
                        klic_agendy = jeho_id if jeho_id != "UNKNOWN" else ip_odesilatele
                        
                        with self.app.lock_soubory:
                            if not hasattr(self.app, 'buffer_dir_res'): self.app.buffer_dir_res = {}
                            if not hasattr(self.app, 'buffer_dir_timer'): self.app.buffer_dir_timer = {}
                            
                            self.app.buffer_dir_res[klic_agendy] = []

                            for polozka in soubory:
                                if not polozka: continue 
                                if "|" in polozka:
                                    s, vel = polozka.rsplit("|", 1)
                                    text_velikosti = f"{vel} MB" if vel != "?" else "? MB"
                                else:
                                    s, text_velikosti = polozka, "? MB"

                                s = os.path.basename(s.replace("\\", "/"))
                                self.app.buffer_dir_res[klic_agendy].append({"nazev": s, "velikost": text_velikosti})
                            
                        if klic_agendy in getattr(self.app, 'buffer_dir_timer', {}):
                            self.app.root.after_cancel(self.app.buffer_dir_timer[klic_agendy])
                            
                        self.app.buffer_dir_timer[klic_agendy] = self.app.root.after(1000, lambda k=klic_agendy, ip=ip_odesilatele, n=jeho_nick: self.app.dokoncit_prijem_slozky(k, ip, n))
                        continue

                    if text_zpravy.startswith("__DIR_GET__:"):
                        casti = text_zpravy.split(":", 2)
                        nazev_souboru = os.path.basename(casti[1])
                        offset = int(casti[2]) if len(casti) > 2 else 0
                        
                        cesta_k_souboru = os.path.join(SDILENA_SLOZKA, nazev_souboru)
                        if os.path.exists(cesta_k_souboru):
                            try:
                                velikost = os.path.getsize(cesta_k_souboru)
                                self.poslat_udp_zpravu(f"__FILE_SIZE_INFO__:{velikost}", ip_odesilatele)
                            except: pass
                            
                            def zpozdene_odeslani():
                                time.sleep(0.5)
                                self.app.odeslat_soubor_tcp(ip_odesilatele, cesta_k_souboru, offset)
                                
                            threading.Thread(target=zpozdene_odeslani, daemon=True).start()
                        continue

                    if text_zpravy.startswith("__FILE_SIZE_INFO__:"):
                        try:
                            velikost = int(text_zpravy.split(":", 1)[1])
                            jeho_id = "UNKNOWN"
                            with self.app.lock_hraci:
                                if ip_odesilatele in self.app.seznam_hracu: 
                                    jeho_id = self.app.seznam_hracu[ip_odesilatele].get("ligo_id", "UNKNOWN")
                            
                            klic_agendy = jeho_id if jeho_id != "UNKNOWN" else ip_odesilatele
                            
                            with self.app.lock_soubory:
                                if klic_agendy in self.app.ocekavane_velikosti:
                                    self.app.ocekavane_velikosti[klic_agendy] = velikost
                                elif ip_odesilatele in self.app.ocekavane_velikosti:
                                    self.app.ocekavane_velikosti[ip_odesilatele] = velikost
                        except: pass
                        continue

                    if text_zpravy.startswith("__FILE_ACCEPT__:"):
                        req_id = text_zpravy.split(":")[1]
                        with self.app.lock_soubory:
                            if req_id in self.app.sdileni_ceka_na_prijemci:
                                cesta = self.app.sdileni_ceka_na_prijemci.pop(req_id)
                                
                                jeho_id = "UNKNOWN"
                                with self.app.lock_hraci:
                                    if ip_odesilatele in self.app.seznam_hracu:
                                        jeho_id = self.app.seznam_hracu[ip_odesilatele].get("ligo_id", "UNKNOWN")
                                klic_agendy = jeho_id if jeho_id != "UNKNOWN" else ip_odesilatele
                                
                                if klic_agendy in getattr(self.app, 'prave_odesilam_na', set()):
                                    if klic_agendy not in getattr(self.app, 'fronta_odesilani', {}):
                                        self.app.fronta_odesilani[klic_agendy] = []
                                    
                                    id_fronty = f"send_queue|{klic_agendy}|{os.path.basename(cesta)}|{time.time()}"
                                    self.app.fronta_odesilani[klic_agendy].append({"id": id_fronty, "cesta": cesta})
                                    
                                    txt_fronta = TEXTY["msg_queued"][self.app.jazyk]
                                    self.app.start_ukol(id_fronty, f"Odesílání čeká: {os.path.basename(cesta)}", is_transfer=False)
                                else:
                                    if not hasattr(self.app, 'prave_odesilam_na'): self.app.prave_odesilam_na = set()
                                    self.app.prave_odesilam_na.add(klic_agendy)
                                    threading.Thread(target=self.app.odeslat_soubor_tcp, args=(ip_odesilatele, cesta, 0, klic_agendy), daemon=True).start()
                        continue

                    if text_zpravy.startswith("__FILE_REJECT__:"):
                        req_id = text_zpravy.split(":")[1]
                        with self.app.lock_soubory:
                            if req_id in self.app.sdileni_ceka_na_prijemci: self.app.sdileni_ceka_na_prijemci.pop(req_id)
                        continue

                    if text_zpravy == "__DISCOVER__":
                        muj_nick = self.app.entry_nick.get().strip() or "Neznámý"
                        moje_hra = self.app.zjisti_moji_hru() 
                        self.poslat_udp_zpravu(f"__IAM__:{self.app.ligo_id}:{muj_nick}:{moje_hra}", ip_odesilatele)
                        continue

                    if text_zpravy.startswith("__DISCONNECT__:"):
                        jeho_id = text_zpravy.split(":")[1]
                        with self.app.lock_hraci:
                            ip_k_smazani = None
                            for u_ip, u_data in list(self.app.seznam_hracu.items()):
                                if u_data.get("ligo_id") == jeho_id:
                                    ip_k_smazani = u_ip
                                    break
                        if ip_k_smazani:
                            self.app.root.after(0, lambda ip_del=ip_k_smazani: self.app.odstranit_hrace(ip_del))
                        continue
                    
                    if text_zpravy.startswith("__IAM__:") or text_zpravy.startswith("__HEARTBEAT__:"):
                        casti = text_zpravy.split(":", 3)
                        if len(casti) >= 4:
                            jeho_id = casti[1]
                            jeho_nick = casti[2]
                            jeho_hra = casti[3] 
                            
                            if jeho_id == self.app.ligo_id: continue
                            
                            with self.app.lock_hraci:
                                stara_ip_k_smazani = None
                                for ulozena_ip, data in self.app.seznam_hracu.items():
                                    if data.get("ligo_id") == jeho_id and ulozena_ip != ip_odesilatele:
                                        stara_ip_k_smazani = ulozena_ip
                                        break
                                        
                                if stara_ip_k_smazani:
                                    self.app.seznam_hracu[ip_odesilatele] = self.app.seznam_hracu.pop(stara_ip_k_smazani)
                                    self.app.zapsat_do_logu(f"[SÍŤ] Hráč {jeho_nick} ({jeho_id}) přešel na novou IP: {stara_ip_k_smazani} -> {ip_odesilatele}")
                                    if stara_ip_k_smazani in self.app.okna_chatu:
                                        self.app.okna_chatu[ip_odesilatele] = self.app.okna_chatu.pop(stara_ip_k_smazani)
                                        
                            self.app.root.after(0, self.app.automaticky_pridat_do_gui, ip_odesilatele, jeho_nick, jeho_hra, jeho_id)
                            with self.app.lock_hraci:
                                if ip_odesilatele in self.app.seznam_hracu:
                                    self.app.seznam_hracu[ip_odesilatele]["posledni_aktivita"] = time.time()
                        continue

                    if text_zpravy.startswith("__ACK__:"):
                        msg_id = text_zpravy.split(":")[1]
                        with self.app.lock_statistiky:
                            if msg_id in self.app.cekajici_zpravy: self.app.cekajici_zpravy.remove(msg_id)
                        continue

                    if text_zpravy.startswith("__MSG__:"):
                        casti = text_zpravy.split(":", 4) 
                        if len(casti) == 5:
                            prefix, msg_id, jeho_id, jeho_nick, samotny_text = casti
                        elif len(casti) == 4:
                            prefix, msg_id, jeho_nick, samotny_text = casti
                            jeho_id = "UNKNOWN"
                        else: continue
                        
                        if jeho_id != "UNKNOWN":
                            with self.app.lock_hraci:
                                stara_ip = None
                                for u_ip, u_data in self.app.seznam_hracu.items():
                                    if u_data.get("ligo_id") == jeho_id and u_ip != ip_odesilatele:
                                        stara_ip = u_ip
                                        break
                                if stara_ip:
                                    self.app.seznam_hracu[ip_odesilatele] = self.app.seznam_hracu.pop(stara_ip)
                                    if stara_ip in self.app.okna_chatu:
                                        self.app.okna_chatu[ip_odesilatele] = self.app.okna_chatu.pop(stara_ip)
                                    self.app.pozadavek_na_vykresleni_radaru()

                        if msg_id in self.prijata_id_zprav:
                            self.poslat_udp_zpravu(f"__ACK__:{msg_id}", ip_odesilatele)
                            continue
                            
                        self.prijata_id_zprav.add(msg_id)
                        if len(self.prijata_id_zprav) > 500: self.prijata_id_zprav.clear()

                        self.poslat_udp_zpravu(f"__ACK__:{msg_id}", ip_odesilatele)
                        with self.app.lock_statistiky:
                            self.app.prijato += 1
                        self.app.root.after(0, self.app.zobrazit_prijatou_zpravu, ip_odesilatele, f"{jeho_nick}: {samotny_text}")
                        continue

                    if text_zpravy.startswith("__SQUAD_INVITE__:"):
                        casti = text_zpravy.split(":", 2)
                        if len(casti) == 3:
                            seznam_ip_str = casti[1]
                            seznam_jmen_str = casti[2]
                            
                            vsechny_ip = seznam_ip_str.split(",")
                            vsechna_jmena = seznam_jmen_str.split(",")
                            
                            cizi_ip = []
                            cizi_jmena = []
                            for ip_kolegy, jmeno_kolegy in zip(vsechny_ip, vsechna_jmena):
                                if ip_kolegy != self.app.moje_ip and ip_kolegy != "127.0.0.1":
                                    cizi_ip.append(ip_kolegy)
                                    cizi_jmena.append(jmeno_kolegy)
                            
                            if not (hasattr(self.app, 'tymove_okno_aktivni') and self.app.tymove_okno_aktivni):
                                if self.app.zvuky_zapnuty:
                                    try:
                                        import winsound 
                                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                                    except: pass
                                self.app.root.after(0, self.app.otevrit_tymovou_mistnost, cizi_ip, cizi_jmena)
                            else:
                                for ip_kolegy, jm in zip(cizi_ip, cizi_jmena):
                                    if ip_kolegy not in getattr(self.app, 'tym_ip_adresy', []):
                                        self.app.tym_ip_adresy.append(ip_kolegy)
                                        if hasattr(self.app, 'hlasovy_klient'):
                                            self.app.hlasovy_klient.nastav_tym(self.app.tym_ip_adresy)    
                                        self.app.root.after(0, lambda n=jm: self.app.tymovy_chat.insert("end", TEXTY["msg_squad_joined"][self.app.jazyk].format(n)))
                        continue

                    if text_zpravy.startswith("__SQUAD__:"):
                        casti = text_zpravy.split(":", 3)
                        if len(casti) == 4:
                            _, msg_id, jeho_nick, samotny_text = casti
                            
                            if not (hasattr(self.app, 'tymove_okno_aktivni') and self.app.tymove_okno_aktivni):
                                self.app.root.after(0, self.app.otevrit_tymovou_mistnost, [ip_odesilatele], [jeho_nick])
                                time.sleep(0.3) 
                                
                            if ip_odesilatele not in getattr(self.app, 'tym_ip_adresy', []):
                                self.app.tym_ip_adresy.append(ip_odesilatele)
                                if hasattr(self.app, 'hlasovy_klient'):
                                    self.app.hlasovy_klient.nastav_tym(self.app.tym_ip_adresy)
                                
                            if hasattr(self.app, 'tymove_okno_aktivni') and self.app.tymove_okno_aktivni:
                                def pridej_squad_msg(n=jeho_nick, t=samotny_text):
                                    try:
                                        self.app.tymovy_chat.insert("end", f"{n}: {t}")
                                        self.app.tymovy_chat.itemconfig("end", fg="#3498db")
                                        self.app.tymovy_chat.yview("end")
                                    except: pass
                                self.app.root.after(0, pridej_squad_msg)
                        continue
                    
                    if not text_zpravy.startswith("__"): continue

                    if text_zpravy.startswith("__REMOTE_CTRL__"):
                        _, prikaz, nazev_souboru = text_zpravy.split(":", 2)
                        if not hasattr(self.app, 'pauznute_prenosy'): self.app.pauznute_prenosy = set()
                        if not hasattr(self.app, 'zrusene_prenosy'): self.app.zrusene_prenosy = set()
                        
                        for tk_id in list(self.app.aktivni_ulohy.keys()):
                            if nazev_souboru in tk_id:
                                if prikaz == "PAUSE":
                                    self.app.pauznute_prenosy.add(tk_id)
                                elif prikaz == "RESUME":
                                    if tk_id in self.app.pauznute_prenosy: self.app.pauznute_prenosy.remove(tk_id)
                                elif prikaz == "CANCEL":
                                    self.app.zrusene_prenosy.add(tk_id)
                        continue
                        
                except Exception as e:
                    continue
                    
        except Exception as e: 
            self.app.zapsat_do_logu(f"[UDP NASLOUCHÁNÍ CHYBA]: {e}")
