import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import qrcode
from qrcode.image.svg import SvgImage
from io import BytesIO
from urllib.parse import urlparse

import requests
import os
import sys
import subprocess

APP_VERSION = "1.1"



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

        # ------------------------
        # Input field
        # ------------------------
        self.entry = ttk.Entry(root, font=("Arial", 14), width=40)
        self.entry.pack(pady=10)
        self.entry.bind("<KeyRelease>", self.auto_update)
        self.entry.bind("<Control-v>", self.auto_update)
        self.entry.bind("<ButtonRelease>", self.auto_update)

        # ------------------------
        # QR Display Area
        # ------------------------
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
        ttk.Button(root, text="Check for Updates", command=self.check_updates).pack(pady=5)


        # ------------------------
        # Save button
        # ------------------------
        ttk.Button(root, text="Save QR", command=self.save_qr).pack(pady=20)
        
        # Version label
        version_label = ttk.Label(root, text=f"v{APP_VERSION}", foreground="#666")
        version_label.pack(side="bottom", pady=5)



        self.generated_img = None  # store pillow image
        self.generated_svg = None  # store svg bytes

    # ------------------------
    # Auto-generate QR
    # ------------------------
    def auto_update(self, event=None):
        text = self.entry.get().strip()
        if not text:
            self.qr_label.config(image="")
            return
        self.generate_qr(text)

    # ------------------------
    # Generate QR
    # ------------------------
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

    # ------------------------
    # Display QR in GUI
    # ------------------------
    def update_display(self, img):
        img = img.resize((250, 250))
        tk_img = ImageTk.PhotoImage(img)
        self.qr_label.config(image=tk_img)
        self.qr_label.image = tk_img

    # ------------------------
    # Save QR to a file
    # ------------------------
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
