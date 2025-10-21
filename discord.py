# discord_bypass_vn_fix.py
# Phiên bản: Đặt nút Copy ngay cạnh tiêu đề Script Bypass.

import os
import json
import time
import threading
import subprocess
import psutil
import pyperclip
import pyautogui
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys

# Cố gắng import pygetwindow / win32 để focus cửa sổ Discord
HAS_PYGETWINDOW = False
HAS_WIN32 = False
try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except Exception:
    pass

try:
    import win32gui
    import win32con
    HAS_WIN32 = True
except Exception:
    pass

# === CẤU HÌNH ===
# Tăng nhẹ độ trễ để Discord UI ổn định hơn trước khi thao tác phím
AUTO_DELAY_AFTER_UI = 10 
PROCESS_WAIT_TIMEOUT = 25  # timeout chờ tiến trình Discord xuất hiện

# --- NỘI DUNG SCRIPT MẪU ---
SCRIPT_FULL = '''delete window.$;
let wpRequire = webpackChunkdiscord_app.push([[Symbol()], {}, r => r]);
webpackChunkdiscord_app.pop();

let ApplicationStreamingStore = Object.values(wpRequire.c).find(x => x?.exports?.Z?.__proto__?.getStreamerActiveStreamMetadata).exports.Z;
let RunningGameStore = Object.values(wpRequire.c).find(x => x?.exports?.ZP?.getRunningGames).exports.ZP;
let QuestsStore = Object.values(wpRequire.c).find(x => x?.exports?.Z?.__proto__?.getQuest).exports.Z;
let ChannelStore = Object.values(wpRequire.c).find(x => x?.exports?.Z?.__proto__?.getAllThreadsForParent).exports.Z;
let GuildChannelStore = Object.values(wpRequire.c).find(x => x?.exports?.ZP?.getSFWDefaultChannel).exports.ZP;
let FluxDispatcher = Object.values(wpRequire.c).find(x => x?.exports?.Z?.__proto__?.flushWaitQueue).exports.Z;
let api = Object.values(wpRequire.c).find(x => x?.exports?.tn?.get).exports.tn;

let quest = [...QuestsStore.quests.values()].find(x => x.id !== "1412491570820812933" && x.userStatus?.enrolledAt && !x.userStatus?.completedAt && new Date(x.config.expiresAt).getTime() > Date.now())
let isApp = typeof DiscordNative !== "undefined"
if(!quest) {
	console.log("You don't have any uncompleted quests!")
} else {
	const pid = Math.floor(Math.random() * 30000) + 1000
	
	const applicationId = quest.config.application.id
	const applicationName = quest.config.application.name
	const questName = quest.config.messages.questName
	const taskConfig = quest.config.taskConfig ?? quest.config.taskConfigV2
	const taskName = ["WATCH_VIDEO", "PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP", "PLAY_ACTIVITY", "WATCH_VIDEO_ON_MOBILE"].find(x => taskConfig.tasks[x] != null)
	const secondsNeeded = taskConfig.tasks[taskName].target
	let secondsDone = quest.userStatus?.progress?.[taskName]?.value ?? 0

	if(taskName === "WATCH_VIDEO" || taskName === "WATCH_VIDEO_ON_MOBILE") {
		const maxFuture = 10, speed = 7, interval = 1
		const enrolledAt = new Date(quest.userStatus.enrolledAt).getTime()
		let completed = false
		let fn = async () => {			
			while(true) {
				const maxAllowed = Math.floor((Date.now() - enrolledAt)/1000) + maxFuture
				const diff = maxAllowed - secondsDone
				const timestamp = secondsDone + speed
				if(diff >= speed) {
					const res = await api.post({url: `/quests/${quest.id}/video-progress`, body: {timestamp: Math.min(secondsNeeded, timestamp + Math.random())}})
					completed = res.body.completed_at != null
					secondsDone = Math.min(secondsNeeded, timestamp)
				}
				
				if(timestamp >= secondsNeeded) {
					break
				}
				await new Promise(resolve => setTimeout(resolve, interval * 1000))
			}
			if(!completed) {
				await api.post({url: `/quests/${quest.id}/video-progress`, body: {timestamp: secondsNeeded}})
			}
			console.log("Quest completed!")
		}
		fn()
		console.log(`Spoofing video for ${questName}.`)
	} else if(taskName === "PLAY_ON_DESKTOP") {
		if(!isApp) {
			console.log("This no longer works in browser for non-video quests. Use the discord desktop app to complete the", questName, "quest!")
		} else {
			api.get({url: `/applications/public?application_ids=${applicationId}`}).then(res => {
				const appData = res.body[0]
				const exeName = appData.executables.find(x => x.os === "win32").name.replace(">","")
				
				const fakeGame = {
					cmdLine: `C:\\Program Files\\${appData.name}\\${exeName}`,
					exeName,
					exePath: `c:/program files/${appData.name.toLowerCase()}/${exeName}`,
					hidden: false,
					isLauncher: false,
					id: applicationId,
					name: appData.name,
					pid: pid,
					pidPath: [pid],
					processName: appData.name,
					start: Date.now(),
				}
				const realGames = RunningGameStore.getRunningGames()
				const fakeGames = [fakeGame]
				const realGetRunningGames = RunningGameStore.getRunningGames
				const realGetGameForPID = RunningGameStore.getGameForPID
				RunningGameStore.getRunningGames = () => fakeGames
				RunningGameStore.getGameForPID = (pid) => fakeGames.find(x => x.pid === pid)
				FluxDispatcher.dispatch({type: "RUNNING_GAMES_CHANGE", removed: realGames, added: [fakeGame], games: fakeGames})
				
				let fn = data => {
					let progress = quest.config.configVersion === 1 ? data.userStatus.streamProgressSeconds : Math.floor(data.userStatus.progress.PLAY_ON_DESKTOP.value)
					console.log(`Quest progress: ${progress}/${secondsNeeded}`)
					
					if(progress >= secondsNeeded) {
						console.log("Quest completed!")
						
						RunningGameStore.getRunningGames = realGetRunningGames
						RunningGameStore.getGameForPID = realGetGameForPID
						FluxDispatcher.dispatch({type: "RUNNING_GAMES_CHANGE", removed: [fakeGame], added: [], games: []})
						FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn)
					}
				}
				FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn)
				
				console.log(`Spoofed your game to ${applicationName}. Wait for ${Math.ceil((secondsNeeded - secondsDone) / 60)} more minutes.`)
			})
		}
	} else if(taskName === "STREAM_ON_DESKTOP") {
		if(!isApp) {
			console.log("This no longer works in browser for non-video quests. Use the discord desktop app to complete the", questName, "quest!")
		} else {
			let realFunc = ApplicationStreamingStore.getStreamerActiveStreamMetadata
			ApplicationStreamingStore.getStreamerActiveStreamMetadata = () => ({
				id: applicationId,
				pid,
				sourceName: null
			})
			
			let fn = data => {
				let progress = quest.config.configVersion === 1 ? data.userStatus.streamProgressSeconds : Math.floor(data.userStatus.progress.STREAM_ON_DESKTOP.value)
				console.log(`Quest progress: ${progress}/${secondsNeeded}`)
				
				if(progress >= secondsNeeded) {
					console.log("Quest completed!")
					
					ApplicationStreamingStore.getStreamerActiveStreamMetadata = realFunc
					FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn)
				}
			}
			FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn)
			
			console.log(`Spoofed your stream to ${applicationName}. Stream any window in vc for ${Math.ceil((secondsNeeded - secondsDone) / 60)} more minutes.`)
			console.log("Remember that you need at least 1 other person to be in the vc!")
		}
	} else if(taskName === "PLAY_ACTIVITY") {
		const channelId = ChannelStore.getSortedPrivateChannels()[0]?.id ?? Object.values(GuildChannelStore.getAllGuilds()).find(x => x != null && x.VOCAL.length > 0).VOCAL[0].channel.id
		const streamKey = `call:${channelId}:1`
		
		let fn = async () => {
			console.log("Completing quest", questName, "-", quest.config.messages.questName)
			
			while(true) {
				const res = await api.post({url: `/quests/${quest.id}/heartbeat`, body: {stream_key: streamKey, terminal: false}})
				const progress = res.body.progress.PLAY_ACTIVITY.value
				console.log(`Quest progress: ${progress}/${secondsNeeded}`)
				
				await new Promise(resolve => setTimeout(resolve, 20 * 1000))
				
				if(progress >= secondsNeeded) {
					await api.post({url: `/quests/${quest.id}/heartbeat`, body: {stream_key: streamKey, terminal: true}})
					break
				}
			}
			
			console.log("Quest completed!")
		}
		fn()
	}
}'''

