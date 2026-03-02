"""
실습과제 19번 - 딜레이 + 복수 사이클 타이머
패턴6 변형: 딜레이 타이머(T000) + 2개 사이클 타이머(T001, T002)

래더 구조 (답안 검증):
렁0:  P0000+P0001(b) → M0000 자기유지
      M0000 분기:
      - TON T000 10 (1초 딜레이)
      - AND NOT T001 → TON T001 60 (6초 사이클, 즉시 시작)
      - AND>= T001 40 → P0040 (4~6초 ON = 2초ON, 4초OFF)
렁14: T000 분기:
      - AND NOT T002 → TON T002 60 (6초 사이클, 1초 딜레이 후)
      - AND<= T002 30 → P0041 (0~3초 ON)
      - AND>= T002 30 → P0042 (3~6초 ON)
"""
from common import run_problem

IL_COMMANDS = [
    # 렁0: 자기유지 + 딜레이 + 사이클1
    "LOAD P0000",
    "OR M0000",
    "AND NOT P0001",
    "OUT M0000",
    "MPUSH",
    "TON T000 10",
    "MLOAD",
    "AND NOT T001",
    "TON T001 60",
    "MPOP",
    "AND>= T001 40",
    "OUT P0040",
    # 렁14: 사이클2 (T000 딜레이 후)
    "LOAD T000",
    "MPUSH",
    "AND NOT T002",
    "TON T002 60",
    "MLOAD",
    "AND<= T002 30",
    "OUT P0041",
    "MPOP",
    "AND>= T002 30",
    "OUT P0042",
    "END",
]

if __name__ == "__main__":
    ok = run_problem(19, IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
