# Files
For each problem, we gnerated several rephrased problems. The rephrased problems for each process can be found in rephrasing_results_flat.csv. To rephrase, we also used French and Danish languages. 
We also added USE and ada embedings of different problems that can be used for assessing their similarity. 
# Model Details

```python
def get_embedding(text):
    response = client.embeddings.create(
      input = text,
      model= "text-embedding-ada-002"
    )
    return response.data[0].embedding
```

# Script used

rephrasing.py