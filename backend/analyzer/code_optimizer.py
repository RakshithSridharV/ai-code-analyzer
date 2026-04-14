def get_optimized_code(patterns, time_complexity, language):
    result = {}

    # -------- NESTED LOOPS --------
    if "nested_loop" in patterns:
        result["issue"] = "Nested loops detected"
        result["before_complexity"] = time_complexity
        result["after_complexity"] = "O(n)"

        if language == "python":
            result["optimized_code"] = (
                "Use a single loop.\n"
                "Example:\n"
                "for i in range(n):\n"
                "    print(i)"
            )

        elif language == "javascript":
            result["optimized_code"] = (
                "Use a single loop.\n"
                "Example:\n"
                "for (let i = 0; i < n; i++) {\n"
                "    console.log(i);\n"
                "}"
            )

        elif language == "java":
            result["optimized_code"] = (
                "Use a single loop.\n"
                "Example:\n"
                "for (int i = 0; i < n; i++) {\n"
                "    System.out.println(i);\n"
                "}"
            )

        else:  # C / C++
            result["optimized_code"] = (
                "Use a single loop.\n"
                "Example:\n"
                "for (int i = 0; i < n; i++) {\n"
                "    printf(\"%d\", i);\n"
                "}"
            )

        return result

    # -------- INEFFICIENT RECURSION --------
    if "inefficient_recursion" in patterns:
        result["issue"] = "Inefficient recursion detected"
        result["before_complexity"] = time_complexity
        result["after_complexity"] = "O(n)"

        if language == "python":
            result["optimized_code"] = (
                "Use memoization.\n"
                "Example:\n"
                "def fib(n, memo={}):\n"
                "    if n in memo:\n"
                "        return memo[n]\n"
                "    if n <= 1:\n"
                "        return n\n"
                "    memo[n] = fib(n-1) + fib(n-2)\n"
                "    return memo[n]"
            )

        elif language == "javascript":
            result["optimized_code"] = (
                "Use memoization.\n"
                "Example:\n"
                "function fib(n, memo = {}) {\n"
                "    if (memo[n]) return memo[n];\n"
                "    if (n <= 1) return n;\n"
                "    memo[n] = fib(n-1, memo) + fib(n-2, memo);\n"
                "    return memo[n];\n"
                "}"
            )

        elif language == "java":
            result["optimized_code"] = (
                "Use memoization.\n"
                "Example:\n"
                "static int fib(int n, Map<Integer, Integer> memo) {\n"
                "    if (memo.containsKey(n)) return memo.get(n);\n"
                "    if (n <= 1) return n;\n"
                "    int val = fib(n-1, memo) + fib(n-2, memo);\n"
                "    memo.put(n, val);\n"
                "    return val;\n"
                "}"
            )

        else:  # C / C++
            result["optimized_code"] = (
                "Use memoization.\n"
                "Example:\n"
                "int fib(int n, int memo[]) {\n"
                "    if (memo[n] != -1) return memo[n];\n"
                "    if (n <= 1) return n;\n"
                "    memo[n] = fib(n-1, memo) + fib(n-2, memo);\n"
                "    return memo[n];\n"
                "}"
            )

        return result

    # -------- EXTRA MEMORY --------
    if "extra_memory" in patterns:
        result["issue"] = "Extra memory usage detected"
        result["before_complexity"] = time_complexity
        result["after_complexity"] = time_complexity
        result["optimized_code"] = (
            "Avoid unnecessary data structures.\n"
            "Prefer in-place operations where possible."
        )
        return result

    return None