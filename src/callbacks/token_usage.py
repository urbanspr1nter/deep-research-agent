def on_step(step, agent):
    if step.token_usage:
        print(f"[MONITOR] Context size: {step.token_usage.input_tokens:,} tokens.")