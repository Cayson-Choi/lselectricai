# 전기기능장 PLC 79회 2과제 모의고사 IL 답안 분석 (31~34)

## IL 답안 공통 프레임워크 ★★★★★

4개 문제 모두 동일한 구조를 따름:

### 1. 시스템 시작 (렁 1)
```
LOAD NOT SSA        ; 또는 LOAD SSB
AND SSB              ; 또는 AND NOT SSA
OUT 과제2
```
- 31번만 `LOAD SSB / AND NOT SSA` 순서 (나머지 `LOAD NOT SSA / AND SSB`)

### 2. 리셋 (렁 3)
```
LOAD 과제2
ANDP SSC             ; P-edge (31,33,34) 또는 ANDN SSC (32번: N-edge!)
OR NOT 과제2         ; 시스템 OFF 시에도 리셋
FMOVP 0 D00000 10000  ; D 레지스터 전체 초기화
FMOVP 0 Z000 10       ; Z 레지스터 초기화 (31,33: 10개, 34: 100개)
BRSTP M00000 1000     ; M 릴레이 전체 리셋 (31번은 BRST 100)
```
- 32번은 FMOVP만 사용 (Z, M 초기화 없음 - 포인터 미사용)

### 3. 리셋 플래그 처리 (렁 4, 31/33/34만)
```
LOAD 리셋             ; 또는 LOADP T0010 (31번)
FMOVP 0 D00010 10000  ; (또는 D00015)
FMOVP 0 Z000 10
BRSTP M00000 1000
```

### 4. 입력부 (렁 6) - 중첩 MPUSH 패턴 ★★★
```
LOAD 과제2
MPUSH                 ; depth 1 (PBC 분기용)
AND NOT 동작중입력금지
MPUSH                 ; depth 2 (PBB 분기용)
ANDP PBA
AND NOT 입력금지N
INCP N
MPOP                  ; depth 2→1
ANDP PBB
AND NOT 입력금지M
INCP M
MPOP                  ; depth 1→0
ANDP PBC
AND 동작조건
SET 동작중입력금지     ; (32번은 SET 없음)
SET 동작
```
- 32번: 3개 입력(N,M,K) → MPUSH 3단 중첩
- 34번: M 입력금지 없음 (무제한 입력)

### 5. 조건 판정 (렁 8)
```
LOAD 과제2
MPUSH
ANDG> N 0 2           ; N>0 AND M>0 (연속 2개 그룹 비교)
OUT 동작조건
MLOAD                 ; (32번: 3분기, 33/34: 2분기)
AND= N 5              ; (또는 9)
OUT 입력금지N
MPOP
AND= M 5              ; (또는 9)
OUT 입력금지M
```

### 6. 연산 (문제별 고유)

### 7. 동작 (1초 타이머)
```
LOAD 동작
AND NOT T0001
TON T0001 10          ; 1초 자동리셋 타이머 (공통)
```

### 8. 출력 - De Morgan OR 패턴 ★★★★★
```
; 단일 릴레이 출력 (31, 32):
LOAD NOT M00001
NOT                   ; = LOAD M00001 (이중 부정)
OUT P00040

; 2레이어 OR 출력 (33, 34):
LOAD NOT M00001       ; ¬A
AND NOT M00011        ; ¬A ∧ ¬B
NOT                   ; ¬(¬A ∧ ¬B) = A ∨ B (De Morgan!)
OUT P00040
```
**핵심**: `LOAD NOT A / AND NOT B / NOT` = `A OR B`

### 9. END

---

## 한글 변수명 사용 ★★★

IL 답안은 **XG5000 변수 테이블**에 정의된 한글 변수명을 사용:
- 과제2, 동작, 동작중입력금지, 동작조건, 모드A, 모드B
- 입력금지N, 입력금지M, 입력금지K
- N, M, K, 큰수, 작은수
- 정지증가, 정지감소, 온정지 (31번)
- 턴1, 턴2, 리셋 (34번)
- 먼위치의시간, 짧은거리의초, 짧은거리시작시간, 짧은거리시작 (31번)
- 이하31, 초과31 (32번)

실제 디바이스 주소는 변수 테이블에서 매핑 (예: 과제2 = D06241.0)

---

## 문제 31 IL 분석 (8페이지, 28렁, 219스텝)

### 문제 설명
- N(시작위치 1~5), M(종료위치 1~5) 입력
- N에서 시작, 상하 1초 지연 점등 → 마지막 램프 1초 점등
- 소등: M에서 먼쪽부터 1초 지연 소등 → M에서 최종 소등
- 1칸 = 0.5초, 재동작 가능

