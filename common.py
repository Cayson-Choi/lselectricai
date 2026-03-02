"""
XG5000 자동화 공통 모듈
모든 실습과제에서 공유하는 함수들
"""
import pyautogui
import time
import win32gui
import win32con
import ctypes
import os
import shutil
import subprocess

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1
OUTPUT_DIR = r"D:\Antigravity\lselectricai"
XGWX_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "output")


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
    log("  Alt+N -> IL 모드")
    pyautogui.keyDown('alt')
    time.sleep(0.1)
    pyautogui.press('n')
    time.sleep(0.1)
    pyautogui.keyUp('alt')
    time.sleep(1.5)


def switch_to_ld():
    log("  Alt+L -> LD 모드")
    pyautogui.keyDown('alt')
    time.sleep(0.1)
    pyautogui.press('l')
    time.sleep(0.1)
    pyautogui.keyUp('alt')
    time.sleep(1.5)


def save_project():
    """Ctrl+S로 프로젝트 저장"""
    log("  Ctrl+S 프로젝트 저장...")
    pyautogui.hotkey('ctrl', 's')
    time.sleep(2)


def copy_xgwx_to_output(project_name):
    """xgwx 파일을 output 폴더로 복사"""
    src = rf"C:\XG5000\Projects\{project_name}\{project_name}.xgwx"
    os.makedirs(XGWX_OUTPUT_DIR, exist_ok=True)
    dst = os.path.join(XGWX_OUTPUT_DIR, f"{project_name}.xgwx")

    if os.path.exists(src):
        shutil.copy2(src, dst)
        log(f"  xgwx 복사 완료: {dst}")
        return True
    else:
        log(f"  xgwx 파일 없음: {src}")
        # 프로젝트 폴더 내 xgwx 파일 탐색
        proj_dir = rf"C:\XG5000\Projects\{project_name}"
        if os.path.isdir(proj_dir):
            for f in os.listdir(proj_dir):
                if f.endswith('.xgwx'):
                    shutil.copy2(os.path.join(proj_dir, f),
                                os.path.join(XGWX_OUTPUT_DIR, f))
                    log(f"  xgwx 복사 완료: {f}")
                    return True
        return False


def close_xg5000():
    log("  XG5000 종료...")
    os.system('taskkill /f /im XG5000.exe 2>nul')
    time.sleep(2)


def find_dialog_edits():
    """화면에 보이는 모든 Edit 컨트롤 찾기"""
    edits = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            cn = win32gui.GetClassName(hwnd)
            if 'edit' in cn.lower():
                r = win32gui.GetWindowRect(hwnd)
                text = wm_gettext(hwnd)
                edits.append((hwnd, r, text))
    win32gui.EnumWindows(
        lambda h, _: win32gui.EnumChildWindows(h, cb, None)
        if win32gui.IsWindowVisible(h) else None, None)
    return edits


