## Hi there 👋

<!--
# 🚀 LigoLAN
**Your personal network admin for hassle-free LAN gaming.**

*💬 I would be incredibly grateful for any feedback, bug reports, or ideas for new features! If you find this tool helpful or run into any issues, please feel free to open an Issue here on GitHub or reach out directly. Let's make LAN parties great again together!*

Created by a gamer for gamers. LigoLAN is an open-source tool designed to eliminate all the frustration associated with setting up a local area network (LAN). No more wasted hours resolving IP address conflicts, manually poking holes in the Windows Firewall, or searching for a free USB flash drive to transfer files.

Install, run, and play. LigoLAN handles the rest.

## ✨ Key Features
*   🛡️ **Smart Firewall & IP Management:** The application automatically (with admin rights) detects your connection, assigns a safe local IP address, and opens the necessary ports in the Windows Firewall. It perfectly cleans up after itself upon exit.
*   📡 **Game Radar (UDP Broadcast):** Automatically scans the network and detects running games of other players (supports dozens of classics like Warcraft 3, CS 1.6, Age of Empires, Minecraft, and more).
*   📁 **Lightning-fast File Sharing (TCP):** Send files and entire folders (automatic ZIP packing) at the maximum speed your cable allows. No complex Windows sharing setup required.
*   💬 **Integrated Chat & Voice Squad:** Local text chat for coordination and a private, encrypted voice channel (UDP) with selected players directly through the app.
*   🔄 **Automatic Updates:** The program checks GitHub on its own and notifies the user if a new version is available.

## 🛠️ Installation and Usage
1. Go to the **Releases** section on the right side of this page and download the latest **LigoLAN_Setup.exe** installer.
2. Install the program (Windows 10 / 11 required).
3. Run LigoLAN. During the initial network setup, the program will request **administrator rights** (UAC) – this is necessary to modify IP addresses and the Firewall.

> **⚠️ Security Warning:** The program automatically opens ports `12345`, `12346`, and `12347` for local communication. We recommend using it primarily on a trusted home / private network.

## 💻 Technology Under the Hood
LigoLAN is written entirely in Python with a focus on asynchronous network communication and stability:
*   **GUI:** `customtkinter` (modern and responsive interface), `tkinterdnd2` (Drag & Drop support).
*   **Networking:** Native `socket` library (TCP for files, UDP for radar and chat).
*   **Audio:** `PyAudio` for low-latency voice transmission over LAN.
*   **Compilation:** The source code is compiled via **Nuitka** for maximum speed and packaged into a professional installer using Inno Setup.

### 👨‍💻 For Developers (How to compile)
If you want to compile the project from source code yourself, make sure you have all required assets (`pozadi.jpg`, `ikona.ico`, `doom.wav`) in the same folder and run this Nuitka command:
```cmd
python -m nuitka --standalone --windows-console-mode=disable --plugin-enable=tk-inter --windows-icon-from-ico=ikona.ico --include-data-files=ikona.ico=ikona.ico --include-data-files=pozadi.jpg=pozadi.jpg --include-data-files=doom.wav=doom.wav Ligo.py
🤝 Support the Author
If this tool saved your LAN party or your sanity, I'd highly appreciate any support for further development! 🍻

☕ Ko-fi: Support via Ko-fi (Card / PayPal)

BTC: bc1qw8utm3daspa5qvnnxc8eznvdtc7xpa8stjndp5

ETH: 0x7E453349678ea7e164c2A2e78D2590815F7FB9c8

LTC: LRaTRP4sGGJQXJ1CZpkjovpYNRHZCZFoUq

Author: Radek Straka | YouTube | Instagram

📄 License
This project is licensed under the MIT License - see the "About" tab directly in the application for the full text. It is provided free of charge and open-source.
