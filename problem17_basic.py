"""
실습과제 17번 - a접점/b접점만 사용 (비교명령 없음)
타이머 4개(T000~T003) + 출력은 a접점/b접점 조합만

동작:
PB1 ON 시퀀스: RL 즉시ON → 3초 → GL ON → 2초 → YL ON
PB2 OFF 시퀀스: YL 즉시OFF → 2초 → GL OFF → 3초 → RL OFF

타이머 배치:
- T000(30): M0000 → 3초 후 a접점 ON → GL ON 시점
- T001(50): M0000 → 5초 후 a접점 ON → YL ON 시점
- T002(20): M0001 → PB2+2초 후 a접점 ON → GL OFF 시점
- T003(50): M0001 → PB2+5초 후 a접점 ON → RL OFF + 전체 리셋

출력 로직 (a접점/b접점만):
- RL = M0000(a) AND T003(b)     → M0000 ON이고 T003 미완료
- GL = T000(a) AND T002(b)      → 3초후 ON, PB2+2초후 OFF
- YL = T001(a) AND M0001(b)     → 5초후 ON, PB2 즉시 OFF
"""
from common import run_problem

IL_COMMANDS = [
    # 자기유지
    "LOAD P0000",
    "OR M0000",
    "AND NOT T003",
    "OUT M0000",
    # PB2 정지 시퀀스
    "LOAD P0001",
    "OR M0001",
    "AND NOT T003",
    "OUT M0001",
    # ON 시퀀스 타이머
    "LOAD M0000",
    "TON T000 30",       # 3초: GL ON 시점
    "LOAD M0000",
    "TON T001 50",       # 5초: YL ON 시점
    # OFF 시퀀스 타이머
    "LOAD M0001",
    "TON T002 20",       # PB2+2초: GL OFF 시점
    "LOAD M0001",
    "TON T003 50",       # PB2+5초: RL OFF + 전체 리셋
    # 출력 (a접점/b접점만)
    "LOAD M0000",
    "AND NOT T003",
    "OUT P0040",         # RL
    "LOAD T000",
    "AND NOT T002",
    "OUT P0041",         # GL
    "LOAD T001",
    "AND NOT M0001",
    "OUT P0042",         # YL
    "END",
]

if __name__ == "__main__":
    ok = run_problem(17, IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
