import os
import subprocess
import tkinter as tk
from tkinter import font
import ctypes
from PIL import Image, ImageTk 

# === AUTOMATIC LOCAL PATHS ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICO_PATH = os.path.join(BASE_DIR, "Image", "Clock-in_logo.ico")
FONT_DIR = os.path.join(BASE_DIR, "font", "Bubblegum_Sans,Poppins", "Bubblegum_Sans")

# === PROJECT & BLENDER CONFIG ===
ROOT_DIR = r"D:\Master\Andi"
BLENDER_PATH = r"D:\Master\Andi\File_Software\Blender Foundation\Blender 4.2\blender-launcher.exe"
# Centralized path for all previews
PREVIEW_ROOT = r"D:\Master\Andi\File sekolah\File Project\Preview"

# --- TASKBAR FIX ---
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('andi.clockkit.v1')
except:
    pass

def load_fonts(directory):
    if os.path.exists(directory):
        for f in os.listdir(directory):
            if f.lower().endswith((".ttf", ".otf")):
                path = os.path.join(directory, f)
                ctypes.windll.gdi32.AddFontResourceExW(path, 0x10, 0)

class SmoothButton(tk.Canvas):
    def __init__(self, parent, text, command, width, height, color="#333333", fg="white", radius=22, f_style=None):
        super().__init__(parent, width=width, height=height, bg="#000000", highlightthickness=0)
        self.command = command
        self.color = color
        self.rect = self.draw_smooth_rect(0, 0, width, height, radius, color)
        self.label = self.create_text(width/2, height/2, text=text, fill=fg, font=f_style)
        self.bind("<Button-1>", lambda e: self.command())

    def draw_smooth_rect(self, x, y, w, h, r, color):
        points = [x+r, y, x+w-r, y, x+w, y, x+w, y+r, x+w, y+h-r, x+w, y+h, 
                  x+w-r, y+h, x+r, y+h, x, y+h, x, y+h-r, x, y+r, x, y]
        return self.create_polygon(points, fill=color, smooth=True, splinesteps=48)

class BlenderManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clock-KIT Launcher") 
        self.root.geometry("1100x850")
        self.root.configure(bg="#000000")

        if os.path.exists(ICO_PATH):
            try: self.root.iconbitmap(ICO_PATH)
            except: pass

        load_fonts(FONT_DIR)
        fams = font.families()
        self.h_f = ("Bubblegum Sans", 34) if "Bubblegum Sans" in fams else ("Arial Bold", 34)
        self.m_f = ("Poppins", 10) if "Poppins" in fams else ("Arial", 10)
        self.b_f = ("Poppins SemiBold", 11) if "Poppins SemiBold" in fams else ("Arial Bold", 11)

        tk.Label(root, text="CLOCK-IN WORKFLOW", bg="#000000", fg="#FFFFFF", font=self.h_f).pack(pady=20)

        container = tk.Frame(root, bg="#000000")
        container.pack(fill=tk.BOTH, expand=True, padx=40)

        left_side = tk.Frame(container, bg="#000000")
        left_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        tk.Label(left_side, text="FILE DEPT (SERVER)", fg="#555555", bg="#000000", font=(self.m_f[0], 9, "bold")).pack(anchor="w", pady=5)
        
        self.dept_list = tk.Listbox(left_side, bg="#0D0D0D", fg="#BBBBBB", borderwidth=0, 
                                    highlightthickness=0, font=self.m_f, 
                                    selectbackground="#4772B3", activestyle='none')
        self.dept_list.pack(fill=tk.BOTH, expand=True)
        self.dept_list.bind('<<ListboxSelect>>', self.on_dept_select)

        right_side = tk.Frame(container, bg="#000000")
        right_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))

        tk.Label(right_side, text="PREVIEW", fg="#555555", bg="#000000", font=(self.m_f[0], 9, "bold")).pack(anchor="w", pady=5)
        self.preview_frame = tk.Frame(right_side, bg="#0D0D0D", height=250)
        self.preview_frame.pack(fill=tk.X, pady=(0, 15))
        self.preview_frame.pack_propagate(False) 
        
        self.preview_label = tk.Label(self.preview_frame, text="No Preview Selected", bg="#0D0D0D", fg="#333333")
        self.preview_label.pack(expand=True)

        tk.Label(right_side, text="CONTENTS / FILE SHOT", fg="#555555", bg="#000000", font=(self.m_f[0], 9, "bold")).pack(anchor="w", pady=5)
        
        self.content_list = tk.Listbox(right_side, bg="#0D0D0D", fg="#BBBBBB", borderwidth=0, 
                                       highlightthickness=0, font=self.m_f, 
                                       selectbackground="#4772B3", activestyle='none')
        self.content_list.pack(fill=tk.BOTH, expand=True)
        self.content_list.bind('<<ListboxSelect>>', self.update_preview)

        toolbar = tk.Frame(root, bg="#000000")
        toolbar.pack(fill=tk.X, padx=40, pady=30)

        SmoothButton(toolbar, "🚀 LOAD SCENE", self.launch_blender, 220, 45, color="#4772B3", f_style=self.b_f).pack(side=tk.RIGHT, padx=(10, 0))
        SmoothButton(toolbar, "Open Folder", self.enter_folder, 140, 40, color="#222222", f_style=self.m_f).pack(side=tk.RIGHT, padx=5)
        SmoothButton(toolbar, "Back", self.go_back, 100, 40, color="#222222", f_style=self.m_f).pack(side=tk.RIGHT, padx=5)

        self.current_dept_path = ROOT_DIR
        self.refresh_depts()

    # --- UPDATED: LOOKS IN CENTRAL PREVIEW FOLDER ---
    def update_preview(self, e):
        sel = self.content_list.curselection()
        if not sel: return
        filename = self.content_list.get(sel[0])[4:].strip()
        name_no_ext = os.path.splitext(filename)[0]
        
        # Path to the specific shot's folder inside the central Preview directory
        shot_preview_folder = os.path.join(PREVIEW_ROOT, name_no_ext)
        img_path = None
        
        if os.path.exists(shot_preview_folder):
            images = [os.path.join(shot_preview_folder, f) for f in os.listdir(shot_preview_folder) 
                      if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            if images:
                # Grab the newest version of the capture
                img_path = max(images, key=os.path.getmtime) 

        if img_path:
            try:
                img = Image.open(img_path)
                
                # Aspect Ratio Calculation (Proportional Resize)
                orig_w, orig_h = img.size
                aspect = orig_w / orig_h
                
                target_w = 450
                new_h = int(target_w / aspect)
                
                photo_img = img.resize((target_w, new_h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(photo_img)
                
                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo 
            except:
                self.preview_label.config(image='', text="Error Loading Image")
        else:
            self.preview_label.config(image='', text="No Preview Available")

    def refresh_depts(self):
        self.dept_list.delete(0, tk.END)
        if os.path.exists(ROOT_DIR):
            for item in sorted(os.listdir(ROOT_DIR)):
                if os.path.isdir(os.path.join(ROOT_DIR, item)):
                    if not item.startswith(".") and "Software" not in item:
                        self.dept_list.insert(tk.END, f"  {item}")
        else:
            self.dept_list.insert(tk.END, "  D: Drive Not Found")

    def on_dept_select(self, e):
        sel = self.dept_list.curselection()
        if sel:
            name = self.dept_list.get(sel[0]).strip()
            self.current_dept_path = os.path.join(ROOT_DIR, name)
            self.refresh_contents()

    def refresh_contents(self):
        self.content_list.delete(0, tk.END)
        try:
            for f in sorted(os.listdir(self.current_dept_path)):
                icon = "  📁 " if os.path.isdir(os.path.join(self.current_dept_path, f)) else "  🎨 "
                if os.path.isdir(os.path.join(self.current_dept_path, f)) or f.lower().endswith(".blend"):
                    self.content_list.insert(tk.END, f"{icon}{f}")
        except: pass

    def enter_folder(self):
        sel = self.content_list.curselection()
        if sel:
            name = self.content_list.get(sel[0])[4:].strip()
            new_p = os.path.join(self.current_dept_path, name)
            if os.path.isdir(new_p):
                self.current_dept_path = new_p
                self.refresh_contents()

    def go_back(self):
        parent = os.path.dirname(self.current_dept_path)
        if len(parent) >= len(ROOT_DIR):
            self.current_dept_path = parent
            self.refresh_contents()

    def launch_blender(self):
        sel = self.content_list.curselection()
        if sel:
            name = self.content_list.get(sel[0])[4:].strip()
            full_p = os.path.join(self.current_dept_path, name)
            mgr_script = os.path.join(BASE_DIR, "shot_manager.py")
            lib_script = os.path.join(BASE_DIR, "Plug-in", "Clock-in-lib.py")
            
            if os.path.exists(BLENDER_PATH) and name.lower().endswith(".blend"):
                python_cmd = (
                    f"import bpy; "
                    f"exec(open({repr(mgr_script)}).read()); "
                    f"exec(open({repr(lib_script)}).read())"
                )
                subprocess.Popen([BLENDER_PATH, full_p, "--python-expr", python_cmd])

if __name__ == "__main__":
    root = tk.Tk()
    app = BlenderManager(root)
    root.mainloop()