# LS Electric PLC Project Memory

## 사용자 지침
- 새로 알게 된 내용이나 내려진 지침은 **즉시 문서에 업데이트** (사용자가 요청하지 않아도 바로)
- 문제를 풀어보라고 하면 **묻지 말고 바로 풀고 실행**까지 완료할 것

## Project Overview
- Directory: D:\Antigravity\LSelectricai
- Focus: LS Electric XGB PLC (XBC-DR20SU, XBC-DR30SU) + XG5000 programming
- Context: 전기기능장 실기시험 관련 PLC 프로그래밍 지원

## Key Learning Data Files
- `learning-data/XBC-DR30SU 매뉴얼.pdf` (17p) - 화성폴리텍 학습 매뉴얼
- `learning-data/XBC-SU_XBE-E_T24_Manual_V2.2_202406_KR.pdf` (383p) - 공식 매뉴얼
- `learning-data/XG5000Help_kor.pdf` (814p) - XG5000 도움말
- `learning-data/XG5000_XGK_XGB_사용설명서.pdf` - XG5000 사용설명서
- `learning-data/XG5000_XGK_XGB_사용설명서5장.pdf` - LD 편집 (5장)
- `learning-data/XG5000_XGK_XGB_사용설명서6장.pdf` - IL 편집 (6장)
- `learning-data/XGK_XGB명령어집 국문V2.8.pdf` - 명령어집
- `전기기능장예제/` - 모의고사 16~21, 31~34 답안 PDF (래더+IL)

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
- 과제 17 (1회 시작/정지): 타이머 4개, 별도 LOAD
- 과제 18 (반복 사이클): 타이머 3개, MPUSH 공통입력 + T002 b접점 자동리셋
- 상세: [IL→래더 변환 패턴](il-to-ladder-patterns.md)

## 전기기능장 모의고사 분석
- [IL 답안 종합 분석](exam-il-answers.md) ← ★★★★★ 4개 문제 IL 코드 + 공통 프레임워크 + 핵심 패턴
- [모의고사 16 분석](exam-problem-16.md) ← ★★★★★ 승곱계산(EXPT/SCH/SORT) + BCD 자릿수 표시
- [모의고사 17 분석](exam-problem-17.md) ← ★★★★★ FIFO큐(FIWRP/FIDEL/SCHP) + SR시프트레지스터 + 간접주소(#D)
- [모의고사 18 분석](exam-problem-18.md) ← ★★★★★ 배수계산 + BSUM + SR 순차점등
- [모의고사 19 분석](exam-problem-19.md) ← ★★★★★ BCD 덧셈/뺄셈(ADDB/SUBB) + 다단계 입력 (342스텝 최장!)
- [모의고사 20 분석](exam-problem-20.md) ← ★★★★★ 배열처리(DETECT/SCH/FIDEL/FIWR) + 타이머 미사용
- [모의고사 21 분석](exam-problem-21.md) ← ★★★★ MIN/MUL + 비트마스크 + De Morgan OR 출력
- [모의고사 26 분석](exam-problem-26.md) ← ★★★★ 구간카운터 + 자동리셋타이머(AND NOT T→TON) + 동적MOVP분기
- [모의고사 30 분석](exam-problem-30.md) ← ★★★★★ GCD/LCM(FF토글+FIWR+SORT+SCH) + 타이머 미사용
- [모의고사 31 분석](exam-problem-31.md) ← ★★★★★ MUL/SUB 시간계산 + ON/OFF 구간분리
- [모의고사 32 분석](exam-problem-32.md) ← ★★★★ BCD 연산 + 비트 매핑
- [모의고사 33 분석](exam-problem-33.md) ← ★★★★★ 이중포인터 스위프 + 인덱스 어드레싱
- [모의고사 34 분석](exam-problem-34.md) ← ★★★★ 핑퐁 왕복 + 만남 카운터

### IL 답안에서 배운 핵심 패턴
- **공통 프레임워크**: 시작→리셋→입력(중첩MPUSH)→조건(ANDG>)→연산→동작(1초타이머)→출력→END
- **De Morgan OR 출력**: `LOAD NOT A / AND NOT B / NOT / OUT Y` = `A OR B → Y`
- **이중 부정**: `LOAD NOT X / NOT` = `LOAD X` (XG5000 LD→IL 변환기 패턴)
- **OR LOAD/AND LOAD**: 복합 블록 결합 (`LOAD= / AND / LOAD= / AND / OR LOAD / AND LOAD`)
- **한글 변수명**: XG5000 변수 테이블에서 정의 후 IL에서 사용 가능
- **새 명령어 총정리**: MUL, DIV, SUB, ADD, NOT, BRST, ANDG>, AND<=3, AND<>, OR LOAD, ANDN, EXPT, SCH, SCHP, SORT, I2L, L2I, BCD, BMOV, FMRP, ADDP, SUBP, BSUM, ADDB, SUBB, DETECT, FIWRP, FIWR, FIDEL, SR, FF, #D간접주소

### "눌렀다 놓으면" 표현 주의! (실습과제 분석)
| 과제 | 문제 원문 | 답안 처리 |
|------|----------|-----------|
| 18 | PB2 눌렀다 놓으면 정지 | LOADN P0001 (음변환) |
| 19 | PB1 눌렀다 놓으면 시작 | 일반 a접점 자기유지 |
| 20 | PB2 눌렀다 놓으면 정지 | 일반 b접점 자기유지 해제 |
→ "눌렀다 놓으면" ≠ 반드시 음변환검출. **답안 이미지 접점 기호가 최종 기준!**

### 치명적 에러 경험 (반드시 기억!)
1. **프로젝트 이름 미입력** → "프로젝트 파일 이름을 입력하여야 합니다" 에러
2. **Enter 타이밍 부족** → OK 로그지만 실제 명령어 누락 (0.7s→1.0s로 해결)
3. **LOADP/LOADN 혼동** → 답안 이미지 |P|/|N| 기호 확인 필수
