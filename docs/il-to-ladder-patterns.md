# IL → 래더 변환 패턴 (과제 13~20 실전 검증 완료)

## 핵심 원칙: 렁(Rung) 구조 제어

### LOAD = 새 렁 시작
- `LOAD`는 **항상 새로운 렁**을 시작함
- 같은 렁 안에서 분기하려면 LOAD 대신 **MPUSH/MLOAD/MPOP** 사용

### OUT 후 누산기 상태
- `OUT M0000` 실행 후 누산기에는 **M0000의 결과값이 유지**됨
- 따라서 `OUT M0000` 직후 `MPUSH`하면 별도의 `LOAD M0000` 없이 M0000 값으로 분기 가능

### MPUSH/MLOAD/MPOP 스택 분기
```
MPUSH    → 현재 누산기를 스택에 저장 (분기 시작)
MLOAD    → 스택에서 누산기 복원 (스택 유지, 중간 분기)
MPOP     → 스택에서 누산기 복원 (스택 해제, 마지막 분기)
```
- XGB: 최대 8단계 중첩 가능
- 분기가 N개면: 1개 MPUSH + (N-2)개 MLOAD + 1개 MPOP

---

## 실패 패턴 vs 성공 패턴 (과제 13에서 검증)

### 실패 1: 별도 LOAD로 분기 → 렁이 분리됨
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
LOAD M0000          ← 새 렁 시작!
TON T000 150
LOAD M0000          ← 또 새 렁!
AND<= T000 50
OUT P0040
...
```
결과: 각 출력이 **별도 렁**으로 분리됨 (답안과 다름)

### 실패 2: LOAD M0000 + MPUSH → 불필요한 LOAD
```
...
OUT M0000
LOAD M0000          ← 새 렁! (불필요)
MPUSH
TON T000 150
...
```
결과: M0000에서 새 렁이 시작되어 **2개 렁**으로 분리됨

### 성공: OUT 직후 MPUSH (LOAD 없이!)
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000            ← 출력 후 누산기에 M0000 값 유지
MPUSH                ← 바로 스택 저장! (같은 렁 유지)
TON T000 150         ← 분기1: 타이머
MLOAD                ← 누산기 복원
AND<= T000 50        ← 분기2: AND로 조건 결합
OUT P0040
MLOAD                ← 누산기 복원
AND<= T000 100       ← 분기3
OUT P0041
MPOP                 ← 마지막 분기 (스택 해제)
AND< T000 150        ← 분기4
OUT P0042
END
```
결과: **하나의 렁**에서 M0000 → TON, 비교1, 비교2, 비교3 모두 분기 (답안과 동일!)

---

## AND 비교 vs LOAD 비교

| 명령 | 동작 | 래더 결과 |
|------|------|-----------|
| `LOAD>= T000 50` | 새 렁 시작 + 비교 | 별도 렁의 비교 접점 |
| `AND>= T000 50` | 현재 렁에서 직렬 비교 | 같은 렁 내 직렬 조건 |
| `OR>= T000 50` | 현재 렁에서 병렬 비교 | 같은 렁 내 병렬 조건 |

**MPUSH 분기 내에서는 반드시 AND 비교 사용** → LOAD 비교를 쓰면 새 렁으로 분리됨

---

## 실습과제별 IL 코드 (검증 완료)

### 패턴 1: 순차 점등 (과제 11, 12) - 별도 렁 구조

과제 11, 12는 답안 이미지에서 각 비교가 **별도 렁**이므로 LOAD 비교 사용:

#### 과제 11
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
LOAD M0000
TON T000 100
LOAD M0000
OUT P0040
LOAD>= T000 50
OUT P0041
LOAD>= T000 100
OUT P0042
END
```

#### 과제 12
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
LOAD M0000
TON T000 90
LOAD>= T000 20
OUT P0040
LOAD>= T000 50
OUT P0041
LOAD>= T000 90
OUT P0042
END
```

### 패턴 2: 순차 소등 (과제 13) - 하나의 렁 + MPUSH 분기 ★★★

