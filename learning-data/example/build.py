"""
Build 실습과제 11 - Phase 8: Fixed inter-rung navigation.
Key fix: After each rung, navigate to next empty row before starting next rung.
Use Ctrl+End → Down → Home to position cursor for the next rung.
"""
import pyautogui, time, ctypes, os, sys, glob, subprocess
from ctypes import wintypes
from PIL import ImageGrab

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05
BASE = r'D:\Antigravity\LSelectricai\learning-data\example'
TEMPLATE = r'D:\Antigravity\LSelectricai\template\template.xgwx'
user32 = ctypes.windll.user32

def ss(name):
    ImageGrab.grab().save(os.path.join(BASE, f'ss_{name}.png'))

def ss_crop(name, x1, y1, x2, y2):
    ImageGrab.grab().crop((x1, y1, x2, y2)).save(os.path.join(BASE, f'ss_{name}.png'))

def log(msg):
    print(msg, flush=True)

def fg_title():
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(user32.GetForegroundWindow(), buf, 256)
    return buf.value

def fg_rect():
    hwnd = user32.GetForegroundWindow()
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    return rect.left, rect.top, rect.right, rect.bottom, w, h

def find_xg():
    result = [None]
    buf = ctypes.create_unicode_buffer(256)
    buf_class = ctypes.create_unicode_buffer(256)
    def cb(hwnd, _):
        user32.GetWindowTextW(hwnd, buf, 256)
        title = buf.value
        if 'XG5000' in title and user32.IsWindowVisible(hwnd):
            user32.GetClassNameW(hwnd, buf_class, 256)
            cls = buf_class.value
            if 'Chrome' in cls or 'Edge' in cls or 'Mozilla' in cls:
                return True
            if title.endswith('XG5000') or title.endswith('XG5000 *') or '- XG5000' in title:
                result[0] = hwnd
                return False
        return True
    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(cb), 0)
    return result[0]

def focus_xg():
    h = find_xg()
    if h:
        user32.SetForegroundWindow(h)
        time.sleep(0.8)
    return h

def ensure_main_xg():
    for _ in range(10):
        t = fg_title()
        _, _, _, _, w, h = fg_rect()
        if 'XG5000' in t and w > 1000:
            return True
        if w < 600:
            pyautogui.press('enter')
            time.sleep(0.3)
            continue
        pyautogui.press('escape')
        time.sleep(0.3)
    focus_xg()
    time.sleep(0.5)
    t = fg_title()
    _, _, _, _, w, h = fg_rect()
    return 'XG5000' in t and w > 1000

def is_error_popup():
    _, _, _, _, w, h = fg_rect()
    return 'XG5000' in fg_title() and w < 400

def close_dialogs():
    """Close any open Input/Instruction dialog or error popup."""
    for _ in range(3):
        t = fg_title()
        if 'Input' in t or 'Variable' in t or 'Instruction' in t:
            pyautogui.press('escape')
            time.sleep(0.5)
        elif is_error_popup():
            pyautogui.press('enter')
            time.sleep(0.3)
        else:
            break

def goto_next_rung():
    """Navigate cursor to the start of the next empty rung row."""
    close_dialogs()
    ensure_main_xg()
    # Ctrl+End goes to the last used cell
    pyautogui.hotkey('ctrl', 'End')
    time.sleep(0.3)
    # Down moves to the row below
    pyautogui.press('down')
    time.sleep(0.2)
    # Home goes to first column (might be rung number = not editable)
    pyautogui.press('home')
    time.sleep(0.2)
    # Right moves to first editable cell (past rung number column)
    pyautogui.press('right')
    time.sleep(0.3)
    log("  → Navigated to next rung")

