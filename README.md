## Hi there 👋

<!--
**NexusLAN/NexusLAN** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
--># 🚀 NexusLAN v1.0
**The definitive Swiss Army knife for every LAN party.**

Created by a gamer for gamers. NexusLAN is an open-source tool designed to eliminate all the frustration associated with setting up a local area network (LAN). No more wasted hours resolving IP address conflicts, manually poking holes in the Windows Firewall, or searching for a free USB flash drive to transfer files.

Install, run, and play. Nexus handles the rest.

---

## ✨ Key Features

*   🛡️ **Smart Firewall & IP Management:** The application automatically (with admin rights) detects your connection, assigns a safe local IP address, and opens the necessary ports in the Windows Firewall. It perfectly cleans up after itself upon exit.
*   📡 **Game Radar (UDP Broadcast):** Automatically scans the network and detects running games of other players (supports dozens of classics like Warcraft 3, CS 1.6, Age of Empires, Minecraft, and more).
*   📁 **Lightning-fast File Sharing (TCP):** Send files and entire folders (automatic ZIP packing) at the maximum speed your cable allows. No complex Windows sharing setup required.
*   💬 **Integrated Chat & Voice Squad:** Local text chat for coordination and a private, encrypted voice channel (UDP) with selected players directly through the app.
*   🔄 **Automatic Updates:** The program checks GitHub on its own and notifies the user if a new version is available.

---

## 🛠️ Installation and Usage

1. Go to the [Releases](../../releases/latest) section and download the latest `NexusLAN_Setup.exe` installer.
2. Install the program (Windows 10 / 11 required).
3. Run **NexusLAN**. During the initial network setup, the program will request **administrator rights** (UAC) – this is necessary to modify IP addresses and the Firewall.
4. *Security Warning:* The program automatically opens ports `12345`, `12346`, and `12347` for local communication. We recommend using it primarily on a trusted home / private network.

---

## 💻 Technology Under the Hood

NexusLAN is written entirely in Python with a focus on asynchronous network communication and stability:
*   **GUI:** `customtkinter` (modern and responsive interface), `tkinterdnd2` (Drag & Drop support).
*   **Networking:** Native `socket` library (TCP for files, UDP for radar and chat).
*   **Audio:** `PyAudio` for low-latency voice transmission over LAN.
*   **Compilation & Distribution:** The source code is compiled via `Nuitka` for maximum speed and packaged into a professional installer using `Inno Setup`.

---

## 🤝 Support the Author

If this tool saved your LAN party or your sanity, I'd highly appreciate any support for further development! 🍻

*   ☕ **Ko-fi:** [Support via Ko-fi (Card / PayPal)](https://ko-fi.com/goodgames88)
*   **BTC:** `bc1qw8utm3daspa5qvnnxc8eznvdtc7xpa8stjndp5`
*   **ETH:** `0x7E453349678ea7e164c2A2e78D2590815F7FB9c8`
*   **LTC:** `LRaTRP4sGGJQXJ1CZpkjovpYNRHZCZFoUq`

**Author:** Radek Straka | [YouTube](https://youtube.com/@radekstraka3045) | [Instagram](https://instagram.com/3d_craft88cz)

---

## 📄 License

This project is licensed under the **MIT License** - see the "About" tab directly in the application for the full text. It is provided free of charge and open-source.
