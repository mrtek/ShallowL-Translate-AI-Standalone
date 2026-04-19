import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import ctypes
import sys
import argparse
import re
import json
import queue
import subprocess
import time
import requests
import docx
import fitz  # PyMuPDF
from openai import OpenAI

# --- Константы ---
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PROMPTS_FILE = os.path.join(BASE_PATH, "prompts.json")
CONFIG_FILE = os.path.join(BASE_PATH, "config.json")
SUPPORTED_LANGS = ["English", "Russian", "German", "French", "Spanish", "Italian", "Chinese", "Japanese"]

DEFAULT_PROMPTS = {
    "Строгий / Strict": {"text": "You are a professional native {target} translator. Translate from {source} to {target} with maximum accuracy. Output ONLY the translation.", "temp": 0.1, "top_p": 0.9, "penalty": 1.1},
    "Литературный / Literary": {"text": "You are a creative writer. Translate from {source} to {target} beautifully, adapting metaphors. Output ONLY the translation.", "temp": 0.7, "top_p": 0.95, "penalty": 1.15},
    "Технический / Technical": {"text": "You are a technical expert. Translate using precise professional terminology. Output ONLY the translation.", "temp": 0.1, "top_p": 0.5, "penalty": 1.1},
    "От женского лица / Female Speaker": {"text": "You are translating from {source} to {target}. The speaker is FEMALE. Use feminine gender endings (e.g. 'Я пошла'). Output ONLY the translation.", "temp": 0.3, "top_p": 0.9, "penalty": 1.1},
    "От мужского лица / Male Speaker": {"text": "You are translating from {source} to {target}. The speaker is MALE. Use masculine gender endings (e.g. 'Я пошел'). Output ONLY the translation.", "temp": 0.3, "top_p": 0.9, "penalty": 1.1},
    "Перевод игр / Game Localization": {"text": "You are a game localizer translating from {source} to {target}. Preserve all tags, placeholders (like {0}, %s), and special symbols. Keep the tone engaging. Output ONLY the translation.", "temp": 0.4, "top_p": 0.9, "penalty": 1.15}
}

DEFAULT_CONFIG = {"theme": "dark", "lang": "RU"}

UI_LANGS = {
    "EN": {
        "title": "ShallowL Translate AI Standalone", "load": "📂 Load File", "save": "💾 Save",
        "translate": "▶ TRANSLATE", "stop": "⏹ STOP", "style": "Translation Style:",
        "prompts": "⚙ Prompts", "ai_info": "🛠 AI Info",
        "wait": "Waiting for AI engine loading... / Ждите загрузки ИИ ядра...",
        "ready": "AI Engine Ready! / Нейросеть готова к работе!",
        "done": "Translation completed! / Перевод завершен!"
    },
    "RU": {
        "title": "ShallowL Translate AI Standalone", "load": "📂 Загрузить файл", "save": "💾 Сохранить",
        "translate": "▶ ПЕРЕВЕСТИ", "stop": "⏹ ОСТАНОВИТЬ", "style": "Стиль перевода:",
        "prompts": "⚙ Настройки промптов", "ai_info": "🛠 Справка по ИИ",
        "wait": "Ждите загрузки ИИ ядра... / Waiting for AI engine loading...",
        "ready": "Нейросеть готова к работе! / AI Engine Ready!",
        "done": "Перевод завершен! / Translation completed!"
    }
}

