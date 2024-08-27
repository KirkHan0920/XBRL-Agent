# XBRL-Agent
Here is XBRL-Agent's official GitHub repository

## What is XBRL?
![image](./Figures/bby.png)
XBRL (eXtensible Business Reporting Language) is a global standard for digital business reporting, widely adopted by regulators worldwide. It standardizes financial data creation and sharing among investors, regulators, and market participants. XBRL links numerical data to its semantic context, enhancing the interpretability of financial information. The image above shows an example of an XBRL report, taken from Best Buy's SEC-10Q filing.

## What is XBRL-Agent?
XBRL-Agent is a pioneering project that evaluates and enhances large language models' (LLMs) capabilities in analyzing XBRL reports. We address LLMs' limitations in financial domain knowledge and mathematical calculations by integrating external tools like retrievers and calculators within an agent framework. Our experiments demonstrate significant improvements, with accuracy increases of up to 17% for domain queries and 42% for numeric type queries. This work explores LLMs' potential in XBRL analysis and enhances their reliability and robustness through innovative techniques, paving the way for more efficient and accurate processing of business financial reports.

## Datasets
![image](./Figures/datasets.png)
We use four tasks (including three datasets) to evaluate LLMs' ability. Sample questions and answers for four tasks with optional support materials are shown above. Among all the datasets, [XBRL Terminology](https://huggingface.co/datasets/KirkHan/XBRL_Terminology) and [Financial Formula Calculation](https://huggingface.co/datasets/KirkHan/XBRL_Formula_Calculation) are collected by ourselves and open-sourced on Hugging Face for academic research.
