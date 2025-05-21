import tkinter as tk
from tkinter import ttk, scrolledtext
import pyautogui
import time
import threading
import keyboard
import json
import os
import pyperclip
from pathlib import Path

class AutoTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Language Auto Typer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set app icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
            
        # Variables
        self.typing_active = False
        self.pause_typing = False
        self.current_thread = None
        self.saved_texts = {}
        self.config_file = Path("auto_typer_config.json")
        
        # Load saved texts
        self.load_saved_texts()
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create typing tab
        typing_frame = ttk.Frame(self.notebook)
        self.notebook.add(typing_frame, text="Auto Typer")
        
        # Create saved texts tab
        saved_frame = ttk.Frame(self.notebook)
        self.notebook.add(saved_frame, text="Saved Texts")
        
        # Create settings tab
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Setup typing tab
        self.setup_typing_tab(typing_frame)
        
        # Setup saved texts tab
        self.setup_saved_texts_tab(saved_frame)
        
        # Setup settings tab
        self.setup_settings_tab(settings_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set up hotkeys
        keyboard.add_hotkey('f6', self.start_typing)
        keyboard.add_hotkey('f7', self.toggle_pause)
        keyboard.add_hotkey('f8', self.stop_typing)
        
        # Apply theme
        self.apply_theme()

    def setup_typing_tab(self, parent):
        # Text input area
        input_frame = ttk.LabelFrame(parent, text="Text to Type")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.text_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Options frame
        options_frame = ttk.Frame(parent)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Delay settings
        delay_frame = ttk.LabelFrame(options_frame, text="Typing Settings")
        delay_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(delay_frame, text="Delay before typing (seconds):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.delay_var = tk.StringVar(value="3")
        delay_entry = ttk.Spinbox(delay_frame, from_=1, to=10, textvariable=self.delay_var, width=5)
        delay_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(delay_frame, text="Speed (typing delay in seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.speed_var = tk.StringVar(value="0.05")
        speed_entry = ttk.Spinbox(delay_frame, from_=0.01, to=0.5, increment=0.01, textvariable=self.speed_var, width=5)
        speed_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Save text option
        save_frame = ttk.LabelFrame(options_frame, text="Save Text")
        save_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(save_frame, text="Save as:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.save_name_var = tk.StringVar()
        save_entry = ttk.Entry(save_frame, textvariable=self.save_name_var, width=15)
        save_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        save_btn = ttk.Button(save_frame, text="Save", command=self.save_current_text)
        save_btn.grid(row=0, column=2, padx=5, pady=2)
        
        # Control buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="Start Typing (F6)", command=self.start_typing)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(control_frame, text="Pause/Resume (F7)", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop (F8)", command=self.stop_typing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Add progress bar
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Hotkey info
        hotkey_label = ttk.Label(parent, text="Hotkeys: F6 = Start, F7 = Pause/Resume, F8 = Stop")
        hotkey_label.pack(pady=5)

        # Add language mode selector
        lang_frame = ttk.LabelFrame(options_frame, text="Language Settings")
        lang_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.lang_mode_var = tk.StringVar(value="auto")
        ttk.Radiobutton(lang_frame, text="Auto Detect", variable=self.lang_mode_var, value="auto").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(lang_frame, text="Arabic Mode", variable=self.lang_mode_var, value="arabic").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(lang_frame, text="English Mode", variable=self.lang_mode_var, value="english").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)

        # Add Arabic typing mode selector
        arabic_frame = ttk.LabelFrame(options_frame, text="Arabic Typing Mode")
        arabic_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.arabic_mode_var = tk.StringVar(value="character")
        ttk.Radiobutton(arabic_frame, text="Character by Character", variable=self.arabic_mode_var, value="character").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(arabic_frame, text="Paste Whole Text", variable=self.arabic_mode_var, value="paste").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)

    def setup_saved_texts_tab(self, parent):
        # List of saved texts
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(list_frame, text="Saved Texts:").pack(anchor=tk.W, padx=5, pady=5)
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.saved_list = tk.Listbox(list_container, yscrollcommand=scrollbar.set, height=10)
        self.saved_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.saved_list.yview)
        
        # Update the listbox with saved texts
        self.update_saved_list()
        
        # Buttons for saved texts
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        load_btn = ttk.Button(btn_frame, text="Load Selected", command=self.load_selected_text)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected_text)
        delete_btn.pack(side=tk.LEFT, padx=5)

    def setup_settings_tab(self, parent):
        # Theme settings
        theme_frame = ttk.LabelFrame(parent, text="Appearance")
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.theme_var = tk.StringVar(value="light")
        ttk.Radiobutton(theme_frame, text="Light Theme", variable=self.theme_var, value="light", command=self.apply_theme).pack(anchor=tk.W, padx=20, pady=5)
        ttk.Radiobutton(theme_frame, text="Dark Theme", variable=self.theme_var, value="dark", command=self.apply_theme).pack(anchor=tk.W, padx=20, pady=5)
        
        # Clipboard settings
        clipboard_frame = ttk.LabelFrame(parent, text="Clipboard Settings")
        clipboard_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.clipboard_delay_var = tk.StringVar(value="0.3")
        ttk.Label(clipboard_frame, text="Clipboard delay (seconds):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        clipboard_entry = ttk.Spinbox(clipboard_frame, from_=0.1, to=1.0, increment=0.1, textvariable=self.clipboard_delay_var, width=5)
        clipboard_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # About section
        about_frame = ttk.LabelFrame(parent, text="About")
        about_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        about_text = "Multi-Language Auto Typer\n\n"
        about_text += "This application allows you to automatically type text in multiple languages including Arabic and English.\n\n"
        about_text += "Instructions:\n"
        about_text += "1. Enter the text you want to type automatically\n"
        about_text += "2. Set the delay and typing speed\n"
        about_text += "3. Click 'Start Typing' or press F6\n"
        about_text += "4. Quickly click where you want the text to be typed\n\n"
        about_text += "You can save frequently used texts for quick access."
        
        about_label = ttk.Label(about_frame, text=about_text, wraplength=500, justify=tk.LEFT)
        about_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Linux compatibility note
        if os.name != 'nt':  # Check if not Windows
            linux_note = ttk.LabelFrame(parent, text="Linux Compatibility")
            linux_note.pack(fill=tk.X, padx=10, pady=10)
            
            linux_text = "For Linux users:\n"
            linux_text += "1. Make sure xclip or xsel is installed for clipboard functionality:\n"
            linux_text += "   sudo apt-get install xclip    or    sudo apt-get install xsel\n"
            linux_text += "2. Some window managers may require adjustments for the auto-typing to work properly."
            
            linux_label = ttk.Label(linux_note, text=linux_text, wraplength=500, justify=tk.LEFT)
            linux_label.pack(padx=10, pady=10, fill=tk.X)
        
    def start_typing(self):
        if self.typing_active:
            return
            
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.status_var.set("Error: No text to type")
            return
            
        try:
            delay = float(self.delay_var.get())
            speed = float(self.speed_var.get())
        except ValueError:
            self.status_var.set("Error: Invalid delay or speed values")
            return
            
        self.typing_active = True
        self.pause_typing = False
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Reset progress bar
        self.progress_bar.config(value=0)
        
        self.status_var.set(f"Starting in {delay} seconds... Click where you want to type!")
        
        # Start typing in a separate thread
        self.current_thread = threading.Thread(target=self.typing_thread, args=(text, delay, speed))
        self.current_thread.daemon = True
        self.current_thread.start()

    def typing_thread(self, text, delay, speed):
        # Countdown
        for i in range(int(delay), 0, -1):
            if not self.typing_active:
                return
            self.status_var.set(f"Starting in {i} seconds... Click where you want to type!")
            time.sleep(1)
            
        self.status_var.set("Typing...")
        
        # Set progress bar maximum
        self.root.after(0, lambda: self.progress_bar.config(maximum=len(text)))
        
        # Determine if we're dealing with Arabic text
        is_arabic = self.lang_mode_var.get() == "arabic" or (
            self.lang_mode_var.get() == "auto" and any(0x0600 <= ord(c) <= 0x06FF for c in text)
        )
        
        # Get the Arabic typing mode
        arabic_mode = getattr(self, 'arabic_mode_var', tk.StringVar(value="character")).get()
        
        # For Arabic text with paste mode, use the whole text approach
        if is_arabic and arabic_mode == "paste":
            self.type_arabic_text_paste(text, speed)
        else:
            # For all other cases, use character by character approach
            chunks = [c for c in text]
            total_chunks = len(chunks)
            
            for i, chunk in enumerate(chunks):
                if not self.typing_active:
                    return
                    
                while self.pause_typing:
                    time.sleep(0.1)
                    if not self.typing_active:
                        return
                
                try:
                    # For Arabic text, use clipboard for each character to ensure proper rendering
                    if is_arabic:
                        pyperclip.copy(chunk)
                        time.sleep(float(getattr(self, 'clipboard_delay_var', tk.StringVar(value="0.3")).get()))
                        pyautogui.hotkey('ctrl', 'v')
                    else:
                        # For non-Arabic, we can use direct typing
                        pyautogui.write(chunk)
                    
                    # Wait according to typing speed
                    time.sleep(speed)
                    
                except Exception as e:
                    self.status_var.set(f"Error typing text: {str(e)}")
                    print(f"Typing error: {str(e)}")
                    self.typing_active = False
                    self.root.after(0, self.reset_buttons)
                    return
                
                # Update progress bar based on character position
                progress_value = i + 1
                self.root.after(0, lambda v=progress_value: self.progress_bar.config(value=v))
            
        self.status_var.set("Typing completed")
        self.typing_active = False
        self.root.after(0, self.reset_buttons)
    
    def type_arabic_text_paste(self, text, speed):
        """Special handling for Arabic text using paste mode"""
        try:
            # Copy the entire text to clipboard
            pyperclip.copy(text)
            
            # Wait a moment to ensure text is copied
            clipboard_delay = float(getattr(self, 'clipboard_delay_var', tk.StringVar(value="0.3")).get())
            time.sleep(clipboard_delay)
            
            # Try multiple paste methods
            try:
                # Method 1: Standard hotkey
                pyautogui.hotkey('ctrl', 'v')
            except:
                try:
                    # Method 2: Alternative approach
                    pyautogui.keyDown('ctrl')
                    pyautogui.press('v')
                    pyautogui.keyUp('ctrl')
                except:
                    # Method 3: Try using win32clipboard
                    try:
                        import win32clipboard
                        win32clipboard.OpenClipboard()
                        win32clipboard.EmptyClipboard()
                        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
                        win32clipboard.CloseClipboard()
                        
                        # Try pasting again
                        time.sleep(clipboard_delay)
                        pyautogui.hotkey('ctrl', 'v')
                    except:
                        self.status_var.set("Failed to paste Arabic text. Please check clipboard functionality.")
            
            # Update progress bar to 100%
            self.root.after(0, lambda: self.progress_bar.config(value=len(text)))
            
            # Wait a moment to ensure text is pasted
            time.sleep(speed * 5)
            
        except Exception as e:
            self.status_var.set(f"Error pasting text: {str(e)}")
            print(f"Clipboard error: {str(e)}")
            self.typing_active = False
            self.root.after(0, self.reset_buttons)

    def process_text_to_chunks(self, text):
        """Break text into appropriate chunks for typing"""
        # This method is kept for backward compatibility
        # Now we handle chunking directly in the typing_thread method
        return [c for c in text]

    def toggle_pause(self):
        if not self.typing_active:
            return
            
        self.pause_typing = not self.pause_typing
        if self.pause_typing:
            self.status_var.set("Typing paused")
            self.pause_btn.config(text="Resume (F7)")
        else:
            self.status_var.set("Typing resumed")
            self.pause_btn.config(text="Pause (F7)")

    def stop_typing(self):
        if not self.typing_active:
            return
            
        self.typing_active = False
        self.status_var.set("Typing stopped")
        self.reset_buttons()

    def reset_buttons(self):
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="Pause/Resume (F7)")
        self.stop_btn.config(state=tk.DISABLED)

    def save_current_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.status_var.set("Error: No text to save")
            return
            
        name = self.save_name_var.get().strip()
        if not name:
            self.status_var.set("Error: Please enter a name for the saved text")
            return
            
        self.saved_texts[name] = text
        self.save_to_file()
        self.update_saved_list()
        self.save_name_var.set("")
        self.status_var.set(f"Text saved as '{name}'")

    def load_selected_text(self):
        selection = self.saved_list.curselection()
        if not selection:
            self.status_var.set("Error: No text selected")
            return
            
        selected_name = self.saved_list.get(selection[0])
        if selected_name in self.saved_texts:
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", self.saved_texts[selected_name])
            self.status_var.set(f"Loaded text: '{selected_name}'")
            self.notebook.select(0)  # Switch to typing tab

    def delete_selected_text(self):
        selection = self.saved_list.curselection()
        if not selection:
            self.status_var.set("Error: No text selected")
            return
            
        selected_name = self.saved_list.get(selection[0])
        if selected_name in self.saved_texts:
            del self.saved_texts[selected_name]
            self.save_to_file()
            self.update_saved_list()
            self.status_var.set(f"Deleted text: '{selected_name}'")

    def update_saved_list(self):
        self.saved_list.delete(0, tk.END)
        for name in sorted(self.saved_texts.keys()):
            self.saved_list.insert(tk.END, name)

    def load_saved_texts(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.saved_texts = json.load(f)
            except Exception as e:
                self.saved_texts = {}
                print(f"Error loading saved texts: {e}")
        else:
            self.saved_texts = {}

    def save_to_file(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.saved_texts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving texts: {e}")

    def apply_theme(self):
        theme = self.theme_var.get()
        if theme == "dark":
            self.root.configure(bg="#333333")
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TFrame", background="#333333")
            style.configure("TLabel", background="#333333", foreground="#ffffff")
            style.configure("TLabelframe", background="#333333", foreground="#ffffff")
            style.configure("TLabelframe.Label", background="#333333", foreground="#ffffff")
            style.configure("TButton", background="#555555", foreground="#ffffff")
            style.configure("TRadiobutton", background="#333333", foreground="#ffffff")
            
            self.text_input.configure(bg="#2a2a2a", fg="#ffffff", insertbackground="#ffffff")
            self.saved_list.configure(bg="#2a2a2a", fg="#ffffff")
        else:
            self.root.configure(bg="#f0f0f0")
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TFrame", background="#f0f0f0")
            style.configure("TLabel", background="#f0f0f0", foreground="#000000")
            style.configure("TLabelframe", background="#f0f0f0", foreground="#000000")
            style.configure("TLabelframe.Label", background="#f0f0f0", foreground="#000000")
            style.configure("TButton", background="#e0e0e0", foreground="#000000")
            style.configure("TRadiobutton", background="#f0f0f0", foreground="#000000")
            
            self.text_input.configure(bg="#ffffff", fg="#000000", insertbackground="#000000")
            self.saved_list.configure(bg="#ffffff", fg="#000000")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTyperApp(root)
    root.mainloop()

    def setup_settings_tab(self, parent):
        # Theme settings
        theme_frame = ttk.LabelFrame(parent, text="Appearance")
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.theme_var = tk.StringVar(value="light")
        ttk.Radiobutton(theme_frame, text="Light Theme", variable=self.theme_var, value="light", command=self.apply_theme).pack(anchor=tk.W, padx=20, pady=5)
        ttk.Radiobutton(theme_frame, text="Dark Theme", variable=self.theme_var, value="dark", command=self.apply_theme).pack(anchor=tk.W, padx=20, pady=5)
        
        # Clipboard settings
        clipboard_frame = ttk.LabelFrame(parent, text="Clipboard Settings")
        clipboard_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.clipboard_delay_var = tk.StringVar(value="0.3")
        ttk.Label(clipboard_frame, text="Clipboard delay (seconds):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        clipboard_entry = ttk.Spinbox(clipboard_frame, from_=0.1, to=1.0, increment=0.1, textvariable=self.clipboard_delay_var, width=5)
        clipboard_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # About section
        about_frame = ttk.LabelFrame(parent, text="About")
        about_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        about_text = "Multi-Language Auto Typer\n\n"
        about_text += "This application allows you to automatically type text in multiple languages including Arabic and English.\n\n"
        about_text += "Instructions:\n"
        about_text += "1. Enter the text you want to type automatically\n"
        about_text += "2. Set the delay and typing speed\n"
        about_text += "3. Click 'Start Typing' or press F6\n"
        about_text += "4. Quickly click where you want the text to be typed\n\n"
        about_text += "You can save frequently used texts for quick access."
        
        about_label = ttk.Label(about_frame, text=about_text, wraplength=500, justify=tk.LEFT)
        about_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def setup_settings_tab(self, parent):
        # RTL text settings
        rtl_frame = ttk.LabelFrame(parent, text="RTL Text Settings")
        rtl_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.rtl_support_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(rtl_frame, text="Enable RTL text support", variable=self.rtl_support_var, 
                       command=self.toggle_rtl_support).pack(anchor=tk.W, padx=20, pady=5)
        
        # RTL text settings
        rtl_frame = ttk.LabelFrame(parent, text="RTL Text Settings")
        rtl_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.rtl_support_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(rtl_frame, text="Enable RTL text support", variable=self.rtl_support_var, 
                       command=self.toggle_rtl_support).pack(anchor=tk.W, padx=20, pady=5)
        
        # About section
        about_frame = ttk.LabelFrame(parent, text="About")
        about_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        about_text = "Multi-Language Auto Typer\n\n"
        about_text += "This application allows you to automatically type text in multiple languages including Arabic and English.\n\n"
        about_text += "Instructions:\n"
        about_text += "1. Enter the text you want to type automatically\n"
        about_text += "2. Set the delay and typing speed\n"
        about_text += "3. Click 'Start Typing' or press F6\n"
        about_text += "4. Quickly click where you want the text to be typed\n\n"
        about_text += "You can save frequently used texts for quick access."
        
        about_label = ttk.Label(about_frame, text=about_text, wraplength=500, justify=tk.LEFT)
        about_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def toggle_rtl_support(self):
        """Toggle RTL text support"""
        self.rtl_support = self.rtl_support_var.get()
        # Apply RTL settings to text input
        if self.rtl_support:
            # Enable RTL for text input
            try:
                self.text_input.config(wrap=tk.WORD)
                # Some platforms support this direct RTL configuration
                try:
                    self.text_input.config(undo=True, autoseparators=True)
                except:
                    pass
            except:
                self.status_var.set("Warning: Limited RTL support on this platform")
        else:
            # Standard LTR settings
            self.text_input.config(wrap=tk.WORD)