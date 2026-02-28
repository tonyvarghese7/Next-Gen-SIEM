# Simulation & Demonstration Guide - Next-Gen SIEM

This guide provides the exact commands and steps required to simulate security attacks and demonstrate the full capabilities of the Next-Gen SIEM system (Wazuh + ML Engine + Shuffle SOAR) to a project guide or evaluator.

> [!IMPORTANT]
> **Need help explaining the technology?** Check out the [**PROJECT_EXPLANATION.md**](file:///d:/Next-Gen-SIEM/PROJECT_EXPLANATION.md) for technical deep-dives into how the ML engine and SOAR work.

---

## 🚀 Demonstration Flow

1.  **System Health**: Show all containers running and the Wazuh Dashboard.
2.  **Signature-Based Detection**: Simulate a Brute Force attack detected by standard Wazuh rules.
3.  **Anomaly-Based Detection (ML)**: Simulate a "Stealth" Zero-Day attack that bypasses standard rules but is caught by the Machine Learning engine.
4.  **Automated Response (SOAR)**: Demonstrate how an alert triggers an automated workflow in Shuffle SOAR.

---

## 🛠️ Phase 1: Preparation

Ensure all services are running:
```powershell
docker-compose ps
```
The status should show `Up` for Indexer, Manager, Dashboard, and ML-Engine.

---

## 🛡️ Phase 2: Simulating Traditional Attacks

### Scenario 1: SSH Brute Force Detection
Standard Wazuh rules detect multiple failed login attempts.

**Command**:
```powershell
# Simulate 10 failed login attempts in 10 seconds
docker-compose exec wazuh.manager bash -c "for i in {1..10}; do logger -t sshd 'Failed password for root from 192.168.1.100 port 22 ssh2'; sleep 1; done"
```

**What to show in Dashboard**:
1. Go to **Security Events**.
2. Filter for `Rule ID: 5712` (SSHD brute force).
3. Show the alert and the high severity level.

### Scenario 2: Web Attack (SQL Injection)
Simulate a malicious web request.

**Command**:
```powershell
docker-compose exec wazuh.manager bash -c "logger -t apache 'GET /index.php?id=1%27%20OR%201=1-- HTTP/1.1' 200"
```

**What to show in Dashboard**:
1. Search for "SQL Injection" in the search bar.
2. Show the alert generated for the suspicious URI pattern.

---

## 🤖 Phase 3: Simulating ML-Driven Anomaly Detection

This is the core "Next-Gen" feature. We will simulate a "Stealth" attack that uses valid ports but anomalous patterns.

### Scenario 3: Zero-Day / Stealth Anomaly
Traditional rules see this as "Normal Web Traffic", but the ML Engine flags the anomaly.

**Command**:
```powershell
.\inject_zeroday.ps1
```

**What to show in Dashboard**:
1. Navigate to **Security Events**.
2. Search for `ml_detection`.
3. **The Wow Factor**: Show the "Normal Web Traffic" alert (Level 3) side-by-side with the "ML Engine Detected Anomaly" alert (Level 12) for the same event.

---

## ⚡ Phase 4: Automated Response (SOAR)

Demonstrate the integration with Shuffle SOAR for rapid incident response.

**Command**:
```powershell
.\trigger_soar_demo.ps1
```

**Demonstration Steps**:
1. Run the script and show the "SUCCESS" response in PowerShell.
2. Open **Shuffle UI**: `http://localhost:3001` (or your configured port).
3. Show the **Workflow Execution** triggered by the alert.
4. Explain how this replaces manual analyst tasks (e.g., auto-blocking an IP).

---

## 📊 Phase 5: Dashboard Overview

Point out these key areas during the demo:
- **Agents Tab**: Show the connected monitoring endpoints.
- **Vulnerabilities**: If scans have run, show the vulnerability map.
- **Security Events**: The real-time stream of all detected threats.

---

> [!TIP]
> **Pro-Tip for Demo**: Always have the Wazuh Dashboard open in the "Discover" tab with a 15-minute refresh rate so alerts appear live as you run the scripts.
