<div align="center">
  <img src="SLTAISlogo.png" alt="Logo" width="180"/>

  # ShallowL Translate AI Standalone

  **Powerful, local, and fully private AI translator**
  
  🇬🇧 **English** | [🇷🇺 Русский](README.md)
</div>

## 🚀 About the Project
**ShallowL Translate AI Standalone** is an autonomous high-quality machine translation application that runs entirely locally on your PC. It leverages the power of the `Dolphin 12B (Mistral Nemo)` neural network and the `KoboldCPP` engine, ensuring absolute data privacy and translation quality comparable to top online services.

Optimized for users with 8GB+ VRAM GPUs (12-16GB recommended).

![Program Interface](gui.png)

## ✨ Key Features
* **100% Local:** No cloud APIs, no subscriptions, no data collection. Your text never leaves your computer.
* **Smart Prompts:** Built-in style editor. Translate technical manuals, literature, games (preserving tags), or use cyberpunk slang.
* **Per-Prompt AI Tuning:** Temperature, Top-P, and Repetition Penalty are saved individually for each prompt for maximum flexibility.
* **Multi-Format Support:** Directly load `TXT`, `DOCX`, and `PDF` files. Save translations to `TXT` or `DOCX`.
* **Adaptive UI:** Bilingual interface (English/Russian) with Dark and Light themes.
* **Smart Hotkeys:** `Ctrl+C/V/A` work flawlessly regardless of your current keyboard layout.
* **Clean Exit:** Closing the app guarantees complete VRAM clearance by terminating background AI processes.

## 🛠️ Installation and Execution

### Requirements
* OS: Windows 10/11
* Python: 3.12 (or compatible) — [Download from official website](https://www.python.org/downloads/windows/)
  > ⚠️ **IMPORTANT:** During Python installation, make sure to check the **"Add Python 3.x to PATH"** box at the very bottom of the first setup screen! Without it, the app won't be able to build the virtual environment.
* GPU: NVIDIA or AMD (minimum 8GB VRAM)

### Step 1. Installation
1. Download the project to your computer.
2. Run `01_install.bat`. It will automatically:
   * Create an isolated virtual environment.
   * Install all required libraries.
   * Download the `koboldcpp.exe` engine into the `bin/` folder.
   * Download the `Dolphin 12B` model into the `models/` folder.

### Step 2. Running the App
Depending on your graphics card, run the corresponding file:
* For NVIDIA GPUs: `02_start_NVIDIA.bat`
* For AMD GPUs: `02_start_AMD.bat`

Wait for the **"AI Engine Ready!"** message in the console — the UI will unlock automatically.

## 📝 License
This project is provided "as is". Feel free to modify the code to suit your needs.