def place_contact_no(device, label=""):
    """Place NO contact using F3."""
    log(f"  F3 NO: {device} {label}")
    pyautogui.press('f3')
    time.sleep(1.0)
    t = fg_title()
    if 'Input' in t or 'Variable' in t:
        dx, dy, dr, db, dw, dh = fg_rect()
        pyautogui.tripleClick(dx + dw//2, dy + 40)
        time.sleep(0.1)
        pyautogui.typewrite(device, interval=0.03)
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.5)
        log(f"    OK")
        return True
    else:
        log(f"    ERROR: got '{t}'")
        if is_error_popup():
            pyautogui.press('enter')
            time.sleep(0.3)
        return False

def place_contact_nc(device, label=""):
    """Place NC contact using F4."""
    log(f"  F4 NC: {device} {label}")
    pyautogui.press('f4')
    time.sleep(1.0)
    t = fg_title()
    if 'Input' in t or 'Variable' in t:
        dx, dy, dr, db, dw, dh = fg_rect()
        pyautogui.tripleClick(dx + dw//2, dy + 40)
        time.sleep(0.1)
        pyautogui.typewrite(device, interval=0.03)
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.5)
        log(f"    OK")
        return True
    else:
        log(f"    ERROR: got '{t}'")
        if is_error_popup():
            pyautogui.press('enter')
            time.sleep(0.3)
        return False

def place_coil(device, label=""):
    """Place coil using F9."""
    log(f"  F9 COIL: {device} {label}")
    pyautogui.press('f9')
    time.sleep(1.0)
    t = fg_title()
    if 'Input' in t or 'Variable' in t:
        dx, dy, dr, db, dw, dh = fg_rect()
        pyautogui.tripleClick(dx + dw//2, dy + 40)
        time.sleep(0.1)
        pyautogui.typewrite(device, interval=0.03)
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.5)
        log(f"    OK")
        return True
    else:
        log(f"    ERROR: got '{t}'")
        if is_error_popup():
            pyautogui.press('enter')
            time.sleep(0.3)
        return False

