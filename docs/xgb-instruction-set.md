# XGB Instruction Set Reference (명령어집 V2.8)

## Basic Contact Instructions
| IL Mnemonic | LD Element | Function |
|---|---|---|
| LOAD S | NO contact (새 rung 시작) | a접점 |
| LOAD NOT S | NC contact (새 rung 시작) | b접점 |
| AND S | Series NO | 직렬 a접점 |
| AND NOT S | Series NC | 직렬 b접점 |
| OR S | Parallel NO | 병렬 a접점 |
| OR NOT S | Parallel NC | 병렬 b접점 |

## Edge Detection (에지검출) ★★★ XG5000 검증완료
| IL Mnemonic | LD Symbol | Function |
|---|---|---|
| LOADP S | \|P\| | 양변환검출 (Positive/Rising edge) → 1스캔 ON |
| LOADN S | \|N\| | 음변환검출 (Negative/Falling edge) → 1스캔 ON |
| ANDP S | \|P\| (직렬) | 직렬 양변환 |
| ANDN S | \|N\| (직렬) | 직렬 음변환 |
| ORP S | \|P\| (병렬) | 병렬 양변환 |
| ORN S | \|N\| (병렬) | 병렬 음변환 |

- 과제 18 답안: `LOADN P0001` 사용 (음변환 = 버튼 놓을 때 검출)
- 주의: 문제에서 "양변환검출" 표현이 있어도 답안 이미지 접점기호(|P| or |N|) 확인 필수!

## Block Combination ★★★ (기능장 필수)
| IL | Function |
|---|---|
| AND LOAD | 블록 직렬 결합 (두 평가블록의 AND) |
| OR LOAD | 블록 병렬 결합 (두 평가블록의 OR) |
| MPUSH | 누산기를 스택에 저장 (분기 시작, 스택 유지) |
| MLOAD | 스택에서 누산기 복원 (중간 분기, 스택 유지) |
| MPOP | 스택에서 누산기 복원 (마지막 분기, 스택 해제) |

### LOAD/OR/AND LOAD 블록결합 패턴 ★★★ (과제 16 검증완료)
MPUSH 분기 내에서 OR 병렬 비교가 필요할 때:
```
MLOAD                ; 스택에서 M0000 복원
LOAD<= T000 50       ; 새 평가블록 시작 (MPUSH 스택과 별개!)
OR>= T000 90         ; 블록에 OR 추가
AND LOAD              ; 복원된 M0000 AND (블록 결과) 결합
OUT P0040
```
- `LOAD<=`는 MPUSH 스택을 건드리지 않고 별도 평가블록을 시작
- `AND LOAD`로 MLOAD된 누산기와 평가블록을 결합

### MPUSH/MLOAD/MPOP 핵심 규칙 (실전 검증!)
- XGB 최대 8단계 중첩
- **OUT 직후 MPUSH 가능**: OUT 후 누산기에 결과값이 유지됨
- **LOAD 없이 MPUSH**: 같은 렁 유지. LOAD를 쓰면 새 렁이 됨!
- 분기 N개: 1개 MPUSH + (N-2)개 MLOAD + 1개 MPOP
- 분기 내 비교는 **AND>=, AND<=** 사용 (LOAD>=는 새 렁!)

## Output Instructions
| IL | LD Element | Function |
|---|---|---|
| OUT D | Coil | 출력 코일 |
| OUT NOT D | Negate Coil | 반전 출력 |
| SET D | Set Coil | 래치 ON |
| RST D | Reset Coil | 래치 OFF, 타이머/카운터 리셋 |
| FF D | Flip-Flop | 실행할 때마다 0↔1 토글 ★ 모의30 |

## Timer Instructions (XGB: T0000~T0255)
| IL | Function | Time bases: 1ms, 10ms, 100ms |
|---|---|---|
| TON T t | ON-delay timer | 입력 ON→t 후 출력 ON |
| TOFF T t | OFF-delay timer | 입력 OFF→t 후 출력 OFF |
| TMR T t | Accumulating timer | 누적 타이머 |

## Counter Instructions (XGB: C0000~C0255)
| IL | Function |
|---|---|
| CTU C N | Up counter (현재값 ≥ N → ON) |
| CTD C N | Down counter |
| CTUD C U D N | Up-Down counter |

