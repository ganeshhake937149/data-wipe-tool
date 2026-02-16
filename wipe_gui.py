import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import random
import string

# Data wipe methods
WIPE_METHODS = {
    "Zero (2 Passes)": ["\x00", "\x00"],
    "US DOD (3 Passes)": ["\x00", "\xFF", "\x00"],
    "British HMG IS5 (3 Passes)": ["\xFF", "\x00", "\xAA"],
    "Russian GOST-R-50739-95 (3 Passes)": ["\x00", "\xFF", "\x00"],
    "NATO Standard (7 Passes)": ["\x00", "\xFF", "\x00", "\xFF", "\x00", "\xFF", "\x00"],
    "Peter Gutmann (35 Passes)": ["\xAA"] * 35
}

# Generate random file/folder names
def random_filename(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Securely wipe a file
def wipe_file(file_path, method):
    if not os.path.isfile(file_path):
        return False

    size = os.path.getsize(file_path)
    dir_name = os.path.dirname(file_path)
    try:
        with open(file_path, "r+b") as f:
            for pattern in WIPE_METHODS[method]:
                f.seek(0)
                f.write(bytes(pattern * size, encoding="latin-1"))
                f.flush()
                os.fsync(f.fileno())

        # Rename the file multiple times
        for _ in range(3):
            new_name = random_filename(len(os.path.basename(file_path)))
            new_path = os.path.join(dir_name, new_name)
            os.rename(file_path, new_path)
            file_path = new_path

        os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error wiping {file_path}: {e}")
        return False

# Wipe selection based on type
def wipe_selection(selection_type):
    method = method_var.get()
    if not method:
        messagebox.showerror("Error", "Please select a wipe method")
        return

    if selection_type == "File":
        path = filedialog.askopenfilename()
        if path:
            if wipe_file(path, method):
                messagebox.showinfo("Success", f"Wiped file: {path}")
    elif selection_type == "Folder":
        folder = filedialog.askdirectory()
        if folder:
            success = True
            for root, dirs, files in os.walk(folder, topdown=False):
                # Wipe all files
                for name in files:
                    file_path = os.path.join(root, name)
                    if not wipe_file(file_path, method):
                        success = False

                # Rename and delete subfolders
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    try:
                        for _ in range(3):
                            new_name = random_filename(len(d))
                            new_path = os.path.join(root, new_name)
                            os.rename(dir_path, new_path)
                            dir_path = new_path
                        os.rmdir(dir_path)
                    except Exception as e:
                        print(f"Failed to remove folder {dir_path}: {e}")
                        success = False

            # Rename and delete main folder
            try:
                for _ in range(3):
                    new_name = random_filename(len(os.path.basename(folder)))
                    new_path = os.path.join(os.path.dirname(folder), new_name)
                    os.rename(folder, new_path)
                    folder = new_path
                os.rmdir(folder)
            except Exception as e:
                print(f"Failed to remove main folder {folder}: {e}")
                success = False

            if success:
                messagebox.showinfo("Success", "Folder and all contents securely wiped.")
            else:
                messagebox.showerror("Partial Success", "Some files or subfolders could not be wiped.")
    elif selection_type in ["Disk", "Pen Drive"]:
        messagebox.showwarning("Not Supported", f"{selection_type} wipe not supported via Python GUI. Use dedicated tools like DBAN or PartedMagic.")

# GUI setup
root = tk.Tk()
root.title("Secure Data Wiper")
root.geometry("400x500")
root.configure(bg="#f0f0f0")

method_var = tk.StringVar()

tk.Label(root, text="\n Welcome to GAM Data-Wiper \n\n Select Wipe Method:", bg="#f0f0f0", font=("Arial", 12, "bold")).pack(pady=10)
method_menu = tk.OptionMenu(root, method_var, *WIPE_METHODS.keys())
method_menu.config(width=30)
method_menu.pack(pady=5)

# Load icon images
def load_icon(path):
    try:
        image = Image.open(path)
        image = image.resize((48, 48), Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Failed to load icon: {path} - {e}")
        return None

file_icon = load_icon("file_icon.png")
folder_icon = load_icon("folder_icon.png")
disk_icon = load_icon("disk_icon.png")
pendrive_icon = load_icon("usb_icon.png")

# Create icon-styled buttons
def create_icon_button(image, label, action_type):
    return tk.Button(
        root,
        image=image,
        text=label,
        compound="left",
        width=200,
        padx=10,
        anchor="w",
        command=lambda: wipe_selection(action_type),
        font=("Arial", 10),
        bg="#007acc",
        fg="white",
        activebackground="#005f9e",
        relief="raised",
        bd=2
    )

create_icon_button(disk_icon, "  Disk", "Disk").pack(pady=7)
create_icon_button(pendrive_icon, "  Pen Drive", "Pen Drive").pack(pady=7)
create_icon_button(file_icon, "  File", "File").pack(pady=7)
create_icon_button(folder_icon, "  Folder", "Folder").pack(pady=7)

root.mainloop()
