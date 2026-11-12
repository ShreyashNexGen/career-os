BUILDING_BLOCKS = [
    {
        "id": "bb-btree",
        "title": "B-Tree Indexing & SQL Query Tuning",
        "tag": "Database Internals",
        "summary": "Why composite index order (Leftmost Prefix Rule) drops query latency from ~850ms to <15ms.",
        "intuition": "A B+Tree stores sorted keys in balanced disk pages (O(log N) height ~3-4 even for 100M rows). Leaf nodes are doubly-linked so range scans (`created_at >= ...`) read sequentially instead of random seeks.",
        "key_rules": [
            "Leftmost Prefix Rule: An index on (brand_id, status, created_at) accelerates queries filtering (brand_id), (brand_id, status), or all 3 — NOT (status, created_at) alone.",
            "Equality Columns First, Range Columns Last: Put '=' predicates (tenant_id, status) before range predicates (>, BETWEEN).",
            "Covering Index: Including queried columns avoids table heap lookups altogether (Index-Only Scan)."
        ],
        "diagram": "Query: WHERE brand_id=7 AND status='LIVE' ORDER BY created_at DESC\nRoot Page [brand_id] -> Branch [status] -> Leaf Doubly-Linked List [sorted created_at] (0 heap scans if covered!)"
    },
    {
        "id": "bb-redis",
        "title": "Redis Caching & Stampede Protection",
        "tag": "Low-Latency Caching",
        "summary": "Cache-Aside vs Write-Through, Hot Keys, and stopping Cache Stampede (Thundering Herd) at 10x traffic.",
        "intuition": "Read from Redis first; on miss, read DB and populate Redis with a TTL. Danger: when a viral key expires, 5,000 requests miss simultaneously and crush MySQL/Postgres.",
        "key_rules": [
            "Cache-Aside: Lazy load on miss; safest general pattern for read-heavy APIs.",
            "Jittered TTL: Add random +/- 15% jitter to expiry times so batches of keys don't expire together.",
            "Mutex / Single-Flight Lock: On cache miss, only 1 worker acquires `SET lock:key 1 NX EX 5` to query DB while others wait/serve stale.",
            "Penetration Guard: Cache `NULL` / empty sentinel for 30s when nonexistent IDs are queried repeatedly."
        ],
        "diagram": "Client -> API -> Redis GET(k)\n  |-- HIT  --> Return (<2ms)\n  |-- MISS --> Acquire Redis SETNX lock -> Query DB (Pool capped) -> SETEX(k, TTL+jitter) -> Release lock"
    },
    {
        "id": "bb-ratelimit",
        "title": "Rate Limiting Algorithms",
        "tag": "API Gateway & Resiliency",
        "summary": "Token Bucket vs Sliding Window Log vs Fixed Window Counter in distributed Redis clusters.",
        "intuition": "Protect downstream microservices and AI endpoints from DDoS, scrapers, and burst spikes without rejecting legitimate traffic.",
        "key_rules": [
            "Fixed Window Counter: Simplest (`INCR user:min`), but allows 2x burst across minute boundary.",
            "Token Bucket (Industry Standard): Bucket refills at R tokens/sec up to Burst Cap C. Allows smooth controlled bursts.",
            "Sliding Window Counter: Weighted overlap of prev + current window counter; ~99.9% accurate with O(1) memory.",
            "Atomic Distributed State: Execute check-and-decrement inside a single Redis Lua script so concurrent nodes never race."
        ],
        "diagram": "Req -> Gateway -> Redis Lua Script(key, now, rate, burst)\n  |-- tokens >= 1 --> tokens -= 1, HTTP 200\n  |-- tokens < 1  --> HTTP 429 Too Many Requests + Retry-After header"
    },
    {
        "id": "bb-queues",
        "title": "Async Queues: BullMQ / Redis vs Kafka",
        "tag": "Event-Driven Architecture",
        "summary": "Decoupling slow work (video encoding, webhooks, emails) from sub-50ms HTTP request threads.",
        "intuition": "Never block an API response waiting on third-party webhooks or heavy processing. Enqueue a lightweight job ID, return 202 Accepted immediately, and let workers process with retries.",
        "key_rules": [
            "BullMQ (Redis-backed): Ideal for job scheduling, delayed retries, rate-limited background tasks in Node.js startups.",
            "Kafka: Immutable partitioned append-only log for high-throughput event streaming (1M+ events/sec), replayability, and multiple independent consumer groups.",
            "Dead Letter Queue (DLQ): After N exponential-backoff retries, move poison messages to a DLQ so healthy jobs aren't blocked."
        ],
        "diagram": "API (202 Accepted) -> Queue/Topic [Partitioned] -> Worker Pool\n  |-- Success --> Ack + Commit Offset\n  |-- Failure --> Exponential Backoff Retry (3x) -> Dead Letter Queue (Alert)"
    },
    {
        "id": "bb-sharding",
        "title": "Database Replication & Horizontal Sharding",
        "tag": "Scale & High Availability",
        "summary": "Moving from 1 primary DB to Read Replicas, Connection Pooling (PgBouncer), and Tenant Sharding.",
        "intuition": "Vertical scaling hits ceiling fast; 90% of apps are read-heavy. Route writes to Primary, reads to Replicas first—only shard when write IOPS or storage outgrows a single beefy machine.",
        "key_rules": [
            "Connection Pooling: Node/Python workers hold limited pools via PgBouncer/ProxySQL so autoscaling containers don't exhaust max_connections.",
            "Replication Lag Trap: Read-your-own-writes immediately after signup/payment must hit Primary or read from Redis session cache.",
            "Shard Key Selection: Pick high-cardinality key aligned with access patterns (e.g., `brand_id` or `user_id`), avoiding hot shards."
        ],
        "diagram": "Writes --> Primary DB --(Async WAL Stream)--> Read Replica 1 & 2\n  (Critical Read-After-Write routes to Primary for 2s)"
    },
    {
        "id": "bb-conhash",
        "title": "Consistent Hashing & Virtual Nodes",
        "tag": "Distributed Systems",
        "summary": "Why `hash(k) % N` breaks caches during node crashes, and how a hash ring fixes it.",
        "intuition": "Modulo hashing remaps ~90% of keys whenever N changes by 1. Consistent hashing maps nodes and keys onto a [0, 2^32-1] ring so adding/removing 1 server only moves K/N keys.",
        "key_rules": [
            "Virtual Nodes (VNodes): Place each physical server at 100-200 positions on the ring so load distributes uniformly even with few nodes.",
            "Lookup: Binary search (TreeMap / bisect) clockwise for first VNode >= hash(key) in O(log(Nodes * VNodes))."
        ],
        "diagram": "Hash Ring [0 .. 2^32-1]: Key H(x) walks clockwise -> Hits Server_B (VNode #42)\nIf Server_B dies -> Only its slice shifts clockwise to Server_C!"
    },
    {
        "id": "bb-idempotency",
        "title": "Idempotency Keys & Distributed Locks",
        "tag": "Payments & Reliability",
        "summary": "Guaranteeing a user is NEVER charged or paid twice even if mobile retries or webhooks fire 5 times.",
        "intuition": "Network timeouts are ambiguous—you never know if the server succeeded before dropping the response. Require the client to generate a UUID `Idempotency-Key` per intent.",
        "key_rules": [
            "Two-Layer Guard: (1) Redis SETNX short lock on key to serialize simultaneous retries, (2) DB UNIQUE constraint on `idempotency_key` inside ACID transaction.",
            "Snapshot Response: Store final HTTP status + JSON body alongside the key so retries replay exact original result safely.",
            "Outbox Pattern: Insert DB ledger row + event outbox row in ONE local ACID transaction instead of dual-writing DB + Kafka."
        ],
        "diagram": "POST /pay [Idempotency-Key: uuid-91]\n  -> Redis Lock + Check DB `idempotency_keys`\n  -> Exists? Return cached receipt!\n  -> New? BEGIN TX -> Debit + Insert Key -> COMMIT -> Publish Event"
    },
    {
        "id": "bb-realtime",
        "title": "WebSockets vs Server-Sent Events (SSE) vs Polling",
        "tag": "Real-Time Systems",
        "summary": "Picking the lightest protocol for chat, AI streaming, live notifications, and location tracking.",
        "intuition": "Don't default to heavy stateful WebSockets when data flows one way!",
        "key_rules": [
            "Short/Long Polling: Simple fallback; high server request overhead at scale.",
            "Server-Sent Events (SSE): Built on standard HTTP, auto-reconnects, ideal for **AI token streaming**, live dashboards, stock tickers (server -> client only).",
            "WebSockets: Full-duplex bidirectional persistent TCP tunnel, ideal for **multiplayer chat, live rider telemetry, collaborative editing**. Scale horizontally with Redis Pub/Sub across WS servers."
        ],
        "diagram": "Client A --WS--> Gateway Node 1 --Publish--> Redis Pub/Sub --Deliver--> Gateway Node 2 --WS--> Client B"
    }
]


