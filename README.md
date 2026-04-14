# 🚀 LigoLAN v1.1
**Your personal network admin for hassle-free LAN gaming.**

## Hi there 👋
*💬 I would be incredibly grateful for any feedback, bug reports, or ideas for new features! If you find this tool helpful or run into any issues, please feel free to open an Issue here on GitHub or reach out directly. Let's make LAN parties great again together!*

Created by a gamer for gamers. LigoLAN is a free tool designed to eliminate all the frustration associated with setting up a local area network (LAN). No more wasted hours resolving IP address conflicts, manually poking holes in the Windows Firewall, or searching for a free USB flash drive to transfer files.

Install, run, and play. LigoLAN handles the rest.


<img width="1019" height="1040" alt="1" src="https://github.com/user-attachments/assets/300179f7-05c6-450d-8310-05baf4aaa042" />


### ✨ What's New in Version 1.1 (Massive Visual & UI Update)
For version 1.1, I focused heavily on a complete visual overhaul and code refactoring.
* **New Game Lobby:** Users are now sorted into a clean lobby system based on the game they are playing. Crucial for network stability with larger groups.
* **Improved 'My Games' Tab:** Games now automatically load their original icons. Added the ability to set and save custom launch mods/parameters for each game.
* **Smarter Chat & Folders:** Stopped annoying chat window pop-ups from interrupting active gameplay. Shared folders are now divided per PC for better orientation.
* **History Memory:** Private chat and Voice Squad now remember message history even if you accidentally close the window.

### ⚙️ Core Features
* 🛡️ **Smart Firewall & IP Management:** Automatically (with admin rights) detects your connection, assigns a safe local IP, and opens necessary ports. Cleans up perfectly upon exit.
* 📡 **Game Radar (UDP Broadcast):** Scans the network and detects running games of other players (supports dozens of classics).
* 📁 **Lightning-fast File Sharing (TCP):** Send files and entire folders (automatic ZIP packing) without complex Windows sharing setup.
* 💬 **Integrated Chat & Voice Squad:** Local text chat and a private, encrypted voice channel (UDP).
* 🔄 **Automatic Updates:** Checks GitHub and notifies the user if a new version is available.

### 🛠️ Installation and Usage
1. Go to the **Releases** section on the right side of this page and download the latest **LigoLAN_Setup.exe** installer.
2. Install the program (Windows 10 / 11 required).
3. Run LigoLAN. During the initial network setup, the program will request **administrator rights** (UAC) – this is necessary to modify IP addresses and the Firewall.

> **⚠️ Security Warning:** The program automatically opens ports `12345`, `12346`, and `12347` for local communication. External access is strictly blocked to everything except your shared folder, but we still recommend using it primarily on a trusted home/private network.

<img width="1019" height="1040" alt="2" src="https://github.com/user-attachments/assets/cd121729-103c-4599-a7ea-99cc826fde2f" />


### 💻 Technology Under the Hood
LigoLAN is written entirely in Python with a focus on asynchronous network communication and stability:
* **GUI:** `customtkinter` (modern UI), `tkinterdnd2` (Drag & Drop).
* **Networking:** Native `socket` library (TCP for files, UDP for radar and chat).
* **Audio:** `PyAudio` for low-latency voice transmission.
* **Architecture:** Modular MVC (Model-View-Controller) separating network layer from GUI.

**Project Structure:** 📁 LigoLAN_Projekt/  
├── 📄 Ligo.py (Entry Point)  
├── 📄 config.py (Constants & Translations)  
├── 📁 core/ (App Brain - System Utils & File Manager)  
├── 📁 network/ (Network Layer - UDP, TCP transfer, Voice Chat)  
├── 📁 gui/ (Graphical Interface & Tabs)  
└── 📁 icons/ (Assets, Icons & Sounds)  

## 🤝 Support the Author
If this tool saved your LAN party or your sanity, I'd highly appreciate any support for further development.

* ☕ **Ko-fi:** [Support via Ko-fi (Card / PayPal)](https://ko-fi.com/goodgames88)
* **BTC:** `bc1qw8utm3daspa5qvnnxc8eznvdtc7xpa8stjndp5`
* **ETH:** `0x7E453349678ea7e164c2A2e78D2590815F7FB9c8`
* **LTC:** `LRaTRP4sGGJQXJ1CZpkjovpYNRHZCZFoUq`

### 👨‍💻 Author & Contacts
**Radek Straka**
* 📺 [YouTube Channel](https://youtube.com/@radekstraka3045)
* 📸 [Instagram (@3d_craft88cz)](https://instagram.com/3d_craft88cz)

This software is provided free of charge "as is", without any warranties. The author is not liable for any damages or data loss resulting from its use. MIT licence

**🔨 For Developers (How to compile):** To create a standalone, super-fast `.exe` file from this source code via Nuitka, use the following terminal command:
```bash
python -m nuitka --standalone --windows-console-mode=disable --plugin-enable=tk-inter --lto=yes --include-package=tkinterdnd2 --windows-icon-from-ico=icons\ikona.ico --include-data-dir=icons=icons --output-dir=Build_Ligo Ligo.pypython -m nuitka --standalone --windows-console-mode=disable --plugin-enable=tk-inter --lto=yes --include-package=tkinterdnd2 --windows-icon-from-ico=icons\ikona.ico --include-data-dir=icons=icons --output-dir=Build_Ligo Ligo.py
```
<img width="1019" height="1040" alt="3" src="https://github.com/user-attachments/assets/5e0cceb9-94e2-4d4c-bc99-d5d876749dab" />

<img width="1019" height="1040" alt="4" src="https://github.com/user-attachments/assets/cea94fd9-22c5-406b-bf47-d55be6e384fb" />
