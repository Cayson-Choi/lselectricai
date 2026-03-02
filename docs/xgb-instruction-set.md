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

## Block Combination
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
