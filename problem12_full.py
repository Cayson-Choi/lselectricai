"""
실습과제 12번 - 전체 자동화 (XG5000 시작부터)
1. XG5000 실행 (UAC 우회)
2. 새 프로젝트 생성
3. IL 모드 전환 + 명령어 입력
4. LD 모드 전환 + 검증 스크린샷
"""

import pyautogui
import time
import win32gui
import win32con
import ctypes
import os
import subprocess

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

def find_dialog_edits():
    """화면에 보이는 모든 Edit 컨트롤 찾기"""
    edits = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            cn = win32gui.GetClassName(hwnd)
            if 'edit' in cn.lower():
                r = win32gui.GetWindowRect(hwnd)
                edits.append((hwnd, r, cn))
    win32gui.EnumWindows(lambda h, _: win32gui.EnumChildWindows(h, cb, None) if win32gui.IsWindowVisible(h) else None, None)
    return edits


def main():
    log("=" * 60)
    log("실습과제 12번 - 전체 자동화")
    log("=" * 60)

    # ========================================
    # Phase 1: XG5000 실행
    # ========================================
    log("\n[Phase 1] XG5000 실행...")
    os.environ['__COMPAT_LAYER'] = 'RunAsInvoker'

    # 혹시 이미 실행 중이면 종료
    os.system('taskkill /f /im XG5000.exe 2>nul')
    time.sleep(2)

    subprocess.Popen([r"C:\XG5000\XG5000.exe"])
    log("  XG5000 시작 대기중...")

    # 윈도우 나타날 때까지 대기 (최대 30초)
    main_hwnd = None
    for i in range(60):
        time.sleep(0.5)
        main_hwnd = find_xg5000_window()
        if main_hwnd:
            log(f"  XG5000 윈도우 감지! (hwnd={main_hwnd}, {i*0.5}초)")
            break

    if not main_hwnd:
        log("ERROR: XG5000 시작 실패!")
        return False

    # 충분히 로딩 대기
    time.sleep(5)
    activate_window(main_hwnd)
    save_screenshot("p12_phase1_started")

    # ========================================
    # Phase 2: 새 프로젝트 생성
    # ========================================
    log("\n[Phase 2] 새 프로젝트 생성...")

    # Ctrl+N 으로 새 프로젝트
    pyautogui.hotkey('ctrl', 'n')
    time.sleep(2)
    save_screenshot("p12_phase2_newdialog")

    # 새 프로젝트 대화상자에서:
    # - PLC 타입 선택 (기본값이 있을 수 있음)
    # - 프로젝트 이름 입력
    # - OK 클릭

    # 대화상자의 Edit 컨트롤 찾기
    # 프로젝트 이름 Edit은 보통 대화상자 안에 있음
    # Tab으로 이동하면서 프로젝트 이름 필드 찾기

    # 먼저 현재 대화상자 상태 확인
    # 기본 PLC 타입이 이미 선택되어 있을 수 있음
    # 프로젝트 이름만 입력하고 Enter

    # 프로젝트명 입력 - Tab으로 이동 후 타이핑
    # XG5000 새 프로젝트 대화상자 구조:
    # - PLC 시리즈 선택 (트리)
    # - PLC 타입 선택
    # - 프로젝트명 입력
    # - 경로 선택

    # Enter 또는 OK 클릭으로 기본값 사용 시도
    time.sleep(1)
    save_screenshot("p12_phase2_dialog_detail")

    # 대화상자에서 OK/확인 버튼 클릭 시도
    # 일단 Enter로 기본값 확인 시도
    pyautogui.press('enter')
    time.sleep(3)
    save_screenshot("p12_phase2_after_enter")

    # 혹시 추가 대화상자가 있으면 처리
    # (이전 프로젝트 저장 여부 등)
    # "저장하시겠습니까?" → 아니오(N)
    pyautogui.press('n')
    time.sleep(1)

    # 다시 확인
    main_hwnd = find_xg5000_window()
    if main_hwnd:
        activate_window(main_hwnd)

    time.sleep(2)
    save_screenshot("p12_phase2_project_ready")

    # 새 프로젝트가 안 만들어졌으면 다시 시도
    main_hwnd = find_xg5000_window()
    if not main_hwnd:
        log("ERROR: XG5000 윈도우 없음!")
        return False

    activate_window(main_hwnd)
    rect = win32gui.GetWindowRect(main_hwnd)
    log(f"  Window: {rect}")

    # ========================================
    # Phase 3: 프로그램 편집 준비
    # ========================================
    log("\n[Phase 3] 프로그램 편집 준비...")

    # 프로젝트 트리에서 프로그램 더블클릭하여 열기
    # 트리 영역에서 "프로그램" 또는 "Program" 항목 찾기
    # 일반적으로 좌측 트리에 있음

    time.sleep(1)
    save_screenshot("p12_phase3_before_program")

    # 프로젝트 트리에서 프로그램을 열어야 할 수 있음
    # 왼쪽 트리 영역 확인
    views = find_view(main_hwnd)
    if views:
        log(f"  에디터 뷰 발견: {len(views)}개")
        # 이미 에디터가 열려 있으면 바로 진행
    else:
        log("  에디터 뷰 없음 - 프로그램 열기 시도...")
        # 트리에서 프로그램 더블클릭
        # 일반적으로 (100, 150) 근처
        pyautogui.doubleClick(100, 150)
        time.sleep(2)

    save_screenshot("p12_phase3_editor_check")

    # ========================================
    # Phase 4: IL 모드 전환 + 명령어 입력
    # ========================================
    log("\n[Phase 4] IL 입력...")

    # IL 모드로 전환
    switch_to_il()
    save_screenshot("p12_phase4_il_mode")

    # 에디터 뷰 영역 확인
    views = find_view(main_hwnd)
    if not views:
        log("ERROR: 에디터 뷰 없음!")
        save_screenshot("p12_error_no_view")
        return False

    view_rect = views[0][1]
    log(f"  에디터 뷰: {view_rect}")

    # 실습과제 12번 IL 명령어
    il_commands = [
        "LOAD P0000",
        "OR M0000",
        "AND NOT P0001",
        "OUT M0000",
        "LOAD M0000",
        "TON T000 90",
        "LOAD>= T000 20",
        "OUT P0040",
        "LOAD>= T000 50",
        "OUT P0041",
        "LOAD>= T000 90",
        "OUT P0042",
        "END",
    ]
    total = len(il_commands)

    # 더블클릭으로 입력 시작
    cx = (view_rect[0] + view_rect[2]) // 2
    cy = view_rect[1] + 45
    log(f"  더블클릭: ({cx}, {cy})")
    pyautogui.doubleClick(cx, cy)
    time.sleep(0.8)

    edits = find_il_edit(main_hwnd)
    if not edits:
        log("ERROR: IL 입력 Edit 없음!")
        save_screenshot("p12_error_no_edit")
        return False

    edit_hwnd = edits[0][0]
    log(f"  Edit hwnd={edit_hwnd}")

    # 명령어 입력
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

    log(f"\n  IL 입력: {success}/{total}")

    # IL 결과 스크린샷
    pyautogui.hotkey('ctrl', 'Home')
    time.sleep(0.3)
    save_screenshot("p12_il_result")

    # ========================================
    # Phase 5: LD 모드 전환
    # ========================================
    log("\n[Phase 5] LD 전환...")
    switch_to_ld()

    pyautogui.hotkey('ctrl', 'Home')
    time.sleep(0.3)

    # LD 전체 스크린샷
    save_screenshot("p12_ld_full")

    # 에디터 영역 스크린샷
    views2 = find_view(main_hwnd)
    if views2:
        vr = views2[0][1]
        save_screenshot("p12_ld_editor", region=(
            int(vr[0])-10, int(vr[1])-40,
            int(vr[2]-vr[0])+20, int(vr[3]-vr[1])+40))

    log("\n" + "=" * 60)
    log(f"실습과제 12번 완료! IL {success}/{total}")
    log("=" * 60)
    return success == total


if __name__ == "__main__":
    ok = main()
    print(f"\n{'성공!' if ok else '확인 필요'}")
