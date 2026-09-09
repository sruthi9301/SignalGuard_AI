import random
from statistics import mean
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def normal_signal():
    return [
        random.uniform(88, 108),
        random.gauss(-48, 5),
        max(20, random.gauss(180, 35)),
        max(-90, random.gauss(-72, 4))
    ]

def anomaly_signal():
    return [
        random.choice([
            random.uniform(20, 40),
            random.uniform(140, 170),
            random.uniform(400, 450)
        ]),
        random.uniform(-18, -5),
        random.uniform(650, 1200),
        random.uniform(-48, -25)
    ]

def generate_signal_dataset(count=70, anomaly_rate=0.12):
    rows = []
    for i in range(count):
        injected = random.random() < anomaly_rate
        values = anomaly_signal() if injected else normal_signal()
        rows.append({
            "id": i + 1,
            "frequency_mhz": round(values[0], 2),
            "amplitude_db": round(values[1], 2),
            "bandwidth_khz": round(values[2], 2),
            "noise_db": round(values[3], 2),
            "source": "simulated",
            "injected_anomaly": injected
        })
    return rows

def train_model():
    training = [normal_signal() for _ in range(500)]
    scaler = StandardScaler()
    X = scaler.fit_transform(training)
    model = IsolationForest(
        n_estimators=150,
        contamination=0.08,
        random_state=42
    )
    model.fit(X)
    baseline = {
        "frequency_mhz": round(mean(x[0] for x in training), 2),
        "amplitude_db": round(mean(x[1] for x in training), 2),
        "bandwidth_khz": round(mean(x[2] for x in training), 2),
        "noise_db": round(mean(x[3] for x in training), 2)
    }
    return model, scaler, baseline

def analyze_signal(rows, model, scaler, baseline):
    matrix = [[r["frequency_mhz"], r["amplitude_db"],
               r["bandwidth_khz"], r["noise_db"]] for r in rows]
    transformed = scaler.transform(matrix)
    predictions = model.predict(transformed)
    scores = model.decision_function(transformed)

    output = []
    anomalies = 0
    for row, prediction, score in zip(rows, predictions, scores):
        is_anomaly = prediction == -1
        anomalies += int(is_anomaly)
        distance = min(abs(float(score)), 1.0)
        confidence = (55 + distance * 40) if is_anomaly else (90 - distance * 25)
        severity = "High" if is_anomaly and row["amplitude_db"] > -25 else ("Medium" if is_anomaly else "Low")
        output.append({
            **row,
            "status": "Anomaly" if is_anomaly else "Normal",
            "severity": severity,
            "confidence": round(confidence, 1),
            "score": round(float(score), 4)
        })

    return {
        "signals": output,
        "summary": {
            "total": len(output),
            "anomalies": anomalies,
            "normal": len(output) - anomalies,
            "anomaly_rate": round(anomalies / len(output) * 100, 1),
            "baseline": baseline
        }
    }
