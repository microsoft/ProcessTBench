# Files
The evnet log for generated plans for the problems can be found in plans_eventlog.csv and the other files provide statistics about this event log.

# Plan generation
For plan generation, we used the same prompt for all the problems and we gave the required files for each problem in the prompt. 

# Model used
```python
def get_completion(messages, model="gpt-4", temperature=0.0, max_tokens=4000, top_p=1.0, frequency_penalty=0, presence_penalty=0):
    response = client.chat.completions.create(
        model = model, # "gpt-4" (0613), "gpt-4-32k (0613)", "chatGPT_GPT35-turbo-0301" "gpt-35-turbo-16k" "text-davinci-003"
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messages
    )
    return response.choices[0].message.content```