```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
MPUSH
TON T000 150
MLOAD
AND<= T000 50
OUT P0040
MLOAD
AND<= T000 100
OUT P0041
MPOP
AND< T000 150
OUT P0042
END
```

### 패턴 3: 구간 ON/OFF (과제 14, 15) - 하나의 렁 + MPUSH 분기

#### 과제 14
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
MPUSH
TON T000 150
MLOAD
AND NOT T000
OUT P0040
MLOAD
AND>= T000 30
AND<= T000 120
OUT P0041
MPOP
AND>= T000 50
AND<= T000 100
OUT P0042
END
```
- P0040(RL): T000 b접점 = 타이머 미완료 동안 ON
- P0041(GL): 3초~12초 구간
- P0042(BZ): 5초~10초 구간

#### 과제 15
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
MPUSH
TON T000 100
MLOAD
AND<= T000 50
OUT P0040
MLOAD
AND>= T000 50
AND<= T000 100
OUT P0041
MPOP
AND>= T000 100
OUT P0042
END
```

### 패턴 4: 재점등 (과제 16) - OR 병렬 비교 ★★★ (검증완료)

```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
MPUSH
TON T000 90
MLOAD
LOAD<= T000 50       ; 새 평가블록: T000<=50
OR>= T000 90         ; OR: T000>=90
AND LOAD              ; M0000 AND (블록)
OUT P0040             ; 0~5초 OR 9초~ ON
MPOP
AND>= T000 50
AND<= T000 90
OUT P0041             ; 5~9초 ON
END
```
- P0040: `LOAD<=/OR>=/AND LOAD` 블록결합으로 OR 병렬 비교 구현
- P0041은 P0042 없이 2출력만 (MPOP 사용)

### 패턴 5: 2타이머 (과제 17) - 다중 렁 + OUT→TON ★★★ (검증완료)

```
LOAD P0000
OR M0000
AND NOT T001
OUT M0000
TON T000 50           ; OUT 직후 TON → 같은 렁 유지 (MPUSH 불필요)
LOAD P0001
OR M0001
AND NOT T001
OUT M0001
TON T001 50           ; 마찬가지로 OUT 직후 TON
LOAD M0000
MPUSH
AND NOT T001
OUT P0040
MLOAD
AND>= T000 30
AND<= T001 20
OUT P0041
MPOP
AND>= T000 50
OUT P0042
END
```
- 렁0: M0000 자기유지 + TON T000 (OUT→TON 패턴)
- 렁6: M0001 자기유지 + TON T001 (OUT→TON 패턴)
- 렁12: M0000 MPUSH 분기 → P0040/P0041/P0042

### 패턴 6: 반복 (과제 18, 19, 20) - TON+b접점 자동리셋 (검증완료)

#### 과제 20 (가장 단순한 반복)
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
MPUSH
AND NOT T000
TON T000 50           ; T000 b접점으로 자동리셋 사이클
MLOAD
OUT P0040             ; M0000 ON 동안 항상 ON
MLOAD
AND>= T000 20
OUT P0041
MPOP
AND<= T000 30
OUT P0042
END
```

#### 과제 18 (음변환검출 LOADN 포함) ★★★
```
LOADN P0001           ; P0001 음변환(falling edge) 검출 → 1스캔 펄스
OUT M0001
LOAD P0000
OR M0000
AND NOT M0001         ; M0001 b접점으로 정지
OUT M0000
MPUSH
AND NOT T000
TON T000 90
MLOAD
AND<= T000 20
OUT P0040
MLOAD
AND>= T000 20
AND<= T000 50
OUT P0041
MPOP
AND>= T000 50
OUT P0042
END
```

#### 과제 19 (딜레이 + 복수 사이클, 2렁 구조)
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
MPUSH
TON T000 10           ; 1초 딜레이 타이머
MLOAD
AND NOT T001
TON T001 60           ; 6초 사이클1 (즉시 시작)
MPOP
AND>= T001 40
OUT P0040
LOAD T000             ; 새 렁: T000 딜레이 후 시작
MPUSH
AND NOT T002
TON T002 60           ; 6초 사이클2 (1초 딜레이 후)
MLOAD
AND<= T002 30
OUT P0041
MPOP
AND>= T002 30
OUT P0042
END
```

