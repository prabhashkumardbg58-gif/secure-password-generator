import customtkinter as ctk
from tkinter import messagebox, filedialog
import random
import string
import math
import hashlib
import requests
import base64
import os
import json
import csv
import time
import qrcode
from PIL import ImageTk
import pyotp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

WORD_BANK = [
    "quantum", "cyber", "falcon", "orbit", "matrix", "shield", "hyper", "neon", 
    "echo", "shadow", "titan", "plasma", "vortex", "stellar", "frost", "cipher",
    "binary", "crypto", "nexus", "aurora", "dynamo", "phantom", "pulse", "solar"
]

VAULT_FILE = "vault.enc"
VAULT_SALT_FILE = "vault.salt"

class QuantumVault:
    @staticmethod
    def _get_fernet_key(master_pwd: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_pwd.encode()))

    @classmethod
    def load_vault(cls, master_pwd: str) -> dict:
        if not os.path.exists(VAULT_FILE) or not os.path.exists(VAULT_SALT_FILE):
            return {}
        with open(VAULT_SALT_FILE, "rb") as f:
            salt = f.read()
        key = cls._get_fernet_key(master_pwd, salt)
        fernet = Fernet(key)
        try:
            with open(VAULT_FILE, "rb") as f:
                decrypted = fernet.decrypt(f.read())
            return json.loads(decrypted.decode())
        except Exception:
            raise ValueError("Invalid Master Password or corrupted vault.")

    @classmethod
    def save_vault(cls, master_pwd: str, data: dict):
        if os.path.exists(VAULT_SALT_FILE):
            with open(VAULT_SALT_FILE, "rb") as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(VAULT_SALT_FILE, "wb") as f:
                f.write(salt)

        key = cls._get_fernet_key(master_pwd, salt)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(json.dumps(data).encode())
        with open(VAULT_FILE, "wb") as f:
            f.write(encrypted)


class QuantumPassApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QUANTUM SECURE PASS - Enterprise Edition")
        self.geometry("780x880")
        self.resizable(False, False)
        self.configure(fg_color="#0b0f19")

        self.history = []
        self.vault_cache = {}
        self.totp_secrets = {}
        self.qr_window = None
        self.last_activity = time.time()

        self.create_tabview()
        self.bind_events()
        self.check_auto_lock()
        self.update_totp_loop()

    def bind_events(self):
        self.bind_all("<Key>", lambda e: self.reset_timer())
        self.bind_all("<Button-1>", lambda e: self.reset_timer())

    def reset_timer(self):
        self.last_activity = time.time()

    def check_auto_lock(self):
        if getattr(self, "vault_unlocked", False):
            if time.time() - self.last_activity > 180:
                self.lock_vault()
                messagebox.showwarning("Auto-Lock", "Vault locked automatically due to 3 minutes of inactivity.")
        self.after(5000, self.check_auto_lock)

    def create_tabview(self):
        self.tabs = ctk.CTkTabview(self, fg_color="#101622", segmented_button_selected_color="#6c5ce7")
        self.tabs.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_generator = self.tabs.add("Generator")
        self.tab_vault = self.tabs.add("Encrypted Vault")
        self.tab_totp = self.tabs.add("2FA Authenticator")
        self.tab_bulk = self.tabs.add("Bulk Export")

        self.setup_generator_ui()
        self.setup_vault_ui()
        self.setup_totp_ui()
        self.setup_bulk_ui()

    # --- Tab 1: Generator UI ---
    def setup_generator_ui(self):
        self.header = ctk.CTkLabel(
            self.tab_generator, text="⚡ QUANTUM GENERATOR", 
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color="#00f0ff"
        )
        self.header.pack(pady=(10, 6))

        self.mode_var = ctk.StringVar(value="Standard")
        self.mode_switch = ctk.CTkSegmentedButton(
            self.tab_generator, values=["Standard", "Passphrase", "PIN", "Pronounceable"],
            variable=self.mode_var, command=self.on_mode_change,
            selected_color="#6c5ce7", unselected_color="#161b22"
        )
        self.mode_switch.pack(pady=4)

        self.display_frame = ctk.CTkFrame(self.tab_generator, fg_color="#161b22", corner_radius=10)
        self.display_frame.pack(pady=8, padx=20, fill="x")

        self.password_var = ctk.StringVar(value="Generate to Begin")
        self.password_entry = ctk.CTkEntry(
            self.display_frame, textvariable=self.password_var,
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color="#00f5d4", fg_color="transparent", border_width=0,
            justify="center", height=40
        )
        self.password_entry.pack(pady=6, padx=10, fill="x")

        self.stats_frame = ctk.CTkFrame(self.tab_generator, fg_color="#0b0f19", corner_radius=8)
        self.stats_frame.pack(pady=2, padx=20, fill="x")

        self.entropy_label = ctk.CTkLabel(self.stats_frame, text="Entropy: 0 bits", font=ctk.CTkFont(size=11), text_color="#8b949e")
        self.entropy_label.pack(side="left", padx=12, pady=4)

        self.crack_label = ctk.CTkLabel(self.stats_frame, text="Crack Time: -", font=ctk.CTkFont(size=11, weight="bold"), text_color="#ffa502")
        self.crack_label.pack(side="right", padx=12, pady=4)

        self.generate_btn = ctk.CTkButton(
            self.tab_generator, text="GENERATE PASSWORD", command=self.generate,
            font=ctk.CTkFont(size=13, weight="bold"), fg_color="#00e5ff", hover_color="#00b4d8",
            text_color="#050811", corner_radius=15, height=38
        )
        self.generate_btn.pack(pady=8, padx=20, fill="x")

        self.btn_grid = ctk.CTkFrame(self.tab_generator, fg_color="transparent")
        self.btn_grid.pack(pady=2, padx=20, fill="x")

        self.copy_btn = ctk.CTkButton(self.btn_grid, text="📋 Copy", command=self.copy_to_clipboard, fg_color="#6c5ce7", width=120)
        self.copy_btn.pack(side="left", padx=2, expand=True, fill="x")

        self.pwned_btn = ctk.CTkButton(self.btn_grid, text="🛡️ Breach Check", command=self.check_pwned_api, fg_color="#eb4d4b", width=120)
        self.pwned_btn.pack(side="left", padx=2, expand=True, fill="x")

        self.qr_btn = ctk.CTkButton(self.btn_grid, text="📱 Show QR", command=self.show_qr_code, fg_color="#2ed573", text_color="#050811", width=120)
        self.qr_btn.pack(side="left", padx=2, expand=True, fill="x")

        self.controls = ctk.CTkFrame(self.tab_generator, fg_color="#161b22", corner_radius=10)
        self.controls.pack(pady=8, padx=20, fill="x")

        self.length_label = ctk.CTkLabel(self.controls, text="LENGTH: 16", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"))
        self.length_label.pack(pady=(6, 0))

        self.length_slider = ctk.CTkSlider(self.controls, from_=4, to=48, number_of_steps=44, command=self.update_length_label)
        self.length_slider.set(16)
        self.length_slider.pack(pady=4, padx=20, fill="x")

        self.switches_frame = ctk.CTkFrame(self.controls, fg_color="transparent")
        self.switches_frame.pack(pady=4, padx=10, fill="x")

        self.num_switch = ctk.CTkSwitch(self.switches_frame, text="Numbers")
        self.num_switch.select()
        self.num_switch.grid(row=0, column=0, padx=10, pady=2, sticky="w")

        self.sym_switch = ctk.CTkSwitch(self.switches_frame, text="Symbols")
        self.sym_switch.select()
        self.sym_switch.grid(row=0, column=1, padx=10, pady=2, sticky="w")

        self.upper_switch = ctk.CTkSwitch(self.switches_frame, text="Uppercase")
        self.upper_switch.select()
        self.upper_switch.grid(row=1, column=0, padx=10, pady=2, sticky="w")

        self.ambig_switch = ctk.CTkSwitch(self.switches_frame, text="No Ambiguous (0,O,l,1)")
        self.ambig_switch.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        self.history_box = ctk.CTkTextbox(self.tab_generator, height=55, fg_color="#0b0f19", text_color="#a29bfe", font=ctk.CTkFont(family="Consolas", size=11))
        self.history_box.pack(pady=6, padx=20, fill="x")
        self.history_box.configure(state="disabled")

    # --- Tab 2: Encrypted Vault with Search & Health Audit ---
    def setup_vault_ui(self):
        self.vault_unlocked = False

        self.vault_top = ctk.CTkFrame(self.tab_vault, fg_color="transparent")
        self.vault_top.pack(pady=6, padx=10, fill="x")

        self.master_pwd_entry = ctk.CTkEntry(self.vault_top, placeholder_text="Master Vault Password", show="*", width=200)
        self.master_pwd_entry.pack(side="left", padx=4)

        ctk.CTkButton(self.vault_top, text="Unlock", command=self.load_vault_entries, fg_color="#6c5ce7", width=75).pack(side="left", padx=3)
        ctk.CTkButton(self.vault_top, text="Lock", command=self.lock_vault, fg_color="#eb4d4b", width=75).pack(side="left", padx=3)
        ctk.CTkButton(self.vault_top, text="Audit Health", command=self.run_vault_audit, fg_color="#f39c12", text_color="#050811", width=95).pack(side="left", padx=3)

        self.search_entry = ctk.CTkEntry(self.tab_vault, placeholder_text="🔍 Live search accounts...")
        self.search_entry.pack(pady=4, padx=15, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_vault_display)

        self.save_form = ctk.CTkFrame(self.tab_vault, fg_color="#161b22", corner_radius=10)
        self.save_form.pack(pady=6, padx=15, fill="x")

        self.vault_acc_entry = ctk.CTkEntry(self.save_form, placeholder_text="Account/Service (e.g. GitHub)")
        self.vault_acc_entry.pack(pady=3, padx=10, fill="x")

        self.vault_pass_entry = ctk.CTkEntry(self.save_form, placeholder_text="Password to Store")
        self.vault_pass_entry.pack(pady=3, padx=10, fill="x")

        ctk.CTkButton(self.save_form, text="Save Entry to Vault", command=self.save_vault_entry, fg_color="#00e5ff", text_color="#050811").pack(pady=6)

        self.vault_list = ctk.CTkTextbox(self.tab_vault, height=180, fg_color="#0b0f19", font=ctk.CTkFont(family="Consolas", size=11))
        self.vault_list.pack(pady=4, padx=15, fill="both", expand=True)
        self.vault_list.configure(state="disabled")

    # --- Tab 3: Built-in 2FA / TOTP Authenticator UI ---
    def setup_totp_ui(self):
        ctk.CTkLabel(self.tab_totp, text="🔑 2FA Authenticator (TOTP)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00f0ff").pack(pady=(12, 6))

        self.totp_form = ctk.CTkFrame(self.tab_totp, fg_color="#161b22", corner_radius=10)
        self.totp_form.pack(pady=6, padx=20, fill="x")

        self.totp_name_entry = ctk.CTkEntry(self.totp_form, placeholder_text="Account Label (e.g. Google, Discord)")
        self.totp_name_entry.pack(pady=4, padx=15, fill="x")

        self.totp_secret_entry = ctk.CTkEntry(self.totp_form, placeholder_text="Base32 Secret Key (e.g. JBSWY3DPEHPK3PXP)")
        self.totp_secret_entry.pack(pady=4, padx=15, fill="x")

        ctk.CTkButton(self.totp_form, text="Add 2FA Key", command=self.add_totp_key, fg_color="#2ed573", text_color="#050811").pack(pady=6)

        self.totp_display = ctk.CTkTextbox(self.tab_totp, height=220, fg_color="#0b0f19", font=ctk.CTkFont(family="Consolas", size=13))
        self.totp_display.pack(pady=6, padx=20, fill="both", expand=True)
        self.totp_display.configure(state="disabled")

    # --- Tab 4: Bulk Export UI ---
    def setup_bulk_ui(self):
        ctk.CTkLabel(self.tab_bulk, text="📦 Bulk Password Exporter", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00f0ff").pack(pady=(20, 10))

        self.bulk_count_slider = ctk.CTkSlider(self.tab_bulk, from_=10, to=200, number_of_steps=19, command=lambda v: self.bulk_count_lbl.configure(text=f"Batch Count: {int(v)}"))
        self.bulk_count_slider.set(25)
        self.bulk_count_slider.pack(pady=5, padx=40, fill="x")

        self.bulk_count_lbl = ctk.CTkLabel(self.tab_bulk, text="Batch Count: 25", font=ctk.CTkFont(family="Consolas", size=12))
        self.bulk_count_lbl.pack(pady=2)

        ctk.CTkButton(self.tab_bulk, text="Generate & Export to CSV", command=self.export_csv, fg_color="#2ed573", text_color="#050811", height=40).pack(pady=20, padx=40, fill="x")

    # --- Generator Engine & Telemetry ---
    def update_length_label(self, val):
        unit = "WORDS" if self.mode_var.get() == "Passphrase" else "LENGTH"
        self.length_label.configure(text=f"{unit}: {int(val)}")

    def on_mode_change(self, mode):
        if mode == "Passphrase":
            self.length_slider.configure(from_=3, to=8, number_of_steps=5)
            self.length_slider.set(4)
        elif mode == "PIN":
            self.length_slider.configure(from_=4, to=12, number_of_steps=8)
            self.length_slider.set(6)
        else:
            self.length_slider.configure(from_=4, to=48, number_of_steps=44)
            self.length_slider.set(16)
        self.update_length_label(self.length_slider.get())

    def calculate_telemetry(self, password, pool_size):
        if not password or pool_size <= 0: return
        entropy = len(password) * math.log2(pool_size)
        self.entropy_label.configure(text=f"Entropy: {entropy:.1f} bits")

        seconds = (2 ** entropy) / 10_000_000_000
        if seconds < 1: crack_str = "Instant"
        elif seconds < 60: crack_str = f"{int(seconds)}s"
        elif seconds < 3600: crack_str = f"{int(seconds/60)}m"
        elif seconds < 86400: crack_str = f"{int(seconds/3600)}h"
        elif seconds < 31536000: crack_str = f"{int(seconds/86400)}d"
        elif seconds < 31536000 * 1000: crack_str = f"{int(seconds/31536000)}y"
        else: crack_str = "Centuries+"

        color = "#ff4757" if entropy < 45 else ("#ffa502" if entropy < 70 else "#2ed573")
        self.crack_label.configure(text=f"Crack Time: ~{crack_str}", text_color=color)

    def generate(self):
        mode = self.mode_var.get()
        length = int(self.length_slider.get())
        password = ""
        pool_size = 0

        if mode == "Passphrase":
            password = "-".join(random.choices(WORD_BANK, k=length))
            pool_size = len(WORD_BANK)
        elif mode == "PIN":
            password = "".join(random.choices(string.digits, k=length))
            pool_size = 10
        elif mode == "Pronounceable":
            vowels = "aeiou"
            consonants = "bcdfghjklmnprstvwxyz"
            password = "".join(random.choice(consonants) + random.choice(vowels) for _ in range(length // 2))
            pool_size = len(vowels) * len(consonants)
        else:
            pool = string.ascii_lowercase
            if self.upper_switch.get(): pool += string.ascii_uppercase
            if self.num_switch.get(): pool += string.digits
            if self.sym_switch.get(): pool += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if self.ambig_switch.get():
                for char in "0Ol1I|": pool = pool.replace(char, "")
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
            self.copy_btn.configure(text="✅ Copied (30s)")
            self.after(30000, lambda: self.copy_btn.configure(text="📋 Copy"))

    def check_pwned_api(self):
        pwd = self.password_var.get()
        if not pwd or pwd == "Generate to Begin":
            messagebox.showwarning("Warning", "Generate or enter a password first.")
            return

        sha1_hash = hashlib.sha1(pwd.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]

        try:
            res = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=5)
            if res.status_code != 200:
                messagebox.showerror("Error", "Could not reach Pwned API.")
                return

            hashes = (line.split(':') for line in res.text.splitlines())
            count = next((int(cnt) for h, cnt in hashes if h == suffix), 0)

            if count > 0:
                messagebox.showwarning("Pwned Alert!", f"⚠️ Warning: Found in {count:,} known data breaches!")
            else:
                messagebox.showinfo("Safe", "✅ Good news: Zero matches found in known breaches.")
        except Exception as e:
            messagebox.showerror("API Error", f"Network error: {e}")

    def show_qr_code(self):
        pwd = self.password_var.get()
        if not pwd or pwd == "Generate to Begin":
            return

        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(pwd)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        if self.qr_window is None or not self.qr_window.winfo_exists():
            self.qr_window = ctk.CTkToplevel(self)
            self.qr_window.title("Mobile Scan")
            self.qr_window.geometry("260x280")
            self.qr_window.attributes("-topmost", True)

        tk_img = ImageTk.PhotoImage(img)
        lbl = ctk.CTkLabel(self.qr_window, image=tk_img, text="")
        lbl.image = tk_img
        lbl.pack(pady=15, padx=15)

    # --- Vault Actions, Filter & Health Audit ---
    def load_vault_entries(self):
        master_pwd = self.master_pwd_entry.get()
        if not master_pwd:
            messagebox.showwarning("Warning", "Enter master password.")
            return
        try:
            self.vault_cache = QuantumVault.load_vault(master_pwd)
            self.vault_unlocked = True
            self.filter_vault_display()
        except ValueError as err:
            messagebox.showerror("Vault Error", str(err))

    def filter_vault_display(self, event=None):
        if not self.vault_unlocked:
            return
        query = self.search_entry.get().lower()
        self.vault_list.configure(state="normal")
        self.vault_list.delete("1.0", "end")

        if not self.vault_cache:
            self.vault_list.insert("end", "[Vault Empty]")
        else:
            for acc, secret in self.vault_cache.items():
                if query in acc.lower() or query in secret.lower():
                    self.vault_list.insert("end", f"Service: {acc}\nPassword: {secret}\n" + "-"*35 + "\n")
        self.vault_list.configure(state="disabled")

    def save_vault_entry(self):
        master_pwd = self.master_pwd_entry.get()
        acc = self.vault_acc_entry.get()
        pwd = self.vault_pass_entry.get() or self.password_var.get()

        if not master_pwd or not acc or not pwd:
            messagebox.showwarning("Warning", "Fill Master Password, Account, and Password fields.")
            return
        try:
            data = QuantumVault.load_vault(master_pwd) if os.path.exists(VAULT_FILE) else {}
            data[acc] = pwd
            QuantumVault.save_vault(master_pwd, data)
            self.vault_cache = data
            self.vault_unlocked = True
            messagebox.showinfo("Saved", f"Stored credentials for {acc}")
            self.vault_acc_entry.delete(0, "end")
            self.vault_pass_entry.delete(0, "end")
            self.filter_vault_display()
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def run_vault_audit(self):
        if not self.vault_unlocked or not self.vault_cache:
            messagebox.showwarning("Audit", "Unlock a non-empty vault first.")
            return

        weak = []
        reused = {}
        for acc, pwd in self.vault_cache.items():
            if len(pwd) < 10:
                weak.append(acc)
            reused[pwd] = reused.get(pwd, 0) + 1

        reused_count = sum(1 for v in reused.values() if v > 1)
        audit_msg = f"Vault Security Audit:\n\n"
        audit_msg += f"• Total Accounts: {len(self.vault_cache)}\n"
        audit_msg += f"• Weak Passwords (<10 chars): {len(weak)} ({', '.join(weak) if weak else 'None'})\n"
        audit_msg += f"• Reused Passwords: {reused_count}\n\n"
        audit_msg += "Status: " + ("🚨 Needs Improvement" if weak or reused_count else "🛡️ Excellent Security")

        messagebox.showinfo("Security Audit Report", audit_msg)

    def lock_vault(self):
        self.master_pwd_entry.delete(0, "end")
        self.vault_cache = {}
        self.vault_unlocked = False
        self.vault_list.configure(state="normal")
        self.vault_list.delete("1.0", "end")
        self.vault_list.configure(state="disabled")

    # --- 2FA / TOTP Logic ---
    def add_totp_key(self):
        label = self.totp_name_entry.get().strip()
        secret = self.totp_secret_entry.get().strip().replace(" ", "").upper()

        if not label or not secret:
            messagebox.showwarning("Warning", "Enter both account label and secret key.")
            return
        try:
            totp = pyotp.TOTP(secret)
            _ = totp.now()  # Validate key
            self.totp_secrets[label] = secret
            self.totp_name_entry.delete(0, "end")
            self.totp_secret_entry.delete(0, "end")
            self.render_totp()
        except Exception:
            messagebox.showerror("Invalid Key", "Invalid Base32 secret key.")

    def render_totp(self):
        self.totp_display.configure(state="normal")
        self.totp_display.delete("1.0", "end")
        if not self.totp_secrets:
            self.totp_display.insert("end", "[No 2FA Accounts Added]")
        else:
            for label, sec in self.totp_secrets.items():
                totp = pyotp.TOTP(sec)
                code = totp.now()
                remaining = 30 - (int(time.time()) % 30)
                self.totp_display.insert("end", f"[{label}]\nCODE: {code[:3]} {code[3:]}  ({remaining}s remaining)\n" + "-"*35 + "\n")
        self.totp_display.configure(state="disabled")

    def update_totp_loop(self):
        if self.totp_secrets:
            self.render_totp()
        self.after(1000, self.update_totp_loop)

    # --- Bulk Export Tool ---
    def export_csv(self):
        count = int(self.bulk_count_slider.get())
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        pool = string.ascii_letters + string.digits + "!@#$%^&*"
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Index", "Generated Password", "Length", "Entropy (bits)"])
            for idx in range(1, count + 1):
                p = "".join(random.choices(pool, k=16))
                entropy = round(16 * math.log2(len(pool)), 2)
                writer.writerow([idx, p, 16, entropy])

        messagebox.showinfo("Export Successful", f"Saved {count} passwords to:\n{file_path}")


if __name__ == "__main__":
    app = QuantumPassApp()
    app.mainloop()