# --- Умный Редактор Промптов ---
class PromptManager(ctk.CTkToplevel):
    def __init__(self, parent, prompts, save_callback):
        super().__init__(parent)
        self.title("⚙ Редактор промптов / Prompt Editor"); self.geometry("800x600"); self.attributes("-topmost", True)
        self.prompts, self.save_callback = prompts, save_callback
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        
        self.list_frame = ctk.CTkFrame(self, width=200)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.listbox = tk.Listbox(self.list_frame, bg="#2b2b2b", fg="white", font=("Arial", 11), borderwidth=0, selectbackground="#1f538d")
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.edit_frame = ctk.CTkFrame(self)
        self.edit_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.name_entry = ctk.CTkEntry(self.edit_frame, placeholder_text="Название / Name", font=("Arial", 14, "bold"))
        self.name_entry.pack(fill="x", padx=10, pady=(10, 5))
        self.text_editor = ctk.CTkTextbox(self.edit_frame, height=120)
        self.text_editor.pack(fill="both", expand=True, padx=10, pady=5)

        sliders_frame = ctk.CTkFrame(self.edit_frame, fg_color="transparent")
        sliders_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(sliders_frame, text="Температура / Temperature (0.1 - 1.2):", font=("Arial", 11)).pack(anchor="w")
        self.s_temp = ctk.CTkSlider(sliders_frame, from_=0.1, to=1.2, command=lambda v: self.l_temp.configure(text=f"{v:.2f}"))
        self.s_temp.pack(fill="x", pady=2); self.l_temp = ctk.CTkLabel(sliders_frame, text="0.2"); self.l_temp.pack()
        
        ctk.CTkLabel(sliders_frame, text="Top-P (0.1 - 1.0):", font=("Arial", 11)).pack(anchor="w")
        self.s_top = ctk.CTkSlider(sliders_frame, from_=0.1, to=1.0, command=lambda v: self.l_top.configure(text=f"{v:.2f}"))
        self.s_top.pack(fill="x", pady=2); self.l_top = ctk.CTkLabel(sliders_frame, text="0.9"); self.l_top.pack()
        
        ctk.CTkLabel(sliders_frame, text="Штраф / Penalty (1.0 - 1.5):", font=("Arial", 11)).pack(anchor="w")
        self.s_pen = ctk.CTkSlider(sliders_frame, from_=1.0, to=1.5, command=lambda v: self.l_pen.configure(text=f"{v:.2f}"))
        self.s_pen.pack(fill="x", pady=2); self.l_pen = ctk.CTkLabel(sliders_frame, text="1.1"); self.l_pen.pack()

        btn_row = ctk.CTkFrame(self.edit_frame, fg_color="transparent"); btn_row.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btn_row, text="➕ New", width=90, command=self.add_p).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="❌ Delete", width=90, fg_color="#dc3545", command=self.del_p).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="💾 Save", width=120, fg_color="#28a745", command=self.save_p).pack(side="right", padx=5)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end"); [self.listbox.insert("end", name) for name in self.prompts]
    def on_select(self, e):
        if not self.listbox.curselection(): return
        name = self.listbox.get(self.listbox.curselection())
        p_data = self.prompts[name]
        self.name_entry.delete(0, "end"); self.name_entry.insert(0, name)
        self.text_editor.delete("1.0", "end"); self.text_editor.insert("end", p_data["text"])
        self.s_temp.set(p_data["temp"]); self.l_temp.configure(text=f'{p_data["temp"]:.2f}')
        self.s_top.set(p_data["top_p"]); self.l_top.configure(text=f'{p_data["top_p"]:.2f}')
        self.s_pen.set(p_data["penalty"]); self.l_pen.configure(text=f'{p_data["penalty"]:.2f}')
    def add_p(self):
        self.name_entry.delete(0, "end"); self.name_entry.insert(0, "New Prompt")
        self.text_editor.delete("1.0", "end")
        self.s_temp.set(0.2); self.l_temp.configure(text="0.20")
        self.s_top.set(0.9); self.l_top.configure(text="0.90")
        self.s_pen.set(1.1); self.l_pen.configure(text="1.10")
    def del_p(self):
        name = self.name_entry.get()
        if name in self.prompts: del self.prompts[name]; self.save_callback(); self.refresh()
    def save_p(self):
        n, t = self.name_entry.get().strip(), self.text_editor.get("1.0", "end").strip()
        if n and t: 
            self.prompts[n] = {"text": t, "temp": round(float(self.s_temp.get()), 2), "top_p": round(float(self.s_top.get()), 2), "penalty": round(float(self.s_pen.get()), 2)}
            self.save_callback(); self.refresh()

