# Conformance
The plans_original_problems.csv file contains the original event log extracted from the TaskBench dataset. Since we only have one case for all processes, the case ID is consistently set to 1 for all rows. Please note that this log only captures sequential behavior, and we have used a similar prompt that was used for other rephrased problems in the other folder.

In plans_original_problems_conformance.csv, you will find the conformance values for different processes compared to their original DAG models, which have been converted to Petri nets
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