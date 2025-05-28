---
layout: home
permalink: index.html

# Please update this with your repository name and title
repository-name: Solve Issues in Large Code Repositoreis
---

[comment]: # "This is the standard layout for the project, but you can clean this and use your own template"

# Project Title

#### Team

- E/19/236,Lahiru Menikdiwela , [email](mailto:e19236@eng.pdn.ac.lk)
- E/19/163, Eshan Jayasundara, [email](mailto:e19163@eng.pdn.ac.lk)
- E/19/007, Achsuthan T., [email](mailto:e19007@eng.pdn.ac.lk)

#### Supervisors

- Prof. Roshan Ragel, [email](mailto:roshanr@eng.pdn.ac.lk)
- Dr. Damayanthi Herath, [email](mailto:damayanthiherath@eng.pdn.ac.lk)

#### Table of content

1. [Abstract](#abstract)
2. [Related works](#related-works)
3. [Methodology](#methodology)
4. [Experiment Setup and Implementation](#experiment-setup-and-implementation)
5. [Results and Analysis](#results-and-analysis)
6. [Conclusion](#conclusion)
7. [Publications](#publications)
8. [Links](#links)

---

<!--
DELETE THIS SAMPLE before publishing to GitHub Pages !!!
This is a sample image, to show how to add images to your page. To learn more options, please refer [this](https://projects.ce.pdn.ac.lk/docs/faq/how-to-add-an-image/)
![Sample Image](./images/sample.png)
-->

## Abstract

The Software Engineering (SWE) Bench is a crucial benchmark for evaluating methods in software engineering problem-solving. Current open-source approaches, such as [agentless solutions](https://arxiv.org/abs/2407.01489), [SWE agents](https://arxiv.org/abs/2405.15793), [AutoCoderOver](https://dl.acm.org/doi/10.1145/3597926.3627613), [SWE Search](https://arxiv.org/abs/2410.20285), and [OpenHands](https://arxiv.org/abs/2407.16741), have limitations in efficiency, cost, and accuracy. This research proposes a novel methodology that balances cost-effectiveness with high SWE Bench scores. Our approach integrates an iterative reasoning process, mimicking the learning process of software engineers, and employs a retrieval-augmented generation (RAG) framework leveraging Stack Overflow datasets. We introduce a graph-based repository representation to reduce the search space and improve retrieval accuracy by establishing structured connections between files. Additionally, we incorporate deep Large Language Model (LLM) thinking strategies, inspired by Google’s [Mind Evolution research](https://arxiv.org/abs/2501.09891), to learn from the wrong patches through iterative recombination and refinement. Our proposed method aims to achieve higher SWE Bench scores while maintaining a cost-effective and practical approach for real-world software development.

## Related works

Several current approaches to SWE Bench optimization have informed this research:

- **Agentless approaches** (e.g., Agentless [_arXiv:2407.01489_](https://arxiv.org/abs/2407.01489)) are simple and cost-efficient but lack iterative reasoning.
- **Agentic approaches** (e.g., [_SWE Agent_](https://arxiv.org/abs/2405.15793), [_AutoCodeRover_](https://dl.acm.org/doi/10.1145/3597926.3627613), [_SWE Search_](https://arxiv.org/abs/2410.20285), [_OpenHands_](https://arxiv.org/abs/2407.16741)) offer dynamic actions through tools but suffer from high cost, tool errors, and complexity.
- **Graph-based retrieval systems** like [_RepoHyper_](https://arxiv.org/abs/2403.06095) and [_RepoGraph_](https://arxiv.org/abs/2410.14684) represent repositories as graphs for semantic search, though often at function-level granularity which increases complexity.
- **Retrieval-Augmented Generation (RAG)** systems (e.g., [_StackRAG_](https://arxiv.org/abs/2406.13840)) leverage external data like Stack Overflow, improving retrieval accuracy. However, relying on keyword-based StackOverflow APIs has limitations. This work instead uses vector databases for semantic search.
- **Recent LLM developments**, including models like Claude, GPT, and [_DeepSeek R1_](https://arxiv.org/abs/2501.12948), introduce advanced reasoning and multi-agent debate to improve patch generation accuracy and decision-making.
- **Deeper LLM Thinking** ([_arXiv:2501.09891_](https://arxiv.org/abs/2501.09891)) emphasizes learning from incorrect outputs, informing this project’s strategy for iterative refinement from failed patches.

## Methodology

The proposed methodology includes the following key steps:

#### 1. **Analysis of the Dataset**

- Analyze relationships between keywords (file names, class names, function names) and golden patches.
- Proceed with retrieval-based implementation if the patch file is within the first-level neighbors 85% of the time.

#### 2. **Graph-Based Repository Representation**

- Construct a graph capturing inter-file relationships (imports, function calls, dependencies).
- Reduces the search space by enabling targeted retrieval based on file connections rather than full-repo searches.

#### 3. **Retrieval-Based Suspicious File Identification**

- Use three retrieval methods:

  - **LLM-Based**: Uses a language model to predict relevant files.
  - **Embedding-Based**: Converts files/descriptions into vectors and computes similarity.
  - **LLM + RAG**: Incorporates Stack Overflow knowledge to refine results.

  <img src='./images/retriver.png'><br/>

- Use DeepSeek R1 as a reasoning model to finalize file selection from multiple retrieval results.

#### 4. **Artificial Stack Trace Generation**

- If patch files aren't consistently found through graph traversal, generate artificial stack traces to guide retrieval.
- Expands the graph level-by-level, feeding context into the LLM to mimic logical execution paths.

#### 5. **RAG with Stack Overflow Data**

- Integrates Stack Overflow knowledge using a semantic search via vector databases.
- Enhances context during retrieval and patch generation, reducing hallucination and improving factuality.

#### 6. **Patch Generation with Multiple LLMs and Iterative Learning**

- Combine multiple LLMs (e.g., [**Claude**](https://www.anthropic.com/index/introducing-claude), [**GPT**](https://openai.com/gpt-4), [**DeepSeek**](https://arxiv.org/abs/2501.12948)) for diverse patch generation.
- Learn from failed patches using iterative refinement and reasoning, improving overall patch quality.

#### Architecture

<img src='./images/architecture.png'><br/>

## Experiment Setup and Implementation

- A **graph-based repository model** is created using technologies like [**NetworkX**](https://networkx.org/) and visualized using [**Gephi**](https://gephi.org/).
- **Vector databases** (e.g., [**ChromaDB**](https://www.trychroma.com/)) and **semantic search tools** (e.g., [**Sentence-BERT**](https://www.sbert.net/)) are used to support embedding-based retrieval.
- **LLMs used**: [**GPT-4**](https://openai.com/gpt-4), [**Claude**](https://www.anthropic.com/index/introducing-claude), [**DeepSeek R1**](https://arxiv.org/abs/2501.12948) for both retrieval and patch generation.
- The decision-making model [**DeepSeek R1**](https://arxiv.org/abs/2501.12948) is used to select the best suspicious file.
- Stack Overflow data is integrated into a RAG framework using [**LlamaIndex**](https://www.llamaindex.ai/), [**BeautifulSoup**](https://www.crummy.com/software/BeautifulSoup/), and [**StackAPI**](https://stackapi.readthedocs.io/en/latest/).
- Evaluation is based on the [**SWE-bench**](https://arxiv.org/abs/2310.06770) framework, focusing on:

  - Retrieval accuracy (targeting >82%)
  - Patch validity
  - Cost-efficiency

- Artificial stack traces are generated if retrieval fails to find correct files initially.

## Results and Analysis

## Conclusion

- Introduces two key innovations:

  1. **Graph-Based Retrieval**: Efficient, accurate retrieval by modeling inter-file relationships in a repository.
  2. **Iterative Learning from Incorrect Patches**: Enhances patch quality by analyzing and refining failed attempts.

- These innovations mimic real-world debugging processes and lead to:

  - Improved patch generation accuracy,
  - Efficient bug localization,
  - Reduced computational costs.

- The proposed approach serves as a **cost-effective, high-performance solution** for automated debugging and patch generation in large codebases evaluated via the SWE Bench framework.

## Publications

[//]: # "Note: Uncomment each once you uploaded the files to the repository"

<!-- 1. [Semester 7 report](./) -->
<!-- 2. [Semester 7 slides](./) -->
<!-- 3. [Semester 8 report](./) -->
<!-- 4. [Semester 8 slides](./) -->
<!-- 5. Author 1, Author 2 and Author 3 "Research paper title" (2021). [PDF](./). -->

## Links

[//]: # " NOTE: EDIT THIS LINKS WITH YOUR REPO DETAILS "

- [Project Repository](https://github.com/cepdnaclk/repository-name)
- [Project Page](https://cepdnaclk.github.io/repository-name)
- [Department of Computer Engineering](http://www.ce.pdn.ac.lk/)
- [University of Peradeniya](https://eng.pdn.ac.lk/)

[//]: # "Please refer this to learn more about Markdown syntax"
[//]: # "https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet"
