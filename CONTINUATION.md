# 프로젝트 인계 문서 (다른 PC에서 이어서 작업하기)

## 프로젝트 개요
- **목표**: LS Electric XGB PLC (XBC-DR30SU) + XG5000 프로그래밍
- **용도**: 전기기능장 실기시험 PLC 래더 프로그래밍 자동화
- **디렉토리**: `D:\Antigravity\LSelectricai`

## 새 PC 설정
1. 이 레포를 clone
2. `C:\Users\<사용자>\.claude\projects\<project-hash>\memory\` 폴더에 아래 메모리 파일들을 복사
3. XG5000 설치 (C:\XG5000\XG5000.exe)

---

## 현재 작업 상태: 실습과제 11 자동 빌드

### 목표 래더 프로그램
```
Rung 0: [P00000(NO) OR M00000(NO)] + P00001(NC) → M00000(Coil)   [자기유지]
Rung 1: M00000(NO) → TON T0000 100                                [10초 타이머]
Rung 2: M00000(NO) → P00040(Coil)                                 [RL 즉시 ON]
Rung 3: >= T0000 50 → P00041(Coil)                                [GL 5초 후]
Rung 4: >= T0000 100 → P00042(Coil)                               [BZ 10초 후]
Rung 5: END
```

### IL 코드 (참조용)
```
LOAD P00000       ; PB1 (NO)
OR M00000         ; 자기유지
AND NOT P00001    ; PB2 (NC) 정지
OUT M00000        ; 내부릴레이 자기유지 코일
LOAD M00000
TON T0000 100     ; 10초 타이머 (100ms base × 100)
LOAD M00000
OUT P00040        ; RL 즉시 ON
LOAD>= T0000 50   ; 5초 이상
OUT P00041        ; GL ON
LOAD>= T0000 100  ; 10초 이상
OUT P00042        ; BZ ON
END
```

### 현재 빌드 스크립트: `learning-data/example/build.py`
- pyautogui로 XG5000 GUI 자동화
- template.xgwx 파일을 열고 LD 편집기에서 자동으로 래더를 그림

### 남은 버그 (반드시 수정 필요!)
**`place_instruction()` 함수의 `pyautogui.click(600, 200)` 문제**

F10 (Instruction 대화상자) 누르기 전에 항상 고정 좌표 `(600, 200)`을 클릭함.
Rung이 쌓이면 이 좌표가 이전 Rung 위에 떨어져서 명령어가 잘못된 위치에 배치됨.

**수정 방법**: `place_instruction()` 에서 `pyautogui.click(600, 200)` 제거.
커서가 이전 명령어/접점 배치 후 올바른 위치에 있으므로 클릭 없이 F10만 누르면 됨.

```python
def place_instruction(full_cmd):
    t_pre = fg_title()
    if 'Input' in t_pre:
        pyautogui.press('escape')
        time.sleep(0.5)
    if not ensure_main_xg():
        focus_xg()
        time.sleep(0.5)
    # pyautogui.click(600, 200)  ← 이 줄 제거!
    # time.sleep(0.3)            ← 이 줄 제거!
    pyautogui.press('f10')
    ...
```

### 빌드 순서 (확인된 동작 방식)
1. Rung 0 첫 행: F3→P00000, F4→P00001, F9→M00000(coil)
2. **바로 분기 추가**: Ctrl+Home → Right → Ctrl+Down → Left×2 → F3→M00000
3. 빈 영역으로 이동: `pyautogui.click(600, 200)` (Rung 0 아래 빈 공간)
4. Rung 1~4, END 순서대로 배치
5. **주의**: 모든 rung을 다 그린 후에 분기선을 추가하면 기존 rung이 덮어씌워짐!

---

## XG5000 GUI 자동화 핵심 정리

### UAC 바이패스
```python
os.environ['__COMPAT_LAYER'] = 'RunAsInvoker'
subprocess.Popen([r'C:\XG5000\XG5000.exe', TEMPLATE])
```

### LD 에디터 단축키
| 키 | 기능 |
|---|---|
| F3 | NO 접점 → Input 대화상자 → 디바이스명 입력 → Enter |
| F4 | NC 접점 → Input 대화상자 → 디바이스명 입력 → Enter |
| F5 | 가로선 (horizontal line) |
| F6 | 세로선 (vertical line) |
| F9 | 코일 → Input 대화상자 → 디바이스명 입력 → Enter |
| F10 | Instruction 대화상자 → 전체 명령어 한 줄로 입력 → OK |
| Ctrl+방향키 | 가로선/세로선 그리기/지우기 (토글) |
| Ctrl+Home | 첫 번째 셀로 이동 |
| Ctrl+End | 마지막 셀로 이동 |

### F10 Instruction 대화상자 입력 형식
- `TON t0 100` (타이머 10초)
- `>= t0 50` (비교 명령, LOAD>= 아님!)
- `END`
- 피연산자를 공백으로 구분하여 전부 한 줄에 입력

### 병렬 분기(OR) 생성 방법
1. Rung 첫 행 배치 완료
2. Ctrl+Home → Right (P00001 위치로)
3. Ctrl(홀드)+Down (세로선 생성)
4. Left **2번** (1번=분기선 선택, 2번=접점 셀)
5. F3 → 디바이스명 입력

**주의사항:**
- P00000 열(첫번째)에서는 세로선 생성 불가 → P00001(두번째) 이후만 가능
- Ctrl+방향키 = 토글 (선 있으면 삭제, 없으면 생성)
- Shift+F1 ≠ 세로선 (F6이 세로선!)
- 모든 rung 그린 후 위로 돌아가서 분기선 넣으면 기존 rung과 합쳐짐 → 분기는 해당 rung 직후에 바로 추가해야 함

### 접점/코일 대화상자 동작
- F3/F4/F9 후 Input 대화상자가 열린 상태로 남을 수 있음
- 다음 F3/F4/F9 누르면 자동 처리
- **F10 전에는 반드시 Escape로 Input 대화상자를 먼저 닫아야 함!**

### 에러 팝업 감지
```python
def is_error_popup():
    _, _, _, _, w, h = fg_rect()
    return 'XG5000' in fg_title() and w < 400