### 핵심 연산 (렁 10) - MUL/SUB 기반 시간 계산
```
MUL M 10 D00003                    ; D00003 = M × 10
SUB 50 D00003 D00005               ; D00005 = 50 - M×10
SUB D00003 10 D00006               ; D00006 = M×10 - 10
MAX D00005 먼위치의시간 2           ; MAX → 먼 위치까지의 시간
MIN D00005 짧은거리의초 2           ; MIN → 짧은 거리의 시간
SUB 먼위치의시간 짧은거리의초 짧은거리시작시간  ; 차이 = 짧은거리 시작 시점
MPUSH
AND>= M 3
OUT 모드A                           ; M≥3: 모드A
MPOP
AND< M 3
OUT 모드B                           ; M<3: 모드B
```

예시 (M=2):
- D00003 = 20, D00005 = 30, D00006 = 10
- 먼위치의시간 = 30, 짧은거리의초 = 10, 짧은거리시작시간 = 20

### ON 구간 (렁 14) - 이중 포인터 확장
```
LOAD 동작
FMOVP N Z001 2          ; Z001=N, Z002=N (초기값)
AND T0001                ; 매 1초
MPUSH
AND NOT 정지증가
INCP Z001                ; Z001 증가 (위로)
MPOP
AND NOT 정지감소
DECP Z002                ; Z002 감소 (아래로)
```

### OFF 구간 (렁 18) - 3타이머 + 모드별 소등
```
LOAD T0002               ; ON 구간 완료 후
TON T0010 먼위치의시간    ; 전체 OFF 타이머
MOVP 6 Z001              ; 포인터 초기화
MOVP 0 Z002
AND NOT T0001
MPUSH
AND 모드A
INCP Z002
AND 짧은거리시작
DECP Z001
MPOP
AND 모드B
DECP Z001
AND 짧은거리시작
INCP Z002
```

### 새 명령어
- **MUL S1 S2 D**: S1 × S2 → D (곱셈)
- **SUB S1 S2 D**: S1 - S2 → D (뺄셈)
- **BRST S N**: S부터 N개 릴레이 일괄 리셋 (연속 실행, vs BRSTP = P-edge)

---

## 문제 32 IL 분석 (6페이지, 17렁, 129스텝)

### 핵심 연산 (렁 8) - BCD 파이프라인
```
UNI M D00010 2           ; M(일의자리)+N(십의자리) → BCD 합성
BIN D00010 D00020        ; BCD → 이진수 변환
DIV D00020 K D00050      ; NM ÷ K → 몫(D00050)
MPUSH
AND<= D00050 31
OUT 이하31
MPOP
AND> D00050 31
OUT 초과31
```

### 동작 (렁 10) - 이하31 + 초과31 분기
```
LOAD 동작
MPUSH
AND 이하31
MOVP D00050 D00000       ; 몫 → D 레지스터 (비트→램프 직접 매핑)
MPOP
AND 초과31
MPUSH
AND NOT T0001
TON T0001 20             ; 2초 자동리셋
MLOAD
AND= T0001 0
MOVP 10 D00000           ; 0.0s: 0b01010 → PLB,PLD ON
MLOAD
LOAD= T0001 5            ; ★ LOAD=/OR=/AND LOAD 블록 결합!
OR= T0001 15
AND LOAD
MOVP 0 D00000            ; 0.5s/1.5s: all OFF
MPOP
AND= T0001 10
MOVP 21 D00000           ; 1.0s: 0b10101 → PLA,PLC,PLE ON
```

### 출력 (렁 12~16) - D 비트→P 매핑
```
LOAD NOT D00000.4
NOT
OUT P00040               ; D00000.4 → PLA
; ... (D00000.3→PLB, .2→PLC, .1→PLD, .0→PLE)
```

### 리셋 특이사항
- **ANDN SSC**: N-edge(음변환) 사용 (다른 문제는 ANDP)

---

## 문제 33 IL 분석 (8페이지, 22렁, 228스텝)

### 핵심: 이중 포인터 스위프 + 중간 동시점등

### 타이머 + 포인터 이동 (렁 10)
```
LOAD 동작
MPUSH
AND NOT T0001
TON T0001 10
MLOAD
AND 모드A
MOVP 5 Z001              ; 역방향: Z001=5
MOVP 6 Z000              ; Z000=6
MLOAD
AND 모드B
MOVP 1 Z001              ; 정방향: Z001=1
MPOP
AND T0001
MPUSH
AND 모드B
INCP Z001
INCP Z000
MPOP
AND 모드A
DECP Z001
DECP Z000
```

