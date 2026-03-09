/* =====================================================================
   AI CODE ANALYZER — PREMIUM FRONTEND ENGINE v2.0
   Features: interactive particle constellation, complexity growth chart,
   confetti celebration, analysis history, code examples, live stats,
   theme toggle, export, code metrics dashboard, keyboard shortcuts.
   ===================================================================== */

// ============================= CONSTANTS =============================
const API_URL = "http://127.0.0.1:5000/analyze";
const HISTORY_KEY = "ai_code_analyzer_history";
const THEME_KEY = "ai_code_analyzer_theme";
const SCORE_CIRCUMFERENCE = 2 * Math.PI * 52; // ~326.73

// Store last analysis for export
let lastAnalysisData = null;

// ============================= CODE EXAMPLES =========================
const CODE_EXAMPLES = {
    python: [
        {
            title: "Fibonacci (Inefficient Recursion)",
            desc: "Classic O(2^n) exponential recursion",
            difficulty: "danger",
            code: `def fib(n):\n    if n <= 1:\n        return n\n    return fib(n - 1) + fib(n - 2)`
        },
        {
            title: "Bubble Sort (Nested Loops)",
            desc: "O(n²) nested loop pattern",
            difficulty: "warning",
            code: `def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n    return arr`
        },
        {
            title: "Binary Search (Efficient)",
            desc: "O(log n) optimized search",
            difficulty: "success",
            code: `def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1`
        },
        {
            title: "Simple Factorial (Recursion)",
            desc: "O(n) linear recursion",
            difficulty: "info",
            code: `def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)`
        },
        {
            title: "Merge Sort",
            desc: "O(n log n) divide and conquer",
            difficulty: "success",
            code: `def merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i])\n            i += 1\n        else:\n            result.append(right[j])\n            j += 1\n    result.extend(left[i:])\n    result.extend(right[j:])\n    return result`
        },
        {
            title: "Two Sum (Hash Map)",
            desc: "O(n) efficient lookup",
            difficulty: "success",
            code: `def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []`
        },
        {
            title: "Matrix Multiplication",
            desc: "O(n³) triple nested loops",
            difficulty: "danger",
            code: `def matrix_multiply(A, B):\n    rows_A, cols_A = len(A), len(A[0])\n    cols_B = len(B[0])\n    result = [[0] * cols_B for _ in range(rows_A)]\n    for i in range(rows_A):\n        for j in range(cols_B):\n            for k in range(cols_A):\n                result[i][j] += A[i][k] * B[k][j]\n    return result`
        },
        {
            title: "Linear Search",
            desc: "O(n) simple traversal",
            difficulty: "info",
            code: `def linear_search(arr, target):\n    for i in range(len(arr)):\n        if arr[i] == target:\n            return i\n    return -1`
        }
    ],
    javascript: [
        {
            title: "Fibonacci (Inefficient Recursion)",
            desc: "Classic O(2^n) exponential recursion",
            difficulty: "danger",
            code: `function fib(n) {\n    if (n <= 1) return n;\n    return fib(n - 1) + fib(n - 2);\n}`
        },
        {
            title: "Nested Loop Sum",
            desc: "O(n²) nested iteration",
            difficulty: "warning",
            code: `function nestedSum(n) {\n    let sum = 0;\n    for (let i = 0; i < n; i++) {\n        for (let j = 0; j < n; j++) {\n            sum += i + j;\n        }\n    }\n    return sum;\n}`
        },
        {
            title: "Linear Search",
            desc: "O(n) single loop",
            difficulty: "info",
            code: `function linearSearch(arr, target) {\n    for (let i = 0; i < arr.length; i++) {\n        if (arr[i] === target) return i;\n    }\n    return -1;\n}`
        },
        {
            title: "Quick Sort",
            desc: "O(n log n) avg, recursive partitioning",
            difficulty: "success",
            code: `function quickSort(arr) {\n    if (arr.length <= 1) return arr;\n    const pivot = arr[arr.length - 1];\n    const left = arr.filter((x, i) => x <= pivot && i < arr.length - 1);\n    const right = arr.filter(x => x > pivot);\n    return [...quickSort(left), pivot, ...quickSort(right)];\n}`
        },
        {
            title: "Debounce Function",
            desc: "O(1) utility function",
            difficulty: "success",
            code: `function debounce(fn, delay) {\n    let timer;\n    return function(...args) {\n        clearTimeout(timer);\n        timer = setTimeout(() => fn.apply(this, args), delay);\n    };\n}`
        }
    ],
    java: [
        {
            title: "Factorial (Recursion)",
            desc: "O(n) recursive approach",
            difficulty: "info",
            code: `public class Main {\n    static int factorial(int n) {\n        if (n <= 1) return 1;\n        return n * factorial(n - 1);\n    }\n}`
        },
        {
            title: "Matrix Print (Nested Loops)",
            desc: "O(n²) nested iteration",
            difficulty: "warning",
            code: `public class Main {\n    static void printMatrix(int[][] matrix) {\n        for (int i = 0; i < matrix.length; i++) {\n            for (int j = 0; j < matrix[0].length; j++) {\n                System.out.print(matrix[i][j] + " ");\n            }\n            System.out.println();\n        }\n    }\n}`
        },
        {
            title: "Binary Search",
            desc: "O(log n) efficient search",
            difficulty: "success",
            code: `public class Main {\n    static int binarySearch(int[] arr, int target) {\n        int low = 0, high = arr.length - 1;\n        while (low <= high) {\n            int mid = (low + high) / 2;\n            if (arr[mid] == target) return mid;\n            else if (arr[mid] < target) low = mid + 1;\n            else high = mid - 1;\n        }\n        return -1;\n    }\n}`
        },
        {
            title: "Fibonacci (Branching Recursion)",
            desc: "O(2^n) exponential recursion",
            difficulty: "danger",
            code: `public class Main {\n    static int fib(int n) {\n        if (n <= 1) return n;\n        return fib(n - 1) + fib(n - 2);\n    }\n}`
        }
    ],
    c: [
        {
            title: "Factorial (Recursion)",
            desc: "O(n) recursive approach",
            difficulty: "info",
            code: `int factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n - 1);\n}`
        },
        {
            title: "Sum of Array (Single Loop)",
            desc: "O(n) linear traversal",
            difficulty: "success",
            code: `int sum(int arr[], int n) {\n    int total = 0;\n    for (int i = 0; i < n; i++) {\n        total += arr[i];\n    }\n    return total;\n}`
        },
        {
            title: "Bubble Sort",
            desc: "O(n²) nested loops",
            difficulty: "warning",
            code: `void bubbleSort(int arr[], int n) {\n    for (int i = 0; i < n - 1; i++) {\n        for (int j = 0; j < n - i - 1; j++) {\n            if (arr[j] > arr[j + 1]) {\n                int temp = arr[j];\n                arr[j] = arr[j + 1];\n                arr[j + 1] = temp;\n            }\n        }\n    }\n}`
        }
    ],
    cpp: [
        {
            title: "Fibonacci (Recursion)",
            desc: "O(2^n) exponential recursion",
            difficulty: "danger",
            code: `#include <iostream>\nusing namespace std;\n\nint fib(int n) {\n    if (n <= 1) return n;\n    return fib(n - 1) + fib(n - 2);\n}`
        },
        {
            title: "Vector Sum (STL)",
            desc: "O(n) linear traversal",
            difficulty: "success",
            code: `#include <vector>\n#include <iostream>\nusing namespace std;\n\nint vectorSum(vector<int>& v) {\n    int total = 0;\n    for (int i = 0; i < v.size(); i++) {\n        total += v[i];\n    }\n    return total;\n}`
        }
    ]
};

