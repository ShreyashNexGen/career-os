from .dsa_part1 import _p

DSA_PART2 = [
    # --- 5. BINARY SEARCH & BS ON ANSWER (15) ---
    _p(56, "Binary Search", "Binary Search & BS on Answer", "Easy", ["Google", "Microsoft"], "binary-search",
       "Standard half-interval elimination: mid = l + (r - l) // 2 prevents integer overflow in C++.",
       "Compare nums[mid] with target and shrink inclusive search space [l, r].",
       "Time: O(log N), Space: O(1)",
       """def search(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if nums[m] == target: return m
        if nums[m] < target: l = m + 1
        else: r = m - 1
    return -1""",
       """int search(vector<int>& nums, int target) {
    int l = 0, r = nums.size() - 1;
    while (l <= r) {
        int m = l + (r - l) / 2;
        if (nums[m] == target) return m;
        if (nums[m] < target) l = m + 1; else r = m - 1;
    }
    return -1;
}"""),

    _p(57, "Search a 2D Matrix", "Binary Search & BS on Answer", "Medium", ["Amazon", "Flipkart"], "search-a-2d-matrix",
       "Sorted row-major matrix == virtual 1D sorted array of size R * C! Map index mid -> (mid // C, mid % C).",
       "Single binary search in O(log(R * C)) instead of two separate searches.",
       "Time: O(log(R*C)), Space: O(1)",
       """def searchMatrix(m, target):
    R, C = len(m), len(m[0])
    l, r = 0, R * C - 1
    while l <= r:
        mid = (l + r) // 2
        v = m[mid // C][mid % C]
        if v == target: return True
        if v < target: l = mid + 1
        else: r = mid - 1
    return False""",
       """bool searchMatrix(vector<vector<int>>& m, int target) {
    int R = m.size(), C = m[0].size(), l = 0, r = R * C - 1;
    while (l <= r) {
        int mid = l + (r - l) / 2, v = m[mid / C][mid % C];
        if (v == target) return true;
        if (v < target) l = mid + 1; else r = mid - 1;
    }
    return false;
}"""),

    _p(58, "Find First and Last Position of Element", "Binary Search & BS on Answer", "Medium", ["LinkedIn", "Swiggy"], "find-first-and-last-position-of-element-in-sorted-array",
       "Run two biased binary searches: left-bound keeps going left on match (`r = m - 1`), right-bound keeps going right (`l = m + 1`).",
       "Clean lower_bound / upper_bound pattern without linear scanning.",
       "Time: O(log N), Space: O(1)",
       """def searchRange(nums, target):
    def bound(left):
        l, r, idx = 0, len(nums) - 1, -1
        while l <= r:
            m = (l + r) // 2
            if nums[m] == target:
                idx = m
                if left: r = m - 1
                else: l = m + 1
            elif nums[m] < target: l = m + 1
            else: r = m - 1
        return idx
    return [bound(True), bound(False)]""",
       """vector<int> searchRange(vector<int>& nums, int target) {
    auto bound = [&](bool left) {
        int l = 0, r = (int)nums.size() - 1, idx = -1;
        while (l <= r) {
            int m = l + (r - l) / 2;
            if (nums[m] == target) { idx = m; if (left) r = m - 1; else l = m + 1; }
            else if (nums[m] < target) l = m + 1; else r = m - 1;
        }
        return idx;
    };
    return {bound(true), bound(false)};
}"""),

    _p(59, "Search in Rotated Sorted Array", "Binary Search & BS on Answer", "Medium", ["Razorpay", "Amazon", "Zepto"], "search-in-rotated-sorted-array",
       "At least ONE half [l..m] or [m..r] is ALWAYS strictly sorted! Identify the sorted half first, then check if target lies inside it.",
       "Eliminates half the search space each iteration in rotated unique array.",
       "Time: O(log N), Space: O(1)",
       """def searchRotated(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if nums[m] == target: return m
        if nums[l] <= nums[m]:
            if nums[l] <= target < nums[m]: r = m - 1
            else: l = m + 1
        else:
            if nums[m] < target <= nums[r]: l = m + 1
            else: r = m - 1
    return -1""",
       """int search(vector<int>& nums, int target) {
    int l = 0, r = nums.size() - 1;
    while (l <= r) {
        int m = l + (r - l) / 2;
        if (nums[m] == target) return m;
        if (nums[l] <= nums[m]) {
            if (nums[l] <= target && target < nums[m]) r = m - 1;
            else l = m + 1;
        } else {
            if (nums[m] < target && target <= nums[r]) l = m + 1;
            else r = m - 1;
        }
    }
    return -1;
}"""),

    _p(60, "Find Minimum in Rotated Sorted Array", "Binary Search & BS on Answer", "Medium", ["Microsoft", "CRED"], "find-minimum-in-rotated-sorted-array",
       "Compare nums[m] with nums[r]: if nums[m] > nums[r], pivot MUST be strictly right (l = m + 1); else min is at or left of m (r = m).",
       "Clean loop condition l < r converges directly onto minimum element.",
       "Time: O(log N), Space: O(1)",
       """def findMin(nums):
    l, r = 0, len(nums) - 1
    while l < r:
        m = (l + r) // 2
        if nums[m] > nums[r]: l = m + 1
        else: r = m
    return nums[l]""",
       """int findMin(vector<int>& nums) {
    int l = 0, r = nums.size() - 1;
    while (l < r) {
        int m = l + (r - l) / 2;
        if (nums[m] > nums[r]) l = m + 1; else r = m;
    }
    return nums[l];
}"""),

    _p(61, "Find Peak Element", "Binary Search & BS on Answer", "Medium", ["Google", "Meta"], "find-peak-element",
       "Uphill Climb Trick: if nums[m] < nums[m + 1], a peak is GUARANTEED on the right (l = m + 1); else on left (r = m).",
       "Because boundaries are -inf, following any increasing slope must hit a local peak.",
       "Time: O(log N), Space: O(1)",
       """def findPeakElement(nums):
    l, r = 0, len(nums) - 1
    while l < r:
        m = (l + r) // 2
        if nums[m] < nums[m + 1]: l = m + 1
        else: r = m
    return l""",
       """int findPeakElement(vector<int>& nums) {
    int l = 0, r = nums.size() - 1;
    while (l < r) {
        int m = l + (r - l) / 2;
        if (nums[m] < nums[m + 1]) l = m + 1; else r = m;
    }
    return l;
}"""),

    _p(62, "Koko Eating Bananas", "Binary Search & BS on Answer", "Medium", ["Amazon", "Swiggy", "Flipkart"], "koko-eating-bananas",
       "BS on Answer: speed k in [1..max(piles)] is monotonic! Compute ceil(p / k) via (p + k - 1) // k.",
       "Smallest feasible k where sum of hours <= h.",
       "Time: O(N log M), Space: O(1)",
       """def minEatingSpeed(piles, h):
    l, r = 1, max(piles)
    while l < r:
        m = (l + r) // 2
        if sum((p + m - 1) // m for p in piles) <= h: r = m
        else: l = m + 1
    return l""",
       """int minEatingSpeed(vector<int>& piles, int h) {
    int l = 1, r = *max_element(piles.begin(), piles.end());
    while (l < r) {
        int m = l + (r - l) / 2;
        long long hrs = 0;
        for (int p : piles) hrs += (p + m - 1) / m;
        if (hrs <= h) r = m; else l = m + 1;
    }
    return l;
}"""),

    _p(63, "Capacity To Ship Packages Within D Days", "Binary Search & BS on Answer", "Medium", ["Zepto", "Amazon"], "capacity-to-ship-packages-within-d-days",
       "BS on Answer: capacity range is [max(weights), sum(weights)]. Greedy pack each day until next package overflows.",
       "Identical pattern to Book Allocation / Painter Partition!",
       "Time: O(N log S), Space: O(1)",
       """def shipWithinDays(weights, days):
    l, r = max(weights), sum(weights)
    while l < r:
        cap = (l + r) // 2; d, cur = 1, 0
        for w in weights:
            if cur + w > cap: d += 1; cur = 0
            cur += w
        if d <= days: r = cap
        else: l = cap + 1
    return l""",
       """int shipWithinDays(vector<int>& weights, int days) {
    int l = *max_element(weights.begin(), weights.end()), r = accumulate(weights.begin(), weights.end(), 0);
    while (l < r) {
        int cap = l + (r - l) / 2, d = 1, cur = 0;
        for (int w : weights) {
            if (cur + w > cap) { d++; cur = 0; }
            cur += w;
        }
        if (d <= days) r = cap; else l = cap + 1;
    }
    return l;
}"""),

    _p(64, "Split Array Largest Sum (Book Allocation)", "Binary Search & BS on Answer", "Hard", ["Google", "Atlassian", "Amazon"], "split-array-largest-sum",
       "Minimize the maximum subarray sum across k splits == Binary search on max_sum in [max(nums), sum(nums)].",
       "Greedily fill current partition until adding next element > mid.",
       "Time: O(N log S), Space: O(1)",
       """def splitArray(nums, k):
    l, r = max(nums), sum(nums)
    while l < r:
        m = (l + r) // 2; parts, cur = 1, 0
        for x in nums:
            if cur + x > m: parts += 1; cur = 0
            cur += x
        if parts <= k: r = m
        else: l = m + 1
    return l""",
       """int splitArray(vector<int>& nums, int k) {
    int l = *max_element(nums.begin(), nums.end()), r = accumulate(nums.begin(), nums.end(), 0);
    while (l < r) {
        int m = l + (r - l) / 2, parts = 1, cur = 0;
        for (int x : nums) { if (cur + x > m) { parts++; cur = 0; } cur += x; }
        if (parts <= k) r = m; else l = m + 1;
    }
    return l;
}"""),

    _p(65, "Median of Two Sorted Arrays", "Binary Search & BS on Answer", "Hard", ["Google", "CRED", "Razorpay"], "median-of-two-sorted-arrays",
       "Binary search partition cut i on the SMALLER array A; j = half - i on B. Valid cut iff A[i-1] <= B[j] and B[j-1] <= A[i]!",
       "Avoids merging in O(M+N); guarantees O(log(min(M, N))).",
       "Time: O(log min(M,N)), Space: O(1)",
       """def findMedianSortedArrays(A, B):
    if len(A) > len(B): A, B = B, A
    m, n = len(A), len(B); half = (m + n + 1) // 2
    l, r = 0, m
    while l <= r:
        i = (l + r) // 2; j = half - i
        AL = A[i-1] if i > 0 else float('-inf'); AR = A[i] if i < m else float('inf')
        BL = B[j-1] if j > 0 else float('-inf'); BR = B[j] if j < n else float('inf')
        if AL <= BR and BL <= AR:
            if (m + n) % 2: return max(AL, BL)
            return (max(AL, BL) + min(AR, BR)) / 2
        elif AL > BR: r = i - 1
        else: l = i + 1""",
       """double findMedianSortedArrays(vector<int>& A, vector<int>& B) {
    if (A.size() > B.size()) return findMedianSortedArrays(B, A);
    int m = A.size(), n = B.size(), half = (m + n + 1) / 2, l = 0, r = m;
    while (l <= r) {
        int i = (l + r) / 2, j = half - i;
        int AL = i > 0 ? A[i-1] : INT_MIN, AR = i < m ? A[i] : INT_MAX;
        int BL = j > 0 ? B[j-1] : INT_MIN, BR = j < n ? B[j] : INT_MAX;
        if (AL <= BR && BL <= AR) {
            if ((m + n) % 2) return max(AL, BL);
            return (max(AL, BL) + min(AR, BR)) / 2.0;
        } else if (AL > BR) r = i - 1; else l = i + 1;
    }
    return 0.0;
}"""),

    _p(66, "Time Based Key-Value Store", "Binary Search & BS on Answer", "Medium", ["PhonePe", "Stripe", "Amazon"], "time-based-key-value-store",
       "Timestamps per key are strictly increasing -> append (timestamp, val) to list and binary search upper_bound!",
       "Avoids tree map overhead; O(1) set and O(log K) get.",
       "Time: O(1) set / O(log K) get, Space: O(N)",
       """from collections import defaultdict
class TimeMap:
    def __init__(self): self.store = defaultdict(list)
    def set(self, k, v, t): self.store[k].append((t, v))
    def get(self, k, t):
        arr = self.store[k]; l, r, res = 0, len(arr) - 1, ""
        while l <= r:
            m = (l + r) // 2
            if arr[m][0] <= t: res = arr[m][1]; l = m + 1
            else: r = m - 1
        return res""",
       """class TimeMap {
    unordered_map<string, vector<pair<int, string>>> mp;
public:
    void set(string k, string v, int t) { mp[k].push_back({t, v}); }
    string get(string k, int t) {
        auto& arr = mp[k]; int l = 0, r = (int)arr.size() - 1; string res = "";
        while (l <= r) {
            int m = l + (r - l) / 2;
            if (arr[m].first <= t) { res = arr[m].second; l = m + 1; }
            else r = m - 1;
        }
        return res;
    }
};"""),

    _p(67, "Single Element in a Sorted Array", "Binary Search & BS on Answer", "Medium", ["Amazon", "Google"], "single-element-in-a-sorted-array",
       "Index Parity Trick: before the single element, pairs start at EVEN index! Force mid even (`if m % 2: m -= 1`); check nums[m] == nums[m+1].",
       "If pair starts cleanly at even m, single element is on the right (l = m + 2); else left (r = m).",
       "Time: O(log N), Space: O(1)",
       """def singleNonDuplicate(nums):
    l, r = 0, len(nums) - 1
    while l < r:
        m = (l + r) // 2
        if m % 2 == 1: m -= 1
        if nums[m] == nums[m + 1]: l = m + 2
        else: r = m
    return nums[l]""",
       """int singleNonDuplicate(vector<int>& nums) {
    int l = 0, r = nums.size() - 1;
    while (l < r) {
        int m = l + (r - l) / 2;
        if (m % 2 == 1) m--;
        if (nums[m] == nums[m + 1]) l = m + 2; else r = m;
    }
    return nums[l];
}"""),

    _p(68, "Aggressive Cows / Magnetic Force Between Two Balls", "Binary Search & BS on Answer", "Medium", ["Flipkart", "Razorpay", "Amazon"], "magnetic-force-between-two-balls",
       "Maximize minimum distance -> sort positions, BS on distance `d`, greedily place balls/cows whenever pos - last >= d.",
       "Classic Indian product company BS on Answer favorite.",
       "Time: O(N log N + N log D), Space: O(1)",
       """def maxDistance(position, m):
    position.sort()
    l, r, ans = 1, position[-1] - position[0], 0
    while l <= r:
        mid = (l + r) // 2; cnt, last = 1, position[0]
        for p in position[1:]:
            if p - last >= mid: cnt += 1; last = p
        if cnt >= m: ans = mid; l = mid + 1
        else: r = mid - 1
    return ans""",
       """int maxDistance(vector<int>& pos, int m) {
    sort(pos.begin(), pos.end());
    int l = 1, r = pos.back() - pos[0], ans = 0;
    while (l <= r) {
        int mid = l + (r - l) / 2, cnt = 1, last = pos[0];
        for (int i = 1; i < pos.size(); ++i)
            if (pos[i] - last >= mid) { cnt++; last = pos[i]; }
        if (cnt >= m) { ans = mid; l = mid + 1; } else r = mid - 1;
    }
    return ans;
}"""),

    _p(69, "Minimum Number of Days to Make m Bouquets", "Binary Search & BS on Answer", "Medium", ["Google", "Adobe"], "minimum-number-of-days-to-make-m-bouquets",
       "Early return -1 if m * k > len(bloomDay); otherwise BS day d in [min, max] counting consecutive bloomed runs of size k.",
       "Reset consecutive counter whenever bloomDay[i] > day.",
       "Time: O(N log D), Space: O(1)",
       """def minDays(bloomDay, m, k):
    if m * k > len(bloomDay): return -1
    l, r = min(bloomDay), max(bloomDay)
    while l < r:
        mid = (l + r) // 2; b = adj = 0
        for x in bloomDay:
            adj = adj + 1 if x <= mid else 0
            if adj == k: b += 1; adj = 0
        if b >= m: r = mid
        else: l = mid + 1
    return l""",
       """int minDays(vector<int>& bloomDay, int m, int k) {
    if ((long long)m * k > bloomDay.size()) return -1;
    int l = *min_element(bloomDay.begin(), bloomDay.end()), r = *max_element(bloomDay.begin(), bloomDay.end());
    while (l < r) {
        int mid = l + (r - l) / 2, b = 0, adj = 0;
        for (int x : bloomDay) {
            adj = (x <= mid) ? adj + 1 : 0;
            if (adj == k) { b++; adj = 0; }
        }
        if (b >= m) r = mid; else l = mid + 1;
    }
    return l;
}"""),

    _p(70, "Find Kth Smallest Element in a Sorted Matrix", "Binary Search & BS on Answer", "Medium", ["Amazon", "Uber"], "kth-smallest-element-in-a-sorted-matrix",
       "BS on VALUE range [matrix[0][0], matrix[n-1][n-1]]! Count <= mid in O(R + C) from bottom-left corner!",
       "Avoids heap O(K log N) space by running value-space binary search in O(1) space.",
       "Time: O(N log(Max-Min)), Space: O(1)",
       """def kthSmallest(matrix, k):
    n = len(matrix); l, r = matrix[0][0], matrix[-1][-1]
    def countLE(mid):
        row, col, cnt = n - 1, 0, 0
        while row >= 0 and col < n:
            if matrix[row][col] <= mid: cnt += row + 1; col += 1
            else: row -= 1
        return cnt
    while l < r:
        m = (l + r) // 2
        if countLE(m) < k: l = m + 1
        else: r = m
    return l""",
       """int kthSmallest(vector<vector<int>>& mat, int k) {
    int n = mat.size(), l = mat[0][0], r = mat[n-1][n-1];
    auto countLE = [&](int mid) {
        int row = n - 1, col = 0, cnt = 0;
        while (row >= 0 && col < n) {
            if (mat[row][col] <= mid) { cnt += row + 1; col++; }
            else row--;
        }
        return cnt;
    };
    while (l < r) {
        int m = l + (r - l) / 2;
        if (countLE(m) < k) l = m + 1; else r = m;
    }
    return l;
}"""),

    # --- 6. LINKED LIST & FAST/SLOW POINTERS (12) ---
    _p(71, "Reverse Linked List", "Linked List & Fast/Slow", "Easy", ["Paytm", "Amazon", "Microsoft"], "reverse-linked-list",
       "Three pointers (prev, cur, nxt): save cur.next, flip cur.next = prev, advance prev & cur.",
       "Iterative O(1) space beats recursive O(N) stack in production.",
       "Time: O(N), Space: O(1)",
       """def reverseList(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    return prev""",
       """ListNode* reverseList(ListNode* head) {
    ListNode *prev = nullptr, *cur = head;
    while (cur) {
        ListNode* nxt = cur->next;
        cur->next = prev;
        prev = cur; cur = nxt;
    }
    return prev;
}"""),

    _p(72, "Merge Two Sorted Lists", "Linked List & Fast/Slow", "Easy", ["Flipkart", "Amazon"], "merge-two-sorted-lists",
       "Always create a Dummy head node so you never need special-case edge checks for empty head!",
       "Compare l1.val and l2.val, link smaller to tail, append leftover list at end.",
       "Time: O(N + M), Space: O(1)",
       """def mergeTwoLists(l1, l2):
    dummy = tail = ListNode()
    while l1 and l2:
        if l1.val < l2.val: tail.next, l1 = l1, l1.next
        else: tail.next, l2 = l2, l2.next
        tail = tail.next
    tail.next = l1 or l2
    return dummy.next""",
       """ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {
    ListNode dummy(0), *tail = &dummy;
    while (l1 && l2) {
        if (l1->val < l2->val) { tail->next = l1; l1 = l1->next; }
        else { tail->next = l2; l2 = l2->next; }
        tail = tail->next;
    }
    tail->next = l1 ? l1 : l2;
    return dummy.next;
}"""),

    _p(73, "Linked List Cycle", "Linked List & Fast/Slow", "Easy", ["Swiggy", "Microsoft"], "linked-list-cycle",
       "Floyd's Tortoise & Hare: slow moves 1 step, fast moves 2 steps -> guaranteed collision iff cycle exists.",
       "O(1) space without HashSet.",
       "Time: O(N), Space: O(1)",
       """def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow == fast: return True
    return False""",
       """bool hasCycle(ListNode *head) {
    ListNode *s = head, *f = head;
    while (f && f->next) {
        s = s->next; f = f->next->next;
        if (s == f) return true;
    }
    return false;
}"""),

    _p(74, "Linked List Cycle II (Find Cycle Start)", "Linked List & Fast/Slow", "Medium", ["Razorpay", "Amazon"], "linked-list-cycle-ii",
       "After slow == fast inside cycle, reset slow = head and advance BOTH slow & fast by 1 step -> they meet at exact cycle entry!",
       "Distance math: head->entry equals meeting->entry mod cycle length.",
       "Time: O(N), Space: O(1)",
       """def detectCycle(head):
    s = f = head
    while f and f.next:
        s, f = s.next, f.next.next
        if s == f:
            s = head
            while s != f: s, f = s.next, f.next
            return s
    return None""",
       """ListNode *detectCycle(ListNode *head) {
    ListNode *s = head, *f = head;
    while (f && f->next) {
        s = s->next; f = f->next->next;
        if (s == f) {
            s = head;
            while (s != f) { s = s->next; f = f->next; }
            return s;
        }
    }
    return nullptr;
}"""),

    _p(75, "Reorder List", "Linked List & Fast/Slow", "Medium", ["Zepto", "Meta", "Amazon"], "reorder-list",
       "Three classic primitives combined: (1) Find mid via fast/slow, (2) Reverse second half, (3) Zip/merge alternating nodes!",
       "Cut mid.next = None before reversing second half.",
       "Time: O(N), Space: O(1)",
       """def reorderList(head):
    s, f = head, head.next
    while f and f.next: s, f = s.next, f.next.next
    prev, cur = None, s.next
    s.next = None
    while cur: nxt = cur.next; cur.next = prev; prev, cur = cur, nxt
    first, second = head, prev
    while second:
        t1, t2 = first.next, second.next
        first.next = second; second.next = t1
        first, second = t1, t2""",
       """void reorderList(ListNode* head) {
    ListNode *s = head, *f = head->next;
    while (f && f->next) { s = s->next; f = f->next->next; }
    ListNode *prev = nullptr, *cur = s->next; s->next = nullptr;
    while (cur) { ListNode* nxt = cur->next; cur->next = prev; prev = cur; cur = nxt; }
    ListNode *first = head, *second = prev;
    while (second) {
        ListNode *t1 = first->next, *t2 = second->next;
        first->next = second; second->next = t1;
        first = t1; second = t2;
    }
}"""),

    _p(76, "Remove Nth Node From End of List", "Linked List & Fast/Slow", "Medium", ["Flipkart", "Microsoft"], "remove-nth-node-from-end-of-list",
       "Dummy node + Gap Trick: advance fast n steps first, then move slow & fast together until fast reaches last node!",
       "Slow stops right BEFORE target node for O(1) deletion in single pass.",
       "Time: O(N), Space: O(1)",
       """def removeNthFromEnd(head, n):
    dummy = ListNode(0, head)
    slow = fast = dummy
    for _ in range(n): fast = fast.next
    while fast.next: slow, fast = slow.next, fast.next
    slow.next = slow.next.next
    return dummy.next""",
       """ListNode* removeNthFromEnd(ListNode* head, int n) {
    ListNode dummy(0, head), *s = &dummy, *f = &dummy;
    for (int i = 0; i < n; ++i) f = f->next;
    while (f->next) { s = s->next; f = f->next; }
    s->next = s->next->next;
    return dummy.next;
}"""),

    _p(77, "Copy List with Random Pointer", "Linked List & Fast/Slow", "Medium", ["CRED", "Amazon", "Bloomberg"], "copy-list-with-random-pointer",
       "Two-pass HashMap (old_node -> new_node) OR O(1) space interleaving trick (clone right next to original).",
       "HashMap version is cleanest in interviews: pass 1 clones nodes, pass 2 wires .next and .random.",
       "Time: O(N), Space: O(N)",
       """def copyRandomList(head):
    if not head: return None
    mp = {None: None}
    cur = head
    while cur: mp[cur] = Node(cur.val); cur = cur.next
    cur = head
    while cur:
        mp[cur].next = mp[cur.next]
        mp[cur].random = mp[cur.random]
        cur = cur.next
    return mp[head]""",
       """Node* copyRandomList(Node* head) {
    if (!head) return nullptr;
    unordered_map<Node*, Node*> mp;
    for (Node* c = head; c; c = c->next) mp[c] = new Node(c->val);
    for (Node* c = head; c; c = c->next) {
        mp[c]->next = mp[c->next];
        mp[c]->random = mp[c->random];
    }
    return mp[head];
}"""),

    _p(78, "Add Two Numbers", "Linked List & Fast/Slow", "Medium", ["Microsoft", "Amazon", "Paytm"], "add-two-numbers",
       "Lists are already reversed (LSB first)! Loop while l1 or l2 or carry != 0, keeping carry = total // 10.",
       "Dummy node collects digit nodes val = total % 10.",
       "Time: O(max(N,M)), Space: O(max(N,M))",
       """def addTwoNumbers(l1, l2):
    dummy = cur = ListNode(); carry = 0
    while l1 or l2 or carry:
        v = carry + (l1.val if l1 else 0) + (l2.val if l2 else 0)
        carry, d = divmod(v, 10)
        cur.next = ListNode(d); cur = cur.next
        if l1: l1 = l1.next
        if l2: l2 = l2.next
    return dummy.next""",
       """ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
    ListNode dummy(0), *cur = &dummy; int carry = 0;
    while (l1 || l2 || carry) {
        int s = carry + (l1 ? l1->val : 0) + (l2 ? l2->val : 0);
        carry = s / 10; cur->next = new ListNode(s % 10); cur = cur->next;
        if (l1) l1 = l1->next; if (l2) l2 = l2->next;
    }
    return dummy.next;
}"""),

    _p(79, "Find the Duplicate Number", "Linked List & Fast/Slow", "Medium", ["Amazon", "Google", "Razorpay"], "find-the-duplicate-number",
       "Treat array values [1..N] as linked list next pointers (idx -> nums[idx])! Duplicate value creates a cycle entry -> Floyd's Cycle II!",
       "Solves in O(N) time and O(1) space without modifying input array.",
       "Time: O(N), Space: O(1)",
       """def findDuplicate(nums):
    s = f = 0
    while True:
        s, f = nums[s], nums[nums[f]]
        if s == f: break
    s = 0
    while s != f: s, f = nums[s], nums[f]
    return s""",
       """int findDuplicate(vector<int>& nums) {
    int s = 0, f = 0;
    do { s = nums[s]; f = nums[nums[f]]; } while (s != f);
    s = 0;
    while (s != f) { s = nums[s]; f = nums[f]; }
    return s;
}"""),

    _p(80, "LRU Cache", "Linked List & Fast/Slow", "Medium", ["Atlassian", "Razorpay", "Zepto", "Amazon"], "lru-cache",
       "HashMap (key -> Node) + Doubly Linked List with dummy head & tail -> O(1) get, put, move-to-front, and evict-LRU!",
       "Top #1 most frequently asked system/coding question at Indian startups.",
       "Time: O(1), Space: O(Capacity)",
       """class Node:
    def __init__(self, k=0, v=0): self.k, self.v, self.prev, self.next = k, v, None, None
class LRUCache:
    def __init__(self, cap):
        self.cap, self.mp = cap, {}
        self.head, self.tail = Node(), Node()
        self.head.next, self.tail.prev = self.tail, self.head
    def _rem(self, n): n.prev.next, n.next.prev = n.next, n.prev
    def _add(self, n):
        n.next, n.prev = self.head.next, self.head
        self.head.next.prev = n; self.head.next = n
    def get(self, k):
        if k not in self.mp: return -1
        self._rem(self.mp[k]); self._add(self.mp[k]); return self.mp[k].v
    def put(self, k, v):
        if k in self.mp: self._rem(self.mp[k]); self.mp[k].v = v; self._add(self.mp[k]); return
        if len(self.mp) == self.cap:
            lru = self.tail.prev; self._rem(lru); del self.mp[lru.k]
        n = Node(k, v); self.mp[k] = n; self._add(n)""",
       """class LRUCache {
    int cap; list<pair<int,int>> dll;
    unordered_map<int, list<pair<int,int>>::iterator> mp;
public:
    LRUCache(int c) : cap(c) {}
    int get(int k) {
        if (!mp.count(k)) return -1;
        dll.splice(dll.begin(), dll, mp[k]);
        return mp[k]->second;
    }
    void put(int k, int v) {
        if (mp.count(k)) { mp[k]->second = v; dll.splice(dll.begin(), dll, mp[k]); return; }
        if (dll.size() == cap) { mp.erase(dll.back().first); dll.pop_back(); }
        dll.push_front({k, v}); mp[k] = dll.begin();
    }
};"""),

    _p(81, "Merge K Sorted Lists", "Linked List & Fast/Slow", "Hard", ["Google", "Uber", "Amazon"], "merge-k-sorted-lists",
       "Min-Heap of size K OR Divide & Conquer pairwise merge (like MergeSort) in O(N log K) time and O(1) extra space!",
       "Pairwise merge avoids Python ListNode comparison issues cleanly.",
       "Time: O(N log K), Space: O(1) iterative D&C",
       """def mergeKLists(lists):
    if not lists: return None
    def merge(a, b):
        d = t = ListNode()
        while a and b:
            if a.val < b.val: t.next, a = a, a.next
            else: t.next, b = b, b.next
            t = t.next
        t.next = a or b; return d.next
    while len(lists) > 1:
        merged = [merge(lists[i], lists[i+1] if i+1 < len(lists) else None) for i in range(0, len(lists), 2)]
        lists = merged
    return lists[0]""",
       """ListNode* mergeKLists(vector<ListNode*>& lists) {
    auto cmp = [](ListNode* a, ListNode* b) { return a->val > b->val; };
    priority_queue<ListNode*, vector<ListNode*>, decltype(cmp)> pq(cmp);
    for (auto l : lists) if (l) pq.push(l);
    ListNode dummy(0), *t = &dummy;
    while (!pq.empty()) {
        auto cur = pq.top(); pq.pop();
        t->next = cur; t = t->next;
        if (cur->next) pq.push(cur->next);
    }
    return dummy.next;
}"""),

    _p(82, "Reverse Nodes in k-Group", "Linked List & Fast/Slow", "Hard", ["Razorpay", "Flipkart", "Microsoft"], "reverse-nodes-in-k-group",
       "Check if k nodes remain first; reverse strictly k links using prev = groupNext so tail automatically connects to next group!",
       "Dummy node holds groupPrev; carefully rewire groupPrev.next -> kth and update groupPrev.",
       "Time: O(N), Space: O(1)",
       """def reverseKGroup(head, k):
    dummy = groupPrev = ListNode(0, head)
    while True:
        kth = groupPrev
        for _ in range(k):
            kth = kth.next
            if not kth: return dummy.next
        groupNext = kth.next
        prev, cur = groupNext, groupPrev.next
        while cur != groupNext:
            nxt = cur.next; cur.next = prev; prev, cur = cur, nxt
        tmp = groupPrev.next; groupPrev.next = kth; groupPrev = tmp""",
       """ListNode* reverseKGroup(ListNode* head, int k) {
    ListNode dummy(0, head), *gp = &dummy;
    while (true) {
        ListNode* kth = gp;
        for (int i = 0; i < k && kth; ++i) kth = kth->next;
        if (!kth) break;
        ListNode *gn = kth->next, *prev = gn, *cur = gp->next;
        while (cur != gn) { ListNode* nxt = cur->next; cur->next = prev; prev = cur; cur = nxt; }
        ListNode* tmp = gp->next; gp->next = kth; gp = tmp;
    }
    return dummy.next;
}"""),

    # --- 7. TREES: DFS, BFS & BST (20) ---
    _p(83, "Invert Binary Tree", "Trees: DFS, BFS & BST", "Easy", ["Google", "Swiggy"], "invert-binary-tree",
       "Swap left and right child pointers recursively at every node.",
       "Base case None; post-order or pre-order swap yields mirror tree.",
       "Time: O(N), Space: O(H)",
       """def invertTree(root):
    if not root: return None
    root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root""",
       """TreeNode* invertTree(TreeNode* root) {
    if (!root) return nullptr;
    swap(root->left, root->right);
    invertTree(root->left); invertTree(root->right);
    return root;
}"""),

    _p(84, "Maximum Depth of Binary Tree", "Trees: DFS, BFS & BST", "Easy", ["Amazon", "LinkedIn"], "maximum-depth-of-binary-tree",
       "Depth = 1 + max(depth(left), depth(right)).",
       "Simple post-order height recursion.",
       "Time: O(N), Space: O(H)",
       """def maxDepth(root):
    return 0 if not root else 1 + max(maxDepth(root.left), maxDepth(root.right))""",
       """int maxDepth(TreeNode* root) {
    return root ? 1 + max(maxDepth(root->left), maxDepth(root->right)) : 0;
}"""),

    _p(85, "Diameter of Binary Tree", "Trees: DFS, BFS & BST", "Easy", ["Google", "Facebook", "Amazon"], "diameter-of-binary-tree",
       "Longest path through node = left_height + right_height! Return height upward while updating global max diameter.",
       "Avoids O(N^2) height recomputation by doing both in one post-order DFS.",
       "Time: O(N), Space: O(H)",
       """def diameterOfBinaryTree(root):
    ans = 0
    def h(node):
        nonlocal ans
        if not node: return 0
        l, r = h(node.left), h(node.right)
        ans = max(ans, l + r)
        return 1 + max(l, r)
    h(root); return ans""",
       """int diameterOfBinaryTree(TreeNode* root) {
    int ans = 0;
    function<int(TreeNode*)> h = [&](TreeNode* n) {
        if (!n) return 0;
        int l = h(n->left), r = h(n->right);
        ans = max(ans, l + r);
        return 1 + max(l, r);
    };
    h(root); return ans;
}"""),

    _p(86, "Balanced Binary Tree", "Trees: DFS, BFS & BST", "Easy", ["Paytm", "Amazon"], "balanced-binary-tree",
       "Bottom-up sentinel: return -1 immediately whenever abs(l - r) > 1 or subtree already returned -1!",
       "Stops early in O(N) instead of top-down O(N^2).",
       "Time: O(N), Space: O(H)",
       """def isBalanced(root):
    def h(n):
        if not n: return 0
        l, r = h(n.left), h(n.right)
        if l == -1 or r == -1 or abs(l - r) > 1: return -1
        return 1 + max(l, r)
    return h(root) != -1""",
       """int h(TreeNode* n) {
    if (!n) return 0;
    int l = h(n->left), r = h(n->right);
    if (l == -1 || r == -1 || abs(l - r) > 1) return -1;
    return 1 + max(l, r);
}
bool isBalanced(TreeNode* root) { return h(root) != -1; }"""),

    _p(87, "Same Tree", "Trees: DFS, BFS & BST", "Easy", ["Amazon", "Microsoft"], "same-tree",
       "Both None -> True; one None or values differ -> False; else recurse left AND right.",
       "Canonical structural + value equality check.",
       "Time: O(N), Space: O(H)",
       """def isSameTree(p, q):
    if not p and not q: return True
    if not p or not q or p.val != q.val: return False
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)""",
       """bool isSameTree(TreeNode* p, TreeNode* q) {
    if (!p && !q) return true;
    if (!p || !q || p->val != q->val) return false;
    return isSameTree(p->left, q->left) && isSameTree(p->right, q->right);
}"""),

    _p(88, "Subtree of Another Tree", "Trees: DFS, BFS & BST", "Easy", ["Flipkart", "Amazon"], "subtree-of-another-tree",
       "At each node in root, check isSameTree(root, subRoot); if false, recurse root.left or root.right.",
       "Or serialize both trees with delimiters ('#') and run substring check in O(N+M).",
       "Time: O(N*M), Space: O(H)",
       """def isSubtree(root, subRoot):
    if not root: return False
    def same(a, b):
        if not a and not b: return True
        if not a or not b or a.val != b.val: return False
        return same(a.left, b.left) and same(a.right, b.right)
    return same(root, subRoot) or isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)""",
       """bool same(TreeNode* a, TreeNode* b) {
    if (!a && !b) return true;
    if (!a || !b || a->val != b->val) return false;
    return same(a->left, b->left) && same(a->right, b->right);
}
bool isSubtree(TreeNode* root, TreeNode* subRoot) {
    if (!root) return false;
    return same(root, subRoot) || isSubtree(root->left, subRoot) || isSubtree(root->right, subRoot);
}"""),

    _p(89, "Lowest Common Ancestor of a BST", "Trees: DFS, BFS & BST", "Medium", ["Razorpay", "Amazon", "Meta"], "lowest-common-ancestor-of-a-binary-search-tree",
       "Exploit BST ordering! While both p and q are < root go left; while both > root go right; first split point IS the LCA!",
       "Iterative O(1) space without recursion stack.",
       "Time: O(H), Space: O(1)",
       """def lowestCommonAncestorBST(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val: root = root.left
        elif p.val > root.val and q.val > root.val: root = root.right
        else: return root""",
       """TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {
    while (root) {
        if (p->val < root->val && q->val < root->val) root = root->left;
        else if (p->val > root->val && q->val > root->val) root = root->right;
        else return root;
    }
    return nullptr;
}"""),

    _p(90, "Lowest Common Ancestor of a Binary Tree", "Trees: DFS, BFS & BST", "Medium", ["Zepto", "Swiggy", "Atlassian"], "lowest-common-ancestor-of-a-binary-tree",
       "If root is None, p, or q return root. Recurse left & right: if BOTH return non-null, current root is LCA!",
       "If only one side returns non-null, propagate that non-null upward.",
       "Time: O(N), Space: O(H)",
       """def lowestCommonAncestor(root, p, q):
    if not root or root == p or root == q: return root
    l = lowestCommonAncestor(root.left, p, q)
    r = lowestCommonAncestor(root.right, p, q)
    return root if (l and r) else (l or r)""",
       """TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {
    if (!root || root == p || root == q) return root;
    TreeNode *l = lowestCommonAncestor(root->left, p, q), *r = lowestCommonAncestor(root->right, p, q);
    return (l && r) ? root : (l ? l : r);
}"""),

    _p(91, "Binary Tree Level Order Traversal", "Trees: DFS, BFS & BST", "Medium", ["CRED", "Amazon", "Microsoft"], "binary-tree-level-order-traversal",
       "Standard Queue BFS: snapshot `len(q)` before inner loop to batch nodes strictly level-by-level.",
       "Append level array after inner for-loop finishes.",
       "Time: O(N), Space: O(N)",
       """from collections import deque
def levelOrder(root):
    if not root: return []
    q, res = deque([root]), []
    while q:
        lvl = []
        for _ in range(len(q)):
            n = q.popleft(); lvl.append(n.val)
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        res.append(lvl)
    return res""",
       """vector<vector<int>> levelOrder(TreeNode* root) {
    if (!root) return {};
    queue<TreeNode*> q; q.push(root); vector<vector<int>> res;
    while (!q.empty()) {
        int sz = q.size(); vector<int> lvl;
        while (sz--) {
            auto n = q.front(); q.pop(); lvl.push_back(n->val);
            if (n->left) q.push(n->left); if (n->right) q.push(n->right);
        }
        res.push_back(lvl);
    }
    return res;
}"""),

    _p(92, "Binary Tree Right Side View", "Trees: DFS, BFS & BST", "Medium", ["Flipkart", "Meta", "Amazon"], "binary-tree-right-side-view",
       "DFS visiting Root -> Right -> Left first: the FIRST node encountered at each depth (depth == len(res)) is the rightmost!",
       "Cleaner than BFS queue and handles skewed trees effortlessly.",
       "Time: O(N), Space: O(H)",
       """def rightSideView(root):
    res = []
    def dfs(n, d):
        if not n: return
        if d == len(res): res.append(n.val)
        dfs(n.right, d + 1); dfs(n.left, d + 1)
    dfs(root, 0); return res""",
       """vector<int> rightSideView(TreeNode* root) {
    vector<int> res;
    function<void(TreeNode*, int)> dfs = [&](TreeNode* n, int d) {
        if (!n) return;
        if (d == res.size()) res.push_back(n->val);
        dfs(n->right, d + 1); dfs(n->left, d + 1);
    };
    dfs(root, 0); return res;
}"""),

    _p(93, "Count Good Nodes in Binary Tree", "Trees: DFS, BFS & BST", "Medium", ["Microsoft", "Amazon"], "count-good-nodes-in-binary-tree",
       "Pass `max_so_far` downward in preorder DFS: node is good iff node.val >= max_so_far.",
       "Update max_so_far = max(max_so_far, node.val) for children.",
       "Time: O(N), Space: O(H)",
       """def goodNodes(root):
    def dfs(n, mx):
        if not n: return 0
        good = 1 if n.val >= mx else 0
        mx = max(mx, n.val)
        return good + dfs(n.left, mx) + dfs(n.right, mx)
    return dfs(root, root.val)""",
       """int dfs(TreeNode* n, int mx) {
    if (!n) return 0;
    int g = n->val >= mx ? 1 : 0; mx = max(mx, n->val);
    return g + dfs(n->left, mx) + dfs(n->right, mx);
}
int goodNodes(TreeNode* root) { return dfs(root, root->val); }"""),

    _p(94, "Validate Binary Search Tree", "Trees: DFS, BFS & BST", "Medium", ["Amazon", "Paytm", "Google"], "validate-binary-search-tree",
       "Never check only immediate children! Pass strict open interval (low, high) down recursion: left gets (low, val), right gets (val, high).",
       "Use 64-bit LONG_MIN/LONG_MAX in C++ because node vals can equal INT_MIN/INT_MAX.",
       "Time: O(N), Space: O(H)",
       """def isValidBST(root):
    def valid(n, lo, hi):
        if not n: return True
        if not (lo < n.val < hi): return False
        return valid(n.left, lo, n.val) and valid(n.right, n.val, hi)
    return valid(root, float('-inf'), float('inf'))""",
       """bool valid(TreeNode* n, long lo, long hi) {
    if (!n) return true;
    if (n->val <= lo || n->val >= hi) return false;
    return valid(n->left, lo, n->val) && valid(n->right, n->val, hi);
}
bool isValidBST(TreeNode* root) { return valid(root, LONG_MIN, LONG_MAX); }"""),

    _p(95, "Kth Smallest Element in a BST", "Trees: DFS, BFS & BST", "Medium", ["Uber", "Amazon", "Razorpay"], "kth-smallest-element-in-a-bst",
       "Inorder traversal of BST yields sorted order! Iterative stack stops immediately at the k-th popped node.",
       "Only touches H + K nodes instead of entire tree.",
       "Time: O(H + K), Space: O(H)",
       """def kthSmallest(root, k):
    st, cur = [], root
    while cur or st:
        while cur: st.append(cur); cur = cur.left
        cur = st.pop(); k -= 1
        if k == 0: return cur.val
        cur = cur.right""",
       """int kthSmallest(TreeNode* root, int k) {
    stack<TreeNode*> st; TreeNode* cur = root;
    while (cur || !st.empty()) {
        while (cur) { st.push(cur); cur = cur->left; }
        cur = st.top(); st.pop();
        if (--k == 0) return cur->val;
        cur = cur->right;
    }
    return -1;
}"""),

    _p(96, "Construct Binary Tree from Preorder & Inorder", "Trees: DFS, BFS & BST", "Medium", ["Microsoft", "Flipkart"], "construct-binary-tree-from-preorder-and-inorder-traversal",
       "Preorder[0] is ALWAYS root! HashMap inorder values -> index in O(1) so you split left/right subtrees without slicing.",
       "Index pointer advances sequentially through preorder during left-then-right construction.",
       "Time: O(N), Space: O(N)",
       """def buildTree(preorder, inorder):
    idx_map = {v: i for i, v in enumerate(inorder)}
    pre_i = 0
    def build(l, r):
        nonlocal pre_i
        if l > r: return None
        val = preorder[pre_i]; pre_i += 1
        root = TreeNode(val)
        mid = idx_map[val]
        root.left = build(l, mid - 1)
        root.right = build(mid + 1, r)
        return root
    return build(0, len(inorder) - 1)""",
       """TreeNode* buildTree(vector<int>& pre, vector<int>& in) {
    unordered_map<int, int> mp;
    for (int i = 0; i < in.size(); ++i) mp[in[i]] = i;
    int p = 0;
    function<TreeNode*(int,int)> build = [&](int l, int r) -> TreeNode* {
        if (l > r) return nullptr;
        int v = pre[p++]; TreeNode* root = new TreeNode(v);
        int mid = mp[v];
        root->left = build(l, mid - 1); root->right = build(mid + 1, r);
        return root;
    };
    return build(0, in.size() - 1);
}"""),

    _p(97, "Binary Tree Maximum Path Sum", "Trees: DFS, BFS & BST", "Hard", ["Google", "CRED", "Amazon", "Meta"], "binary-tree-maximum-path-sum",
       "Clamp negative branch gains with `max(0, dfs(child))`! At each node update ans = max(ans, val + l + r), return val + max(l, r).",
       "You can split at most once (at highest node in path), so only one branch goes upward.",
       "Time: O(N), Space: O(H)",
       """def maxPathSum(root):
    best = float('-inf')
    def dfs(n):
        nonlocal best
        if not n: return 0
        l = max(0, dfs(n.left)); r = max(0, dfs(n.right))
        best = max(best, n.val + l + r)
        return n.val + max(l, r)
    dfs(root); return best""",
       """int maxPathSum(TreeNode* root) {
    int best = INT_MIN;
    function<int(TreeNode*)> dfs = [&](TreeNode* n) {
        if (!n) return 0;
        int l = max(0, dfs(n->left)), r = max(0, dfs(n->right));
        best = max(best, n->val + l + r);
        return n->val + max(l, r);
    };
    dfs(root); return best;
}"""),

    _p(98, "Serialize and Deserialize Binary Tree", "Trees: DFS, BFS & BST", "Hard", ["Uber", "LinkedIn", "Atlassian"], "serialize-and-deserialize-binary-tree",
       "Preorder DFS with '#' null markers unambiguously uniquely reconstructs any binary tree without needing inorder!",
       "Tokenize with iterator/index during deserialization.",
       "Time: O(N), Space: O(N)",
       """class Codec:
    def serialize(self, root):
        out = []
        def dfs(n):
            if not n: out.append('#'); return
            out.append(str(n.val)); dfs(n.left); dfs(n.right)
        dfs(root); return ",".join(out)
    def deserialize(self, data):
        it = iter(data.split(","))
        def dfs():
            v = next(it)
            if v == '#': return None
            n = TreeNode(int(v)); n.left = dfs(); n.right = dfs(); return n
        return dfs()""",
       """class Codec {
public:
    string serialize(TreeNode* root) {
        if (!root) return "#,";
        return to_string(root->val) + "," + serialize(root->left) + serialize(root->right);
    }
    TreeNode* build(stringstream& ss) {
        string tok; getline(ss, tok, ',');
        if (tok == "#" || tok.empty()) return nullptr;
        TreeNode* n = new TreeNode(stoi(tok));
        n->left = build(ss); n->right = build(ss); return n;
    }
    TreeNode* deserialize(string data) { stringstream ss(data); return build(ss); }
};"""),

    _p(99, "Binary Tree Zigzag Level Order Traversal", "Trees: DFS, BFS & BST", "Medium", ["Swiggy", "Amazon"], "binary-tree-zigzag-level-order-traversal",
       "Standard level-order BFS using an indexed array of size `sz`: fill `i` on even levels and `sz - 1 - i` on odd levels (no reverse needed!).",
       "Clean O(N) single pass per level.",
       "Time: O(N), Space: O(N)",
       """from collections import deque
def zigzagLevelOrder(root):
    if not root: return []
    q, res, rev = deque([root]), [], False
    while q:
        sz = len(q); lvl = [0] * sz
        for i in range(sz):
            n = q.popleft()
            lvl[sz - 1 - i if rev else i] = n.val
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        res.append(lvl); rev = not rev
    return res""",
       """vector<vector<int>> zigzagLevelOrder(TreeNode* root) {
    if (!root) return {};
    queue<TreeNode*> q; q.push(root); vector<vector<int>> res; bool rev = false;
    while (!q.empty()) {
        int sz = q.size(); vector<int> lvl(sz);
        for (int i = 0; i < sz; ++i) {
            auto n = q.front(); q.pop();
            lvl[rev ? sz - 1 - i : i] = n->val;
            if (n->left) q.push(n->left); if (n->right) q.push(n->right);
        }
        res.push_back(lvl); rev = !rev;
    }
    return res;
}"""),

    _p(100, "Flatten Binary Tree to Linked List", "Trees: DFS, BFS & BST", "Medium", ["Microsoft", "Adobe"], "flatten-binary-tree-to-linked-list",
       "Morris-style O(1) space: if cur.left exists, attach rightmost node of cur.left to cur.right, then move cur.left to cur.right!",
       "Walk down cur = cur.right until finished.",
       "Time: O(N), Space: O(1)",
       """def flatten(root):
    cur = root
    while cur:
        if cur.left:
            prev = cur.left
            while prev.right: prev = prev.right
            prev.right = cur.right
            cur.right = cur.left; cur.left = None
        cur = cur.right""",
       """void flatten(TreeNode* root) {
    TreeNode* cur = root;
    while (cur) {
        if (cur->left) {
            TreeNode* prev = cur->left;
            while (prev->right) prev = prev->right;
            prev->right = cur->right;
            cur->right = cur->left; cur->left = nullptr;
        }
        cur = cur->right;
    }
}"""),

    _p(101, "Vertical Order Traversal of a Binary Tree", "Trees: DFS, BFS & BST", "Hard", ["Meta", "Amazon", "Google"], "vertical-order-traversal-of-a-binary-tree",
       "Collect (col, row, val) triples via DFS/BFS, sort all triples -> group by col! Ties in same (col, row) sort by val automatically.",
       "Avoids complex nested ordered maps.",
       "Time: O(N log N), Space: O(N)",
       """from collections import defaultdict
def verticalTraversal(root):
    nodes = []
    def dfs(n, r, c):
        if not n: return
        nodes.append((c, r, n.val))
        dfs(n.left, r + 1, c - 1); dfs(n.right, r + 1, c + 1)
    dfs(root, 0, 0); nodes.sort()
    cols = defaultdict(list)
    for c, r, v in nodes: cols[c].append(v)
    return list(cols.values())""",
       """vector<vector<int>> verticalTraversal(TreeNode* root) {
    vector<tuple<int,int,int>> nodes;
    function<void(TreeNode*,int,int)> dfs = [&](TreeNode* n, int r, int c) {
        if (!n) return;
        nodes.push_back({c, r, n->val});
        dfs(n->left, r+1, c-1); dfs(n->right, r+1, c+1);
    };
    dfs(root, 0, 0); sort(nodes.begin(), nodes.end());
    vector<vector<int>> res; int prevC = INT_MIN;
    for (auto& [c, r, v] : nodes) {
        if (c != prevC) { res.push_back({}); prevC = c; }
        res.back().push_back(v);
    }
    return res;
}"""),

    _p(102, "All Nodes Distance K in Binary Tree", "Trees: DFS, BFS & BST", "Medium", ["Amazon", "Flipkart"], "all-nodes-distance-k-in-binary-tree",
       "Trees are directed top-down; record `parent[node]` pointer map via DFS, then run multi-directional BFS (left, right, parent) starting at target!",
       "Stop BFS exactly at distance == k and return queue values.",
       "Time: O(N), Space: O(N)",
       """from collections import deque
def distanceK(root, target, k):
    par = {}
    def dfs(n, p=None):
        if not n: return
        par[n] = p; dfs(n.left, n); dfs(n.right, n)
    dfs(root)
    q, seen = deque([(target, 0)]), {target}
    while q:
        if q[0][1] == k: return [n.val for n, _ in q]
        n, d = q.popleft()
        for nxt in (n.left, n.right, par[n]):
            if nxt and nxt not in seen: seen.add(nxt); q.append((nxt, d + 1))
    return []""",
       """vector<int> distanceK(TreeNode* root, TreeNode* target, int k) {
    unordered_map<TreeNode*, TreeNode*> par;
    function<void(TreeNode*, TreeNode*)> dfs = [&](TreeNode* n, TreeNode* p) {
        if (!n) return; par[n] = p; dfs(n->left, n); dfs(n->right, n);
    };
    dfs(root, nullptr);
    queue<TreeNode*> q; q.push(target); unordered_set<TreeNode*> seen{target};
    int dist = 0;
    while (!q.empty() && dist < k) {
        int sz = q.size(); dist++;
        while (sz--) {
            auto n = q.front(); q.pop();
            for (auto nxt : {n->left, n->right, par[n]})
                if (nxt && !seen.count(nxt)) { seen.insert(nxt); q.push(nxt); }
        }
    }
    vector<int> res; while (!q.empty()) { res.push_back(q.front()->val); q.pop(); }
    return res;
}"""),
]
