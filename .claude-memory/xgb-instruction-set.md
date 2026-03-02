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

## Block Combination
| IL | Function |
|---|---|
| AND LOAD | 블록 직렬 결합 |
| OR LOAD | 블록 병렬 결합 |
| MPUSH/MLOAD/MPOP | 스택 분기 (XGB: 8단계) |

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

## 실습과제 11 IL Program
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
