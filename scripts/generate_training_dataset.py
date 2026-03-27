import json
from typing import List, Dict

# Define the extraction and generation function
def generate_training_samples(measurements: List[Dict], protocol: str) -> List[Dict]:
    instructions = []
    for measurement in measurements:
        if protocol == "OPTIMIZE":
            instructions.append({
                "instruction": "Optimize the EcoLobster measurement for better performance.",
                "input": measurement,
                "output": optimize_measurement(measurement)
            })
        elif protocol == "DIAGNOSE":
            instructions.append({
                "instruction": "Diagnose the given EcoLobster measurement.",
                "input": measurement,
                "output": diagnose_measurement(measurement)
            })
        elif protocol == "COMPARE":
            instructions.append({
                "instruction": "Compare this measurement with another measurement.",
                "input": measurement,
                "output": compare_measurement(measurement)
            })
        elif protocol == "ESTIMATE":
            instructions.append({
                "instruction": "Estimate the future values based on this measurement.",
                "input": measurement,
                "output": estimate_values(measurement)
            })
        elif protocol == "AUDIT":
            instructions.append({
                "instruction": "Audit the accuracy of the EcoLobster measurement.",
                "input": measurement,
                "output": audit_measurement(measurement)
            })
    return instructions

# Stub functions for each protocol

def optimize_measurement(measurement):
    return "Optimized result"  # Replace with actual logic

def diagnose_measurement(measurement):
    return "Diagnosis result"  # Replace with actual logic

def compare_measurement(measurement):
    return "Comparison result"  # Replace with actual logic

def estimate_values(measurement):
    return "Estimated values"  # Replace with actual logic

def audit_measurement(measurement):
    return "Audit result"  # Replace with actual logic

# Example usage
if __name__ == '__main__':
    # Sample measurement data
    eco_lobster_measurements = [
        {"id": 1, "value": 100},
        {"id": 2, "value": 150}
    ]
    training_samples = []
    for protocol in ["OPTIMIZE", "DIAGNOSE", "COMPARE", "ESTIMATE", "AUDIT"]:
        training_samples.extend(generate_training_samples(eco_lobster_measurements, protocol))
    # Save as JSON
    with open('training_samples.json', 'w') as json_file:
        json.dump(training_samples, json_file, indent=4)
