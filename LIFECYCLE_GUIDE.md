# Lifecycle Management Guide - Next-Gen SIEM

This guide provides procedures for properly stopping and starting the SIEM project, whether you want to resume work or start from a completely fresh state.

---

## 🛑 Proper Shutdown Procedures

### 1. Standard Stop (Recommended)
Use this if you want to stop the services but **keep your data** (logs, alerts, and dashboards) for the next time.
```powershell
docker-compose stop
```

### 2. Full Stop (Remove Containers)
Use this to stop and remove all containers while still **preserving your data** in external volumes.
```powershell
docker-compose down
```

### 3. Total Wipe (Start from Scratch)
**WARNING**: This will delete all your alerts, logs, and dashboard configurations.
```powershell
docker-compose down -v
```

---

## 🚀 Starting Procedures

### 1. Resuming the System
If you previously used `stop` or `down` without the `-v` flag, you can resume exactly where you left off:
```powershell
docker-compose up -d
```

### 2. Starting from Scratch (Cold Start)
If you have never run the project on this machine, or if you just used `down -v` to wipe it:

#### Step A: Generate SSL Certificates
Wazuh requires fresh certificates for its internal mTLS communication.
```powershell
docker-compose -f generate-indexer-certs.yml run --rm generator
```

#### Step B: Bring up the Stack
```powershell
docker-compose up -d
```

#### Step C: Implementation Checks
Wait about 2-3 minutes for the Indexer to initialize, then check the status:
```powershell
docker-compose ps
```

---

## 🔧 Troubleshooting Startup Issues

### "API Connection Down"
If you see this in the dashboard after a restart:
1. Verify all containers are "Up".
2. Check the manager logs: `docker-compose logs wazuh.manager`.
3. If you see configuration errors, ensure `config/wazuh_cluster/wazuh_manager.conf` has only one `<ossec_config>` block (this was fixed in your implementation).

### "Indexer Health Red/Yellow"
Wait a few more minutes. The Indexer (OpenSearch) can take time to perform internal health checks after a cold start.

---

## 💡 Pro-Tip
For a smooth demonstration, always start the stack at least 15 minutes before your guide arrives to ensure all background initialization is complete.
