from .dsa_part1 import _p

DSA_PART4 = [
    # --- 12. 1D DYNAMIC PROGRAMMING (16) ---
    _p(155, "Climbing Stairs", "1D Dynamic Programming", "Easy", ["Amazon", "Paytm"], "climbing-stairs",
       "Fibonacci Recurrence: dp[i] = dp[i-1] + dp[i-2] because you can only arrive at i from i-1 or i-2!",
       "Space-optimize down to two variables (a, b).",
       "Time: O(N), Space: O(1)",
       """def climbStairs(n):
    a, b = 1, 1
    for _ in range(n - 1): a, b = b, a + b
    return b""",
       """int climbStairs(int n) {
    int a = 1, b = 1;
    while (--n) { int c = a + b; a = b; b = c; }
    return b;
}"""),

    _p(156, "Min Cost Climbing Stairs", "1D Dynamic Programming", "Easy", ["Microsoft", "Swiggy"], "min-cost-climbing-stairs",
       "dp[i] = cost[i] + min(dp[i-1], dp[i-2]); final answer is min(last two) since you can step past the end from either!",
       "Bottom-up O(1) space DP.",
       "Time: O(N), Space: O(1)",
       """def minCostClimbingStairs(cost):
    a, b = 0, 0
    for c in cost: a, b = b, c + min(a, b)
    return min(a, b)""",
       """int minCostClimbingStairs(vector<int>& cost) {
    int a = 0, b = 0;
    for (int c : cost) { int nxt = c + min(a, b); a = b; b = nxt; }
    return min(a, b);
}"""),

    _p(157, "House Robber", "1D Dynamic Programming", "Medium", ["Razorpay", "Amazon", "CRED"], "house-robber",
       "At house i: pick max(rob_current + prev2, skip_current == prev1)!",
       "Classic non-adjacent maximum sum DP in O(1) space.",
       "Time: O(N), Space: O(1)",
       """def rob(nums):
    prev2 = prev1 = 0
    for x in nums: prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1""",
       """int rob(vector<int>& nums) {
    int p2 = 0, p1 = 0;
    for (int x : nums) { int cur = max(p1, p2 + x); p2 = p1; p1 = cur; }
    return p1;
}"""),

    _p(158, "House Robber II (Circular)", "1D Dynamic Programming", "Medium", ["Google", "Flipkart"], "house-robber-ii",
       "Circular Break Trick: you CANNOT rob both first and last house -> answer = max(rob(nums[:-1]), rob(nums[1:]))!",
       "Handles len == 1 edge case upfront.",
       "Time: O(N), Space: O(1)",
       """def robII(nums):
    if len(nums) == 1: return nums[0]
    def line(arr):
        p2 = p1 = 0
        for x in arr: p2, p1 = p1, max(p1, p2 + x)
        return p1
    return max(line(nums[:-1]), line(nums[1:]))""",
       """int rob(vector<int>& nums) {
    if (nums.size() == 1) return nums[0];
    auto line = [&](int l, int r) {
        int p2 = 0, p1 = 0;
        for (int i = l; i <= r; ++i) { int c = max(p1, p2 + nums[i]); p2 = p1; p1 = c; }
        return p1;
    };
    return max(line(0, nums.size() - 2), line(1, nums.size() - 1));
}"""),

    _p(159, "Longest Palindromic Substring", "1D Dynamic Programming", "Medium", ["Amazon", "Microsoft", "Zepto"], "longest-palindromic-substring",
       "Expand Around Center: test every index as BOTH odd center (i, i) and even center (i, i+1) in O(1) space!",
       "Much simpler and lower memory than O(N^2) DP table.",
       "Time: O(N^2), Space: O(1)",
       """def longestPalindrome(s):
    res = ""
    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]: l -= 1; r += 1
        return s[l+1:r]
    for i in range(len(s)):
        res = max(res, expand(i, i), expand(i, i + 1), key=len)
    return res""",
       """string longestPalindrome(string s) {
    int st = 0, best = 0;
    auto exp = [&](int l, int r) {
        while (l >= 0 && r < s.size() && s[l] == s[r]) { l--; r++; }
        if (r - l - 1 > best) { best = r - l - 1; st = l + 1; }
    };
    for (int i = 0; i < s.size(); ++i) { exp(i, i); exp(i, i + 1); }
    return s.substr(st, best);
}"""),

    _p(160, "Palindromic Substrings (Count)", "1D Dynamic Programming", "Medium", ["Meta", "Flipkart"], "palindromic-substrings",
       "Expand Around Center counting each successful match `ans += 1` across (i, i) and (i, i+1).",
       "Clean O(N^2) time and O(1) space.",
       "Time: O(N^2), Space: O(1)",
       """def countSubstrings(s):
    def exp(l, r):
        cnt = 0
        while l >= 0 and r < len(s) and s[l] == s[r]: cnt += 1; l -= 1; r += 1
        return cnt
    return sum(exp(i, i) + exp(i, i + 1) for i in range(len(s)))""",
       """int countSubstrings(string s) {
    int ans = 0;
    auto exp = [&](int l, int r) { while (l >= 0 && r < s.size() && s[l--] == s[r++]) ans++; };
    for (int i = 0; i < s.size(); ++i) { exp(i, i); exp(i, i + 1); }
    return ans;
}"""),

    _p(161, "Decode Ways", "1D Dynamic Programming", "Medium", ["Uber", "Amazon"], "decode-ways",
       "State dp[i] = ways to decode suffix s[i:]: if s[i] == '0' -> 0 ways; else add dp[i+1] + (dp[i+2] if 10 <= int(s[i:i+2]) <= 26).",
       "Space-optimize from right to left using two vars.",
       "Time: O(N), Space: O(1)",
       """def numDecodings(s):
    nxt, nxt2 = 1, 0
    for i in range(len(s) - 1, -1, -1):
        cur = 0 if s[i] == '0' else nxt
        if i + 1 < len(s) and (s[i] == '1' or (s[i] == '2' and s[i+1] in '0123456')):
            cur += nxt2
        nxt, nxt2 = cur, nxt
    return nxt""",
       """int numDecodings(string s) {
    int n = s.size(), nxt = 1, nxt2 = 0;
    for (int i = n - 1; i >= 0; --i) {
        int cur = (s[i] == '0') ? 0 : nxt;
        if (i + 1 < n && (s[i] == '1' || (s[i] == '2' && s[i+1] <= '6'))) cur += nxt2;
        nxt2 = nxt; nxt = cur;
    }
    return nxt;
}"""),

    _p(162, "Coin Change", "1D Dynamic Programming", "Medium", ["Razorpay", "Zepto", "Amazon"], "coin-change",
       "Unbounded Knapsack Bottom-Up: `dp[a] = min(dp[a], 1 + dp[a - coin])` for all coins <= a.",
       "Initialize dp = [amount+1] * (amount+1) with dp[0] = 0.",
       "Time: O(Amount * Coins), Space: O(Amount)",
       """def coinChange(coins, amount):
    dp = [amount + 1] * (amount + 1); dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a: dp[a] = min(dp[a], 1 + dp[a - c])
    return dp[amount] if dp[amount] <= amount else -1""",
       """int coinChange(vector<int>& coins, int amount) {
    vector<int> dp(amount + 1, amount + 1); dp[0] = 0;
    for (int a = 1; a <= amount; ++a)
        for (int c : coins) if (c <= a) dp[a] = min(dp[a], 1 + dp[a - c]);
    return dp[amount] > amount ? -1 : dp[amount];
}"""),

    _p(163, "Maximum Product Subarray", "1D Dynamic Programming", "Medium", ["LinkedIn", "Amazon", "CRED"], "maximum-product-subarray",
       "Negative * Negative = Positive! Track BOTH `curMax` and `curMin` at every element (or handle zero by resetting!).",
       "Update curMax, curMin simultaneously from candidates (x, x*curMax, x*curMin).",
       "Time: O(N), Space: O(1)",
       """def maxProduct(nums):
    curMax = curMin = ans = nums[0]
    for x in nums[1:]:
        vals = (x, x * curMax, x * curMin)
        curMax, curMin = max(vals), min(vals)
        ans = max(ans, curMax)
    return ans""",
       """int maxProduct(vector<int>& nums) {
    int mx = nums[0], mn = nums[0], ans = nums[0];
    for (int i = 1; i < nums.size(); ++i) {
        int x = nums[i];
        if (x < 0) swap(mx, mn);
        mx = max(x, mx * x); mn = min(x, mn * x);
        ans = max(ans, mx);
    }
    return ans;
}"""),

    _p(164, "Word Break", "1D Dynamic Programming", "Medium", ["Swiggy", "Amazon", "Meta"], "word-break",
       "dp[i] = True if suffix s[i:] is segmentable! For each matched word w in dict, dp[i] |= dp[i + len(w)].",
       "Iterate i backwards from n-1 to 0 with dp[n] = True.",
       "Time: O(N * M * L), Space: O(N)",
       """def wordBreak(s, wordDict):
    n = len(s); dp = [False]*(n+1); dp[n] = True
    for i in range(n - 1, -1, -1):
        for w in wordDict:
            if i + len(w) <= n and s[i:i+len(w)] == w and dp[i+len(w)]:
                dp[i] = True; break
    return dp[0]""",
       """bool wordBreak(string s, vector<string>& dict) {
    int n = s.size(); vector<bool> dp(n + 1, false); dp[n] = true;
    for (int i = n - 1; i >= 0; --i)
        for (auto& w : dict)
            if (i + w.size() <= n && s.compare(i, w.size(), w) == 0 && dp[i + w.size()]) {
                dp[i] = true; break;
            }
    return dp[0];
}"""),

    _p(165, "Longest Increasing Subsequence (LIS)", "1D Dynamic Programming", "Medium", ["Google", "Flipkart", "Atlassian"], "longest-increasing-subsequence",
       "Patience Sorting + Binary Search (O(N log N)): maintain `tails` array; replace first element >= x via bisect_left, or append x!",
       "Length of `tails` equals exact LIS length (though elements aren't always the subsequence itself).",
       "Time: O(N log N), Space: O(N)",
       """import bisect
def lengthOfLIS(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails): tails.append(x)
        else: tails[i] = x
    return len(tails)""",
       """int lengthOfLIS(vector<int>& nums) {
    vector<int> tails;
    for (int x : nums) {
        auto it = lower_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) tails.push_back(x);
        else *it = x;
    }
    return tails.size();
}"""),

    _p(166, "Partition Equal Subset Sum", "1D Dynamic Programming", "Medium", ["Amazon", "Paytm", "Uber"], "partition-equal-subset-sum",
       "0/1 Knapsack Subset Sum for target = sum // 2! Note: if total is odd return False immediately; iterate sum BACKWARDS in 1D DP!",
       "Iterating target down to x prevents reusing the same element multiple times.",
       "Time: O(N * Target), Space: O(Target)",
       """def canPartition(nums):
    s = sum(nums)
    if s % 2: return False
    T = s // 2; dp = [False]*(T+1); dp[0] = True
    for x in nums:
        for t in range(T, x - 1, -1): dp[t] = dp[t] or dp[t - x]
    return dp[T]""",
       """bool canPartition(vector<int>& nums) {
    int s = accumulate(nums.begin(), nums.end(), 0);
    if (s % 2) return false;
    int T = s / 2; vector<bool> dp(T + 1, false); dp[0] = true;
    for (int x : nums)
        for (int t = T; t >= x; --t) dp[t] = dp[t] || dp[t - x];
    return dp[T];
}"""),

    _p(167, "Perfect Squares", "1D Dynamic Programming", "Medium", ["Google", "Microsoft"], "perfect-squares",
       "Unbounded coin change where coins = [1, 4, 9, 16, ..., <= n]! Bottom-up dp[i] = 1 + min(dp[i - sq]).",
       "Or BFS from n subtracting squares to find shortest steps.",
       "Time: O(N * sqrt(N)), Space: O(N)",
       """def numSquares(n):
    dp = list(range(n + 1))
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            dp[i] = min(dp[i], 1 + dp[i - j*j]); j += 1
    return dp[n]""",
       """int numSquares(int n) {
    vector<int> dp(n + 1, INT_MAX); dp[0] = 0;
    for (int i = 1; i <= n; ++i)
        for (int j = 1; j * j <= i; ++j) dp[i] = min(dp[i], 1 + dp[i - j * j]);
    return dp[n];
}"""),

    _p(168, "Jump Game II (Min Jumps DP/Greedy)", "1D Dynamic Programming", "Medium", ["Flipkart", "Amazon"], "jump-game-ii",
       "BFS-style Greedy Window: maintain current reachable boundary `end` and `farthest`; when i hits `end`, increment jumps and set end = farthest!",
       "Linear O(N) time and O(1) space instead of O(N^2) DP.",
       "Time: O(N), Space: O(1)",
       """def jump(nums):
    jumps = cur_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end: jumps += 1; cur_end = farthest
    return jumps""",
       """int jump(vector<int>& nums) {
    int jumps = 0, end = 0, far = 0;
    for (int i = 0; i + 1 < nums.size(); ++i) {
        far = max(far, i + nums[i]);
        if (i == end) { jumps++; end = far; }
    }
    return jumps;
}"""),

    _p(169, "Combination Sum IV (Order Matters)", "1D Dynamic Programming", "Medium", ["Google", "Meta"], "combination-sum-iv",
       "Loop Order Trick! When order matters (permutations), put `for target in 1..T:` on the OUTSIDE and `for num in nums:` on the INSIDE!",
       "Contrasts with Coin Change II where coins loop goes outside.",
       "Time: O(T * N), Space: O(T)",
       """def combinationSum4(nums, target):
    dp = [0] * (target + 1); dp[0] = 1
    for t in range(1, target + 1):
        for x in nums:
            if t >= x: dp[t] += dp[t - x]
    return dp[target]""",
       """int combinationSum4(vector<int>& nums, int target) {
    vector<unsigned long long> dp(target + 1, 0); dp[0] = 1;
    for (int t = 1; t <= target; ++t)
        for (int x : nums) if (t >= x) dp[t] += dp[t - x];
    return dp[target];
}"""),

    _p(170, "Triangle (Min Path Sum Top-Down)", "1D Dynamic Programming", "Medium", ["Amazon", "Apple"], "triangle",
       "Roll UP from bottom row `n-2` up to row 0: `dp[c] = triangle[r][c] + min(dp[c], dp[c+1])` in 1D array!",
       "Avoids boundary checking since row below always has 1 extra element.",
       "Time: O(R^2), Space: O(R)",
       """def minimumTotal(tri):
    dp = tri[-1][:]
    for r in range(len(tri) - 2, -1, -1):
        for c in range(len(tri[r])):
            dp[c] = tri[r][c] + min(dp[c], dp[c + 1])
    return dp[0]""",
       """int minimumTotal(vector<vector<int>>& tri) {
    vector<int> dp = tri.back();
    for (int r = tri.size() - 2; r >= 0; --r)
        for (int c = 0; c < tri[r].size(); ++c) dp[c] = tri[r][c] + min(dp[c], dp[c+1]);
    return dp[0];
}"""),

    # --- 13. 2D DYNAMIC PROGRAMMING (14) ---
    _p(171, "Unique Paths", "2D Dynamic Programming", "Medium", ["Amazon", "Google"], "unique-paths",
       "1D row rolling DP: `dp[c] += dp[c - 1]` initialized to all 1s!",
       "Moves down + right only, so previous row value is already in dp[c].",
       "Time: O(M*N), Space: O(N)",
       """def uniquePaths(m, n):
    dp = [1] * n
    for _ in range(m - 1):
        for c in range(1, n): dp[c] += dp[c - 1]
    return dp[-1]""",
       """int uniquePaths(int m, int n) {
    vector<int> dp(n, 1);
    while (--m) for (int c = 1; c < n; ++c) dp[c] += dp[c - 1];
    return dp.back();
}"""),

    _p(172, "Longest Common Subsequence (LCS)", "2D Dynamic Programming", "Medium", ["Razorpay", "Amazon", "Flipkart"], "longest-common-subsequence",
       "If t1[i] == t2[j]: `1 + dp[i+1][j+1]`; else `max(dp[i+1][j], dp[i][j+1])`!",
       "Foundation for Edit Distance, Diff tools, and Shortest Common Supersequence.",
       "Time: O(M*N), Space: O(min(M,N))",
       """def longestCommonSubsequence(s1, s2):
    m, n = len(s1), len(s2)
    dp = [0] * (n + 1)
    for i in range(m - 1, -1, -1):
        nxt = [0] * (n + 1)
        for j in range(n - 1, -1, -1):
            nxt[j] = 1 + dp[j+1] if s1[i] == s2[j] else max(dp[j], nxt[j+1])
        dp = nxt
    return dp[0]""",
       """int longestCommonSubsequence(string s1, string s2) {
    int m = s1.size(), n = s2.size();
    vector<int> dp(n + 1, 0);
    for (int i = m - 1; i >= 0; --i) {
        vector<int> nxt(n + 1, 0);
        for (int j = n - 1; j >= 0; --j)
            nxt[j] = (s1[i] == s2[j]) ? 1 + dp[j+1] : max(dp[j], nxt[j+1]);
        dp = move(nxt);
    }
    return dp[0];
}"""),

    _p(173, "Best Time to Buy/Sell Stock with Cooldown", "2D Dynamic Programming", "Medium", ["Google", "Amazon"], "best-time-to-buy-and-sell-stock-with-cooldown",
       "Finite State Machine DP (3 states): `hold`, `sold` (cooldown next), `rest` (can buy)! Transitions update cleanly each day.",
       "Eliminates complex O(N^2) lookbacks.",
       "Time: O(N), Space: O(1)",
       """def maxProfitCooldown(prices):
    hold, sold, rest = float('-inf'), 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)""",
       """int maxProfit(vector<int>& prices) {
    int hold = INT_MIN, sold = 0, rest = 0;
    for (int p : prices) {
        int ph = hold, ps = sold;
        hold = max(hold, rest - p); sold = ph + p; rest = max(rest, ps);
    }
    return max(sold, rest);
}"""),

    _p(174, "Coin Change II (Number of Combinations)", "2D Dynamic Programming", "Medium", ["Amazon", "Swiggy"], "coin-change-ii",
       "Loop Order Matters! Put `for coin in coins:` OUTSIDE and `for a in coin..amount:` INSIDE so combinations (not permutations) are counted!",
       "1D rolling array dp[a] += dp[a - coin].",
       "Time: O(Coins * Amount), Space: O(Amount)",
       """def change(amount, coins):
    dp = [0] * (amount + 1); dp[0] = 1
    for c in coins:
        for a in range(c, amount + 1): dp[a] += dp[a - c]
    return dp[amount]""",
       """int change(int amount, vector<int>& coins) {
    vector<unsigned long long> dp(amount + 1, 0); dp[0] = 1;
    for (int c : coins)
        for (int a = c; a <= amount; ++a) dp[a] += dp[a - c];
    return dp[amount];
}"""),

    _p(175, "Target Sum", "2D Dynamic Programming", "Medium", ["Meta", "Amazon"], "target-sum",
       "Math Reduction! Assigning +/- splits array into P - N = target and P + N = total -> P = (total + target) // 2! Exact Subset Sum DP!",
       "Reduces +/- branching into classic 0/1 knapsack count.",
       "Time: O(N * P), Space: O(P)",
       """def findTargetSumWays(nums, target):
    tot = sum(nums)
    if (tot + target) % 2 or abs(target) > tot: return 0
    P = (tot + target) // 2; dp = [0]*(P+1); dp[0] = 1
    for x in nums:
        for s in range(P, x - 1, -1): dp[s] += dp[s - x]
    return dp[P]""",
       """int findTargetSumWays(vector<int>& nums, int target) {
    int tot = accumulate(nums.begin(), nums.end(), 0);
    if ((tot + target) % 2 || abs(target) > tot) return 0;
    int P = (tot + target) / 2; vector<int> dp(P + 1, 0); dp[0] = 1;
    for (int x : nums) for (int s = P; s >= x; --s) dp[s] += dp[s - x];
    return dp[P];
}"""),

    _p(176, "Interleaving String", "2D Dynamic Programming", "Medium", ["Google", "Microsoft"], "interleaving-string",
       "dp[i][j] = can s1[i:] and s2[j:] form s3[i+j:]! Check s1[i] == s3[i+j] and dp[i+1][j] OR s2[j] == s3[i+j] and dp[i][j+1].",
       "Quick guard: return False immediately if len(s1) + len(s2) != len(s3).",
       "Time: O(M*N), Space: O(N)",
       """def isInterleave(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3): return False
    dp = [False]*(n+1); dp[n] = True
    for i in range(m, -1, -1):
        for j in range(n, -1, -1):
            if i == m and j == n: continue
            ok = False
            if i < m and s1[i] == s3[i+j] and dp[j]: ok = True
            if j < n and s2[j] == s3[i+j] and dp[j+1]: ok = True
            dp[j] = ok
    return dp[0]""",
       """bool isInterleave(string s1, string s2, string s3) {
    int m = s1.size(), n = s2.size(); if (m + n != s3.size()) return false;
    vector<bool> dp(n + 1, false); dp[n] = true;
    for (int i = m; i >= 0; --i) for (int j = n; j >= 0; --j) {
        if (i == m && j == n) continue;
        bool ok = (i < m && s1[i] == s3[i+j] && dp[j]) || (j < n && s2[j] == s3[i+j] && dp[j+1]);
        dp[j] = ok;
    }
    return dp[0];
}"""),

    _p(177, "Longest Increasing Path in a Matrix", "2D Dynamic Programming", "Hard", ["Google", "Uber", "Razorpay"], "longest-increasing-path-in-a-matrix",
       "Strict inequality guarantees NO cycles (it's a DAG)! Simple DFS + Memoization grid computes max path per cell in O(R * C)!",
       "No visited set needed because values strictly increase.",
       "Time: O(R*C), Space: O(R*C)",
       """def longestIncreasingPath(mat):
    R, C = len(mat), len(mat[0]); memo = {}
    def dfs(r, c):
        if (r, c) in memo: return memo[(r, c)]
        best = 1
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0<=nr<R and 0<=nc<C and mat[nr][nc] > mat[r][c]:
                best = max(best, 1 + dfs(nr, nc))
        memo[(r, c)] = best; return best
    return max(dfs(r, c) for r in range(R) for c in range(C))""",
       """int longestIncreasingPath(vector<vector<int>>& m) {
    int R = m.size(), C = m[0].size(), ans = 0, d[5]={1,0,-1,0,1};
    vector<vector<int>> memo(R, vector<int>(C, 0));
    function<int(int,int)> dfs = [&](int r, int c) {
        if (memo[r][c]) return memo[r][c];
        int b = 1;
        for (int k = 0; k < 4; ++k) {
            int nr = r+d[k], nc = c+d[k+1];
            if (nr>=0 && nr<R && nc>=0 && nc<C && m[nr][nc] > m[r][c]) b = max(b, 1 + dfs(nr, nc));
        }
        return memo[r][c] = b;
    };
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) ans = max(ans, dfs(r, c));
    return ans;
}"""),

    _p(178, "Distinct Subsequences", "2D Dynamic Programming", "Hard", ["Google", "Amazon"], "distinct-subsequences",
       "When s[i] == t[j]: sum BOTH choices: match char (`dp[i+1][j+1]`) + skip s[i] (`dp[i+1][j]`); else only skip (`dp[i+1][j]`)!",
       "1D rolling array updated backwards j = n-1..0.",
       "Time: O(M*N), Space: O(N)",
       """def numDistinct(s, t):
    m, n = len(s), len(t); dp = [0]*(n+1); dp[n] = 1
    for i in range(m - 1, -1, -1):
        for j in range(n):
            if s[i] == t[j]: dp[j] += dp[j + 1]
    return dp[0]""",
       """int numDistinct(string s, string t) {
    int m = s.size(), n = t.size(); vector<unsigned long long> dp(n + 1, 0); dp[n] = 1;
    for (int i = m - 1; i >= 0; --i)
        for (int j = 0; j < n; ++j) if (s[i] == t[j]) dp[j] += dp[j + 1];
    return dp[0];
}"""),

    _p(179, "Edit Distance (Levenshtein)", "2D Dynamic Programming", "Medium", ["Atlassian", "Amazon", "Zepto"], "edit-distance",
       "If w1[i] == w2[j]: `dp[i+1][j+1]`; else `1 + min(insert: dp[i][j+1], delete: dp[i+1][j], replace: dp[i+1][j+1])`!",
       "Base cases: last row = remaining chars in w2, last col = remaining in w1.",
       "Time: O(M*N), Space: O(M*N)",
       """def minDistance(w1, w2):
    m, n = len(w1), len(w2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][n] = m - i
    for j in range(n+1): dp[m][j] = n - j
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if w1[i] == w2[j]: dp[i][j] = dp[i+1][j+1]
            else: dp[i][j] = 1 + min(dp[i+1][j], dp[i][j+1], dp[i+1][j+1])
    return dp[0][0]""",
       """int minDistance(string w1, string w2) {
    int m = w1.size(), n = w2.size();
    vector<vector<int>> dp(m + 1, vector<int>(n + 1, 0));
    for (int i = 0; i <= m; ++i) dp[i][n] = m - i;
    for (int j = 0; j <= n; ++j) dp[m][j] = n - j;
    for (int i = m - 1; i >= 0; --i) for (int j = n - 1; j >= 0; --j) {
        if (w1[i] == w2[j]) dp[i][j] = dp[i+1][j+1];
        else dp[i][j] = 1 + min({dp[i+1][j], dp[i][j+1], dp[i+1][j+1]});
    }
    return dp[0][0];
}"""),

    _p(180, "Burst Balloons (Interval DP)", "2D Dynamic Programming", "Hard", ["Google", "CRED"], "burst-balloons",
       "Think LAST balloon to pop, NOT first! Pad array with [1] + nums + [1]; if k is popped LAST in (l, r), neighbors are nums[l-1] and nums[r+1] cleanly!",
       "Splits (l, r) into completely independent subproblems (l, k-1) and (k+1, r).",
       "Time: O(N^3), Space: O(N^2)",
       """def maxCoins(nums):
    a = [1] + nums + [1]; n = len(a)
    dp = [[0]*n for _ in range(n)]
    for length in range(2, n):
        for l in range(0, n - length):
            r = l + length
            for k in range(l + 1, r):
                dp[l][r] = max(dp[l][r], a[l]*a[k]*a[r] + dp[l][k] + dp[k][r])
    return dp[0][n - 1]""",
       """int maxCoins(vector<int>& nums) {
    vector<int> a = {1}; for (int x : nums) a.push_back(x); a.push_back(1);
    int n = a.size(); vector<vector<int>> dp(n, vector<int>(n, 0));
    for (int len = 2; len < n; ++len)
        for (int l = 0; l + len < n; ++l) {
            int r = l + len;
            for (int k = l + 1; k < r; ++k)
                dp[l][r] = max(dp[l][r], a[l]*a[k]*a[r] + dp[l][k] + dp[k][r]);
        }
    return dp[0][n - 1];
}"""),

    _p(181, "Regular Expression Matching", "2D Dynamic Programming", "Hard", ["Meta", "Google", "Uber"], "regular-expression-matching",
       "When p[j+1] == '*': two choices — skip `x*` completely (`dfs(i, j+2)`) OR consume 1 char if first chars match (`match and dfs(i+1, j)`)!",
       "Memoize (i, j) pairs in O(M * N).",
       "Time: O(M*N), Space: O(M*N)",
       """from functools import lru_cache
def isMatch(s, p):
    @lru_cache(None)
    def dfs(i, j):
        if j == len(p): return i == len(s)
        match = i < len(s) and p[j] in (s[i], '.')
        if j + 1 < len(p) and p[j + 1] == '*':
            return dfs(i, j + 2) or (match and dfs(i + 1, j))
        return match and dfs(i + 1, j + 1)
    return dfs(0, 0)""",
       """bool isMatch(string s, string p) {
    int m = s.size(), n = p.size();
    vector<vector<int>> dp(m + 1, vector<int>(n + 1, 0)); dp[m][n] = 1;
    for (int i = m; i >= 0; --i) for (int j = n - 1; j >= 0; --j) {
        bool match = (i < m && (p[j] == s[i] || p[j] == '.'));
        if (j + 1 < n && p[j+1] == '*') dp[i][j] = dp[i][j+2] || (match && dp[i+1][j]);
        else dp[i][j] = match && dp[i+1][j+1];
    }
    return dp[0][0];
}"""),

    _p(182, "Minimum Path Sum", "2D Dynamic Programming", "Medium", ["Swiggy", "Amazon"], "minimum-path-sum",
       "1D row DP: `dp[c] = grid[r][c] + min(dp[c], dp[c-1])` handling row 0 and col 0 cleanly.",
       "Modifies 1D dp array in-place.",
       "Time: O(R*C), Space: O(C)",
       """def minPathSum(grid):
    R, C = len(grid), len(grid[0]); dp = [float('inf')] * C; dp[0] = 0
    for r in range(R):
        dp[0] += grid[r][0]
        for c in range(1, C): dp[c] = grid[r][c] + min(dp[c], dp[c - 1])
    return dp[-1]""",
       """int minPathSum(vector<vector<int>>& g) {
    int R = g.size(), C = g[0].size(); vector<int> dp(C, INT_MAX); dp[0] = 0;
    for (int r = 0; r < R; ++r) {
        dp[0] += g[r][0];
        for (int c = 1; c < C; ++c) dp[c] = g[r][c] + min(dp[c], dp[c - 1]);
    }
    return dp.back();
}"""),

    _p(183, "Maximal Square", "2D Dynamic Programming", "Medium", ["Flipkart", "Microsoft"], "maximal-square",
       "Square DP Trick: if matrix[r][c] == '1', `dp[r][c] = 1 + min(top, left, top_left)`! Answer is max_side^2.",
       "Any zero in the 3 neighbors caps maximal square ending at (r,c).",
       "Time: O(R*C), Space: O(R*C)",
       """def maximalSquare(mat):
    R, C = len(mat), len(mat[0]); dp = [[0]*(C+1) for _ in range(R+1)]; mx = 0
    for r in range(R):
        for c in range(C):
            if mat[r][c] == '1':
                dp[r+1][c+1] = 1 + min(dp[r][c+1], dp[r+1][c], dp[r][c])
                mx = max(mx, dp[r+1][c+1])
    return mx * mx""",
       """int maximalSquare(vector<vector<char>>& m) {
    int R = m.size(), C = m[0].size(), mx = 0;
    vector<vector<int>> dp(R + 1, vector<int>(C + 1, 0));
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) if (m[r][c] == '1') {
        dp[r+1][c+1] = 1 + min({dp[r][c+1], dp[r+1][c], dp[r][c]});
        mx = max(mx, dp[r+1][c+1]);
    }
    return mx * mx;
}"""),

    _p(184, "0/1 Knapsack / Partition to K Equal Sum Subsets", "2D Dynamic Programming", "Medium", ["Google", "Amazon"], "partition-to-k-equal-sum-subsets",
       "Bitmask DP over `2^N` subsets: `dp[mask]` stores current bucket sum mod `target`; valid when `dp[(1<<n)-1] == 0`!",
       "Avoids exponential backtracking TLE by caching subset states.",
       "Time: O(N * 2^N), Space: O(2^N)",
       """def canPartitionKSubsets(nums, k):
    tot = sum(nums)
    if tot % k: return False
    T = tot // k; nums.sort(reverse=True)
    if nums[0] > T: return False
    n = len(nums); dp = [-1] * (1 << n); dp[0] = 0
    for mask in range(1 << n):
        if dp[mask] == -1: continue
        for i in range(n):
            if not (mask & (1 << i)) and dp[mask] + nums[i] <= T:
                dp[mask | (1 << i)] = (dp[mask] + nums[i]) % T
    return dp[(1 << n) - 1] == 0""",
       """bool canPartitionKSubsets(vector<int>& nums, int k) {
    int tot = accumulate(nums.begin(), nums.end(), 0);
    if (tot % k) return false;
    int T = tot / k, n = nums.size();
    vector<int> dp(1 << n, -1); dp[0] = 0;
    for (int mask = 0; mask < (1 << n); ++mask) if (dp[mask] != -1)
        for (int i = 0; i < n; ++i) if (!(mask & (1 << i)) && dp[mask] + nums[i] <= T)
            dp[mask | (1 << i)] = (dp[mask] + nums[i]) % T;
    return dp[(1 << n) - 1] == 0;
}"""),

    # --- 14. GREEDY & INTERVALS (10) ---
    _p(185, "Jump Game", "Greedy & Intervals", "Medium", ["Paytm", "Amazon", "Zepto"], "jump-game",
       "Work backwards! Move `goal = i` left whenever `i + nums[i] >= goal`; reachable iff goal reaches 0!",
       "Single linear pass in O(1) space.",
       "Time: O(N), Space: O(1)",
       """def canJump(nums):
    goal = len(nums) - 1
    for i in range(len(nums) - 2, -1, -1):
        if i + nums[i] >= goal: goal = i
    return goal == 0""",
       """bool canJump(vector<int>& nums) {
    int goal = nums.size() - 1;
    for (int i = nums.size() - 2; i >= 0; --i) if (i + nums[i] >= goal) goal = i;
    return goal == 0;
}"""),

    _p(186, "Gas Station", "Greedy & Intervals", "Medium", ["Google", "Flipkart", "Razorpay"], "gas-station",
       "Total sum >= 0 guarantees a unique solution! Reset `start = i + 1` and `tank = 0` whenever running tank dips < 0!",
       "If you run out of gas going A->B, no station between A and B can reach past B.",
       "Time: O(N), Space: O(1)",
       """def canCompleteCircuit(gas, cost):
    if sum(gas) < sum(cost): return -1
    tank = start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0: tank = 0; start = i + 1
    return start""",
       """int canCompleteCircuit(vector<int>& gas, vector<int>& cost) {
    int tot = 0, tank = 0, start = 0;
    for (int i = 0; i < gas.size(); ++i) {
        int d = gas[i] - cost[i]; tot += d; tank += d;
        if (tank < 0) { tank = 0; start = i + 1; }
    }
    return tot >= 0 ? start : -1;
}"""),

    _p(187, "Hand of Straights", "Greedy & Intervals", "Medium", ["Google", "Amazon"], "hand-of-straights",
       "Sort keys of frequency Counter: start consecutive group of size W from the smallest active card and subtract its count across [x..x+W-1]!",
       "If any card in [x..x+W-1] lacks count, return False.",
       "Time: O(N log N), Space: O(N)",
       """from collections import Counter
def isNStraightHand(hand, groupSize):
    if len(hand) % groupSize: return False
    cnt = Counter(hand)
    for k in sorted(cnt):
        if cnt[k] > 0:
            need = cnt[k]
            for v in range(k, k + groupSize):
                if cnt[v] < need: return False
                cnt[v] -= need
    return True""",
       """bool isNStraightHand(vector<int>& hand, int w) {
    if (hand.size() % w) return false;
    map<int, int> cnt; for (int x : hand) cnt[x]++;
    for (auto& [k, need] : cnt) if (need > 0)
        for (int v = k + w - 1; v >= k; --v) { if (cnt[v] < need) return false; cnt[v] -= need; }
    return true;
}"""),

    _p(188, "Partition Labels", "Greedy & Intervals", "Medium", ["Amazon", "Swiggy"], "partition-labels",
       "Store `last_index[char]`: expand partition `end = max(end, last[s[i]])`; cut whenever `i == end`!",
       "Two passes over string in O(1) space (26 chars).",
       "Time: O(N), Space: O(1)",
       """def partitionLabels(s):
    last = {c: i for i, c in enumerate(s)}
    res, start, end = [], 0, 0
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end: res.append(i - start + 1); start = i + 1
    return res""",
       """vector<int> partitionLabels(string s) {
    int last[26] = {0}; for (int i = 0; i < s.size(); ++i) last[s[i]-'a'] = i;
    vector<int> res; int st = 0, end = 0;
    for (int i = 0; i < s.size(); ++i) {
        end = max(end, last[s[i]-'a']);
        if (i == end) { res.push_back(i - st + 1); st = i + 1; }
    }
    return res;
}"""),

    _p(189, "Valid Parenthesis String (* Wildcard)", "Greedy & Intervals", "Medium", ["Meta", "CRED"], "valid-parenthesis-string",
       "Track interval `[leftMin, leftMax]` of open '(' counts! '(' shifts both +1; ')' shifts both -1; '*' widens [leftMin-1, leftMax+1]. Clamp leftMin >= 0!",
       "Valid iff leftMax never drops < 0 and leftMin == 0 at end.",
       "Time: O(N), Space: O(1)",
       """def checkValidString(s):
    lo = hi = 0
    for c in s:
        if c == '(': lo += 1; hi += 1
        elif c == ')': lo -= 1; hi -= 1
        else: lo -= 1; hi += 1
        if hi < 0: return False
        lo = max(0, lo)
    return lo == 0""",
       """bool checkValidString(string s) {
    int lo = 0, hi = 0;
    for (char c : s) {
        if (c == '(') { lo++; hi++; } else if (c == ')') { lo--; hi--; } else { lo--; hi++; }
        if (hi < 0) return false;
        lo = max(0, lo);
    }
    return lo == 0;
}"""),

    _p(190, "Merge Intervals", "Greedy & Intervals", "Medium", ["Razorpay", "Zepto", "Atlassian", "Amazon"], "merge-intervals",
       "Sort by start time ascending: if `res[-1][1] >= start`, merge `res[-1][1] = max(res[-1][1], end)`; else append new interval!",
       "#1 most tested interval problem in backend interviews.",
       "Time: O(N log N), Space: O(N)",
       """def merge(intervals):
    intervals.sort()
    res = [intervals[0]]
    for s, e in intervals[1:]:
        if s <= res[-1][1]: res[-1][1] = max(res[-1][1], e)
        else: res.append([s, e])
    return res""",
       """vector<vector<int>> merge(vector<vector<int>>& iv) {
    sort(iv.begin(), iv.end());
    vector<vector<int>> res{iv[0]};
    for (int i = 1; i < iv.size(); ++i) {
        if (iv[i][0] <= res.back()[1]) res.back()[1] = max(res.back()[1], iv[i][1]);
        else res.push_back(iv[i]);
    }
    return res;
}"""),

    _p(191, "Insert Interval", "Greedy & Intervals", "Medium", ["Google", "LinkedIn"], "insert-interval",
       "Already sorted! Three clean phases: (1) append intervals ending before newStart, (2) merge all overlapping intervals into [minStart, maxEnd], (3) append rest!",
       "Linear O(N) without re-sorting.",
       "Time: O(N), Space: O(N)",
       """def insert(intervals, newInterval):
    res, i, n = [], 0, len(intervals)
    while i < n and intervals[i][1] < newInterval[0]: res.append(intervals[i]); i += 1
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval[0] = min(newInterval[0], intervals[i][0])
        newInterval[1] = max(newInterval[1], intervals[i][1]); i += 1
    res.append(newInterval)
    return res + intervals[i:]""",
       """vector<vector<int>> insert(vector<vector<int>>& iv, vector<int>& nw) {
    vector<vector<int>> res; int i = 0, n = iv.size();
    while (i < n && iv[i][1] < nw[0]) res.push_back(iv[i++]);
    while (i < n && iv[i][0] <= nw[1]) {
        nw[0] = min(nw[0], iv[i][0]); nw[1] = max(nw[1], iv[i++][1]);
    }
    res.push_back(nw);
    while (i < n) res.push_back(iv[i++]);
    return res;
}"""),

    _p(192, "Non-overlapping Intervals", "Greedy & Intervals", "Medium", ["Flipkart", "Meta"], "non-overlapping-intervals",
       "Sort by END time (or start & keep min end): on overlap, REMOVE the interval with the LARGER end time so more space stays free!",
       "Greedy interval scheduling maximizes kept non-overlapping intervals.",
       "Time: O(N log N), Space: O(1)",
       """def eraseOverlapIntervals(intervals):
    intervals.sort(); prevEnd = intervals[0][1]; rem = 0
    for s, e in intervals[1:]:
        if s >= prevEnd: prevEnd = e
        else: rem += 1; prevEnd = min(prevEnd, e)
    return rem""",
       """int eraseOverlapIntervals(vector<vector<int>>& iv) {
    sort(iv.begin(), iv.end()); int prevEnd = iv[0][1], rem = 0;
    for (int i = 1; i < iv.size(); ++i) {
        if (iv[i][0] >= prevEnd) prevEnd = iv[i][1];
        else { rem++; prevEnd = min(prevEnd, iv[i][1]); }
    }
    return rem;
}"""),

    _p(193, "Meeting Rooms II (Minimum Platforms / Sweep Line)", "Greedy & Intervals", "Medium", ["Uber", "Razorpay", "Amazon"], "meeting-rooms-ii",
       "Two-Pointer Sweep Line: sort `starts` and `ends` separately! While starts[i] < ends[j] -> need new room (`cnt++`); else free room (`cnt--, j++`)!",
       "Equivalent to Minimum Railway Platforms in Indian interviews.",
       "Time: O(N log N), Space: O(N)",
       """def minMeetingRooms(intervals):
    starts = sorted(i[0] for i in intervals)
    ends = sorted(i[1] for i in intervals)
    s = e = rooms = best = 0
    while s < len(starts):
        if starts[s] < ends[e]: rooms += 1; s += 1
        else: rooms -= 1; e += 1
        best = max(best, rooms)
    return best""",
       """int minMeetingRooms(vector<vector<int>>& iv) {
    vector<int> st, en; for (auto& x : iv) { st.push_back(x[0]); en.push_back(x[1]); }
    sort(st.begin(), st.end()); sort(en.begin(), en.end());
    int s = 0, e = 0, cur = 0, best = 0;
    while (s < st.size()) {
        if (st[s] < en[e]) { cur++; s++; } else { cur--; e++; }
        best = max(best, cur);
    }
    return best;
}"""),

    _p(194, "Minimum Interval to Include Each Query", "Greedy & Intervals", "Hard", ["Google", "Atlassian"], "minimum-interval-to-include-each-query",
       "Offline Queries + Min-Heap: sort intervals & queries ascending; push valid intervals `(length, end)` into Min-Heap, pop expired (`end < q`), top is min length!",
       "Answers queries in original order using saved index.",
       "Time: O(N log N + Q log Q), Space: O(N + Q)",
       """import heapq
def minInterval(intervals, queries):
    intervals.sort(); h, res, i = [], {}, 0
    for q in sorted(queries):
        while i < len(intervals) and intervals[i][0] <= q:
            l, r = intervals[i]; heapq.heappush(h, (r - l + 1, r)); i += 1
        while h and h[0][1] < q: heapq.heappop(h)
        res[q] = h[0][0] if h else -1
    return [res[q] for q in queries]""",
       """vector<int> minInterval(vector<vector<int>>& iv, vector<int>& queries) {
    sort(iv.begin(), iv.end());
    vector<int> sq = queries; sort(sq.begin(), sq.end());
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;
    unordered_map<int, int> mp; int i = 0;
    for (int q : sq) {
        while (i < iv.size() && iv[i][0] <= q) { pq.push({iv[i][1]-iv[i][0]+1, iv[i][1]}); i++; }
        while (!pq.empty() && pq.top().second < q) pq.pop();
        mp[q] = pq.empty() ? -1 : pq.top().first;
    }
    vector<int> res; for (int q : queries) res.push_back(mp[q]);
    return res;
}"""),

    # --- 15. BIT MANIPULATION & MATH (6) ---
    _p(195, "Single Number", "Bit Manipulation & Math", "Easy", ["Amazon", "Paytm"], "single-number",
       "XOR Trick: `a ^ a = 0` and `a ^ 0 = a` -> XOR all numbers together; duplicates cancel out leaving the unique number in O(1) space!",
       "Bitwise associative + commutative cancellation.",
       "Time: O(N), Space: O(1)",
       """def singleNumber(nums):
    x = 0
    for n in nums: x ^= n
    return x""",
       """int singleNumber(vector<int>& nums) {
    int x = 0; for (int n : nums) x ^= n; return x;
}"""),

    _p(196, "Number of 1 Bits (Brian Kernighan)", "Bit Manipulation & Math", "Easy", ["Qualcomm", "Apple"], "number-of-1-bits",
       "Kernighan Trick: `n &= (n - 1)` strips the LOWEST set bit in 1 operation -> loops ONLY K times where K = number of 1 bits!",
       "Strictly faster than checking all 32 bits when sparse.",
       "Time: O(SetBits), Space: O(1)",
       """def hammingWeight(n):
    cnt = 0
    while n: n &= n - 1; cnt += 1
    return cnt""",
       """int hammingWeight(uint32_t n) {
    int cnt = 0; while (n) { n &= (n - 1); cnt++; } return cnt;
}"""),

    _p(197, "Counting Bits", "Bit Manipulation & Math", "Easy", ["Google", "Microsoft"], "counting-bits",
       "DP + Bit Offset: `dp[i] = dp[i >> 1] + (i & 1)` computes popcount for 0..N in linear O(N) time!",
       "Right shift drops LSB and reuses precomputed count.",
       "Time: O(N), Space: O(N)",
       """def countBits(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1): dp[i] = dp[i >> 1] + (i & 1)
    return dp""",
       """vector<int> countBits(int n) {
    vector<int> dp(n + 1, 0);
    for (int i = 1; i <= n; ++i) dp[i] = dp[i >> 1] + (i & 1);
    return dp;
}"""),

    _p(198, "Missing Number", "Bit Manipulation & Math", "Easy", ["Flipkart", "Amazon"], "missing-number",
       "XOR indices `0..N` with array elements `nums[0..N-1]` — every existing value cancels out leaving missing number in O(1) space with ZERO overflow risk!",
       "Or Gauss sum `n*(n+1)//2 - sum(nums)`.",
       "Time: O(N), Space: O(1)",
       """def missingNumber(nums):
    res = len(nums)
    for i, x in enumerate(nums): res ^= i ^ x
    return res""",
       """int missingNumber(vector<int>& nums) {
    int res = nums.size();
    for (int i = 0; i < nums.size(); ++i) res ^= i ^ nums[i];
    return res;
}"""),

    _p(199, "Pow(x, n) (Binary Exponentiation)", "Bit Manipulation & Math", "Medium", ["Meta", "Razorpay", "Google"], "powx-n",
       "Binary Exponentiation: square x and halve n each step (`n >>= 1`); multiply into `res` when `n & 1`! Cast exponent to `long long` in C++ for INT_MIN!",
       "Computes x^n in O(log N) instead of O(N).",
       "Time: O(log N), Space: O(1)",
       """def myPow(x, n):
    if n < 0: x, n = 1 / x, -n
    res = 1.0
    while n:
        if n & 1: res *= x
        x *= x; n >>= 1
    return res""",
       """double myPow(double x, int n) {
    long long exp = n; if (exp < 0) { x = 1.0 / x; exp = -exp; }
    double res = 1.0;
    while (exp > 0) {
        if (exp & 1) res *= x;
        x *= x; exp >>= 1;
    }
    return res;
}"""),

    _p(200, "Rotate Image (Matrix 90° Clockwise)", "Bit Manipulation & Math", "Medium", ["Microsoft", "Amazon", "Swiggy"], "rotate-image",
       "In-Place 2-Step Trick: (1) Transpose matrix across main diagonal (`swap(m[r][c], m[c][r])`), (2) Reverse every row!",
       "Zero extra memory needed; trivial to remember under interview pressure.",
       "Time: O(N^2), Space: O(1)",
       """def rotateImage(matrix):
    n = len(matrix)
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    for row in matrix: row.reverse()""",
       """void rotate(vector<vector<int>>& m) {
    int n = m.size();
    for (int r = 0; r < n; ++r)
        for (int c = r + 1; c < n; ++c) swap(m[r][c], m[c][r]);
    for (auto& row : m) reverse(row.begin(), row.end());
}"""),
]