// ============================= INIT ==================================
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initParticles();
    initLineNumbers();
    initExampleTabs();
    renderExamples("python");
    initKeyboardShortcuts();
});

// ============================= THEME TOGGLE ==========================
function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) {
        document.documentElement.setAttribute("data-theme", saved);
    }
}

function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    localStorage.setItem(THEME_KEY, next);
    showToast(`Switched to ${next} mode`, "info");
}

// ============================= PARTICLE CONSTELLATION =================
function initParticles() {
    const canvas = document.getElementById("particles");
    const ctx = canvas.getContext("2d");
    let w, h, particles;
    let mouseX = -1000, mouseY = -1000;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    window.addEventListener("resize", resize);
    resize();

    // Track mouse for interactive particles
    document.addEventListener("mousemove", (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    const COUNT = 60;
    const MAX_DIST = 130;
    const MOUSE_DIST = 180;

    particles = Array.from({ length: COUNT }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 1.8 + 0.5,
        opacity: Math.random() * 0.4 + 0.15
    }));

    function draw() {
        ctx.clearRect(0, 0, w, h);

        // Draw connections between particles
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < MAX_DIST) {
                    const alpha = (1 - dist / MAX_DIST) * 0.12;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(108, 99, 255, ${alpha})`;
                    ctx.lineWidth = 0.6;
                    ctx.stroke();
                }
            }
        }

        // Draw particles and apply mouse interaction
        particles.forEach(p => {
            // Mouse repulsion effect
            const dx = mouseX - p.x;
            const dy = mouseY - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < MOUSE_DIST && dist > 0) {
                const force = (1 - dist / MOUSE_DIST) * 0.8;
                p.vx -= (dx / dist) * force * 0.05;
                p.vy -= (dy / dist) * force * 0.05;

                // Draw connection to mouse
                const alpha = (1 - dist / MOUSE_DIST) * 0.15;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(mouseX, mouseY);
                ctx.strokeStyle = `rgba(168, 85, 247, ${alpha})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(108, 99, 255, ${p.opacity})`;
            ctx.fill();

            // Move with damping
            p.x += p.vx;
            p.y += p.vy;
            p.vx *= 0.99;
            p.vy *= 0.99;

            // Add base velocity if too slow
            if (Math.abs(p.vx) < 0.1) p.vx += (Math.random() - 0.5) * 0.1;
            if (Math.abs(p.vy) < 0.1) p.vy += (Math.random() - 0.5) * 0.1;

            // Wrap
            if (p.x < -10) p.x = w + 10;
            if (p.x > w + 10) p.x = -10;
            if (p.y < -10) p.y = h + 10;
            if (p.y > h + 10) p.y = -10;
        });

        requestAnimationFrame(draw);
    }

    draw();
}

// ============================= LINE NUMBERS & STATS ==================
function initLineNumbers() {
    const textarea = document.getElementById("code");
    const lineNumsEl = document.getElementById("line-numbers");
    const lineCountEl = document.getElementById("line-count");
    const charCountEl = document.getElementById("char-count");

    function update() {
        const val = textarea.value;
        const lines = val.split("\n");
        const lineCount = lines.length;

        lineNumsEl.textContent = lines.map((_, i) => i + 1).join("\n");
        lineCountEl.textContent = `${lineCount} line${lineCount !== 1 ? "s" : ""}`;
        charCountEl.textContent = `${val.length} char${val.length !== 1 ? "s" : ""}`;
    }

    textarea.addEventListener("input", update);
    textarea.addEventListener("scroll", () => {
        lineNumsEl.scrollTop = textarea.scrollTop;
    });

    update();
}

// ============================= KEYBOARD SHORTCUTS ====================
function initKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
        // ? to show shortcuts (only when not typing in textarea)
        if (e.key === "?" && document.activeElement.tagName !== "TEXTAREA") {
            e.preventDefault();
            openShortcutsModal();
        }

        // Ctrl+Enter to analyze
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            analyzeCode();
        }

        // Ctrl+E to toggle examples
        if ((e.ctrlKey || e.metaKey) && e.key === "e") {
            e.preventDefault();
            toggleExamples();
        }

        // Ctrl+H to open history
        if ((e.ctrlKey || e.metaKey) && e.key === "h") {
            e.preventDefault();
            openHistoryModal();
        }

        // Ctrl+D to toggle theme
        if ((e.ctrlKey || e.metaKey) && e.key === "d") {
            e.preventDefault();
            toggleTheme();
        }

        // Escape to close modals/drawers
        if (e.key === "Escape") {
            closeHistoryModal();
            closeShortcutsModal();
            closeExportMenu();
            const drawer = document.getElementById("examples-drawer");
            if (drawer.classList.contains("open")) toggleExamples();
        }
    });
}

// ============================= ANALYZE CODE ==========================
async function analyzeCode() {
    const code = document.getElementById("code").value.trim();
    const lang = document.getElementById("language-select").value;
    const btn = document.getElementById("analyze-btn");

    if (!code) {
        showToast("Please paste some code first", "error");
        return;
    }

    // Show loading state
    btn.disabled = true;
    btn.querySelector(".btn-text").style.display = "none";
    btn.querySelector(".btn-loader").style.display = "inline-flex";

    try {
        const payload = { code };
        if (lang !== "auto") payload.language = lang;

        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.error) {
            showToast(`Analysis error: ${data.error}`, "error");
            return;
        }

        lastAnalysisData = data;
        renderResults(data);
        saveToHistory(data, code);
        showToast("Analysis complete!", "success");

        // Show export + time
        document.getElementById("export-dropdown").style.display = "block";

        if (data.analysis_time_ms) {
            const timeEl = document.getElementById("analysis-time");
            timeEl.style.display = "inline-flex";
            document.getElementById("analysis-time-value").textContent = data.analysis_time_ms;
        }

        // Celebrate high scores
        if (data.quality_score >= 80) {
            setTimeout(() => launchConfetti(), 400);
        }

    } catch (error) {
        console.error(error);
        showToast("Could not connect to backend. Is it running?", "error");
    } finally {
        btn.disabled = false;
        btn.querySelector(".btn-text").style.display = "inline";
        btn.querySelector(".btn-loader").style.display = "none";
    }
}

// ============================= RENDER RESULTS ========================
function renderResults(data) {
    document.getElementById("empty-state").style.display = "none";
    document.getElementById("results").style.display = "block";

    // --- Language ---
    const langNames = { python: "Python", javascript: "JavaScript", java: "Java", c: "C", cpp: "C++" };
    document.getElementById("lang-value").textContent = langNames[data.language] || data.language;

    // --- AI Verdict ---
    const aiEl = document.getElementById("ai-value");
    aiEl.className = "meta-value";
    if (data.ai?.prediction === "Efficient") {
        aiEl.innerHTML = `<span class="badge badge-green">✓ Efficient</span>`;
    } else {
        aiEl.innerHTML = `<span class="badge badge-red">✗ Inefficient</span>`;
    }

    // --- Optimization Priority ---
    const prioEl = document.getElementById("priority-value");
    const prioText = data.ai?.optimization_priority ?? "N/A";
    const prioColors = { "Low": "badge-green", "Medium": "badge-amber", "High": "badge-red", "Very High": "badge-red" };
    prioEl.innerHTML = `<span class="badge ${prioColors[prioText] || 'badge-blue'}">${prioText}</span>`;

    // --- Complexity ---
    document.getElementById("time-value").textContent = data.analysis?.time_complexity ?? "—";
    document.getElementById("space-value").textContent = data.analysis?.space_complexity ?? "—";

    // --- Quality Score Gauge ---
    animateScore(data.quality_score ?? 0);

    // --- Code Metrics Dashboard ---
    renderMetrics(data.metrics);

    // --- Complexity Growth Chart ---
    drawComplexityChart(data.analysis?.time_complexity ?? "O(1)");

    // --- Patterns ---
    renderPatterns(data.patterns);

    // --- Explanations ---
    renderExplanations(data.explanation);

    // --- Suggestions ---
    renderSuggestions(data.suggestions);

    // --- Optimized Code ---
    renderOptimization(data.optimization);
}

// ============================= RENDER CODE METRICS ===================
function renderMetrics(metrics) {
    const section = document.getElementById("metrics-section");
    if (!metrics) {
        section.style.display = "none";
        return;
    }

    section.style.display = "block";

    // Cyclomatic Complexity
    const cc = metrics.cyclomatic_complexity ?? 1;
    document.getElementById("metric-cc").textContent = cc;
    const ccPercent = Math.min(cc / 20 * 100, 100);
    document.getElementById("metric-cc-bar").style.width = ccPercent + "%";
    let ccHint = "Simple";
    if (cc > 10) ccHint = "Complex";
    else if (cc > 5) ccHint = "Moderate";
    document.getElementById("metric-cc-hint").textContent = ccHint;

    // Maintainability Index
    const mi = metrics.maintainability_index ?? 50;
    document.getElementById("metric-mi").textContent = mi;
    document.getElementById("metric-mi-bar").style.width = mi + "%";
    let miHint = "Excellent";
    if (mi < 20) miHint = "Difficult to maintain";
    else if (mi < 50) miHint = "Moderate";
    else if (mi < 75) miHint = "Good";
    document.getElementById("metric-mi-hint").textContent = miHint;

    // Comment Ratio
    const cr = metrics.comment_ratio ?? 0;
    document.getElementById("metric-cr").textContent = cr + "%";
    document.getElementById("metric-cr-bar").style.width = Math.min(cr * 2, 100) + "%";
    let crHint = "Well documented";
    if (cr < 5) crHint = "Consider adding comments";
    else if (cr < 15) crHint = "Lightly documented";
    document.getElementById("metric-cr-hint").textContent = crHint;

    // Functions & line stats
    document.getElementById("metric-fn").textContent = metrics.function_count ?? 0;
    document.getElementById("metric-loc").textContent = (metrics.code_lines ?? 0) + " lines";
    document.getElementById("metric-blanks").textContent = (metrics.blank_lines ?? 0) + " blank";
    document.getElementById("metric-comments").textContent = (metrics.comment_lines ?? 0) + " comments";
}

// ============================= ANIMATE SCORE GAUGE ===================
function animateScore(score) {
    const fill = document.getElementById("score-ring-fill");
    const valueEl = document.getElementById("score-value");
    const offset = SCORE_CIRCUMFERENCE - (score / 100) * SCORE_CIRCUMFERENCE;

    let color;
    if (score >= 80) color = "#10b981";
    else if (score >= 60) color = "#3b82f6";
    else if (score >= 35) color = "#f59e0b";
    else color = "#ef4444";

    fill.style.stroke = color;
    fill.style.filter = `drop-shadow(0 0 10px ${color}60)`;

    fill.style.transition = "none";
    fill.style.strokeDashoffset = SCORE_CIRCUMFERENCE;

    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            fill.style.transition = "stroke-dashoffset 1.4s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.6s ease";
            fill.style.strokeDashoffset = offset;
        });
    });

    // Animate the number
    let current = 0;
    const duration = 1200;
    const start = performance.now();

    function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        current = Math.round(eased * score);
        valueEl.textContent = current;
        if (progress < 1) requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);
}

// ============================= COMPLEXITY GROWTH CHART ================
function drawComplexityChart(userComplexity) {
    const canvas = document.getElementById("complexity-chart");
    const ctx = canvas.getContext("2d");

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = 280 * dpr;
    canvas.style.height = "280px";
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = 280;
    const PAD = { top: 25, right: 20, bottom: 35, left: 50 };
    const plotW = W - PAD.left - PAD.right;
    const plotH = H - PAD.top - PAD.bottom;

    const complexities = [
        { label: "O(1)",      fn: () => 1,                           color: "#10b981" },
        { label: "O(log n)",  fn: (n) => Math.log2(Math.max(n, 1)),  color: "#3b82f6" },
        { label: "O(n)",      fn: (n) => n,                          color: "#6c63ff" },
        { label: "O(n log n)",fn: (n) => n * Math.log2(Math.max(n, 1)), color: "#a78bfa" },
        { label: "O(n²)",     fn: (n) => n * n,                      color: "#f59e0b" },
        { label: "O(2^n)",    fn: (n) => Math.pow(2, n),             color: "#ef4444" }
    ];

    function matchComplexity(str) {
        if (!str) return null;
        if (str.includes("2^n")) return "O(2^n)";
        if (str.includes("n^3") || str.includes("n^4")) return "O(n²)";
        if (str.includes("n^2")) return "O(n²)";
        if (str.includes("n log n")) return "O(n log n)";
        if (str.includes("O(n)") && !str.includes("log")) return "O(n)";
        if (str.includes("log")) return "O(log n)";
        if (str.includes("O(1)")) return "O(1)";
        return "O(n)";
    }

    const userLabel = matchComplexity(userComplexity);
    const maxN = 15;
    const STEPS = 80;

    let maxY = 0;
    complexities.forEach(c => {
        for (let i = 0; i <= STEPS; i++) {
            const n = (i / STEPS) * maxN;
            const y = Math.min(c.fn(n), 500);
            if (y > maxY) maxY = y;
        }
    });

    ctx.clearRect(0, 0, W, H);

    // Grid lines
    const isDark = document.documentElement.getAttribute("data-theme") !== "light";
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.06)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = PAD.top + (plotH / 4) * i;
        ctx.beginPath();
        ctx.moveTo(PAD.left, y);
        ctx.lineTo(W - PAD.right, y);
        ctx.stroke();
    }

    // Axes
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.1)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(PAD.left, PAD.top);
    ctx.lineTo(PAD.left, H - PAD.bottom);
    ctx.lineTo(W - PAD.right, H - PAD.bottom);
    ctx.stroke();

    // Labels
    ctx.fillStyle = isDark ? "rgba(255,255,255,0.3)" : "rgba(0,0,0,0.35)";
    ctx.font = "11px Inter, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Input Size (n)", W / 2, H - 6);

    ctx.save();
    ctx.translate(14, H / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("Operations", 0, 0);
    ctx.restore();

    // Draw curves
    complexities.forEach(c => {
        const isUser = c.label === userLabel;
        ctx.beginPath();
        ctx.strokeStyle = c.color;
        ctx.lineWidth = isUser ? 3 : 1.5;
        ctx.globalAlpha = isUser ? 1 : 0.3;

        if (isUser) {
            ctx.shadowColor = c.color;
            ctx.shadowBlur = 14;
        }

        for (let i = 0; i <= STEPS; i++) {
            const n = (i / STEPS) * maxN;
            const raw = Math.min(c.fn(n), maxY);
            const x = PAD.left + (n / maxN) * plotW;
            const y = PAD.top + plotH - (raw / maxY) * plotH;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }

        ctx.stroke();
        ctx.shadowColor = "transparent";
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;
    });

    // Legend
    const legendEl = document.getElementById("chart-legend");
    legendEl.innerHTML = "";
    complexities.forEach(c => {
        const isUser = c.label === userLabel;
        const item = document.createElement("div");
        item.className = "legend-item" + (isUser ? " active" : "");
        item.innerHTML = `
            <span class="legend-dot" style="background:${c.color};${isUser ? `box-shadow:0 0 8px ${c.color}` : ""}"></span>
            <span>${c.label}${isUser ? " ← Your Code" : ""}</span>
        `;
        legendEl.appendChild(item);
    });
}

// ============================= RENDER PATTERNS =======================
function renderPatterns(patterns) {
    const container = document.getElementById("patterns-container");
    container.innerHTML = "";

    if (!patterns || !patterns.length) {
        container.innerHTML = '<span class="pattern-pill success">✓ No patterns detected</span>';
        return;
    }

    const patternStyles = {
        "nested_loop":           { icon: "🔁", label: "Nested Loop",           cls: "danger" },
        "deep_nesting":          { icon: "🏗️", label: "Deep Nesting",          cls: "danger" },
        "inefficient_recursion": { icon: "⚠️", label: "Inefficient Recursion", cls: "danger" },
        "recursion":             { icon: "🔄", label: "Recursion",             cls: "warning" },
        "linear_recursion":      { icon: "↩️", label: "Linear Recursion",      cls: "info" },
        "recursion_stack":       { icon: "📚", label: "Stack Overhead",        cls: "warning" },
        "extra_memory":          { icon: "💾", label: "Extra Memory",          cls: "info" },
        "efficient_code":        { icon: "✅", label: "Efficient Code",        cls: "success" }
    };

    patterns.forEach(p => {
        const style = patternStyles[p] || { icon: "🔹", label: p.replaceAll("_", " "), cls: "purple" };
        const pill = document.createElement("span");
        pill.className = `pattern-pill ${style.cls}`;
        pill.textContent = `${style.icon} ${style.label}`;
        container.appendChild(pill);
    });
}

// ============================= RENDER EXPLANATIONS ===================
function renderExplanations(explanations) {
    const section = document.getElementById("explanation-section");
    const content = document.getElementById("explanation-content");

    if (!explanations || !explanations.length) {
        section.style.display = "none";
        return;
    }

    section.style.display = "block";
    content.innerHTML = "";

    explanations.forEach(text => {
        const div = document.createElement("div");
        div.className = "explanation-item";
        div.textContent = text;
        content.appendChild(div);
    });
}

// ============================= RENDER SUGGESTIONS ====================
function renderSuggestions(suggestions) {
    const section = document.getElementById("suggestions-section");
    const list = document.getElementById("suggestions-list");

    if (!suggestions || !suggestions.length) {
        section.style.display = "none";
        return;
    }

    section.style.display = "block";
    list.innerHTML = "";

    suggestions.forEach(s => {
        const li = document.createElement("li");
        li.textContent = s;
        list.appendChild(li);
    });
}

// ============================= RENDER OPTIMIZATION ===================
function renderOptimization(opt) {
    const section = document.getElementById("optimization-section");
    const meta = document.getElementById("opt-meta");
    const codeEl = document.getElementById("optimized-code");
    const descEl = document.getElementById("opt-description");

    if (!opt) {
        section.style.display = "none";
        return;
    }

    section.style.display = "block";

    // Description
    if (opt.description) {
        descEl.style.display = "block";
        descEl.textContent = opt.description;
    } else {
        descEl.style.display = "none";
    }

    // Meta tags
    meta.innerHTML = "";
    if (opt.issue) {
        const issueTag = document.createElement("span");
        issueTag.className = "opt-tag issue-tag";
        issueTag.textContent = opt.issue;
        meta.appendChild(issueTag);
    }
    if (opt.before_complexity) {
        const beforeTag = document.createElement("span");
        beforeTag.className = "opt-tag before";
        beforeTag.textContent = `Before: ${opt.before_complexity}`;
        meta.appendChild(beforeTag);
    }
    if (opt.after_complexity) {
        const afterTag = document.createElement("span");
        afterTag.className = "opt-tag after";
        afterTag.textContent = `After: ${opt.after_complexity}`;
        meta.appendChild(afterTag);
    }

    // Code
    const codeText = typeof opt === "string" ? opt : (opt.optimized_code ?? "No optimized code available");
    codeEl.textContent = codeText;
}

// ============================= COPY OPTIMIZED CODE ===================
function copyOptimizedCode() {
    const code = document.getElementById("optimized-code").textContent;
    navigator.clipboard.writeText(code).then(() => {
        const btn = document.getElementById("copy-btn");
        btn.textContent = "✅ Copied!";
        btn.classList.add("copied");
        setTimeout(() => {
            btn.textContent = "📋 Copy";
            btn.classList.remove("copied");
        }, 2000);
    }).catch(() => {
        showToast("Failed to copy to clipboard", "error");
    });
}

// ============================= EXPORT FUNCTIONS ======================
function toggleExportMenu() {
    const menu = document.getElementById("export-menu");
    menu.classList.toggle("open");
}

function closeExportMenu() {
    document.getElementById("export-menu").classList.remove("open");
}

// Close export menu when clicking outside
document.addEventListener("click", (e) => {
    const dropdown = document.getElementById("export-dropdown");
    if (dropdown && !dropdown.contains(e.target)) {
        closeExportMenu();
    }
});

function exportJSON() {
    if (!lastAnalysisData) {
        showToast("No analysis data to export", "error");
        return;
    }

    const blob = new Blob([JSON.stringify(lastAnalysisData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `code-analysis-${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    closeExportMenu();
    showToast("JSON exported successfully!", "success");
}

function exportReport() {
    if (!lastAnalysisData) {
        showToast("No analysis data to export", "error");
        return;
    }

    const d = lastAnalysisData;
    const langNames = { python: "Python", javascript: "JavaScript", java: "Java", c: "C", cpp: "C++" };
    const report = [
        `═══════════════════════════════════════`,
        `   AI CODE ANALYZER — ANALYSIS REPORT`,
        `═══════════════════════════════════════`,
        ``,
        `Language:        ${langNames[d.language] || d.language}`,
        `Quality Score:   ${d.quality_score}/100`,
        `AI Verdict:      ${d.ai?.prediction ?? "N/A"}`,
        `Opt. Priority:   ${d.ai?.optimization_priority ?? "N/A"}`,
        `Analysis Time:   ${d.analysis_time_ms ?? "N/A"}ms`,
        ``,
        `───── COMPLEXITY ─────`,
        `Time:  ${d.analysis?.time_complexity ?? "N/A"}`,
        `Space: ${d.analysis?.space_complexity ?? "N/A"}`,
        ``,
        `───── METRICS ─────`,
        `Cyclomatic Complexity:  ${d.metrics?.cyclomatic_complexity ?? "N/A"}`,
        `Maintainability Index:  ${d.metrics?.maintainability_index ?? "N/A"}`,
        `Comment Ratio:          ${d.metrics?.comment_ratio ?? "N/A"}%`,
        `Functions Found:        ${d.metrics?.function_count ?? "N/A"}`,
        `Code Lines:             ${d.metrics?.code_lines ?? "N/A"}`,
        ``,
        `───── PATTERNS ─────`,
        ...(d.patterns?.map(p => `  • ${p.replace(/_/g, " ")}`) ?? ["  None"]),
        ``,
        `───── SUGGESTIONS ─────`,
        ...(d.suggestions?.map((s, i) => `  ${i+1}. ${s}`) ?? ["  None"]),
        ``,
        `═══════════════════════════════════════`,
        `Generated: ${new Date().toLocaleString()}`,
    ].join("\n");

    navigator.clipboard.writeText(report).then(() => {
        closeExportMenu();
        showToast("Report copied to clipboard!", "success");
    }).catch(() => {
        showToast("Failed to copy report", "error");
    });
}

// ============================= TOAST NOTIFICATIONS ===================
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    const icons = { success: "✅", error: "❌", info: "ℹ️" };
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || "ℹ️"}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("toast-exit");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ============================= CONFETTI CELEBRATION ==================
function launchConfetti() {
    const canvas = document.getElementById("confetti");
    const ctx = canvas.getContext("2d");

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const colors = ["#6c63ff", "#a855f7", "#10b981", "#f59e0b", "#3b82f6", "#ef4444", "#a78bfa", "#22d3ee"];
    const particles = [];

    for (let i = 0; i < 120; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * -canvas.height * 0.5,
            w: Math.random() * 8 + 4,
            h: Math.random() * 6 + 3,
            color: colors[Math.floor(Math.random() * colors.length)],
            vx: (Math.random() - 0.5) * 3.5,
            vy: Math.random() * 4 + 2,
            rotation: Math.random() * 360,
            rotationSpeed: (Math.random() - 0.5) * 10,
            opacity: 1
        });
    }

    let startTime = performance.now();

    function draw(now) {
        const elapsed = now - startTime;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        let alive = false;

        particles.forEach(p => {
            if (p.opacity <= 0) return;
            alive = true;

            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate((p.rotation * Math.PI) / 180);
            ctx.globalAlpha = p.opacity;
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
            ctx.restore();

            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.08;
            p.rotation += p.rotationSpeed;

            if (elapsed > 2000) {
                p.opacity -= 0.02;
            }
        });

        if (alive) {
            requestAnimationFrame(draw);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    requestAnimationFrame(draw);
}

// ============================= EXAMPLES DRAWER =======================
function toggleExamples() {
    const drawer = document.getElementById("examples-drawer");
    const backdrop = document.getElementById("drawer-backdrop");
    drawer.classList.toggle("open");
    backdrop.classList.toggle("active");
}

function initExampleTabs() {
    const tabs = document.querySelectorAll("#example-tabs button");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            renderExamples(tab.dataset.lang);
        });
    });
}

