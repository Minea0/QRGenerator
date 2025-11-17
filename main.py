import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk
import qrcode
from qrcode.image.svg import SvgImage
from io import BytesIO
from urllib.parse import urlparse

import tempfile
import zipfile
import shutil

import requests
import os
import sys
import subprocess
import webbrowser

APP_VERSION = "1.0.1"
UPDATE_URL = "https://raw.githubusercontent.com/Minea0/QRGenerator/main/latest_version.txt"
ZIP_URL = "https://github.com/Minea0/QRGenerator/releases/download/v1.0.1/QRGenerator-1.0.1.zip"



# ------------------------
# Utility functions
# ------------------------

def normalize_url(link: str) -> str:
    parsed = urlparse(link)
    if not parsed.scheme:
        return "http://" + link
    return link

EC_LEVELS = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H
}

# ------------------------
# Main Application
# ------------------------

class QRGui:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Generator")
        self.root.geometry("450x650")
        self.root.resizable(False, False)

        # Default settings
        self.box_size = tk.IntVar(value=10)
        self.border_size = tk.IntVar(value=4)
        self.ec_level = tk.StringVar(value="M")
        self.format = tk.StringVar(value="png")


        # Input field
        self.entry = ttk.Entry(root, font=("Arial", 14), width=40)
        self.entry.pack(pady=10)
        self.entry.bind("<KeyRelease>", self.auto_update)
        self.entry.bind("<Control-v>", self.auto_update)
        self.entry.bind("<ButtonRelease>", self.auto_update)
        self.entry.focus_set()


        # QR Display Area
        self.qr_label = ttk.Label(root)
        self.qr_label.pack(pady=10)

        # ------------------------
        # Settings Section
        # Any change in settings should regenerate the QR
        def _settings_changed(*args):
            self.auto_update()

        self.box_size.trace_add('write', _settings_changed)
        self.border_size.trace_add('write', _settings_changed)
        self.ec_level.trace_add('write', _settings_changed)
        self.format.trace_add('write', _settings_changed)
        # ------------------------
        settings_frame = ttk.LabelFrame(root, text="Settings")
        settings_frame.pack(pady=10, fill="x", padx=10)

        ttk.Label(settings_frame, text="Error Correction:").pack(anchor="w")
        ttk.Combobox(settings_frame, textvariable=self.ec_level, values=["L", "M", "Q", "H"], state="readonly").pack(fill="x")

        ttk.Label(settings_frame, text="Box Size (px):").pack(anchor="w", pady=(5,0))
        ttk.Spinbox(settings_frame, from_=5, to=50, textvariable=self.box_size).pack(fill="x")

        ttk.Label(settings_frame, text="Border Size:").pack(anchor="w", pady=(5,0))
        ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.border_size).pack(fill="x")

        ttk.Label(settings_frame, text="Format:").pack(anchor="w", pady=(5,0))
        ttk.Combobox(settings_frame, textvariable=self.format, values=["png", "svg"], state="readonly").pack(fill="x")

        # Save button
        ttk.Button(root, text="Save QR", command=self.save_qr).pack(pady=20)
        


        # version and update tooltip
        footer = tk.Frame(root)
        footer.pack(side="bottom", pady=5)

        version_label = tk.Label(footer, text=f"v{APP_VERSION}", fg="#666")
        version_label.pack(side="left")

        link = tk.Label(footer, text="Check for updates", fg="blue", cursor="hand2")
        link.pack(side="left", padx=10)
        link.bind("<Button-1>", lambda e: self.check_updates())



        self.generated_img = None  # store pillow image
        self.generated_svg = None  # store svg bytes


    #handle update checking
    def check_updates(self):
        try:
            latest = requests.get(UPDATE_URL, timeout=5).text.strip()
        except:
            tk.messagebox.showerror("Update check failed", "Cannot contact update server.")
            return

        if latest == APP_VERSION:
            tk.messagebox.showinfo("Up to date", "You already have the latest version.")
            return

        if not tk.messagebox.askyesno("Update available",
                f"A new version ({latest}) is available. Install?"):
            return

        try:
            temp_zip = os.path.join(tempfile.gettempdir(), "QRGenerator_Update.zip")
            with open(temp_zip, "wb") as f:
                f.write(requests.get(ZIP_URL, timeout=10).content)

            extract_path = os.path.join(tempfile.gettempdir(), "QRGenerator_Update")
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)

            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            install_path = os.path.dirname(sys.argv[0])

            # copy over new files
            for rootdir, dirs, files in os.walk(extract_path):
                rel = os.path.relpath(rootdir, extract_path)
                dest = os.path.join(install_path, rel)
                if not os.path.exists(dest):
                    os.makedirs(dest)
                for file in files:
                    shutil.copy2(os.path.join(rootdir, file),
                                os.path.join(dest, file))

            tk.messagebox.showinfo("Update installed", "Restart the program to finish updating.")
            self.root.quit()

        except Exception as e:
            tk.messagebox.showerror("Update failed", str(e))





    # Auto-generate QR
    def auto_update(self, event=None):
        text = self.entry.get().strip()
        if not text:
            self.qr_label.config(image="")
            return
        self.generate_qr(text)


    # Generate QR
    def generate_qr(self, link):
        link = normalize_url(link)
        qr = qrcode.QRCode(
            version=None,
            error_correction=EC_LEVELS[self.ec_level.get()],
            box_size=self.box_size.get(),
            border=self.border_size.get(),
        )
        qr.add_data(link)
        qr.make(fit=True)

        if self.format.get() == "svg":
            # SVG output stored but PNG for display
            img_svg = qr.make_image(image_factory=SvgImage)
            svg_buffer = BytesIO()
            img_svg.save(svg_buffer)
            self.generated_svg = svg_buffer.getvalue()

            # For display convert to PNG
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        else:
            # PNG only
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            self.generated_svg = None

        self.generated_img = img
        self.update_display(img)


    # Display QR in GUI
    def update_display(self, img):
        img = img.resize((250, 250))
        tk_img = ImageTk.PhotoImage(img)
        self.qr_label.config(image=tk_img)
        self.qr_label.image = tk_img


    # Save QR to a file
    def save_qr(self):
        if self.generated_img is None and self.generated_svg is None:
            return

        fmt = self.format.get()
        filetypes = [(fmt.upper(), f"*.{fmt}")]
        path = filedialog.asksaveasfilename(defaultextension=f".{fmt}", filetypes=filetypes)
        if not path:
            return

        if fmt == "svg" and self.generated_svg is not None:
            with open(path, "wb") as f:
                f.write(self.generated_svg)
        else:
            self.generated_img.save(path)


# ------------------------
# Run the app
# ------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = QRGui(root)
    root.mainloop()
