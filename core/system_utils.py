import os
import sys
import socket
import subprocess
import ctypes
import re

class SystemUtils:
    
    @staticmethod
    def vykonat_jako_spravce(prikazy):
        if not prikazy: return True
        spojene_prikazy = " & ".join(prikazy)
        try:
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c {spojene_prikazy}", None, 0)
            return ret > 32
        except Exception:
            return False

    @staticmethod
    def dostat_prikazy_firewall_povolit(udp_port, tcp_port):
        cesta_k_nam = sys.executable
        return [
            f'netsh advfirewall firewall add rule name="LAN Party APP" dir=in action=allow program="{cesta_k_nam}" enable=yes profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party APP" dir=out action=allow program="{cesta_k_nam}" enable=yes profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party Ping" protocol=icmpv4:8,any dir=in action=allow profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party Chat IN" protocol=UDP dir=in localport={udp_port} action=allow profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party Chat OUT" protocol=UDP dir=out remoteport={udp_port} action=allow profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party File IN" protocol=TCP dir=in localport={tcp_port} action=allow profile=any',
            f'netsh advfirewall firewall add rule name="LAN Party File OUT" protocol=TCP dir=out remoteport={tcp_port} action=allow profile=any'
        ]

    @staticmethod
    def dostat_prikazy_firewall_uklid():
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

    @staticmethod
    def ziskat_lokalni_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except: IP = '127.0.0.1'
        finally: s.close()
        return IP

    @staticmethod
    def ziskat_vsechny_moje_ip():
        moje_adresy = ["127.0.0.1"]
        try:
            for interface in socket.getaddrinfo(socket.gethostname(), None):
                ip = interface[4][0]
                if ip not in moje_adresy and not ":" in ip: 
                    moje_adresy.append(ip)
        except: pass
        return moje_adresy

    @staticmethod
    def ziskat_aktivni_adaptery():
        try:
            prikaz = "Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -ExpandProperty Name"
            vystup = subprocess.check_output(["powershell", "-command", prikaz], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            adaptery = [linka.strip() for linka in vystup.split('\n') if linka.strip()]
            return adaptery if adaptery else ["Ethernet", "Wi-Fi"]
        except: return ["Ethernet", "Wi-Fi"]

    @staticmethod
    def ziskat_ip_podle_adapteru(nazev_adapteru):
        try:
            prikaz = f"(Get-NetIPAddress -InterfaceAlias '{nazev_adapteru}' -AddressFamily IPv4).IPAddress"
            vystup = subprocess.check_output(["powershell", "-command", prikaz], text=True, creationflags=subprocess.CREATE_NO_WINDOW).strip()
            if vystup: return vystup.split('\n')[0].strip()
        except: pass
        return SystemUtils.ziskat_lokalni_ip()

    @staticmethod
    def najdi_port_procesu(nazev_exe):
        try:
            vystup_task = subprocess.check_output(
                ["tasklist", "/fi", f"imagename eq {nazev_exe}", "/nh"], 
                text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            match = re.search(rf'{nazev_exe}\s+(\d+)', vystup_task, re.IGNORECASE)
            if not match: return None
            pid = match.group(1)
            
            vystup_net = subprocess.check_output(["netstat", "-ano"], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            for radek in vystup_net.splitlines():
                if pid in radek and ("LISTENING" in radek or "NASLOUCHÁNÍ" in radek):
                    port_match = re.search(r'TCP\s+\S+:(\d+)', radek)
                    if port_match: return port_match.group(1)
        except: pass
        return None

    @staticmethod
    def zjisti_spustenou_hru(zname_procesy):
        try:
            vystup = subprocess.check_output(["tasklist", "/NH", "/FO", "CSV"], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            vystup_mala_pismena = vystup.lower()
            for exe, nazev in zname_procesy.items():
                if exe.lower() in vystup_mala_pismena:
                    nalezeny_port = SystemUtils.najdi_port_procesu(exe)
                    if nalezeny_port:
                        return f"{nazev} (Port: {nalezeny_port})"
                    return nazev
        except: pass
        return ""

    @staticmethod
    def ziskej_hw_info():
        cpu_name = "Neznámý CPU"
        ram_gb = 0
        gpu_name = "Neznámá GPU"

        try:
            import winreg
            klicek = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu, _ = winreg.QueryValueEx(klicek, "ProcessorNameString")
            cpu_name = cpu.replace("Intel(R) Core(TM) ", "").replace("AMD Ryzen ", "Ryzen ").replace(" CPU", "").replace(" @", " |").strip()
        except:
            import platform
            try: cpu_name = platform.processor()
            except: pass

        try:
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

        try:
            import winreg
            klicek_gpu_base = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}")
            nalezene_grafiky = []
            for i in range(5):
                try:
                    sub_key_name = f"{i:04d}"
                    sub_key = winreg.OpenKey(klicek_gpu_base, sub_key_name)
                    gpu, _ = winreg.QueryValueEx(sub_key, "DriverDesc")
                    if gpu and "Basic Display" not in gpu:
                        cisty_nazev = gpu.replace("NVIDIA GeForce ", "NVIDIA ").replace("AMD Radeon ", "AMD ").strip()
                        nalezene_grafiky.append(cisty_nazev)
                except: pass
            if nalezene_grafiky:
                herni_gpu = [g for g in nalezene_grafiky if "NVIDIA" in g.upper() or "RTX" in g.upper() or "GTX" in g.upper() or "RX " in g.upper()]
                gpu_name = herni_gpu[0] if herni_gpu else nalezene_grafiky[-1]
        except: pass

        return {"cpu": cpu_name, "ram": ram_gb, "gpu": gpu_name}

    @staticmethod
    def ziskej_ikonu_z_exe(cesta_exe, nazev_hry, slozka_ikon):
        os.makedirs(slozka_ikon, exist_ok=True)
        bezpecny_nazev = "".join([c for c in nazev_hry if c.isalnum() or c in " _-"]).strip()
        if not bezpecny_nazev: return None
        
        cesta_k_png = os.path.join(slozka_ikon, f"{bezpecny_nazev}.png")
        if os.path.exists(cesta_k_png) and os.path.getsize(cesta_k_png) > 0:
            return cesta_k_png

        if not os.path.exists(cesta_exe): return None

        try:
            ps_exe = cesta_exe.replace("'", "''")
            ps_png = cesta_k_png.replace("'", "''")
            ps_cmd = f"""
            try {{
                Add-Type -AssemblyName System.Drawing
                $icon = [System.Drawing.Icon]::ExtractAssociatedIcon('{ps_exe}')
                if ($icon -ne $null) {{
                    $bitmap = $icon.ToBitmap()
                    $bitmap.Save('{ps_png}', [System.Drawing.Imaging.ImageFormat]::Png)
                    $bitmap.Dispose()
                    $icon.Dispose()
                }}
            }} catch {{ }}
            """
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            if os.path.exists(cesta_k_png) and os.path.getsize(cesta_k_png) > 0:
                return cesta_k_png
        except: pass
        return None
