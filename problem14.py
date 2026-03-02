"""
실습과제 14번 - 대칭 점등-소등 (구간 ON/OFF)
패턴3: >= AND <= 범위비교, 하나의 렁 + MPUSH

래더 구조 (답안 검증):
- P0000+P0001(b) → M0000 자기유지
- M0000 → TON T000 150
- T000(b접점) → P0040 (타이머 미완료 동안 ON = 0~15초)
- >= T000 30 AND <= T000 120 → P0041 (3~12초)
- >= T000 50 AND <= T000 100 → P0042 (5~10초)
"""
from common import run_problem

IL_COMMANDS = [
    "LOAD P0000",
    "OR M0000",
    "AND NOT P0001",
    "OUT M0000",
    "MPUSH",
    "TON T000 150",
    "MLOAD",
    "AND NOT T000",
    "OUT P0040",
    "MLOAD",
    "AND>= T000 30",
    "AND<= T000 120",
    "OUT P0041",
    "MPOP",
    "AND>= T000 50",
    "AND<= T000 100",
    "OUT P0042",
    "END",
]

if __name__ == "__main__":
    ok = run_problem(14, IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