### 포인터 제어 + 리셋 (렁 11) - OR LOAD/AND LOAD 복합
```
LOAD 동작
RST M00000[Z000]          ; 뒤쪽 소등
OUT M00000[Z001]          ; 앞쪽 점등
LOAD= Z001 6
AND 모드B
LOAD= Z001 0
AND 모드A
OR LOAD                   ; (Z001=6∧모드B) OR (Z001=0∧모드A)
AND LOAD                  ; 동작 AND 위 결과
OUT 리셋
```

### 중간 램프 동시점등 (렁 13) - <=3 + OR LOAD/AND LOAD 반복 ×5
```
; 위치 1에 대해:
AND<=3 작은수 1 큰수       ; 범위 내 확인
LOAD= Z001 작은수
AND 모드B
LOAD= Z001 큰수
AND 모드A
OR LOAD                    ; 모드별 트리거 조건 OR
AND LOAD                   ; 범위 확인 AND 트리거
SET M00011                 ; 중간 램프 ON
; ... 위치 2~5 반복 (MLOAD로 분기)
```

### 출력 (렁 17~21) - 2레이어 De Morgan OR
```
LOAD NOT M00001
AND NOT M00011
NOT                        ; M00001 OR M00011
OUT P00040
```

---

## 문제 34 IL 분석 (6페이지, 27렁, 175스텝)

### 문제 설명
- N: 시작 위치 (1~5)
- M: 동시 점등 횟수 (카운터)
- 양쪽에서 점등 → PLA/PLE에서 턴 → M번 만남 후 정지
- 1칸 = 1초, 재동작 가능

### 핵심: 핑퐁(왕복) 패턴 + 만남 카운터

### 포인터 이동 (렁 13) - 4분기 MPUSH
```
LOAD 동작
FMOVP N Z001 2            ; Z001=N, Z002=N
AND T0001
MPUSH
AND NOT 턴1
INCP Z001                  ; 턴1 전: Z001 증가
MLOAD
AND 턴1
DECP Z001                  ; 턴1 후: Z001 감소
MLOAD
AND NOT 턴2
DECP Z002                  ; 턴2 전: Z002 감소
MPOP
AND 턴2
INCP Z002                  ; 턴2 후: Z002 증가
```

### 턴 제어 (렁 15) - 왕복 로직
```
LOAD 동작
MPUSH
AND= Z001 5
SET 턴1                    ; Z001=5 도달 → 방향 전환
MLOAD
AND= Z001 1
AND 턴1
RST 턴1                    ; Z001=1 복귀 AND 턴1 → 턴1 해제
MLOAD
AND= Z002 1
SET 턴2                    ; Z002=1 도달 → 방향 전환
MPOP
AND= Z002 5
AND 턴2
RST 턴2                    ; Z002=5 복귀 AND 턴2 → 턴2 해제
```

경로: Z001: N→5→1→5→1... / Z002: N→1→5→1→5...

### 출력 (렁 17-18) - 3연속 인덱스 윈도우 ★★★
```
; Z001 레이어:
LOAD 동작
RST M00000[Z001]           ; 이전 위치 OFF
SET M00001[Z001]           ; 현재 위치 ON
RST M00002[Z001]           ; 다음 위치 OFF

; Z002 레이어:
LOAD 동작
RST M00010[Z002]
SET M00011[Z002]
RST M00012[Z002]
```
- M0000x[Z]: 3연속 RST/SET/RST로 정확히 1칸만 ON인 윈도우 생성

### 리셋 제어 (렁 20) - 만남 카운터
```
LOAD 동작
MOVP -1 D00100             ; 카운터 = -1 (초기값, P-edge)
MPUSH
AND= Z001 Z002             ; 두 포인터가 같은 위치
AND NOT T0001
INCP D00100                ; 만남 횟수 증가
MPOP
AND= M D00100              ; M번 만남 달성
TON T0010 10               ; 1초 대기
AND T0010
OUT 리셋                    ; 리셋 트리거
```

### 최종 출력 - 인덱스 오프셋 주의!
```
; P00040 = M00002 OR M00012 (NOT M00001!)
LOAD NOT M00002
AND NOT M00012
NOT
OUT P00040                 ; PLA = 위치 1
```
M00001이 아니라 **M00002**부터 시작 → 인덱스 오프셋 +1

---

## 새로 발견한 명령어 종합

### 산술 연산
| IL | Function |
|---|---|
| MUL S1 S2 D | S1 × S2 → D (곱셈) |
| SUB S1 S2 D | S1 - S2 → D (뺄셈) |
| DIV S1 S2 D | S1 ÷ S2 → 몫 D, 나머지 D+1 |

