# Strategic Project Decisions & Rationale

## ADR 001: Project Selection and Domain Context
**Date:** 2026-03-27
**Status:** Decided

**Context:** To transition from Electronic Engineering to Cloud/Backend roles, the project requires a domain that demonstrates technical depth and real-world applicability.

**Decision:** I chose the "Telecom Network Monitoring & Incident Platform".

**Rationale:**
* **Leveraging Background**: Utilizes my background in Electronic Engineering to bridge the gap between hardware physics (sensors) and software architecture.
* **Technical Realism**: Monitoring RF metrics like RSSI and Latency provides a realistic data source for high-load backend systems.
* **Professional Differentiator**: It moves away from generic "To-Do" apps, showing a specialized ability to handle industrial IoT and observability problems.

---

## ADR 002: Branching Strategy and Professional Workflow
**Date:** 2026-03-27
**Status:** Decided

**Context:** The project needs a workflow that ensures code quality and supports long-term maintenance.

**Decision:** Implementation of **GitFlow** (Feature-branch workflow).

**Rationale:**
* **Release Management**: GitFlow is ideal for products with scheduled release cycles, allowing us to group features (like the OOP refactor) before merging to production.
* **Parallel Development**: Enables "Feature Isolation," where we can enhance simulator physics in one branch while researching OOP in another without code conflicts.
* **Main Branch Stability**: Ensures the `main` branch always contains a functional, "deployable" version of the platform.
* **Version Control Mastery**: This flow forces the practice of Atomic Commits, Merge Conflict Resolution and other essential skills when using Git.
* **Simulating Professional Environments**: This flow tries to mimic the workflow of a professional engineering team.

---

## ADR 003: Core Skill Alignment
**Objective:** To demonstrate competencies required for Backend and Cloud Engineering roles.

**Targeted Skills:**
* **Backend Engineering**: RESTful API design (FastAPI), domain modeling, and asynchronous processing.
* **Distributed Systems**: Event-driven architecture and decoupled processing.
* **Cloud & DevOps**: Infrastructure as Code, AWS services (EC2, RDS, S3), Docker containerization, and CI/CD pipelines.
* **Observability**: Structured logging and system health monitoring.

---

## ADR 004: Success Metrics (Professional Benchmarks)
**Context:** Defining what constitutes a "Senior-level" or professional-grade completion of this project.

**Metrics for Success:**
1. **Architectural Decoupling**: 100% separation between the Data Ingestion (API) and Data Processing (Workers).
2. **Data Consistency**: The simulator achieves a "physics-aware" signal drift where RSSI values stay within ±5% of realistic hardware behavior.
3. **99.9% Fault Tolerance**: The system must handle simulated device failures (offline status) without crashing the backend workers.
4. **Documentation Coverage**: Every major architectural decision is backed by an ADR (like this one) and a fully documented API (Swagger/OpenAPI).
5. **Deployment Automation**: A "One-Click" deployment process where GitHub Actions automatically builds, tests, and deploys the system to AWS.