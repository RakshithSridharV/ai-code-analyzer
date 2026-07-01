from analyzer.java_analyzer import analyze_java_code
from analyzer.js_analyzer import analyze_js_code
from analyzer.c_analyzer import analyze_c_code

# ── JAVA: Trapping Rain Water (LeetCode #42) - O(n^2)
java_brute = """
public int trap(int[] height) {
    int n = height.length;
    int water = 0;
    for (int i = 0; i < n; i++) {
        int leftMax = 0, rightMax = 0;
        for (int j = 0; j <= i; j++)
            leftMax = Math.max(leftMax, height[j]);
        for (int j = i; j < n; j++)
            rightMax = Math.max(rightMax, height[j]);
        water += Math.min(leftMax, rightMax) - height[i];
    }
    return water;
}"""

java_fib = """
public int fib(int n) {
    if (n <= 1) return n;
    return fib(n-1) + fib(n-2);
}"""

java_bsearch = """
public int search(int[] nums, int target) {
    int left = 0, right = nums.length - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) return mid;
        else if (nums[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}"""

print("=== JAVA ===")
r = analyze_java_code(java_brute)
print(f"Trapping Rain Water: {r['time_complexity']} / {r['space_complexity']}  (expected O(n^2)/O(1))")
r2 = analyze_java_code(java_fib)
print(f"Fibonacci recursive: {r2['time_complexity']} / {r2['space_complexity']}  (expected O(2^n)/O(n))")
r3 = analyze_java_code(java_bsearch)
print(f"Binary Search:       {r3['time_complexity']} / {r3['space_complexity']}  (expected O(log n)/O(1))")

# ── JS tests ──────────────────────────────────────────────────────────────────
js_twosum = """
var twoSum = function(nums, target) {
    const map = new Map();
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (map.has(complement)) return [map.get(complement), i];
        map.set(nums[i], i);
    }
};"""

js_bubble = """
var sortColors = function(nums) {
    for (let i = 0; i < nums.length; i++) {
        for (let j = 0; j < nums.length - i - 1; j++) {
            if (nums[j] > nums[j+1]) {
                let tmp = nums[j]; nums[j] = nums[j+1]; nums[j+1] = tmp;
            }
        }
    }
};"""

js_arrow = """
const maxProfit = (prices) => {
    let maxP = 0, minP = Infinity;
    prices.forEach(price => {
        minP = Math.min(minP, price);
        maxP = Math.max(maxP, price - minP);
    });
    return maxP;
};"""

print("\n=== JAVASCRIPT ===")
tc, sc, rec, lp = analyze_js_code(js_twosum)
print(f"Two Sum (HashMap):   {tc} / {sc}  (expected O(n)/O(n))")
tc2, sc2, _, _ = analyze_js_code(js_bubble)
print(f"Bubble Sort:         {tc2} / {sc2}  (expected O(n^2)/O(1))")
tc3, sc3, _, _ = analyze_js_code(js_arrow)
print(f"Max Profit (arrow):  {tc3} / {sc3}  (expected O(n)/O(1))")

# ── C tests ───────────────────────────────────────────────────────────────────
c_bsearch = """
int binarySearch(int arr[], int n, int target) {
    int left = 0, right = n - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}"""

c_matrix = """
void multiply(int a[10][10], int b[10][10], int c[10][10]) {
    for (int i = 0; i < 10; i++)
        for (int j = 0; j < 10; j++)
            for (int k = 0; k < 10; k++)
                c[i][j] += a[i][k] * b[k][j];
}"""

c_sort = """
int cmp(const void* a, const void* b) { return *(int*)a - *(int*)b; }
void sortArray(int* nums, int n) {
    qsort(nums, n, sizeof(int), cmp);
}"""

c_recursive = """
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}"""

print("\n=== C ===")
tc, sc, rec, lp = analyze_c_code(c_bsearch)
print(f"Binary Search:       {tc} / {sc}  (expected O(log n)/O(1))")
tc2, sc2, _, _ = analyze_c_code(c_matrix)
print(f"Matrix Multiply 3D:  {tc2} / {sc2}  (expected O(n^3)/O(1))")
tc3, sc3, _, _ = analyze_c_code(c_sort)
print(f"qsort call:          {tc3} / {sc3}  (expected O(n log n)/O(n))")
tc4, sc4, rec4, _ = analyze_c_code(c_recursive)
print(f"Factorial recursive: {tc4} / {sc4}  (expected O(n)/O(n)), recursive={rec4}")
