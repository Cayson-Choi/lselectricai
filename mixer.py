"""
혼합기 제어 PLC 프로그램
순차 제어 (SET/RST) + 타이머 3개

동작 시퀀스:
  P0 시작 → P20 ON(액체A) → P3 감지 → P20 OFF, P21 ON(액체B)
  → P4 감지 → P21 OFF → 5초 대기 → P23 ON(모터 10초)
  → P23 OFF → 5초 대기 → P22 ON(배출) → 조건해제 시 P22 OFF

스텝:
  M0000: 액체A 주입 (P20 ON)
  M0001: 액체B 주입 (P21 ON)
  M0002: 혼합 전 5초 대기
  M0003: 혼합 모터 10초 (P23 ON)
  M0004: 배출 전 5초 대기
  M0005: 배출 (P22 ON)

타이머:
  T000(50): 혼합 전 5초
  T001(100): 모터 10초
  T002(50): 배출 전 5초
"""
from common import run_problem

IL_COMMANDS = [
    # 시작 (유휴 상태에서만)
    "LOAD P0000",
    "AND NOT M0001",
    "AND NOT M0002",
    "AND NOT M0003",
    "AND NOT M0004",
    "AND NOT M0005",
    "SET M0000",
    # Step 0→1: P3 감지 → 액체B 주입
    "LOAD M0000",
    "AND P0003",
    "SET M0001",
    "RST M0000",
    # Step 1→2: P4 감지 → 대기
    "LOAD M0001",
    "AND P0004",
    "SET M0002",
    "RST M0001",
    # Step 2: 혼합 전 5초 대기
    "LOAD M0002",
    "TON T000 50",
    # Step 2→3: T000 완료 → 모터 시작
    "LOAD T000",
    "SET M0003",
    "RST M0002",
    # Step 3: 모터 10초 동작
    "LOAD M0003",
    "TON T001 100",
    # Step 3→4: T001 완료 → 대기
    "LOAD T001",
    "SET M0004",
    "RST M0003",
    # Step 4: 배출 전 5초 대기
    "LOAD M0004",
    "TON T002 50",
    # Step 4→5: T002 완료 → 배출
    "LOAD T002",
    "SET M0005",
    "RST M0004",
    # 출력
    "LOAD M0000",
    "OUT P0020",         # 밸브A (액체A 주입)
    "LOAD M0001",
    "OUT P0021",         # 밸브B (액체B 주입)
    "LOAD M0003",
    "OUT P0023",         # 혼합 모터
    "LOAD M0005",
    "OUT P0022",         # 배출 밸브
    "END",
]

if __name__ == "__main__":
    ok = run_problem("Mixer", IL_COMMANDS)
    print(f"\n{'성공!' if ok else '확인 필요'}")
