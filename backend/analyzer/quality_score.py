def calculate_quality_score(ai_prediction, features=None):
    label = ai_prediction.get("label", "Efficient")
    confidence = ai_prediction.get("confidence", 1.0)
    
    # Start with a perfect heuristic baseline
    base_score = 100
    
    if features and len(features) >= 5:
        # features format: [loop_depth(int), is_recursive(0/1), extra_mem(0/1), time_penalty(1-4), space_penalty(1-2)]
        loop_depth = features[0]
        time_penalty = features[3]
        space_penalty = features[4]
        
        # Apply structured heuristic deductions based strictly on algorithmic complexity
        deductions = 0
        if loop_depth > 1:
            deductions += (loop_depth - 1) * 15
        if time_penalty > 1:
            deductions += (time_penalty - 1) * 15
        if space_penalty > 1:
            deductions += (space_penalty - 1) * 5
            
        base_score -= deductions

    # Apply AI confidence penalty if flagged as inefficient
    if label == "Inefficient":
        # deduct up to 25 points for AI classification
        base_score -= (confidence * 25)
        
    return max(0, min(100, round(float(base_score))))