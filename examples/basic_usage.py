"""
Basic usage example for EcoCompute AI.
"""

from ecocompute import EnergyAuditor, estimate_training_cost, format_training_estimate


def example_energy_auditing():
    """Example: Monitor energy during inference."""
    print("=" * 50)
    print("Example 1: Energy Auditing")
    print("=" * 50)
    
    # Note: This requires a GPU with NVML support
    try:
        auditor = EnergyAuditor(gpu_index=0, sample_interval_ms=100)
        auditor.start()
        
        # Simulate some work (replace with your actual inference code)
        import time
        time.sleep(2)
        
        energy, avg_power, peak_power = auditor.stop()
        
        print(f"Energy consumed: {energy:.2f} J")
        print(f"Average power: {avg_power:.2f} W")
        print(f"Peak power: {peak_power:.2f} W")
        
    except ImportError as e:
        print(f"Note: {e}")
        print("Install pynvml to use energy auditing: pip install pynvml")


def example_training_estimation():
    """Example: Estimate training cost before starting."""
    print("\n" + "=" * 50)
    print("Example 2: Training Cost Estimation")
    print("=" * 50)
    
    # Estimate cost for training a 1.3B model on 100B tokens
    estimate = estimate_training_cost(
        model_params=1.3e9,      # 1.3B parameters
        training_tokens=100e9,   # 100B tokens
        gpu_type="A100-80GB",
        num_gpus=8,
        cloud_region="us-east",
    )
    
    print(format_training_estimate(estimate))


def example_compare_configurations():
    """Example: Compare different hardware configurations."""
    print("\n" + "=" * 50)
    print("Example 3: Compare Hardware Configurations")
    print("=" * 50)
    
    configs = [
        {"gpu_type": "A100-80GB", "num_gpus": 8},
        {"gpu_type": "H100-80GB", "num_gpus": 4},
        {"gpu_type": "RTX-4090", "num_gpus": 8},
    ]
    
    model_params = 7e9  # 7B model
    training_tokens = 500e9  # 500B tokens
    
    print(f"Model: {model_params/1e9:.0f}B parameters")
    print(f"Training: {training_tokens/1e9:.0f}B tokens\n")
    
    print(f"{'Config':<25} {'Time':<15} {'Cost':<15} {'Carbon':<15}")
    print("-" * 70)
    
    for config in configs:
        estimate = estimate_training_cost(
            model_params=model_params,
            training_tokens=training_tokens,
            **config,
        )
        
        config_name = f"{config['num_gpus']}x {config['gpu_type']}"
        print(f"{config_name:<25} "
              f"{estimate['training_days']:.1f} days{'':<7} "
              f"${estimate['cost_usd']:,.0f}{'':<7} "
              f"{estimate['carbon_kg']:,.0f} kg CO2")


if __name__ == "__main__":
    example_training_estimation()
    example_compare_configurations()
    example_energy_auditing()