def place_instruction(cmd, label=""):
    """Place instruction using F10. Must close Input dialog first!"""
    log(f"  F10 INST: {cmd} {label}")
    close_dialogs()
    ensure_main_xg()

    pyautogui.press('f10')
    time.sleep(1.5)
    t = fg_title()
    if 'Instruction' not in t:
        log(f"    ERROR: got '{t}'")
        if is_error_popup():
            pyautogui.press('enter')
            time.sleep(0.3)
        return False

    dx, dy, dr, db, dw, dh = fg_rect()
    pyautogui.tripleClick(dx + dw//2, dy + 40)
    time.sleep(0.1)
    pyautogui.typewrite(cmd, interval=0.03)
    time.sleep(0.3)
    pyautogui.click(dx + dw - 130, db - 20)
    time.sleep(1.5)

    t = fg_title()
    if is_error_popup():
        log(f"    ERROR POPUP")
        pyautogui.press('enter')
        time.sleep(0.3)
        return False
    log(f"    OK")
    return True

# ============================================================
# MAIN
# ============================================================
user32.LoadKeyboardLayoutW("00000409", 1)
time.sleep(0.3)

log("=== Phase 8: Fixed LD Build with Navigation ===")

for f in glob.glob(os.path.join(BASE, 'ss_*.png')):
    os.remove(f)

# Restart XG5000
log("\nRestarting XG5000...")
os.system('taskkill /f /im XG5000.exe 2>NUL')
time.sleep(3)
os.environ['__COMPAT_LAYER'] = 'RunAsInvoker'
subprocess.Popen([r'C:\XG5000\XG5000.exe', TEMPLATE])
for i in range(30):
    time.sleep(1)
    if find_xg():
        log(f"  Found after {i+1}s")
        break
time.sleep(6)

if not find_xg():
    log("XG5000 failed!"); sys.exit(1)
focus_xg()
ensure_main_xg()
time.sleep(1)
log(f"Ready: '{fg_title()}'")

# Ensure LD mode
pyautogui.hotkey('alt', 'l')
time.sleep(0.5)

# ============================================================
# Rung 0 row 1: P00000(NO) + P00001(NC) → M00000(Coil)
# ============================================================
log("\n=== Rung 0 (row 1) ===")
pyautogui.click(600, 160)
time.sleep(0.5)

place_contact_no('P00000', 'PB1')
place_contact_nc('P00001', 'PB2 stop')
place_coil('M00000', 'self-hold')

ss('r0_row1')

# ============================================================
# Rung 0 branch: OR M00000
# ============================================================
log("\n=== Rung 0 (branch) ===")
close_dialogs()
ensure_main_xg()

pyautogui.hotkey('ctrl', 'Home')
time.sleep(0.3)
pyautogui.press('right')
time.sleep(0.3)

# Ctrl+Down for vertical line
pyautogui.keyDown('ctrl')
time.sleep(0.1)
pyautogui.press('down')
time.sleep(0.1)
pyautogui.keyUp('ctrl')
time.sleep(0.5)

pyautogui.press('left')
time.sleep(0.2)
pyautogui.press('left')
time.sleep(0.3)

place_contact_no('M00000', 'self-hold branch')
ss('r0_branch')

# ============================================================
# Navigate to Rung 1 area (special: after branch, use click)
# ============================================================
log("\n=== Navigate to Rung 1 area ===")
close_dialogs()
ensure_main_xg()
# After Rung 0 with branch (2 rows), click empty area below
pyautogui.click(600, 210)
time.sleep(0.5)
log("  → Clicked empty area below Rung 0")

# ============================================================
# Rung 1: M00000(NO) → TON T0000 100
# ============================================================
log("\n=== Rung 1: M00000 → TON T0000 100 ===")
place_contact_no('M00000', 'timer input')
place_instruction('TON t0 100', '10s timer')
ss('r1_done')

# ============================================================
# Navigate to next rung
# ============================================================
goto_next_rung()

# ============================================================
# Rung 2: M00000(NO) → P00040(Coil)
# ============================================================
log("\n=== Rung 2: M00000 → P00040 ===")
place_contact_no('M00000', 'RL input')
place_coil('P00040', 'RL output')
ss('r2_done')

# ============================================================
# Navigate to next rung
# ============================================================
goto_next_rung()

# ============================================================
# Rung 3: >= T0000 50 → P00041(Coil)
# ============================================================
log("\n=== Rung 3: >= T0000 50 → P00041 ===")
place_instruction('>= t0 50', '5s compare')
place_coil('P00041', 'GL output')
ss('r3_done')

# ============================================================
# Navigate to next rung
# ============================================================
goto_next_rung()

# ============================================================
# Rung 4: >= T0000 100 → P00042(Coil)
# ============================================================
log("\n=== Rung 4: >= T0000 100 → P00042 ===")
place_instruction('>= t0 100', '10s compare')
place_coil('P00042', 'BZ output')
ss('r4_done')

# ============================================================
# Navigate to next rung
# ============================================================
goto_next_rung()

# ============================================================
# END
# ============================================================
log("\n=== END ===")
place_instruction('END', 'program end')
ss('end_done')

# ============================================================
# Verify in IL
# ============================================================
log("\n=== Verify: Switch to IL ===")
close_dialogs()
ensure_main_xg()
time.sleep(0.5)
pyautogui.hotkey('alt', 'n')
time.sleep(1.5)

# Handle potential error popup
t = fg_title()
if is_error_popup() or ('XG5000' in t and 'template' not in t.lower()):
    log(f"  Error/popup on IL switch: '{t}'")
    pyautogui.press('enter')
    time.sleep(0.5)
    pyautogui.press('escape')
    time.sleep(0.3)

ss('il_verify')

# Full LD view
pyautogui.hotkey('alt', 'l')
time.sleep(1.0)
t = fg_title()
if is_error_popup():
    pyautogui.press('enter')
    time.sleep(0.3)

# Scroll to top
pyautogui.hotkey('ctrl', 'Home')
time.sleep(0.3)
ss('ld_full')

log("\n=== DONE ===")
log(f"Title: '{fg_title()}'")
