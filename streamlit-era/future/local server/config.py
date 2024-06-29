import httpx

# "do_sample": true # creative / random
# "do_sample": false # deterministic
# "temperature": high # creative
# "temperature": low # precise
# "top_p/top_k" # diversity
# num_beams # deep thinking
# length_penalty: Low # concise output
# no_repeat_ngram_size: Prevents the repetition of n-grams
# early_stopping: Stops the generation early in beam search if all beam hypotheses reached the EOS token.


creative_writing_mode = {
    "do_sample": True,
    "temperature": 1.0,
    "top_p": 0.92,
    "top_k": 60,
    "repetition_penalty": 1.0,
    "num_beams": 2,
    "num_return_sequences": 1,
    "no_repeat_ngram_size": 2,
}


no_bs_chat_mode = {
    "do_sample": False,
    "temperature": 0.5,
    "top_p": 0.9,
    "top_k": 20,
    "repetition_penalty": 1.2,
    "num_beams": 3,
    "num_return_sequences": 1,
    "no_repeat_ngram_size": 2,
    "length_penalty": 0.8,
}


balanced_chat_mode = {
    "do_sample": True,
    "temperature": 0.7,
    "top_p": 0.85,
    "top_k": 50,
    "repetition_penalty": 1.1,
    "num_beams": 1,
    "num_return_sequences": 1,
    "no_repeat_ngram_size": 2,
}

code_writing_mode = {
    "do_sample": True,
    "temperature": 0.5,
    "top_p": 0.8,
    "top_k": 40,
    "repetition_penalty": 1.2,
    "num_beams": 1,
    "num_return_sequences": 1,
    "no_repeat_ngram_size": 3,
}

deep_thinking_mode = {
    "do_sample": False,
    "temperature": 0.6,
    "top_p": 0.95,
    "top_k": 50,
    "repetition_penalty": 1.1,
    "num_beams": 5,
    "num_return_sequences": 1,
    "no_repeat_ngram_size": 3,
    "early_stopping": True,
}


async def call_model(prompt, max_new_tokens, config):
    url = "http://localhost:8000/"
    config["prompt"] = prompt
    config["max_new_tokens"] = max_new_tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=config, timeout=1000)
    assert response.status_code == 200
    assert "generated_text" in response.json()
    return response.json()["generated_text"]
