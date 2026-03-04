# Script to inject a "Stealth" attack log
# Scenario: An attacker uses a valid application port (80) but executes a malicious payload pattern 
# that Wazuh doesn't have a specific signature for yet (Zero-Day).
# Wazuh sees it as just "Web Traffic" (Level 3), but ML sees the anomaly in the packet features.

$wazuh_path = "/var/ossec/logs/alerts/alerts.json"
$container = "next-gen-siem-ml-engine-1"

# 1. The Stealth Log
# - Rule ID: 100001 (Normal Web Traffic) -> Wazuh thinks this is fine.
# - Data Features: Unusual source port (99999 is invalid/anomaly), weird time, strange metadata.
$stealth_log = @{
    timestamp = "2023-10-27T04:20:00.000+0000" # 4 AM (Unusual time)
    rule = @{ 
        id = "100001" 
        description = "Web Server Log - 200 OK" 
        level = 3 # Low level, usually ignored by analysts
    }
    data = @{ 
        src_port = "66666" 
        dst_port = "31337" 
        action = "drop" # From known anomaly
        user_agent = "MaliciousBot/1.0" 
    }
    id = "demo_zeroday_001"
} | ConvertTo-Json -Compress
$stealth_log += "`n"

Write-Host "Injecting 'Stealth' Zero-Day Attack Log..." -ForegroundColor Yellow
Write-Host "Wazuh Classification: Low Risk (Level 3)" -ForegroundColor Gray

# Write to a temp file first to ensure encoding is perfect
$tempFile = "web_log_temp.json"
$stealth_log | Out-File -FilePath $tempFile -Encoding ascii -NoNewline

# Copy to container
docker cp $tempFile ${container}:/tmp/stealth.json

# Append to alerts.json
docker exec $container sh -c "cat /tmp/stealth.json >> $wazuh_path"

# Cleanup
Remove-Item $tempFile
docker exec $container rm /tmp/stealth.json

Write-Host "Injection Complete. Check if ML flagged it as an Anomaly." -ForegroundColor Green
