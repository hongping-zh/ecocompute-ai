import json
import pandas as pd

# Load data from markdown files
rtx_data = pd.read_csv('RTX5090_Energy_Benchmark_Report.md', sep='|', skipinitialspace=True, engine='python')
quantization_data = pd.read_csv('data/QUANTIZATION_ENERGY_COMPLETE_DATASET_2026-03-06_EN.md', sep='|', skipinitialspace=True, engine='python')

# Process data - Extraction of relevant information
training_samples = []

protocol_types = ['OPTIMIZE', 'DIAGNOSE', 'COMPARE', 'ESTIMATE', 'AUDIT']

# Generate structured training samples
for index, row in rtx_data.iterrows():
    sample = {
        'instruction': f"Extract energy benchmarks for protocol type {protocol_types[index % len(protocol_types)]}.",
        'input_data': row.to_dict(),
        'protocol_type': protocol_types[index % len(protocol_types)]
    }
    training_samples.append(sample)

for index, row in quantization_data.iterrows():
    sample = {
        'instruction': f"Extract quantization data for protocol type {protocol_types[index % len(protocol_types)]}.",
        'input_data': row.to_dict(),
        'protocol_type': protocol_types[index % len(protocol_types)]
    }
    training_samples.append(sample)

# Ensure at least 500 samples
if len(training_samples) < 500:
    raise ValueError('Not enough samples generated.')

# Save generated training samples to JSON file
output_filepath = 'generated_training_samples.json'
with open(output_filepath, 'w') as json_file:
    json.dump(training_samples, json_file, indent=4)

print(f'Training samples saved to {output_filepath}')