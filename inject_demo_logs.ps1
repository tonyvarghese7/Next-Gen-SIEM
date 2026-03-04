# Script to inject test alerts into Wazuh logs for ML Demo

$wazuh_path = "/var/ossec/logs/alerts/alerts.json"
$container = "next-gen-siem-ml-engine-1" # Adjust if your container name is different, usually dir_service_1

# 1. Normal Traffic Pattern (HTTP on port 80)
$normal_log = @{
    timestamp = "2023-10-27T10:00:00.000+0000"
    rule = @{ id = "100001"; description = "Normal Web Traffic" }
    data = @{ src_port = "12345"; dst_port = "80"; action = "allow" }
    id = "demo_normal_001"
} | ConvertTo-Json -Compress
$normal_log += "`n"

# 2. Anomalous Traffic Pattern (High port, unusual action)
$anomaly_log = @{
    timestamp = "2023-10-27T03:00:00.000+0000" # 3 AM
    rule = @{ id = "999999"; description = "Suspicious Traffic" }
    data = @{ src_port = "66666"; dst_port = "31337"; action = "drop" } # High ports
    id = "demo_anomaly_001"
} | ConvertTo-Json -Compress
$anomaly_log += "`n"

Write-Host "Injecting Normal Log..." -ForegroundColor Green
$tempFile = "demo_log_temp.json"
$normal_log | Out-File -FilePath $tempFile -Encoding ascii -NoNewline
docker cp $tempFile ${container}:/tmp/normal.json
docker exec $container sh -c "cat /tmp/normal.json >> $wazuh_path"

Start-Sleep -Seconds 2

Write-Host "Injecting Anomalous Log..." -ForegroundColor Red
$anomaly_log | Out-File -FilePath $tempFile -Encoding ascii -NoNewline
docker cp $tempFile ${container}:/tmp/anomaly.json
docker exec $container sh -c "cat /tmp/anomaly.json >> $wazuh_path"

# Cleanup
Remove-Item $tempFile
docker exec $container rm /tmp/normal.json /tmp/anomaly.json

Write-Host "Injection Complete. Check ml-engine logs."
