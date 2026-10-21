import math

def generate_blocks(t):
    blocks = {}
    max_s = t.bit_length() - 1
    for s in range(0, max_s + 1):
        for r in range(1, (t >> s).bit_length() + 1):
            val = (1 << s) * ((1 << r) - 1)
            if val > t:
                break
            if val not in blocks:
                blocks[val] = (val, s, r)
    block_list = list(blocks.values())
    block_list.sort(key=lambda x: x[0])
    return block_list

def find_optimal_decompositions(t):
    blocks = generate_blocks(t)
    n = len(blocks)
    blocks_desc = sorted(blocks, key=lambda x: x[0], reverse=True)

    best_min = 0
    best_solutions = []
    current = []

    def dfs(start, remaining, last_val):
        nonlocal best_min, best_solutions

        if remaining == 0:
            if last_val is not None:
                if last_val > best_min:
                    best_min = last_val
                    best_solutions = [current.copy()]
                elif last_val == best_min:
                    if not best_solutions:
                        best_solutions.append(current.copy())
            return

        if last_val is not None and last_val <= best_min:
            return

        for i in range(start, n):
            val, s, r = blocks_desc[i]
            if val > remaining:
                continue
            if last_val is not None and val <= best_min:
                break

            current.append((val, s, r))
            dfs(i + 1, remaining - val, val)
            current.pop()

    dfs(0, t, None)
    return best_solutions

def calculate_std(values):
    n = len(values)
    if n == 0:
        return 0.0
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    return math.sqrt(variance)


def find_min_std_decompositions(t, max_solutions=1000):
    blocks = generate_blocks(t)
    # 按值升序排列，便于DP遍历（顺序无关）
    blocks_sorted = sorted(blocks, key=lambda x: x[0])
    n = len(blocks)
    # dp: (sum, count) -> min_sq
    dp = {(0, 0): 0}
    # 前驱字典： (new_sum, new_count) -> (prev_sum, prev_count, block_index)
    prev = {}

    for idx, (val, s, r) in enumerate(blocks_sorted):
        # 深拷贝当前状态，避免在本次迭代中重复使用同一个块
        items = list(dp.items())
        for (cur_sum, cur_count), cur_sq in items:
            new_sum = cur_sum + val
            if new_sum > t:
                continue
            new_count = cur_count + 1
            new_sq = cur_sq + val * val
            key = (new_sum, new_count)
            if key not in dp or new_sq < dp[key]:
                dp[key] = new_sq
                prev[key] = (cur_sum, cur_count, idx)

    # 找出所有 sum == t 的状态中标准差最小的
    best_std = float('inf')
    best_key = None
    for (s, c), sq in dp.items():
        if s == t and c > 0:
            mean = t / c
            variance = sq / c - mean * mean
            if variance < 0 and variance > -1e-9:
                variance = 0.0
            std = math.sqrt(variance)
            if std < best_std - 1e-12:
                best_std = std
                best_key = (s, c)

    if best_key is None:
        return float('inf'), []

    # 回溯重构组合
    solution = []
    cur_key = best_key
    while cur_key != (0, 0):
        prev_sum, prev_count, idx = prev[cur_key]
        val = blocks_sorted[idx][0]
        solution.append(blocks_sorted[idx])  # (val, s, r)
        cur_key = (prev_sum, prev_count)
    # 恢复降序（与原代码一致）
    solution.sort(key=lambda x: x[0], reverse=True)
    return best_std, [solution]

def find_min_count_decompositions(t, max_solutions=10000):
    blocks = generate_blocks(t)
    n = len(blocks)
    blocks_desc = sorted(blocks, key=lambda x: x[0], reverse=True)

    best_count = float('inf')
    best_solutions = []
    current = []

    def dfs(start, remaining, count):
        nonlocal best_count, best_solutions

        if remaining == 0:
            if count < best_count:
                best_count = count
                best_solutions = [current.copy()]
            elif count == best_count:
                if len(best_solutions) < max_solutions:
                    best_solutions.append(current.copy())
            return

        if count >= best_count:
            return

        if remaining < blocks[0][0]:
            return

        for i in range(start, n):
            val, s, r = blocks_desc[i]
            if val > remaining:
                continue

            current.append((val, s, r))
            dfs(i + 1, remaining - val, count + 1)
            current.pop()

    dfs(0, t, 0)
    return best_count, best_solutions

def format_solution(t, solution):
    values = sorted([val for val, _, _ in solution], reverse=True)
    return f"{t} = " + " + ".join(map(str, values))

def main():
    # 单次输入，计算后退出（不再循环）
    user_input = input("请输入预分解的数字：").strip()
    try:
        t = int(user_input)
    except ValueError:
        print("请输入有效的整数。")
        return

    # 1) 最优分解（最大化最小项）
    optimal_solutions = find_optimal_decompositions(t)
    if not optimal_solutions:
        print("无解")
        return
    opt_sol = optimal_solutions[0]
    opt_count = len(opt_sol)
    print("最优分解：", format_solution(t, opt_sol))
    min_val = min(val for val, _, _ in opt_sol)
    print(f"其最小块值为：{min_val}")

    print()  # 空行分隔

    # 2) 项数最少分解（无条件输出，并从中选出最小值最大的）
    best_count, count_solutions = find_min_count_decompositions(t)
    if count_solutions:
        # 从所有最少项数解中，挑选最小值最大的那一个
        best_min_in_count = -1
        best_sol_in_count = None
        for sol in count_solutions:
            min_val = min(val for val, _, _ in sol)
            if min_val > best_min_in_count:
                best_min_in_count = min_val
                best_sol_in_count = sol
        if best_sol_in_count is not None:
            print("项数最少分解：", format_solution(t, best_sol_in_count))
            print(f"其最小项数为：{best_count}")

    print()  # 空行分隔

    # 3) 标准差最小分解
    best_std, std_solutions = find_min_std_decompositions(t)
    if std_solutions:
        for sol in std_solutions:
            print("标准差最小分解：", format_solution(t, sol))
        print(f"其最小标准差为：{best_std:.6f}")
    else:
        print("无标准差最小分解")

    print()  # 空行分隔

if __name__ == "__main__":
    main()