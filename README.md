# Next-Generation SIEM with ML Anomaly Detection

A comprehensive, state-of-the-art Security Information and Event Management (SIEM) system built on the Wazuh stack, enhanced with Machine Learning for anomaly detection and Shuffle SOAR for automated incident response.

## 🚀 Key Features

- **Real-time Log Analysis**: High-performance log ingestion and analysis using Wazuh.
- **ML Anomaly Detection**: Integrated Python-based ML engine to detect "Stealth" and Zero-Day attacks that bypass traditional signature-based rules.
- **SOAR Automation**: Automated incident response workflows using Shuffle SOAR.
- **Centralized Visualization**: Beautiful and intuitive dashboards using Wazuh Dashboard (OpenSearch).
- **Endpoint Monitoring**: Robust file integrity monitoring and vulnerability detection.

## 🛠️ Quick Start

### 1. Prerequisites
- Docker Desktop
- 8GB+ RAM allocated to Docker

### 2. Deployment
```powershell
# Generate SSL Certificates
docker-compose -f generate-indexer-certs.yml run --rm generator

# Start the Stack
docker-compose up -d
```

### 3. Access
- **Wazuh Dashboard**: `https://localhost` (admin/admin)
- **Wazuh API**: `https://localhost:55000`
- **Local SOAR Responder API**: `http://localhost:8088/health`

---

## 📖 Documentation & Guides

- [**Simulation & Demonstration Guide**](file:///d:/Next-Gen-SIEM/SIMULATION_GUIDE.md): Detailed steps and commands for your demo.
- [**Lifecycle Management Guide**](file:///d:/Next-Gen-SIEM/LIFECYCLE_GUIDE.md): How to properly stop, start, and reset the entire system.
- [**Technical Explanation Guide**](file:///d:/Next-Gen-SIEM/PROJECT_EXPLANATION.md): Deep-dive into ML and component logic.
- [**Implementation Roadmap**](file:///d:/Next-Gen-SIEM/IMPLEMENTATION_ROADMAP.md): How we built the project.
- [**Wazuh Testing Guide**](file:///d:/Next-Gen-SIEM/WAZUH_TESTING_GUIDE.md): Technical verification.

---

## 🏗️ Architecture

```mermaid
graph TD
    A[Wazuh Agent] -->|Logs| B(Wazuh Manager)
    B -->|Alerts| C(Wazuh Indexer)
    C <--> D(Wazuh Dashboard)
    B -->|LogStream| E(ML Engine)
    E -->|Anomaly Alerts| B
    B -->|Webhooks| F(Shuffle SOAR)
    F -->|HTTP Actions| G(Local SOAR Responder API)
    G -->|Mitigation (simulated)| A
```