---

## 렁 구조 판단 기준 ★★★

답안 이미지를 보고 IL을 작성할 때:

### 하나의 렁 (MPUSH 사용)
- 자기유지 출력(M0000) 아래에 TON과 비교가 **세로선으로 연결**되어 있으면
- 모든 분기가 **같은 렁 번호** 안에 있으면
- → `OUT M0000` 직후 `MPUSH` 사용, AND 비교

### 별도 렁 (LOAD 사용)
- 각 비교 접점이 **좌측 전원선에서 독립적으로 시작**하면
- 각 출력이 **다른 렁 번호**를 가지면
- → 각각 `LOAD` 또는 `LOAD>=` 등으로 새 렁 시작

### 판단 포인트
답안 이미지에서 **렁 번호**를 확인:
- 렁0에서 END까지 하나의 렁 번호만 있으면 → MPUSH 구조
- 여러 렁 번호가 있으면 → LOAD 구조

---

## 검증된 추가 패턴 ★★★

### 1. OR 병렬 비교: LOAD/OR/AND LOAD 블록결합 (과제 16 검증)

```
MLOAD                ; M0000 복원 (스택에서)
LOAD<= T000 50       ; 새 평가블록 시작: T000 <= 50
OR>= T000 90         ; 블록에 OR 추가: T000 >= 90
AND LOAD              ; 이전 누산기(M0000) AND (블록 결과)
OUT P0040
```
- `LOAD<=`는 새 평가블록 (MPUSH 스택과 별개)
- `OR>=`로 병렬 조건 추가
- `AND LOAD`로 스택의 누산기와 결합

### 2. OUT 직후 TON (과제 17 검증)

```
OUT M0000
TON T000 50          ; LOAD 없이 → 같은 렁 유지
```
- MPUSH 불필요 (분기가 하나뿐일 때)
- 누산기가 그대로 TON의 enable로 사용됨

### 3. LOADN/LOADP 에지검출 (과제 18 검증)

```
LOADN P0001          ; P0001의 음변환(falling edge) 검출
OUT M0001            ; 1스캔 펄스 출력
```
- `LOADP` = Positive transition (양변환/상승에지) ✅ XG5000 지원 확인
- `LOADN` = Negative transition (음변환/하강에지) ✅ XG5000 지원 확인
- 과제 18 답안은 **LOADN** (음변환) 사용
- **실수 경험**: 처음에 LOADP로 작성 → 답안은 |N| → LOADN으로 수정하여 일치 확인

### 4. 비교명령 없이 a접점/b접점만으로 풀기 (과제 17 응용, XG5000 검증완료) ★★★

비교명령(>=, <=) 대신 **타이머를 시점마다 각각 배치**하고 타이머 a접점/b접점으로 직접 제어.

**원리**: 비교명령 1개 = 타이머 1개로 대체
- `>= T000 30` (3초 이상) → 별도 `TON T_x 30` + T_x(a접점) 으로 동일 효과
- `<= T000 50` (5초 이하) → 별도 `TON T_x 50` + T_x(b접점) 으로 동일 효과

**과제 17 응용 풀이 (타이머 4개, 비교명령 0개)**:
```
; 자기유지
LOAD P0000
OR M0000
AND NOT T003          ; T003 완료 시 전체 리셋
OUT M0000
LOAD P0001
OR M0001
AND NOT T003
OUT M0001
; ON 시퀀스 타이머
LOAD M0000
TON T000 30           ; 3초: GL ON 시점
LOAD M0000
TON T001 50           ; 5초: YL ON 시점
; OFF 시퀀스 타이머
LOAD M0001
TON T002 20           ; PB2+2초: GL OFF 시점
LOAD M0001
TON T003 50           ; PB2+5초: RL OFF + 리셋
; 출력 (a접점/b접점만!)
LOAD M0000
AND NOT T003
OUT P0040             ; RL: M0000 ON이고 T003 미완료
LOAD T000
AND NOT T002
OUT P0041             ; GL: 3초후 ON, PB2+2초후 OFF
LOAD T001
AND NOT M0001
OUT P0042             ; YL: 5초후 ON, PB2 즉시 OFF
END
```

