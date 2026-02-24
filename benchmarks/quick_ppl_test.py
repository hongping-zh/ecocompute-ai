#!/usr/bin/env python3
"""
Quick Perplexity Test for INT8 Quantization Accuracy Assessment
================================================================

Measures perplexity (PPL) across FP16, INT8 Default (threshold=6.0),
and INT8 Pure (threshold=0.0) configurations to quantify the
accuracy-energy trade-off in bitsandbytes quantization.

Author: Hongping Zhang
Date: 2026-02-24
Repository: https://github.com/hongping-zh/ecocompute-ai

Usage:
    python quick_ppl_test.py --model 01-ai/Yi-1.5-6B --num-samples 50
    python quick_ppl_test.py --model mistralai/Mistral-7B-Instruct-v0.2 --num-samples 100
"""

import argparse, json, time, torch
from datetime import datetime
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from datasets import load_dataset
import numpy as np

def calculate_perplexity(model, tokenizer, texts, max_length=512):
    device = model.device
    total_loss = 0
    total_tokens = 0

    print(f"Calculating perplexity on {len(texts)} samples...")
    for idx, text in enumerate(texts):
        if idx % 10 == 0:
            print(f"  Progress: {idx}/{len(texts)}")

        encodings = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
        input_ids = encodings.input_ids.to(device)

        if input_ids.size(1) < 10:
            continue

        with torch.no_grad():
            outputs = model(input_ids, labels=input_ids)
            loss = outputs.loss

        num_tokens = input_ids.size(1)
        total_loss += loss.item() * num_tokens
        total_tokens += num_tokens

    avg_loss = total_loss / total_tokens
    ppl = np.exp(avg_loss)
    print(f"  Total tokens: {total_tokens}, Avg loss: {avg_loss:.4f}")
    return ppl

def load_model_with_config(model_name, config_name):
    print(f"\n{'='*60}\nLoading: {model_name} ({config_name})\n{'='*60}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    if config_name == "fp16":
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True
        )
        config_dict = {"precision": "FP16", "llm_int8_threshold": None}
    elif config_name == "int8_default":
        model = AutoModelForCausalLM.from_pretrained(
            model_name, quantization_config=BitsAndBytesConfig(load_in_8bit=True, llm_int8_threshold=6.0),
            device_map="auto", trust_remote_code=True
        )
        config_dict = {"precision": "INT8", "llm_int8_threshold": 6.0}
    elif config_name == "int8_pure":
        model = AutoModelForCausalLM.from_pretrained(
            model_name, quantization_config=BitsAndBytesConfig(load_in_8bit=True, llm_int8_threshold=0.0),
            device_map="auto", trust_remote_code=True
        )
        config_dict = {"precision": "INT8", "llm_int8_threshold": 0.0}

    model.eval()
    print(f"Memory: {torch.cuda.memory_allocated()/1e9:.2f} GB")
    return model, tokenizer, config_dict

def main():
    parser = argparse.ArgumentParser(description="Quick PPL test for INT8 accuracy assessment")
    parser.add_argument("--model", default="01-ai/Yi-1.5-6B")
    parser.add_argument("--num-samples", type=int, default=50)
    parser.add_argument("--configs", nargs="+", default=["fp16", "int8_default", "int8_pure"])
    args = parser.parse_args()

    print("="*60 + f"\nQUICK PERPLEXITY TEST\nModel: {args.model}\nSamples: {args.num_samples}\n" + "="*60)

    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
    texts = [item["text"] for item in dataset if len(item["text"]) > 100][:args.num_samples]
    print(f"Loaded {len(texts)} samples\n")

    results = {"model": args.model, "timestamp": datetime.now().isoformat(), "num_samples": len(texts), "configurations": {}}

    for config_name in args.configs:
        print(f"\n{'#'*60}\nTesting: {config_name}\n{'#'*60}")
        start = time.time()
        model, tokenizer, config_dict = load_model_with_config(args.model, config_name)
        ppl = calculate_perplexity(model, tokenizer, texts)
        elapsed = time.time() - start
        results["configurations"][config_name] = {"config": config_dict, "perplexity": float(ppl), "time_seconds": elapsed}
        print(f"\n{'='*60}\nResults: PPL = {ppl:.4f} (Time: {elapsed:.1f}s)\n{'='*60}")
        del model
        torch.cuda.empty_cache()
        time.sleep(3)

    print(f"\n{'='*60}\nCOMPARATIVE ANALYSIS\n{'='*60}\n")
    fp16_ppl = results["configurations"].get("fp16", {}).get("perplexity")

    for name, data in results["configurations"].items():
        ppl = data["perplexity"]
        if fp16_ppl and name != "fp16":
            delta = ((ppl - fp16_ppl) / fp16_ppl) * 100
            status = "Negligible" if abs(delta) < 1.0 else "Minor" if abs(delta) < 2.0 else "Significant"
            print(f"{name}:\n  PPL: {ppl:.4f}\n  Delta vs FP16: {delta:+.2f}%\n  Status: {status} impact\n")
        else:
            print(f"{name} (baseline):\n  PPL: {ppl:.4f}\n")

    Path("../data").mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_short = args.model.split("/")[-1]
    json_file = f"../data/ppl_{model_short}_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {json_file}\n{'='*60}")

if __name__ == "__main__":
    main()
