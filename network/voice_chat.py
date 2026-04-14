import socket
import threading

class VoiceChat:
    def __init__(self, voice_port, callback_chyba):
        self.voice_port = voice_port
        self.mikrofon_zapnuty = False
        self.mistnost_aktivni = False
        self.tym_ip_adresy = []
        self.callback_chyba = callback_chyba # Funkce pro bezpečný výpis chyb do GUI
        
        try:
            import pyaudio
            self.audio_modul = pyaudio.PyAudio()
            self.pyaudio_dostupne = True
        except ImportError:
            self.pyaudio_dostupne = False

    def nastav_tym(self, ip_adresy):
        self.tym_ip_adresy = ip_adresy

    def start(self):
        self.mistnost_aktivni = True
        threading.Thread(target=self._prijimat_hlas, daemon=True).start()

    def stop(self):
        self.mistnost_aktivni = False
        self.mikrofon_zapnuty = False

    def zapni_mikrofon(self):
        self.mikrofon_zapnuty = True
        threading.Thread(target=self._vysilat_mikrofon, daemon=True).start()

    def vypni_mikrofon(self):
        self.mikrofon_zapnuty = False

    def _vysilat_mikrofon(self):
        if not self.pyaudio_dostupne: return
        import pyaudio
        CHUNK = 512
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        stream = None
        sock = None
        try:
            stream = self.audio_modul.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            while self.mikrofon_zapnuty and self.mistnost_aktivni:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    for ip in self.tym_ip_adresy:
                        sock.sendto(data, (ip, self.voice_port))
                except: break
        except Exception as e:
            self.callback_chyba(f"[CHYBA MIKROFONU]: {e}")
        finally:
            try: 
                if stream:
                    stream.stop_stream()
                    stream.close()
            except: pass
            try: 
                if sock: sock.close()
            except: pass

    def _prijimat_hlas(self):
        if not self.pyaudio_dostupne: return
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
            sock.settimeout(0.5) 
            sock.bind(("0.0.0.0", self.voice_port))

            stream = self.audio_modul.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
            
            while self.mistnost_aktivni:
                try:
                    data, addr = sock.recvfrom(4096) 
                    if addr[0] in self.tym_ip_adresy:
                        stream.write(data)
                except socket.timeout:
                    continue
                except:
                    break
        except OSError:
            self.callback_chyba("[SÍŤOVÁ CHYBA] Zvukový port 12347 je již obsazen!")
        finally:
            try:
                if stream:
                    stream.stop_stream()
                    stream.close()
            except: pass
            try:
                if sock: sock.close()
            except: pass
