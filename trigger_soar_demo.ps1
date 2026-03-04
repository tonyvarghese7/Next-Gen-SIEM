##############################################
# SOAR Demonstration Script
#############################################
# This script demonstrates the automated response flow:
# Wazuh Alert → Shuffle SOAR → Automated Action

$webhookUrl = "http://localhost:3001/api/v1/hooks/webhook_ae437071-5388-4f1a-b7ff-5deb98c16fa9"

# Simulate a Wazuh ML Anomaly Alert (Rule 100010)
$wazuhAlert = @{
    "timestamp" = (Get-Date -Format "o")
    "rule" = @{
        "level" = 12
        "description" = "ML Engine Detected Anomaly"
        "id" = "100010"
        "firedtimes" = 1
        "mail" = $true
        "groups" = @("ml_detection", "high_severity")
    }
    "agent" = @{
        "id" = "000"
        "name" = "demo-agent"
        "ip" = "172.18.0.5"
    }
    "manager" = @{
        "name" = "wazuh.manager"
    }
    "id" = "demo_ml_anomaly_001"
    "full_log" = "ML Model detected anomalous behavior: Stealth attack on port 66666"
    "decoder" = @{
        "name" = "ml_engine"
    }
    "data" = @{
        "prediction" = "anomaly"
        "anomaly_score" = "-0.85"
        "src_ip" = "192.168.1.100"
        "dst_port" = "66666"
        "action" = "connection_attempt"
    }
    "location" = "/var/ossec/logs/ml_anomalies.json"
} | ConvertTo-Json -Depth 10

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SOAR DEMONSTRATION - Triggering Shuffle" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "[STEP 1] Simulating ML Detection..." -ForegroundColor Yellow
Write-Host "          → Anomaly Score: -0.85"
Write-Host "          → Source IP: 192.168.1.100"
Write-Host "          → Suspicious Port: 66666`n"

Write-Host "[STEP 2] Sending Alert to Shuffle SOAR..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $wazuhAlert -ContentType "application/json"
    Write-Host "          → Webhook Response: SUCCESS`n" -ForegroundColor Green
    
    Write-Host "[STEP 3] Check Shuffle for Automated Response:" -ForegroundColor Yellow
    Write-Host "          → Open: http://localhost:3001"
    Write-Host "          → Navigate to your workflow"
    Write-Host "          → Click execution count (top-right)"
    Write-Host "          → View the alert data and any configured actions`n"
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ SOAR DEMONSTRATION COMPLETE!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    
} catch {
    Write-Host "          → Error: $($_.Exception.Message)`n" -ForegroundColor Red
    Write-Host "[TROUBLESHOOTING]" -ForegroundColor Yellow
    Write-Host "  1. Verify Shuffle is running: docker-compose ps (in shuffle directory)"
    Write-Host "  2. Verify webhook is started in Shuffle UI"
    Write-Host "  3. Check webhook URL matches: $webhookUrl`n"
}
