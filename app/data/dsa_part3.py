from .dsa_part1 import _p

DSA_PART3 = [
    # --- 8. TRIES (6) ---
    _p(103, "Implement Trie (Prefix Tree)", "Tries", "Medium", ["Google", "Razorpay", "Amazon"], "implement-trie-prefix-tree",
       "Each node stores `children[26]` (or dict) + `is_end` boolean. Prefix lookup returns node != None; word search checks node.is_end.",
       "O(L) insert/search independent of dictionary size.",
       "Time: O(L) per op, Space: O(TotalChars)",
       """class TrieNode:
    def __init__(self): self.ch, self.end = {}, False
class Trie:
    def __init__(self): self.root = TrieNode()
    def insert(self, w):
        cur = self.root
        for c in w: cur = cur.ch.setdefault(c, TrieNode())
        cur.end = True
    def search(self, w):
        cur = self.root
        for c in w:
            if c not in cur.ch: return False
            cur = cur.ch[c]
        return cur.end
    def startsWith(self, p):
        cur = self.root
        for c in p:
            if c not in cur.ch: return False
            cur = cur.ch[c]
        return True""",
       """struct TrieNode {
    TrieNode* ch[26] = {}; bool end = false;
};
class Trie {
    TrieNode* root = new TrieNode();
public:
    void insert(string w) {
        auto cur = root;
        for (char c : w) { if (!cur->ch[c-'a']) cur->ch[c-'a'] = new TrieNode(); cur = cur->ch[c-'a']; }
        cur->end = true;
    }
    bool search(string w) {
        auto cur = root;
        for (char c : w) { if (!cur->ch[c-'a']) return false; cur = cur->ch[c-'a']; }
        return cur->end;
    }
    bool startsWith(string p) {
        auto cur = root;
        for (char c : p) { if (!cur->ch[c-'a']) return false; cur = cur->ch[c-'a']; }
        return true;
    }
};"""),

    _p(104, "Design Add and Search Words Data Structure", "Tries", "Medium", ["Meta", "Flipkart"], "design-add-and-search-words-data-structure",
       "Wildcard '.' -> trigger DFS recursion over ALL existing children of current TrieNode when c == '.'!",
       "Standard Trie traversal for exact characters + branching recursion for dots.",
       "Time: O(L) exact / O(26^dots * L) worst, Space: O(TotalChars)",
       """class WordDictionary:
    def __init__(self): self.root = {}
    def addWord(self, word):
        cur = self.root
        for c in word: cur = cur.setdefault(c, {})
        cur['$'] = True
    def search(self, word):
        def dfs(i, node):
            if i == len(word): return '$' in node
            c = word[i]
            if c == '.': return any(dfs(i + 1, nxt) for k, nxt in node.items() if k != '$')
            return c in node and dfs(i + 1, node[c])
        return dfs(0, self.root)""",
       """class WordDictionary {
    struct Node { Node* ch[26]={}; bool end=false; };
    Node* root = new Node();
    bool dfs(int i, const string& w, Node* n) {
        if (i == w.size()) return n->end;
        if (w[i] == '.') {
            for (int k = 0; k < 26; ++k) if (n->ch[k] && dfs(i+1, w, n->ch[k])) return true;
            return false;
        }
        return n->ch[w[i]-'a'] && dfs(i+1, w, n->ch[w[i]-'a']);
    }
public:
    void addWord(string w) {
        Node* c = root; for (char ch : w) { if (!c->ch[ch-'a']) c->ch[ch-'a'] = new Node(); c = c->ch[ch-'a']; } c->end = true;
    }
    bool search(string w) { return dfs(0, w, root); }
};"""),

    _p(105, "Word Search II", "Tries", "Hard", ["Amazon", "Uber", "Airbnb"], "word-search-ii",
       "Insert all target words into a Trie, run DFS once per board cell, and PRUNE matched leaf words from Trie to avoid TLE!",
       "Stores full word on leaf node so DFS appends result in O(1); deletes leaf branch once matched.",
       "Time: O(M*N * 4^L), Space: O(TotalChars)",
       """def findWords(board, words):
    root = {}
    for w in words:
        cur = root
        for c in w: cur = cur.setdefault(c, {})
        cur['$'] = w
    R, C, res = len(board), len(board[0]), []
    def dfs(r, c, node):
        ch = board[r][c]
        if ch not in node: return
        nxt = node[ch]
        if '$' in nxt: res.append(nxt.pop('$'))
        board[r][c] = '#'
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and board[nr][nc] != '#': dfs(nr, nc, nxt)
        board[r][c] = ch
        if not nxt: node.pop(ch)
    for r in range(R):
        for c in range(C): dfs(r, c, root)
    return res""",
       """struct TN { TN* ch[26]={}; string word=""; };
vector<string> findWords(vector<vector<char>>& b, vector<string>& words) {
    TN* root = new TN();
    for (auto& w : words) { TN* c = root; for (char ch : w) { if (!c->ch[ch-'a']) c->ch[ch-'a'] = new TN(); c = c->ch[ch-'a']; } c->word = w; }
    vector<string> res; int R = b.size(), C = b[0].size();
    function<void(int,int,TN*)> dfs = [&](int r, int c, TN* n) {
        char ch = b[r][c]; if (ch == '#' || !n->ch[ch-'a']) return;
        n = n->ch[ch-'a'];
        if (!n->word.empty()) { res.push_back(n->word); n->word.clear(); }
        b[r][c] = '#';
        int d[5] = {1,0,-1,0,1};
        for (int k = 0; k < 4; ++k) { int nr = r+d[k], nc = c+d[k+1]; if (nr>=0 && nr<R && nc>=0 && nc<C) dfs(nr, nc, n); }
        b[r][c] = ch;
    };
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) dfs(r, c, root);
    return res;
}"""),

    _p(106, "Maximum XOR of Two Numbers in an Array", "Tries", "Medium", ["Google", "CRED"], "maximum-xor-of-two-numbers-in-an-array",
       "Bitwise Trie from MSB (bit 30) down to LSB (bit 0): to maximize XOR, greedily walk into the OPPOSITE bit (1 - bit) whenever present!",
       "Avoids O(N^2) pairs; solves in O(32 * N).",
       "Time: O(32 * N), Space: O(32 * N)",
       """def findMaximumXOR(nums):
    root = {}
    for x in nums:
        cur = root
        for b in range(30, -1, -1):
            bit = (x >> b) & 1
            cur = cur.setdefault(bit, {})
    best = 0
    for x in nums:
        cur, xor_val = root, 0
        for b in range(30, -1, -1):
            bit = (x >> b) & 1; want = 1 - bit
            if want in cur: xor_val |= (1 << b); cur = cur[want]
            else: cur = cur[bit]
        best = max(best, xor_val)
    return best""",
       """int findMaximumXOR(vector<int>& nums) {
    struct BN { BN* ch[2]={}; }; BN* root = new BN();
    for (int x : nums) {
        BN* c = root;
        for (int b = 30; b >= 0; --b) {
            int bit = (x >> b) & 1;
            if (!c->ch[bit]) c->ch[bit] = new BN();
            c = c->ch[bit];
        }
    }
    int best = 0;
    for (int x : nums) {
        BN* c = root; int xv = 0;
        for (int b = 30; b >= 0; --b) {
            int bit = (x >> b) & 1, want = 1 - bit;
            if (c->ch[want]) { xv |= (1 << b); c = c->ch[want]; }
            else c = c->ch[bit];
        }
        best = max(best, xv);
    }
    return best;
}"""),

    _p(107, "Search Suggestions System", "Tries", "Medium", ["Amazon", "Swiggy"], "search-suggestions-system",
       "Sort products lexicographically -> every prefix match is a contiguous block! Binary search lower_bound or narrow [l..r] two pointers.",
       "Two-pointer prefix narrowing takes O(N log N + searchWordLen).",
       "Time: O(N log N + L), Space: O(1) aux",
       """def suggestedProducts(products, searchWord):
    products.sort(); res, l, r = [], 0, len(products) - 1
    for i, c in enumerate(searchWord):
        while l <= r and (len(products[l]) <= i or products[l][i] != c): l += 1
        while l <= r and (len(products[r]) <= i or products[r][i] != c): r -= 1
        res.append(products[l:min(l + 3, r + 1)])
    return res""",
       """vector<vector<string>> suggestedProducts(vector<string>& p, string w) {
    sort(p.begin(), p.end());
    vector<vector<string>> res; int l = 0, r = p.size() - 1;
    for (int i = 0; i < w.size(); ++i) {
        while (l <= r && (p[l].size() <= i || p[l][i] != w[i])) l++;
        while (l <= r && (p[r].size() <= i || p[r][i] != w[i])) r--;
        vector<string> cur;
        for (int k = l; k < min(l + 3, r + 1); ++k) cur.push_back(p[k]);
        res.push_back(cur);
    }
    return res;
}"""),

    _p(108, "Replace Words", "Tries", "Medium", ["Uber", "Google"], "replace-words",
       "Insert dictionary roots into Trie; for each sentence word stop at the FIRST `end` node (shortest root wins!).",
       "Avoids checking all dictionary prefixes per word.",
       "Time: O(Dict + Sentence), Space: O(Dict)",
       """def replaceWords(dictionary, sentence):
    root = {}
    for w in dictionary:
        c = root
        for ch in w: c = c.setdefault(ch, {})
        c['$'] = True
    def shortest(w):
        c = root
        for i, ch in enumerate(w):
            if '$' in c: return w[:i]
            if ch not in c: break
            c = c[ch]
        return w
    return " ".join(shortest(w) for w in sentence.split())""",
       """string replaceWords(vector<string>& dict, string sentence) {
    struct N { N* ch[26]={}; bool end=false; }; N* root = new N();
    for (auto& w : dict) { N* c = root; for (char ch : w) { if (!c->ch[ch-'a']) c->ch[ch-'a'] = new N(); c = c->ch[ch-'a']; } c->end = true; }
    stringstream ss(sentence); string w, out;
    while (ss >> w) {
        N* c = root; string pref;
        for (char ch : w) { if (c->end || !c->ch[ch-'a']) break; pref += ch; c = c->ch[ch-'a']; }
        out += (c->end ? pref : w) + " ";
    }
    if (!out.empty()) out.pop_back(); return out;
}"""),

    # --- 9. HEAPS / PRIORITY QUEUE (12) ---
    _p(109, "Kth Largest Element in a Stream", "Heaps / Priority Queue", "Easy", ["Amazon", "LinkedIn"], "kth-largest-element-in-a-stream",
       "Keep a Min-Heap capped strictly at size K! The top of the size-K Min-Heap IS the K-th largest element in O(1)!",
       "Never keep all N items; pop whenever len(heap) > k.",
       "Time: O(log K) per add, Space: O(K)",
       """import heapq
class KthLargest:
    def __init__(self, k, nums):
        self.k, self.h = k, nums
        heapq.heapify(self.h)
        while len(self.h) > k: heapq.heappop(self.h)
    def add(self, val):
        heapq.heappush(self.h, val)
        if len(self.h) > self.k: heapq.heappop(self.h)
        return self.h[0]""",
       """class KthLargest {
    int k; priority_queue<int, vector<int>, greater<int>> pq;
public:
    KthLargest(int k, vector<int>& nums) : k(k) {
        for (int x : nums) add(x);
    }
    int add(int val) {
        pq.push(val);
        if (pq.size() > k) pq.pop();
        return pq.top();
    }
};"""),

    _p(110, "Last Stone Weight", "Heaps / Priority Queue", "Easy", ["Amazon", "Swiggy"], "last-stone-weight",
       "Repeatedly extract top-2 maximums -> Max-Heap (negate values in Python heapq!). Push diff if x != y.",
       "Simulation using priority queue.",
       "Time: O(N log N), Space: O(N)",
       """import heapq
def lastStoneWeight(stones):
    h = [-s for s in stones]; heapq.heapify(h)
    while len(h) > 1:
        y, x = -heapq.heappop(h), -heapq.heappop(h)
        if y != x: heapq.heappush(h, -(y - x))
    return -h[0] if h else 0""",
       """int lastStoneWeight(vector<int>& stones) {
    priority_queue<int> pq(stones.begin(), stones.end());
    while (pq.size() > 1) {
        int y = pq.top(); pq.pop(); int x = pq.top(); pq.pop();
        if (y != x) pq.push(y - x);
    }
    return pq.empty() ? 0 : pq.top();
}"""),

    _p(111, "K Closest Points to Origin", "Heaps / Priority Queue", "Medium", ["Zepto", "Meta", "Amazon"], "k-closest-points-to-origin",
       "Skip sqrt! Compare d^2 = x^2 + y^2 using a Max-Heap of size K (or quickselect in O(N) average).",
       "Maintain size-K max heap so worst element gets evicted each time.",
       "Time: O(N log K), Space: O(K)",
       """import heapq
def kClosest(points, k):
    h = []
    for x, y in points:
        heapq.heappush(h, (-(x*x + y*y), x, y))
        if len(h) > k: heapq.heappop(h)
    return [[x, y] for _, x, y in h]""",
       """vector<vector<int>> kClosest(vector<vector<int>>& pts, int k) {
    priority_queue<pair<int, int>> pq;
    for (int i = 0; i < pts.size(); ++i) {
        pq.push({pts[i][0]*pts[i][0] + pts[i][1]*pts[i][1], i});
        if (pq.size() > k) pq.pop();
    }
    vector<vector<int>> res;
    while (!pq.empty()) { res.push_back(pts[pq.top().second]); pq.pop(); }
    return res;
}"""),

    _p(112, "Kth Largest Element in an Array", "Heaps / Priority Queue", "Medium", ["Razorpay", "Flipkart", "Meta"], "kth-largest-element-in-an-array",
       "Min-Heap of size K -> O(N log K) guaranteed worst-case; or Quickselect -> O(N) avg.",
       "Size-K min heap keeps code immune to adversarial inputs.",
       "Time: O(N log K), Space: O(K)",
       """import heapq
def findKthLargest(nums, k):
    h = nums[:k]; heapq.heapify(h)
    for x in nums[k:]:
        if x > h[0]: heapq.heapreplace(h, x)
    return h[0]""",
       """int findKthLargest(vector<int>& nums, int k) {
    priority_queue<int, vector<int>, greater<int>> pq;
    for (int x : nums) { pq.push(x); if (pq.size() > k) pq.pop(); }
    return pq.top();
}"""),

    _p(113, "Task Scheduler", "Heaps / Priority Queue", "Medium", ["Meta", "Amazon", "Atlassian"], "task-scheduler",
       "Math Formula: bottlenecks come from max_freq tasks! min_time = max(len(tasks), (max_f - 1) * (n + 1) + count_of_max_f).",
       "Every chunk of length (n+1) holds one of each max-freq task, plus leftover tasks fill idle slots.",
       "Time: O(N), Space: O(1)",
       """from collections import Counter
def leastInterval(tasks, n):
    cnt = list(Counter(tasks).values())
    mx = max(cnt)
    return max(len(tasks), (mx - 1) * (n + 1) + cnt.count(mx))""",
       """int leastInterval(vector<char>& tasks, int n) {
    int f[26] = {0}, mx = 0, mxCnt = 0;
    for (char c : tasks) mx = max(mx, ++f[c - 'A']);
    for (int x : f) if (x == mx) mxCnt++;
    return max((int)tasks.size(), (mx - 1) * (n + 1) + mxCnt);
}"""),

    _p(114, "Find Median from Data Stream", "Heaps / Priority Queue", "Hard", ["Google", "CRED", "Amazon", "Uber"], "find-median-from-data-stream",
       "Two Heaps: Max-Heap `small` (lower half) + Min-Heap `large` (upper half). Always keep len(small) == len(large) or +1!",
       "Push to small -> pop max to large -> rebalance if len(large) > len(small).",
       "Time: O(log N) add / O(1) median, Space: O(N)",
       """import heapq
class MedianFinder:
    def __init__(self): self.lo, self.hi = [], [] # lo: max-heap, hi: min-heap
    def addNum(self, num):
        heapq.heappush(self.lo, -num)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        if len(self.hi) > len(self.lo): heapq.heappush(self.lo, -heapq.heappop(self.hi))
    def findMedian(self):
        return -self.lo[0] if len(self.lo) > len(self.hi) else (-self.lo[0] + self.hi[0]) / 2""",
       """class MedianFinder {
    priority_queue<int> lo;
    priority_queue<int, vector<int>, greater<int>> hi;
public:
    void addNum(int num) {
        lo.push(num); hi.push(lo.top()); lo.pop();
        if (hi.size() > lo.size()) { lo.push(hi.top()); hi.pop(); }
    }
    double findMedian() {
        return lo.size() > hi.size() ? lo.top() : (lo.top() + hi.top()) / 2.0;
    }
};"""),

    _p(115, "Design Twitter", "Heaps / Priority Queue", "Medium", ["PhonePe", "Twitter", "Uber"], "design-twitter",
       "Keep global monotonic timestamp + per-user tweet list; getNewsFeed merges K sorted tweet tails using a Max-Heap!",
       "Same K-way merge principle behind real production fan-out-on-read feeds.",
       "Time: O(F log F) newsfeed, Space: O(Users + Tweets)",
       """import heapq
from collections import defaultdict
class Twitter:
    def __init__(self):
        self.t = 0; self.tweets = defaultdict(list); self.fol = defaultdict(set)
    def postTweet(self, uid, tid):
        self.t += 1; self.tweets[uid].append((-self.t, tid))
    def getNewsFeed(self, uid):
        h, res = [], []
        for f in self.fol[uid] | {uid}:
            if self.tweets[f]:
                idx = len(self.tweets[f]) - 1
                ts, tid = self.tweets[f][idx]
                heapq.heappush(h, (ts, tid, f, idx - 1))
        while h and len(res) < 10:
            ts, tid, f, idx = heapq.heappop(h)
            res.append(tid)
            if idx >= 0: nts, ntid = self.tweets[f][idx]; heapq.heappush(h, (nts, ntid, f, idx - 1))
        return res
    def follow(self, a, b): self.fol[a].add(b)
    def unfollow(self, a, b): self.fol[a].discard(b)""",
       """class Twitter {
    int t = 0;
    unordered_map<int, vector<pair<int,int>>> tw;
    unordered_map<int, unordered_set<int>> fol;
public:
    void postTweet(int u, int id) { tw[u].push_back({++t, id}); }
    vector<int> getNewsFeed(int u) {
        priority_queue<tuple<int,int,int,int>> pq;
        fol[u].insert(u);
        for (int f : fol[u]) if (!tw[f].empty()) {
            int i = tw[f].size() - 1;
            pq.push({tw[f][i].first, tw[f][i].second, f, i - 1});
        }
        vector<int> res;
        while (!pq.empty() && res.size() < 10) {
            auto [ts, id, f, i] = pq.top(); pq.pop();
            res.push_back(id);
            if (i >= 0) pq.push({tw[f][i].first, tw[f][i].second, f, i - 1});
        }
        return res;
    }
    void follow(int a, int b) { fol[a].insert(b); }
    void unfollow(int a, int b) { if (a != b) fol[a].erase(b); }
};"""),

    _p(116, "Reorganize String", "Heaps / Priority Queue", "Medium", ["Amazon", "Google"], "reorganize-string",
       "Max-Heap by frequency: pop top-1, hold previous character `prev` for 1 step cooldown before re-pushing if count > 0!",
       "Impossible iff max_freq > (n + 1) // 2.",
       "Time: O(N log 26), Space: O(1)",
       """import heapq
from collections import Counter
def reorganizeString(s):
    h = [(-f, c) for c, f in Counter(s).items()]; heapq.heapify(h)
    prev, res = (0, ''), []
    while h:
        f, c = heapq.heappop(h); res.append(c)
        if prev[0] < 0: heapq.heappush(h, prev)
        prev = (f + 1, c)
    return "".join(res) if len(res) == len(s) else "" """,
       """string reorganizeString(string s) {
    int cnt[26] = {0}; for (char c : s) cnt[c-'a']++;
    priority_queue<pair<int,char>> pq;
    for (int i = 0; i < 26; ++i) if (cnt[i]) pq.push({cnt[i], 'a'+i});
    string res; pair<int,char> prev{0, 0};
    while (!pq.empty()) {
        auto [f, c] = pq.top(); pq.pop(); res += c;
        if (prev.first > 0) pq.push(prev);
        prev = {f - 1, c};
    }
    return res.size() == s.size() ? res : "";
}"""),

    _p(117, "IPO (Maximize Capital)", "Heaps / Priority Queue", "Hard", ["Atlassian", "Amazon"], "ipo",
       "Two-Phase Greedy: sort projects by required capital ascending, use Min-pointer to push affordable projects into a Max-Heap of profits!",
       "Pick k times from the profit Max-Heap; stop early if heap empty.",
       "Time: O(N log N + K log N), Space: O(N)",
       """import heapq
def findMaximizedCapital(k, w, profits, capital):
    projs = sorted(zip(capital, profits)); h, i = [], 0
    for _ in range(k):
        while i < len(projs) and projs[i][0] <= w:
            heapq.heappush(h, -projs[i][1]); i += 1
        if not h: break
        w += -heapq.heappop(h)
    return w""",
       """int findMaximizedCapital(int k, int w, vector<int>& p, vector<int>& c) {
    vector<pair<int,int>> projs;
    for (int i = 0; i < p.size(); ++i) projs.push_back({c[i], p[i]});
    sort(projs.begin(), projs.end());
    priority_queue<int> pq; int i = 0;
    while (k--) {
        while (i < projs.size() && projs[i].first <= w) pq.push(projs[i++].second);
        if (pq.empty()) break;
        w += pq.top(); pq.pop();
    }
    return w;
}"""),

    _p(118, "Minimum Cost to Hire K Workers / Connect Ropes", "Heaps / Priority Queue", "Easy", ["Amazon", "Razorpay"], "last-stone-weight",
       "Connect N Ropes / Minimum Cost Combining: always merge the 2 SMALLEST pieces using a Min-Heap!",
       "Huffman coding greedy property minimizes weighted sum of merges.",
       "Time: O(N log N), Space: O(N)",
       """import heapq
def minCostConnectRopes(sticks):
    heapq.heapify(sticks); cost = 0
    while len(sticks) > 1:
        s = heapq.heappop(sticks) + heapq.heappop(sticks)
        cost += s; heapq.heappush(sticks, s)
    return cost""",
       """int connectSticks(vector<int>& sticks) {
    priority_queue<int, vector<int>, greater<int>> pq(sticks.begin(), sticks.end());
    int cost = 0;
    while (pq.size() > 1) {
        int a = pq.top(); pq.pop(); int b = pq.top(); pq.pop();
        cost += a + b; pq.push(a + b);
    }
    return cost;
}"""),

    _p(119, "Smallest Range Covering Elements from K Lists", "Heaps / Priority Queue", "Hard", ["Google", "Flipkart"], "smallest-range-covering-elements-from-k-lists",
       "Track current `max_val` separately + Min-Heap storing (val, list_id, idx): range is [heap[0].val, max_val]; pop min and advance its list!",
       "Stops immediately when any list reaches its end.",
       "Time: O(N log K), Space: O(K)",
       """import heapq
def smallestRange(nums):
    h = [(row[0], i, 0) for i, row in enumerate(nums)]
    heapq.heapify(h)
    mx = max(row[0] for row in nums)
    best = [h[0][0], mx]
    while True:
        lo, i, idx = heapq.heappop(h)
        if mx - lo < best[1] - best[0]: best = [lo, mx]
        if idx + 1 == len(nums[i]): return best
        nxt = nums[i][idx + 1]
        mx = max(mx, nxt)
        heapq.heappush(h, (nxt, i, idx + 1))""",
       """vector<int> smallestRange(vector<vector<int>>& nums) {
    using T = tuple<int,int,int>;
    priority_queue<T, vector<T>, greater<T>> pq;
    int mx = INT_MIN;
    for (int i = 0; i < nums.size(); ++i) { pq.push({nums[i][0], i, 0}); mx = max(mx, nums[i][0]); }
    int bestL = get<0>(pq.top()), bestR = mx;
    while (true) {
        auto [lo, i, idx] = pq.top(); pq.pop();
        if (mx - lo < bestR - bestL) { bestL = lo; bestR = mx; }
        if (idx + 1 == nums[i].size()) break;
        int nxt = nums[i][idx + 1]; mx = max(mx, nxt);
        pq.push({nxt, i, idx + 1});
    }
    return {bestL, bestR};
}"""),

    _p(120, "Meeting Rooms III", "Heaps / Priority Queue", "Hard", ["Google", "Uber"], "meeting-rooms-iii",
       "Two Min-Heaps: `free` (room_id) and `busy` (end_time, room_id). Pop all meetings ending <= start into `free`; if empty, pop earliest busy & delay!",
       "Keep track of usage count per room_id.",
       "Time: O(M log M + M log N), Space: O(N)",
       """import heapq
def mostBooked(n, meetings):
    meetings.sort()
    free, busy, cnt = list(range(n)), [], [0] * n
    for s, e in meetings:
        while busy and busy[0][0] <= s:
            _, r = heapq.heappop(busy); heapq.heappush(free, r)
        if free:
            r = heapq.heappop(free); heapq.heappush(busy, (e, r))
        else:
            end, r = heapq.heappop(busy); heapq.heappush(busy, (end + e - s, r))
        cnt[r] += 1
    return cnt.index(max(cnt))""",
       """int mostBooked(int n, vector<vector<int>>& meetings) {
    sort(meetings.begin(), meetings.end());
    priority_queue<int, vector<int>, greater<int>> freeR;
    priority_queue<pair<long long,int>, vector<pair<long long,int>>, greater<>> busy;
    for (int i = 0; i < n; ++i) freeR.push(i);
    vector<int> cnt(n, 0);
    for (auto& m : meetings) {
        long long s = m[0], e = m[1];
        while (!busy.empty() && busy.top().first <= s) { freeR.push(busy.top().second); busy.pop(); }
        if (!freeR.empty()) { int r = freeR.top(); freeR.pop(); busy.push({e, r}); cnt[r]++; }
        else { auto [end, r] = busy.top(); busy.pop(); busy.push({end + e - s, r}); cnt[r]++; }
    }
    return max_element(cnt.begin(), cnt.end()) - cnt.begin();
}"""),

    # --- 10. BACKTRACKING (12) ---
    _p(121, "Subsets", "Backtracking", "Medium", ["Amazon", "Flipkart"], "subsets",
       "Pick or Skip binary decision at each index `i` -> generates all 2^N subsets cleanly without duplicates.",
       "Copy current path when i == len(nums).",
       "Time: O(N * 2^N), Space: O(N)",
       """def subsets(nums):
    res, path = [], []
    def dfs(i):
        if i == len(nums): res.append(path[:]); return
        dfs(i + 1)
        path.append(nums[i]); dfs(i + 1); path.pop()
    dfs(0); return res""",
       """vector<vector<int>> subsets(vector<int>& nums) {
    vector<vector<int>> res; vector<int> p;
    function<void(int)> dfs = [&](int i) {
        if (i == nums.size()) { res.push_back(p); return; }
        dfs(i + 1); p.push_back(nums[i]); dfs(i + 1); p.pop_back();
    };
    dfs(0); return res;
}"""),

    _p(122, "Combination Sum", "Backtracking", "Medium", ["Razorpay", "Amazon", "Adobe"], "combination-sum",
       "Unlimited reuse allowed -> pass `i` (NOT `i + 1`) when picking nums[i]; advance `i + 1` only when skipping!",
       "Sort early + prune when rem < 0.",
       "Time: O(2^(T/min)), Space: O(T/min)",
       """def combinationSum(cands, target):
    res, path = [], []
    def dfs(i, rem):
        if rem == 0: res.append(path[:]); return
        if i == len(cands) or rem < 0: return
        path.append(cands[i]); dfs(i, rem - cands[i]); path.pop()
        dfs(i + 1, rem)
    dfs(0, target); return res""",
       """vector<vector<int>> combinationSum(vector<int>& c, int target) {
    vector<vector<int>> res; vector<int> p;
    function<void(int, int)> dfs = [&](int i, int rem) {
        if (rem == 0) { res.push_back(p); return; }
        if (i == c.size() || rem < 0) return;
        p.push_back(c[i]); dfs(i, rem - c[i]); p.pop_back();
        dfs(i + 1, rem);
    };
    dfs(0, target); return res;
}"""),

    _p(123, "Combination Sum II", "Backtracking", "Medium", ["Microsoft", "Swiggy"], "combination-sum-ii",
       "Dedup Trick: sort input, loop `j` from `i`..n, skip `if j > i and cands[j] == cands[j-1]: continue`!",
       "Allows duplicate numbers at deeper recursion levels while blocking identical branches at same level.",
       "Time: O(2^N), Space: O(N)",
       """def combinationSum2(cands, target):
    cands.sort(); res, path = [], []
    def dfs(start, rem):
        if rem == 0: res.append(path[:]); return
        for j in range(start, len(cands)):
            if j > start and cands[j] == cands[j-1]: continue
            if cands[j] > rem: break
            path.append(cands[j]); dfs(j + 1, rem - cands[j]); path.pop()
    dfs(0, target); return res""",
       """vector<vector<int>> combinationSum2(vector<int>& c, int target) {
    sort(c.begin(), c.end()); vector<vector<int>> res; vector<int> p;
    function<void(int,int)> dfs = [&](int st, int rem) {
        if (rem == 0) { res.push_back(p); return; }
        for (int j = st; j < c.size(); ++j) {
            if (j > st && c[j] == c[j-1]) continue;
            if (c[j] > rem) break;
            p.push_back(c[j]); dfs(j + 1, rem - c[j]); p.pop_back();
        }
    };
    dfs(0, target); return res;
}"""),

    _p(124, "Permutations", "Backtracking", "Medium", ["Amazon", "Paytm", "Google"], "permutations",
       "Swap index `i` with `j` in `[i..n-1]`, recurse `i + 1`, then swap back! Zero extra `used` array needed!",
       "Generates all N! permutations in-place.",
       "Time: O(N * N!), Space: O(N)",
       """def permute(nums):
    res = []
    def dfs(i):
        if i == len(nums): res.append(nums[:]); return
        for j in range(i, len(nums)):
            nums[i], nums[j] = nums[j], nums[i]; dfs(i + 1); nums[i], nums[j] = nums[j], nums[i]
    dfs(0); return res""",
       """vector<vector<int>> permute(vector<int>& nums) {
    vector<vector<int>> res;
    function<void(int)> dfs = [&](int i) {
        if (i == nums.size()) { res.push_back(nums); return; }
        for (int j = i; j < nums.size(); ++j) {
            swap(nums[i], nums[j]); dfs(i + 1); swap(nums[i], nums[j]);
        }
    };
    dfs(0); return res;
}"""),

    _p(125, "Subsets II (With Duplicates)", "Backtracking", "Medium", ["Flipkart", "Meta"], "subsets-ii",
       "Sort input, append current path at EVERY dfs entry, and skip `j > start and nums[j] == nums[j-1]` in loop.",
       "Prevents duplicate subsets without needing set-of-tuples.",
       "Time: O(N * 2^N), Space: O(N)",
       """def subsetsWithDup(nums):
    nums.sort(); res, path = [], []
    def dfs(start):
        res.append(path[:])
        for j in range(start, len(nums)):
            if j > start and nums[j] == nums[j-1]: continue
            path.append(nums[j]); dfs(j + 1); path.pop()
    dfs(0); return res""",
       """vector<vector<int>> subsetsWithDup(vector<int>& nums) {
    sort(nums.begin(), nums.end()); vector<vector<int>> res; vector<int> p;
    function<void(int)> dfs = [&](int st) {
        res.push_back(p);
        for (int j = st; j < nums.size(); ++j) {
            if (j > st && nums[j] == nums[j-1]) continue;
            p.push_back(nums[j]); dfs(j + 1); p.pop_back();
        }
    };
    dfs(0); return res;
}"""),

    _p(126, "Word Search", "Backtracking", "Medium", ["Zepto", "Amazon", "Microsoft"], "word-search",
       "Mark grid cell `board[r][c] = '#'` in-place before 4-way DFS, restore char on backtrack! Zero visited matrix needed.",
       "Prune out-of-bounds and mismatched chars immediately.",
       "Time: O(M*N * 4^L), Space: O(L)",
       """def exist(board, word):
    R, C = len(board), len(board[0])
    def dfs(r, c, i):
        if i == len(word): return True
        if r < 0 or c < 0 or r >= R or c >= C or board[r][c] != word[i]: return False
        tmp = board[r][c]; board[r][c] = '#'
        found = any(dfs(r+dr, c+dc, i+1) for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)))
        board[r][c] = tmp
        return found
    return any(dfs(r, c, 0) for r in range(R) for c in range(C))""",
       """bool exist(vector<vector<char>>& b, string w) {
    int R = b.size(), C = b[0].size();
    function<bool(int,int,int)> dfs = [&](int r, int c, int i) {
        if (i == w.size()) return true;
        if (r<0 || c<0 || r>=R || c>=C || b[r][c] != w[i]) return false;
        char t = b[r][c]; b[r][c] = '#';
        bool ok = dfs(r+1,c,i+1) || dfs(r-1,c,i+1) || dfs(r,c+1,i+1) || dfs(r,c-1,i+1);
        b[r][c] = t; return ok;
    };
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) if (dfs(r, c, 0)) return true;
    return false;
}"""),

    _p(127, "Palindrome Partitioning", "Backtracking", "Medium", ["Google", "Amazon"], "palindrome-partitioning",
       "At start index `i`, try every end `j >= i`: ONLY recurse on `j + 1` if `s[i:j+1]` is a palindrome!",
       "Backtracking pops current slice after recursive exploration.",
       "Time: O(N * 2^N), Space: O(N)",
       """def partition(s):
    res, path = [], []
    def dfs(i):
        if i == len(s): res.append(path[:]); return
        for j in range(i, len(s)):
            sub = s[i:j+1]
            if sub == sub[::-1]:
                path.append(sub); dfs(j + 1); path.pop()
    dfs(0); return res""",
       """vector<vector<string>> partition(string s) {
    vector<vector<string>> res; vector<string> p;
    auto isPal = [&](int l, int r) { while (l < r) if (s[l++] != s[r--]) return false; return true; };
    function<void(int)> dfs = [&](int i) {
        if (i == s.size()) { res.push_back(p); return; }
        for (int j = i; j < s.size(); ++j) if (isPal(i, j)) {
            p.push_back(s.substr(i, j - i + 1)); dfs(j + 1); p.pop_back();
        }
    };
    dfs(0); return res;
}"""),

    _p(128, "Letter Combinations of a Phone Number", "Backtracking", "Medium", ["Amazon", "Atlassian"], "letter-combinations-of-a-phone-number",
       "Cartesian product recursion over digit-to-letters map.",
       "Base case i == len(digits) appends joined string.",
       "Time: O(4^N * N), Space: O(N)",
       """def letterCombinations(digits):
    if not digits: return []
    mp = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}
    res = []
    def dfs(i, cur):
        if i == len(digits): res.append(cur); return
        for ch in mp[digits[i]]: dfs(i + 1, cur + ch)
    dfs(0, ""); return res""",
       """vector<string> letterCombinations(string digits) {
    if (digits.empty()) return {};
    vector<string> mp = {"","","abc","def","ghi","jkl","mno","pqrs","tuv","wxyz"}, res;
    string cur;
    function<void(int)> dfs = [&](int i) {
        if (i == digits.size()) { res.push_back(cur); return; }
        for (char c : mp[digits[i] - '0']) { cur.push_back(c); dfs(i + 1); cur.pop_back(); }
    };
    dfs(0); return res;
}"""),

    _p(129, "N-Queens", "Backtracking", "Hard", ["Razorpay", "Google", "CRED"], "n-queens",
       "Diagonal Trick: all cells on same main diagonal share `(r - c)`; anti-diagonal share `(r + c)`! Track 3 O(1) sets: cols, posDiag, negDiag.",
       "Place exactly one queen per row `r`, checking column & both diagonals in O(1).",
       "Time: O(N!), Space: O(N)",
       """def solveNQueens(n):
    cols, pos, neg, res = set(), set(), set(), []
    board = [["."] * n for _ in range(n)]
    def dfs(r):
        if r == n: res.append(["".join(row) for row in board]); return
        for c in range(n):
            if c in cols or (r + c) in pos or (r - c) in neg: continue
            cols.add(c); pos.add(r+c); neg.add(r-c); board[r][c] = 'Q'
            dfs(r + 1)
            cols.remove(c); pos.remove(r+c); neg.remove(r-c); board[r][c] = '.'
    dfs(0); return res""",
       """vector<vector<string>> solveNQueens(int n) {
    vector<vector<string>> res; vector<string> b(n, string(n, '.'));
    vector<int> col(n, 0), d1(2*n, 0), d2(2*n, 0);
    function<void(int)> dfs = [&](int r) {
        if (r == n) { res.push_back(b); return; }
        for (int c = 0; c < n; ++c) {
            if (col[c] || d1[r+c] || d2[r-c+n]) continue;
            col[c] = d1[r+c] = d2[r-c+n] = 1; b[r][c] = 'Q';
            dfs(r + 1);
            col[c] = d1[r+c] = d2[r-c+n] = 0; b[r][c] = '.';
        }
    };
    dfs(0); return res;
}"""),

    _p(130, "Sudoku Solver", "Backtracking", "Hard", ["Uber", "Amazon"], "sudoku-solver",
       "Precompute 3 bitmasks/arrays (row[9], col[9], box[9]) + list of empty cells so backtracking runs fast with O(1) validity checks!",
       "Try digits 1..9 at each empty cell and undo masks on backtrack.",
       "Time: O(9^Empty), Space: O(Empty)",
       """def solveSudoku(board):
    rows, cols, boxes = [set() for _ in range(9)], [set() for _ in range(9)], [set() for _ in range(9)]
    empty = []
    for r in range(9):
        for c in range(9):
            if board[r][c] == '.': empty.append((r, c))
            else: v = board[r][c]; rows[r].add(v); cols[c].add(v); boxes[(r//3)*3+c//3].add(v)
    def dfs(k):
        if k == len(empty): return True
        r, c = empty[k]; b = (r//3)*3 + c//3
        for ch in "123456789":
            if ch not in rows[r] and ch not in cols[c] and ch not in boxes[b]:
                board[r][c] = ch; rows[r].add(ch); cols[c].add(ch); boxes[b].add(ch)
                if dfs(k + 1): return True
                board[r][c] = '.'; rows[r].remove(ch); cols[c].remove(ch); boxes[b].remove(ch)
        return False
    dfs(0)""",
       """void solveSudoku(vector<vector<char>>& b) {
    int rMask[9]={0}, cMask[9]={0}, box[9]={0}; vector<pair<int,int>> emp;
    for (int r = 0; r < 9; ++r) for (int c = 0; c < 9; ++c) {
        if (b[r][c] == '.') emp.push_back({r, c});
        else { int m = 1 << (b[r][c]-'1'); rMask[r]|=m; cMask[c]|=m; box[(r/3)*3+c/3]|=m; }
    }
    function<bool(int)> dfs = [&](int k) {
        if (k == emp.size()) return true;
        auto [r, c] = emp[k]; int bx = (r/3)*3 + c/3;
        for (int d = 0; d < 9; ++d) {
            int m = 1 << d;
            if (!(rMask[r]&m) && !(cMask[c]&m) && !(box[bx]&m)) {
                b[r][c] = '1' + d; rMask[r]|=m; cMask[c]|=m; box[bx]|=m;
                if (dfs(k + 1)) return true;
                b[r][c] = '.'; rMask[r]^=m; cMask[c]^=m; box[bx]^=m;
            }
        }
        return false;
    };
    dfs(0);
}"""),

    _p(131, "Generate Parentheses", "Backtracking", "Medium", ["Swiggy", "Microsoft", "Amazon"], "generate-parentheses",
       "Track counts `open` and `close`: add '(' iff open < n; add ')' iff close < open!",
       "Guaranteed valid balanced strings at leaf open == close == n.",
       "Time: Catalan(N), Space: O(N)",
       """def generateParenthesis(n):
    res = []
    def dfs(o, c, s):
        if len(s) == 2 * n: res.append(s); return
        if o < n: dfs(o + 1, c, s + "(")
        if c < o: dfs(o, c + 1, s + ")")
    dfs(0, 0, ""); return res""",
       """vector<string> generateParenthesis(int n) {
    vector<string> res; string s;
    function<void(int,int)> dfs = [&](int o, int c) {
        if (s.size() == 2 * n) { res.push_back(s); return; }
        if (o < n) { s.push_back('('); dfs(o + 1, c); s.pop_back(); }
        if (c < o) { s.push_back(')'); dfs(o, c + 1); s.pop_back(); }
    };
    dfs(0, 0); return res;
}"""),

    _p(132, "Rat in a Maze / Unique Paths III", "Backtracking", "Hard", ["Paytm", "Google"], "unique-paths-iii",
       "Count total walkable zero squares upfront; recurse 4-ways marking visited cells `-1`, return 1 iff reaching end with remaining == 0!",
       "Exact Hamiltonian path backtracking on grid.",
       "Time: O(3^(R*C)), Space: O(R*C)",
       """def uniquePathsIII(grid):
    R, C, rem, sr, sc = len(grid), len(grid[0]), 1, 0, 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 0: rem += 1
            elif grid[r][c] == 1: sr, sc = r, c
    def dfs(r, c, left):
        if r < 0 or c < 0 or r >= R or c >= C or grid[r][c] < 0: return 0
        if grid[r][c] == 2: return 1 if left == 0 else 0
        grid[r][c] = -1
        ans = sum(dfs(r+dr, c+dc, left-1) for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)))
        grid[r][c] = 0
        return ans
    return dfs(sr, sc, rem)""",
       """int uniquePathsIII(vector<vector<int>>& g) {
    int R = g.size(), C = g[0].size(), rem = 1, sr = 0, sc = 0;
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) {
        if (g[r][c] == 0) rem++; else if (g[r][c] == 1) { sr = r; sc = c; }
    }
    function<int(int,int,int)> dfs = [&](int r, int c, int left) {
        if (r<0 || c<0 || r>=R || c>=C || g[r][c] < 0) return 0;
        if (g[r][c] == 2) return left == 0 ? 1 : 0;
        int orig = g[r][c]; g[r][c] = -1;
        int ans = dfs(r+1,c,left-1)+dfs(r-1,c,left-1)+dfs(r,c+1,left-1)+dfs(r,c-1,left-1);
        g[r][c] = orig; return ans;
    };
    return dfs(sr, sc, rem);
}"""),

    # --- 11. GRAPHS: BFS, DFS, TOPO, DIJKSTRA, DSU (22) ---
    _p(133, "Number of Islands", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Amazon", "Zepto", "Swiggy"], "number-of-islands",
       "Sink visited land cells directly to '0' during DFS/BFS so you need zero extra visited matrix!",
       "Each unvisited '1' launches a flood-fill that counts +1 island.",
       "Time: O(R*C), Space: O(R*C)",
       """def numIslands(grid):
    R, C, ans = len(grid), len(grid[0]), 0
    def dfs(r, c):
        if r<0 or c<0 or r>=R or c>=C or grid[r][c] != '1': return
        grid[r][c] = '0'
        dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)
    for r in range(R):
        for c in range(C):
            if grid[r][c] == '1': ans += 1; dfs(r, c)
    return ans""",
       """int numIslands(vector<vector<char>>& g) {
    int R = g.size(), C = g[0].size(), ans = 0;
    function<void(int,int)> dfs = [&](int r, int c) {
        if (r<0 || c<0 || r>=R || c>=C || g[r][c] != '1') return;
        g[r][c] = '0'; dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1);
    };
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c)
        if (g[r][c] == '1') { ans++; dfs(r, c); }
    return ans;
}"""),

    _p(134, "Max Area of Island", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Flipkart", "DoorDash"], "max-area-of-island",
       "Same island flood-fill, returning `1 + sum(4 neighbors)` from DFS.",
       "Sink visited 1s to 0s and take max over all components.",
       "Time: O(R*C), Space: O(R*C)",
       """def maxAreaOfIsland(grid):
    R, C = len(grid), len(grid[0])
    def dfs(r, c):
        if r<0 or c<0 or r>=R or c>=C or grid[r][c] == 0: return 0
        grid[r][c] = 0
        return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)
    return max((dfs(r, c) for r in range(R) for c in range(C)), default=0)""",
       """int maxAreaOfIsland(vector<vector<int>>& g) {
    int R = g.size(), C = g[0].size(), best = 0;
    function<int(int,int)> dfs = [&](int r, int c) {
        if (r<0 || c<0 || r>=R || c>=C || !g[r][c]) return 0;
        g[r][c] = 0;
        return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1);
    };
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) best = max(best, dfs(r, c));
    return best;
}"""),

    _p(135, "Clone Graph", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Meta", "Amazon"], "clone-graph",
       "Map old Node -> cloned Node FIRST before recursing on neighbors so cycles terminate in O(1)!",
       "DFS clones node and populates clone.neighbors recursively.",
       "Time: O(V + E), Space: O(V)",
       """def cloneGraph(node):
    if not node: return None
    mp = {}
    def dfs(n):
        if n in mp: return mp[n]
        mp[n] = Node(n.val)
        mp[n].neighbors = [dfs(nb) for nb in n.neighbors]
        return mp[n]
    return dfs(node)""",
       """unordered_map<Node*, Node*> mp;
Node* cloneGraph(Node* node) {
    if (!node) return nullptr;
    if (mp.count(node)) return mp[node];
    mp[node] = new Node(node->val);
    for (auto nb : node->neighbors) mp[node]->neighbors.push_back(cloneGraph(nb));
    return mp[node];
}"""),

    _p(136, "Rotting Oranges", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Zepto", "Swiggy", "Amazon"], "rotting-oranges",
       "Multi-Source BFS! Seed queue with ALL initially rotten oranges at minute 0, count fresh oranges, decrement fresh on infection!",
       "Simultaneous BFS ripple spreads minute-by-minute cleanly.",
       "Time: O(R*C), Space: O(R*C)",
       """from collections import deque
def orangesRotting(grid):
    R, C, q, fresh, mins = len(grid), len(grid[0]), deque(), 0, 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 2: q.append((r, c))
            elif grid[r][c] == 1: fresh += 1
    while q and fresh > 0:
        mins += 1
        for _ in range(len(q)):
            r, c = q.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0<=nr<R and 0<=nc<C and grid[nr][nc] == 1:
                    grid[nr][nc] = 2; fresh -= 1; q.append((nr, nc))
    return mins if fresh == 0 else -1""",
       """int orangesRotting(vector<vector<int>>& g) {
    int R = g.size(), C = g[0].size(), fresh = 0, mins = 0; queue<pair<int,int>> q;
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) {
        if (g[r][c] == 2) q.push({r, c}); else if (g[r][c] == 1) fresh++;
    }
    int d[5] = {1,0,-1,0,1};
    while (!q.empty() && fresh > 0) {
        mins++; int sz = q.size();
        while (sz--) {
            auto [r, c] = q.front(); q.pop();
            for (int k = 0; k < 4; ++k) {
                int nr = r+d[k], nc = c+d[k+1];
                if (nr>=0 && nr<R && nc>=0 && nc<C && g[nr][nc] == 1) {
                    g[nr][nc] = 2; fresh--; q.push({nr, nc});
                }
            }
        }
    }
    return fresh == 0 ? mins : -1;
}"""),

    _p(137, "Pacific Atlantic Water Flow", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Google", "Amazon"], "pacific-atlantic-water-flow",
       "Reverse Flow Trick! Instead of flowing downhill from every cell, climb UPHILL from Pacific borders and Atlantic borders separately, then intersect!",
       "Only touches each cell at most twice.",
       "Time: O(R*C), Space: O(R*C)",
       """def pacificAtlantic(h):
    R, C = len(h), len(h[0])
    pac, atl = set(), set()
    def dfs(r, c, vis, prev):
        if r<0 or c<0 or r>=R or c>=C or (r,c) in vis or h[r][c] < prev: return
        vis.add((r,c))
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)): dfs(r+dr, c+dc, vis, h[r][c])
    for r in range(R): dfs(r, 0, pac, 0); dfs(r, C-1, atl, 0)
    for c in range(C): dfs(0, c, pac, 0); dfs(R-1, c, atl, 0)
    return list(pac & atl)""",
       """vector<vector<int>> pacificAtlantic(vector<vector<int>>& h) {
    int R = h.size(), C = h[0].size();
    vector<vector<int>> p(R, vector<int>(C)), a(R, vector<int>(C));
    function<void(int,int,vector<vector<int>>&,int)> dfs = [&](int r, int c, vector<vector<int>>& v, int prev) {
        if (r<0 || c<0 || r>=R || c>=C || v[r][c] || h[r][c] < prev) return;
        v[r][c] = 1;
        dfs(r+1,c,v,h[r][c]); dfs(r-1,c,v,h[r][c]); dfs(r,c+1,v,h[r][c]); dfs(r,c-1,v,h[r][c]);
    };
    for (int r = 0; r < R; ++r) { dfs(r, 0, p, 0); dfs(r, C-1, a, 0); }
    for (int c = 0; c < C; ++c) { dfs(0, c, p, 0); dfs(R-1, c, a, 0); }
    vector<vector<int>> res;
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) if (p[r][c] && a[r][c]) res.push_back({r, c});
    return res;
}"""),

    _p(138, "Surrounded Regions", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Microsoft", "Uber"], "surrounded-regions",
       "Border Escape Trick: mark all 'O's reachable from the 4 borders as safe ('T'), flip remaining 'O' -> 'X', restore 'T' -> 'O'!",
       "Inverse framing simplifies interior capture logic completely.",
       "Time: O(R*C), Space: O(R*C)",
       """def solve(board):
    R, C = len(board), len(board[0])
    def dfs(r, c):
        if r<0 or c<0 or r>=R or c>=C or board[r][c] != 'O': return
        board[r][c] = 'T'
        dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)
    for r in range(R): dfs(r, 0); dfs(r, C-1)
    for c in range(C): dfs(0, c); dfs(R-1, c)
    for r in range(R):
        for c in range(C):
            board[r][c] = 'O' if board[r][c] == 'T' else 'X'""",
       """void solve(vector<vector<char>>& b) {
    int R = b.size(), C = b[0].size();
    function<void(int,int)> dfs = [&](int r, int c) {
        if (r<0 || c<0 || r>=R || c>=C || b[r][c] != 'O') return;
        b[r][c] = 'T'; dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1);
    };
    for (int r = 0; r < R; ++r) { dfs(r, 0); dfs(r, C-1); }
    for (int c = 0; c < C; ++c) { dfs(0, c); dfs(R-1, c); }
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) b[r][c] = (b[r][c] == 'T' ? 'O' : 'X');
}"""),

    _p(139, "Course Schedule (Cycle Detection in DAG)", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Razorpay", "Amazon", "Atlassian"], "course-schedule",
       "Kahn's Topological Sort BFS: track indegrees, push nodes with indegree 0, decrement neighbors; valid iff popped_count == numCourses!",
       "If a cycle exists, cycle nodes never hit indegree 0.",
       "Time: O(V + E), Space: O(V + E)",
       """from collections import deque
def canFinish(n, prereqs):
    adj = [[] for _ in range(n)]; indeg = [0] * n
    for a, b in prereqs: adj[b].append(a); indeg[a] += 1
    q = deque([i for i in range(n) if indeg[i] == 0]); done = 0
    while q:
        u = q.popleft(); done += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    return done == n""",
       """bool canFinish(int n, vector<vector<int>>& prereqs) {
    vector<vector<int>> adj(n); vector<int> ind(n, 0);
    for (auto& e : prereqs) { adj[e[1]].push_back(e[0]); ind[e[0]]++; }
    queue<int> q; for (int i = 0; i < n; ++i) if (!ind[i]) q.push(i);
    int done = 0;
    while (!q.empty()) {
        int u = q.front(); q.pop(); done++;
        for (int v : adj[u]) if (--ind[v] == 0) q.push(v);
    }
    return done == n;
}"""),

    _p(140, "Course Schedule II (Topological Order)", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Flipkart", "Uber", "Amazon"], "course-schedule-ii",
       "Identical Kahn's BFS, simply appending popped nodes to `order` and returning `order if len(order) == n else []`!",
       "Cleanest way to emit dependency build order.",
       "Time: O(V + E), Space: O(V + E)",
       """from collections import deque
def findOrder(n, prereqs):
    adj = [[] for _ in range(n)]; indeg = [0] * n
    for a, b in prereqs: adj[b].append(a); indeg[a] += 1
    q, order = deque([i for i in range(n) if indeg[i] == 0]), []
    while q:
        u = q.popleft(); order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    return order if len(order) == n else []""",
       """vector<int> findOrder(int n, vector<vector<int>>& prereqs) {
    vector<vector<int>> adj(n); vector<int> ind(n, 0), ord;
    for (auto& e : prereqs) { adj[e[1]].push_back(e[0]); ind[e[0]]++; }
    queue<int> q; for (int i = 0; i < n; ++i) if (!ind[i]) q.push(i);
    while (!q.empty()) {
        int u = q.front(); q.pop(); ord.push_back(u);
        for (int v : adj[u]) if (--ind[v] == 0) q.push(v);
    }
    return ord.size() == n ? ord : vector<int>{};
}"""),

    _p(141, "Redundant Connection (Union-Find / DSU)", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Google", "Razorpay"], "redundant-connection",
       "Union-Find (DSU) with Path Compression: the FIRST edge (u, v) where find(u) == find(v) creates a cycle and is redundant!",
       "Maintain parent array initialized to i.",
       "Time: O(N * alpha(N)), Space: O(N)",
       """def findRedundantConnection(edges):
    par = list(range(len(edges) + 1))
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for u, v in edges:
        pu, pv = find(u), find(v)
        if pu == pv: return [u, v]
        par[pu] = pv""",
       """vector<int> findRedundantConnection(vector<vector<int>>& edges) {
    vector<int> par(edges.size() + 1); iota(par.begin(), par.end(), 0);
    function<int(int)> find = [&](int x) { return par[x] == x ? x : par[x] = find(par[x]); };
    for (auto& e : edges) {
        int pu = find(e[0]), pv = find(e[1]);
        if (pu == pv) return e;
        par[pu] = pv;
    }
    return {};
}"""),

    _p(142, "Number of Connected Components / Provinces", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["CRED", "Amazon"], "number-of-provinces",
       "Start with count = N; decrement count by 1 every time DSU successfully merges two previously disconnected roots!",
       "Works cleanly on adjacency matrix or edge lists.",
       "Time: O(N^2 * alpha(N)), Space: O(N)",
       """def findCircleNum(isConnected):
    n = len(isConnected); par = list(range(n)); comps = n
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j]:
                pi, pj = find(i), find(j)
                if pi != pj: par[pi] = pj; comps -= 1
    return comps""",
       """int findCircleNum(vector<vector<int>>& mat) {
    int n = mat.size(), comps = n; vector<int> par(n); iota(par.begin(), par.end(), 0);
    function<int(int)> find = [&](int x) { return par[x] == x ? x : par[x] = find(par[x]); };
    for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) if (mat[i][j]) {
        int pi = find(i), pj = find(j);
        if (pi != pj) { par[pi] = pj; comps--; }
    }
    return comps;
}"""),

    _p(143, "Word Ladder", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Hard", ["Amazon", "Google", "Meta"], "word-ladder",
       "Unweighted shortest transformation -> BFS! Mutate each character a..z (26 * L) instead of comparing every pair of words (N^2).",
       "Delete visited words directly from `wordSet` upon enqueue to prevent cycles.",
       "Time: O(N * L * 26), Space: O(N * L)",
       """from collections import deque
def ladderLength(beginWord, endWord, wordList):
    ws = set(wordList)
    if endWord not in ws: return 0
    q = deque([(beginWord, 1)])
    while q:
        w, d = q.popleft()
        if w == endWord: return d
        for i in range(len(w)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                nw = w[:i] + c + w[i+1:]
                if nw in ws: ws.remove(nw); q.append((nw, d + 1))
    return 0""",
       """int ladderLength(string begin, string end, vector<string>& list) {
    unordered_set<string> ws(list.begin(), list.end());
    if (!ws.count(end)) return 0;
    queue<pair<string,int>> q; q.push({begin, 1});
    while (!q.empty()) {
        auto [w, d] = q.front(); q.pop();
        if (w == end) return d;
        for (int i = 0; i < w.size(); ++i) {
            char orig = w[i];
            for (char c = 'a'; c <= 'z'; ++c) {
                w[i] = c;
                if (ws.count(w)) { ws.erase(w); q.push({w, d + 1}); }
            }
            w[i] = orig;
        }
    }
    return 0;
}"""),

    _p(144, "Is Graph Bipartite?", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Microsoft", "Flipkart"], "is-graph-bipartite",
       "2-Coloring BFS/DFS across all components: color unvisited node 0, neighbors get `1 - color`; conflict iff neighbor already shares color!",
       "Checks odd-length cycles cleanly.",
       "Time: O(V + E), Space: O(V)",
       """from collections import deque
def isBipartite(graph):
    col = {}
    for s in range(len(graph)):
        if s in col: continue
        col[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for v in graph[u]:
                if v not in col: col[v] = 1 - col[u]; q.append(v)
                elif col[v] == col[u]: return False
    return True""",
       """bool isBipartite(vector<vector<int>>& g) {
    vector<int> col(g.size(), -1);
    for (int i = 0; i < g.size(); ++i) if (col[i] == -1) {
        queue<int> q; q.push(i); col[i] = 0;
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int v : g[u]) {
                if (col[v] == -1) { col[v] = 1 - col[u]; q.push(v); }
                else if (col[v] == col[u]) return false;
            }
        }
    }
    return true;
}"""),

    _p(145, "Network Delay Time (Dijkstra's Algorithm)", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Google", "Uber", "Amazon"], "network-delay-time",
       "Weighted non-negative shortest path -> Min-Heap Dijkstra storing (dist, node). Skip stale heap pops `if d > dist[u]: continue`!",
       "Answer is max(dist[1..n]) if all nodes reached, else -1.",
       "Time: O(E log V), Space: O(V + E)",
       """import heapq
def networkDelayTime(times, n, k):
    adj = [[] for _ in range(n + 1)]
    for u, v, w in times: adj[u].append((v, w))
    dist = [float('inf')] * (n + 1); dist[k] = 0
    h = [(0, k)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]: continue
        for v, w in adj[u]:
            if d + w < dist[v]: dist[v] = d + w; heapq.heappush(h, (dist[v], v))
    mx = max(dist[1:])
    return mx if mx < float('inf') else -1""",
       """int networkDelayTime(vector<vector<int>>& times, int n, int k) {
    vector<vector<pair<int,int>>> adj(n + 1);
    for (auto& t : times) adj[t[0]].push_back({t[1], t[2]});
    vector<int> dist(n + 1, INT_MAX); dist[k] = 0;
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq; pq.push({0, k});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;
        for (auto [v, w] : adj[u]) if (d + w < dist[v]) { dist[v] = d + w; pq.push({dist[v], v}); }
    }
    int mx = *max_element(dist.begin() + 1, dist.end());
    return mx == INT_MAX ? -1 : mx;
}"""),

    _p(146, "Cheapest Flights Within K Stops", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Razorpay", "Airbnb", "Swiggy"], "cheapest-flights-within-k-stops",
       "Bellman-Ford for K + 1 iterations! Copy `prev_dist = dist[:]` at the start of each round so a path only advances 1 edge per round!",
       "Simpler and safer than modified Dijkstra when hop limits apply.",
       "Time: O(K * E), Space: O(V)",
       """def findCheapestPrice(n, flights, src, dst, k):
    dist = [float('inf')] * n; dist[src] = 0
    for _ in range(k + 1):
        nxt = dist[:]
        for u, v, w in flights:
            if dist[u] != float('inf') and dist[u] + w < nxt[v]: nxt[v] = dist[u] + w
        dist = nxt
    return -1 if dist[dst] == float('inf') else dist[dst]""",
       """int findCheapestPrice(int n, vector<vector<int>>& flights, int src, int dst, int k) {
    vector<int> dist(n, INT_MAX); dist[src] = 0;
    for (int i = 0; i <= k; ++i) {
        vector<int> nxt = dist;
        for (auto& f : flights)
            if (dist[f[0]] != INT_MAX && dist[f[0]] + f[2] < nxt[f[1]]) nxt[f[1]] = dist[f[0]] + f[2];
        dist = move(nxt);
    }
    return dist[dst] == INT_MAX ? -1 : dist[dst];
}"""),

    _p(147, "Min Cost to Connect All Points (MST - Prim's)", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Amazon", "Google"], "min-cost-to-connect-all-points",
       "Dense graph MST -> O(N^2) Prim's without priority queue! Track min_dist[i] from current MST to each unvisited node.",
       "Fastest possible MST on complete graphs without building E = N^2 edges.",
       "Time: O(N^2), Space: O(N)",
       """def minCostConnectPoints(pts):
    n = len(pts); vis = [False]*n; minD = [float('inf')]*n; minD[0] = 0; cost = 0
    for _ in range(n):
        u = -1
        for i in range(n):
            if not vis[i] and (u == -1 or minD[i] < minD[u]): u = i
        vis[u] = True; cost += minD[u]
        for v in range(n):
            if not vis[v]:
                d = abs(pts[u][0]-pts[v][0]) + abs(pts[u][1]-pts[v][1])
                if d < minD[v]: minD[v] = d
    return cost""",
       """int minCostConnectPoints(vector<vector<int>>& pts) {
    int n = pts.size(), cost = 0;
    vector<int> minD(n, INT_MAX), vis(n, 0); minD[0] = 0;
    for (int step = 0; step < n; ++step) {
        int u = -1;
        for (int i = 0; i < n; ++i) if (!vis[i] && (u == -1 || minD[i] < minD[u])) u = i;
        vis[u] = 1; cost += minD[u];
        for (int v = 0; v < n; ++v) if (!vis[v])
            minD[v] = min(minD[v], abs(pts[u][0]-pts[v][0]) + abs(pts[u][1]-pts[v][1]));
    }
    return cost;
}"""),

    _p(148, "Swim in Rising Water", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Hard", ["Google", "Uber"], "swim-in-rising-water",
       "Minimax Path -> Dijkstra storing `(max_elevation_so_far, r, c)` in Min-Heap! Stop the instant you pop (N-1, N-1).",
       "Path bottleneck cost is max cell height along the route.",
       "Time: O(N^2 log N), Space: O(N^2)",
       """import heapq
def swimInWater(grid):
    n = len(grid); h = [(grid[0][0], 0, 0)]; vis = {(0,0)}
    while h:
        t, r, c = heapq.heappop(h)
        if r == n - 1 and c == n - 1: return t
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0<=nr<n and 0<=nc<n and (nr,nc) not in vis:
                vis.add((nr,nc)); heapq.heappush(h, (max(t, grid[nr][nc]), nr, nc))""",
       """int swimInWater(vector<vector<int>>& g) {
    int n = g.size(), d[5]={1,0,-1,0,1};
    priority_queue<tuple<int,int,int>, vector<tuple<int,int,int>>, greater<>> pq;
    vector<vector<int>> vis(n, vector<int>(n, 0));
    pq.push({g[0][0], 0, 0}); vis[0][0] = 1;
    while (!pq.empty()) {
        auto [t, r, c] = pq.top(); pq.pop();
        if (r == n-1 && c == n-1) return t;
        for (int k = 0; k < 4; ++k) {
            int nr = r+d[k], nc = c+d[k+1];
            if (nr>=0 && nr<n && nc>=0 && nc<n && !vis[nr][nc]) {
                vis[nr][nc] = 1; pq.push({max(t, g[nr][nc]), nr, nc});
            }
        }
    }
    return -1;
}"""),

    _p(149, "Path With Minimum Effort", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Google", "Meta"], "path-with-minimum-effort",
       "Dijkstra on Grid where edge weight is `abs(h[nr][nc] - h[r][c])` and path cost is `max(effort, edge_weight)`!",
       "First time (R-1, C-1) is popped from Min-Heap is guaranteed optimal effort.",
       "Time: O(R*C log(R*C)), Space: O(R*C)",
       """import heapq
def minimumEffortPath(h):
    R, C = len(h), len(h[0]); eff = [[float('inf')]*C for _ in range(R)]; eff[0][0] = 0
    pq = [(0, 0, 0)]
    while pq:
        e, r, c = heapq.heappop(pq)
        if r == R - 1 and c == C - 1: return e
        if e > eff[r][c]: continue
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0<=nr<R and 0<=nc<C:
                ne = max(e, abs(h[nr][nc] - h[r][c]))
                if ne < eff[nr][nc]: eff[nr][nc] = ne; heapq.heappush(pq, (ne, nr, nc))""",
       """int minimumEffortPath(vector<vector<int>>& h) {
    int R = h.size(), C = h[0].size(), d[5]={1,0,-1,0,1};
    vector<vector<int>> eff(R, vector<int>(C, INT_MAX)); eff[0][0] = 0;
    priority_queue<tuple<int,int,int>, vector<tuple<int,int,int>>, greater<>> pq; pq.push({0, 0, 0});
    while (!pq.empty()) {
        auto [e, r, c] = pq.top(); pq.pop();
        if (r == R-1 && c == C-1) return e;
        if (e > eff[r][c]) continue;
        for (int k = 0; k < 4; ++k) {
            int nr = r+d[k], nc = c+d[k+1];
            if (nr>=0 && nr<R && nc>=0 && nc<C) {
                int ne = max(e, abs(h[nr][nc] - h[r][c]));
                if (ne < eff[nr][nc]) { eff[nr][nc] = ne; pq.push({ne, nr, nc}); }
            }
        }
    }
    return 0;
}"""),

    _p(150, "Accounts Merge (DSU on Strings)", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Meta", "LinkedIn", "Razorpay"], "accounts-merge",
       "Map every email -> first seen account_id! Whenever an email repeats, union(current_id, owner_id) in DSU, then group emails by find(id)!",
       "Avoids building quadratic email edges.",
       "Time: O(N log N), Space: O(N)",
       """from collections import defaultdict
def accountsMerge(accounts):
    par = list(range(len(accounts)))
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    owner = {}
    for i, acc in enumerate(accounts):
        for email in acc[1:]:
            if email in owner: par[find(i)] = find(owner[email])
            else: owner[email] = i
    groups = defaultdict(list)
    for email, i in owner.items(): groups[find(i)].append(email)
    return [[accounts[i][0]] + sorted(emails) for i, emails in groups.items()]""",
       """vector<vector<string>> accountsMerge(vector<vector<string>>& accs) {
    int n = accs.size(); vector<int> par(n); iota(par.begin(), par.end(), 0);
    function<int(int)> find = [&](int x) { return par[x]==x ? x : par[x]=find(par[x]); };
    unordered_map<string, int> own;
    for (int i = 0; i < n; ++i)
        for (int j = 1; j < accs[i].size(); ++j) {
            if (own.count(accs[i][j])) par[find(i)] = find(own[accs[i][j]]);
            else own[accs[i][j]] = i;
        }
    unordered_map<int, vector<string>> grp;
    for (auto& [e, id] : own) grp[find(id)].push_back(e);
    vector<vector<string>> res;
    for (auto& [id, es] : grp) {
        sort(es.begin(), es.end()); es.insert(es.begin(), accs[id][0]); res.push_back(move(es));
    }
    return res;
}"""),

    _p(151, "Alien Dictionary (Topological Sort)", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Hard", ["Google", "Airbnb", "CRED"], "alien-dictionary",
       "Compare adjacent word pairs (w1, w2): first mismatching char adds directed edge w1[j] -> w2[j]. Edge case: if len(w1) > len(w2) and w1 starts with w2 -> invalid!",
       "Run Kahn's BFS over active unique characters.",
       "Time: O(TotalChars), Space: O(1)",
       """from collections import deque
def alienOrder(words):
    adj = {c: set() for w in words for c in w}
    ind = {c: 0 for c in adj}
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]
        if len(w1) > len(w2) and w1[:len(w2)] == w2: return ""
        for a, b in zip(w1, w2):
            if a != b:
                if b not in adj[a]: adj[a].add(b); ind[b] += 1
                break
    q = deque([c for c in ind if ind[c] == 0]); res = []
    while q:
        u = q.popleft(); res.append(u)
        for v in adj[u]:
            ind[v] -= 1
            if ind[v] == 0: q.append(v)
    return "".join(res) if len(res) == len(adj) else "" """,
       """string alienOrder(vector<string>& words) {
    unordered_map<char, unordered_set<char>> adj; unordered_map<char, int> ind;
    for (auto& w : words) for (char c : w) ind[c] = 0;
    for (int i = 0; i + 1 < words.size(); ++i) {
        string &w1 = words[i], &w2 = words[i+1];
        if (w1.size() > w2.size() && w1.rfind(w2, 0) == 0) return "";
        for (int j = 0; j < min(w1.size(), w2.size()); ++j) if (w1[j] != w2[j]) {
            if (!adj[w1[j]].count(w2[j])) { adj[w1[j]].insert(w2[j]); ind[w2[j]]++; }
            break;
        }
    }
    queue<char> q; for (auto& [c, d] : ind) if (d == 0) q.push(c);
    string res;
    while (!q.empty()) {
        char u = q.front(); q.pop(); res += u;
        for (char v : adj[u]) if (--ind[v] == 0) q.push(v);
    }
    return res.size() == ind.size() ? res : "";
}"""),

    _p(152, "Reconstruct Itinerary (Eulerian Path)", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Hard", ["Uber", "Google"], "reconstruct-itinerary",
       "Hierholzer's Algorithm: sort neighbors ascending, pop smallest edge via DFS, and append node in POST-ORDER (reverse at end)!",
       "Post-order guarantees trapped dead-end airport lands at the very end of the itinerary.",
       "Time: O(E log E), Space: O(E)",
       """from collections import defaultdict
def findItinerary(tickets):
    adj = defaultdict(list)
    for u, v in sorted(tickets, reverse=True): adj[u].append(v)
    route = []
    def dfs(u):
        while adj[u]: dfs(adj[u].pop())
        route.append(u)
    dfs("JFK")
    return route[::-1]""",
       """vector<string> findItinerary(vector<vector<string>>& tickets) {
    unordered_map<string, priority_queue<string, vector<string>, greater<string>>> adj;
    for (auto& t : tickets) adj[t[0]].push(t[1]);
    vector<string> route;
    function<void(string)> dfs = [&](string u) {
        while (!adj[u].empty()) { string v = adj[u].top(); adj[u].pop(); dfs(v); }
        route.push_back(u);
    };
    dfs("JFK"); reverse(route.begin(), route.end()); return route;
}"""),

    _p(153, "Critical Connections in a Network (Tarjan's Bridges)", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Hard", ["Amazon", "Google"], "critical-connections-in-a-network",
       "Tarjan's Bridge Finding: track discovery `disc[u]` and lowest reachable `low[u]`. Edge (u, v) is a bridge iff `low[v] > disc[u]`!",
       "Skip immediate parent edge during undirected DFS.",
       "Time: O(V + E), Space: O(V + E)",
       """def criticalConnections(n, conns):
    adj = [[] for _ in range(n)]
    for u, v in conns: adj[u].append(v); adj[v].append(u)
    disc, low, res, t = [-1]*n, [0]*n, [], [0]
    def dfs(u, p):
        disc[u] = low[u] = t[0]; t[0] += 1
        for v in adj[u]:
            if v == p: continue
            if disc[v] == -1:
                dfs(v, u); low[u] = min(low[u], low[v])
                if low[v] > disc[u]: res.append([u, v])
            else: low[u] = min(low[u], disc[v])
    dfs(0, -1); return res""",
       """vector<vector<int>> criticalConnections(int n, vector<vector<int>>& conns) {
    vector<vector<int>> adj(n), res; for (auto& c : conns) { adj[c[0]].push_back(c[1]); adj[c[1]].push_back(c[0]); }
    vector<int> disc(n, -1), low(n, 0); int timer = 0;
    function<void(int,int)> dfs = [&](int u, int p) {
        disc[u] = low[u] = timer++;
        for (int v : adj[u]) {
            if (v == p) continue;
            if (disc[v] == -1) {
                dfs(v, u); low[u] = min(low[u], low[v]);
                if (low[v] > disc[u]) res.push_back({u, v});
            } else low[u] = min(low[u], disc[v]);
        }
    };
    dfs(0, -1); return res;
}"""),

    _p(154, "Shortest Path in Binary Matrix", "Graphs: BFS, DFS, Topo, Dijkstra, DSU", "Medium", ["Meta", "Amazon"], "shortest-path-in-binary-matrix",
       "8-directional BFS starting from (0,0) with length 1; mark cell = 1 on enqueue so it isn't revisited.",
       "Immediate early exit if grid[0][0] == 1 or grid[n-1][n-1] == 1.",
       "Time: O(N^2), Space: O(N^2)",
       """from collections import deque
def shortestPathBinaryMatrix(grid):
    n = len(grid)
    if grid[0][0] or grid[n-1][n-1]: return -1
    q = deque([(0, 0, 1)]); grid[0][0] = 1
    while q:
        r, c, d = q.popleft()
        if r == n - 1 and c == n - 1: return d
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r+dr, c+dc
                if 0<=nr<n and 0<=nc<n and grid[nr][nc] == 0:
                    grid[nr][nc] = 1; q.append((nr, nc, d + 1))
    return -1""",
       """int shortestPathBinaryMatrix(vector<vector<int>>& g) {
    int n = g.size(); if (g[0][0] || g[n-1][n-1]) return -1;
    queue<tuple<int,int,int>> q; q.push({0, 0, 1}); g[0][0] = 1;
    while (!q.empty()) {
        auto [r, c, d] = q.front(); q.pop();
        if (r == n-1 && c == n-1) return d;
        for (int dr = -1; dr <= 1; ++dr) for (int dc = -1; dc <= 1; ++dc) {
            int nr = r+dr, nc = c+dc;
            if (nr>=0 && nr<n && nc>=0 && nc<n && g[nr][nc] == 0) { g[nr][nc] = 1; q.push({nr, nc, d + 1}); }
        }
    }
    return -1;
}"""),
]
