"""
실습과제 17번 - 2타이머 교차비교 (시작/정지 독립 시퀀스)
패턴5: 가장 복잡한 패턴, 다중 렁

래더 구조 (답안 검증):
렁0:  P0000+T001(b) → M0000 자기유지, M0000 → TON T000 50
렁6:  P0001+T001(b) → M0001 자기유지, M0001 → TON T001 50
렁12: M0000에서 분기:
      - AND NOT T001 → P0040
      - AND>= T000 30, AND<= T001 20 → P0041
      - AND>= T000 50 → P0042
"""
from common import run_problem

IL_COMMANDS = [
    # 렁0: M0000 자기유지 + TON T000
    "LOAD P0000",
    "OR M0000",
    "AND NOT T001",
    "OUT M0000",
    "TON T000 50",
    # 렁6: M0001 자기유지 + TON T001
    "LOAD P0001",
    "OR M0001",
    "AND NOT T001",
    "OUT M0001",
    "TON T001 50",
    # 렁12: 출력 분기
    "LOAD M0000",
    "MPUSH",
    "AND NOT T001",
    "OUT P0040",
    "MLOAD",
    "AND>= T000 30",
    "AND<= T001 20",
    "OUT P0041",
    "MPOP",
    "AND>= T000 50",
    "OUT P0042",
    "END",
]

if __name__ == "__main__":
    ok = run_problem(17, IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
