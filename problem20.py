"""
실습과제 20번 - 반복 동작 (사이클 타이머)
패턴6: TON+b접점 자동리셋, 가장 단순한 반복

래더 구조 (답안 검증):
렁0 (하나의 렁):
- P0000+P0001(b) → M0000 자기유지
- M0000 분기:
  - AND NOT T000 → TON T000 50 (5초 자동반복)
  - (직접연결) → P0040 (M0000 ON 동안 항상 ON)
  - AND>= T000 20 → P0041 (2~5초 ON = 3초ON, 2초OFF)
  - AND<= T000 30 → P0042 (0~3초 ON = 3초ON, 2초OFF)
"""
from common import run_problem

IL_COMMANDS = [
    "LOAD P0000",
    "OR M0000",
    "AND NOT P0001",
    "OUT M0000",
    "MPUSH",
    "AND NOT T000",
    "TON T000 50",
    "MLOAD",
    "OUT P0040",
    "MLOAD",
    "AND>= T000 20",
    "OUT P0041",
    "MPOP",
    "AND<= T000 30",
    "OUT P0042",
    "END",
]

if __name__ == "__main__":
    ok = run_problem(20, IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
