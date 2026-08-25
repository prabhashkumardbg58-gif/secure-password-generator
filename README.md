# ⚡ Quantum Secure Pass - Enterprise Edition

An advanced, cyberpunk-styled cybersecurity utility and password manager built with **Python** and **CustomTkinter**.

---

## ✨ Features

### 🔐 Password & Key Generation
- **Multiple Modes:** Standard Alphanumeric, Memorable Passphrases, Numeric PINs, and Phonetic/Pronounceable strings.
- **Shannon Entropy Engine:** Real-time entropy calculation in bits.
- **Time-to-Crack Telemetry:** Dynamic brute-force estimation based on high-speed hardware profiles.
- **Custom Character Filtering:** Exclude ambiguous characters (`0, O, l, 1, I, |`) to eliminate readability errors.

### 🛡️ Security & Auditing
- **HaveIBeenPwned API Integration:** Check passwords against public corporate breaches using secure SHA-1 $k$-Anonymity hashing.
- **Security Health Audit:** Automatically scans encrypted vault entries to flag weak passwords (<10 chars) and reused credentials.
- **Auto-Clearing Clipboard:** Clears copied passwords from the OS clipboard after 30 seconds.
- **Inactivity Auto-Lock:** Automatically locks the encrypted vault after 3 minutes of inactivity.

### 🗄️ AES-256 Encrypted Vault
- **Zero-Knowledge Encryption:** Encrypts credentials locally using Fernet (AES-256-CBC) derived via PBKDF2HMAC-SHA256.
- **Live Search & Filter:** Instant search bar to locate stored service credentials quickly.

### 🔑 2FA / TOTP Authenticator
- Built-in Time-Based One-Time Password generator compatible with standard 2FA secrets (Base32).
- Real-time countdown timer with 30-second token refresh.

### 📲 Portability & Tools
- **Mobile Transfer via QR Code:** Generates high-contrast QR codes to beam passwords directly to mobile cameras.
- **Bulk CSV Exporter:** Batch generate up to 200 high-entropy passwords formatted into structured `.csv` files for IT management.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure **Python 3.10+** is installed on your machine.

### 2. Install Dependencies
```bash
pip install -r requirements.txt