# XG5000 GUI Automation Notes

## Python 환경 및 의존성
```
pip install pyautogui pywin32
```
- `pyautogui` — 키보드/마우스/스크린샷
- `pywin32` (win32gui, win32con) — Win32 API 윈도우 조작
- `ctypes` — SendMessageW, ShowWindow 등 (표준 라이브러리)
- `subprocess` — XG5000 프로세스 실행 (표준 라이브러리)

### pyautogui 필수 설정
```python
pyautogui.FAILSAFE = False   # 마우스가 화면 코너로 이동 시 FailSafe 방지 (자동화 중 필수!)
pyautogui.PAUSE = 0.1        # 각 pyautogui 호출 사이 0.1초 자동 대기
```

## UAC Bypass (핵심!)
- XG5000 실행 시 UAC 팝업이 뜨면 pyautogui 등 자동화 불가
- 해결: `__COMPAT_LAYER=RunAsInvoker` 환경변수 설정 후 실행
- bash: `export __COMPAT_LAYER=RunAsInvoker && "C:/XG5000/XG5000.exe"`
- Python: `os.environ['__COMPAT_LAYER'] = 'RunAsInvoker'` 후 subprocess.Popen

## XG5000 경로
- 실행파일: `C:\XG5000\XG5000.exe`
- 기본 프로젝트 저장: `C:\XG5000\Projects\`

## GUI Automation 이슈 (실전에서 확인된 문제들)
- `pyautogui.typewrite()`: XG5000 **메인 에디터**에서 문자 입력 안됨 (F키는 동작)
  - 단, **New Project 대화상자**에서는 typewrite 동작함! (P14~P20 전부 이 방식 성공)
- `clip.exe + Ctrl+V`: New Project 다이얼로그에서 작동 안됨
- `ctypes clipboard + Ctrl+V`: memmove access violation 발생 가능
- `WM_SETTEXT`: New Project 대화상자의 Edit 컨트롤에서 작동 안됨 (verify 빈값)
  - 단, **IL 에디터의 Edit 컨트롤**에서는 WM_SETTEXT 정상 동작!
- pyautogui.FAILSAFE: 마우스 코너 이동 시 트리거 → `FAILSAFE = False` 필요
- 트리 키보드 탐색: 포커스가 트리에 없으면 동작 안함

## .xgwx 파일 포맷
- 138바이트 바이너리 헤더 + gzip 압축 UTF-8 XML + 트레일러
- 헤더 오프셋 134: uint32 LE = gzip 데이터 크기
- XML 추출: `zlib.decompressobj(-zlib.MAX_WBITS)` (오프셋 148부터 = 138 + 10바이트 gzip헤더)
- ProgramData (LD): bzip2 압축 → base64 인코딩된 바이너리

## LD 에디터 요소 배치 (핵심!)
- **F3** = NO 접점 → "Input Variable/Device(-| |-)" 대화상자 → 디바이스명 입력 → Enter
- **F4** = NC 접점 → "Input Variable/Device(-|/|-)" 대화상자 → 디바이스명 입력 → Enter
- **F5** = 가로선 (horizontal line)
- **F6** = 세로선 (vertical line) — 병렬 분기(OR 분기) 생성에 사용!
- **F9** = 코일 → "Input Variable/Device(-( )-)" 대화상자 → 디바이스명 입력 → Enter
- **F10** = Instruction 대화상자 → **전체 명령어를 한 줄로 입력** → OK/Enter
  - 예: `TON t0 100` (타이머), `>= t0 50` (비교), `END`
  - 피연산자 별도 대화상자 아님! Instruction 필드에 공백으로 구분하여 전부 입력
- **Ctrl + 방향키** = 가로선/세로선 그리기 및 지우기
- **Shift+F1** ≠ 세로선 (주의!)

## 병렬 분기(OR) 생성 방법 (핵심!)
- **P00000 열(첫번째 접점)에서는 세로선 생성 불가** → P00001 열(두번째 이후)에서만 가능
- 왼쪽 전원 레일이 자동으로 분기 행의 좌측 연결 제공
- **순서**:
  1. Rung 0 첫 행 배치: F3→P00000, F4→P00001, F9→M00000(coil)
  2. Ctrl+Home → Right (P00001로 이동)
  3. Ctrl(누른상태)+Down (P00001 아래 세로선 생성 = 닫힘 연결)
  4. Left **2번** (1번=분기선 선택, 2번=접점 배치 셀로 이동)
  5. F3→M00000 (분기 접점 배치)
- Ctrl+Up 불필요! 전원 레일이 자동 연결
- Ctrl+방향키 = 토글 (선 있으면 삭제, 없으면 생성)

## 접점/코일 대화상자 동작
- F3/F4 접점 배치 후 Input 대화상자가 열린 상태로 남을 수 있음
- 다음 F3/F4/F9 누르면 자동으로 처리됨
- **F10 전에는 반드시 Escape로 Input 대화상자를 먼저 닫아야 함!**
- Escape 후 그리드 클릭으로 포커스 복구 필요

## 빌드 순서 주의사항 (매우 중요!)
- **분기(OR)는 해당 rung 직후에 바로 추가** → 다른 rung을 다 그린 후 돌아가면 안됨!
- 모든 rung 그린 후 위로 돌아가서 Ctrl+Down 하면 기존 rung과 합쳐짐
- **place_instruction()에서 F10 전 고정좌표 클릭 금지!** 커서가 이동되어 잘못된 위치에 배치됨
- 올바른 순서: Rung0(+분기) → 빈영역 클릭 → Rung1 → Rung2 → ... → END

## IL/LD 모드 전환 (핵심 단축키!)
- **Alt+N** = IL 편집 모드로 전환
- **Alt+L** = LD(래더) 편집 모드로 전환
- 메뉴 클릭 방식(보기→IL/LD)보다 훨씬 안정적!
- IL 컬럼: 렁 | 스텝 | 명령어 | OP 1 | OP 2 | ...

### IL 명령어 입력 방법 (핵심!)
1. **더블클릭**으로 그리드 행의 명령 입력 창 열기 (단순 클릭+Enter는 불안정)
2. 명령 입력 Edit 컨트롤 특징: **x>650, 넓이>500** (에디터 영역에 위치)
   - 주의: x≈200 위치의 Edit은 프로젝트 트리 검색창 (잘못된 대상!)
3. **WM_SETTEXT**로 텍스트 설정 → **Enter**로 확정 (다음 행 자동 열림)
4. 마지막 명령 후 **Escape**로 입력 모드 종료

### IL 명령어 구문 주의사항
- `AND NOT P0001` (스페이스 필수!) — `ANDNOT`은 XG5000에서 불인식
- `OR NOT` 도 마찬가지로 스페이스 구분
- `LOAD>= T000 50` — 비교 명령은 LOAD>=, LOAD<=, LOAD> 등 (새 렁 시작!)
- `AND<= T000 50` — 분기 내 비교 (같은 렁 유지!)
- `TON T000 100` — 타이머 명령
- `MPUSH` / `MLOAD` / `MPOP` — 스택 분기 (하나의 렁 유지)
- `END` — 프로그램 종료

### IL 래더 구조 핵심 (실전 검증!)
- **LOAD = 새 렁 시작** → 같은 렁 유지하려면 LOAD 사용 금지
- **OUT 후 MPUSH** → OUT 직후 누산기에 결과값 유지, 바로 MPUSH 가능
- **AND 비교 vs LOAD 비교** → MPUSH 분기 내에서는 AND>=, AND<= 사용
- 상세: [IL→래더 변환 패턴](il-to-ladder-patterns.md)

## 디바이스 명명법 (IL 입력 시)
- 타이머: `T000` (IL 입력) → XG5000 표시: `T0000`
- 입출력: `P0000` (IL 입력) → XG5000 표시: `P00000`
- 보조릴레이: `M0000` (IL 입력) → XG5000 표시: `M00000`
- **IL 입력 시 축약 가능**: P0000 = P00000, T000 = T0000

## 자동화 전체 흐름 34단계 (common.py 기준, 과제14~20 검증 완료)

### Phase 0: XG5000 시작 + 새 프로젝트 생성 (`start_xg5000_with_new_project`)
1. `__COMPAT_LAYER = RunAsInvoker` 환경변수 설정 → UAC 팝업 방지
2. `taskkill /f /im XG5000.exe` → 2초 대기 (기존 인스턴스 정리)
3. `subprocess.Popen("C:\XG5000\XG5000.exe")` 실행
4. 0.5초 간격 최대 60회(30초) `EnumWindows`로 "xg5000" 타이틀 검색
5. **5초 추가 대기** (XG5000 내부 초기화 완료)
6. 윈도우 활성화: `SW_MAXIMIZE` → Alt키 트릭 → `SetForegroundWindow`
7. **`Ctrl+N`** → 새 프로젝트 대화상자 → 2초 대기
8. **프로젝트 이름 입력** ★★★ 누락 시 "프로젝트 파일 이름을 입력하여야 합니다" 에러!
   - 1차: `pyautogui.typewrite(name)` → 0.5초 후 Edit에서 텍스트 확인
   - 2차(실패시): `WM_SETTEXT` → 빈 Edit 중 넓이>100인 것에 설정
   - 3차(실패시): PowerShell `Set-Clipboard` → `Ctrl+V`
9. **`Enter`** → 프로젝트 생성 확정 → 2초 대기
10. **`Y`** → "파일이 이미 존재합니다" 덮어쓰기 확인 → 2초 대기
11. `find_xg5000_window` → `activate_window` (에러 복구)
12. `AfxFrameOrView` 에디터 뷰 존재 확인
13. 뷰 없으면 재시도: `Enter` → `typewrite(name)` → `Enter` → `Y` → 2초
14. 다시 `find_xg5000_window` → `activate_window` → 2초
15. 에디터 뷰 재확인 → 여전히 없으면 `doubleClick(100, 275)` (트리에서 프로그램 열기)
16. 스크린샷: `{prefix}_started.png`

### Phase 1: IL 명령어 입력 (`enter_il_commands`)
17. `Escape` × 2 (각 0.3초 대기, 기존 모달/입력 상태 정리)
18. `Alt+N` → IL 편집 모드 전환 → 1.5초 대기
19. `AfxFrameOrView`로 `view_rect` 좌표 취득
20. 에디터 뷰 중앙X, 상단+45 위치 **더블클릭** → 1.0초 대기
21. `EnumChildWindows`로 Edit 컨트롤 찾기 (조건: `x>650, 넓이>500`)
    - 못 찾으면 → `switch_to_il()` 재시도 → 더블클릭 재시도
22. **첫 번째 명령어 입력**:
    - `WM_SETTEXT(edit, "")` 클리어 → 0.1초
    - `WM_SETTEXT(edit, cmd)` 설정 → 0.2초
    - `WM_GETTEXT` 검증 → 불일치 시 1회 재시도
23. **`Enter`** → 명령어 확정 + 다음 행 자동 열림 → **1.0초 대기**
24. **2번째~마지막 명령어 반복** (i > 0):
    - 새 Edit 대기: 0.2초 간격 최대 10회 폴링
      - `prev_edit_hwnd != new_hwnd` → 새 Edit 확인
      - retry >= 3이면 hwnd 같아도 진행 (재사용 케이스)
    - 대기 실패 시: 행 위치 계산 → 더블클릭 강제 열기
    - `WM_SETTEXT` 클리어 → 설정 → 검증 → `Enter` → 1.0초 대기
    - `prev_edit_hwnd` 업데이트
25. 마지막 명령어(`END`) 후 **`Escape`** → 0.5초 대기 (입력 모드 종료)

### Phase 2: 검증 스크린샷 (`verify_and_screenshot`)
26. `Ctrl+Home` → IL 에디터 맨 위 스크롤 → 0.3초
27. 전체 스크린샷: `{prefix}_il_result.png`
28. 에디터 영역 크롭 스크린샷: `{prefix}_il_editor.png`
29. `Alt+L` → LD(래더) 모드 전환 → 1.5초 대기
30. `Ctrl+Home` → LD 에디터 맨 위 스크롤 → 0.3초
31. 전체 스크린샷: `{prefix}_ld_full.png`
32. 에디터 영역 크롭 스크린샷: `{prefix}_ld_editor.png`

### Phase 3: 종료
33. `taskkill /f /im XG5000.exe` → 2초 대기
34. 결과 판정: `success == total` → 성공/확인필요 로그

## 윈도우 탐지 함수 상세

### find_xg5000_window()
- `win32gui.EnumWindows`로 보이는 윈도우 중 타이틀에 "xg5000" 포함하는 것 찾기
- 대소문자 무시 (`.lower()`)
- 반환: hwnd (핸들) 또는 None

### activate_window(hwnd)
1. `ShowWindow(hwnd, SW_MAXIMIZE)` → 최대화
2. **Alt키 트릭** ★★★:
   ```python
   keybd_event(0x12, 0, 0, 0)   # Alt 누르기
   keybd_event(0x12, 0, 2, 0)   # Alt 떼기
   ```
   - Windows는 다른 프로세스의 윈도우를 포그라운드로 가져오는 것을 차단함
   - Alt키를 짧게 눌렀다 떼면 이 잠금이 해제됨 → SetForegroundWindow 성공
3. `SetForegroundWindow(hwnd)` → try/except로 감싸 (간혹 실패)
4. 0.3초 대기

### find_view(main_hwnd)
- `EnumChildWindows`로 클래스명에 `AfxFrameOrView` 포함하는 자식 윈도우 찾기
- XG5000의 LD/IL 에디터 영역이 이 클래스를 사용
- 반환: [(hwnd, rect), ...] — rect는 (left, top, right, bottom)

### find_il_edit(main_hwnd)
- `EnumChildWindows`로 클래스명에 `edit` 포함하는 자식 윈도우 찾기
- **필터 조건: `x > 650` AND `넓이 > 500`** ★★★
  - x≈200 위치의 Edit은 프로젝트 트리 검색창 → 잘못된 대상!
  - IL 에디터의 명령어 입력창은 항상 x>650, 넓이>500
- 반환: [(hwnd, rect), ...]

### find_dialog_edits()
- 모든 보이는 윈도우의 자식 Edit 컨트롤을 수집
- New Project 대화상자의 Edit 필드 찾기용
- WM_GETTEXT로 현재 텍스트도 함께 반환

## 화면 좌표 (1920x1080, DPI 100%)
- 프로젝트 트리 영역: x≈100, y=130~400
- NewProgram 위치: 약 (95, 275) — 에디터 뷰 없을 때 더블클릭 대상
- MDI 에디터 영역: 중앙 (700, 400)
- **그리드 첫 번째 셀**: 약 (600, 160) — 매번 확인 필요!
- Instruction 대화상자 위치: 약 (769, 260) 크기 383x513

---

## 에러 히스토리 & 해결법 ★★★ (실전 디버깅 기록)

### 에러 1: "프로젝트 파일 이름을 입력하여야 합니다"
- **상황**: XG5000 시작 후 Ctrl+N → Enter 했지만 프로젝트 이름이 비어있음
- **원인**: 프로젝트 이름 입력 단계를 누락하거나, 입력 방법이 실패함
- **해결**: `pyautogui.typewrite(project_name)` 으로 New Project 대화상자에 직접 타이핑
  - typewrite는 New Project 대화상자에서는 동작함 (메인 에디터에서는 안됨)
  - 폴백: WM_SETTEXT → 클립보드 Ctrl+V

### 에러 2: "파일이 이미 존재합니다. 덮어쓸까요?"
- **상황**: 같은 이름의 프로젝트가 이미 C:\XG5000\Projects에 존재
- **원인**: 이전 실행에서 만든 프로젝트 파일이 남아있음
- **해결**: Enter 후 `pyautogui.press('y')` 로 덮어쓰기 확인
  - 과제별 고유 이름 사용: `P14`, `P15`, ..., `P20`

### 에러 3: IL 명령어 누락 (가장 치명적!) ★★★
- **상황**: 18개 명령어 모두 OK 로그가 나왔지만, IL 에디터에 14개만 표시됨
  - 중간의 MLOAD → AND>= T000 30 → AND<= T000 120 → OUT P0041 블록이 통째로 누락
- **원인**: Enter 키 후 대기 시간 부족 (0.7초)
  - WM_SETTEXT로 텍스트 설정 → WM_GETTEXT로 확인 → OK 로그 출력
  - 그러나 Enter로 확정하기 전에 다음 명령어의 WM_SETTEXT가 같은 Edit에 덮어씀
  - 즉, **텍스트 확인은 성공했지만 Enter 확정이 안 된 상태에서 다음 줄이 덮어쓴 것**
- **해결 (2가지)**:
  1. Enter 후 대기 시간 **0.7초 → 1.0초**로 증가
  2. **`prev_edit_hwnd` 추적**: Enter 후 새 Edit 컨트롤의 hwnd가 이전과 다른지 확인
     ```python
     prev_edit_hwnd = edit_hwnd
     pyautogui.press('enter')
     time.sleep(1.0)
     # 다음 루프에서:
     for retry in range(10):
         edits = find_il_edit(main_hwnd)
         if edits and edits[0][0] != prev_edit_hwnd:
             edit_hwnd = edits[0][0]
             break
         time.sleep(0.2)
     ```
  - **교훈: WM_SETTEXT/GETTEXT 성공 ≠ 명령어 입력 성공. Enter 확정 후 새 Edit 출현을 반드시 확인!**

### 에러 4: LOADP vs LOADN (과제 18)
- **상황**: 처음에 LOADP(양변환/상승에지)로 작성했으나 답안은 |N|(음변환/하강에지)
- **원인**: 문제 설명의 "양변환검출(N에지)" 표현이 혼동을 줌
  - "양변환" = positive transition (상승에지)
  - "N에지" = Negative edge (하강에지)
  - 답안 이미지에서 접점 기호가 `|N|`으로 명확히 표시됨
- **해결**: `LOADP P0001` → `LOADN P0001`로 변경
- **교훈: 문제 텍스트보다 답안 이미지의 접점 기호(|P| 또는 |N|)를 우선 확인!**

### 에러 5: 에디터 뷰 미출현
- **상황**: 프로젝트 생성 후 AfxFrameOrView 윈도우를 못 찾음
- **원인**: 프로젝트는 만들어졌지만 프로그램(NewProgram)이 편집기에 열리지 않은 상태
- **해결**: 프로젝트 트리에서 프로그램을 더블클릭 → `doubleClick(100, 275)`
  - 트리의 NewProgram 항목 위치가 약 (100, 275)
