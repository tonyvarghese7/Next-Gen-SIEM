# Wazuh Testing Guide - Next-Gen SIEM

This guide provides step-by-step instructions to run and test the Wazuh SIEM system in your Next-Gen-SIEM project.

## Prerequisites

- Docker Desktop installed and running
- PowerShell (Windows)
- At least 4GB RAM available for Docker
- Ports available: 443, 9200, 1514, 1515, 514, 55000

## Architecture Overview

Your SIEM stack includes:
- **Wazuh Manager**: Security monitoring and log analysis
- **Wazuh Indexer**: Data storage and indexing (OpenSearch-based)
- **Wazuh Dashboard**: Web UI for visualization
- **ML Engine**: Machine learning anomaly detection
- **Wazuh Agent**: Collects logs from monitored systems

---

## Step 1: Generate SSL Certificates

SSL certificates are required for secure communication between components.

```powershell
# Navigate to project directory
cd d:\Next-Gen-SIEM

# Generate certificates using Docker Compose
docker-compose -f generate-indexer-certs.yml run --rm generator
```

**Expected Output**: Certificate files created in `config/wazuh_indexer_ssl_certs/`

**Verification**:
```powershell
ls config/wazuh_indexer_ssl_certs/
```

You should see files like:
- `root-ca.pem`
- `admin.pem`, `admin-key.pem`
- `wazuh.manager.pem`, `wazuh.manager-key.pem`
- `wazuh.indexer.pem`, `wazuh.indexer-key.pem`
- `wazuh.dashboard.pem`, `wazuh.dashboard-key.pem`

---

## Step 2: Start the SIEM Stack

Start all services using Docker Compose.

```powershell
# Start all services in detached mode
docker-compose up -d
```

**Expected Output**:
```
Creating network "next-gen-siem_default" with the default driver
Creating volume "next-gen-siem_wazuh_logs" with default driver
...
Creating next-gen-siem_wazuh.indexer_1 ... done
Creating next-gen-siem_wazuh.manager_1  ... done
Creating next-gen-siem_wazuh.dashboard_1 ... done
Creating next-gen-siem_ml-engine_1      ... done
Creating next-gen-siem_wazuh-agent_1    ... done
```

---

## Step 3: Verify Container Status

Check that all containers are running properly.

```powershell
# Check container status
docker-compose ps
```

**Expected Output**: All services should show "Up" status
```
NAME                          STATUS
next-gen-siem_wazuh.manager_1    Up
next-gen-siem_wazuh.indexer_1    Up
next-gen-siem_wazuh.dashboard_1  Up
next-gen-siem_ml-engine_1        Up
next-gen-siem_wazuh-agent_1      Up
```

**Check Container Logs** (if any service is not running):
```powershell
# View logs for specific service
docker-compose logs wazuh.manager
docker-compose logs wazuh.indexer
docker-compose logs wazuh.dashboard
```

---

## Step 4: Wait for Services to Initialize

Services need time to fully initialize (especially the indexer).

```powershell
# Wait 2-3 minutes, then check Wazuh Manager status
docker-compose logs wazuh.manager | Select-String "Listening on port"
```

**Expected Output**: Should show the manager is listening on ports 1514, 1515, and 55000

```powershell
# Check Indexer health
docker-compose exec wazuh.indexer curl -k -u admin:SecretPassword https://localhost:9200/_cluster/health?pretty
```

**Expected Output**:
```json
{
  "cluster_name" : "wazuh-cluster",
  "status" : "green",
  "number_of_nodes" : 1
}
```

---

## Step 5: Access Wazuh Dashboard

Open the web interface to interact with Wazuh.

### Access URL
```
https://localhost
```

### Default Credentials
- **Username**: `admin`
- **Password**: `admin`

### First Login Steps
1. Open browser and navigate to `https://localhost`
2. Accept the self-signed certificate warning
3. Enter credentials: `admin` / `admin`
4. You should see the Wazuh Dashboard home page

**Troubleshooting**:
- If page doesn't load, wait another 2-3 minutes for dashboard initialization
- Check dashboard logs: `docker-compose logs wazuh.dashboard`

---

## Step 6: Verify Agent Connection

Check that the Wazuh agent is connected to the manager.

### Via Dashboard
1. Navigate to **Agents** in the left sidebar
2. You should see `demo-agent` listed with status "Active"

### Via Command Line
```powershell
# List connected agents
docker-compose exec wazuh.manager /var/ossec/bin/agent_control -l
```

**Expected Output**:
```
Wazuh agent_control. List of available agents:
   ID: 001, Name: demo-agent, IP: any, Active/Local
```

---

## Step 7: Test Log Ingestion

Verify that Wazuh is receiving and processing logs.

### Method 1: Inject Demo Logs (Recommended)

Use the provided PowerShell script to inject test logs:

```powershell
# Inject demo security logs
.\inject_demo_logs.ps1
```

**What it does**: Simulates various security events (SSH logins, web attacks, etc.)

### Method 2: Manual Log Injection

```powershell
# Execute command inside the agent container
docker-compose exec wazuh-agent bash -c "logger -t test 'Test security event from Wazuh agent'"
```

### Verify Logs in Dashboard
1. Go to **Security Events** or **Discover** tab
2. Set time range to "Last 15 minutes"
3. You should see the injected events

---

## Step 8: Test ML Engine Integration

Verify the machine learning engine is processing logs.

### Check ML Engine Status
```powershell
# View ML engine logs
docker-compose logs ml-engine
```

**Expected Output**: Should show the ML engine starting and processing logs

### Trigger ML Anomaly Detection

```powershell
# Inject zero-day attack simulation
.\inject_zeroday.ps1
```

**What it does**: Simulates anomalous behavior that the ML engine should detect