CASE_STUDIES = [
    {
        "id": "cs-zepto",
        "type": "HLD",
        "title": "Swiggy / Zepto: Hyperlocal Rider Dispatch & Inventory Locking",
        "companies": ["Zepto", "Swiggy", "Blinkit", "Zomato"],
        "scale": "50,000+ concurrent orders/min | Sub-100ms dark-store inventory check | 3s GPS pings",
        "summary": "How 10-minute delivery platforms track moving riders via Geohashing and guarantee zero overselling when 50 users checkout the last milk carton simultaneously.",
        "steps": [
            "1. Rider Location Ingestion: Riders stream (lat, lng) every 3s over WebSockets/UDP -> Ingestion Gateway batches updates -> Redis GEOADD (`riders:city`) using Geohash spatial cells with 15s TTL.",
            "2. Dark Store Mapping: On app open, user's (lat, lng) maps to nearest serviceable Dark Store Polygon (cached by Geohash prefix in Redis).",
            "3. Zero-Oversell Cart & Checkout: Product stock lives in Redis (`DECRBY` Lua script checks `stock >= qty` atomically before creating order) + durable async sync to Postgres Inventory table.",
            "4. Dispatch Matching Engine: Order Confirmed event hits Kafka -> Dispatch Service runs `GEOSEARCH` within 3km radius -> Scores top 5 free riders by ETA + battery + heading -> Sends push offer with 15s Redis lock (`rider:lock:id`)."
        ],
        "tradeoffs": [
            "Redis GEO vs QuadTree in memory: Redis GEO gives built-in O(N + log M) radius queries with automatic TTL expiry if a rider loses signal.",
            "Atomic Lua Decrement vs DB Pessimistic Lock (`SELECT FOR UPDATE`): Lua prevents DB row-lock pileups during flash sales; DB reconciles on payment confirmation."
        ],
        "diagram": "Rider App --3s GPS--> WS Gateway -> Redis GEOADD\nCheckout -> API -> Redis Lua Atomic Stock Lock -> Kafka(order.placed) -> Dispatch Worker (GEOSEARCH 3km) -> Lock Rider + Push"
    },
    {
        "id": "cs-razorpay",
        "type": "HLD",
        "title": "Razorpay / UPI: Idempotent Payment Gateway & Ledger",
        "companies": ["Razorpay", "CRED", "PhonePe", "Juspay"],
        "scale": "10,000+ TPS | 99.99% Availability | Strict ACID Double-Entry Accounting",
        "summary": "Designing a fault-tolerant payment switch that prevents double debits during network flaps, bank timeouts, and duplicate webhooks.",
        "steps": [
            "1. Idempotent Gateway: Client generates UUID `Idempotency-Key`. Gateway enforces Redis distributed lock + Postgres unique constraint so network retries return identical payment status.",
            "2. State Machine & Double-Entry Ledger: Never just `balance -= 100`! Record immutable Debit/Credit ledger rows inside an ACID Postgres transaction (`SERIALIZABLE` or row-level locks ordered by account_id to prevent deadlocks).",
            "3. Bank / PSP Routing & Circuit Breaker: Payment Executor selects PSP (HDFC/ICICI/Axis) dynamically based on real-time sliding-window success rates. If HDFC latency spikes, Circuit Breaker trips and auto-routes to Axis.",
            "4. Webhook Delivery & Reconciliation: Transactional Outbox publishes `payment.captured` to Queue -> Webhook Worker delivers with HMAC signature + exponential backoff. Nightly/hourly Cron compares internal ledger against bank settlement files."
        ],
        "tradeoffs": [
            "Double-Entry Immutable Ledger vs Mutable Balance Column: Immutable append-only rows provide 100% auditability and catch reconciliation mismatches immediately.",
            "Deadlock Prevention: Always acquire locks in deterministic ascending order of `account_id` during wallet-to-wallet transfers."
        ],
        "diagram": "Client -> Gateway (Idempotency Check) -> Ledger TX (Outbox) -> PSP Router (Circuit Breaker) -> Bank UPI\nBank Webhook -> HMAC Verify -> Queue -> Merchant Webhook (Exp Backoff)"
    },
    {
        "id": "cs-bms",
        "type": "HLD",
        "title": "BookMyShow: High-Concurrency Seat Locking Engine",
        "companies": ["BookMyShow", "Dream11", "Uber", "Paytm Insider"],
        "scale": "500,000 concurrent users for Coldplay/IPL tickets | 10-minute seat hold TTL",
        "summary": "Handling extreme contention where thousands of users click the exact same front-row seats in the same millisecond.",
        "steps": [
            "1. Virtual Waiting Room (Token Queue): During mega events, Edge/Redis issues queue tickets so backend checkout servers never get flooded beyond capacity.",
            "2. Two-Phase Seat State: Seats transition `AVAILABLE -> LOCKED (10m) -> BOOKED`.",
            "3. Redis Hold Layer: When user clicks Seat A12, API runs Redis `SET seat:show_9:A12 user_42 NX EX 600`. Only ONE user globally succeeds in <2ms! Seats auto-unlock after 10 minutes via Redis TTL if payment drops.",
            "4. Optimistic DB Confirmation: On payment webhook success, Postgres executes `UPDATE seats SET status='BOOKED', version=version+1 WHERE id='A12' AND version=old_ver` inside transaction -> clears Show Map cache."
        ],
        "tradeoffs": [
            "Redis NX EX 600 vs Holding DB Transactions Open for 10 mins: Never hold SQL transactions across user payment wait time! Redis TTL locks free Postgres connections completely.",
            "CDN / Cache Invalidation: Serve read-heavy seat layout JSON from short-TTL Redis/CDN updated asynchronously via Pub/Sub."
        ],
        "diagram": "Users -> Virtual Queue -> Seat Map (Cached Read)\nSelect Seat A12 -> Redis `SET NX EX 600` (1 Winner!)\nPay Success -> Postgres Optimistic Update (version check) -> Publish Seat Update"
    },
    {
        "id": "cs-viralme",
        "type": "HLD",
        "title": "ViralMe CreatorOS: High-Throughput UGC & Analytics Pipeline",
        "companies": ["ViralMe", "ShareChat", "Shopify", "CleverTap"],
        "scale": "1,000+ creator installs | 30%+ WoW growth | High-burst campaign webhook tracking",
        "summary": "Designing the exact backend behind CreatorOS: real-time UGC link attribution, creator payout escrow, and fast brand analytics dashboards.",
        "steps": [
            "1. Edge Attribution & Click Tracking: Creator links (`viralme.onelink.me/...`) resolve at Edge Worker -> Async fire-and-forget click event pushed to Redis Stream / BullMQ -> Instant 302 redirect in <15ms.",
            "2. Media Upload Offloading: Creator mobile apps NEVER upload 100MB reels through Node.js API servers! API generates **Pre-Signed Cloudflare R2 / S3 URLs** so media uploads directly from mobile -> Object Store, triggering webhook completion.",
            "3. Hot Counter Aggregation: Avoid hammering MySQL/Postgres with `+1 view` writes. Accumulate live campaign metrics in Redis `HINCRBY` and flush batch totals to RDBMS every 30 seconds.",
            "4. Dashboard Queries: Index Postgres/MySQL tables with composite B-Tree `(brand_id, campaign_id, created_at)` + cache aggregated brand reports for 60s."
        ],
        "tradeoffs": [
            "Pre-Signed Direct Upload vs Proxy Upload: Keeps Node.js event loop non-blocking and saves 2x bandwidth cost.",
            "Buffered Redis `HINCRBY` Flush vs Direct DB Increment: Survives viral creator spikes without row-lock contention."
        ],
        "diagram": "Creator Mobile -> Request Pre-Signed S3/R2 URL -> Direct Video Upload\nClick/View Events -> Edge -> BullMQ/Redis Flush (30s) -> MySQL (Composite B-Tree) -> Brand Dashboard"
    },
    {
        "id": "cs-whatsapp",
        "type": "HLD",
        "title": "WhatsApp: Real-Time 1:1 & Group Chat Architecture",
        "companies": ["WhatsApp", "Slack", "Discord", "Gupshup"],
        "scale": "50B+ messages/day | <100ms delivery | Guaranteed message ordering & offline sync",
        "summary": "Persistent WebSocket gateway fleet, presence heartbeats, offline queue storage, and group fan-out.",
        "steps": [
            "1. Stateful WebSocket Gateways: Clients maintain persistent TLS WebSocket connections to Gateway Nodes. A Session Registry (Redis: `user_id -> gateway_node_ip`) tracks who is connected where.",
            "2. 1:1 Delivery Flow: User A sends msg -> Gateway A generates Snowflake/ULID monotonic message ID -> Writes to Cassandra/ScyllaDB (partitioned by `chat_id`, clustered by `msg_id` DESC) -> Looks up User B in Session Registry -> Routes via internal RPC/Redis PubSub to Gateway B -> ACK sent back to User A ('Double Tick').",
            "3. Offline Handling: If User B is offline, message stays persisted in Undelivered Inbox DB + triggers Push Notification (FCM/APNs). On reconnect, client syncs since `last_ack_msg_id`.",
            "4. Group Fan-out & Presence: Groups (<512 members) fan out message IDs to members' queues asynchronously. Online/Last-Seen heartbeats ping every 10s with lazy fetch on chat open."
        ],
        "tradeoffs": [
            "Cassandra / ScyllaDB vs MySQL for Messages: Time-series append-heavy message logs partitioned by `(chat_id, bucket)` scale horizontally with fast range scans.",
            "Lazy Presence vs Broadcast Presence: Only query/subscribe presence of contacts currently visible in UI instead of broadcasting every online status change."
        ],
        "diagram": "User A --WS--> Chat Gateway 1 -> Persist (Cassandra) + Lookup Session(Redis)\n  |-- B Online  --> Forward to Gateway 2 --WS--> User B\n  |-- B Offline --> Hold Undelivered + FCM Push"
    },
    {
        "id": "cs-lld-ratelimiter",
        "type": "LLD",
        "title": "LLD Machine Coding: Thread-Safe Token Bucket Rate Limiter",
        "companies": ["Atlassian", "Razorpay", "Stripe", "CRED"],
        "scale": "60-min Machine Coding Round | Clean OOP + Thread Safety + Zero Stale Background Threads",
        "summary": "Production-grade Token Bucket Rate Limiter written cleanly without background refill timers (lazy time-delta refill on `allowRequest`).",
        "steps": [
            "1. Lazy Refill Trick: Instead of spawning a background timer thread for millions of users, store `(tokens, last_refill_ts)` per key and refill `elapsed * rate` on demand inside `allowRequest()`.",
            "2. Strategy Interface: Define `RateLimiter` abstraction so caller can swap TokenBucket vs SlidingWindowLog cleanly (Open-Closed Principle).",
            "3. Per-Key Concurrency Lock: Use per-user mutex (or striped lock) instead of 1 global lock so User A doesn't block User B."
        ],
        "tradeoffs": [
            "Lazy Refill vs Background Refill Thread: O(1) idle memory, zero thread-pool overhead, trivial to port to Redis Lua.",
            "Floating-Point Precision vs Nanosecond Integers: Using float monotonic clock (`time.monotonic()` / `steady_clock`) prevents wall-clock NTP backward jumps."
        ],
        "diagram": "RateLimiter (Interface) <-- TokenBucketLimiter\nState per user: { tokens: double, lastTs: monotonic_ns }\nallowRequest(userId): lock(user) -> add elapsed*rate (cap max) -> if >=1: tokens-=1, True else False",
        "python_code": """import time, threading

class TokenBucket:
    def __init__(self, capacity: int, refill_per_sec: float):
        self.capacity = float(capacity)
        self.rate = refill_per_sec
        self.tokens = float(capacity)
        self.last_ts = time.monotonic()
        self.lock = threading.Lock()

    def allow(self) -> bool:
        with self.lock:
            now = time.monotonic()
            self.tokens = min(self.capacity, self.tokens + (now - self.last_ts) * self.rate)
            self.last_ts = now
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False

class RateLimiterService:
    def __init__(self, capacity: int, refill_per_sec: float):
        self.cap, self.rate = capacity, refill_per_sec
        self.buckets, self.map_lock = {}, threading.Lock()

    def allow_request(self, user_id: str) -> bool:
        with self.map_lock:
            if user_id not in self.buckets:
                self.buckets[user_id] = TokenBucket(self.cap, self.rate)
            bucket = self.buckets[user_id]
        return bucket.allow()""",
        "cpp_code": """#include <bits/stdc++.h>
using namespace std;

class TokenBucket {
    double cap, rate, tokens;
    chrono::steady_clock::time_point last_ts;
    mutex mtx;
public:
    TokenBucket(double c, double r) : cap(c), rate(r), tokens(c), last_ts(chrono::steady_clock::now()) {}
    bool allow() {
        lock_guard<mutex> lock(mtx);
        auto now = chrono::steady_clock::now();
        double elapsed = chrono::duration<double>(now - last_ts).count();
        tokens = min(cap, tokens + elapsed * rate);
        last_ts = now;
        if (tokens >= 1.0) { tokens -= 1.0; return true; }
        return false;
    }
};

class RateLimiterService {
    double cap, rate; mutex map_mtx;
    unordered_map<string, shared_ptr<TokenBucket>> buckets;
public:
    RateLimiterService(double c, double r) : cap(c), rate(r) {}
    bool allowRequest(const string& userId) {
        shared_ptr<TokenBucket> b;
        {
            lock_guard<mutex> lk(map_mtx);
            if (!buckets.count(userId)) buckets[userId] = make_shared<TokenBucket>(cap, rate);
            b = buckets[userId];
        }
        return b->allow();
    }
};"""
    },
    {
        "id": "cs-lld-lru",
        "type": "LLD",
        "title": "LLD Machine Coding: Generic Thread-Safe LRU Cache with TTL",
        "companies": ["Atlassian", "Zepto", "Amazon", "Flipkart"],
        "scale": "O(1) Get / Put / Evict | Per-Entry TTL Expiration | Clean Doubly-Linked List + HashMap",
        "summary": "Beyond LeetCode LRU: production machine coding adds generic types, optional TTL expiry, and thread-safe mutex synchronization.",
        "steps": [
            "1. Core Data Structures: HashMap (`key -> Node*`) for O(1) lookup + Doubly Linked List with sentinel dummy `head` (MRU) and `tail` (LRU) for O(1) detach & insert.",
            "2. TTL Support: Store `expires_at` on each node; on `get(key)`, if expired, evict node immediately and return None / -1.",
            "3. Eviction Policy Extensibility: Keep eviction separate behind `CachePolicy` if asked to support LFU later."
        ],
        "tradeoffs": [
            "Lazy Expiry vs Active Sweeper: Lazy check on `get` + optional periodic sample sweep matches Redis's real expiration strategy.",
            "Dummy Sentinels: Completely eliminate null head/tail edge-case bugs during 45-minute coding rounds."
        ],
        "diagram": "Map: key -> Node*\nDLL: [Head] <-> [Most Recent] <-> ... <-> [Least Recent] <-> [Tail]\nget(k): check TTL -> detach(node) -> insertAfter(head)",
        "python_code": """import time, threading

class _Node:
    def __init__(self, k=None, v=None, exp=None):
        self.k, self.v, self.exp = k, v, exp
        self.prev = self.next = None

class TTLLRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map = {}
        self.lock = threading.Lock()
        self.head, self.tail = _Node(), _Node()
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _insert_front(self, node):
        node.next, node.prev = self.head.next, self.head
        self.head.next.prev = node; self.head.next = node

    def get(self, key):
        with self.lock:
            if key not in self.map: return None
            node = self.map[key]
            if node.exp and time.monotonic() > node.exp:
                self._remove(node); del self.map[key]; return None
            self._remove(node); self._insert_front(node)
            return node.v

    def put(self, key, value, ttl_sec: float = None):
        with self.lock:
            exp = (time.monotonic() + ttl_sec) if ttl_sec else None
            if key in self.map:
                self._remove(self.map[key])
                self.map[key].v, self.map[key].exp = value, exp
                self._insert_front(self.map[key]); return
            if len(self.map) >= self.cap:
                lru = self.tail.prev; self._remove(lru); del self.map[lru.k]
            node = _Node(key, value, exp)
            self.map[key] = node; self._insert_front(node)""",
        "cpp_code": """#include <bits/stdc++.h>
using namespace std;

template<typename K, typename V>
class TTLLRUCache {
    struct Entry { K key; V val; chrono::steady_clock::time_point exp; bool has_ttl; };
    size_t cap; mutex mtx;
    list<Entry> dll;
    unordered_map<K, typename list<Entry>::iterator> mp;
public:
    TTLLRUCache(size_t c) : cap(c) {}
    optional<V> get(const K& key) {
        lock_guard<mutex> lk(mtx);
        if (!mp.count(key)) return nullopt;
        auto it = mp[key];
        if (it->has_ttl && chrono::steady_clock::now() > it->exp) {
            dll.erase(it); mp.erase(key); return nullopt;
        }
        dll.splice(dll.begin(), dll, it);
        return it->val;
    }
    void put(const K& key, const V& val, int ttl_ms = -1) {
        lock_guard<mutex> lk(mtx);
        bool has_ttl = ttl_ms > 0;
        auto exp = chrono::steady_clock::now() + chrono::milliseconds(max(0, ttl_ms));
        if (mp.count(key)) {
            mp[key]->val = val; mp[key]->exp = exp; mp[key]->has_ttl = has_ttl;
            dll.splice(dll.begin(), dll, mp[key]); return;
        }
        if (dll.size() >= cap) { mp.erase(dll.back().key); dll.pop_back(); }
        dll.push_front({key, val, exp, has_ttl});
        mp[key] = dll.begin();
    }
};"""
    },
    {
        "id": "cs-lld-splitwise",
        "type": "LLD",
        "title": "LLD Machine Coding: Splitwise Expense Ledger & Debt Simplifier",
        "companies": ["Flipkart", "PhonePe", "Swiggy", "Razorpay"],
        "scale": "60-90 min Indian Startup Machine Coding Round | Strategy Pattern + Greedy Debt Simplification",
        "summary": "Clean extensible OOP for Equal, Exact, and Percentage splits plus greedy min-cash-flow settlement.",
        "steps": [
            "1. Entities: `User`, `Expense`, `Split` (`EqualSplit`, `ExactSplit`, `PercentSplit`), `ExpenseManager`.",
            "2. Strategy / Validation: Each split strategy validates constraints cleanly (e.g., Exact splits sum == amount; Percent splits sum == 100.0%).",
            "3. Net Balance Ledger: Track net balance per user (`+` means owed money, `-` means owes money). Greedy simplification pairs largest creditor with largest debtor in O(N log N) using two heaps!"
        ],
        "tradeoffs": [
            "Floating-point cents vs Integer Paise: Always store money as integer paise/cents (`int`) in real fintech systems to eliminate rounding drift!",
            "Pairwise Balance Matrix vs Net Balance Simplification: Net balance reduces N*(N-1)/2 transactions down to at most N-1 settlements."
        ],
        "diagram": "ExpenseManager --(Strategy)--> Equal / Exact / Percent Validator\nBalances[user] += paid - share\nSimplify: MaxCreditor Heap <-> MaxDebtor Heap -> Min Transactions",
        "python_code": """from collections import defaultdict
import heapq

class SplitwiseManager:
    def __init__(self):
        self.net = defaultdict(int) # store in paise/cents (int) to avoid float bugs

    def add_expense(self, paid_by: str, amount_cents: int, participants: list[str], split_type="EQUAL", values=None):
        n = len(participants)
        if split_type == "EQUAL":
            share, rem = divmod(amount_cents, n)
            shares = [share + (1 if i < rem else 0) for i in range(n)]
        elif split_type == "EXACT":
            assert sum(values) == amount_cents, "Exact splits must equal total"
            shares = values
        elif split_type == "PERCENT":
            assert abs(sum(values) - 100.0) < 1e-6, "Percent must sum to 100"
            shares = [round(amount_cents * p / 100.0) for p in values]
        else:
            raise ValueError("Unsupported split type")

        self.net[paid_by] += amount_cents
        for u, s in zip(participants, shares):
            self.net[u] -= s

    def simplify_debts(self):
        creditors = [(-bal, u) for u, bal in self.net.items() if bal > 0]
        debtors = [(bal, u) for u, bal in self.net.items() if bal < 0]
        heapq.heapify(creditors); heapq.heapify(debtors)
        txns = []
        while creditors and debtors:
            neg_c, cred = heapq.heappop(creditors)
            d_bal, debt = heapq.heappop(debtors)
            amt = min(-neg_c, -d_bal)
            txns.append(f"{debt} pays {cred}: {amt}")
            if -neg_c > amt: heapq.heappush(creditors, (-( -neg_c - amt ), cred))
            if -d_bal > amt: heapq.heappush(debtors, (d_bal + amt, debt))
        return txns""",
        "cpp_code": """#include <bits/stdc++.h>
using namespace std;

class SplitwiseManager {
    unordered_map<string, long long> net; // store integer cents/paise
public:
    void addEqualExpense(const string& paidBy, long long amt, const vector<string>& users) {
        long long n = users.size(), share = amt / n, rem = amt % n;
        net[paidBy] += amt;
        for (int i = 0; i < n; ++i) net[users[i]] -= (share + (i < rem ? 1 : 0));
    }
    void addExactExpense(const string& paidBy, long long amt, const vector<string>& users, const vector<long long>& vals) {
        net[paidBy] += amt;
        for (size_t i = 0; i < users.size(); ++i) net[users[i]] -= vals[i];
    }
    vector<string> simplifyDebts() {
        priority_queue<pair<long long, string>> cred, debt;
        for (auto& [u, b] : net) {
            if (b > 0) cred.push({b, u});
            else if (b < 0) debt.push({-b, u});
        }
        vector<string> txns;
        while (!cred.empty() && !debt.empty()) {
            auto [cAmt, cUser] = cred.top(); cred.pop();
            auto [dAmt, dUser] = debt.top(); debt.pop();
            long long pay = min(cAmt, dAmt);
            txns.push_back(dUser + " pays " + cUser + ": " + to_string(pay));
            if (cAmt > pay) cred.push({cAmt - pay, cUser});
            if (dAmt > pay) debt.push({dAmt - pay, dUser});
        }
        return txns;
    }
};"""
    }
]