**비교표:**
| 항목 | 기존(비교명령 사용) | 응용(a접점/b접점만) |
|------|---------------------|---------------------|
| 타이머 | 2개 (T000,T001) | 4개 (T000~T003) |
| 비교명령 | 3개 (>=,<=) | 0개 |
| 출력로직 | 비교접점 조합 | a접점/b접점만 |
| 렁 수 | 12+α | 10개 |

**설계 방법:**
1. 타이밍 다이어그램에서 각 출력의 ON/OFF 시점을 추출
2. 각 시점마다 별도 TON 타이머 배치
3. 출력 = (ON 시점 타이머 a접점) AND (OFF 시점 타이머 b접점)
4. 마지막 타이머(가장 늦은 시점)의 a접점으로 자기유지 해제 (전체 리셋)

**과제 18 응용 풀이 (반복 사이클, 타이머 3개, 비교명령 0개)**:
반복 패턴 = T002 b접점 자동리셋 + 공통 입력 MPUSH 분기
```
; PB2 음변환검출
LOADN P0001
OUT M0001
; 자기유지
LOAD P0000
OR M0000
AND NOT M0001
OUT M0000
; 타이머 (공통 입력: M0000 AND NOT T002)
LOAD M0000
AND NOT T002
MPUSH
TON T000 20           ; 2초: RL OFF / GL ON
MLOAD
TON T001 50           ; 5초: GL OFF / BZ ON
MPOP
TON T002 90           ; 9초: BZ OFF + 사이클 리셋
; 출력 (a접점/b접점만!)
LOAD M0000
AND NOT T000
OUT P0040             ; RL: 0~2초
LOAD T000
AND NOT T001
OUT P0041             ; GL: 2~5초
LOAD T001
AND NOT T002
OUT P0042             ; BZ: 5~9초
END
```

**과제 17 vs 18 응용 비교:**
| 항목 | 과제17 (시작/정지) | 과제18 (반복 사이클) |
|------|-------------------|---------------------|
| 사이클 | 1회 (시작→정지→종료) | 반복 (T002 b접점 자동리셋) |
| 타이머 | 4개 (별도 LOAD) | 3개 (MPUSH 공통입력) |
| 리셋 | T003 완료→자기유지 해제 | T002 b접점→타이머 전체 리셋 |
| PB2 | 정지 시퀀스 (M0001+T002,T003) | 즉시 정지 (LOADN+M0001) |

---

## 실전 에러 & 교훈 ★★★

### 교훈 1: LOAD = 새 렁 (가장 빈번한 실수)
- `OUT M0000` 후 `LOAD M0000` → 새 렁 시작! (같은 렁이 아님)
- **해결**: OUT 직후 MPUSH (LOAD 없이)

### 교훈 2: IL 입력 시 Enter 타이밍 (자동화 치명적 버그)
- WM_SETTEXT → WM_GETTEXT 성공 ≠ 명령어 확정
- Enter 후 대기 부족하면 **다음 명령어가 같은 Edit에 덮어씀**
- 겉으로는 18/18 OK인데 실제로는 14개만 입력됨
- **해결**: Enter 후 1.0초 대기 + prev_edit_hwnd로 새 Edit 출현 확인

### 교훈 3: LOADP vs LOADN (답안 이미지 확인 필수)
- 문제 텍스트의 "양변환" 표현을 신뢰하지 말 것
- **답안 이미지의 접점 기호 |P| 또는 |N|이 진실**

### 교훈 4: MPUSH 분기 내 비교는 반드시 AND
- `LOAD>= T000 50` → 새 렁! (MPUSH 분기 탈출)
- `AND>= T000 50` → 같은 렁 유지 (올바른 방법)
- 단, OR 병렬 비교가 필요하면 LOAD/OR/AND LOAD 블록결합 사용