# ---------------- HELPERS ----------------

def tim_duong_dan_settings():
    localappdata = os.getenv("LOCALAPPDATA")
    appdata = os.getenv("APPDATA")
    duongdan = []
    if appdata:
        for build in ["discord", "discordcanary", "discordptb"]:
            duongdan.append(os.path.join(appdata, build))
    if localappdata:
        for build in ["Discord", "DiscordCanary", "DiscordPTB"]:
            duongdan.append(os.path.join(localappdata, build))
    for d in duongdan:
        path = os.path.join(d, "settings.json")
        if os.path.exists(path):
            return path
    return None

def bat_devtools_trong_settings(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return False, f"Không thể đọc settings.json: {e}"
    try:
        # Hỗ trợ nhiều build/version của Discord
        data["DANGEROUS_ENABLE_DEVTOOLS_ONLY_ENABLE_IF_YOURE_A_DEV"] = True 
        data["DANGEROUS_ENABLE_DEVTOOLS_ONLY_ENABLE_IF_YOU_KNOW_WHAT_YOURE_DOING"] = True
        data["IS_DEVTOOLS_ENABLED"] = True
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True, path
    except Exception as e:
        return False, f"Không thể ghi settings.json: {e}"

def tim_update_exe():
    localappdata = os.getenv("LOCALAPPDATA")
    if localappdata:
        for build in ["Discord", "DiscordCanary", "DiscordPTB"]:
            update_exe = os.path.join(localappdata, build, "Update.exe")
            if os.path.exists(update_exe):
                return update_exe, build
    return None, "Không tìm thấy"

def tat_tien_trinh_discord():
    so_luong = 0
    current_pid = os.getpid()
    current_name = os.path.basename(sys.executable).lower()
    for p in psutil.process_iter(['name', 'exe', 'pid']):
        try:
            pid = p.info.get('pid')
            if pid == current_pid:
                continue
            pname = (p.info.get('name') or '').lower()
            pexe = (p.info.get('exe') or '').lower()
            if pname == current_name or current_name in pexe:
                continue
            if 'discord' in pname or 'update.exe' in pname or 'discord' in pexe:
                try:
                    p.kill()
                    so_luong += 1
                except Exception:
                    pass
        except Exception:
            continue
    return so_luong

def doi_discord_khoi_dong(timeout=PROCESS_WAIT_TIMEOUT):
    start = time.time()
    while time.time() - start < timeout:
        for p in psutil.process_iter(['name']):
            if 'discord' in (p.info.get('name', '') or '').lower():
                return True
        time.sleep(0.5)
    return False

def mo_discord(update_exe):
    try:
        process_name = "Discord.exe"
        subprocess.Popen([update_exe, "--processStart", process_name], shell=False, close_fds=False)
        time.sleep(1)
        return True, "Đã mở"
    except Exception as e:
        return False, str(e)

def focus_discord_window_best_effort(max_retries=3, delay_between_retry=0.3):
    """
    Cố gắng tìm và focus cửa sổ Discord. Thử lại nhiều lần để tăng độ tin cậy.
    """
    if not (HAS_PYGETWINDOW or HAS_WIN32):
        return False

    for i in range(max_retries):
        try:
            if HAS_PYGETWINDOW:
                titles = [t for t in gw.getAllTitles() if t and ('Discord' in t or 'Electron' in t)]
                if titles:
                    w = gw.getWindowsWithTitle(titles[0])[0]
                    if w.isMinimized:
                        w.restore()
                    w.activate()
                    return True
            
            elif HAS_WIN32:
                wins = []
                def enum_cb(hwnd, ctx):
                    txt = win32gui.GetWindowText(hwnd)
                    if txt and ('Discord' in txt or 'Electron' in txt):
                        ctx.append(hwnd)
                win32gui.EnumWindows(enum_cb, wins)
                
                if wins:
                    hwnd = wins[0]
                    if not win32gui.IsWindowVisible(hwnd):
                         win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    return True
        except Exception:
            pass
        
        time.sleep(delay_between_retry)
        
    return False

def tu_dong_mo_console_va_allow_pasting(log_fn, delay=AUTO_DELAY_AFTER_UI):
    """
    Tự động hóa DevTools sau khi Discord đã khởi động
    """
    log_fn(f"⌛ Chờ {delay}s để giao diện Discord ổn định...", "yellow")
    time.sleep(delay)
    
    # --- Logic Focus: Chỉ Focus NGAY TRƯỚC KHI gửi phím ---
    log_fn("🔍 Đang cố gắng Focus cửa sổ Discord...", "cyan")
    
    # Tăng retries và giảm delay để tập trung vào việc focus nhanh và chắc chắn
    ok_focus = focus_discord_window_best_effort(max_retries=5, delay_between_retry=0.1)

    if not ok_focus:
        log_fn("⚠️ CẢNH BÁO: KHÔNG THỂ FOCUS cửa sổ tự động.", "red")
        log_fn("⚠️ Vui lòng click vào Discord và sau đó nhấn **Ctrl+Shift+I** thủ công.", "red")
        time.sleep(3) # Cho người dùng 3s để tự thao tác

    # --- Thao tác DevTools ---
    try:
        if ok_focus:
             log_fn("✅ Focus thành công. Gửi Ctrl+Shift+I...", "green")
        
        pyautogui.hotkey("ctrl", "shift", "i")
        time.sleep(1.6)
        
        log_fn("⌨️ Clear console (Ctrl+L)...", "cyan")
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.6)
        
        log_fn("⌨️ Gõ 'allow pasting' → Enter...", "cyan")
        pyautogui.typewrite("'allow pasting'", interval=0.04)
        pyautogui.press("enter")
        time.sleep(0.4)
        
        log_fn("🎉 Hoàn tất! DevTools Console đã mở, sẵn sàng để DÁN Script.", "green")
    except Exception as e:
        log_fn(f"❌ Lỗi tự động DevTools: {e}", "red")
        log_fn("⚠️ Thao tác tự động thất bại. Vui lòng thực hiện thủ công.", "red")


