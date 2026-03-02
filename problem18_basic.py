"""
실습과제 18번 - a접점/b접점만 사용 (비교명령 없음)
타이머 3개(T000~T002) + T002 b접점 자동리셋 반복

동작:
PB1 → 반복 사이클: RL(2초) → GL(3초) → BZ(4초) → 리셋 반복
PB2 놓으면 정지 (LOADN 음변환검출)

타이머 배치 (공통 입력: M0000 AND NOT T002):
- T000(20): 2초 후 ON → RL OFF / GL ON 시점
- T001(50): 5초 후 ON → GL OFF / BZ ON 시점
- T002(90): 9초 후 ON → BZ OFF + 사이클 리셋 (b접점)

출력 로직 (a접점/b접점만):
- RL = M0000(a) AND T000(b) → M0000 ON이고 2초 전까지
- GL = T000(a) AND T001(b) → 2초후~5초전
- BZ = T001(a) AND T002(b) → 5초후~9초전
"""
from common import run_problem

IL_COMMANDS = [
    # PB2 음변환검출 (놓을 때 1스캔 ON)
    "LOADN P0001",
    "OUT M0001",
    # 자기유지
    "LOAD P0000",
    "OR M0000",
    "AND NOT M0001",
    "OUT M0000",
    # 타이머 (공통 입력 + MPUSH 분기)
    "LOAD M0000",
    "AND NOT T002",
    "MPUSH",
    "TON T000 20",       # 2초: RL→GL 전환
    "MLOAD",
    "TON T001 50",       # 5초: GL→BZ 전환
    "MPOP",
    "TON T002 90",       # 9초: 사이클 리셋
    # 출력 (a접점/b접점만)
    "LOAD M0000",
    "AND NOT T000",
    "OUT P0040",         # RL: 0~2초
    "LOAD T000",
    "AND NOT T001",
    "OUT P0041",         # GL: 2~5초
    "LOAD T001",
    "AND NOT T002",
    "OUT P0042",         # BZ: 5~9초
    "END",
]

if __name__ == "__main__":
    ok = run_problem(18, IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