```

### 디바이스 명명법
- 타이머: `t0` (소문자) = `T0000`
- 입출력: `P00000`, `P00040` 등
- 보조릴레이: `M00000`
- 비교명령: `>=` (LOAD>= 아님!)

### IL 모드 (View → IL, Alt+N)
- IL 그리드는 **읽기 전용에 가까움** — typewrite, clipboard paste, F2, 더블클릭 모두 입력 안됨
- LD로 작성한 후 IL로 전환하여 확인하는 용도로만 사용 가능
- 직접 IL 편집은 현재 방법으로는 불가

### 화면 좌표 (1920×1080, DPI 100%)
- 그리드 첫 번째 셀: 약 (600, 160)
- Instruction 대화상자: 약 (769, 260) 크기 383×513
- 메뉴바: y ≈ 10 (Project | Edit | Find/Replace | View | ...)

---

## .xgwx 파일 포맷
- 138바이트 바이너리 헤더 + gzip 압축 UTF-8 XML + 트레일러
- 헤더 오프셋 134: uint32 LE = gzip 데이터 크기
- XML 추출: `zlib.decompressobj(-zlib.MAX_WBITS)` (오프셋 148부터)
- ProgramData (LD): bzip2 압축 → base64 인코딩된 바이너리

---

## 실습과제 정리
- 문제 1~10: 시퀀스 회로 (자기유지, 인터록, 우선, 전동기 제어)
- 문제 11~20: 타이밍 다이어그램 → 래더 변환
- 과제 파일: `learning-data/실습과제 20개 문제.pdf`
- 답안 이미지: `learning-data/실습과제 XX 답.png`

## 학습 데이터 파일
- `learning-data/XBC-DR30SU 매뉴얼.pdf` (17p) - 화성폴리텍 학습 매뉴얼
- `learning-data/XBC-SU_XBE-E_T24_Manual_V2.2_202406_KR.pdf` (383p) - 공식 매뉴얼
- `learning-data/XG5000Help_kor.pdf` (814p) - XG5000 소프트웨어 도움말
- `template/template.xgwx` - 빈 XG5000 프로젝트 템플릿

## 타이밍 다이어그램 → 래더 변환 패턴 (핵심!)
1. **순차 ON**: TON 하나 + >= 비교로 각 출력 시점 결정
2. **순차 OFF**: <= 비교로 각 출력 OFF 시점 결정
3. **대칭 ON-OFF**: >= AND <= 범위 조건
4. **재점등**: OR 조건으로 여러 구간 결합
5. **독립 2타이머**: 각각 다른 트리거로 시작
6. **반복 사이클**: TON 자동리셋 트릭 (타이머 완료 시 입력 릴레이 리셋)

---

## 메모리 파일 목록 (새 PC의 .claude/memory/에 복사)
이 파일들은 Claude Code가 대화 시작 시 자동으로 읽는 메모리 파일입니다.
새 PC의 `.claude/projects/<project-hash>/memory/` 폴더에 복사하세요.

1. `MEMORY.md` - 프로젝트 인덱스 (필수)
2. `xbc-plc-specs.md` - PLC 하드웨어/디바이스 참조
3. `xg5000-programming.md` - XG5000 소프트웨어 가이드
4. `timer-counter-ref.md` - 타이머/카운터 참조
5. `timing-diagram-to-ladder.md` - 타이밍 → 래더 패턴 (핵심!)
6. `xgb-instruction-set.md` - IL/래더 명령어 집합
7. `xg5000-automation.md` - GUI 자동화 가이드
