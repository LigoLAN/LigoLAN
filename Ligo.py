import customtkinter as ctk
import tkinter.messagebox as mb
from gui.app_window import ModerniAppka, LANPartyTool
import os

if __name__ == "__main__":
    try:
        root = ModerniAppka() 
    except Exception as e:
        root = ctk.CTk() 
        root.withdraw() 
        mb.showerror("Kritická chyba", f"Knihovna tkinterdnd2 chybí!\nSpusťte cmd a zadejte:\npip install tkinterdnd2\n\nDetail: {e}")
        root.destroy()
        root = ctk.CTk() 
        
    app = LANPartyTool(root)
    
    try:
        root.mainloop()
    except Exception:
        os._exit(0)
