"""
Example: Using EcoCompute with Hugging Face Trainer.
"""

# Note: This example requires transformers and a GPU
# pip install transformers torch pynvml

def example_with_trainer():
    """Example of using EcoComputeCallback with Hugging Face Trainer."""
    
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
    )
    from ecocompute import EcoComputeCallback
    
    # Load model and tokenizer
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Create EcoCompute callback
    eco_callback = EcoComputeCallback(
        gpu_index=0,
        sample_interval_ms=100,
        log_to_wandb=False,  # Set True if using W&B
        carbon_intensity_gco2_kwh=400,  # US East
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        logging_steps=10,
    )
    
    # Create trainer with callback
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=your_dataset,  # Replace with your dataset
        callbacks=[eco_callback],
    )
    
    # Train
    trainer.train()
    
    # Get energy summary
    summary = eco_callback.get_summary()
    print(f"\nTotal Energy: {summary['total_energy_wh']:.2f} Wh")
    print(f"Total Carbon: {summary['total_carbon_g']:.2f} g CO2e")


if __name__ == "__main__":
    print("This example requires a dataset and GPU to run.")
    print("See the code for usage pattern with Hugging Face Trainer.")
