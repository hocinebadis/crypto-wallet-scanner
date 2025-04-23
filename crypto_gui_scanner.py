
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from datetime import datetime

with open('bip39_english.txt', 'r') as f:
    bip39_words_set = set(f.read().split())

wallet_filenames = ['wallet.dat', 'keystore', 'keyfile', 'private.key', 'ethwallet.json']
btc_address_pattern = re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b')
eth_address_pattern = re.compile(r'\b0x[a-fA-F0-9]{40}\b')
hex_private_key_pattern = re.compile(r'\b[a-fA-F0-9]{64}\b')

class CryptoScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Crypto Wallet Scanner")
        self.path = ""

        self.frame = tk.Frame(root, padx=10, pady=10)
        self.frame.pack()

        self.path_label = tk.Label(self.frame, text="Selected Folder: None")
        self.path_label.pack()

        self.browse_btn = tk.Button(self.frame, text="📁 Choose Folder", command=self.choose_folder)
        self.browse_btn.pack(pady=5)

        self.scan_btn = tk.Button(self.frame, text="🚀 Start Scan", command=self.start_scan, state='disabled')
        self.scan_btn.pack(pady=5)

        self.output = scrolledtext.ScrolledText(self.frame, width=80, height=20)
        self.output.pack()

        self.save_btn = tk.Button(self.frame, text="💾 Save Results", command=self.save_results, state='disabled')
        self.save_btn.pack(pady=5)

        self.matches = []

    def choose_folder(self):
        self.path = filedialog.askdirectory()
        if self.path:
            self.path_label.config(text=f"Selected Folder: {self.path}")
            self.scan_btn.config(state='normal')

    def log_match(self, match_type, file_path):
        log = f"[{match_type}] {file_path}\n"
        self.output.insert(tk.END, log)
        self.output.see(tk.END)
        self.matches.append(log)

    def is_bip39_phrase(self, text):
        words = text.lower().split()
        return len(words) in (12, 24) and all(word in bip39_words_set for word in words)

    def start_scan(self):
        self.output.delete(1.0, tk.END)
        self.matches = []
        self.output.insert(tk.END, f"🔎 Scanning {self.path}...\n\n")
        self.root.update()

        for root_dir, dirs, files in os.walk(self.path):
            for file in files:
                file_path = os.path.join(root_dir, file)
                try:
                    if any(name in file.lower() for name in wallet_filenames):
                        self.log_match("FILENAME MATCH", file_path)

                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                        if btc_address_pattern.search(content):
                            self.log_match("BTC ADDRESS", file_path)
                        if eth_address_pattern.search(content):
                            self.log_match("ETH ADDRESS", file_path)
                        if hex_private_key_pattern.search(content):
                            self.log_match("POSSIBLE PRIVATE KEY", file_path)
                        if self.is_bip39_phrase(content):
                            self.log_match("BIP39 SEED PHRASE", file_path)
                except:
                    continue

        self.output.insert(tk.END, "\n✅ Scan complete!\n")
        self.save_btn.config(state='normal')

    def save_results(self):
        if not self.matches:
            messagebox.showinfo("No Matches", "Nothing to save.")
            return

        filename = f"crypto_scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.writelines(self.matches)

        messagebox.showinfo("Saved", f"Results saved to {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoScannerApp(root)
    root.mainloop()
