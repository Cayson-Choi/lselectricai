# LS Electric PLC Project Memory

## 사용자 지침
- 새로 알게 된 내용이나 내려진 지침은 **즉시 문서에 업데이트** (사용자가 요청하지 않아도 바로)
- 문제를 풀어보라고 하면 **묻지 말고 바로 풀고 실행**까지 완료할 것

## Project Overview
- Directory: D:\Antigravity\LSelectricai
- Focus: LS Electric XGB PLC (XBC-DR20SU, XBC-DR30SU) + XG5000 programming
- Context: 전기기능장 실기시험 관련 PLC 프로그래밍 지원

## Key Learning Data Files
- `learning-data/XBC-DR30SU 매뉴얼.pdf` (17 pages) - 화성폴리텍 제작 학습 매뉴얼
- `learning-data/XBC-SU_XBE-E_T24_Manual_V2.2_202406_KR.pdf` (383 pages) - 공식 매뉴얼
- `learning-data/XG5000Help_kor.pdf` (814 pages) - XG5000 소프트웨어 도움말

## Detailed Notes
- [XBC PLC Specs & Devices](xbc-plc-specs.md)
- [XG5000 Programming Guide](xg5000-programming.md)
- [Timer & Counter Reference](timer-counter-ref.md)
- [LD 편집 가이드 (5장)](ld-editing-guide.md) ← 단축키 총정리
- [IL 편집 가이드 (6장)](il-editing-guide.md)
- [XGB 명령어 레퍼런스](xgb-instruction-set.md) ← MPUSH/MLOAD/MPOP 포함
- [Timing Diagram → Ladder Patterns](timing-diagram-to-ladder.md) ← 래더 패턴 (이미지답안 검증완료)
- [IL → Ladder 변환 패턴](il-to-ladder-patterns.md) ← ★★★ IL 코드 작성 핵심! (과제13~20 실전검증)

## XG5000 Automation Notes
- [XG5000 Automation Guide](xg5000-automation.md) ← GUI 자동화 + IL 입력 자동화 + 에러 히스토리

### 자동화 코드 파일 (D:\Antigravity\lselectricai)
- `common.py` — 핵심 자동화 모듈 (XG5000 시작, IL 입력, 검증, 저장, xgwx 복사)
- `learning-data/` — PDF 매뉴얼 7개 + 답안 이미지 10개 + 문제 PDF
- Python 의존성: `pyautogui`, `pywin32`
- 개별 과제 스크립트(problemXX.py, run_all.py)는 정리 삭제됨 → IL 명령어는 메모리 문서에 보존

### 자동화 워크플로우 지침
- run_problem() 완료 후 XG5000을 **닫지 않음** → 사용자가 래더 확인 후 수동 종료
- Ctrl+S 저장 → xgwx 파일을 output/ 폴더로 복사

## 실습과제 (20문제)
- 문제 1~10: 시퀀스 회로 (자기유지, 인터록, 우선, 전동기 제어) - 답 대기중
- 문제 11~20: 타이밍 다이어그램 → 래더 변환 ✅ 이미지 답안 검증 완료
- 과제 파일: learning-data/실습과제 11-20 문제.pdf
- 답안 이미지: learning-data/실습과제 XX 답.png (11~20 존재)

### 실습과제 11~20 패턴 분류 (✅ = XG5000 실전 검증 완료)
- 패턴1(순차점등): 11,12 → 단일TON + `>=` 비교 (별도렁, LOAD 사용)
- 패턴2(순차소등): 13 → 단일TON + `<=` 비교 (하나의렁, MPUSH 사용) ✅
- 패턴3(구간ON/OFF): 14,15 → `>=` AND `<=` 범위비교 (MPUSH 사용) ✅
- 패턴4(재점등): 16 → LOAD/OR/AND LOAD 블록결합 ✅
- 패턴5(2타이머): 17 → OUT→TON + 다중렁 + MPUSH 분기 ✅
- 패턴6(반복): 18,19,20 → TON+b접점 자동리셋 + LOADN 에지검출 ✅

### IL 코드 핵심 교훈
- **LOAD = 새 렁** → 같은 렁 유지: MPUSH/MLOAD/MPOP 사용
- **OUT 직후 MPUSH** → LOAD 없이 바로 분기 (누산기 값 유지)
- **OUT 직후 TON** → MPUSH 없이 같은 렁 유지 (분기 1개일 때)
- **AND 비교** → 분기 내에서는 AND>=, AND<= 사용 (LOAD>=는 새 렁!)
- **OR 병렬**: LOAD<=/OR>=/AND LOAD 블록결합
- **에지검출**: LOADN (음변환), LOADP (양변환) ← XG5000 모두 지원
- 상세: [IL→래더 변환 패턴](il-to-ladder-patterns.md)

### XG5000 자동화 실전 결과 (과제 14~20)
| 과제 | IL수 | 결과 | 패턴 | 비고 |
|------|------|------|------|------|
| 14 | 18/18 | ✅ | MPUSH+구간비교 | |
| 15 | 17/17 | ✅ | MPUSH+순차교체 | |
| 16 | 16/16 | ✅ | LOAD/OR/AND LOAD | 새 패턴 검증 |
| 17 | 22/22 | ✅ | OUT→TON+다중렁 | 새 패턴 검증 |
| 18 | 20/20 | ✅ | LOADN 에지검출 | LOADP→LOADN 수정 |
| 19 | 23/23 | ✅ | 딜레이+복수사이클 | |
| 20 | 16/16 | ✅ | 단순반복 | |

### 응용 풀이: 비교명령 없이 a접점/b접점만 사용
- `>= T000 30` → 별도 TON + a접점으로 대체
- `<= T000 50` → 별도 TON + b접점으로 대체
- 타이머 수 증가하지만 비교명령 0개로 동일 동작 구현 가능
- 과제 17 (1회 시작/정지): 타이머 4개, 별도 LOAD → `problem17_basic.py` ✅
- 과제 18 (반복 사이클): 타이머 3개, MPUSH 공통입력 + T002 b접점 자동리셋 → `problem18_basic.py` ✅
- 상세: [IL→래더 변환 패턴](il-to-ladder-patterns.md)

### 치명적 에러 경험 (반드시 기억!)
1. **프로젝트 이름 미입력** → "프로젝트 파일 이름을 입력하여야 합니다" 에러
2. **Enter 타이밍 부족** → OK 로그지만 실제 명령어 누락 (0.7s→1.0s로 해결)
3. **LOADP/LOADN 혼동** → 답안 이미지 |P|/|N| 기호 확인 필수
