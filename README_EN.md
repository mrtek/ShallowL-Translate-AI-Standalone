<div align="center">
  <img src="SLTAISlogo.png" alt="Logo" width="180"/>

  # ShallowL Translate AI Standalone

  **Powerful, local, and fully private AI translator**
  
  🇬🇧 **English** | [🇷🇺 Русский](README.md)
</div>

## 🚀 About the Project
**ShallowL Translate AI Standalone** is an autonomous high-quality machine translation application that runs entirely locally on your PC. It leverages modern Large Language Models (LLMs) and the `KoboldCPP` engine, ensuring absolute data privacy and translation quality comparable to top online services.

Supports GPUs with 4GB+ VRAM (8GB+ recommended for better quality).

![Program Interface](gui.png)

## ✨ Key Features
* **100% Local:** No cloud APIs, no subscriptions, no data collection. Your text never leaves your computer.
* **Two Translation Modes:**
  * **Fast Mode:** Direct batch translation for maximum speed.
  * **Smart Mode:** Three-stage process with entity extraction, glossary creation, and context-aware translation for superior quality.
* **Model Manager:** Built-in model downloader with progress bar. Choose models based on your GPU (4GB/6GB/8GB+).
* **Smart Prompts:** Built-in translation style editor. Technical docs, literature, games (preserving tags), gender-specific styles.
* **Per-Prompt AI Tuning:** Temperature, Top-P, and Repetition Penalty are configured individually for each prompt.
* **Batch Settings:** Flexible token and line-per-batch configuration with presets for different models.
* **Multi-Format Support:** Directly load `TXT`, `DOCX`, and `PDF` files. Save translations to `TXT` or `DOCX`.
* **Bilingual UI:** Full English and Russian interface support with Dark and Light themes.
* **Smart Hotkeys:** `Ctrl+C/V/A` work flawlessly regardless of keyboard layout.
* **Automatic Cleanup:** Closing the app guarantees complete VRAM clearance.

## 🛠️ Installation and Setup

### Requirements
* OS: Windows 10/11 (64-bit)
* GPU: NVIDIA or AMD (minimum 4GB VRAM, 8GB+ recommended)
> 💡 **Zero External Dependencies:** The application is fully self-contained. **No system-wide Python installation is required**; all necessary components will be downloaded and configured automatically within the project folder.

### Step 1. Installation
1. Download the project to your computer (Code → Download ZIP).
2. Extract the archive to a convenient location.
3. Run `01_install.bat`. It will automatically:
   * Download and configure a portable version of Python 3.12.
   * Install all required libraries (CustomTkinter, PyMuPDF, python-docx, OpenAI, requests).
   * Download the `koboldcpp.exe` engine into the `bin/` folder.
4. Wait for the **"Setup completed successfully!"** message.

### Step 2. Launch
Depending on your graphics card, run the corresponding file:
* For **NVIDIA** GPUs: `02_start_NVIDIA.bat`
* For **AMD** GPUs: `02_start_AMD.bat`

The program will start and begin loading the AI engine.

### Step 3. Download a Model
1. On first launch, you'll see a **"Model not found!"** message.
2. Click the **"🤖 Model Manager"** button.
3. Choose a model based on your GPU:
   * **8GB+ VRAM:** Dolphin Mistral Nemo 12B, Llama 3.1 8B
   * **6GB+ VRAM:** Qwen 2.5 7B, Mistral 7B
   * **4GB+ VRAM:** Llama 3.2 3B, Gemma 2 2B
4. Click **"Download"** and wait for completion.
5. Click **"Use"** to activate the model.
6. The program will automatically restart with the selected model.

### Step 4. Start Translating
After the model loads, you'll see **"✅ AI Engine Ready!"** — you can start translating!

## 📖 Usage

### Basic Translation
1. Click **"Load"** and select a file (TXT/DOCX/PDF) or paste text into the left panel.
2. Select source and target languages.
3. Choose a translation style (Strict, Literary, Technical, etc.).
4. Select mode: **Fast** (speed) or **Smart** (quality).
5. Click **"TRANSLATE"**.
6. The result will appear in the right panel.
7. Click **"Save"** to save the translation.

### Prompt Configuration
1. Click **"📝 Prompts"** to open the editor.
2. Select an existing prompt or create a new one (**"New"**).
3. Configure AI parameters:
   * **Temperature:** 0.1-0.3 for precision, 0.7-1.2 for creativity.
   * **Top-P:** 0.5 for strictness, 0.9-1.0 for diversity.
   * **Penalty:** 1.1-1.2 to avoid repetition.
4. Click **"Save"**.

### Batch Settings
1. Click **"⚡ Batch Settings"**.
2. Adjust parameters or choose a preset:
   * **Quality:** Slow, high quality.
   * **Balanced:** Optimal balance (recommended).
   * **Speed:** Fast, may reduce quality.
   * **Auto:** Automatic settings for current model.
3. Click **"Apply"**.

## 🔧 Project Structure
```
AITranslator/
├── lang/                    # Localization files
│   └── translations.json
├── bin/                     # Executables (created during installation)
│   ├── python/             # Portable Python
│   └── koboldcpp.exe       # AI engine
├── models/                  # AI models (created when downloaded)
├── main.py                  # Main application code
├── icon.ico                 # Application icon
├── SLTAISlogo.png          # Logo
├── gui.png                  # Interface screenshot
├── 01_install.bat          # Installation script
├── 02_start_NVIDIA.bat     # Launch for NVIDIA
├── 02_start_AMD.bat        # Launch for AMD
└── README.md               # Documentation
```

## ❓ FAQ

**Q: The program won't start / crashes**  
A: Ensure you have the latest GPU drivers installed. Check `app.log` for error details.

**Q: Model takes too long to load**  
A: This is normal for large models (7-12GB). First load can take 1-3 minutes depending on disk speed.

**Q: Translation quality is poor**  
A: Try:
- Switch to Smart mode
- Choose a different prompt style
- Adjust AI parameters (lower Temperature for precision)
- Use a higher-quality model

**Q: Can I use my own models?**  
A: Yes, place a GGUF file in the `models/` folder and select it via Model Manager.

**Q: The program uses too much VRAM**  
A: Choose a smaller model (Q2_K/Q3_K quantization) or a model with fewer parameters (3B instead of 7B).

## 📝 License
This project is provided "as is" under the MIT License. Feel free to modify the code to suit your needs.

## 🤝 Acknowledgments
* [KoboldCPP](https://github.com/LostRuins/koboldcpp) - AI engine
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - UI framework
* HuggingFace community for providing models

---

<div align="center">
  Made with ❤️ for privacy-conscious translators
</div>