def _p(num, title, pattern, diff, companies, slug, trick, intuition, comp, py, cpp):
    return {
        "num": num,
        "id": f"dsa-{num:03d}",
        "title": title,
        "pattern": pattern,
        "difficulty": diff,
        "companies": companies,
        "leetcode_url": f"https://leetcode.com/problems/{slug}/",
        "trick": trick,
        "intuition": intuition,
        "complexity": comp,
        "python_code": py.strip(),
        "cpp_code": cpp.strip(),
    }

DSA_PART1 = [
    # --- 1. ARRAYS & HASHING (15) ---
    _p(1, "Two Sum", "Arrays & Hashing", "Easy", ["Amazon", "Razorpay", "Google"], "two-sum",
       "Need pair summing to target? Store visited values in HashMap and check (target - x) in O(1).",
       "Brute: O(N^2) nested loops. Optimal: Single pass HashMap mapping num -> index; lookup complement before inserting.",
       "Time: O(N), Space: O(N)",
       """def twoSum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i""",
       """vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int, int> seen;
    for (int i = 0; i < nums.size(); ++i) {
        int need = target - nums[i];
        if (seen.count(need)) return {seen[need], i};
        seen[nums[i]] = i;
    }
    return {};
}"""),

    _p(2, "Contains Duplicate", "Arrays & Hashing", "Easy", ["Microsoft", "Flipkart"], "contains-duplicate",
       "Frequency/uniqueness check without sorting -> HashSet tracks seen elements in O(1).",
       "Brute: Sort O(N log N) and compare neighbors. Optimal: Insert into HashSet; if already present return True.",
       "Time: O(N), Space: O(N)",
       """def containsDuplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False""",
       """bool containsDuplicate(vector<int>& nums) {
    unordered_set<int> seen;
    for (int x : nums) {
        if (!seen.insert(x).second) return true;
    }
    return false;
}"""),

    _p(3, "Valid Anagram", "Arrays & Hashing", "Easy", ["CRED", "Swiggy"], "valid-anagram",
       "Permutation or anagram check on lowercase letters -> fixed 26-int frequency array avoids HashMap overhead.",
       "Brute: Sort both strings O(N log N). Optimal: Increment count for s[i], decrement for t[i]; verify all 26 counts equal 0.",
       "Time: O(N), Space: O(1)",
       """def isAnagram(s, t):
    if len(s) != len(t): return False
    cnt = [0] * 26
    for a, b in zip(s, t):
        cnt[ord(a) - 97] += 1
        cnt[ord(b) - 97] -= 1
    return all(c == 0 for c in cnt)""",
       """bool isAnagram(string s, string t) {
    if (s.size() != t.size()) return false;
    int cnt[26] = {0};
    for (int i = 0; i < s.size(); ++i) {
        cnt[s[i] - 'a']++;
        cnt[t[i] - 'a']--;
    }
    for (int c : cnt) if (c != 0) return false;
    return true;
}"""),

    _p(4, "Group Anagrams", "Arrays & Hashing", "Medium", ["Zepto", "Amazon", "Atlassian"], "group-anagrams",
       "Group strings with identical character frequencies -> use 26-count tuple/string as canonical HashMap key in O(N*K).",
       "Brute: Sort each string O(N * K log K). Optimal: Build 26-length frequency signature per string and group in dict.",
       "Time: O(N * K), Space: O(N * K)",
       """from collections import defaultdict
def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        cnt = [0] * 26
        for ch in s: cnt[ord(ch) - 97] += 1
        groups[tuple(cnt)].append(s)
    return list(groups.values())""",
       """vector<vector<string>> groupAnagrams(vector<string>& strs) {
    unordered_map<string, vector<string>> mp;
    for (auto& s : strs) {
        string key = s;
        sort(key.begin(), key.end());
        mp[key].push_back(s);
    }
    vector<vector<string>> res;
    for (auto& kv : mp) res.push_back(move(kv.second));
    return res;
}"""),

    _p(5, "Top K Frequent Elements", "Arrays & Hashing", "Medium", ["Razorpay", "Uber", "Amazon"], "top-k-frequent-elements",
       "Top K frequencies in linear O(N) time -> Bucket Sort indexed by frequency (0..N) beats O(N log K) heap.",
       "Brute: Sort by frequency O(N log N). Optimal: Count frequencies, place numbers into buckets[freq], iterate buckets backwards.",
       "Time: O(N), Space: O(N)",
       """from collections import Counter
def topKFrequent(nums, k):
    cnt = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, f in cnt.items():
        buckets[f].append(num)
    res = []
    for f in range(len(nums), 0, -1):
        for num in buckets[f]:
            res.append(num)
            if len(res) == k: return res""",
       """vector<int> topKFrequent(vector<int>& nums, int k) {
    unordered_map<int, int> cnt;
    for (int x : nums) cnt[x]++;
    vector<vector<int>> buckets(nums.size() + 1);
    for (auto& [val, f] : cnt) buckets[f].push_back(val);
    vector<int> res;
    for (int f = nums.size(); f > 0 && res.size() < k; --f)
        for (int v : buckets[f]) {
            res.push_back(v);
            if (res.size() == k) break;
        }
    return res;
}"""),

    _p(6, "Product of Array Except Self", "Arrays & Hashing", "Medium", ["Swiggy", "Flipkart", "Microsoft"], "product-of-array-except-self",
       "No division allowed + product of all other elements -> two passes: left prefix products * right suffix products.",
       "Brute: O(N^2) products. Optimal: Pass 1 stores prefix product in res[i]; Pass 2 multiplies running suffix scalar into res[i].",
       "Time: O(N), Space: O(1) extra",
       """def productExceptSelf(nums):
    n = len(nums)
    res = [1] * n
    pre = 1
    for i in range(n):
        res[i] = pre
        pre *= nums[i]
    suf = 1
    for i in range(n - 1, -1, -1):
        res[i] *= suf
        suf *= nums[i]
    return res""",
       """vector<int> productExceptSelf(vector<int>& nums) {
    int n = nums.size(), pre = 1, suf = 1;
    vector<int> res(n, 1);
    for (int i = 0; i < n; ++i) { res[i] = pre; pre *= nums[i]; }
    for (int i = n - 1; i >= 0; --i) { res[i] *= suf; suf *= nums[i]; }
    return res;
}"""),

    _p(7, "Valid Sudoku", "Arrays & Hashing", "Medium", ["PhonePe", "Uber"], "valid-sudoku",
       "Check 9x9 constraints cleanly -> encode box index as (r // 3, c // 3) alongside row and col sets.",
       "Maintain 3 bitmasks or sets per row, col, and 3x3 subgrid; return False immediately upon duplicate digit.",
       "Time: O(81), Space: O(81)",
       """def isValidSudoku(board):
    rows, cols, boxes = [set() for _ in range(9)], [set() for _ in range(9)], [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v == '.': continue
            b = (r // 3) * 3 + c // 3
            if v in rows[r] or v in cols[c] or v in boxes[b]: return False
            rows[r].add(v); cols[c].add(v); boxes[b].add(v)
    return True""",
       """bool isValidSudoku(vector<vector<char>>& board) {
    int r[9]={0}, c[9]={0}, b[9]={0};
    for (int i = 0; i < 9; ++i)
        for (int j = 0; j < 9; ++j) {
            if (board[i][j] == '.') continue;
            int mask = 1 << (board[i][j] - '1'), box = (i/3)*3 + j/3;
            if ((r[i] & mask) || (c[j] & mask) || (b[box] & mask)) return false;
            r[i] |= mask; c[j] |= mask; b[box] |= mask;
        }
    return true;
}"""),

    _p(8, "Longest Consecutive Sequence", "Arrays & Hashing", "Medium", ["Google", "CRED", "Zepto"], "longest-consecutive-sequence",
       "Only start counting streaks at sequence heads: numbers where (x - 1) is NOT in the HashSet -> guarantees O(N) total work.",
       "Brute: Sort O(N log N). Optimal: Put all items in HashSet. For x, if x-1 not in set, expand x+1, x+2... while in set.",
       "Time: O(N), Space: O(N)",
       """def longestConsecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x + 1
            while y in s: y += 1
            best = max(best, y - x)
    return best""",
       """int longestConsecutive(vector<int>& nums) {
    unordered_set<int> s(nums.begin(), nums.end());
    int best = 0;
    for (int x : s) {
        if (!s.count(x - 1)) {
            int y = x + 1;
            while (s.count(y)) y++;
            best = max(best, y - x);
        }
    }
    return best;
}"""),

    _p(9, "Subarray Sum Equals K", "Arrays & Hashing", "Medium", ["Razorpay", "Facebook", "Amazon"], "subarray-sum-equals-k",
       "Subarray sum with negatives? Sliding window fails -> Prefix Sum + HashMap counting how many times (curr_sum - k) appeared!",
       "Brute: O(N^2) sums. Optimal: Accumulate prefix sum; add freq[prefix - k] to ans; increment freq[prefix]. Seed freq[0]=1.",
       "Time: O(N), Space: O(N)",
       """from collections import defaultdict
def subarraySum(nums, k):
    freq = defaultdict(int, {0: 1})
    cur = ans = 0
    for x in nums:
        cur += x
        ans += freq[cur - k]
        freq[cur] += 1
    return ans""",
       """int subarraySum(vector<int>& nums, int k) {
    unordered_map<int, int> freq{{0, 1}};
    int cur = 0, ans = 0;
    for (int x : nums) {
        cur += x;
        if (freq.count(cur - k)) ans += freq[cur - k];
        freq[cur]++;
    }
    return ans;
}"""),

    _p(10, "Maximum Subarray (Kadane's Algorithm)", "Arrays & Hashing", "Medium", ["Flipkart", "Microsoft", "Swiggy"], "maximum-subarray",
       "Drop negative baggage: if running sum drops below 0 (or cur + x < x), restart fresh at x.",
       "Kadane's DP: best ending here cur = max(x, cur + x); global ans = max(ans, cur).",
       "Time: O(N), Space: O(1)",
       """def maxSubArray(nums):
    cur = best = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best""",
       """int maxSubArray(vector<int>& nums) {
    int cur = nums[0], best = nums[0];
    for (int i = 1; i < nums.size(); ++i) {
        cur = max(nums[i], cur + nums[i]);
        best = max(best, cur);
    }
    return best;
}"""),

    _p(11, "Majority Element (Boyer-Moore Voting)", "Arrays & Hashing", "Easy", ["Amazon", "Adobe"], "majority-element",
       "Guaranteed > N/2 element? Keep a candidate and counter: same increments, different decrements, cancel out pairs in O(1) space.",
       "Brute: HashMap O(N) space. Optimal: Boyer-Moore voting cancels non-majority pairs leaving the true majority.",
       "Time: O(N), Space: O(1)",
       """def majorityElement(nums):
    cand, cnt = 0, 0
    for x in nums:
        if cnt == 0: cand = x
        cnt += 1 if x == cand else -1
    return cand""",
       """int majorityElement(vector<int>& nums) {
    int cand = 0, cnt = 0;
    for (int x : nums) {
        if (cnt == 0) cand = x;
        cnt += (x == cand ? 1 : -1);
    }
    return cand;
}"""),

    _p(12, "Sort Colors (Dutch National Flag)", "Arrays & Hashing", "Medium", ["Paytm", "Microsoft", "Amazon"], "sort-colors",
       "3 distinct values (0, 1, 2) in-place one pass? 3 pointers (low, mid, high) swap 0s left and 2s right.",
       "When swapping mid with high, do NOT increment mid because the swapped element from high is uninspected.",
       "Time: O(N), Space: O(1)",
       """def sortColors(nums):
    l, m, r = 0, 0, len(nums) - 1
    while m <= r:
        if nums[m] == 0:
            nums[l], nums[m] = nums[m], nums[l]; l += 1; m += 1
        elif nums[m] == 1: m += 1
        else:
            nums[m], nums[r] = nums[r], nums[m]; r -= 1""",
       """void sortColors(vector<int>& nums) {
    int l = 0, m = 0, r = nums.size() - 1;
    while (m <= r) {
        if (nums[m] == 0) swap(nums[l++], nums[m++]);
        else if (nums[m] == 1) m++;
        else swap(nums[m], nums[r--]);
    }
}"""),

    _p(13, "First Missing Positive", "Arrays & Hashing", "Hard", ["Atlassian", "Amazon", "CRED"], "first-missing-positive",
       "Missing positive in [1..N] using O(1) space? Cyclic Sort! Place each value v in [1..N] at index v - 1.",
       "Swap nums[i] with nums[nums[i]-1] while valid and misplaced; then scan for first index where nums[i] != i + 1.",
       "Time: O(N), Space: O(1)",
       """def firstMissingPositive(nums):
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            j = nums[i] - 1
            nums[i], nums[j] = nums[j], nums[i]
    for i in range(n):
        if nums[i] != i + 1: return i + 1
    return n + 1""",
       """int firstMissingPositive(vector<int>& nums) {
    int n = nums.size();
    for (int i = 0; i < n; ++i)
        while (nums[i] >= 1 && nums[i] <= n && nums[nums[i] - 1] != nums[i])
            swap(nums[i], nums[nums[i] - 1]);
    for (int i = 0; i < n; ++i)
        if (nums[i] != i + 1) return i + 1;
    return n + 1;
}"""),

    _p(14, "Next Permutation", "Arrays & Hashing", "Medium", ["Google", "Flipkart", "Zepto"], "next-permutation",
       "Right-to-left: find first dip nums[i] < nums[i+1], swap with smallest larger on right, reverse suffix i+1..end.",
       "If entire array is descending, skip swap and reverse the whole array to reset to smallest permutation.",
       "Time: O(N), Space: O(1)",
       """def nextPermutation(nums):
    i = len(nums) - 2
    while i >= 0 and nums[i] >= nums[i + 1]: i -= 1
    if i >= 0:
        j = len(nums) - 1
        while nums[j] <= nums[i]: j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = reversed(nums[i + 1:])""",
       """void nextPermutation(vector<int>& nums) {
    int n = nums.size(), i = n - 2;
    while (i >= 0 && nums[i] >= nums[i + 1]) i--;
    if (i >= 0) {
        int j = n - 1;
        while (nums[j] <= nums[i]) j--;
        swap(nums[i], nums[j]);
    }
    reverse(nums.begin() + i + 1, nums.end());
}"""),

    _p(15, "Set Matrix Zeroes", "Arrays & Hashing", "Medium", ["Swiggy", "Microsoft"], "set-matrix-zeroes",
       "Use row 0 and col 0 as O(1) marker flags; track col0 separately in 1 boolean so matrix[0][0] doesn't collide.",
       "Pass 1: mark row/col headers on seeing 0. Pass 2 (reverse): fill zeroes so markers aren't overwritten early.",
       "Time: O(M*N), Space: O(1)",
       """def setZeroes(m):
    R, C, col0 = len(m), len(m[0]), False
    for r in range(R):
        if m[r][0] == 0: col0 = True
        for c in range(1, C):
            if m[r][c] == 0: m[r][0] = m[0][c] = 0
    for r in range(R - 1, -1, -1):
        for c in range(C - 1, 0, -1):
            if m[r][0] == 0 or m[0][c] == 0: m[r][c] = 0
        if col0: m[r][0] = 0""",
       """void setZeroes(vector<vector<int>>& m) {
    int R = m.size(), C = m[0].size(); bool col0 = false;
    for (int r = 0; r < R; ++r) {
        if (m[r][0] == 0) col0 = true;
        for (int c = 1; c < C; ++c)
            if (m[r][c] == 0) m[r][0] = m[0][c] = 0;
    }
    for (int r = R - 1; r >= 0; --r) {
        for (int c = C - 1; c >= 1; --c)
            if (m[r][0] == 0 || m[0][c] == 0) m[r][c] = 0;
        if (col0) m[r][0] = 0;
    }
}"""),

    # --- 2. TWO POINTERS (12) ---
    _p(16, "Valid Palindrome", "Two Pointers", "Easy", ["Paytm", "Meta"], "valid-palindrome",
       "Skip non-alphanumerics from both ends with two converging pointers in O(1) extra space.",
       "While l < r, skip non-isalnum, compare lowercase chars.",
       "Time: O(N), Space: O(1)",
       """def isPalindrome(s):
    l, r = 0, len(s) - 1
    while l < r:
        while l < r and not s[l].isalnum(): l += 1
        while l < r and not s[r].isalnum(): r -= 1
        if s[l].lower() != s[r].lower(): return False
        l += 1; r -= 1
    return True""",
       """bool isPalindrome(string s) {
    int l = 0, r = (int)s.size() - 1;
    while (l < r) {
        while (l < r && !isalnum(s[l])) l++;
        while (l < r && !isalnum(s[r])) r--;
        if (tolower(s[l++]) != tolower(s[r--])) return false;
    }
    return true;
}"""),

    _p(17, "Two Sum II (Sorted Array)", "Two Pointers", "Medium", ["Amazon", "Adobe"], "two-sum-ii-input-array-is-sorted",
       "Sorted array pair sum -> left + right pointers move inward deterministically in O(1) space.",
       "Sum < target? l++. Sum > target? r--. Exact? Return 1-based indices.",
       "Time: O(N), Space: O(1)",
       """def twoSumII(nums, target):
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target: return [l + 1, r + 1]
        if s < target: l += 1
        else: r -= 1""",
       """vector<int> twoSum(vector<int>& nums, int target) {
    int l = 0, r = nums.size() - 1;
    while (l < r) {
        int s = nums[l] + nums[r];
        if (s == target) return {l + 1, r + 1};
        if (s < target) l++; else r--;
    }
    return {};
}"""),

    _p(18, "3Sum", "Two Pointers", "Medium", ["Razorpay", "Zepto", "Amazon"], "3sum",
       "Sort array first -> fix nums[i] (skip duplicates!) and run 2Sum two pointers on i+1..end (skipping inner duplicates).",
       "Reduces O(N^3) to O(N^2) without needing a HashSet for dedup.",
       "Time: O(N^2), Space: O(1) aux",
       """def threeSum(nums):
    nums.sort()
    res = []
    for i, a in enumerate(nums):
        if i > 0 and a == nums[i - 1]: continue
        l, r = i + 1, len(nums) - 1
        while l < r:
            s = a + nums[l] + nums[r]
            if s < 0: l += 1
            elif s > 0: r -= 1
            else:
                res.append([a, nums[l], nums[r]])
                l += 1
                while l < r and nums[l] == nums[l - 1]: l += 1
    return res""",
       """vector<vector<int>> threeSum(vector<int>& nums) {
    sort(nums.begin(), nums.end());
    vector<vector<int>> res;
    for (int i = 0; i < nums.size(); ++i) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        int l = i + 1, r = nums.size() - 1;
        while (l < r) {
            int s = nums[i] + nums[l] + nums[r];
            if (s < 0) l++;
            else if (s > 0) r--;
            else {
                res.push_back({nums[i], nums[l], nums[r]});
                l++; while (l < r && nums[l] == nums[l - 1]) l++;
            }
        }
    }
    return res;
}"""),

    _p(19, "Container With Most Water", "Two Pointers", "Medium", ["Swiggy", "Google", "Amazon"], "container-with-most-water",
       "Greedy shrinkage: width always shrinks, so ALWAYS advance the shorter wall—moving the taller wall can never increase area.",
       "Start widest [0, n-1]; track max((r-l) * min(h[l], h[r])) while advancing smaller height pointer.",
       "Time: O(N), Space: O(1)",
       """def maxArea(h):
    l, r, ans = 0, len(h) - 1, 0
    while l < r:
        ans = max(ans, (r - l) * min(h[l], h[r]))
        if h[l] < h[r]: l += 1
        else: r -= 1
    return ans""",
       """int maxArea(vector<int>& h) {
    int l = 0, r = h.size() - 1, ans = 0;
    while (l < r) {
        ans = max(ans, (r - l) * min(h[l], h[r]));
        if (h[l] < h[r]) l++; else r--;
    }
    return ans;
}"""),

    _p(20, "Trapping Rain Water", "Two Pointers", "Hard", ["CRED", "Flipkart", "Atlassian", "Amazon"], "trapping-rain-water",
       "Water at i = min(maxL, maxR) - h[i]. Process whichever side has smaller max wall because that side bounds water immediately!",
       "Keep lMax, rMax scalars and l, r pointers. If lMax <= rMax, trapped water at l is guaranteed lMax - h[l].",
       "Time: O(N), Space: O(1)",
       """def trap(h):
    l, r, lMax, rMax, water = 0, len(h) - 1, 0, 0, 0
    while l < r:
        if h[l] <= h[r]:
            lMax = max(lMax, h[l])
            water += lMax - h[l]; l += 1
        else:
            rMax = max(rMax, h[r])
            water += rMax - h[r]; r -= 1
    return water""",
       """int trap(vector<int>& h) {
    int l = 0, r = h.size() - 1, lm = 0, rm = 0, ans = 0;
    while (l < r) {
        if (h[l] <= h[r]) { lm = max(lm, h[l]); ans += lm - h[l++]; }
        else { rm = max(rm, h[r]); ans += rm - h[r--]; }
    }
    return ans;
}"""),

    _p(21, "Remove Duplicates from Sorted Array", "Two Pointers", "Easy", ["Meesho", "Microsoft"], "remove-duplicates-from-sorted-array",
       "Read/Write slow-fast pointer: write pointer k only advances when reader sees nums[i] != nums[k-1].",
       "In-place overwrite keeping first k elements sorted and unique.",
       "Time: O(N), Space: O(1)",
       """def removeDuplicates(nums):
    k = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[k - 1]:
            nums[k] = nums[i]; k += 1
    return k""",
       """int removeDuplicates(vector<int>& nums) {
    int k = 1;
    for (int i = 1; i < nums.size(); ++i)
        if (nums[i] != nums[k - 1]) nums[k++] = nums[i];
    return k;
}"""),

    _p(22, "Move Zeroes", "Two Pointers", "Easy", ["Groww", "Meta"], "move-zeroes",
       "Preserve non-zero relative order while pushing 0s right -> swap non-zero at fast index with slow write pointer.",
       "Single pass swap guarantees minimal writes when non-zero elements are sparse.",
       "Time: O(N), Space: O(1)",
       """def moveZeroes(nums):
    k = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[k], nums[i] = nums[i], nums[k]; k += 1""",
       """void moveZeroes(vector<int>& nums) {
    int k = 0;
    for (int i = 0; i < nums.size(); ++i)
        if (nums[i] != 0) swap(nums[k++], nums[i]);
}"""),

    _p(23, "4Sum", "Two Pointers", "Medium", ["Amazon", "Apple"], "4sum",
       "Generalize 3Sum: sort, fix i and j (deduping both), run 2 pointers; watch out for 32-bit int overflow in C++ (cast long long).",
       "Prune early when smallest possible sum > target or largest < target.",
       "Time: O(N^3), Space: O(1) aux",
       """def fourSum(nums, target):
    nums.sort(); n = len(nums); res = []
    for i in range(n - 3):
        if i > 0 and nums[i] == nums[i - 1]: continue
        for j in range(i + 1, n - 2):
            if j > i + 1 and nums[j] == nums[j - 1]: continue
            l, r = j + 1, n - 1
            while l < r:
                s = nums[i] + nums[j] + nums[l] + nums[r]
                if s < target: l += 1
                elif s > target: r -= 1
                else:
                    res.append([nums[i], nums[j], nums[l], nums[r]])
                    l += 1
                    while l < r and nums[l] == nums[l - 1]: l += 1
    return res""",
       """vector<vector<int>> fourSum(vector<int>& nums, int target) {
    sort(nums.begin(), nums.end()); int n = nums.size(); vector<vector<int>> res;
    for (int i = 0; i < n - 3; ++i) {
        if (i > 0 && nums[i] == nums[i-1]) continue;
        for (int j = i + 1; j < n - 2; ++j) {
            if (j > i + 1 && nums[j] == nums[j-1]) continue;
            int l = j + 1, r = n - 1;
            while (l < r) {
                long long s = (long long)nums[i] + nums[j] + nums[l] + nums[r];
                if (s < target) l++; else if (s > target) r--;
                else {
                    res.push_back({nums[i], nums[j], nums[l], nums[r]});
                    l++; while (l < r && nums[l] == nums[l-1]) l++;
                }
            }
        }
    }
    return res;
}"""),

    _p(24, "Rotate Array", "Two Pointers", "Medium", ["PhonePe", "Microsoft"], "rotate-array",
       "Triple Reverse Trick: reverse whole array, reverse first k, reverse rest -> O(1) space in 3 lines!",
       "Always take k %= n first in case k >= n.",
       "Time: O(N), Space: O(1)",
       """def rotate(nums, k):
    n = len(nums); k %= n
    def rev(l, r):
        while l < r: nums[l], nums[r] = nums[r], nums[l]; l += 1; r -= 1
    rev(0, n - 1); rev(0, k - 1); rev(k, n - 1)""",
       """void rotate(vector<int>& nums, int k) {
    k %= nums.size();
    reverse(nums.begin(), nums.end());
    reverse(nums.begin(), nums.begin() + k);
    reverse(nums.begin() + k, nums.end());
}"""),

    _p(25, "Squares of a Sorted Array", "Two Pointers", "Easy", ["Uber", "LinkedIn"], "squares-of-a-sorted-array",
       "Largest squares are at the extremes (leftmost negative or rightmost positive) -> fill output array from back!",
       "Two pointers at 0 and n-1 pick larger abs value and place square at index pos = n-1 down to 0.",
       "Time: O(N), Space: O(N)",
       """def sortedSquares(nums):
    n = len(nums); res = [0] * n; l, r = 0, n - 1
    for pos in range(n - 1, -1, -1):
        if abs(nums[l]) > abs(nums[r]):
            res[pos] = nums[l] ** 2; l += 1
        else:
            res[pos] = nums[r] ** 2; r -= 1
    return res""",
       """vector<int> sortedSquares(vector<int>& nums) {
    int n = nums.size(), l = 0, r = n - 1;
    vector<int> res(n);
    for (int p = n - 1; p >= 0; --p) {
        if (abs(nums[l]) > abs(nums[r])) { res[p] = nums[l]*nums[l]; l++; }
        else { res[p] = nums[r]*nums[r]; r--; }
    }
    return res;
}"""),

    _p(26, "Boats to Save People", "Two Pointers", "Medium", ["Amazon", "Google"], "boats-to-save-people",
       "Max 2 people per boat -> sort weights; always pair heaviest person with lightest if they fit, else heaviest rides solo.",
       "Greedy pairing minimizes boats because lightest person maximizes chances of fitting with heaviest.",
       "Time: O(N log N), Space: O(1)",
       """def numRescueBoats(people, limit):
    people.sort(); l, r, boats = 0, len(people) - 1, 0
    while l <= r:
        if people[l] + people[r] <= limit: l += 1
        r -= 1; boats += 1
    return boats""",
       """int numRescueBoats(vector<int>& people, int limit) {
    sort(people.begin(), people.end());
    int l = 0, r = people.size() - 1, boats = 0;
    while (l <= r) {
        if (people[l] + people[r] <= limit) l++;
        r--; boats++;
    }
    return boats;
}"""),

    _p(27, "Backspace String Compare", "Two Pointers", "Easy", ["Google", "Atlassian"], "backspace-string-compare",
       "O(1) space without Stack? Iterate backwards from end of both strings, counting '#' skips on the fly!",
       "Skip character whenever skip_count > 0 or curr == '#'; compare valid characters.",
       "Time: O(N + M), Space: O(1)",
       """def backspaceCompare(s, t):
    def nextChar(st, idx):
        skip = 0
        while idx >= 0:
            if st[idx] == '#': skip += 1
            elif skip > 0: skip -= 1
            else: break
            idx -= 1
        return idx
    i, j = len(s) - 1, len(t) - 1
    while i >= 0 or j >= 0:
        i, j = nextChar(s, i), nextChar(t, j)
        if (i >= 0) != (j >= 0) or (i >= 0 and s[i] != t[j]): return False
        i -= 1; j -= 1
    return True""",
       """bool backspaceCompare(string s, string t) {
    int i = s.size() - 1, j = t.size() - 1;
    auto nxt = [](const string& st, int idx) {
        int skip = 0;
        while (idx >= 0) {
            if (st[idx] == '#') skip++;
            else if (skip > 0) skip--;
            else break;
            idx--;
        }
        return idx;
    };
    while (i >= 0 || j >= 0) {
        i = nxt(s, i); j = nxt(t, j);
        if ((i >= 0) != (j >= 0) || (i >= 0 && s[i] != t[j])) return false;
        i--; j--;
    }
    return true;
}"""),

    # --- 3. SLIDING WINDOW (14) ---
    _p(28, "Best Time to Buy and Sell Stock", "Sliding Window", "Easy", ["Razorpay", "Zepto", "Amazon"], "best-time-to-buy-and-sell-stock",
       "Track lowest buy price seen so far; max profit at day r is prices[r] - min_buy.",
       "One pass min-so-far + max-diff; O(1) space.",
       "Time: O(N), Space: O(1)",
       """def maxProfit(prices):
    low, best = float('inf'), 0
    for p in prices:
        low = min(low, p)
        best = max(best, p - low)
    return best""",
       """int maxProfit(vector<int>& prices) {
    int low = INT_MAX, best = 0;
    for (int p : prices) {
        low = min(low, p);
        best = max(best, p - low);
    }
    return best;
}"""),

    _p(29, "Longest Substring Without Repeating Characters", "Sliding Window", "Medium", ["Swiggy", "CRED", "Amazon", "Atlassian"], "longest-substring-without-repeating-characters",
       "Map char -> last_index; on duplicate inside active window [l..r], jump l directly to last_index[ch] + 1!",
       "Avoids shrinking l one character at a time; ensures l = max(l, last[ch] + 1).",
       "Time: O(N), Space: O(min(N, Alphabet))",
       """def lengthOfLongestSubstring(s):
    last, l, best = {}, 0, 0
    for r, ch in enumerate(s):
        if ch in last and last[ch] >= l:
            l = last[ch] + 1
        last[ch] = r
        best = max(best, r - l + 1)
    return best""",
       """int lengthOfLongestSubstring(string s) {
    vector<int> last(256, -1);
    int l = 0, best = 0;
    for (int r = 0; r < s.size(); ++r) {
        if (last[s[r]] >= l) l = last[s[r]] + 1;
        last[s[r]] = r;
        best = max(best, r - l + 1);
    }
    return best;
}"""),

    _p(30, "Longest Repeating Character Replacement", "Sliding Window", "Medium", ["Google", "Flipkart"], "longest-repeating-character-replacement",
       "Window is valid iff (window_len - max_freq) <= k! Never even need to decrement max_freq when shrinking!",
       "Wait: max_freq only grows monotonically—if a shorter window can't beat our best, we don't care about reducing max_freq.",
       "Time: O(N), Space: O(26)",
       """def characterReplacement(s, k):
    cnt = [0] * 26; l = maxf = best = 0
    for r, ch in enumerate(s):
        idx = ord(ch) - 65; cnt[idx] += 1
        maxf = max(maxf, cnt[idx])
        while (r - l + 1) - maxf > k:
            cnt[ord(s[l]) - 65] -= 1; l += 1
        best = max(best, r - l + 1)
    return best""",
       """int characterReplacement(string s, int k) {
    int cnt[26] = {0}, l = 0, maxf = 0, best = 0;
    for (int r = 0; r < s.size(); ++r) {
        maxf = max(maxf, ++cnt[s[r] - 'A']);
        while ((r - l + 1) - maxf > k) cnt[s[l++] - 'A']--;
        best = max(best, r - l + 1);
    }
    return best;
}"""),

    _p(31, "Permutation in String", "Sliding Window", "Medium", ["Microsoft", "PhonePe"], "permutation-in-string",
       "Fixed sliding window of size len(s1) + matches counter (0..26) compares two frequency arrays in O(1) per step!",
       "Avoids comparing 26 elements each step by tracking exact match count.",
       "Time: O(N), Space: O(1)",
       """def checkInclusion(s1, s2):
    if len(s1) > len(s2): return False
    c1, c2 = [0]*26, [0]*26
    for i in range(len(s1)):
        c1[ord(s1[i])-97] += 1; c2[ord(s2[i])-97] += 1
    if c1 == c2: return True
    for r in range(len(s1), len(s2)):
        c2[ord(s2[r])-97] += 1
        c2[ord(s2[r-len(s1)])-97] -= 1
        if c1 == c2: return True
    return False""",
       """bool checkInclusion(string s1, string s2) {
    if (s1.size() > s2.size()) return false;
    vector<int> c1(26, 0), c2(26, 0);
    for (int i = 0; i < s1.size(); ++i) { c1[s1[i]-'a']++; c2[s2[i]-'a']++; }
    if (c1 == c2) return true;
    for (int r = s1.size(); r < s2.size(); ++r) {
        c2[s2[r]-'a']++; c2[s2[r - s1.size()]-'a']--;
        if (c1 == c2) return true;
    }
    return false;
}"""),

    _p(32, "Minimum Window Substring", "Sliding Window", "Hard", ["Uber", "Zepto", "Meta", "Amazon"], "minimum-window-substring",
       "Track `have == need` unique required char counts: expand r until valid, then greedily shrink l to minimize length!",
       "Only update `have` when window frequency matches required frequency exactly.",
       "Time: O(N + M), Space: O(128)",
       """from collections import Counter
def minWindow(s, t):
    need = Counter(t); win = {}
    have, req = 0, len(need)
    best, best_l, l = float('inf'), 0, 0
    for r, ch in enumerate(s):
        win[ch] = win.get(ch, 0) + 1
        if ch in need and win[ch] == need[ch]: have += 1
        while have == req:
            if r - l + 1 < best: best = r - l + 1; best_l = l
            lc = s[l]; win[lc] -= 1
            if lc in need and win[lc] < need[lc]: have -= 1
            l += 1
    return "" if best == float('inf') else s[best_l:best_l+best]""",
       """string minWindow(string s, string t) {
    int need[128] = {0}, win[128] = {0}, req = 0, have = 0;
    for (char c : t) if (need[c]++ == 0) req++;
    int l = 0, best = INT_MAX, bestL = 0;
    for (int r = 0; r < s.size(); ++r) {
        char c = s[r];
        if (++win[c] == need[c]) have++;
        while (have == req) {
            if (r - l + 1 < best) { best = r - l + 1; bestL = l; }
            char lc = s[l++];
            if (win[lc]-- == need[lc]) have--;
        }
    }
    return best == INT_MAX ? "" : s.substr(bestL, best);
}"""),

    _p(33, "Sliding Window Maximum", "Sliding Window", "Hard", ["Google", "Razorpay", "Amazon"], "sliding-window-maximum",
       "Maintain a Monotonic Decreasing Deque of INDICES: front is always current window maximum, pop indices <= r - k.",
       "Pop smaller elements from back before pushing r so deque stays strictly decreasing.",
       "Time: O(N), Space: O(K)",
       """from collections import deque
def maxSlidingWindow(nums, k):
    dq, res = deque(), []
    for r, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x: dq.pop()
        dq.append(r)
        if dq[0] <= r - k: dq.popleft()
        if r >= k - 1: res.append(nums[dq[0]])
    return res""",
       """vector<int> maxSlidingWindow(vector<int>& nums, int k) {
    deque<int> dq; vector<int> res;
    for (int r = 0; r < nums.size(); ++r) {
        while (!dq.empty() && nums[dq.back()] <= nums[r]) dq.pop_back();
        dq.push_back(r);
        if (dq.front() <= r - k) dq.pop_front();
        if (r >= k - 1) res.push_back(nums[dq.front()]);
    }
    return res;
}"""),

    _p(34, "Minimum Size Subarray Sum", "Sliding Window", "Medium", ["Microsoft", "Flipkart"], "minimum-size-subarray-sum",
       "All positive integers? Monotonic sum property holds -> expand r to reach >= target, shrink l to minimize length.",
       "Guaranteed O(N) because each index enters and leaves window at most once.",
       "Time: O(N), Space: O(1)",
       """def minSubArrayLen(target, nums):
    l = cur = 0; best = float('inf')
    for r, x in enumerate(nums):
        cur += x
        while cur >= target:
            best = min(best, r - l + 1)
            cur -= nums[l]; l += 1
    return 0 if best == float('inf') else best""",
       """int minSubArrayLen(int target, vector<int>& nums) {
    int l = 0, cur = 0, best = INT_MAX;
    for (int r = 0; r < nums.size(); ++r) {
        cur += nums[r];
        while (cur >= target) { best = min(best, r - l + 1); cur -= nums[l++]; }
    }
    return best == INT_MAX ? 0 : best;
}"""),

    _p(35, "Max Consecutive Ones III", "Sliding Window", "Medium", ["Google", "Zepto"], "max-consecutive-ones-iii",
       "Flip at most K zeros == Longest subarray containing at most K zeros! Track zero_count in sliding window.",
       "Shrink l whenever zero_count > k.",
       "Time: O(N), Space: O(1)",
       """def longestOnes(nums, k):
    l = zeros = best = 0
    for r, x in enumerate(nums):
        if x == 0: zeros += 1
        while zeros > k:
            if nums[l] == 0: zeros -= 1
            l += 1
        best = max(best, r - l + 1)
    return best""",
       """int longestOnes(vector<int>& nums, int k) {
    int l = 0, zeros = 0, best = 0;
    for (int r = 0; r < nums.size(); ++r) {
        if (nums[r] == 0) zeros++;
        while (zeros > k) if (nums[l++] == 0) zeros--;
        best = max(best, r - l + 1);
    }
    return best;
}"""),

    _p(36, "Fruit Into Baskets", "Sliding Window", "Medium", ["Amazon", "Google"], "fruit-into-baskets",
       "Exact alias for 'Longest Subarray With At Most 2 Distinct Numbers' -> HashMap of counts + shrink when len > 2.",
       "Clean O(N) sliding window deleting keys when count reaches 0.",
       "Time: O(N), Space: O(1)",
       """from collections import defaultdict
def totalFruit(fruits):
    cnt, l, best = defaultdict(int), 0, 0
    for r, f in enumerate(fruits):
        cnt[f] += 1
        while len(cnt) > 2:
            cnt[fruits[l]] -= 1
            if cnt[fruits[l]] == 0: del cnt[fruits[l]]
            l += 1
        best = max(best, r - l + 1)
    return best""",
       """int totalFruit(vector<int>& fruits) {
    unordered_map<int, int> cnt;
    int l = 0, best = 0;
    for (int r = 0; r < fruits.size(); ++r) {
        cnt[fruits[r]]++;
        while (cnt.size() > 2) {
            if (--cnt[fruits[l]] == 0) cnt.erase(fruits[l]);
            l++;
        }
        best = max(best, r - l + 1);
    }
    return best;
}"""),

    _p(37, "Subarrays with K Different Integers", "Sliding Window", "Hard", ["Amazon", "Uber"], "subarrays-with-k-different-integers",
       "Exact(K) is hard directly, so use the AtMost Trick: Exact(K) = AtMost(K) - AtMost(K - 1)!",
       "For any window with <= k distinct elements, adding index r creates (r - l + 1) new valid subarrays ending at r.",
       "Time: O(N), Space: O(K)",
       """from collections import defaultdict
def subarraysWithKDistinct(nums, k):
    def atMost(K):
        cnt, l, ans = defaultdict(int), 0, 0
        for r, x in enumerate(nums):
            cnt[x] += 1
            while len(cnt) > K:
                cnt[nums[l]] -= 1
                if cnt[nums[l]] == 0: del cnt[nums[l]]
                l += 1
            ans += r - l + 1
        return ans
    return atMost(k) - atMost(k - 1)""",
       """int subarraysWithKDistinct(vector<int>& nums, int k) {
    auto atMost = [&](int K) {
        unordered_map<int, int> cnt; int l = 0, ans = 0;
        for (int r = 0; r < nums.size(); ++r) {
            cnt[nums[r]]++;
            while (cnt.size() > K) {
                if (--cnt[nums[l]] == 0) cnt.erase(nums[l]);
                l++;
            }
            ans += r - l + 1;
        }
        return ans;
    };
    return atMost(k) - atMost(k - 1);
}"""),

    _p(38, "Find All Anagrams in a String", "Sliding Window", "Medium", ["Microsoft", "CRED"], "find-all-anagrams-in-a-string",
       "Fixed-width sliding window of size len(p): slide across s and record index l whenever window counts == p counts.",
       "Same core mechanic as Permutation in String, collecting starting indices instead of returning bool.",
       "Time: O(N), Space: O(1)",
       """def findAnagrams(s, p):
    if len(p) > len(s): return []
    cp, cs = [0]*26, [0]*26
    for i in range(len(p)): cp[ord(p[i])-97] += 1; cs[ord(s[i])-97] += 1
    res = [0] if cp == cs else []
    for r in range(len(p), len(s)):
        cs[ord(s[r])-97] += 1; cs[ord(s[r-len(p)])-97] -= 1
        if cp == cs: res.append(r - len(p) + 1)
    return res""",
       """vector<int> findAnagrams(string s, string p) {
    if (p.size() > s.size()) return {};
    vector<int> cp(26, 0), cs(26, 0), res;
    for (int i = 0; i < p.size(); ++i) { cp[p[i]-'a']++; cs[s[i]-'a']++; }
    if (cp == cs) res.push_back(0);
    for (int r = p.size(); r < s.size(); ++r) {
        cs[s[r]-'a']++; cs[s[r-p.size()]-'a']--;
        if (cp == cs) res.push_back(r - p.size() + 1);
    }
    return res;
}"""),

    _p(39, "Maximum Points You Can Obtain from Cards", "Sliding Window", "Medium", ["Google", "Flipkart"], "maximum-points-you-can-obtain-from-cards",
       "Picking k cards from ends == Leaving a contiguous subarray of size (n - k) in the middle with MINIMUM sum!",
       "Compute total_sum minus min fixed-window sum of length (n - k).",
       "Time: O(N), Space: O(1)",
       """def maxScore(cardPoints, k):
    n = len(cardPoints); w = n - k
    cur = min_w = sum(cardPoints[:w])
    for r in range(w, n):
        cur += cardPoints[r] - cardPoints[r - w]
        min_w = min(min_w, cur)
    return sum(cardPoints) - min_w""",
       """int maxScore(vector<int>& cardPoints, int k) {
    int n = cardPoints.size(), w = n - k, tot = 0, cur = 0;
    for (int i = 0; i < n; ++i) { tot += cardPoints[i]; if (i < w) cur += cardPoints[i]; }
    int minW = cur;
    for (int r = w; r < n; ++r) { cur += cardPoints[r] - cardPoints[r - w]; minW = min(minW, cur); }
    return tot - minW;
}"""),

    _p(40, "Binary Subarrays With Sum", "Sliding Window", "Medium", ["Uber", "Amazon"], "binary-subarrays-with-sum",
       "All values 0 or 1? Non-negative numbers allow Exact(goal) = AtMost(goal) - AtMost(goal - 1) in O(1) space!",
       "Avoids HashMap overhead of general Subarray Sum Equals K.",
       "Time: O(N), Space: O(1)",
       """def numSubarraysWithSum(nums, goal):
    def atMost(G):
        if G < 0: return 0
        l = s = ans = 0
        for r, x in enumerate(nums):
            s += x
            while s > G: s -= nums[l]; l += 1
            ans += r - l + 1
        return ans
    return atMost(goal) - atMost(goal - 1)""",
       """int numSubarraysWithSum(vector<int>& nums, int goal) {
    auto atMost = [&](int G) {
        if (G < 0) return 0;
        int l = 0, s = 0, ans = 0;
        for (int r = 0; r < nums.size(); ++r) {
            s += nums[r];
            while (s > G) s -= nums[l++];
            ans += r - l + 1;
        }
        return ans;
    };
    return atMost(goal) - atMost(goal - 1);
}"""),

    _p(41, "Frequency of the Most Frequent Element", "Sliding Window", "Medium", ["Google", "Razorpay"], "frequency-of-the-most-frequent-element",
       "Sort first! Target in window [l..r] is ALWAYS nums[r]. Cost to lift all elements in [l..r] to nums[r] is nums[r]*len - win_sum <= k.",
       "If cost > k, shrink l until affordable.",
       "Time: O(N log N), Space: O(1)",
       """def maxFrequency(nums, k):
    nums.sort(); l = total = best = 0
    for r, x in enumerate(nums):
        total += x
        while x * (r - l + 1) - total > k:
            total -= nums[l]; l += 1
        best = max(best, r - l + 1)
    return best""",
       """int maxFrequency(vector<int>& nums, int k) {
    sort(nums.begin(), nums.end());
    long long l = 0, total = 0, best = 0;
    for (long long r = 0; r < nums.size(); ++r) {
        total += nums[r];
        while (nums[r] * (r - l + 1) - total > k) total -= nums[l++];
        best = max(best, r - l + 1);
    }
    return best;
}"""),

    # --- 4. STACK & MONOTONIC STACK (14) ---
    _p(42, "Valid Parentheses", "Stack & Monotonic Stack", "Easy", ["Paytm", "Amazon", "Swiggy"], "valid-parentheses",
       "Map closing bracket -> matching opener. Stack must be non-empty and top must match on close, then empty at end.",
       "LIFO matches innermost valid bracket pair.",
       "Time: O(N), Space: O(N)",
       """def isValid(s):
    mp = {')':'(', '}':'{', ']':'['}; st = []
    for c in s:
        if c in mp:
            if not st or st.pop() != mp[c]: return False
        else: st.append(c)
    return not st""",
       """bool isValid(string s) {
    stack<char> st;
    for (char c : s) {
        if (c == '(' || c == '{' || c == '[') st.push(c);
        else {
            if (st.empty()) return false;
            char top = st.top(); st.pop();
            if ((c == ')' && top != '(') || (c == '}' && top != '{') || (c == ']' && top != '[')) return false;
        }
    }
    return st.empty();
}"""),

    _p(43, "Min Stack", "Stack & Monotonic Stack", "Medium", ["Flipkart", "Razorpay", "Amazon"], "min-stack",
       "Store (val, min_so_far) pairs in stack (or parallel minStack) so getMin() stays O(1) after pops!",
       "Each pushed element carries snapshot of minimum below/at itself.",
       "Time: O(1) all ops, Space: O(N)",
       """class MinStack:
    def __init__(self): self.st = []
    def push(self, v): self.st.append((v, min(v, self.st[-1][1]) if self.st else v))
    def pop(self): self.st.pop()
    def top(self): return self.st[-1][0]
    def getMin(self): return self.st[-1][1]""",
       """class MinStack {
    stack<pair<int,int>> st;
public:
    void push(int v) { st.push({v, st.empty() ? v : min(v, st.top().second)}); }
    void pop() { st.pop(); }
    int top() { return st.top().first; }
    int getMin() { return st.top().second; }
};"""),

    _p(44, "Evaluate Reverse Polish Notation", "Stack & Monotonic Stack", "Medium", ["LinkedIn", "Amazon"], "evaluate-reverse-polish-notation",
       "Watch division & operand order! b = pop(), a = pop(), push (a op b). In Python int(a / b) truncates toward zero!",
       "Note Python '//' floors toward -inf for negatives, so use int(a / b).",
       "Time: O(N), Space: O(N)",
       """def evalRPN(tokens):
    st = []
    for t in tokens:
        if t in "+-*/":
            b, a = st.pop(), st.pop()
            if t == '+': st.append(a + b)
            elif t == '-': st.append(a - b)
            elif t == '*': st.append(a * b)
            else: st.append(int(a / b))
        else: st.append(int(t))
    return st[0]""",
       """int evalRPN(vector<string>& tokens) {
    stack<long long> st;
    for (auto& t : tokens) {
        if (t == "+" || t == "-" || t == "*" || t == "/") {
            long long b = st.top(); st.pop(); long long a = st.top(); st.pop();
            if (t == "+") st.push(a + b); else if (t == "-") st.push(a - b);
            else if (t == "*") st.push(a * b); else st.push(a / b);
        } else st.push(stoll(t));
    }
    return st.top();
}"""),

    _p(45, "Daily Temperatures", "Stack & Monotonic Stack", "Medium", ["Zepto", "Meta", "Google"], "daily-temperatures",
       "Need Next Greater Element distance? Keep monotonic decreasing stack of INDICES; pop when temps[i] > temps[st.top()].",
       "Difference i - idx gives exact days waited.",
       "Time: O(N), Space: O(N)",
       """def dailyTemperatures(temps):
    res, st = [0] * len(temps), []
    for i, t in enumerate(temps):
        while st and temps[st[-1]] < t:
            idx = st.pop()
            res[idx] = i - idx
        st.append(i)
    return res""",
       """vector<int> dailyTemperatures(vector<int>& temps) {
    vector<int> res(temps.size(), 0); stack<int> st;
    for (int i = 0; i < temps.size(); ++i) {
        while (!st.empty() && temps[st.top()] < temps[i]) {
            res[st.top()] = i - st.top(); st.pop();
        }
        st.push(i);
    }
    return res;
}"""),

    _p(46, "Next Greater Element I", "Stack & Monotonic Stack", "Easy", ["Amazon", "Swiggy"], "next-greater-element-i",
       "Precompute next greater for every item in nums2 using decreasing monotonic stack + HashMap, then answer nums1 in O(1).",
       "Classic monotonic decreasing stack lookup table.",
       "Time: O(N + M), Space: O(N)",
       """def nextGreaterElement(nums1, nums2):
    nxt, st = {}, []
    for x in nums2:
        while st and st[-1] < x: nxt[st.pop()] = x
        st.append(x)
    return [nxt.get(x, -1) for x in nums1]""",
       """vector<int> nextGreaterElement(vector<int>& nums1, vector<int>& nums2) {
    unordered_map<int, int> nxt; stack<int> st;
    for (int x : nums2) {
        while (!st.empty() && st.top() < x) { nxt[st.top()] = x; st.pop(); }
        st.push(x);
    }
    vector<int> res;
    for (int x : nums1) res.push_back(nxt.count(x) ? nxt[x] : -1);
    return res;
}"""),

    _p(47, "Next Greater Element II (Circular)", "Stack & Monotonic Stack", "Medium", ["Flipkart", "Microsoft"], "next-greater-element-ii",
       "Circular array trick: loop i from 0 to 2*N - 1 using index i % N! Only push indices during first pass (i < N).",
       "Simulates array concatenated with itself without duplicating memory.",
       "Time: O(N), Space: O(N)",
       """def nextGreaterElements(nums):
    n = len(nums); res, st = [-1] * n, []
    for i in range(2 * n):
        cur = nums[i % n]
        while st and nums[st[-1]] < cur: res[st.pop()] = cur
        if i < n: st.append(i)
    return res""",
       """vector<int> nextGreaterElements(vector<int>& nums) {
    int n = nums.size(); vector<int> res(n, -1); stack<int> st;
    for (int i = 0; i < 2 * n; ++i) {
        int cur = nums[i % n];
        while (!st.empty() && nums[st.top()] < cur) { res[st.top()] = cur; st.pop(); }
        if (i < n) st.push(i);
    }
    return res;
}"""),

    _p(48, "Car Fleet", "Stack & Monotonic Stack", "Medium", ["Google", "Waymo"], "car-fleet",
       "Sort cars descending by start position: if time_to_target(car) <= lead_fleet_time, it catches up and merges into lead fleet!",
       "Faster trailing cars slow down to match slower leading car, never passing.",
       "Time: O(N log N), Space: O(N)",
       """def carFleet(target, position, speed):
    cars = sorted(zip(position, speed), reverse=True)
    fleets = cur_max_t = 0
    for pos, spd in cars:
        t = (target - pos) / spd
        if t > cur_max_t:
            fleets += 1; cur_max_t = t
    return fleets""",
       """int carFleet(int target, vector<int>& pos, vector<int>& spd) {
    vector<pair<int, double>> cars;
    for (int i = 0; i < pos.size(); ++i)
        cars.push_back({pos[i], (double)(target - pos[i]) / spd[i]});
    sort(cars.rbegin(), cars.rend());
    int fleets = 0; double cur = 0;
    for (auto& [p, t] : cars) if (t > cur) { fleets++; cur = t; }
    return fleets;
}"""),

    _p(49, "Largest Rectangle in Histogram", "Stack & Monotonic Stack", "Hard", ["Atlassian", "Amazon", "CRED"], "largest-rectangle-in-histogram",
       "Monotonic Increasing Stack + Sentinel 0 at end: when popping height h, right boundary is i and left boundary is new stack top!",
       "Width = i if stack empty else (i - st[-1] - 1).",
       "Time: O(N), Space: O(N)",
       """def largestRectangleArea(heights):
    st, best = [], 0
    for i, h in enumerate(heights + [0]):
        while st and heights[st[-1]] >= h:
            H = heights[st.pop()]
            W = i if not st else i - st[-1] - 1
            best = max(best, H * W)
        st.append(i)
    return best""",
       """int largestRectangleArea(vector<int>& heights) {
    stack<int> st; int best = 0, n = heights.size();
    for (int i = 0; i <= n; ++i) {
        int h = (i == n) ? 0 : heights[i];
        while (!st.empty() && heights[st.top()] >= h) {
            int H = heights[st.top()]; st.pop();
            int W = st.empty() ? i : i - st.top() - 1;
            best = max(best, H * W);
        }
        st.push(i);
    }
    return best;
}"""),

    _p(50, "Asteroid Collision", "Stack & Monotonic Stack", "Medium", ["Razorpay", "Lyft", "Amazon"], "asteroid-collision",
       "Collision ONLY happens when stack top > 0 (moving right) AND incoming asteroid < 0 (moving left)!",
       "While colliding: smaller explodes; equal both explode; track alive flag for incoming.",
       "Time: O(N), Space: O(N)",
       """def asteroidCollision(asteroids):
    st = []
    for a in asteroids:
        while st and a < 0 < st[-1]:
            if st[-1] < -a: st.pop(); continue
            elif st[-1] == -a: st.pop()
            break
        else:
            st.append(a)
    return st""",
       """vector<int> asteroidCollision(vector<int>& asteroids) {
    vector<int> st;
    for (int a : asteroids) {
        bool alive = true;
        while (alive && !st.empty() && a < 0 && st.back() > 0) {
            if (st.back() < -a) st.pop_back();
            else { if (st.back() == -a) st.pop_back(); alive = false; }
        }
        if (alive) st.push_back(a);
    }
    return st;
}"""),

    _p(51, "Remove K Digits", "Stack & Monotonic Stack", "Medium", ["Microsoft", "PhonePe"], "remove-k-digits",
       "Greedy Monotonic Increasing Stack: pop larger preceding digits while k > 0, trim leftover from end if k > 0, strip leading 0s.",
       "Removing a larger digit from a more significant position always yields a strictly smaller number.",
       "Time: O(N), Space: O(N)",
       """def removeKdigits(num, k):
    st = []
    for c in num:
        while k and st and st[-1] > c: st.pop(); k -= 1
        st.append(c)
    res = "".join(st[:len(st) - k]).lstrip('0')
    return res or "0" """,
       """string removeKdigits(string num, int k) {
    string st;
    for (char c : num) {
        while (k > 0 && !st.empty() && st.back() > c) { st.pop_back(); k--; }
        if (!st.empty() || c != '0') st.push_back(c);
    }
    while (k-- > 0 && !st.empty()) st.pop_back();
    return st.empty() ? "0" : st;
}"""),

    _p(52, "Sum of Subarray Minimums", "Stack & Monotonic Stack", "Medium", ["Amazon", "Google"], "sum-of-subarray-minimums",
       "Contribution Trick: instead of inspecting all subarrays, count (left_choices * right_choices * arr[i]) where arr[i] is the min!",
       "Use strict '<' on one side and '<=' on the other to avoid double counting equal minimums.",
       "Time: O(N), Space: O(N)",
       """def sumSubarrayMins(arr):
    MOD, st, ans = 10**9 + 7, [], 0
    for i, x in enumerate(arr + [0]):
        while st and arr[st[-1]] >= x:
            mid = st.pop()
            left = mid - (st[-1] if st else -1)
            right = i - mid
            ans = (ans + arr[mid] * left * right) % MOD
        st.append(i)
    return ans""",
       """int sumSubarrayMins(vector<int>& arr) {
    long long MOD = 1e9 + 7, ans = 0; stack<int> st; int n = arr.size();
    for (int i = 0; i <= n; ++i) {
        int x = (i == n) ? 0 : arr[i];
        while (!st.empty() && arr[st.top()] >= x) {
            int mid = st.top(); st.pop();
            long long left = mid - (st.empty() ? -1 : st.top());
            long long right = i - mid;
            ans = (ans + arr[mid] * left * right) % MOD;
        }
        st.push(i);
    }
    return ans;
}"""),

    _p(53, "Decode String", "Stack & Monotonic Stack", "Medium", ["Google", "Bloomberg", "Zepto"], "decode-string",
       "Nested brackets -> stack stores (previous_string, repeat_count). On ']', pop prev + curr * repeat!",
       "Clean iterative parser handles arbitrary nesting depth cleanly.",
       "Time: O(OutputLen), Space: O(N)",
       """def decodeString(s):
    st, cur, num = [], "", 0
    for c in s:
        if c.isdigit(): num = num * 10 + int(c)
        elif c == '[': st.append((cur, num)); cur, num = "", 0
        elif c == ']':
            prev, k = st.pop()
            cur = prev + cur * k
        else: cur += c
    return cur""",
       """string decodeString(string s) {
    stack<pair<string, int>> st; string cur = ""; int num = 0;
    for (char c : s) {
        if (isdigit(c)) num = num * 10 + (c - '0');
        else if (c == '[') { st.push({cur, num}); cur = ""; num = 0; }
        else if (c == ']') {
            auto [prev, k] = st.top(); st.pop();
            string rep; while (k--) rep += cur;
            cur = prev + rep;
        } else cur += c;
    }
    return cur;
}"""),

    _p(54, "Online Stock Span", "Stack & Monotonic Stack", "Medium", ["Flipkart", "Microsoft"], "online-stock-span",
       "Store (price, span) on decreasing stack: while stack top price <= today's price, absorb its accumulated span!",
       "Amortized O(1) per next() call since each item is pushed and popped once.",
       "Time: O(1) amortized, Space: O(N)",
       """class StockSpanner:
    def __init__(self): self.st = []
    def next(self, price):
        span = 1
        while self.st and self.st[-1][0] <= price: span += self.st.pop()[1]
        self.st.append((price, span))
        return span""",
       """class StockSpanner {
    stack<pair<int,int>> st;
public:
    int next(int price) {
        int span = 1;
        while (!st.empty() && st.top().first <= price) { span += st.top().second; st.pop(); }
        st.push({price, span});
        return span;
    }
};"""),

    _p(55, "Basic Calculator II", "Stack & Monotonic Stack", "Medium", ["Meta", "Amazon"], "basic-calculator-ii",
       "Track previous operator `op`: push +num / -num immediately; evaluate * and / directly against stack top!",
       "Handles operator precedence cleanly without parentheses; sum stack at end.",
       "Time: O(N), Space: O(N)",
       """def calculate(s):
    st, num, op = [], 0, '+'
    for i, c in enumerate(s):
        if c.isdigit(): num = num * 10 + int(c)
        if (not c.isdigit() and c != ' ') or i == len(s) - 1:
            if op == '+': st.append(num)
            elif op == '-': st.append(-num)
            elif op == '*': st.append(st.pop() * num)
            elif op == '/': st.append(int(st.pop() / num))
            op, num = c, 0
    return sum(st)""",
       """int calculate(string s) {
    stack<int> st; long num = 0; char op = '+';
    for (int i = 0; i < s.size(); ++i) {
        if (isdigit(s[i])) num = num * 10 + (s[i] - '0');
        if ((!isdigit(s[i]) && s[i] != ' ') || i == s.size() - 1) {
            if (op == '+') st.push(num);
            else if (op == '-') st.push(-num);
            else if (op == '*') { int t = st.top(); st.pop(); st.push(t * num); }
            else if (op == '/') { int t = st.top(); st.pop(); st.push(t / num); }
            op = s[i]; num = 0;
        }
    }
    int ans = 0; while (!st.empty()) { ans += st.top(); st.pop(); } return ans;
}"""),
]
