import customtkinter as ctk
from tkinter import messagebox
import random
import string
import math
import time

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Word bank for passphrase mode
WORD_BANK = [
    "quantum", "cyber", "falcon", "orbit", "matrix", "shield", "hyper", "neon", 
    "echo", "shadow", "titan", "plasma", "vortex", "stellar", "frost", "cipher",
    "binary", "crypto", "nexus", "aurora", "dynamo", "phantom", "pulse", "solar"
]

class QuantumPassApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QUANTUM SECURE PASS - Pro Suite")
        self.geometry("640x780")
        self.resizable(False, False)
        self.configure(fg_color="#0b0f19")

        self.history = []
        self.create_widgets()

    def create_widgets(self):
        # Header
        self.header = ctk.CTkLabel(
            self, text="⚡ QUANTUM SECURE PASS", 
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color="#00f0ff"
        )
        self.header.pack(pady=(18, 8))

        # Mode Selector
        self.mode_var = ctk.StringVar(value="Standard")
        self.mode_switch = ctk.CTkSegmentedButton(
            self, values=["Standard", "Passphrase", "PIN"],
            variable=self.mode_var, command=self.on_mode_change,
            selected_color="#6c5ce7", unselected_color="#161b22"
        )
        self.mode_switch.pack(pady=6)

        # Output Card
        self.display_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=12, border_width=1, border_color="#30363d")
        self.display_frame.pack(pady=10, padx=25, fill="x")

        self.password_var = ctk.StringVar(value="Generate to Begin")
        self.password_entry = ctk.CTkEntry(
            self.display_frame, textvariable=self.password_var,
            font=ctk.CTkFont(family="Consolas", size=17, weight="bold"),
            text_color="#00f5d4", fg_color="transparent", border_width=0,
            justify="center", height=45
        )
        self.password_entry.pack(pady=8, padx=10, fill="x")

        # Telemetry Frame (Entropy & Crack Time)
        self.stats_frame = ctk.CTkFrame(self, fg_color="#101622", corner_radius=10)
        self.stats_frame.pack(pady=5, padx=25, fill="x")

        self.entropy_label = ctk.CTkLabel(self.stats_frame, text="Entropy: 0 bits", font=ctk.CTkFont(size=11), text_color="#8b949e")
        self.entropy_label.pack(side="left", padx=15, pady=6)

        self.crack_label = ctk.CTkLabel(self.stats_frame, text="Crack Time: -", font=ctk.CTkFont(size=11, weight="bold"), text_color="#ffa502")
        self.crack_label.pack(side="right", padx=15, pady=6)

        # Main Generate Button
        self.generate_btn = ctk.CTkButton(
            self, text="GENERATE PASSWORD", command=self.generate,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#00e5ff", hover_color="#00b4d8", text_color="#050811",
            corner_radius=20, height=42
        )
        self.generate_btn.pack(pady=10, padx=25, fill="x")

        # Action Buttons
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=4, padx=25, fill="x")

        self.copy_btn = ctk.CTkButton(
            self.action_frame, text="📋 Copy (Auto-Clears in 30s)", command=self.copy_to_clipboard,
            fg_color="#6c5ce7", hover_color="#5843be", height=35
        )
        self.copy_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Controls Container
        self.controls = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=12)
        self.controls.pack(pady=8, padx=25, fill="x")

        self.length_label = ctk.CTkLabel(self.controls, text="LENGTH: 16", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"))
        self.length_label.pack(pady=(8, 2))

        self.length_slider = ctk.CTkSlider(self.controls, from_=4, to=48, number_of_steps=44, command=self.update_length_label)
        self.length_slider.set(16)
        self.length_slider.pack(pady=(0, 8), padx=20, fill="x")

        # Checkbox Options
        self.switches_frame = ctk.CTkFrame(self.controls, fg_color="transparent")
        self.switches_frame.pack(pady=4, padx=10, fill="x")

        self.num_switch = ctk.CTkSwitch(self.switches_frame, text="Numbers (0-9)")
        self.num_switch.select()
        self.num_switch.grid(row=0, column=0, padx=10, pady=4, sticky="w")

        self.sym_switch = ctk.CTkSwitch(self.switches_frame, text="Symbols (!@#)")
        self.sym_switch.select()
        self.sym_switch.grid(row=0, column=1, padx=10, pady=4, sticky="w")

        self.upper_switch = ctk.CTkSwitch(self.switches_frame, text="Uppercase (A-Z)")
        self.upper_switch.select()
        self.upper_switch.grid(row=1, column=0, padx=10, pady=4, sticky="w")

        self.ambig_switch = ctk.CTkSwitch(self.switches_frame, text="Exclude Ambiguous (0,O,l,1)")
        self.ambig_switch.grid(row=1, column=1, padx=10, pady=4, sticky="w")

        # Session History View
        self.history_label = ctk.CTkLabel(self, text="Session History (Recent 4)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#8b949e")
        self.history_label.pack(pady=(6, 2))

        self.history_box = ctk.CTkTextbox(self, height=70, fg_color="#101622", text_color="#a29bfe", font=ctk.CTkFont(family="Consolas", size=11))
        self.history_box.pack(pady=2, padx=25, fill="x")
        self.history_box.configure(state="disabled")

    def update_length_label(self, val):
        self.length_label.configure(text=f"LENGTH: {int(val)}")

    def on_mode_change(self, mode):
        if mode == "Passphrase":
            self.length_slider.configure(from_=3, to=8, number_of_steps=5)
            self.length_slider.set(4)
            self.length_label.configure(text="WORDS: 4")
        elif mode == "PIN":
            self.length_slider.configure(from_=4, to=12, number_of_steps=8)
            self.length_slider.set(6)
            self.length_label.configure(text="LENGTH: 6")
        else:
            self.length_slider.configure(from_=4, to=48, number_of_steps=44)
            self.length_slider.set(16)
            self.length_label.configure(text="LENGTH: 16")

    def calculate_telemetry(self, password, pool_size):
        if not password or pool_size <= 0:
            return
        entropy = len(password) * math.log2(pool_size)
        self.entropy_label.configure(text=f"Entropy: {entropy:.1f} bits")

        # Assuming 10 billion guesses/sec (modern GPU rig)
        seconds = (2 ** entropy) / 10_000_000_000

        if seconds < 1: crack_str = "Instant"
        elif seconds < 60: crack_str = f"{int(seconds)} secs"
        elif seconds < 3600: crack_str = f"{int(seconds/60)} mins"
        elif seconds < 86400: crack_str = f"{int(seconds/3600)} hours"
        elif seconds < 31536000: crack_str = f"{int(seconds/86400)} days"
        elif seconds < 31536000 * 1000: crack_str = f"{int(seconds/31536000)} years"
        else: crack_str = "Centuries+"

        color = "#ff4757" if entropy < 45 else ("#ffa502" if entropy < 70 else "#2ed573")
        self.crack_label.configure(text=f"Crack Time: ~{crack_str}", text_color=color)

    def generate(self):
        mode = self.mode_var.get()
        length = int(self.length_slider.get())
        password = ""
        pool_size = 0

        if mode == "Passphrase":
            selected = random.choices(WORD_BANK, k=length)
            password = "-".join(selected)
            pool_size = len(WORD_BANK)
        elif mode == "PIN":
            password = "".join(random.choices(string.digits, k=length))
            pool_size = 10
        else:
            pool = string.ascii_lowercase
            if self.upper_switch.get(): pool += string.ascii_uppercase
            if self.num_switch.get(): pool += string.digits
            if self.sym_switch.get(): pool += "!@#$%^&*()_+-=[]{}|;:,.<>?"

            if self.ambig_switch.get():
                for char in "0Ol1I|":
                    pool = pool.replace(char, "")

            if not pool:
                messagebox.showwarning("Warning", "Select at least one character type.")
                return

            password = "".join(random.choices(pool, k=length))
            pool_size = len(pool)

        self.password_var.set(password)
        self.calculate_telemetry(password, pool_size)
        self.add_to_history(password)

    def add_to_history(self, pwd):
        self.history.insert(0, pwd)
        self.history = self.history[:4]
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        self.history_box.insert("end", "\n".join(self.history))
        self.history_box.configure(state="disabled")

    def copy_to_clipboard(self):
        pwd = self.password_var.get()
        if pwd and pwd not in ["Generate to Begin", ""]:
            self.clipboard_clear()
            self.clipboard_append(pwd)
            self.copy_btn.configure(text="✅ Copied! (Clearing in 30s)")
            self.after(30000, self.auto_clear_clipboard)

    def auto_clear_clipboard(self):
        self.clipboard_clear()
        self.copy_btn.configure(text="📋 Copy (Auto-Clears in 30s)")

if __name__ == "__main__":
    app = QuantumPassApp()
    app.mainloop()