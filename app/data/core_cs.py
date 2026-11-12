CORE_CS_TOPICS = [
    {
        "category": "SQL & Queries",
        "items": [
            {
                "id": "cs-sql-1",
                "q": "Find the 2nd / Nth Highest Salary per Department (Handling Ties cleanly)",
                "a": "Use `DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC)` inside a CTE, then `WHERE rnk = N`. Unlike `ROW_NUMBER()`, `DENSE_RANK()` handles ties properly without skipping rank numbers; unlike `LIMIT 1 OFFSET N-1`, it scales cleanly per group.",
                "code": """WITH ranked AS (
  SELECT name, dept_id, salary,
         DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk
  FROM employees
)
SELECT name, dept_id, salary FROM ranked WHERE rnk = 2;"""
            },
            {
                "id": "cs-sql-2",
                "q": "WHERE vs HAVING vs QUALIFY — Exact Execution Order",
                "a": "SQL executes in order: `FROM/JOIN` -> `WHERE` (filters raw rows BEFORE grouping) -> `GROUP BY` -> `HAVING` (filters aggregated groups) -> `Window Functions` -> `SELECT` -> `ORDER BY` -> `LIMIT`. You cannot filter an aggregate like `COUNT(*) > 5` inside `WHERE`.",
                "code": """SELECT customer_id, COUNT(*) AS orders
FROM orders WHERE status = 'PAID'
GROUP BY customer_id HAVING COUNT(*) >= 3;"""
            },
            {
                "id": "cs-sql-3",
                "q": "Find Duplicate Emails and Delete All But Lowest ID",
                "a": "Self-join or `ROW_NUMBER()` partition by email ordered by id ASC. Delete rows where `rn > 1`.",
                "code": """DELETE p1 FROM Person p1
JOIN Person p2 ON p1.email = p2.email AND p1.id > p2.id;"""
            },
            {
                "id": "cs-sql-4",
                "q": "Running Total & Moving Average Using Window Frames",
                "a": "Combine `SUM(amount) OVER (ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` for exact running totals without slow O(N^2) self-joins.",
                "code": """SELECT dt, rev,
  SUM(rev) OVER (ORDER BY dt ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7d
FROM daily_revenue;"""
            }
        ]
    },
    {
        "category": "DBMS & ACID",
        "items": [
            {
                "id": "cs-dbms-1",
                "q": "Isolation Levels & Read Anomalies (Read Committed vs Repeatable Read vs Serializable)",
                "a": "1) Read Uncommitted: Dirty reads allowed. 2) Read Committed (Postgres default): No dirty reads, but non-repeatable reads possible. 3) Repeatable Read (MySQL InnoDB default via MVCC + gap locks): Prevents dirty & non-repeatable reads; InnoDB gap locks also prevent phantom reads on locking reads. 4) Serializable: Full conflict-free ordering.",
                "code": ""
            },
            {
                "id": "cs-dbms-2",
                "q": "Clustered vs Non-Clustered Index (Why UUIDv4 hurts B-Tree inserts)",
                "a": "Clustered index (InnoDB primary key) physically orders table rows in leaf pages. Non-clustered (secondary) index stores `(indexed_col -> PK)`. Random UUIDv4 PKs cause random B-Tree page splits & fragmentation; monotonic IDs (BIGINT AUTO_INCREMENT or time-ordered UUIDv7/ULID) keep inserts sequential at the right leaf!",
                "code": ""
            },
            {
                "id": "cs-dbms-3",
                "q": "How MVCC (Multi-Version Concurrency Control) Lets Readers Never Block Writers",
                "a": "Instead of locking rows on `SELECT`, Postgres/InnoDB keep row version snapshots (`xmin/xmax` or Undo Logs). Readers read the committed snapshot matching their transaction start timestamp while writers append a new version cleanly.",
                "code": ""
            },
            {
                "id": "cs-dbms-4",
                "q": "Preventing SQL Deadlocks in Wallet / Escrow Transfers",
                "a": "Deadlocks happen when Tx1 locks Account A then wants B, while Tx2 locks B then wants A. Fix: always acquire `SELECT ... FOR UPDATE` locks in canonical ascending `account_id` order (`min(from, to)` first, then `max(from, to)`).",
                "code": ""
            }
        ]
    },
    {
        "category": "OS & Concurrency",
        "items": [
            {
                "id": "cs-os-1",
                "q": "Process vs Thread & Context Switch Cost",
                "a": "A Process has isolated virtual address space, file descriptors, and page tables—context switching flushes TLB/MMU state (expensive). Threads within the same process share heap, code, and FDs, owning only separate Stack + Registers + PC (fast switch, but needs mutexes/atomics for shared heap).",
                "code": ""
            },
            {
                "id": "cs-os-2",
                "q": "Mutex vs Binary Semaphore vs Condition Variable",
                "a": "Mutex enforces strict ownership—only the thread that locked it can unlock it (prevents accidental release + supports priority inheritance). A Semaphore is a signaling counter (`wait/signal`) with no ownership, usable across threads/processes to signal producer-consumer readiness.",
                "code": ""
            },
            {
                "id": "cs-os-3",
                "q": "4 Coffman Conditions for Deadlock (and How to Break Them)",
                "a": "1) Mutual Exclusion, 2) Hold & Wait, 3) No Preemption, 4) Circular Wait. In backend engineering, you break Circular Wait most cleanly via global lock ordering (`lock(min_id)` then `lock(max_id)`), or use lock timeouts (`try_lock_for`).",
                "code": ""
            },
            {
                "id": "cs-os-4",
                "q": "Why Node.js Event Loop Scales I/O Despite Single JS Thread",
                "a": "libuv delegates non-blocking socket I/O to OS epoll (Linux) / kqueue (macOS) / IOCP (Windows) and keeps a small thread pool for DNS/file ops. Only offload heavy CPU work (crypto, video, giant JSON) to Worker Threads or queues so event loop latency stays <10ms.",
                "code": ""
            }
        ]
    },
    {
        "category": "Networks & Backend Auth",
        "items": [
            {
                "id": "cs-net-1",
                "q": "What Happens When You Type a URL & Hit Enter (DNS -> TCP -> TLS -> HTTP)",
                "a": "Browser cache -> OS/Router DNS UDP lookup -> TCP 3-Way Handshake (SYN, SYN-ACK, ACK) -> TLS 1.3 Handshake (1-RTT key exchange + cert verify) -> HTTP Request routed through Reverse Proxy/Nginx -> App Server -> DB/Redis -> JSON/HTML Response.",
                "code": ""
            },
            {
                "id": "cs-net-2",
                "q": "JWT Stateless Auth vs Session Cookies + Refresh Token Rotation",
                "a": "Pure JWTs cannot be revoked instantly before expiry! Production pattern: short-lived Access JWT (15m) + HttpOnly Secure Refresh Token stored hashed in Redis/DB. On logout or theft detection, delete refresh token & blacklist active JTI in Redis.",
                "code": ""
            },
            {
                "id": "cs-net-3",
                "q": "HTTP/1.1 vs HTTP/2 vs HTTP/3 (QUIC)",
                "a": "HTTP/1.1 opens multiple TCP connections and suffers HTTP Head-of-Line (HoL) blocking. HTTP/2 multiplexes parallel streams over 1 TCP connection (still suffers TCP HoL on packet loss). HTTP/3 runs over UDP (QUIC) with independent per-stream recovery + 0-RTT reconnects.",
                "code": ""
            },
            {
                "id": "cs-net-4",
                "q": "CORS Preflight (OPTIONS) & Idempotent HTTP Methods",
                "a": "Non-simple cross-origin requests (e.g., `Authorization` header or `application/json` PUT/DELETE) trigger an automatic `OPTIONS` preflight checking `Access-Control-Allow-*` headers. GET, HEAD, PUT, DELETE are idempotent; POST is NOT idempotent unless guarded by an Idempotency-Key.",
                "code": ""
            }
        ]
    }
]
