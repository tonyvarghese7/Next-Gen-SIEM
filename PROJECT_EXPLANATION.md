# Project Technical Explanation - Next-Gen SIEM

This document acts as a "cheat sheet" to help you explain *what* is happening and *why* it's happening during your project demonstration.

---

## 1. The Core Stack (Wazuh)

### Wazuh Manager
*   **What is it?** The "brain" of the SIEM.
*   **What does it do?** It collects logs, analyzes them using a massive library of pre-defined "signatures" (rules), and generates alerts if something matches (like a known virus or a brute-force pattern).
*   **Presentation Tip**: If asked how it detects the SSH Brute Force, say: *"The Manager monitors the authentication logs. It has a rule that says: 'If the same IP fails to log in 8 times within 2 minutes, trigger a high-severity alert'."*

### Wazuh Indexer
*   **What is it?** A high-performance search and analytics engine (based on OpenSearch).
*   **What does it do?** It stores all the alerts and logs so they can be searched and visualized instantly.

### Wazuh Dashboard
*   **What is it?** The user interface (web portal).
*   **What does it do?** It provides the charts, tables, and buttons you use to see what's happening.

---

## 2. The Next-Gen Component (ML Engine)

### Machine Learning Engine
*   **What is it?** A custom Python service that uses an "Isolation Forest" (or similar) algorithm to find patterns that don't look right.
*   **What does it do?** Instead of looking for a specific signature, it looks for "Statistical Outliers". It learns what "Normal" looks like (e.g., traffic on port 80 at 2 PM) and flags things that are different (e.g., massive traffic on an unusual port at 4 AM).

### Explaining Phase 3 (The Zero-Day)
*   **The Scenario**: An attacker uses a valid port but sends data in a way that hasn't been seen before.
*   **Wazuh's Reaction**: Because there is no "rule" for this specific data, it classifies it as "Normal Web Traffic" (Level 3). It isn't "smart" enough to know it's bad.
*   **ML Engine's Reaction**: It looks at features like `src_port`, `dst_port`, `action`, and `time`. It sees that these values don't fit the "Normal" cluster. It assigns an **Anomaly Score**. If the score is high (e.g., -0.8), it sends a "Next-Gen" alert back to Wazuh.
*   **Presentation Tip**: *"Wazuh is like a security guard with a list of known criminals. The ML Engine is like an experienced guard who notices someone acting suspiciously even if they aren't on the list."*

---

## 3. The Response Component (Shuffle SOAR)

### SOAR (Security Orchestration, Automation, and Response)
*   **What is it?** An automation platform.
*   **What does it do?** It connects different security tools together. Instead of a human having to manually block an IP address in the firewall, Shuffle receives the alert from Wazuh and automatically runs a script to block that IP.
*   **Presentation Tip**: *"The SIEM detects the fire, but the SOAR is the automatic sprinkler system that puts it out without human intervention."*

---

## 4. How Everything Connects (Data Flow)

1.  **Ingestion**: Logs come from the Manager.
2.  **Streaming**: The Manager streams these logs to the **ML Engine**.
3.  **Detection**: If ML Engine finds an anomaly, it writes a new alert.
4.  **Reaction**: The Manager sees the ML alert and sends a "Webhook" to **Shuffle SOAR**.
5.  **Action**: Shuffle executes the automated workflow.

---

## Common Viva Questions
*   **Q: Why use ML if Wazuh is already good?**
    *   *A: Because Wazuh relies on 'Known Bad' signatures. ML can detect 'Unknown Bad' (Zero-Day) attacks by looking at behavioral anomalies.*
*   **Q: What is the Anomaly Score?**
    *   *A: It's a mathematical value. Scores closer to -1 indicate highly unusual behavior, while scores closer to 1 are very normal.*
*   **Q: Is this real-time?**
    *   *A: Yes, logs are processed within seconds of being generated.*