# --- GIAO DIỆN CHÍNH ---

class GiaoDienDiscord:
    def __init__(self, root):
        self.root = root
        root.title("Công cụ Discord DevTools (Bypass Quest)")
        # Kích thước GUI
        root.geometry("1000x880") 

        self.path_settings = tim_duong_dan_settings()
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        style = ttk.Style()
        style.theme_use('clam')

        main = ttk.Frame(root, padding=12)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="🚀 BẬT DEVTOOLS & BYPASS QUEST", font=("Segoe UI", 16, "bold")).pack(pady=(6,10))

        self.trangthai = ttk.Label(main, text="Đang kiểm tra tệp cấu hình Discord...", foreground="orange")
        self.trangthai.pack(pady=4)

        nut_frame = ttk.Frame(main)
        nut_frame.pack(fill="x", pady=8)

        self.nut_bat = ttk.Button(nut_frame, text="1. Kích hoạt DevTools", command=self.bat_devtools)
        self.nut_bat.pack(side="left", padx=6, expand=True)

        self.nut_khoi_dong = ttk.Button(nut_frame, text="2. Bắt đầu/Tải lại Bypass", command=self.bat_qua_trinh_khoi_dong)
        self.nut_khoi_dong.pack(side="left", padx=6, expand=True)

        ttk.Separator(main).pack(fill="x", pady=10)

        # --- HƯỚNG DẪN CẬP NHẬT ---
        hd_frame = ttk.LabelFrame(main, text="HƯỚNG DẪN CHI TIẾT", padding=10)
        hd_frame.pack(fill="x", pady=6)
        
        huongdan = f"""
        **BƯỚC CHUẨN BỊ (TRONG DISCORD)**
        1️Mở Discord (App Desktop).
        2️**NHẬN QUEST TRƯỚC:** Hãy chắc chắn bạn đã nhấn **“Chấp nhận nhiệm vụ”** Quest muốn làm.

        **BƯỚC THỰC HIỆN (TRONG TOOL NÀY)**
        3️Click "**1. Kích hoạt DevTools**". (Tool tự động sửa settings.json)
        4️Click "**2. Bắt đầu/Tải lại Bypass**". (Tool sẽ tắt và mở lại Discord)
        5️**COPY SCRIPT Ở PHÍA DƯỚI:** Click nút Copy Script hoặc **Ctrl+C** trên ô Script.

        **BƯỚC HOÀN THÀNH (TRONG DISCORD) - TỰ ĐỘNG SAU {AUTO_DELAY_AFTER_UI} GIÂY:**
        6️Tool tự động **Focus** Discord, mở Console (**Ctrl+Shift+I**), Clear Console (**Ctrl+L**) và gõ **`allow pasting`**.
        7️Dán Script đã Copy (**Ctrl+V**) → **Enter** vào Console đang mở.
        
        **QUAN TRỌNG:** Tool cần **giữ MỞ** để Discord không bị tắt trong quá trình Bypass!"""
        
        tk.Label(hd_frame, text=huongdan, justify="left", font=("Consolas", 10), wraplength=950).pack(fill="x")

        # --- LOG ---
        self.logbox = scrolledtext.ScrolledText(main, height=8, font=("Consolas", 9), bg="#1e1e1e", fg="white", wrap="word")
        self.logbox.pack(fill="x", expand=False, pady=(8,10))
        self.logbox.tag_config("green", foreground="#39ff14")
        self.logbox.tag_config("red", foreground="#ff4444")
        self.logbox.tag_config("yellow", foreground="#ffff00")
        self.logbox.tag_config("cyan", foreground="#00ffff")
        self.logbox.tag_config("white", foreground="white")
        self.logbox.config(state="disabled")

        # --- SCRIPT ---
        
        # KHUNG CHỨA TIÊU ĐỀ VÀ NÚT COPY
        script_header_frame = ttk.Frame(main, padding=(0, 0, 0, 4))
        script_header_frame.pack(fill="x")

        # THÊM NÚT COPY VÀ ĐẶT BÊN PHẢI
        copy_btn = ttk.Button(script_header_frame, text="💾 Copy Script", command=self.copy_script_button)
        copy_btn.pack(side="right", padx=6)
        
        # TIÊU ĐỀ SCRIPT (LabelFrame không thể dùng trong trường hợp này, dùng Label thường)
        ttk.Label(script_header_frame, 
                  text="SCRIPT BYPASS (Ctrl+C để copy / Click nút Copy)", 
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=6)
        
        # KHUNG CHỨA TEXT BOX (để Textbox vẫn có đường viền)
        script_container_frame = ttk.Frame(main, borderwidth=1, relief="sunken")
        script_container_frame.pack(fill="both", expand=True, pady=(0, 4))
        
        self.script_text = tk.Text(script_container_frame, height=10, font=("Consolas", 10), wrap="none", padx=6, pady=6)
        self.script_text.pack(fill="both", expand=True, side="top")
        
        xscroll = tk.Scrollbar(script_container_frame, orient='horizontal', command=self.script_text.xview)
        xscroll.pack(fill='x', side='bottom')
        self.script_text['xscrollcommand'] = xscroll.set

        self.script_text.insert("1.0", SCRIPT_FULL)
        self.script_text.config(state="disabled", bg="#f0f0f0", fg="black")

        self.script_text.bind("<Control-c>", self.copy_script_binding)


        self.kiemtra_trangthai()
        self.ghi_log("✅ Công cụ sẵn sàng.", "green")

    # ---------- UI helpers ----------
    def kiemtra_trangthai(self):
        update_exe, loai = tim_update_exe()
        color = "green" if update_exe else "red"
        self.trangthai.config(text=f"Update.exe: {loai}", foreground=color)

    def ghi_log(self, msg, color="white"):
        ts = time.strftime("%H:%M:%S")
        try:
            self.logbox.config(state="normal")
            self.logbox.insert("end", f"[{ts}] {msg}\n", color)
            self.logbox.config(state="disabled")
            self.logbox.see("end")
        except Exception:
            pass

    def copy_script_binding(self, event=None):
        try:
            content = self.script_text.get("1.0", "end-1c")
            pyperclip.copy(content)
            self.ghi_log("✅ Đã copy Script Bypass (Ctrl+C).", "green")
        except Exception as e:
            self.ghi_log(f"❌ Lỗi copy script: {e}", "red")
        return "break"

    def copy_script_button(self):
        # Gọi lại hàm xử lý copy
        self.copy_script_binding() 

    # ---------- Actions ----------
    def bat_devtools(self):
        self.ghi_log("🔧 Đang kích hoạt DevTools trong settings.json...", "yellow")
        if not self.path_settings:
            self.ghi_log("❌ Không tìm thấy settings.json. Hãy mở Discord trước.", "red")
            messagebox.showerror("Lỗi", "Không tìm thấy settings.json. Vui lòng mở Discord App trước.")
            return
        ok, msg = bat_devtools_trong_settings(self.path_settings)
        if ok:
            self.ghi_log(f"✅ Đã bật DevTools: {os.path.basename(msg)}", "green")
            messagebox.showinfo("Thành công", "DevTools đã được bật. Tiếp tục bước 2.")
        else:
            self.ghi_log(f"❌ Lỗi khi bật DevTools: {msg}", "red")
            messagebox.showerror("Lỗi", f"Lỗi: {msg}")

    def bat_qua_trinh_khoi_dong(self):
        self.nut_bat.config(state="disabled")
        self.nut_khoi_dong.config(state="disabled", text="Đang khởi động lại...")
        threading.Thread(target=self.khoi_dong_lai_discord, daemon=True).start()

    def khoi_dong_lai_discord(self):
        self.ghi_log("🧩 Đang tắt các tiến trình Discord (safe kill)...", "yellow")
        so = tat_tien_trinh_discord()
        self.ghi_log(f"⚠️ Đã tắt {so} tiến trình (nếu có).", "yellow")
        time.sleep(0.8)

        update_exe, loai = tim_update_exe()
        if not update_exe:
            self.ghi_log("❌ Không tìm thấy Update.exe. Hủy.", "red")
            messagebox.showerror("Lỗi", "Không tìm thấy Update.exe. Kiểm tra cài đặt Discord.")
            self.nut_bat.config(state="normal")
            self.nut_khoi_dong.config(state="normal", text="2. Bắt đầu/Tải lại Bypass")
            return

        self.ghi_log(f"🚀 Thực thi khởi động: {update_exe}", "green")
        ok, msg = mo_discord(update_exe)
        if not ok:
            self.ghi_log(f"❌ Lỗi khi mở Discord: {msg}", "red")
            messagebox.showerror("Lỗi", f"Lỗi khi mở Discord: {msg}")
            self.nut_bat.config(state="normal")
            self.nut_khoi_dong.config(state="normal", text="2. Bắt đầu/Tải lại Bypass")
            return

        self.ghi_log(f"⏳ Đang chờ tiến trình Discord xuất hiện (timeout {PROCESS_WAIT_TIMEOUT}s)...", "yellow")
        if doi_discord_khoi_dong(PROCESS_WAIT_TIMEOUT):
            self.ghi_log(f"🎉 Discord tiến trình đã xuất hiện.", "green")
            # Bắt đầu tự động hóa DevTools trên thread riêng
            threading.Thread(target=tu_dong_mo_console_va_allow_pasting, 
                             args=(self.ghi_log, AUTO_DELAY_AFTER_UI), daemon=True).start()
        else:
            self.ghi_log("⚠️ Discord chưa xuất hiện sau timeout. Vui lòng kiểm tra Task Manager.", "yellow")
            messagebox.showwarning("Lưu ý", "Discord chưa khởi động sau timeout. Vui lòng kiểm tra.")

        self.nut_bat.config(state="normal")
        self.nut_khoi_dong.config(state="normal", text="2. Bắt đầu/Tải lại Bypass")

    def on_close(self):
        if messagebox.askyesno("Thoát", "Bạn có muốn đóng Tool Bypass không?"):
            self.root.destroy()

# --- CHẠY ỨNG DỤNG ---
if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.02

    root = tk.Tk()
    app = GiaoDienDiscord(root)
    root.mainloop()