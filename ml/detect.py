import time
import json
import traceback
import joblib
import pandas as pd
import os
from features import LogFeatureExtractor, create_preprocessor

# Paths
LOG_FILE = '/var/ossec/logs/alerts/alerts.json'
MODEL_DIR = './models'
ANOMALY_LOG = '/var/ossec/logs/ml_anomalies.json'

# Load Models
print("Loading models...")
try:
    iso_forest = joblib.load(os.path.join(MODEL_DIR, 'iso_forest_model.joblib'))
    mlp = joblib.load(os.path.join(MODEL_DIR, 'mlp_model.joblib'))
    pipeline = joblib.load(os.path.join(MODEL_DIR, 'pipeline.joblib'))
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    exit(1)

def follow(thefile):
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(1)
            # Check if file was rotated or recreated
            try:
                if os.stat(LOG_FILE).st_ino != os.fstat(thefile.fileno()).st_ino:
                    new_file = open(LOG_FILE, 'r')
                    thefile.close()
                    thefile = new_file
            except:
                pass
            continue
        yield line

def process_log(line):
    if not line.strip():
        return
    try:
        data = json.loads(line)
        
        # Extract features expected by the model
        # The features.py expects a DataFrame with specific columns
        # We need to map the alert JSON to these columns
        
        log_data = {
            'timestamp': data.get('timestamp'),
            'src_port': data.get('data', {}).get('src_port'),
            'dst_port': data.get('data', {}).get('dst_port'),
            'rule_id': data.get('rule', {}).get('id'),
            'action': data.get('data', {}).get('action', 'unknown') # Default if missing
        }
        
        df = pd.DataFrame([log_data])
        
        # Transform features
        # Assuming the pipeline includes the preprocessor, or we need to use features.py manually
        # Based on features.py content, it has LogFeatureExtractor and create_preprocessor
        # Let's see if the pipeline.joblib already includes these or if we need to apply them.
        # Usually requirements for pipeline are strict.
        
        # Let's try predicting with the pipeline directly first if it encapsulates everything
        # If not, we might need to use the extracted features class.
        
        # For this implementation, I will assume the pipeline handles the transformation 
        # OR use the loaded pipeline object which likely is the full pipeline.
        
        prediction = iso_forest.predict(pipeline.transform(df))
        score = iso_forest.decision_function(pipeline.transform(df))
        print(f"Processed alert {data.get('id')}: Prediction={prediction[0]} Score={score[0]:.4f}")
        
        if score[0] < 0.1: # Adjusted threshold for demo sensitivity (normally 0)
            print(f"Anomaly detected: {data.get('id')}")
            with open(ANOMALY_LOG, 'a') as f:
                anomaly_record = {
                    'timestamp': data.get('timestamp'),
                    'alert_id': data.get('id'),
                    'description': data.get('rule', {}).get('description'),
                    'prediction': 'anomaly',
                    'score': float(score[0])
                }
                f.write(json.dumps(anomaly_record) + '\n')
                
    except Exception as e:
        print(f"Error processing log: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print(f"Monitoring {LOG_FILE}...")
    # Wait for file to exist
    while not os.path.exists(LOG_FILE):
        print(f"Waiting for {LOG_FILE}...")
        time.sleep(5)

    with open(LOG_FILE, 'r') as f:
        for line in follow(f):
            process_log(line)
