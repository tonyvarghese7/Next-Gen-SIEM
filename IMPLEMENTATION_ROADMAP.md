# Implementation Roadmap - Next-Gen SIEM

This document details the step-by-step construction of the Next-Generation SIEM project, explaining how we transformed a standard monitoring tool into an intelligent, automated security platform.

---

## Phase 0: The Foundation (Infrastructure)

The project began with a **containerized architecture** using Docker Compose. This ensures all components (Indexer, Manager, Dashboard) are isolated but can communicate securely.

1.  **Container Selection**: We used the Wazuh 4.7.2 stack for stability and compatibility.
2.  **Resource Optimization**: Configured memory limits (`vm.max_map_count`) and JVM options to ensure the Indexer (OpenSearch) performs efficiently on local hardware.

---

## Phase 1: Security & Trust (Certificates)

To protect security data, we implemented **Mutual TLS (mTLS)** across all components.
*   **How we did it**: We used a temporary `generator` container to create a unique Root Certificate Authority (CA) and issued individual node certificates for the Manager, Indexer, and Dashboard.
*   **Result**: All internal traffic is encrypted, preventing attackers from intercepting alerts.

---

## Phase 2: Intelligence Layer (ML Engine)

The core innovation is the custom **Machine Learning Engine**.

1.  **The Detector (`detect.py`)**: Developed in Python using the `scikit-learn` and `pandas` libraries.
2.  **Data Streaming**: We used a **Volume Mount** to share the Manager's logs (`alerts.json`) with the ML container in real-time.
3.  **The Algorithm**: 
    *   Uses a pre-trained **Isolation Forest** model to perform "Unsupervised Learning".
    *   It analyzes 5-dimensional feature sets: `timestamp`, `src_port`, `dst_port`, `rule_id`, and `action`.
4.  **Anomaly Injection**: When a log deviates from the norm (indicated by a negative `decision_function` score), the engine writes an anomaly record to a dedicated JSON file.

---

## Phase 3: The Integration Bridge

To make the ML alerts visible in the Dashboard, we had to bridge the ML Engine back to Wazuh.

1.  **Custom Rules**: We created `config/rules/ml_rules.xml`, defining Rule ID `100010`.
2.  **Log Integration**: Configured the Wazuh Manager to monitor the ML Engine's output file (`ml_anomalies.json`).
3.  **The Result**: The "Statistical Findings" from the ML engine are converted back into "Security Events" that appear in the Wazuh Dashboard.

---

## Phase 4: Active Response (Shuffle SOAR)

Finally, we closed the loop with automation.

1.  **Webhook Configuration**: Configured Wazuh to send JSON payloads to the **Shuffle SOAR** endpoint whenever a high-severity ML alert is triggered.
2.  **Workflow Design**: Built a Shuffle workflow that parses the IP address from the alert and (hypothetically) triggers a block on the endpoint or sends a Slack notification.

---

## Summary of the "How"

We didn't just "install" a SIEM; we **engineered a pipeline**:
*   **Ingestion** (Manager) ➔ **Analysis** (ML Engine) ➔ **Ingest Again** (Manager) ➔ **Visualization** (Dashboard) ➔ **Automation** (Shuffle).

This multi-stage architecture represents the "Next-Gen" approach to modern cybersecurity.
