"""Challenge content.

Expected values are always expressed in the node's own unit - a user typing
"30" into a node labelled GB/s is answering in GB/s, not in bytes.
"""

CHALLENGES: list[dict] = [
    # ----------------------------------------------------------------- foundation
    {
        "slug": "url-shortener",
        "title": "URL Shortener",
        "subtitle": "Two estimates, one dependency",
        "description": (
            "A link shortener creates 100M new links a day and serves the "
            "redirects. Work out what the write and read paths actually have to "
            "handle."
        ),
        "difficulty": "foundation",
        "estimatedMinutes": 4,
        "modes": ["learn", "practice", "interview"],
        "suggestedSecondsPerNode": 90,
        "scenario": {
            "description": (
                "A URL shortener accepts new links and redirects visitors. The "
                "product team reports 100M new links created per day, and "
                "analytics show each link is followed about 10 times over its "
                "life."
            ),
            "givens": [
                {"label": "New links", "value": "100M / day"},
                {"label": "Read/write ratio", "value": "10 : 1"},
            ],
        },
        "complexity": {
            "level": "foundation",
            "chainDepth": 3,
            "dependencyCount": 2,
            "ambiguity": 1,
            "conceptCount": 2,
            "timePressure": 1,
        },
        "nodes": [
            {
                "id": "new_links",
                "type": "input",
                "label": "New links / day",
                "unit": "links/day",
                "value": 100_000_000,
                "displayValue": "100M links/day",
            },
            {
                "id": "write_qps",
                "type": "estimate",
                "label": "Write QPS",
                "unit": "QPS",
                "dependsOn": ["new_links"],
                "conceptId": "qps",
                "prompt": "How many links are created per second on average?",
                "givens": [{"label": "New links", "value": "100M / day"}],
                "expectedMin": 800,
                "expectedMax": 1500,
                "hints": [
                    "You don't need 86,400. Round a day to something you can divide by in your head.",
                    "100M / 100K - just count the zeros.",
                ],
                "explanation": {
                    "steps": [
                        "1 day ~ 100K seconds",
                        "100M / 100K",
                        "~ 1,000 writes/sec",
                    ],
                    "shortcut": "1 day ~ 100K seconds",
                    "note": "The exact figure is 1,157 QPS. At napkin resolution, 1K is the right answer to say out loud.",
                },
            },
            {
                "id": "read_qps",
                "type": "estimate",
                "label": "Read QPS",
                "unit": "QPS",
                "dependsOn": ["write_qps"],
                "conceptId": "read-write-ratio",
                "prompt": "Each link is followed about 10 times. What is the average read QPS?",
                "givens": [
                    {"label": "Write QPS", "value": "~1K"},
                    {"label": "Read/write ratio", "value": "10 : 1"},
                ],
                "expectedMin": 8_000,
                "expectedMax": 15_000,
                "hints": [
                    "Reads scale off the write rate, not off the user count.",
                    "1K writes/sec x 10 reads per link.",
                ],
                "explanation": {
                    "steps": [
                        "~1K writes/sec",
                        "x10 reads per link",
                        "~ 10K reads/sec",
                    ],
                    "shortcut": "reads = writes x ratio",
                    "note": "10K read QPS against a key-value lookup is comfortably cacheable - which is exactly why this system is usually cache-fronted.",
                },
            },
        ],
    },
    # ------------------------------------------------------------------- builder
    {
        "slug": "chat-system",
        "title": "Chat System",
        "subtitle": "Traffic, peak and storage",
        "description": (
            "Size the messaging backbone for a 50M DAU chat app: send rate, "
            "peak load, and what it costs to keep the history."
        ),
        "difficulty": "builder",
        "estimatedMinutes": 7,
        "modes": ["learn", "practice", "interview"],
        "suggestedSecondsPerNode": 100,
        "scenario": {
            "description": (
                "A 1:1 and small-group chat service has 50M daily active users. "
                "Messages are text with metadata; media is handled by a separate "
                "service. History is kept indefinitely and is expected to be "
                "searchable."
            ),
            "givens": [
                {"label": "DAU", "value": "50M"},
                {"label": "Media", "value": "handled elsewhere"},
            ],
        },
        "complexity": {
            "level": "builder",
            "chainDepth": 5,
            "dependencyCount": 4,
            "ambiguity": 2,
            "conceptCount": 4,
            "timePressure": 2,
        },
        "nodes": [
            {
                "id": "dau",
                "type": "input",
                "label": "Daily active users",
                "unit": "DAU",
                "value": 50_000_000,
                "displayValue": "50M DAU",
            },
            {
                "id": "messages_day",
                "type": "estimate",
                "label": "Messages / day",
                "unit": "messages/day",
                "dependsOn": ["dau"],
                "conceptId": "dau-to-traffic",
                "prompt": "How many messages are sent across the platform per day?",
                "givens": [{"label": "DAU", "value": "50M"}],
                "expectedMin": 1_000_000_000,
                "expectedMax": 4_000_000_000,
                "hints": [
                    "Pick a messages-per-user-per-day number and commit to it. Messaging is high-engagement.",
                    "40 messages sent per active user per day is a defensible anchor.",
                ],
                "explanation": {
                    "steps": [
                        "Assume ~40 messages sent per active user per day",
                        "50M x 40",
                        "= 2B messages/day",
                    ],
                    "shortcut": "requests/day = DAU x actions per user per day",
                    "note": "Messaging engagement runs far above feed apps. Anything from 20 to 80 per user is arguable - what matters is that you say which you chose.",
                },
            },
            {
                "id": "write_qps",
                "type": "estimate",
                "label": "Average write QPS",
                "unit": "QPS",
                "dependsOn": ["messages_day"],
                "conceptId": "qps",
                "prompt": "What is the average message write rate?",
                "givens": [{"label": "Messages", "value": "~2B / day"}],
                "expectedMin": 15_000,
                "expectedMax": 30_000,
                "hints": ["1 day ~ 100K seconds.", "2B / 100K."],
                "explanation": {
                    "steps": ["2B / 100K seconds", "= 20,000 writes/sec"],
                    "shortcut": "1 day ~ 100K seconds",
                },
            },
            {
                "id": "peak_qps",
                "type": "estimate",
                "label": "Peak write QPS",
                "unit": "QPS",
                "dependsOn": ["write_qps"],
                "conceptId": "peak-traffic",
                "prompt": "What peak write rate would you provision for?",
                "givens": [
                    {"label": "Average", "value": "~20K QPS"},
                    {"label": "Audience", "value": "global, evening-heavy per region"},
                ],
                "expectedMin": 40_000,
                "expectedMax": 100_000,
                "hints": [
                    "Traffic is never flat. What is the usual multiplier over the daily average?",
                    "A global user base flattens the curve somewhat - 2-3x rather than 5x.",
                ],
                "explanation": {
                    "steps": ["~20K average QPS", "x3 peak multiplier", "~ 60K peak QPS"],
                    "shortcut": "peak ~ average x 3",
                    "note": "Global spread pulls the multiplier down; a single-region app would justify 4-5x here.",
                },
            },
            {
                "id": "storage_day",
                "type": "estimate",
                "label": "Storage / day",
                "unit": "TB/day",
                "dependsOn": ["messages_day"],
                "conceptId": "daily-storage",
                "prompt": "How much message storage is written per day, in TB?",
                "givens": [
                    {"label": "Messages", "value": "~2B / day"},
                    {"label": "Payload", "value": "text + metadata"},
                ],
                "expectedMin": 0.5,
                "expectedMax": 2.5,
                "hints": [
                    "A chat message with its metadata - ids, timestamps, delivery state - is bigger than the text alone.",
                    "500 bytes to 1 KB per stored message is a reasonable anchor.",
                ],
                "explanation": {
                    "steps": [
                        "Assume ~500 bytes per stored message",
                        "2e9 x 500 bytes",
                        "= 1e12 bytes",
                        "~ 1 TB/day",
                    ],
                    "shortcut": "storage/day = objects/day x bytes/object",
                    "note": "1 TB/day is ~400 TB/year before replication. Indefinite retention is a real product cost, and worth raising.",
                },
            },
        ],
    },
    # -------------------------------------------------------------------- system
    {
        "slug": "instagram-feed",
        "title": "Instagram Feed",
        "subtitle": "A branching chain: traffic, bandwidth, storage, capacity",
        "description": (
            "Estimate the core capacity requirements for a photo feed serving "
            "100M DAU - from user actions through to servers and petabytes."
        ),
        "difficulty": "system",
        "estimatedMinutes": 10,
        "modes": ["learn", "practice", "interview"],
        "suggestedSecondsPerNode": 110,
        "scenario": {
            "description": (
                "A photo-sharing feed serves 100M daily active users. Users "
                "scroll a ranked feed of images and a minority of them post. "
                "Images are served from origin plus a CDN, and originals are "
                "retained for the life of the account."
            ),
            "givens": [
                {"label": "DAU", "value": "100M"},
                {"label": "Content", "value": "compressed images, no video"},
            ],
        },
        "complexity": {
            "level": "system",
            "chainDepth": 8,
            "dependencyCount": 6,
            "ambiguity": 3,
            "conceptCount": 6,
            "timePressure": 2,
        },
        "nodes": [
            {
                "id": "dau",
                "type": "input",
                "label": "Daily active users",
                "unit": "DAU",
                "value": 100_000_000,
                "displayValue": "100M DAU",
            },
            {
                "id": "actions_day",
                "type": "estimate",
                "label": "Feed requests / day",
                "unit": "requests/day",
                "dependsOn": ["dau"],
                "conceptId": "dau-to-traffic",
                "prompt": "How many feed requests does the platform serve per day?",
                "givens": [{"label": "DAU", "value": "100M"}],
                "expectedMin": 500_000_000,
                "expectedMax": 2_000_000_000,
                "hints": [
                    "How many times a day does a typical user open the app and pull the feed?",
                    "~10 feed requests per user per day is a defensible anchor for a scroll-heavy app.",
                ],
                "explanation": {
                    "steps": [
                        "Assume ~10 feed requests per user per day",
                        "100M x 10",
                        "= 1B requests/day",
                    ],
                    "shortcut": "requests/day = DAU x actions per user per day",
                },
            },
            {
                "id": "avg_qps",
                "type": "estimate",
                "label": "Average QPS",
                "unit": "QPS",
                "dependsOn": ["actions_day"],
                "conceptId": "qps",
                "prompt": "What is the average feed request rate?",
                "givens": [{"label": "Requests", "value": "~1B / day"}],
                "expectedMin": 8_000,
                "expectedMax": 15_000,
                "hints": ["1 day ~ 100K seconds.", "1B / 100K."],
                "explanation": {
                    "steps": ["1B / 100K seconds", "~ 10K QPS"],
                    "shortcut": "1 day ~ 100K seconds",
                },
            },
            {
                "id": "peak_qps",
                "type": "estimate",
                "label": "Peak QPS",
                "unit": "QPS",
                "dependsOn": ["avg_qps"],
                "conceptId": "peak-traffic",
                "prompt": "What peak request rate should the feed be sized for?",
                "givens": [
                    {"label": "Average", "value": "~10K QPS"},
                    {"label": "Usage", "value": "consumer app, evening-heavy"},
                ],
                "expectedMin": 20_000,
                "expectedMax": 50_000,
                "hints": [
                    "The daily average hides a sharp evening peak.",
                    "2-5x over average. Consumer social sits toward 3x.",
                ],
                "explanation": {
                    "steps": ["~10K average QPS", "x3 peak multiplier", "~ 30K peak QPS"],
                    "shortcut": "peak ~ average x 3",
                },
            },
            {
                "id": "peak_bandwidth",
                "type": "estimate",
                "label": "Peak egress bandwidth",
                "unit": "GB/s",
                "dependsOn": ["peak_qps"],
                "conceptId": "bandwidth",
                "prompt": "How much egress bandwidth at peak, in GB/s?",
                "givens": [
                    {"label": "Peak QPS", "value": "~30K"},
                    {"label": "Feed response", "value": "images dominate the payload"},
                ],
                "expectedMin": 3,
                "expectedMax": 15,
                "hints": [
                    "Bandwidth is peak QPS times the average bytes returned.",
                    "A feed response carrying a handful of compressed images is on the order of 200 KB.",
                ],
                "explanation": {
                    "steps": [
                        "Assume ~200 KB per feed response",
                        "3e4 QPS x 2e5 bytes",
                        "= 6e9 bytes/s",
                        "~ 6 GB/s (~48 Gbps)",
                    ],
                    "shortcut": "bandwidth = peak QPS x payload size",
                    "note": "At this volume the honest answer is that a CDN absorbs almost all of it - origin egress would be a small fraction.",
                },
            },
            {
                "id": "storage_day",
                "type": "estimate",
                "label": "Photo storage / day",
                "unit": "TB/day",
                "dependsOn": ["dau"],
                "conceptId": "daily-storage",
                "prompt": "How much new photo data is stored per day, in TB?",
                "givens": [
                    {"label": "DAU", "value": "100M"},
                    {"label": "Posting", "value": "a minority of users post"},
                ],
                "expectedMin": 5,
                "expectedMax": 50,
                "hints": [
                    "Not every active user posts. What fraction would you assume?",
                    "~10% of DAU posting one compressed photo of 1-2 MB.",
                ],
                "explanation": {
                    "steps": [
                        "Assume ~10% of DAU post 1 photo/day -> 10M photos/day",
                        "~1.5 MB per stored photo",
                        "1e7 x 1.5e6 bytes = 1.5e13 bytes",
                        "~ 15 TB/day",
                    ],
                    "shortcut": "storage/day = objects/day x bytes/object",
                    "note": "Thumbnails and resized variants add 20-50% on top. Worth naming even if you don't compute it.",
                },
            },
            {
                "id": "storage_5y",
                "type": "estimate",
                "label": "Total storage, 5 years",
                "unit": "PB",
                "dependsOn": ["storage_day"],
                "conceptId": "retention-replication",
                "prompt": "How much total capacity over 5 years, including replication?",
                "givens": [
                    {"label": "Daily", "value": "~15 TB/day"},
                    {"label": "Durability", "value": "3 replicas"},
                ],
                "expectedMin": 40,
                "expectedMax": 150,
                "hints": [
                    "Stretch the daily figure over the retention window, then multiply by copies.",
                    "1 year ~ 400 days, so 5 years ~ 2,000 days.",
                ],
                "explanation": {
                    "steps": [
                        "15 TB/day x 2,000 days",
                        "= 30,000 TB = 30 PB logical",
                        "x3 replication",
                        "~ 90 PB",
                    ],
                    "shortcut": "total = daily x days x replication",
                    "note": "This is the number that makes tiering cold photos to cheaper storage an architectural decision rather than an optimisation.",
                },
            },
            {
                "id": "servers",
                "type": "estimate",
                "label": "Feed servers",
                "unit": "servers",
                "dependsOn": ["peak_qps"],
                "conceptId": "server-capacity",
                "prompt": "How many application servers for the feed at peak?",
                "givens": [
                    {"label": "Peak QPS", "value": "~30K"},
                    {"label": "Work per request", "value": "ranked feed, cache-backed"},
                ],
                "expectedMin": 20,
                "expectedMax": 120,
                "hints": [
                    "Pick a per-server throughput figure and justify it from the work each request does.",
                    "~1K QPS per server for a cache-backed ranked feed, then add headroom.",
                ],
                "explanation": {
                    "steps": [
                        "Assume ~1K QPS per app server",
                        "30K / 1K = 30 servers at full load",
                        "x1.5 for headroom and failure domains",
                        "~ 45-50 servers",
                    ],
                    "shortcut": "servers = peak QPS / QPS per server, x1.5",
                    "note": "Fleet size is dominated by the per-server assumption. State it before you divide.",
                },
            },
        ],
    },
]
