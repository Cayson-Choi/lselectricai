"""
실습과제 14~20 전체 자동 실행
각 과제마다 XG5000을 종료하고 처음부터 다시 시작
"""
import time
from common import log

from problem14 import IL_COMMANDS as IL_14
from problem15 import IL_COMMANDS as IL_15
from problem16 import IL_COMMANDS as IL_16
from problem17 import IL_COMMANDS as IL_17
from problem18 import IL_COMMANDS as IL_18
from problem19 import IL_COMMANDS as IL_19
from problem20 import IL_COMMANDS as IL_20
from common import run_problem, close_xg5000

PROBLEMS = [
    (14, IL_14),
    (15, IL_15),
    (16, IL_16),
    (17, IL_17),
    (18, IL_18),
    (19, IL_19),
    (20, IL_20),
]


def main():
    log("=" * 60)
    log("실습과제 14~20 전체 자동 실행")
    log("=" * 60)

    results = {}
    for i, (num, il_cmds) in enumerate(PROBLEMS):
        ok = run_problem(num, il_cmds)
        results[num] = ok

        # 마지막 과제가 아니면 사용자 확인 후 다음 진행
        if i < len(PROBLEMS) - 1:
            input(f"\n  과제 {num} 래더 확인 후 Enter를 누르면 다음 과제로 진행합니다...")
            close_xg5000()
            time.sleep(2)

    # 결과 요약
    log("\n" + "=" * 60)
    log("전체 결과 요약")
    log("=" * 60)
    for num, ok in results.items():
        status = "OK" if ok else "FAIL"
        log(f"  과제 {num}: {status}")

    total_ok = sum(1 for v in results.values() if v)
    log(f"\n  {total_ok}/{len(results)} 성공")
    log("=" * 60)


if __name__ == "__main__":
    main()