## Comparison (Contact-type) - 가장 중요!
| IL (LOAD form) | Function |
|---|---|
| LOAD>= S1 S2 | S1 ≥ S2 → ON |
| LOAD> S1 S2 | S1 > S2 → ON |
| LOAD= S1 S2 | S1 = S2 → ON |
| LOAD< S1 S2 | S1 < S2 → ON |
| LOAD<= S1 S2 | S1 ≤ S2 → ON |
| LOAD<> S1 S2 | S1 ≠ S2 → ON |
- AND>=, OR>= 등 동일 패턴

## Data Transfer Instructions (전기기능장 수준)
| IL | Function |
|---|---|
| MOVP S D | S→D 전송 (P-edge, 1회 실행) |
| FMOVP S D N | S값을 D부터 N개 연속 채움 (P-edge) |
| INCP D | D값 1 증가 (P-edge) |
| DECP D | D값 1 감소 (P-edge) |

## Arithmetic / Logic Instructions
| IL | Function |
|---|---|
| ADD S1 S2 D | S1 + S2 → D (덧셈) ★ 모의18 |
| ADDP S1 S2 D | S1 + S2 → D (펄스 덧셈, 1회) ★ 모의17 |
| SUB S1 S2 D | S1 - S2 → D (뺄셈) |
| SUBP S1 S2 D | S1 - S2 → D (펄스 뺄셈, 1회) ★ 모의17 |
| MUL S1 S2 D | S1 × S2 → D (곱셈) |
| DIV S1 S2 D | S1 ÷ S2 → 몫 D, 나머지 D+1 (정수 나눗셈) |
| EXPT S1 S2 D | S1^S2 → D (승곱, DWORD) ★ 모의16 |
| MAX S D N | S부터 N개 중 최대값 → D |
| MIN S D N | S부터 N개 중 최소값 → D |
| BSUM S D | 비트합: S의 2진수에서 1의 갯수 → D ★ 모의18 |
| NOT | 누산기 반전 (중간 결과 NOT) ★ De Morgan OR 출력 패턴에 필수 |

## BCD Arithmetic Instructions ★ 모의19 신규
| IL | Function |
|---|---|
| ADDB S1 S2 D | BCD 덧셈: S1+S2→D (BCD 형식) |
| SUBB S1 S2 D | BCD 뺄셈: S1-S2→D (BCD 형식) |

## Search / Sort Instructions
| IL | Function |
|---|---|
| SCH S1 S2 D N | 검색: S2부터 N개에서 S1값 찾기 → D=첫위치, D+1=일치수 ★ 모의16 |
| SCHP S1 S2 D1 D2 | Search Pulse: 활성 비트 위치 검색 ★ 모의17 |
| DETECT S1 S2 D N | 배열 검출: S1부터 N개에서 S2보다 큰 값의 갯수/위치 ★ 모의20 |
| SORT S1 S2 S3 S4 S5 | 정렬: 배열 정렬 (S1=데이터, S2~=제어파라미터) ★ 모의16 |

## Array / FIFO Operations ★ 모의17,18,20 신규
| IL | Function |
|---|---|
| FIWRP S D | FIFO Write Pulse: 큐에 데이터 기록 ★ 모의17 |
| FIDEL S1 S2 D | FIFO Delete: 큐/배열에서 요소 삭제 ★ 모의17,20 |
| FIWR S D | FIFO Write: 배열에 데이터 등록 (D=포인터+데이터) ★ 모의20 |
| FMRP S D | 필무브레지스터 펄스 (배열 데이터 설정) ★ 모의16 |
| SR S1 S2 S3 N | Shift Register: 비트 시프트 (S2=입력, S3=방향, N=비트수) ★ 모의17,18 |

## BCD / Conversion Instructions
| IL | Function |
|---|---|
| UNI S D N | S부터 N개 단위 BCD 값을 D에 합성 (예: 일의자리+십의자리 → BCD 워드) |
| BIN S D | BCD값 S를 이진수로 변환하여 D에 저장 |
| BCD S D | 이진수 S를 BCD로 변환하여 D에 저장 (BIN의 역변환) |
| I2L S D | 정수(WORD)→롱(DWORD) 변환 (D,D+1에 저장) |
| L2I S D | 롱(DWORD)→정수(WORD) 변환 |
| BMOV S D param | 비트무브 - 특정 비트필드 추출 (예: BCD 자릿수 추출) |

