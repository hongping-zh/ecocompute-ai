import random
import json

# Sample data for demonstration purposes
protocols = {
    "OPTIMIZE": ["Optimize the model for speed", "Reduce memory usage", "Enhance accuracy"],
    "DIAGNOSE": ["Diagnose the performance issues", "Analyze model behavior", "Identify potential bottlenecks"],
    "COMPARE": ["Compare against baseline performance", "Benchmark with other models", "Evaluate different quantization methods"],
    "ESTIMATE": ["Estimate the expected loss", "Predict the runtime", "Assess the memory footprint"],
    "AUDIT": ["Audit the model for compliance", "Check the training data integrity", "Ensure fairness in predictions"],
}

def generate_samples(protocol, count):
    samples = []
    for _ in range(count):
        instruction = random.choice(protocols[protocol])
        sample = {
            "protocol": protocol,
            "instruction": instruction,
            "additional_info": f"This is a sample for {protocol}."
        }
        samples.append(sample)
    return samples

def main():
    total_samples = 500
    samples_per_protocol = total_samples // len(protocols)

    all_samples = []
    for protocol in protocols.keys():
        all_samples.extend(generate_samples(protocol, samples_per_protocol))

    # If uneven distribution, fill the rest with random instructions 
    remaining_count = total_samples - len(all_samples)
    if remaining_count > 0:
        additional_samples = generate_samples(random.choice(list(protocols.keys())), remaining_count)
        all_samples.extend(additional_samples)

    # Save the samples to a JSON file
    with open('instruction_following_samples.json', 'w') as f:
        json.dump(all_samples, f, indent=4)

if __name__ == "__main__":
    main()