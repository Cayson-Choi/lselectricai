# XG5000 GUI Automation Notes

## UAC Bypass (핵심!)
- XG5000 실행 시 UAC 팝업이 뜨면 pyautogui 등 자동화 불가
- 해결: `__COMPAT_LAYER=RunAsInvoker` 환경변수 설정 후 실행
- bash: `export __COMPAT_LAYER=RunAsInvoker && "C:/XG5000/XG5000.exe"`
- Python: `os.environ['__COMPAT_LAYER'] = 'RunAsInvoker'` 후 subprocess/ShellExecute

## XG5000 경로
- 실행파일: `C:\XG5000\XG5000.exe`
- 기본 프로젝트 저장: `C:\XG5000\Projects\`

## GUI Automation 이슈 (확인된 문제들)
- `pyautogui.typewrite()`: XG5000에서 문자 입력 안됨 (F키는 동작)
- `clip.exe + Ctrl+V`: New Project 다이얼로그에서 작동 안됨
- `ctypes clipboard + Ctrl+V`: memmove access violation 발생 가능
- `WM_SETTEXT`: New Project 다이얼로그의 Edit 컨트롤에서 작동 안됨 (verify 빈값)
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

## IL 모드 (View → IL, 단축키 Alt+N)
- IL 그리드는 직접 편집 불가 (typewrite, Ctrl+V, F2, 더블클릭 모두 안됨)
- LD로 작성 후 IL로 전환하여 확인하는 용도로만 사용
- IL 컬럼: Rung | Step | Commands | OP 1 variable | OP 2 variable | ...

## 디바이스 명명법
- 타이머: `t0` (소문자, 짧은형) = `T0000`
- 입출력: `P00000`, `P00040` 등
- 보조릴레이: `M00000`
- 비교명령: `>=` (LOAD>= 아님!)

## 화면 좌표 (1920x1080, DPI 100%)
- 프로젝트 트리 영역: x≈100, y=130~400
- NewProgram 위치: 약 (95, 275)
- MDI 에디터 영역: 중앙 (700, 400)
- **그리드 첫 번째 셀**: 약 (600, 160) — 매번 확인 필요!
- Instruction 대화상자 위치: 약 (769, 260) 크기 383x513