# --- Главное приложение ---
class TranslatorApp(ctk.CTk):
    def __init__(self, model_path, gpu_layers, engine):
        super().__init__()
        self.model_path, self.gpu_layers, self.engine = model_path, gpu_layers, engine
        self.client, self.engine_proc = None, None
        self.is_translating = False
        
        self.config_ai = self.load_json(CONFIG_FILE, DEFAULT_CONFIG)
        self.ui_lang = self.config_ai.get("lang", "RU")
        self.load_and_migrate_prompts()
        
        self.title("ShallowL Translate AI Standalone")
        self.geometry("1300x850")
        ctk.set_appearance_mode(self.config_ai.get("theme", "dark"))
        
        icon_path = os.path.join(BASE_PATH, "icon.ico")
        if os.path.exists(icon_path): self.iconbitmap(icon_path)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_ui()
        self.apply_ui_lang()
        
        self.bind_all("<Control-KeyPress>", self._smart_hotkey_handler)
        self.lock_ui(True) 
        
        self.ui_queue = queue.Queue(); self.process_queue()
        self.ai_task_queue = queue.Queue()
        threading.Thread(target=self.ai_thread_loop, daemon=True).start()

    def load_and_migrate_prompts(self):
        raw_prompts = self.load_json(PROMPTS_FILE, DEFAULT_PROMPTS)
        self.prompts = {}
        migrated = False
        for k, v in raw_prompts.items():
            if isinstance(v, str): 
                if k in DEFAULT_PROMPTS: self.prompts[k] = DEFAULT_PROMPTS[k]
                else: self.prompts[k] = {"text": v, "temp": 0.2, "top_p": 0.9, "penalty": 1.1}
                migrated = True
            else: self.prompts[k] = v
        if migrated: self.save_json(PROMPTS_FILE, self.prompts)

    def _smart_hotkey_handler(self, event):
        if event.keysym.lower() in ['c', 'v', 'x', 'a']: return
        kc = event.keycode; widget = event.widget
        try:
            if kc == 67: widget.event_generate("<<Copy>>"); return "break"
            elif kc == 86: widget.event_generate("<<Paste>>"); return "break"
            elif kc == 88: widget.event_generate("<<Cut>>"); return "break"
            elif kc == 65: 
                if hasattr(widget, "tag_add"): widget.tag_add("sel", "1.0", "end")
                elif hasattr(widget, "select_range"): widget.select_range(0, "end"); widget.icursor("end")
                return "break"
        except Exception: pass

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=10)
        top_bar.grid_columnconfigure(0, weight=1); top_bar.grid_columnconfigure(1, weight=1)

        ltop = ctk.CTkFrame(top_bar, fg_color="transparent")
        ltop.grid(row=0, column=0, sticky="ew", padx=(0,5))
        self.btn_load = ctk.CTkButton(ltop, text="Load", width=160, command=self.load_file)
        self.btn_load.pack(side="left")
        self.combo_src = ctk.CTkComboBox(ltop, values=SUPPORTED_LANGS, width=150)
        self.combo_src.set("English"); self.combo_src.pack(side="right")

        rtop = ctk.CTkFrame(top_bar, fg_color="transparent")
        rtop.grid(row=0, column=1, sticky="ew", padx=(5,0))
        self.combo_tgt = ctk.CTkComboBox(rtop, values=SUPPORTED_LANGS, width=150)
        self.combo_tgt.set("Russian"); self.combo_tgt.pack(side="left")
        self.btn_save = ctk.CTkButton(rtop, text="Save", width=160, command=self.save_file)
        self.btn_save.pack(side="right")

        self.text_l = ctk.CTkTextbox(self, font=("Arial", 14), wrap="word", border_width=1)
        self.text_l.grid(row=1, column=0, padx=(15, 5), pady=5, sticky="nsew")
        self.text_r = ctk.CTkTextbox(self, font=("Arial", 14), wrap="word", border_width=1)
        self.text_r.grid(row=1, column=1, padx=(5, 15), pady=5, sticky="nsew")

        ctrl_bar = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
        self.btn_go = ctk.CTkButton(ctrl_bar, text="▶ TRANSLATE", fg_color="#28a745", font=("Arial", 14, "bold"), height=45, command=self.start_trans)
        self.btn_go.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.btn_stop = ctk.CTkButton(ctrl_bar, text="⏹ STOP", fg_color="#dc3545", font=("Arial", 14, "bold"), height=45, state="disabled", command=self.stop_trans)
        self.btn_stop.pack(side="right", fill="x", expand=True, padx=(5,0))

        bottom_row = ctk.CTkFrame(self, fg_color="transparent")
        bottom_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 15))
        
        # Левый блок настроек интерфейса
        left_ui_settings = ctk.CTkFrame(bottom_row, fg_color="transparent")
        left_ui_settings.pack(side="left", anchor="s", padx=(0, 15))
        
        ctk.CTkLabel(left_ui_settings, text="UI Lang:", font=("Arial", 10)).pack(anchor="w")
        self.ui_lang_btn = ctk.CTkSegmentedButton(left_ui_settings, values=["EN", "RU"], width=80, command=self.change_ui_lang)
        self.ui_lang_btn.set(self.ui_lang); self.ui_lang_btn.pack(pady=(0, 8))

        ctk.CTkLabel(left_ui_settings, text="Theme:", font=("Arial", 10)).pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.config_ai["theme"].capitalize())
        ctk.CTkRadioButton(left_ui_settings, text="Dark", variable=self.theme_var, value="Dark", command=self.change_theme).pack(pady=4, anchor="w")
        ctk.CTkRadioButton(left_ui_settings, text="Light", variable=self.theme_var, value="Light", command=self.change_theme).pack(pady=4, anchor="w")

        # Динамический цвет консоли
        self.log_a = ctk.CTkTextbox(bottom_row, height=120, fg_color=("#e8e8e8", "#1e1e1e"), text_color=("#000000", "#00ff00"), state="disabled")
        self.log_a.pack(side="left", fill="both", expand=True)

        # Правый блок управления ИИ
        side_panel = ctk.CTkFrame(bottom_row, width=300)
        side_panel.pack(side="right", fill="y", padx=(15, 0))
        self.lbl_style = ctk.CTkLabel(side_panel, text="Style / Стиль:", font=("Arial", 12, "bold"))
        self.lbl_style.pack(pady=(15,0))
        self.combo_p = ctk.CTkComboBox(side_panel, values=list(self.prompts.keys()), width=240)
        self.combo_p.set(list(self.prompts.keys())[0]); self.combo_p.pack(pady=5)
        
        b_row = ctk.CTkFrame(side_panel, fg_color="transparent"); b_row.pack(pady=5)
        self.btn_pr = ctk.CTkButton(b_row, text="Prompts", width=110, command=self.open_prompts)
        self.btn_pr.pack(side="left", padx=3)
        self.btn_info = ctk.CTkButton(b_row, text="AI Info", width=110, command=self.open_ai_info)
        self.btn_info.pack(side="left", padx=3)

    def apply_ui_lang(self):
        u = UI_LANGS[self.ui_lang]
        self.title(u["title"])
        self.btn_load.configure(text=u["load"])
        self.btn_save.configure(text=u["save"])
        self.btn_go.configure(text=u["translate"])
        self.btn_stop.configure(text=u["stop"])
        self.lbl_style.configure(text=u["style"])
        self.btn_pr.configure(text=u["prompts"])
        self.btn_info.configure(text=u["ai_info"])

    def change_ui_lang(self, lang):
        self.ui_lang = lang
        self.config_ai["lang"] = lang
        self.save_json(CONFIG_FILE, self.config_ai)
        self.apply_ui_lang()

    def change_theme(self):
        t = self.theme_var.get().lower(); self.config_ai["theme"] = t; ctk.set_appearance_mode(t)
        self.save_json(CONFIG_FILE, self.config_ai)

    def lock_ui(self, lock):
        s = "disabled" if lock else "normal"
        for w in [self.btn_load, self.btn_save, self.btn_go, self.combo_src, self.combo_tgt, self.combo_p, self.btn_pr, self.btn_info]:
            if w: w.configure(state=s)

    def load_file(self):
        p = filedialog.askopenfilename(filetypes=[("Documents", "*.docx *.pdf *.txt")])
        if not p: return
        self.text_l.delete("1.0", "end"); ext = os.path.splitext(p)[1].lower()
        try:
            if ext == ".docx":
                doc = docx.Document(p); self.text_l.insert("end", "\n".join([pa.text for pa in doc.paragraphs]))
            elif ext == ".pdf":
                with fitz.open(p) as d: self.text_l.insert("end", "\n".join([pg.get_text() for pg in d]))
            else:
                with open(p, 'r', encoding='utf-8') as f: self.text_l.insert("end", f.read())
        except Exception as e: messagebox.showerror("Error", str(e))

    def save_file(self):
        # Оставили только TXT и DOCX
        p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt"), ("Word", "*.docx")])
        if not p: return
        txt = self.text_r.get("1.0", "end").strip(); ext = os.path.splitext(p)[1].lower()
        try:
            if ext == ".docx":
                d = docx.Document(); d.add_paragraph(txt); d.save(p)
            else:
                with open(p, 'w', encoding='utf-8') as f: f.write(txt)
        except Exception as e: messagebox.showerror("Error", str(e))

    def start_engine(self):
        self.log(UI_LANGS[self.ui_lang]["wait"])
        exe = os.path.join(BASE_PATH, "bin", "koboldcpp.exe")
        model = os.path.join(BASE_PATH, self.model_path)
        cmd = [exe, "--model", model, "--gpulayers", str(self.gpu_layers), "--port", "5001", "--quiet", "--nommap"]
        cmd.append("--usecublas" if self.engine == "cuda" else "--usevulkan")
        try:
            self.engine_proc = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        except: return False
        for _ in range(120):
            try:
                if requests.get("http://127.0.0.1:5001/api/v1/model", timeout=1).status_code == 200:
                    self.client = OpenAI(base_url="http://127.0.0.1:5001/v1", api_key="sk-123")
                    self.log(UI_LANGS[self.ui_lang]["ready"]); self.lock_ui(False)
                    try:
                        h = ctypes.WinDLL('kernel32').GetConsoleWindow()
                        if h != 0: ctypes.WinDLL('user32').ShowWindow(h, 0)
                    except: pass
                    return True
            except: time.sleep(1)
        return False

    def ai_thread_loop(self):
        if not self.start_engine(): return
        while True:
            t = self.ai_task_queue.get()
            if t: self._do_translation(*t)

    def _do_translation(self, text, src, tgt, p_name):
        p_data = self.prompts.get(p_name, DEFAULT_PROMPTS["Строгий / Strict"])
        sys_p = p_data["text"].replace("{source}", src).replace("{target}", tgt)
        t_temp, t_top, t_pen = p_data.get("temp", 0.2), p_data.get("top_p", 0.9), max(0.0, p_data.get("penalty", 1.1) - 1.0) 

        for p in text.split("\n"):
            if not self.is_translating: break
            if not p.strip(): self.ui_queue.put(("text", "\n")); continue
            
            if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', p):
                self.ui_queue.put(("text", p + "\n"))
                continue

            try:
                resp = self.client.chat.completions.create(
                    model="local", messages=[{"role":"system","content":sys_p},{"role":"user","content":f"Translate to {tgt}: {p}"}],
                    temperature=t_temp, top_p=t_top, presence_penalty=t_pen, stream=True
                )
                for c in resp:
                    if not self.is_translating: break
                    if c.choices[0].delta.content: self.ui_queue.put(("text", c.choices[0].delta.content))
                self.ui_queue.put(("text", "\n"))
            except: break
        self.is_translating = False
        self.ui_queue.put(("btn_state", "stopped")); self.log(UI_LANGS[self.ui_lang]["done"])

    def process_queue(self):
        try:
            while True:
                m, d = self.ui_queue.get_nowait()
                if m == "text": self.text_r.insert("end", d); self.text_r.see("end")
                elif m == "log": 
                    self.log_a.configure(state="normal"); self.log_a.delete("1.0", "end")
                    self.log_a.insert("end", d); self.log_a.configure(state="disabled")
                elif m == "btn_state":
                    if d == "translating": self.btn_go.configure(state="disabled"); self.btn_stop.configure(state="normal")
                    else: self.btn_go.configure(state="normal"); self.btn_stop.configure(state="disabled")
                elif m == "clear": self.text_r.delete("1.0", "end")
        except: pass
        self.after(50, self.process_queue)

    def log(self, m): self.ui_queue.put(("log", m))
    def load_json(self, f, d):
        try:
            if not os.path.exists(f): 
                with open(f, 'w', encoding='utf-8') as file: json.dump(d, file, indent=4, ensure_ascii=False); return d
            with open(f, 'r', encoding='utf-8') as file: return json.load(file)
        except: return d
    def save_json(self, f, d):
        with open(f, 'w', encoding='utf-8') as file: json.dump(d, file, indent=4, ensure_ascii=False)
        
    def start_trans(self):
        txt = self.text_l.get("1.0", "end").strip()
        if txt and self.client:
            self.is_translating = True
            self.ui_queue.put(("btn_state", "translating")); self.ui_queue.put(("clear", ""))
            self.ai_task_queue.put((txt, self.combo_src.get(), self.combo_tgt.get(), self.combo_p.get()))
            
    def stop_trans(self): self.is_translating = False
    def open_prompts(self): PromptManager(self, self.prompts, lambda: self.save_json(PROMPTS_FILE, self.prompts))
    
    def open_ai_info(self):
        sw = ctk.CTkToplevel(self); sw.title("AI Info / Справка"); sw.geometry("600x450"); sw.attributes("-topmost", True)
        info = (
            "ENG:\n"
            "🌡 Temp: Controls creativity. (0.1 - strict, 0.9 - creative).\n"
            "🎯 Top-P: Vocabulary limit. (0.5 - basic words, 1.0 - all words).\n"
            "♻ Penalty: Prevents word repetition. (1.0 - off, 1.2 - strong).\n\n"
            "RUS:\n"
            "Настройки ИИ привязаны к каждому Промпту индивидуально.\n"
            "🌡 Температура (Temp): Управляет креативностью.\n"
            "• 0.1: ИИ выбирает самые точные слова. Идеально для тех. перевода.\n"
            "• 0.9: ИИ подбирает синонимы, делает текст литературным.\n\n"
            "🎯 Top-P: Ограничивает словарный запас.\n"
            "• 0.5: Отбрасываются редкие слова. Текст строгий.\n"
            "• 1.0: Используется весь лексикон.\n\n"
            "♻ Штраф за повторы (Penalty): Запрещает зацикливаться на словах.\n"
            "• 1.0: Выключен.\n"
            "• 1.15: Золотая середина.\n"
            "• 1.2+: ИИ начнет портить текст, лишь бы не повторять слова."
        )
        lbl = ctk.CTkLabel(sw, text=info, justify="left", font=("Arial", 13), wraplength=550)
        lbl.pack(padx=20, pady=20, fill="both", expand=True)
        ctk.CTkButton(sw, text="OK", command=sw.destroy).pack(pady=10)

    def on_closing(self):
        if self.engine_proc:
            try: self.engine_proc.terminate()
            except: pass
        if os.name == 'nt': os.system("taskkill /f /im koboldcpp.exe >nul 2>&1")
        self.destroy(); os._exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="models/dolphin-2.9.3-mistral-nemo-12b.Q4_K_M.gguf")
    parser.add_argument("--gpu-layers", type=int, default=99); parser.add_argument("--engine", type=str, default="cuda")
    args = parser.parse_args(); app = TranslatorApp(args.model, args.gpu_layers, args.engine); app.mainloop()