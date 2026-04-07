Unify for your vision to see the big picture.
From Amazon Web Services to Databricks to Snowflake, today's tools are incredibly powerful. Any one of them can support end-to-end data architecture — from transactional workloads to analytics, from streaming pipelines to machine learning and generative AI. They scale, secure, share, and enable teams to move faster than ever before.

And yet, something strange happens inside growing organizations.

As enterprises adopt these platforms, they don't converge — they expand. Teams build deep expertise in their chosen tools. A data science team gravitates toward Databricks. A data engineering team toward Snowflake. A platform team builds on AWS. Each group builds excellence in its own part of the problem.

But enterprise business problems don't exist in parts.

They cut across systems, teams, and platforms — and that's where things begin to break down.

Budgets are separated. Ownership is fragmented. Incentives are local. What should be a straightforward end-to-end data flow becomes a chain of handoffs: pipelines stitched together across teams, duplicated logic at every boundary, and orchestration that is more about coordination on Slack than automation.

In theory, architecture is supposed to solve this. The role of a data architect is to create a cohesive vision — one where teams can operate independently while still contributing to a unified system.

In practice, the architecture devolves into a patchwork of wiring silos together.

What emerges is not a designed system, but an organic one, a web of hidden dependencies, triggers, and handoffs that "just works"… until it doesn't. And when it doesn't, the efforts to diagnose, fix, and sustain the system far exceed the efforts to build and drain value from the enterprise.

This is the challenge of silos in a modern data architecture.

And increasingly, solving it requires more than just better tools. It requires a shift in how we think about ownership, flow, and system design — and often, the ability to step outside of organizational boundaries to realign the architecture around outcomes. Platforms like AWS provide the foundation for unifying these systems, but realizing that vision requires intentional design and, in many cases, a partner who can see the big picture.

Ask yourself: what are the fundamentals of an ideal data architecture?
When you strip away tools, teams, and trends, the core principles are surprisingly simple:

Security
Scalability
Durability
Cost
Accessibility

These are not platform-specific concerns — they are universal. Any architecture, regardless of whether it runs on AWS, Snowflake, Databricks, or all three, ultimately succeeds or fails based on how well it delivers on these fundamentals.

But in a siloed environment, every handoff puts pressure on them.

Security models diverge across systems.
Costs become harder to track and optimize.
Data is duplicated to bridge gaps, impacting durability and consistency.
Access becomes fragmented, requiring multiple pathways to reach the same information.
And scalability is no longer a system property — it becomes a coordination problem between teams.
What should be a cohesive architecture starts to behave like a collection of loosely connected systems, each solving the same fundamental problems in slightly different ways.

A cohesive architecture, by contrast, consistently reinforces these fundamentals throughout the entire data flow. It reduces the number of handoffs, standardizes how data is stored and accessed, and creates a shared foundation that all teams can build on.

To get there, we need to look for the common threads across platforms.

At the most fundamental level, everything starts with storage.

Whether you are using Snowflake or Databricks, the underlying reality is that data often lives in object storage — and in the AWS ecosystem, that means Amazon S3. S3 becomes the durable, scalable backbone that multiple platforms can share, rather than duplicate.

The next layer is understanding what that data represents.

This is where the concept of a catalog becomes critical. A catalog is not just a list of tables — it is the system of record for meaning. It tells us what data exists, how it is structured, and how it should be used.

Open table formats like Apache Iceberg are emerging as a powerful bridge here, supported across platforms like Snowflake and Databricks. They allow data to remain interoperable while still benefiting from each engine's performance and features.

And this is where things get especially interesting.

The catalog is no longer just for engineers — it is becoming the foundation for how machines understand data.

As organizations move toward agentic AI and natural language interfaces, the semantic layer becomes critical. This is the layer that allows an LLM to interpret data correctly — to understand not just structure, but meaning.

By centralizing that semantic understanding — whether through shared catalogs, metadata layers, or AWS-native services — you create a single source of truth accessible from any platform.

Instead of duplicating logic across systems, you share understanding.

And that changes the game.

It means you can leverage AI capabilities in the platform of your choice, while grounding them in a consistent, trusted view of your data. It means less translation, fewer inconsistencies, and a much stronger foundation for building intelligent systems.

Ultimately, breaking silos is not about choosing a single platform.

It's about identifying and reinforcing the layers that can unify them.

