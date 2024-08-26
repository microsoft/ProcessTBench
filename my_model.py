# my_model.py contains the code to interact with the OpenAI API via Microsoft Azure

import os
from openai import AzureOpenAI
import time
import dotenv

dotenv.load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2023-07-01-preview"
)
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
    return response.choices[0].message.content

def get_embedding(text):
    response = client.embeddings.create(
      input = text,
      model= "text-embedding-ada-002"
    )
    return response.data[0].embedding


def get_completion_robust(messages, model="gpt-4", temperature=0.0, max_tokens=4000, top_p=1.0, frequency_penalty=0, presence_penalty=0):
    # Boostrap the output to ensure the results is that of the assistant
    retry_attempts = 0
    retry_sec = [1, 2, 4, 8, 16, 32]
    success_api_call = False

    while retry_attempts < 6 and not success_api_call:
      try:
        response = client.chat.completions.create(
            model = model, # "gpt-4", "gpt-4-32k", "chatGPT_GPT35-turbo-0301" "gpt-35-turbo-16k" "text-davinci-003"
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            messages=messages
        )
        success_api_call = True
      except Exception as e:
        sec_to_sleep = retry_sec[retry_attempts]
        print(f" {e} \n Re-trying Open API call in {sec_to_sleep} seconds...")
        time.sleep(sec_to_sleep)
        retry_attempts += 1

    return response.choices[0].message.content