function renderExamples(lang) {
    const list = document.getElementById("example-list");
    const examples = CODE_EXAMPLES[lang] || [];
    list.innerHTML = "";

    examples.forEach(ex => {
        const item = document.createElement("div");
        item.className = "example-item";

        const diffColors = {
            danger: `background:var(--red-bg);color:var(--red)`,
            warning: `background:var(--amber-bg);color:var(--amber)`,
            info: `background:var(--blue-bg);color:var(--blue)`,
            success: `background:var(--green-bg);color:var(--green)`
        };
        const diffLabels = { danger: "Hard", warning: "Medium", info: "Easy", success: "Optimal" };

        item.innerHTML = `
            <div class="example-item-title">${ex.title}</div>
            <div class="example-item-desc">${ex.desc}</div>
            <span class="example-item-badge" style="${diffColors[ex.difficulty] || ''}">${diffLabels[ex.difficulty] || ex.difficulty}</span>
        `;
        item.addEventListener("click", () => {
            document.getElementById("code").value = ex.code;
            document.getElementById("code").dispatchEvent(new Event("input"));
            document.getElementById("language-select").value = lang;
            toggleExamples();
            showToast(`Loaded: ${ex.title}`, "info");
        });
        list.appendChild(item);
    });
}

// ============================= ANALYSIS HISTORY ======================
function saveToHistory(data, code) {
    let history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");

    history.unshift({
        timestamp: new Date().toISOString(),
        language: data.language,
        score: data.quality_score,
        timeComplexity: data.analysis?.time_complexity,
        codeSnippet: code.substring(0, 100),
        prediction: data.ai?.prediction
    });

    if (history.length > 30) history = history.slice(0, 30);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function openHistoryModal() {
    const modal = document.getElementById("history-modal");
    modal.classList.add("open");
    renderHistory();
}

function closeHistoryModal() {
    document.getElementById("history-modal").classList.remove("open");
}

function openShortcutsModal() {
    document.getElementById("shortcuts-modal").classList.add("open");
}

function closeShortcutsModal() {
    document.getElementById("shortcuts-modal").classList.remove("open");
}

function renderHistory() {
    const list = document.getElementById("history-list");
    const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");

    if (!history.length) {
        list.innerHTML = '<p class="empty-history">No analysis history yet</p>';
        return;
    }

    list.innerHTML = "";

    history.forEach(item => {
        const div = document.createElement("div");
        div.className = "history-item";

        const date = new Date(item.timestamp);
        const timeStr = date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

        let scoreColor = "#ef4444";
        if (item.score >= 80) scoreColor = "#10b981";
        else if (item.score >= 60) scoreColor = "#3b82f6";
        else if (item.score >= 35) scoreColor = "#f59e0b";

        div.innerHTML = `
            <div>
                <div class="history-lang">${item.language ?? "?"} — ${item.timeComplexity ?? "?"}</div>
                <div class="history-time">${timeStr}</div>
            </div>
            <div class="history-score" style="color:${scoreColor}">${item.score ?? "?"}/100</div>
        `;

        list.appendChild(div);
    });
}

function clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
    renderHistory();
    showToast("History cleared", "info");
}

// ============================= WINDOW RESIZE HANDLER =================
window.addEventListener("resize", () => {
    const resultsEl = document.getElementById("results");
    if (resultsEl && resultsEl.style.display !== "none") {
        const timeVal = document.getElementById("time-value").textContent;
        if (timeVal && timeVal !== "—") {
            drawComplexityChart(timeVal);
        }
    }
});