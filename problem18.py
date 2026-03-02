"""
실습과제 18번 - 반복 동작 + 음변환검출(N에지)
패턴6: TON+b접점 자동리셋 사이클

래더 구조 (답안 검증):
렁0:  P0001 음변환검출(LOADN) → M0001 (1스캔 펄스)
렁3:  P0000+M0001(b) → M0000 자기유지
      M0000 분기:
      - AND NOT T000 → TON T000 90 (9초 자동반복)
      - AND<= T000 20 → P0040 (0~2초)
      - AND>= T000 20, AND<= T000 50 → P0041 (2~5초)
      - AND>= T000 50 → P0042 (5~9초)
"""
from common import run_problem

IL_COMMANDS = [
    # 렁0: 양변환검출
    "LOADN P0001",
    "OUT M0001",
    # 렁3: 자기유지 + 반복타이머 + 출력
    "LOAD P0000",
    "OR M0000",
    "AND NOT M0001",
    "OUT M0000",
    "MPUSH",
    "AND NOT T000",
    "TON T000 90",
    "MLOAD",
    "AND<= T000 20",
    "OUT P0040",
    "MLOAD",
    "AND>= T000 20",
    "AND<= T000 50",
    "OUT P0041",
    "MPOP",
    "AND>= T000 50",
    "OUT P0042",
    "END",
]

if __name__ == "__main__":
    ok = run_problem(18, IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
