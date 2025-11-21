def get_signal(prob, sm_score):
    if prob > 0.65 and sm_score >= 2:
        return "BUY"
    elif prob < 0.35 and sm_score <= -1:
        return "SELL"
    else:
        return "WAIT"