## Group Comparison (IL 형태)
| IL | Function |
|---|---|
| ANDG> S C N | AND 그룹비교: S부터 N개 모두 > C (예: ANDG> N 0 2 → N>0 AND M>0) |
| AND<=3 S1 S2 S3 | AND 범위비교: S1 ≤ S2 ≤ S3 |
| AND<> S1 S2 | AND 부등비교: S1 ≠ S2 → ON ★ 모의33 |
- LOAD/OR 형태도 존재 (LOADG>, LOAD<=3, LOAD<> 등)

## Batch Instructions
| IL | Function |
|---|---|
| BRST S N | S부터 N개 릴레이 일괄 리셋 (연속 실행) |
| BRSTP S N | S부터 N개 릴레이 일괄 리셋 (P-edge, 1회) |

## Range Comparison (3-operand)
| IL | Function |
|---|---|
| <=3 S1 S2 S3 | S1 ≤ S2 ≤ S3 → ON (범위 내 확인) |

## Jump / Label (래더 전용 - IL에서는 MPUSH/MLOAD/MPOP으로 대체)
| IL | Function |
|---|---|
| JMP N | 라벨 N으로 점프 (중간 렁 건너뜀) |
| LBL N | 라벨 N (점프 도착지) |

## Index Register & Indexed Addressing
- Z000~Z009: 인덱스 레지스터
- M00000[Z000] → M(00000 + Z000값) 동적 접근
- D, M, P 등 대부분 디바이스에 인덱스 사용 가능

## Indirect Addressing ★ 모의17 신규
- **#D00000**: D00000의 값을 주소로 사용 (포인터)
- 예: D00000=100이면 #D00000 → D00100 참조
- 런타임에 동적으로 참조 대상 변경 가능

## D Register Bit Addressing
- D06241.0 → D06241의 비트0 (개별 비트를 플래그로 사용)
- D06241.5 → D06241의 비트5
- M 릴레이처럼 SET/RST 가능
- **★★★ 비트 10 이상은 16진수 필수!** (XG5000 검증완료)
  - .0~.9 → 그대로 사용
  - .10 → .A, .11 → .B, .12 → .C, .13 → .D, .14 → .E, .15 → .F
  - `.10`은 XG5000 에러 발생! 반드시 `.A` 사용

## END
| IL | Function |
|---|---|
| END | 프로그램 종료 (필수) |

## Device Naming (XBC)
- P: I/O (P00000~)
- M: 보조릴레이 (M00000~)
- K: Keep릴레이 (K00000~)
- T: 타이머 (T0000~T0255)
- C: 카운터 (C0000~C0255)
- D: 데이터레지스터 (D00000~)
- Z: 인덱스레지스터 (Z000~Z009)
- F: 특수릴레이 (F00000~)

## IL 코드 실전 예제 (검증 완료)

### 과제 13 - 순차소등 (하나의 렁 + MPUSH) ★ 정답 검증 완료
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000         ; 누산기에 M0000 결과 유지
MPUSH             ; 스택 저장 (LOAD 없이 바로!)
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

### 과제 12 - 순차점등 (별도 렁 구조)
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

### 과제 16 - OR 병렬 비교 (LOAD/OR/AND LOAD 블록결합) ★ 정답 검증 완료
```
LOAD P0000
OR M0000
AND NOT P0001
OUT M0000
MPUSH
TON T000 90
MLOAD
LOAD<= T000 50       ; 새 평가블록
OR>= T000 90         ; OR 추가
AND LOAD              ; M0000 AND (블록)
OUT P0040
MPOP
AND>= T000 50
AND<= T000 90
OUT P0041
END
```

### 과제 17 - 2타이머 OUT→TON (MPUSH 없이 같은 렁) ★ 정답 검증 완료
```
LOAD P0000
OR M0000
AND NOT T001
OUT M0000
TON T000 50           ; OUT 직후 TON → LOAD 없이 같은 렁 유지!
LOAD P0001
OR M0001
AND NOT T001
OUT M0001
TON T001 50
LOAD M0000
MPUSH
AND NOT T001
OUT P0040
MLOAD
AND>= T000 30
AND<= T001 20        ; 교차 타이머 비교!
OUT P0041
MPOP
AND>= T000 50
OUT P0042
END
```

### 과제 18 - LOADN 음변환검출 + 반복 ★ 정답 검증 완료
```
LOADN P0001           ; 음변환(falling edge) → 1스캔 펄스
OUT M0001
LOAD P0000
OR M0000
AND NOT M0001
OUT M0000
MPUSH
AND NOT T000
TON T000 90           ; T000 b접점 자동리셋 반복
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

### 상세 IL 패턴: [IL→래더 변환 패턴](il-to-ladder-patterns.md)
