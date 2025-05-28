# Solve Issues in Large Code Repositories: Enhancing Software Engineering Solutions with Iterative Reasoning and Graph-Based Retrieval

### A Novel Approach to SWE Bench Optimization

## Introduction

This repository contains the implementation and research artifacts for our final year project titled:
**"Solve Issues in Large Code Repositories"**

The project addresses limitations in current automated debugging and patch generation methods by introducing a hybrid approach that combines:

* **Iterative reasoning**, to mimic real-world developer behavior.
* **Graph-based retrieval**, to reduce the search space and improve precision.
* **Retrieval-Augmented Generation (RAG)** leveraging Stack Overflow for enhanced context.
* **Multi-LLM-based patch generation and refinement**, ensuring higher SWE-bench performance with cost-effective computation.

---

## Objectives

### General Objective

Enhance the efficiency and accuracy of automated software engineering solutions evaluated using the SWE Bench framework.

### Specific Objectives

* Develop an iterative reasoning system for issue resolution.
* Create a graph-based representation of code repositories for accurate file retrieval.
* Integrate Stack Overflow knowledge using RAG to improve contextual understanding.
* Combine multiple LLMs (e.g., [Claude](https://www.anthropic.com/index/introducing-claude), [GPT-4](https://openai.com/gpt-4), [DeepSeek R1](https://arxiv.org/abs/2501.12948)) for diverse patch generation.
* Learn from incorrect patches using iterative refinement and reasoning models.
* Achieve retrieval accuracy >82% on SWE-bench tasks.

---

## Methodology

* **Graph-Based Repository Modeling**
  Built using [NetworkX](https://networkx.org/) and visualized with [Gephi](https://gephi.org/), representing inter-file relationships like imports and function calls.

* **Retrieval-Augmented Generation (RAG)**
  Enhanced contextual understanding using [Stack Overflow](https://stackoverflow.com/) data stored in [ChromaDB](https://www.trychroma.com/), queried semantically via [Sentence-BERT](https://www.sbert.net/), and processed with [LlamaIndex](https://www.llamaindex.ai/).

* **Iterative Reasoning & Multi-LLM Patch Generation**
  Employing reasoning models like [DeepSeek R1](https://arxiv.org/abs/2501.12948) and multiple LLMs to generate, compare, and refine patches.

* **Artificial Stack Trace Generation**
  For difficult cases where standard retrieval fails, simulate execution paths using graph traversal to identify probable buggy files.

---

## Technologies Used

| Technology        | Purpose                                 |
| ----------------- | --------------------------------------- |
| Python            | Primary development language            |
| NetworkX          | Graph construction                      |
| Gephi             | Graph visualization                     |
| ChromaDB          | Vector database for semantic retrieval  |
| OpenAI-embeddings | Embedding generation                    |
| Langchain         | RAG integration and vector search       |
| BeautifulSoup     | Web scraping (Stack Overflow)           |
| StackAPI          | API access to Stack Overflow data       |
| GPT-4, Claude     | LLMs for retrieval and patch generation |
| DeepSeek R1       | Reasoning and decision-making           |

---

## Experiment Setup

* Graph-based repository model construction.
* SWE-bench dataset preprocessing.
* Retrieval techniques benchmarked:

  * LLM-based
  * Embedding-based
  * LLM + RAG
* Artificial stack traces generated when direct retrieval fails.
* Stack Overflow context integration using vector search.
* Evaluation metrics:

  * Retrieval Accuracy (target: >82%)
  * Patch Validity (unit test pass/fail)
  * Cost-efficiency (LLM token usage and execution time)

---

## Results and Analysis *(To be updated after implementation)*

> *Expected Outcomes:*

* Improved retrieval accuracy compared to baseline agentless models.
* More accurate and contextually relevant patch generation.
* Reduced computation cost due to graph-pruned search space.
* Iterative learning model able to refine patches across runs.

---

## References

* [SWE Bench](https://arxiv.org/abs/2310.06770)
* [Agentless](https://arxiv.org/abs/2407.01489)
* [SWE Agent](https://arxiv.org/abs/2405.15793)
* [AutoCodeRover](https://dl.acm.org/doi/10.1145/3597926.3627613)
* [SWE Search](https://arxiv.org/abs/2410.20285)
* [OpenHands](https://arxiv.org/abs/2407.16741)
* [RepoHyper](https://arxiv.org/abs/2403.06095)
* [RepoGraph](https://arxiv.org/abs/2410.14684)
* [StackRAG](https://arxiv.org/abs/2406.13840)
* [DeepSeek R1](https://arxiv.org/abs/2501.12948)
* [Evolving Deeper LLM Thinking](https://arxiv.org/abs/2501.09891)

---

## Contributors

* **Achsuthan T.** – E/19/007 – [achsuthant@eng.pdn.ac.lk](mailto:achsuthant@eng.pdn.ac.lk)
* **Eshan Jayasundara** – E/19/163 – [eshanj@eng.pdn.ac.lk](mailto:eshanj@eng.pdn.ac.lk)
* **Lahiru Menikdiwela** – E/19/236 – [lahirum@eng.pdn.ac.lk](mailto:lahirum@eng.pdn.ac.lk)
* **Supervisors:**

  * Prof. Roshan G. Ragel
  * Dr. Damayanthi Herath

---

## License

This repository is for academic and non-commercial research use only. Licensing options to be determined based on publication and university policy.