def start_xg5000_with_new_project(project_name="TestProject"):
    """XG5000 실행 + 새 프로젝트 생성. 성공 시 main_hwnd 반환."""
    os.environ['__COMPAT_LAYER'] = 'RunAsInvoker'
    close_xg5000()

    subprocess.Popen([r"C:\XG5000\XG5000.exe"])
    log("  XG5000 시작 대기중...")

    main_hwnd = None
    for i in range(60):
        time.sleep(0.5)
        main_hwnd = find_xg5000_window()
        if main_hwnd:
            log(f"  XG5000 윈도우 감지! ({i*0.5}초)")
            break

    if not main_hwnd:
        log("ERROR: XG5000 시작 실패!")
        return None

    time.sleep(5)
    activate_window(main_hwnd)

    # 새 프로젝트 대화상자 열기
    pyautogui.hotkey('ctrl', 'n')
    time.sleep(2)

    # 프로젝트 이름 입력 - 대화상자의 Edit 컨트롤 찾기
    log(f"  프로젝트 이름 입력: {project_name}")
    dialog_edits = find_dialog_edits()
    log(f"  Edit 컨트롤 {len(dialog_edits)}개 발견")
    for hwnd, r, text in dialog_edits:
        log(f"    Edit x={r[0]} w={r[2]-r[0]} text='{text}'")

    # 프로젝트명 필드에 직접 타이핑 시도
    # Tab으로 필드 이동 후 타이핑
    pyautogui.typewrite(project_name, interval=0.03)
    time.sleep(0.5)

    # 그래도 안 되면 WM_SETTEXT 시도
    dialog_edits2 = find_dialog_edits()
    name_set = False
    for hwnd, r, text in dialog_edits2:
        if text == project_name:
            name_set = True
            log(f"  이름 입력 성공 (typewrite)")
            break

    if not name_set:
        # WM_SETTEXT 시도 - 각 Edit에 시도
        for hwnd, r, text in dialog_edits2:
            w = r[2] - r[0]
            if w > 100 and not text:  # 빈 Edit 중 넓은 것
                wm_settext(hwnd, project_name)
                time.sleep(0.1)
                check = wm_gettext(hwnd)
                if check == project_name:
                    log(f"  이름 입력 성공 (WM_SETTEXT)")
                    name_set = True
                    break

    if not name_set:
        # 클립보드 + Ctrl+V 시도
        log("  클립보드 Ctrl+V 시도...")
        subprocess.run(['powershell', '-command',
                       f'Set-Clipboard -Value "{project_name}"'],
                      capture_output=True)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)

    # Enter로 프로젝트 생성
    pyautogui.press('enter')
    time.sleep(2)

    # "파일이 이미 존재합니다. 덮어쓸까요?" → 예(Y)
    pyautogui.press('y')
    time.sleep(2)

    # "프로젝트 파일 이름을 입력하여야 합니다" 에러 처리
    main_hwnd = find_xg5000_window()
    if main_hwnd:
        activate_window(main_hwnd)

    # 에디터 뷰 확인 (프로젝트 생성 성공 여부)
    views = find_view(main_hwnd) if main_hwnd else []
    if not views:
        log("  프로젝트 생성 재시도...")
        # 에러 다이얼로그가 있으면 확인
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.typewrite(project_name, interval=0.03)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)
        pyautogui.press('y')  # 덮어쓰기 확인
        time.sleep(2)

    main_hwnd = find_xg5000_window()
    if main_hwnd:
        activate_window(main_hwnd)
    time.sleep(2)

    # 에디터 뷰 확인
    views = find_view(main_hwnd) if main_hwnd else []
    if not views:
        log("  에디터 뷰 없음 - 프로그램 더블클릭 시도...")
        pyautogui.doubleClick(100, 275)
        time.sleep(2)

    return main_hwnd


