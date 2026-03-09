def get_optimized_code(patterns, time_complexity, language):
    """
    Generate optimized code suggestions based on detected patterns.
    Returns a dict with issue, description, before/after complexity, and optimized code.
    """
    result = {}

    # -------- NESTED LOOPS --------
    if "nested_loop" in patterns:
        result["issue"] = "Nested loops detected"
        result["description"] = (
            "Nested loops multiply the iteration count, leading to quadratic or worse complexity. "
            "The key strategy is to replace the inner loop with a hash-based lookup (O(1) average), "
            "use sorting + two-pointer techniques, or precompute values to avoid redundant work."
        )
        result["before_complexity"] = time_complexity
        result["after_complexity"] = "O(n)"

        if language == "python":
            result["optimized_code"] = (
                "# Instead of nested loops for pair-finding:\n"
                "# BEFORE: O(n²)\n"
                "# for i in range(n):\n"
                "#     for j in range(n):\n"
                "#         if arr[i] + arr[j] == target: ...\n\n"
                "# AFTER: O(n) using a hash set\n"
                "def find_pair(arr, target):\n"
                "    seen = set()\n"
                "    for num in arr:\n"
                "        complement = target - num\n"
                "        if complement in seen:\n"
                "            return (complement, num)\n"
                "        seen.add(num)\n"
                "    return None"
            )
        elif language == "javascript":
            result["optimized_code"] = (
                "// Instead of nested loops for pair-finding:\n"
                "// BEFORE: O(n²) — nested for loops\n"
                "// AFTER: O(n) using a Set\n"
                "function findPair(arr, target) {\n"
                "    const seen = new Set();\n"
                "    for (const num of arr) {\n"
                "        const complement = target - num;\n"
                "        if (seen.has(complement)) {\n"
                "            return [complement, num];\n"
                "        }\n"
                "        seen.add(num);\n"
                "    }\n"
                "    return null;\n"
                "}"
            )
        elif language == "java":
            result["optimized_code"] = (
                "// Instead of nested loops for pair-finding:\n"
                "// BEFORE: O(n²) — nested for loops\n"
                "// AFTER: O(n) using a HashSet\n"
                "static int[] findPair(int[] arr, int target) {\n"
                "    Set<Integer> seen = new HashSet<>();\n"
                "    for (int num : arr) {\n"
                "        int complement = target - num;\n"
                "        if (seen.contains(complement)) {\n"
                "            return new int[]{complement, num};\n"
                "        }\n"
                "        seen.add(num);\n"
                "    }\n"
                "    return null;\n"
                "}"
            )
        else:  # C / C++
            result["optimized_code"] = (
                "// Instead of nested loops, use sorting + two pointers:\n"
                "// BEFORE: O(n²) — nested for loops\n"
                "// AFTER: O(n log n) using sort + two pointers\n"
                "void findPair(int arr[], int n, int target) {\n"
                "    qsort(arr, n, sizeof(int), compare);\n"
                "    int left = 0, right = n - 1;\n"
                "    while (left < right) {\n"
                "        int sum = arr[left] + arr[right];\n"
                "        if (sum == target) return;\n"
                "        else if (sum < target) left++;\n"
                "        else right--;\n"
                "    }\n"
                "}"
            )
        return result

    # -------- INEFFICIENT RECURSION --------
    if "inefficient_recursion" in patterns:
        result["issue"] = "Inefficient recursion (branching)"
        result["description"] = (
            "Branching recursion (e.g., calling f(n-1) + f(n-2)) causes exponential blowup "
            "because the same subproblems are solved repeatedly. Memoization caches results "
            "to avoid redundant computation, reducing time from O(2^n) to O(n)."
        )
        result["before_complexity"] = time_complexity
        result["after_complexity"] = "O(n)"

        if language == "python":
            result["optimized_code"] = (
                "# TECHNIQUE: Memoization (Top-Down DP)\n"
                "# Cache previously computed results to avoid redundant work.\n\n"
                "from functools import lru_cache\n\n"
                "@lru_cache(maxsize=None)\n"
                "def fib(n):\n"
                "    if n <= 1:\n"
                "        return n\n"
                "    return fib(n - 1) + fib(n - 2)\n\n"
                "# Or use Bottom-Up DP (iterative):\n"
                "def fib_iterative(n):\n"
                "    if n <= 1:\n"
                "        return n\n"
                "    a, b = 0, 1\n"
                "    for _ in range(2, n + 1):\n"
                "        a, b = b, a + b\n"
                "    return b"
            )
        elif language == "javascript":
            result["optimized_code"] = (
                "// TECHNIQUE: Memoization (Top-Down DP)\n"
                "function fib(n, memo = {}) {\n"
                "    if (memo[n] !== undefined) return memo[n];\n"
                "    if (n <= 1) return n;\n"
                "    memo[n] = fib(n - 1, memo) + fib(n - 2, memo);\n"
                "    return memo[n];\n"
                "}\n\n"
                "// Or Bottom-Up DP (iterative):\n"
                "function fibIterative(n) {\n"
                "    if (n <= 1) return n;\n"
                "    let a = 0, b = 1;\n"
                "    for (let i = 2; i <= n; i++) {\n"
                "        [a, b] = [b, a + b];\n"
                "    }\n"
                "    return b;\n"
                "}"
            )
        elif language == "java":
            result["optimized_code"] = (
                "// TECHNIQUE: Memoization (Top-Down DP)\n"
                "static Map<Integer, Integer> memo = new HashMap<>();\n\n"
                "static int fib(int n) {\n"
                "    if (memo.containsKey(n)) return memo.get(n);\n"
                "    if (n <= 1) return n;\n"
                "    int val = fib(n - 1) + fib(n - 2);\n"
                "    memo.put(n, val);\n"
                "    return val;\n"
                "}"
            )
        else:
            result["optimized_code"] = (
                "// TECHNIQUE: Bottom-Up DP (iterative)\n"
                "int fib(int n) {\n"
                "    if (n <= 1) return n;\n"
                "    int a = 0, b = 1, temp;\n"
                "    for (int i = 2; i <= n; i++) {\n"
                "        temp = b;\n"
                "        b = a + b;\n"
                "        a = temp;\n"
                "    }\n"
                "    return b;\n"
                "}"
            )
        return result

    # -------- LINEAR RECURSION --------
    if "linear_recursion" in patterns:
        result["issue"] = "Linear recursion detected"
        result["description"] = (
            "This function uses a single recursive self-call per invocation. "
            "While correct, it uses O(n) stack space and risks stack overflow on large inputs. "
            "Converting to an iterative loop eliminates the stack overhead."
        )
        result["before_complexity"] = time_complexity
        result["after_complexity"] = time_complexity.replace("+ recursion stack", "").strip()

        if language == "python":
            result["optimized_code"] = (
                "# TECHNIQUE: Convert recursion to iteration\n"
                "# BEFORE (recursive):\n"
                "# def factorial(n):\n"
                "#     if n <= 1: return 1\n"
                "#     return n * factorial(n - 1)\n\n"
                "# AFTER (iterative — O(1) space):\n"
                "def factorial(n):\n"
                "    result = 1\n"
                "    for i in range(2, n + 1):\n"
                "        result *= i\n"
                "    return result"
            )
        elif language == "javascript":
            result["optimized_code"] = (
                "// TECHNIQUE: Convert recursion to iteration\n"
                "function factorial(n) {\n"
                "    let result = 1;\n"
                "    for (let i = 2; i <= n; i++) {\n"
                "        result *= i;\n"
                "    }\n"
                "    return result;\n"
                "}"
            )
        elif language == "java":
            result["optimized_code"] = (
                "// TECHNIQUE: Convert recursion to iteration\n"
                "static long factorial(int n) {\n"
                "    long result = 1;\n"
                "    for (int i = 2; i <= n; i++) {\n"
                "        result *= i;\n"
                "    }\n"
                "    return result;\n"
                "}"
            )
        else:
            result["optimized_code"] = (
                "// TECHNIQUE: Convert recursion to iteration\n"
                "long long factorial(int n) {\n"
                "    long long result = 1;\n"
                "    for (int i = 2; i <= n; i++) {\n"
                "        result *= i;\n"
                "    }\n"
                "    return result;\n"
                "}"
            )
        return result

    # -------- EXTRA MEMORY --------
    if "extra_memory" in patterns:
        result["issue"] = "Extra memory usage detected"
        result["description"] = (
            "The code allocates data structures (lists, dicts, sets) proportional to input size. "
            "Consider whether in-place algorithms, generators, or streaming approaches "
            "could reduce memory usage without sacrificing readability."
        )
        result["before_complexity"] = time_complexity
        result["after_complexity"] = time_complexity
        result["optimized_code"] = (
            "# Consider these memory optimization strategies:\n"
            "# 1. Use generators instead of lists: (x for x in range(n))\n"
            "# 2. Process data in chunks instead of loading all at once\n"
            "# 3. Use in-place sorting: arr.sort() instead of sorted(arr)\n"
            "# 4. Reuse variables instead of creating new collections"
        )
        return result

    return None