"""
실습과제 15번 - 순차 교체 (5초씩 교대)
패턴3: 구간 ON/OFF, 하나의 렁 + MPUSH

래더 구조 (답안 검증):
- P0000+P0001(b) → M0000 자기유지
- M0000 → TON T000 100
- <= T000 50 → P0040 (0~5초)
- >= T000 50 AND <= T000 100 → P0041 (5~10초)
- >= T000 100 → P0042 (10초~)
"""
from common import run_problem

IL_COMMANDS = [
    "LOAD P0000",
    "OR M0000",
    "AND NOT P0001",
    "OUT M0000",
    "MPUSH",
    "TON T000 100",
    "MLOAD",
    "AND<= T000 50",
    "OUT P0040",
    "MLOAD",
    "AND>= T000 50",
    "AND<= T000 100",
    "OUT P0041",
    "MPOP",
    "AND>= T000 100",
    "OUT P0042",
    "END",
]

if __name__ == "__main__":
    ok = run_problem(15, IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
