# Improving Plan Generation in Large Language Models with Process Mining

```
## Different Plans For Problems
This section contains different plans that can be used to provide the bjectives of the problems in process ids. x1_planner.py is used for this purpose. 

## Diffrent Problems 
we rephrase the problems given in TaskBench Dataset (https://github.com/microsoft/JARVIS/tree/main/taskbench)
x2_rephrasing is used for this purpose. 

## Models
We discovered process models of the generated plans. We used inductive miner with three different thresholds, i.e., 0, 0.1, and 0.2 for this purpose. We also converted reference DAGs of problems into Petri nets. 

## Conformance Quality
We provided conformance checking quality of generated plans for rephrased problems. 

# TaskBench data that is used in this dataset
├── taskbench_multimedia.json
├── taskbench_multimedia_dag.json
├── taskbench_multimedia_dag_partitioned.json # partitioned for multiprocessing
├── tool_desc_multimedia.json

├── utils.py
├── my_model.py
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
