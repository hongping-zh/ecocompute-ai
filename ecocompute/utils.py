"""
Utility functions for EcoCompute AI.
"""

from typing import Dict, Optional

# Regional carbon intensity data (gCO2/kWh)
REGION_CARBON_INTENSITY = {
    "us-east": 400,
    "us-west": 250,
    "eu-west": 300,
    "eu-north": 50,
    "asia-east": 550,
    "asia-south": 700,
    "default": 400,
}

# GPU specifications (TDP in Watts, TFLOPS FP16)
GPU_SPECS = {
    "RTX-5090": {"tdp": 575, "tflops_fp16": 419, "memory_gb": 32},
    "RTX-4090": {"tdp": 450, "tflops_fp16": 330, "memory_gb": 24},
    "A100-80GB": {"tdp": 400, "tflops_fp16": 312, "memory_gb": 80},
    "A100-40GB": {"tdp": 400, "tflops_fp16": 312, "memory_gb": 40},
    "H100-80GB": {"tdp": 700, "tflops_fp16": 990, "memory_gb": 80},
    "L4": {"tdp": 72, "tflops_fp16": 121, "memory_gb": 24},
    "T4": {"tdp": 70, "tflops_fp16": 65, "memory_gb": 16},
}

# Cloud pricing ($/hour per GPU)
CLOUD_PRICING = {
    "A100-80GB": 2.50,
    "A100-40GB": 2.00,
    "H100-80GB": 4.00,
    "RTX-4090": 0.80,
    "L4": 0.50,
    "T4": 0.35,
}


def calculate_carbon_footprint(
    energy_joules: float,
    region: str = "default",
    custom_intensity: Optional[float] = None,
) -> Dict[str, float]:
    """
    Calculate carbon footprint from energy consumption.
    
    Args:
        energy_joules: Energy consumption in Joules
        region: Cloud region for carbon intensity lookup
        custom_intensity: Custom carbon intensity (gCO2/kWh), overrides region
        
    Returns:
        Dictionary with carbon metrics
    """
    # Get carbon intensity
    if custom_intensity is not None:
        intensity = custom_intensity
    else:
        intensity = REGION_CARBON_INTENSITY.get(region, REGION_CARBON_INTENSITY["default"])
    
    # Convert Joules to kWh
    energy_kwh = energy_joules / 3600000
    
    # Calculate carbon
    carbon_g = energy_kwh * intensity
    carbon_kg = carbon_g / 1000
    
    # Equivalent metrics
    km_driven = carbon_kg / 0.154  # Average car: 154g CO2/km
    
    return {
        "energy_j": energy_joules,
        "energy_kwh": energy_kwh,
        "carbon_g": carbon_g,
        "carbon_kg": carbon_kg,
        "carbon_intensity_gco2_kwh": intensity,
        "equivalent_km_driven": km_driven,
    }


def estimate_training_cost(
    model_params: float,
    training_tokens: float,
    gpu_type: str = "A100-80GB",
    num_gpus: int = 8,
    cloud_region: str = "us-east",
    utilization: float = 0.5,
) -> Dict[str, float]:
    """
    Estimate training cost, time, and carbon footprint.
    
    Uses Chinchilla scaling law: FLOPs ≈ 6 * N * D
    
    Args:
        model_params: Number of model parameters (e.g., 1.3e9 for 1.3B)
        training_tokens: Number of training tokens (e.g., 100e9 for 100B)
        gpu_type: GPU type (e.g., "A100-80GB")
        num_gpus: Number of GPUs
        cloud_region: Cloud region for carbon intensity
        utilization: GPU utilization factor (0-1)
        
    Returns:
        Dictionary with cost, time, and carbon estimates
    """
    # Get GPU specs
    gpu = GPU_SPECS.get(gpu_type, GPU_SPECS["A100-80GB"])
    price = CLOUD_PRICING.get(gpu_type, 2.50)
    
    # Calculate FLOPs (Chinchilla: 6 * N * D)
    total_flops = 6 * model_params * training_tokens
    
    # Calculate time
    effective_tflops = gpu["tflops_fp16"] * 1e12 * utilization
    training_seconds = total_flops / (effective_tflops * num_gpus)
    training_hours = training_seconds / 3600
    training_days = training_hours / 24
    
    # Calculate cost
    total_cost = training_hours * num_gpus * price
    
    # Calculate energy and carbon
    energy_joules = gpu["tdp"] * num_gpus * training_seconds
    carbon = calculate_carbon_footprint(energy_joules, cloud_region)
    
    return {
        "model_params": model_params,
        "training_tokens": training_tokens,
        "gpu_type": gpu_type,
        "num_gpus": num_gpus,
        "total_flops": total_flops,
        "training_hours": training_hours,
        "training_days": training_days,
        "cost_usd": total_cost,
        "energy_kwh": carbon["energy_kwh"],
        "carbon_kg": carbon["carbon_kg"],
        "equivalent_km_driven": carbon["equivalent_km_driven"],
    }


def format_training_estimate(estimate: Dict[str, float]) -> str:
    """
    Format training estimate as a readable string.
    
    Args:
        estimate: Dictionary from estimate_training_cost()
        
    Returns:
        Formatted string
    """
    return f"""
Training Estimate for {estimate['model_params']/1e9:.1f}B model
{'='*50}
Hardware: {estimate['num_gpus']}x {estimate['gpu_type']}
Training Tokens: {estimate['training_tokens']/1e9:.0f}B

Time:   {estimate['training_days']:.1f} days ({estimate['training_hours']:.0f} hours)
Cost:   ${estimate['cost_usd']:,.0f}
Energy: {estimate['energy_kwh']:,.0f} kWh
Carbon: {estimate['carbon_kg']:,.0f} kg CO2e (≈ {estimate['equivalent_km_driven']:,.0f} km driven)
"""
