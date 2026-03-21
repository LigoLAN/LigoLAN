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
**Definitivní švýcarský nůž pro každou LAN párty.**

Vytvořeno hráčem pro hráče. NexusLAN je open-source nástroj navržený tak, aby eliminoval veškerou frustraci spojenou s nastavováním lokální sítě (LAN). Už žádné zbytečné hodiny strávené řešením konfliktů IP adres, ručním propichováním Windows Firewallu nebo hledáním volné flashky pro přenos souborů.

Nainstaluj, spusť a hraj. O zbytek se postará Nexus.

---

## ✨ Hlavní funkce

*   🛡️ **Chytrý Firewall & IP Management:** Aplikace automaticky (s právy správce) detekuje tvé připojení, přidělí bezpečnou lokální IP adresu a otevře potřebné porty ve Windows Firewallu. Při ukončení po sobě umí perfektně uklidit.
*   📡 **Herní Radar (UDP Broadcast):** Automaticky skenuje síť a detekuje běžící hry ostatních hráčů (podpora pro desítky klasik jako Warcraft 3, CS 1.6, Age of Empires, Minecraft a další).
*   📁 **Bleskové sdílení souborů (TCP):** Posílej soubory i celé složky (automatické balení do ZIPu) rychlostí, kterou ti dovolí tvůj kabel. Žádné složité nastavování sdílení ve Windows.
*   💬 **Integrovaný Chat & Voice Squad:** Textový lokální chat pro domluvu a privátní šifrovaný hlasový kanál (UDP) s vybranými hráči přímo přes aplikaci.
*   🔄 **Automatické aktualizace:** Program si sám dokáže sáhnout na GitHub a upozornit uživatele na novou verzi.

---

## 🛠️ Instalace a Použití

1. Přejdi do sekce [Releases](../../releases/latest) a stáhni si nejnovější instalační soubor `NexusLAN_Setup.exe`.
2. Nainstaluj program (vyžaduje Windows 10 / 11).
3. Spusť **NexusLAN**. Při prvním nastavení sítě si program vyžádá **práva správce** (UAC) – to je nezbytné pro úpravu IP adres a Firewallu.
4. *Bezpečnostní upozornění:* Program automaticky otevírá porty `12345`, `12346` a `12347` pro lokální komunikaci. Doporučujeme používat primárně v bezpečné domácí / privátní síti.

---

## 💻 Technologie pod kapotou

NexusLAN je napsaný kompletně v Pythonu s důrazem na asynchronní síťovou komunikaci a stabilitu:
*   **GUI:** `customtkinter` (moderní a responzivní rozhraní), `tkinterdnd2` (Drag & Drop podpora).
*   **Sítě:** Nativní knihovna `socket` (TCP pro soubory, UDP pro radar a chat).
*   **Audio:** `PyAudio` pro nízkolatenční přenos hlasu na LAN síti.
*   **Kompilace & Distribuce:** Zdrojový kód je zkompilovaný přes `Nuitka` pro maximální rychlost a zabalený do profesionálního instalátoru pomocí `Inno Setup`.

---

## 🤝 Podpora autora

Pokud ti tento nástroj zachránil LAN párty nebo ušetřil nervy, budu vděčný za jakoukoliv podporu dalšího vývoje! 🍻

*   ☕ **Ko-fi:** [Podpořit přes Ko-fi (Karta / PayPal)](https://ko-fi.com/goodgames88)
*   **BTC:** `bc1qw8utm3daspa5qvnnxc8eznvdtc7xpa8stjndp5`
*   **ETH:** `0x7E453349678ea7e164c2A2e78D2590815F7FB9c8`
*   **LTC:** `LRaTRP4sGGJQXJ1CZpkjovpYNRHZCZFoUq`

**Autor:** Radek Straka | [YouTube](https://youtube.com/@radekstraka3045) | [Instagram](https://instagram.com/3d_craft88cz)

---

## 📄 Licence

Tento projekt je licencován pod **MIT License** - viz záložka "O programu" přímo v aplikaci pro plné znění. Je poskytován zdarma a open-source.