The Fundamental Layer — Storage
Before jumping into a unified cross-platform architecture, we need to dig into the foundation: storage.

Storage decisions often align with your silos — and that's not necessarily a bad thing.

Different workloads have fundamentally different needs.

Operational systems (OLTP) depend on block storage, optimized for low-latency reads and writes, transactional integrity, and tight consistency guarantees. This is where systems like PostgreSQL and Oracle Database excel.

Analytical systems (OLAP), on the other hand, prioritize throughput, scale, and parallel processing, which is where object storage and distributed compute engines come into play.

The tension between these two worlds is where silos often begin.

But here's the important question:

Can you simplify everything into a single system — say, a PostgreSQL instance — and avoid the complexity of a lakehouse altogether?

Sometimes, yes.

If your data volume is manageable, your analytical needs are modest, and your team benefits from simplicity over scale, a well-tuned PostgreSQL system can serve both operational and analytical workloads. Many organizations have successfully run hybrid workloads this way for quite some time.

But there are tradeoffs:

Analytical queries begin to compete with transactional workloads
Data modeling becomes constrained by operational schemas
Scaling becomes vertical instead of horizontal
Sharing data across teams or tools becomes more difficult
At a certain point, the system becomes good at everything, but optimal at nothing.

This is where evolution — not replacement — becomes the right strategy.

From Oracle to Modern Architecture: A Pragmatic Path
Let's take a common real-world scenario:

You have an Oracle system supporting both OLTP and OLAP workloads. It has grown over time to handle reporting, analytics, and operational processing in a single environment.

You don't need a big-bang rewrite — you need a controlled separation of concerns.

Step 1: Stabilize the Operational Core
Start by identifying and isolating your true OLTP workload.

Preserve transactional integrity
Maintain low-latency performance
Avoid disrupting core business operations
This often leads to:

Lift-and-shift Oracle → managed PostgreSQL (or staying on Oracle temporarily)
Moving to a managed service to reduce operational overhead
At this stage, you are not modernizing everything — you are protecting what must remain stable.

Step 2: Decouple Analytics from Transactions
Next, begin separating analytical workloads from the operational database.

Identify heavy queries, reporting jobs, and batch processes
Replicate data out of the OLTP system into a separate analytical layer
This can be done via:

CDC (change data capture)
Scheduled extracts
Streaming pipelines
The goal is simple:

Stop asking your transactional system to do analytical work.

Step 3: Introduce Object Storage as the Integration Layer
Now introduce a shared storage layer — typically something like Amazon S3.

Land replicated data into S3
Store it in open, queryable formats (Parquet, Iceberg, etc.)
Treat this as the source of truth for analytics
This is the inflection point.

You move from:

"Each system owns its own data."
To:

"Data is shared through a common layer."
Step 4: Layer in Analytical Engines
Once data is in object storage, you unlock one of the most important shifts in modern architecture:

You are no longer choosing a single engine — you are enabling many.

Traditionally, analytical systems tightly coupled storage and compute. Choosing a platform meant committing your data, performance model, and access patterns to that system. But when your data lives in a shared object storage layer, that constraint disappears.

Now, you can attach different engines based on the problem you're solving.

Platforms like Databricks and Snowflake remain incredibly powerful options:

Databricks excels at large-scale data processing, streaming, and machine learning workloads
Snowflake provides strong governance, performance, and data sharing capabilities
These are often the primary engines organizations adopt — and for good reason.

But they are no longer the only options.

When your foundation is object storage — such as Amazon S3 — you can also leverage AWS-native services that operate directly on that data:

AWS Lake Formation to centrally define permissions and governance across datasets
Amazon Athena for ad hoc querying without managing infrastructure
AWS Glue for cataloging, ETL, and schema management
These services shift the model even further:

You don't need to move data into a platform — you bring compute to where the data already lives.

And beyond managed platforms, there is a growing ecosystem of lightweight, open tools that can operate directly on object storage.

For example, DuckDB allows you to query large datasets locally or in embedded environments, often directly against Parquet files in S3. This opens up entirely new workflows:

Local-first analytics
Developer-friendly exploration
Embedded analytics in applications
Cost-efficient querying without persistent infrastructure
This is a fundamentally different model from the traditional warehouse approach.

Instead of centralizing everything into a single system, you create a shared data layer with multiple access patterns:

