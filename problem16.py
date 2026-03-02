"""
실습과제 16번 - 재점등 (OFF 후 다시 ON)
패턴4: OR 병렬 비교, 하나의 렁 + MPUSH + LOAD/OR/AND LOAD 블록결합

래더 구조 (답안 검증):
- P0000+P0001(b) → M0000 자기유지
- M0000 → TON T000 90
- (<= T000 50) OR (>= T000 90) → P0040 (0~5초 OR 9초~)
- >= T000 50 AND <= T000 90 → P0041 (5~9초)
- P0042 없음 (출력 2개만)
"""
from common import run_problem

IL_COMMANDS = [
    "LOAD P0000",
    "OR M0000",
    "AND NOT P0001",
    "OUT M0000",
    "MPUSH",
    "TON T000 90",
    "MLOAD",
    "LOAD<= T000 50",
    "OR>= T000 90",
    "AND LOAD",
    "OUT P0040",
    "MPOP",
    "AND>= T000 50",
    "AND<= T000 90",
    "OUT P0041",
    "END",
]

if __name__ == "__main__":
    ok = run_problem(16, IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
