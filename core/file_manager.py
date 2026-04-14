import os
import zipfile
import shutil
import threading
import time

class FileManager:
    @staticmethod
    def ziskat_velikost_slozky(cesta):
        """Projistí složku a vrátí její velikost v bajtech."""
        celkova = 0
        for r, d, files in os.walk(cesta):
            for f in files:
                try: celkova += os.path.getsize(os.path.join(r, f))
                except: pass
        return celkova

    @staticmethod
    def zabalit_slozku_async(zdrojova_slozka, cilovy_zip, zruseno_check_fn, callback_progress, callback_hotovo, callback_chyba):
        """Univerzální funkce pro bleskové balení složky s podporou zrušení a progrese."""
        def proces_baleni():
            try:
                celkova_velikost = FileManager.ziskat_velikost_slozky(zdrojova_slozka)
                zabaleno_bajtu = 0
                posledni_update = time.time()
                velikost_kousku = 1048576  # 1 MB kousky
                
                with zipfile.ZipFile(cilovy_zip, 'w', zipfile.ZIP_STORED) as zipf:
                    for root_dir, dirs, files in os.walk(zdrojova_slozka):
                        for file in files:
                            # Kontrola, jestli uživatel neklikl na tlačítko "Zrušit"
                            if zruseno_check_fn and zruseno_check_fn():
                                zipf.close()
                                try: os.remove(cilovy_zip)
                                except: pass
                                return 
                                
                            file_path = os.path.join(root_dir, file)
                            arcname = os.path.relpath(file_path, start=zdrojova_slozka)
                            
                            try:
                                with open(file_path, 'rb') as f_in:
                                    with zipf.open(arcname, 'w') as f_out:
                                        while True:
                                            kousek = f_in.read(velikost_kousku)
                                            if not kousek: break
                                            
                                            f_out.write(kousek)
                                            zabaleno_bajtu += len(kousek)
                                            
                                            # Průběžně posíláme procenta do GUI
                                            nyni = time.time()
                                            if celkova_velikost > 0 and (nyni - posledni_update > 0.2):
                                                procenta = int((zabaleno_bajtu / celkova_velikost) * 100)
                                                callback_progress(procenta)
                                                posledni_update = nyni
                            except Exception as e:
                                print(f"[ZIP] Chyba souboru {arcname}: {e}")
                                
                # Hotovo, posíláme zprávu zpět!
                callback_hotovo(cilovy_zip)
                
            except Exception as e:
                callback_chyba(str(e))

        # Spustí se neblokujícím způsobem na pozadí
        threading.Thread(target=proces_baleni, daemon=True).start()

    @staticmethod
    def kopirovat_soubor_async(zdroj, cil, callback_hotovo, callback_chyba):
        """Kopíruje soubory bez zamrznutí GUI."""
        def proces_kopirovani():
            try:
                shutil.copy2(zdroj, cil)
                callback_hotovo(cil)
            except Exception as e:
                callback_chyba(str(e))
        threading.Thread(target=proces_kopirovani, daemon=True).start()
