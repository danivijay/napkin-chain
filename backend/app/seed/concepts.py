"""Concept content.

Each concept is one estimation skill, sized to be read in a couple of minutes
so a user can leave a challenge, learn the thing they lack, and come back.
"""

CONCEPTS: list[dict] = [
    {
        "conceptId": "dau-to-traffic",
        "title": "DAU to traffic",
        "area": "traffic",
        "order": 1,
        "readMinutes": 2,
        "oneLiner": "Users are not requests. Multiply by what each user actually does.",
        "explanation": [
            "Every capacity estimate starts by turning people into actions. "
            "A DAU number on its own says nothing about load.",
            "Pick an actions-per-user-per-day figure and defend it. Interviewers "
            "care far more about the reasoning behind the multiplier than about "
            "the multiplier itself.",
            "Feed-style consumption apps sit around 10-50 actions per user per "
            "day. Messaging is higher, 30-100. Utility apps are often below 5.",
        ],
        "shortcut": "requests/day = DAU x actions per user per day",
        "shortcutNote": "State the multiplier out loud. An unstated assumption is the mistake, not a wrong number.",
        "examples": [
            {
                "given": "100M DAU, feed app, ~10 actions/user/day",
                "working": ["100M x 10", "= 1,000M", "= 1B requests/day"],
                "result": "1B requests/day",
            },
            {
                "given": "20M DAU messaging app, ~40 messages sent/user/day",
                "working": ["20M x 40", "= 800M"],
                "result": "800M messages/day",
            },
        ],
        "pitfalls": [
            "Treating DAU as concurrent users. They are not concurrent.",
            "Forgetting that one user action can fan out into several backend requests.",
        ],
        "drill": {
            "prompt": "A photo app has 40M DAU. A typical user opens the app twice a day and each open loads roughly 8 items. Roughly how many item reads per day?",
            "given": "40M DAU, 2 sessions/day, 8 items per session",
            "unit": "reads/day",
            "expectedMin": 400_000_000,
            "expectedMax": 900_000_000,
            "explanation": [
                "40M x 2 sessions = 80M sessions/day",
                "80M x 8 items ~ 640M reads/day",
            ],
        },
        "relatedConceptIds": ["qps", "read-write-ratio"],
    },
    {
        "conceptId": "qps",
        "title": "Requests/day to QPS",
        "area": "traffic",
        "order": 2,
        "readMinutes": 1,
        "oneLiner": "One day is about 100,000 seconds. Everything else follows.",
        "explanation": [
            "A day is 86,400 seconds. Round it to 100K and the arithmetic becomes "
            "something you can do while talking.",
            "Dividing by 100K instead of 86.4K makes your answer ~15% low. At "
            "napkin resolution that is noise - and it errs on the readable side.",
        ],
        "shortcut": "1 day ~ 100K seconds",
        "shortcutNote": "So QPS ~ requests per day / 100,000. Move the decimal five places.",
        "examples": [
            {
                "given": "1B requests/day",
                "working": ["1B / 100K", "= 10,000"],
                "result": "~10K QPS",
            },
            {
                "given": "100M requests/day",
                "working": ["100M / 100K", "= 1,000"],
                "result": "~1K QPS",
            },
        ],
        "pitfalls": [
            "Dividing by 24 and stopping - that gives requests per hour, not per second.",
            "Quoting average QPS as if it were the number you provision for. It isn't.",
        ],
        "drill": {
            "prompt": "A service handles 50M requests per day. Approximately what is the average QPS?",
            "given": "50M requests/day",
            "unit": "QPS",
            "expectedMin": 400,
            "expectedMax": 750,
            "explanation": ["50M / 100K", "= 500 QPS"],
        },
        "relatedConceptIds": ["dau-to-traffic", "peak-traffic"],
        "relatedChallengeSlugs": ["url-shortener", "instagram-feed"],
    },
    {
        "conceptId": "peak-traffic",
        "title": "Peak traffic",
        "area": "traffic",
        "order": 3,
        "readMinutes": 2,
        "oneLiner": "Average traffic is a fiction. Provision for the peak.",
        "explanation": [
            "Traffic is never flat. Usage clusters into a few hours of the day, "
            "and consumer apps have sharp evening peaks.",
            "A peak multiplier of 2-3x over the daily average is the usual "
            "starting point. Global apps with users spread across time zones "
            "flatten out toward 2x; single-region consumer apps run 3-5x.",
            "Event-driven systems - ticket sales, live sport, breaking news - "
            "break this rule entirely and can spike 10-100x. Say so if the "
            "scenario hints at it.",
        ],
        "shortcut": "peak QPS ~ average QPS x 3",
        "shortcutNote": "Justify the multiplier from the system's shape, not from habit.",
        "examples": [
            {
                "given": "10K average QPS, single-region consumer app",
                "working": ["10K x 3"],
                "result": "~30K peak QPS",
            },
            {
                "given": "5K average QPS, globally distributed B2B API",
                "working": ["5K x 2", "traffic is spread across time zones"],
                "result": "~10K peak QPS",
            },
        ],
        "pitfalls": [
            "Sizing servers off the average and discovering the peak in production.",
            "Applying a 3x multiplier to a system whose load is genuinely event-driven.",
        ],
        "drill": {
            "prompt": "A consumer app averages 8K QPS with most usage in the evening. What peak QPS would you provision for?",
            "given": "8K average QPS, evening-heavy single region",
            "unit": "QPS",
            "expectedMin": 16_000,
            "expectedMax": 40_000,
            "explanation": ["8K x 3 = 24K peak QPS", "Evening-heavy usage justifies the higher end of 2-3x."],
        },
        "relatedConceptIds": ["qps", "server-capacity"],
        "relatedChallengeSlugs": ["instagram-feed", "chat-system"],
    },
    {
        "conceptId": "read-write-ratio",
        "title": "Read/write ratio",
        "area": "traffic",
        "order": 4,
        "readMinutes": 2,
        "oneLiner": "Most systems are read-heavy, and that decides the architecture.",
        "explanation": [
            "Separating reads from writes is usually the single most useful split "
            "in a capacity estimate. They hit different components and scale "
            "differently.",
            "Rough anchors: URL shorteners and content sites are 10:1 to 100:1 "
            "read-heavy. Social feeds are 10:1 to 100:1. Messaging is close to "
            "1:1 per message but fans out on delivery. Logging and metrics "
            "ingestion is write-heavy, often 1:0.1.",
            "The ratio tells you where caching pays and where durability costs "
            "you.",
        ],
        "shortcut": "reads = writes x ratio",
        "shortcutNote": "Name the ratio before you use it, and tie it to the product's behaviour.",
        "examples": [
            {
                "given": "1,000 write QPS, 10:1 read-heavy",
                "working": ["1,000 x 10"],
                "result": "~10K read QPS",
            },
        ],
        "pitfalls": [
            "Quoting a single QPS figure for a system whose reads and writes differ by two orders of magnitude.",
            "Assuming read-heavy without checking - ingestion pipelines are the opposite.",
        ],
        "drill": {
            "prompt": "A link shortener creates 500 links/sec and is 20:1 read-heavy. What is the read QPS?",
            "given": "500 write QPS, 20:1 read/write",
            "unit": "QPS",
            "expectedMin": 8_000,
            "expectedMax": 12_000,
            "explanation": ["500 x 20 = 10,000 read QPS"],
        },
        "relatedConceptIds": ["qps", "server-capacity"],
        "relatedChallengeSlugs": ["url-shortener"],
    },
    {
        "conceptId": "daily-storage",
        "title": "Daily storage",
        "area": "storage",
        "order": 1,
        "readMinutes": 2,
        "oneLiner": "Objects per day times bytes per object. The trick is the byte size.",
        "explanation": [
            "Storage estimates fail on the payload size, not on the arithmetic. "
            "Have anchors ready and state them.",
            "Useful anchors: a chat message with metadata ~ 500 bytes to 1 KB. A "
            "tweet-sized record ~ 1 KB. A compressed phone photo ~ 1-3 MB. A "
            "minute of 1080p video ~ 30-60 MB. A log line ~ 200 bytes.",
            "Only a fraction of users create content. On a photo app, 5-10% of "
            "DAU posting is a defensible starting assumption.",
        ],
        "shortcut": "storage/day = objects/day x bytes/object",
        "shortcutNote": "1 TB is roughly 1e12 bytes. 1 PB is roughly 1e15.",
        "examples": [
            {
                "given": "2B messages/day at ~500 bytes each",
                "working": ["2e9 x 500", "= 1e12 bytes"],
                "result": "~1 TB/day",
            },
            {
                "given": "10M photos/day at ~1.5 MB each",
                "working": ["1e7 x 1.5e6", "= 1.5e13 bytes"],
                "result": "~15 TB/day",
            },
        ],
        "pitfalls": [
            "Using raw camera file sizes instead of what actually gets stored after compression.",
            "Assuming every active user creates content every day.",
        ],
        "drill": {
            "prompt": "A service ingests 500M log lines per day at roughly 200 bytes each. Roughly how much storage per day, in GB?",
            "given": "500M lines/day, ~200 bytes/line",
            "unit": "GB/day",
            "expectedMin": 70,
            "expectedMax": 150,
            "explanation": ["5e8 x 200 bytes = 1e11 bytes", "= 100 GB/day"],
        },
        "relatedConceptIds": ["retention-replication", "bandwidth"],
        "relatedChallengeSlugs": ["chat-system", "instagram-feed"],
    },
    {
        "conceptId": "retention-replication",
        "title": "Retention and replication",
        "area": "storage",
        "order": 2,
        "readMinutes": 2,
        "oneLiner": "Total storage is daily storage stretched over time and multiplied by copies.",
        "explanation": [
            "Two multipliers turn a daily figure into a capacity plan: how long "
            "you keep the data, and how many copies you hold.",
            "Replication factor 3 is the default assumption for durable storage. "
            "Add backups and it drifts to 4-5x. Erasure coding pulls it back "
            "toward 1.3-1.5x for cold data - worth mentioning if the volume is "
            "large.",
            "A year is about 400 days for napkin purposes. It keeps the "
            "multiplication honest and slightly conservative.",
        ],
        "shortcut": "total = daily x days retained x replication factor",
        "shortcutNote": "1 year ~ 400 days. 5 years ~ 2,000 days.",
        "examples": [
            {
                "given": "1 TB/day, kept 1 year, 3 replicas",
                "working": ["1 TB x 400 days", "= 400 TB", "x 3 replicas"],
                "result": "~1.2 PB",
            },
        ],
        "pitfalls": [
            "Quoting logical data size and calling it provisioned capacity.",
            "Ignoring that retention policy is a product decision you are allowed to propose.",
        ],
        "drill": {
            "prompt": "A system writes 2 TB/day, keeps data for 1 year, and replicates 3x. Roughly how much total storage, in PB?",
            "given": "2 TB/day, 1 year retention, 3x replication",
            "unit": "PB",
            "expectedMin": 1.5,
            "expectedMax": 3.5,
            "explanation": ["2 TB x 400 days = 800 TB", "800 TB x 3 = 2,400 TB ~ 2.4 PB"],
        },
        "relatedConceptIds": ["daily-storage"],
        "relatedChallengeSlugs": ["instagram-feed"],
    },
    {
        "conceptId": "bandwidth",
        "title": "Bandwidth",
        "area": "bandwidth",
        "order": 1,
        "readMinutes": 2,
        "oneLiner": "Bandwidth is just QPS times payload size - at the peak, not the average.",
        "explanation": [
            "Egress is the number that costs money and the number that saturates "
            "first. Compute it from peak QPS and the average response size.",
            "Anchors worth knowing: 1 Gbps ~ 125 MB/s. A single well-provisioned "
            "server tops out around 1-10 Gbps. Anything in the tens of GB/s is a "
            "CDN conversation, not an origin conversation.",
            "Split egress from ingress. For most consumer systems egress "
            "dominates by an order of magnitude.",
        ],
        "shortcut": "bandwidth = peak QPS x average payload size",
        "shortcutNote": "1 Gbps ~ 125 MB/s. 8 bits to a byte - keep the units straight.",
        "examples": [
            {
                "given": "30K peak QPS, ~200 KB average response",
                "working": ["3e4 x 2e5 bytes", "= 6e9 bytes/s"],
                "result": "~6 GB/s (~48 Gbps)",
            },
        ],
        "pitfalls": [
            "Mixing bits and bytes. GB/s and Gbps differ by 8x.",
            "Computing bandwidth from average QPS and under-provisioning the link.",
        ],
        "drill": {
            "prompt": "A service peaks at 20K QPS with an average response of 50 KB. Roughly what egress bandwidth, in GB/s?",
            "given": "20K peak QPS, 50 KB average response",
            "unit": "GB/s",
            "expectedMin": 0.7,
            "expectedMax": 1.5,
            "explanation": ["2e4 x 5e4 bytes = 1e9 bytes/s", "= 1 GB/s (~8 Gbps)"],
        },
        "relatedConceptIds": ["peak-traffic", "daily-storage"],
        "relatedChallengeSlugs": ["instagram-feed"],
    },
    {
        "conceptId": "server-capacity",
        "title": "Server capacity",
        "area": "capacity",
        "order": 1,
        "readMinutes": 2,
        "oneLiner": "Divide peak load by what one box can actually do, then add headroom.",
        "explanation": [
            "Pick a per-server throughput anchor and justify it from the work "
            "being done. A cache lookup and a database join are not the same "
            "server.",
            "Anchors: a simple in-memory or cache-backed request ~ 5-10K QPS per "
            "server. A typical application request touching a database ~ 500-2K "
            "QPS. Anything CPU-bound - image processing, compression - drops to "
            "tens or hundreds.",
            "Then add headroom. Running at 100% utilisation leaves nothing for "
            "failure, deploys, or the next spike. Size for 50-70% utilisation.",
        ],
        "shortcut": "servers = peak QPS / QPS per server, then x1.5 for headroom",
        "shortcutNote": "State the per-server number. It is the assumption being tested.",
        "examples": [
            {
                "given": "30K peak QPS, ~1K QPS per app server",
                "working": ["30K / 1K = 30 servers", "x1.5 headroom"],
                "result": "~45-50 servers",
            },
        ],
        "pitfalls": [
            "Sizing the fleet with no headroom for failure domains or deploys.",
            "Using one throughput number for services doing wildly different work.",
        ],
        "drill": {
            "prompt": "A service peaks at 12K QPS. Each app server handles about 1K QPS. How many servers would you provision, including headroom?",
            "given": "12K peak QPS, 1K QPS per server",
            "unit": "servers",
            "expectedMin": 15,
            "expectedMax": 30,
            "explanation": ["12K / 1K = 12 servers at full load", "x1.5 headroom ~ 18 servers"],
        },
        "relatedConceptIds": ["peak-traffic", "read-write-ratio"],
        "relatedChallengeSlugs": ["instagram-feed"],
    },
]
