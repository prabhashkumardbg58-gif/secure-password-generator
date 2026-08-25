import customtkinter as ctk
from tkinter import messagebox
import random
import string

# --- Configuration & Theme ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PasswordGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QUANTUM SECURE PASS")
        self.geometry("520x620")
        self.resizable(False, False)
        self.configure(fg_color="#0d1117")

        self.create_widgets()

    def create_widgets(self):
        # Header / Title
        self.header_label = ctk.CTkLabel(
            self,
            text="🔒 QUANTUM SECURE PASS",
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color="#00f0ff"
        )
        self.header_label.pack(pady=(25, 15))

        # Generate Button (Neon Gradient Look)
        self.generate_btn = ctk.CTkButton(
            self,
            text="GENERATE PASSWORD",
            command=self.generate_password,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color="#00e5ff",
            hover_color="#00b4d8",
            text_color="#050811",
            corner_radius=25,
            height=48,
            border_width=2,
            border_color="#00f0ff"
        )
        self.generate_btn.pack(pady=10, padx=40, fill="x")

        # Password Display Card
        self.display_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=15, border_width=1, border_color="#30363d")
        self.display_frame.pack(pady=15, padx=30, fill="x")

        self.password_var = ctk.StringVar(value="Click Generate to Start")
        self.password_entry = ctk.CTkEntry(
            self.display_frame,
            textvariable=self.password_var,
            font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
            text_color="#00f5d4",
            fg_color="transparent",
            border_width=0,
            justify="center",
            height=50
        )
        self.password_entry.pack(pady=10, padx=15, fill="x")

        # Middle Dashboard (Strength & Copy)
        self.mid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mid_frame.pack(pady=10, padx=30, fill="x")

        # Strength Box
        self.strength_card = ctk.CTkFrame(self.mid_frame, fg_color="#161b22", corner_radius=12, border_width=1, border_color="#30363d")
        self.strength_card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.strength_title = ctk.CTkLabel(self.strength_card, text="SECURITY RATING", font=ctk.CTkFont(size=10, weight="bold"), text_color="#8b949e")
        self.strength_title.pack(pady=(12, 2))

        self.strength_label = ctk.CTkLabel(self.strength_card, text="IDLE", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#6e7681")
        self.strength_label.pack(pady=(0, 12))

        # Copy Button
        self.copy_btn = ctk.CTkButton(
            self.mid_frame,
            text="📋 COPY PASS",
            command=self.copy_to_clipboard,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#6c5ce7",
            hover_color="#5843be",
            text_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#a29bfe"
        )
        self.copy_btn.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # Controls Container
        self.controls_card = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=15, border_width=1, border_color="#30363d")
        self.controls_card.pack(pady=15, padx=30, fill="x")

        # Length Slider
        self.length_label = ctk.CTkLabel(
            self.controls_card, 
            text="LENGTH: 16", 
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#c9d1d9"
        )
        self.length_label.pack(pady=(15, 5))

        self.length_slider = ctk.CTkSlider(
            self.controls_card, 
            from_=6, 
            to=32, 
            number_of_steps=26,
            command=self.update_slider_label,
            button_color="#00f0ff",
            button_hover_color="#00b4d8",
            progress_color="#6c5ce7"
        )
        self.length_slider.set(16)
        self.length_slider.pack(pady=(0, 15), padx=20, fill="x")

        # Switch Toggles
        self.switches_frame = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        self.switches_frame.pack(pady=(0, 15), padx=10, fill="x")

        self.num_switch = ctk.CTkSwitch(self.switches_frame, text="Numbers", progress_color="#00e5ff")
        self.num_switch.select()
        self.num_switch.grid(row=0, column=0, padx=12, pady=6)

        self.sym_switch = ctk.CTkSwitch(self.switches_frame, text="Symbols", progress_color="#00e5ff")
        self.sym_switch.select()
        self.sym_switch.grid(row=0, column=1, padx=12, pady=6)

        self.upper_switch = ctk.CTkSwitch(self.switches_frame, text="Uppercase", progress_color="#6c5ce7")
        self.upper_switch.select()
        self.upper_switch.grid(row=1, column=0, padx=12, pady=6)

        self.lower_switch = ctk.CTkSwitch(self.switches_frame, text="Lowercase", progress_color="#6c5ce7")
        self.lower_switch.select()
        self.lower_switch.grid(row=1, column=1, padx=12, pady=6)

    def update_slider_label(self, value):
        self.length_label.configure(text=f"LENGTH: {int(value)}")

    def calculate_strength(self, pwd):
        score = 0
        if len(pwd) >= 12: score += 1
        if len(pwd) >= 18: score += 1
        if any(c in string.digits for c in pwd): score += 1
        if any(c in string.punctuation for c in pwd): score += 1
        if any(c.islower() for c in pwd) and any(c.isupper() for c in pwd): score += 1

        if score <= 2:
            return "VULNERABLE", "#ff4757"
        elif score <= 4:
            return "SECURE", "#ffa502"
        else:
            return "LEGENDARY STRENGTH", "#2ed573"

    def generate_password(self):
        pool = ""
        if self.upper_switch.get():
            pool += string.ascii_uppercase
        if self.lower_switch.get():
            pool += string.ascii_lowercase
        if self.num_switch.get():
            pool += string.digits
        if self.sym_switch.get():
            pool += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not pool:
            messagebox.showwarning("Warning", "Select at least one character type!")
            return

        length = int(self.length_slider.get())
        password = "".join(random.choice(pool) for _ in range(length))
        self.password_var.set(password)

        # Update rating
        rating, color = self.calculate_strength(password)
        self.strength_label.configure(text=rating, text_color=color)

    def copy_to_clipboard(self):
        pwd = self.password_var.get()
        if pwd and pwd != "Click Generate to Start":
            self.clipboard_clear()
            self.clipboard_append(pwd)
            messagebox.showinfo("Success", "Password copied to clipboard!")

if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()