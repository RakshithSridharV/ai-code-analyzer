"""
Real Dataset Fetcher & Feature Extractor

This script downloads real human-written code snippets from the Google 
MBPP (Mostly Basic Python Problems) dataset to build a realistic ML model.
It runs the code through our AST-based feature extractor to generate
the training features (loop_depth, uses_extra_memory, etc.).

We pull the raw JSONL directly to bypass any versioning issues with 
third-party dataset libraries.
"""

import os
import csv
import json
import logging
import requests
import signal

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analyzer.language_detector import detect_language
from backend.analyzer.parser import parse_code
from backend.analyzer.time_complexity import estimate_time_complexity
from backend.analyzer.space_complexity import estimate_space_complexity
from backend.analyzer.recursion_detector import detect_recursion
from backend.analyzer.pattern_detector import detect_patterns
from backend.analyzer.feature_extractor import extract_features

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tests(code, test_list):
    """
    Evaluates the code against the provided test list.
    Returns 0 if all tests pass (Good Code/Efficient), 1 if they fail or timeout (Bad Code/Inefficient).
    
    WARNING: This executes arbitrary code with exec(). It should only be run in a trusted environment 
    or sandboxed. The data source (Google MBPP) is generally safe, but tampered URLs pose a security risk.
    """
    exec_globals = {}
    
    def handler(signum, frame):
        raise TimeoutError("Execution timed out")
        
    try:
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(2)
            
        # Define the function
        exec(code, exec_globals)
        # Run tests
        for test in test_list:
            if isinstance(test, str):
                exec(test, exec_globals)
                
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
            
        return 0  # 0 indicates passing (Good Code)
    except Exception:
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        return 1  # 1 indicates failure (Bad/Inefficient Code)


def fetch_and_extract_features(output_file=None):
    if output_file is None:
        output_file = os.path.join(os.path.dirname(__file__), "code_quality_dataset.csv")

    logger.info("Downloading MBPP Python code snippets...")
    
    url = "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl"
    
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        lines = res.text.strip().split('\n')
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return
        
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["loop_depth", "is_recursive", "uses_extra_memory", "time_penalty", "space_penalty", "label"])
        
        valid_samples = 0
        
        for line in lines:
            if not line:
                continue
            
            try:
                row_obj = json.loads(line)
                code = row_obj.get("code", "")
                test_list = row_obj.get("test_list", [])
                
                if not code or len(code) > 2000:
                    continue
                    
                lang = detect_language(code)
                if lang != "python":
                    continue
                    
                # 1. Parse AST
                tree = parse_code(code)
                if isinstance(tree, str):
                    continue
                    
                # 2. Extract specific base features
                is_recursive = detect_recursion(tree)
                time_c = "O(2^n)" if is_recursive else estimate_time_complexity(tree)
                space_c = estimate_space_complexity(code, is_recursive)
                
                # 3. Detect Patterns
                patterns = detect_patterns(time_c, space_c, is_recursive)
                
                # 4. Extract ML Features
                features = extract_features(time_c, space_c, patterns)
                
                # 5. Bootstrap Label
                time_penalty = features[3]
                space_penalty = features[4]
                
                # Realistic penalty formulation - if the code has poor time/space complexity
                # We use test pass/fail as an efficiency proxy
                label = check_tests(code, test_list)
                
                writer.writerow([*features, label])
                valid_samples += 1
                
                if valid_samples % 100 == 0:
                    logger.info(f"Processed {valid_samples} real code samples...")
                    
            except Exception as e:
                pass

    logger.info(f"✅ Extracted {valid_samples} real samples to {output_file}")


if __name__ == "__main__":
    fetch_and_extract_features()