### BCD 변환
| IL | Function |
|---|---|
| UNI S D N | S부터 N개 BCD 합성 → D |
| BIN S D | BCD → Binary 변환 |

### 논리
| IL | Function |
|---|---|
| NOT | 누산기 반전 (중간 결과 NOT) |

### 그룹 비교 (IL 형태)
| IL | Function |
|---|---|
| ANDG> S C N | AND 그룹비교: S부터 N개 모두 > C |
| AND<=3 S1 S2 S3 | AND 범위비교: S1 ≤ S2 ≤ S3 |

### 일괄 처리
| IL | Function |
|---|---|
| BRST S N | 일괄 리셋 (연속 실행) |
| BRSTP S N | 일괄 리셋 (P-edge, 1회) |

### 블록 결합
| IL | Function |
|---|---|
| OR LOAD | 두 평가블록의 OR 결합 |
| AND LOAD | 두 평가블록의 AND 결합 |

---

## 핵심 IL 패턴 정리

### 1. 이중 부정 출력 (LOAD NOT / NOT)
```
LOAD NOT M00001    ; ¬A
NOT                ; ¬(¬A) = A
OUT P00040         ; P00040 = A
```
= `LOAD M00001 / OUT P00040`와 동일
→ XG5000 LD→IL 변환기가 생성하는 패턴

### 2. De Morgan OR 출력 (LOAD NOT / AND NOT / NOT) ★★★
```
LOAD NOT M00001    ; ¬A
AND NOT M00011     ; ¬A ∧ ¬B
NOT                ; ¬(¬A ∧ ¬B) = A ∨ B
OUT P00040         ; P00040 = A OR B
```

### 3. 조건부 OR (LOAD=/AND/OR LOAD/AND LOAD) ★★★
```
; (조건1 AND 모드B) OR (조건2 AND 모드A) → 결과
LOAD= Z001 작은수   ; 블록1 시작
AND 모드B
LOAD= Z001 큰수     ; 블록2 시작
AND 모드A
OR LOAD              ; 블록1 OR 블록2
AND LOAD             ; 상위 조건 AND (블록 결과)
SET M00011
```

### 4. 중첩 MPUSH (2단 이상)
```
LOAD 과제2
MPUSH               ; depth 1
AND NOT 입력금지
MPUSH               ; depth 2
ANDP PBA → INCP N
MPOP                ; depth 2 해제
ANDP PBB → INCP M
MPOP                ; depth 1 해제
ANDP PBC → SET 동작
```

### 5. 4분기 MPUSH (MPUSH + 2×MLOAD + MPOP)
```
MPUSH     ; 분기 1
...
MLOAD     ; 분기 2
...
MLOAD     ; 분기 3
...
MPOP      ; 분기 4 (마지막)
```

### 6. FMOVP로 Z 레지스터 동시 초기화
```
FMOVP N Z001 2      ; Z001=N, Z002=N (연속 2개에 같은 값)
```

### 7. 3연속 인덱스 윈도우 (34번)
```
RST M00000[Z]        ; Z 위치 OFF
SET M00001[Z]        ; Z+1 위치 ON
RST M00002[Z]        ; Z+2 위치 OFF
```
→ 정확히 1칸만 ON인 이동 윈도우

---

## 4개 문제 비교

| 항목 | 31번 | 32번 | 33번 | 34번 |
|------|------|------|------|------|
| 난이도 | ★★★★★ | ★★★★ | ★★★★★ | ★★★★ |
| 렁/스텝 | 28/219 | 17/129 | 22/228 | 27/175 |
| 입력 | N,M (1~5) | N,M,K (0~9) | N,M (1~5) | N(1~5),M(무제한) |
| 핵심연산 | MUL+SUB (시간계산) | UNI+BIN+DIV (BCD) | MAX+MIN | FMOVP N Z001 2 |
| 포인터 | Z001↑,Z002↓ (ON/OFF 분리) | 없음 | Z001(앞),Z000(뒤) | Z001↕,Z002↕ (왕복) |
| 출력방식 | NOT 이중부정 | D비트→P 매핑 | 2레이어 De Morgan OR | 3연속인덱스+De Morgan |
| 특수패턴 | ON구간+OFF구간 분리 | LOAD=/OR=/AND LOAD | <=3+OR LOAD 반복×5 | 핑퐁+만남카운터 |
| 리셋엣지 | ANDP SSC | ANDN SSC | ANDP SSC | ANDP SSC |
| 새명령어 | MUL,SUB,BRST | UNI,BIN,DIV,ANDN | AND<=3,OR LOAD | MOVP -1 (음수) |
