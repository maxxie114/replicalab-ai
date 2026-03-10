# ── 13. Quick interactive demo ────────────────────────────────────────────────
import torch

DEMO_SEED     = 999
DEMO_SCENARIO = "math_reasoning"

reset_data = client.reset(seed=DEMO_SEED, scenario=DEMO_SCENARIO, difficulty="easy")
obs = reset_data["observation"]
print(f"Episode: {reset_data['episode_id']}")
print(f"Paper:   {obs['scientist']['paper_title']}\n")

done = False
total_reward = 0.0

model.eval()
while not done:
    # transformers 5.x requires content as a list of blocks, not a plain string
    messages = [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
        {"role": "user",   "content": [{"type": "text", "text": obs_to_prompt(obs)}]},
    ]

    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        out = model.generate(
            inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    text = tokenizer.decode(out[0][inputs.shape[-1]:], skip_special_tokens=True)
    action = parse_action(text)
    result = client.step(action)

    rnd = obs['scientist']['round_number'] + 1
    r   = result['reward']
    total_reward += r

    print(f"Round {rnd}: action={action['action_type']}  reward={r:.3f}")
    if action.get('rationale'):
        print(f"         rationale: {action['rationale'][:80]}")

    done = result["done"]
    if not done:
        obs = result["observation"]

print(f"\nEpisode done. Total reward: {total_reward:.3f}")
print("Agreement reached:", result.get("info", {}).get("agreement_reached"))
