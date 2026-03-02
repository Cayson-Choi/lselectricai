"""
실습과제 13번 - IL 코드 수정 v3
MPUSH를 AND NOT P0001 직후에 배치 → 하나의 렁으로 합치기
답안과 완전히 동일한 래더 구조
"""

import pyautogui
import time
import win32gui
import win32con
import ctypes
import os

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1
OUTPUT_DIR = r"D:\Antigravity\lselectricai"

def log(msg):
    print(msg)

def save_screenshot(name, region=None):
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    if region:
        r = tuple(int(x) for x in region)
        pyautogui.screenshot(region=r).save(path)
    else:
        pyautogui.screenshot().save(path)

def find_xg5000_window():
    result = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if "xg5000" in win32gui.GetWindowText(hwnd).lower():
                result.append(hwnd)
    win32gui.EnumWindows(cb, None)
    return result[0] if result else None

def activate_window(hwnd):
    ctypes.windll.user32.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    time.sleep(0.5)
    ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.1)
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass
    time.sleep(0.3)

def find_il_edit(main_hwnd):
    edits = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if 'edit' in win32gui.GetClassName(hwnd).lower():
                r = win32gui.GetWindowRect(hwnd)
                w = r[2] - r[0]
                if r[0] > 650 and w > 500:
                    edits.append((hwnd, r))
    win32gui.EnumChildWindows(main_hwnd, cb, None)
    return edits

def find_view(main_hwnd):
    views = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if 'AfxFrameOrView' in win32gui.GetClassName(hwnd):
                views.append((hwnd, win32gui.GetWindowRect(hwnd)))
    win32gui.EnumChildWindows(main_hwnd, cb, None)
    return views

def wm_settext(hwnd, text):
    ctypes.windll.user32.SendMessageW(hwnd, 0x000C, 0, text)

def wm_gettext(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    ctypes.windll.user32.SendMessageW(hwnd, 0x000D, 256, buf)
    return buf.value

def switch_to_il():
    log("  Alt+N → IL 모드")
    pyautogui.keyDown('alt')
    time.sleep(0.1)
    pyautogui.press('n')
    time.sleep(0.1)
    pyautogui.keyUp('alt')
    time.sleep(1.5)

def switch_to_ld():
    log("  Alt+L → LD 모드")
    pyautogui.keyDown('alt')
    time.sleep(0.1)
    pyautogui.press('l')
    time.sleep(0.1)
    pyautogui.keyUp('alt')
    time.sleep(1.5)


def main():
    log("=" * 60)
    log("실습과제 13번 v3 - 하나의 렁 구조")
    log("=" * 60)

    # 1. XG5000 활성화
    main_hwnd = find_xg5000_window()
    if not main_hwnd:
        log("ERROR: XG5000 not found!")
        return False
    activate_window(main_hwnd)

    # 2. Escape
    pyautogui.press('escape')
    time.sleep(0.3)
    pyautogui.press('escape')
    time.sleep(0.3)

    # 3. IL 모드로 전환
    switch_to_il()

    # 4. 기존 코드 전부 Undo
    log("기존 코드 Undo...")
    for _ in range(50):
        pyautogui.hotkey('ctrl', 'z')
        time.sleep(0.1)
    time.sleep(0.5)

    save_screenshot("p13_v3_after_undo")

    # 5. 에디터 뷰 확인
    views = find_view(main_hwnd)
    if not views:
        log("ERROR: 에디터 뷰 없음!")
        return False
    view_rect = views[0][1]
    log(f"에디터 뷰: {view_rect}")

    # 6. 수정된 IL - OUT M0000 직후 MPUSH (AND M0000 제거)
    il_commands = [
        "LOAD P0000",
        "OR M0000",
        "AND NOT P0001",
        "OUT M0000",          # M0000 출력 (누산기 유지)
        "MPUSH",              # 바로 스택 저장 (AND M0000 없이!)
        "TON T000 150",
        "MLOAD",
        "AND<= T000 50",
        "OUT P0040",
        "MLOAD",
        "AND<= T000 100",
        "OUT P0041",
        "MPOP",
        "AND< T000 150",
        "OUT P0042",
        "END",
    ]
    total = len(il_commands)

    # 7. 더블클릭으로 입력 시작
    cx = (view_rect[0] + view_rect[2]) // 2
    cy = view_rect[1] + 45
    log(f"더블클릭: ({cx}, {cy})")
    pyautogui.doubleClick(cx, cy)
    time.sleep(0.8)

    edits = find_il_edit(main_hwnd)
    if not edits:
        log("IL 전환 재시도...")
        switch_to_il()
        pyautogui.doubleClick(cx, cy)
        time.sleep(0.8)
        edits = find_il_edit(main_hwnd)
        if not edits:
            log("FATAL: Cannot open IL input!")
            save_screenshot("p13_v3_error")
            return False

    edit_hwnd = edits[0][0]
    log(f"Edit hwnd={edit_hwnd}")

    # 8. 명령어 입력
    success = 0
    for i, cmd in enumerate(il_commands):
        if i > 0:
            edits = find_il_edit(main_hwnd)
            if not edits:
                log(f"  [{i+1}] Edit 없음 - 재시도...")
                row_y = view_rect[1] + 45 + (i * 18)
                if row_y > view_rect[3] - 20:
                    row_y = view_rect[3] - 30
                pyautogui.doubleClick(cx, row_y)
                time.sleep(0.8)
                edits = find_il_edit(main_hwnd)
                if not edits:
                    log(f"  [{i+1}] FAILED: {cmd}")
                    continue
            edit_hwnd = edits[0][0]

        wm_settext(edit_hwnd, "")
        time.sleep(0.05)
        wm_settext(edit_hwnd, cmd)
        time.sleep(0.15)

        actual = wm_gettext(edit_hwnd)
        if actual != cmd:
            wm_settext(edit_hwnd, cmd)
            time.sleep(0.15)
            actual = wm_gettext(edit_hwnd)

        ok = actual == cmd
        log(f"  [{i+1}/{total}] {cmd} -> {'OK' if ok else 'FAIL:'+actual}")
        if ok:
            success += 1

        pyautogui.press('enter')
        time.sleep(0.7)

    pyautogui.press('escape')
    time.sleep(0.5)

    log(f"\nIL 입력: {success}/{total}")

    # 9. IL 결과 스크린샷
    pyautogui.hotkey('ctrl', 'Home')
    time.sleep(0.3)
    save_screenshot("p13_v3_il_result")

    views = find_view(main_hwnd)
    if views:
        vr = views[0][1]
        save_screenshot("p13_v3_il_editor", region=(
            int(vr[0])-10, int(vr[1])-40,
            int(vr[2]-vr[0])+20, int(vr[3]-vr[1])+40))

    # 10. LD 모드로 전환
    log("\nLD 모드로 전환...")
    switch_to_ld()

    pyautogui.hotkey('ctrl', 'Home')
    time.sleep(0.3)

    save_screenshot("p13_v3_ld_full")

    views2 = find_view(main_hwnd)
    if views2:
        vr2 = views2[0][1]
        save_screenshot("p13_v3_ld_editor", region=(
            int(vr2[0])-10, int(vr2[1])-40,
            int(vr2[2]-vr2[0])+20, int(vr2[3]-vr2[1])+40))

    log("\n" + "=" * 60)
    log(f"완료! IL {success}/{total}")
    log("=" * 60)
    return success == total


if __name__ == "__main__":
    ok = main()
    print(f"\n{'성공!' if ok else '확인 필요'}")