def enter_il_commands(main_hwnd, il_commands, prefix):
    """IL 명령어 입력. 성공 개수 반환."""
    pyautogui.press('escape')
    time.sleep(0.3)
    pyautogui.press('escape')
    time.sleep(0.3)

    switch_to_il()

    views = find_view(main_hwnd)
    if not views:
        log("ERROR: 에디터 뷰 없음!")
        save_screenshot(f"{prefix}_error_no_view")
        return 0
    view_rect = views[0][1]
    log(f"  에디터 뷰: {view_rect}")

    total = len(il_commands)
    cx = (view_rect[0] + view_rect[2]) // 2
    cy = view_rect[1] + 45

    pyautogui.doubleClick(cx, cy)
    time.sleep(1.0)

    edits = find_il_edit(main_hwnd)
    if not edits:
        log("  IL 전환 재시도...")
        switch_to_il()
        pyautogui.doubleClick(cx, cy)
        time.sleep(1.0)
        edits = find_il_edit(main_hwnd)
        if not edits:
            log("FATAL: Cannot open IL input!")
            save_screenshot(f"{prefix}_error")
            return 0

    edit_hwnd = edits[0][0]
    prev_edit_hwnd = None

    success = 0
    for i, cmd in enumerate(il_commands):
        if i > 0:
            # Enter 후 새 Edit 컨트롤이 나타날 때까지 대기
            new_edit_found = False
            for retry in range(10):
                edits = find_il_edit(main_hwnd)
                if edits:
                    new_hwnd = edits[0][0]
                    new_rect = edits[0][1]
                    # 새 Edit이 열렸는지 확인 (위치 또는 hwnd 변경)
                    if new_hwnd != prev_edit_hwnd or retry >= 3:
                        edit_hwnd = new_hwnd
                        new_edit_found = True
                        break
                time.sleep(0.2)

            if not new_edit_found:
                # 더블클릭으로 강제로 열기
                row_y = view_rect[1] + 45 + (i * 18)
                if row_y > view_rect[3] - 20:
                    row_y = view_rect[3] - 30
                pyautogui.doubleClick(cx, row_y)
                time.sleep(1.0)
                edits = find_il_edit(main_hwnd)
                if not edits:
                    log(f"  [{i+1}] FAILED (no edit): {cmd}")
                    continue
                edit_hwnd = edits[0][0]

        # 텍스트 설정 전 기존 내용 클리어
        wm_settext(edit_hwnd, "")
        time.sleep(0.1)
        wm_settext(edit_hwnd, cmd)
        time.sleep(0.2)

        actual = wm_gettext(edit_hwnd)
        if actual != cmd:
            # 재시도
            wm_settext(edit_hwnd, "")
            time.sleep(0.1)
            wm_settext(edit_hwnd, cmd)
            time.sleep(0.2)
            actual = wm_gettext(edit_hwnd)

        ok = actual == cmd
        log(f"  [{i+1}/{total}] {cmd} -> {'OK' if ok else 'FAIL:'+actual}")
        if ok:
            success += 1

        prev_edit_hwnd = edit_hwnd
        pyautogui.press('enter')
        time.sleep(1.0)  # Enter 후 충분히 대기

    pyautogui.press('escape')
    time.sleep(0.5)
    return success


def verify_and_screenshot(main_hwnd, prefix):
    """IL/LD 스크린샷 촬영"""
    pyautogui.hotkey('ctrl', 'Home')
    time.sleep(0.3)
    save_screenshot(f"{prefix}_il_result")

    views = find_view(main_hwnd)
    if views:
        vr = views[0][1]
        save_screenshot(f"{prefix}_il_editor", region=(
            int(vr[0])-10, int(vr[1])-40,
            int(vr[2]-vr[0])+20, int(vr[3]-vr[1])+40))

    log("  LD 모드로 전환...")
    switch_to_ld()
    pyautogui.hotkey('ctrl', 'Home')
    time.sleep(0.3)

    save_screenshot(f"{prefix}_ld_full")

    views2 = find_view(main_hwnd)
    if views2:
        vr2 = views2[0][1]
        save_screenshot(f"{prefix}_ld_editor", region=(
            int(vr2[0])-10, int(vr2[1])-40,
            int(vr2[2]-vr2[0])+20, int(vr2[3]-vr2[1])+40))


def run_problem(problem_num, il_commands):
    """과제 전체 자동화: XG5000 시작 → IL 입력 → LD 검증 → 종료"""
    prefix = f"p{problem_num}"
    log("=" * 60)
    log(f"실습과제 {problem_num}번")
    log("=" * 60)

    # 1. XG5000 시작 + 새 프로젝트
    log("\n[Phase 1] XG5000 시작...")
    main_hwnd = start_xg5000_with_new_project(f"P{problem_num}")
    if not main_hwnd:
        return False
    save_screenshot(f"{prefix}_started")

    # 2. IL 입력
    log("\n[Phase 2] IL 입력...")
    total = len(il_commands)
    success = enter_il_commands(main_hwnd, il_commands, prefix)
    log(f"\n  IL 입력: {success}/{total}")

    # 3. 검증 스크린샷
    log("\n[Phase 3] 검증...")
    verify_and_screenshot(main_hwnd, prefix)

    # 4. 저장 + xgwx 복사
    log("\n[Phase 4] 저장 및 xgwx 복사...")
    save_project()
    project_name = f"P{problem_num}"
    copy_xgwx_to_output(project_name)

    result = success == total
    log(f"\n{'=' * 60}")
    log(f"과제 {problem_num} {'성공' if result else '확인필요'}! IL {success}/{total}")
    log(f"래더를 확인하세요. XG5000은 열려있습니다.")
    log(f"{'=' * 60}\n")
    return result