Heavy processing in Databricks
Governed analytics in Snowflake
Serverless querying in Athena
Embedded or local analysis with DuckDB
All are operating on the same underlying data.

The key insight is this:

The goal is not to replace one engine with another.

It is to make engines interchangeable.

When storage is unified, compute becomes a choice — not a constraint.

Step 5: Introduce a Catalog and Semantic Layer
As your architecture evolves and more systems begin to interact with shared data, complexity doesn't disappear — it shifts.

Now the challenge becomes understanding and governing that data consistently across platforms.

This is where the catalog and semantic layer become critical.

At a basic level, a catalog answers fundamental questions:

What data exists?
Where is it stored?
How is it structured?
Who can access it?
But in a modern, multi-engine architecture, the catalog does much more than that — it becomes the control plane for your data ecosystem.

This is where open table formats like Apache Iceberg play a pivotal role.

Iceberg is not just a storage format — it is a way of managing data as a table on top of object storage.

It brings capabilities that were traditionally tied to databases into the shared storage layer:

Schema evolution without breaking downstream systems
Time travel and versioned data access
Partitioning and performance optimizations
ACID-like guarantees on large-scale datasets
But its most important contribution is interoperability.

Because Iceberg is supported across multiple engines — Databricks, Snowflake, AWS services, and others — it allows those systems to operate on the same datasets with a shared understanding of structure and state.

Without something like Iceberg, object storage can become fragmented:

Different engines interpret data differently
Metadata is duplicated or inconsistent
Pipelines recreate structure instead of sharing it
With Iceberg, you establish a single table definition across systems.

Now, the catalog layer comes into focus.

Services like AWS Glue Data Catalog, Unity Catalog, or other metadata systems provide:

Centralized schema management
Data discovery
Access control integration
Lineage tracking
And when combined with governance tools like AWS Lake Formation, you can enforce consistent permissions across all engines accessing the data.

This is the point where architecture begins to feel cohesive.

You are no longer just sharing raw files — you are sharing structured, governed, and universally understood data assets.

And this is also where the semantic layer emerges.

The semantic layer builds on top of the catalog to define:

Business meaning (e.g., "customer", "order", "revenue")
Relationships between datasets
Metrics and definitions used across teams
This layer is what allows different consumers — analysts, applications, and increasingly AI systems — to interpret data consistently.

And that last point is becoming more important than ever.

As organizations move toward agentic AI and natural language interfaces, the catalog and semantic layer become the bridge between raw data and machine understanding.

An LLM does not inherently understand your schemas — but it can understand:

Well-defined metadata
Consistent naming
Documented relationships
By centralizing this semantic understanding — often anchored in shared storage and catalog services on AWS — you enable AI systems to query, reason about, and act on your data across platforms.

Instead of each system teaching AI its own version of the truth, you define that truth once — and share it everywhere.

That is what turns a collection of tools into a cohesive data architecture.

Step 6: Pick your Pathway to a Unified Data Solution
Every company has unique needs, and targeting architecture can feel overwhelming. Where you actually start in migrating and unifying a data platform depends on the scale of your data and the complexity of your organization.

Here are some pragmatic pathways based on typical data sizes and maturity levels for companies migrating to the cloud.

Practical Pathways: Unifying Data by Company Size
Small Companies (Up to ~1 TB of Data)

Small — Up to 1 TB
Medium Companies (1 TB — 100 TB)

Medium — 1TB to 100TB
Large Companies (100 TB — PB Scale, Pre-Enterprise Cloud Maturity)

Large — 100TB to PB scale
The Key Insight
You don't break silos by replacing systems — you break them by redefining how those systems work together.

The goal is not consolidation for its own sake, but coordination through a shared foundation.

Block storage systems remain the backbone of operations — optimized for transactions, consistency, and real-time business processes
Object storage becomes the backbone of integration — durable, scalable, and shared across platforms
Analytical engines become interchangeable layers — chosen based on workload, not constrained by where the data lives
When you anchor your architecture in a shared storage and metadata layer — often centered on platforms like Amazon S3 with open formats and centralized catalogs — you shift from isolated systems to a connected ecosystem.

This is the transition that matters.

It's how you move from a monolithic Oracle environment to a modern, data-diverse architecture — not through disruption, but through deliberate separation of concerns and a foundation that encourages sharing instead of duplication.

And once that foundation is in place, silos don't need to be torn down.

They simply stop forming.