### Verify ML Alerts
1. In Wazuh Dashboard, go to **Security Events**
2. Filter by rule group: `ml_detection`
3. You should see alerts generated by the ML engine

---

## Step 9: Test SOAR Integration (Optional)

If you have Shuffle SOAR configured:

```powershell
# Trigger SOAR workflow demo
.\trigger_soar_demo.ps1
```

**What it does**: Sends test alerts to Shuffle for automated response

---

## Step 10: Health Check Summary

Run these commands to verify overall system health:

```powershell
# 1. Check all containers are running
docker-compose ps

# 2. Check Wazuh Manager API
docker-compose exec wazuh.manager curl -k -u wazuh-wui:MyS3cr37P450r.*- https://localhost:55000/

# 3. Check Indexer cluster health
docker-compose exec wazuh.indexer curl -k -u admin:SecretPassword https://localhost:9200/_cluster/health?pretty

# 4. Check agent status
docker-compose exec wazuh.manager /var/ossec/bin/agent_control -l

# 5. View recent alerts
docker-compose exec wazuh.manager tail -n 20 /var/ossec/logs/alerts/alerts.json
```

---

## Common Testing Scenarios

### Test 1: SSH Brute Force Detection

```powershell
# Simulate multiple failed SSH attempts
docker-compose exec wazuh-agent bash -c "
for i in {1..10}; do
  logger -t sshd 'Failed password for invalid user admin from 192.168.1.100 port 22 ssh2'
  sleep 1
done
"
```

**Expected**: Alert for SSH brute force attack in dashboard

### Test 2: Web Attack Detection

```powershell
# Simulate SQL injection attempt
docker-compose exec wazuh-agent bash -c "logger -t apache 'GET /index.php?id=1%27%20OR%201=1-- HTTP/1.1'"
```

**Expected**: Web attack alert in dashboard

### Test 3: File Integrity Monitoring

```powershell
# Create/modify a monitored file
docker-compose exec wazuh-agent bash -c "echo 'test' > /tmp/test_fim.txt"
```

**Expected**: File integrity monitoring alert (if FIM is configured)

---

## Monitoring and Logs

### View Real-time Logs

```powershell
# Wazuh Manager logs
docker-compose logs -f wazuh.manager

# All services logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f wazuh.dashboard
docker-compose logs -f ml-engine
```

### Access Log Files Directly

```powershell
# Wazuh alerts (JSON format)
docker-compose exec wazuh.manager tail -f /var/ossec/logs/alerts/alerts.json

# Wazuh manager log
docker-compose exec wazuh.manager tail -f /var/ossec/logs/ossec.log
```

---

## Performance Metrics

### Check Resource Usage

```powershell
# View container resource usage
docker stats
```

### Check Indexer Statistics

```powershell
# View index statistics
docker-compose exec wazuh.indexer curl -k -u admin:SecretPassword https://localhost:9200/_cat/indices?v
```

---

## Troubleshooting

### Issue: Containers Keep Restarting

```powershell
# Check logs for errors
docker-compose logs wazuh.indexer | Select-String "ERROR"

# Check system resources
docker stats

# Increase Docker memory allocation (Docker Desktop Settings)
```

### Issue: Dashboard Not Accessible

```powershell
# Check dashboard status
docker-compose ps wazuh.dashboard

# View dashboard logs
docker-compose logs wazuh.dashboard

# Restart dashboard
docker-compose restart wazuh.dashboard
```

### Issue: Agent Not Connecting

```powershell
# Check agent logs
docker-compose logs wazuh-agent

# Verify manager is listening
docker-compose exec wazuh.manager netstat -tuln | Select-String "1514"

# Restart agent
docker-compose restart wazuh-agent
```

### Issue: No Alerts Appearing

```powershell
# Check if logs are reaching manager
docker-compose exec wazuh.manager tail /var/ossec/logs/archives/archives.log

# Check rule configuration
docker-compose exec wazuh.manager cat /var/ossec/etc/rules/ml_rules.xml

# Restart manager to reload rules
docker-compose restart wazuh.manager
```

---

## Stopping and Cleaning Up

### Stop All Services

```powershell
# Stop all containers
docker-compose down
```

### Stop and Remove All Data

```powershell
# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

### Restart Services

```powershell
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart wazuh.manager
```

---

## Next Steps

1. **Configure Custom Rules**: Edit `config/rules/ml_rules.xml` to add custom detection rules
2. **Add More Agents**: Deploy Wazuh agents on other systems to monitor
3. **Configure Integrations**: Set up Shuffle SOAR, email alerts, or Slack notifications
4. **Tune ML Models**: Adjust ML engine parameters in `ml/` directory
5. **Create Custom Dashboards**: Build visualizations in Wazuh Dashboard

---

## Quick Reference

### Important URLs
- **Wazuh Dashboard**: https://localhost
- **Wazuh API**: https://localhost:55000
- **Indexer API**: https://localhost:9200

### Default Credentials
- **Dashboard**: admin / admin
- **API**: wazuh-wui / MyS3cr37P450r.*-
- **Indexer**: admin / SecretPassword

### Key Directories
- **Config**: `d:\Next-Gen-SIEM\config\`
- **ML Models**: `d:\Next-Gen-SIEM\ml\`
- **Logs**: Docker volume `wazuh_logs`
- **Rules**: `config/rules/ml_rules.xml`

### Useful Commands
```powershell
# Start stack
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Stop stack
docker-compose down

# Restart service
docker-compose restart <service-name>
```

---

## Support and Documentation

- **Wazuh Documentation**: https://documentation.wazuh.com/
- **Project README**: [README.md](file:///d:/Next-Gen-SIEM/README.md)
- **Docker Compose Config**: [docker-compose.yml](file:///d:/Next-Gen-SIEM/docker-compose.yml)
