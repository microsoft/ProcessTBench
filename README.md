# Improving Plan Generation in Large Language Models with Process Mining
Large Language Models (LLMs) have shown significant promise in plan generation. Yet, existing datasets often lack the complexity needed for advanced tool use scenarios — such as handling paraphrased query statements, supporting multiple languages, and managing actions that can be done in parallel. These scenarios are crucial for evaluating the evolving capabilities of LLMs in real-world applications. Moreover, current datasets don’t enable the study of LLMs from a process perspective, particularly in scenarios where understanding typical behaviors and challenges in executing the same process under different conditions or formulations is crucial. To address these gaps, we present the ProcessTBench dataset, i.e., a synthetic dataset as an extension of the TaskBench dataset specifically designed to evaluate LLMs within a process mining framework
```
## generated_plans_and_variants
This section contains different plans that can be used to provide the bjectives of the problems in process ids. Generated using generate_plans_and_variants.py

## paraphrased_queries 
we paraphrase the problems given in the TaskBench Dataset (https://github.com/microsoft/JARVIS/tree/main/taskbench)
Generated using paraphrase_queries.py

## process_models
We discovered process models of the generated plans. We used inductive miner with three different thresholds, i.e., 0, 0.1, and 0.2 for this purpose. We also converted reference DAGs of problems into Petri nets. Examples of how to generate more in dag_to_petri_net_results.py

## conformance_quality
Contains the results of checking the quality of the paraphrased queries via conformance checking. Generated plans using generate_plans_conformance_quality_rephrased.py and generate_plans_conformance_quality_original.py

# TaskBench data that is used in this dataset
├── taskbench_multimedia.json
├── taskbench_multimedia_dag.json
├── taskbench_multimedia_dag_partitioned.json # partitioned for multiprocessing
├── tool_desc_multimedia.json

├── utils.py
├── my_model.py # embedding and LLM model settings
├── readme.md
└── requirements.txt

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
