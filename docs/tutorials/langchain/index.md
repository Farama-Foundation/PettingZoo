---
title: "LangChain"
---

# LangChain Tutorial

This tutorial provides an example of using [LangChain](https://github.com/hwchase17/langchain) create LLM agents that can interact with PettingZoo environments:

* [LangChain: Creating LLM Agents](/tutorials/langchain/langchain.md): _Create LLM Agents using LangChain_


## LangChain Overview

[LangChain](https://github.com/hwchase17/langchain) is a framework for developing applications powered by language models through composability.

There are six main areas that LangChain is designed to help with. These are, in increasing order of complexity:

### 📃 LLMs and Prompts:

This includes prompt management, prompt optimization, a generic interface for all LLMs, and common utilities for working with LLMs.

### 🔗 Chains:

Chains go beyond a single LLM call and involve sequences of calls (whether to an LLM or a different utility). LangChain provides a standard interface for chains, lots of integrations with other tools, and end-to-end chains for common applications.

### 📚 Data Augmented Generation:

Data Augmented Generation involves specific types of chains that first interact with an external data source to fetch data for use in the generation step. Examples include summarization of long pieces of text and question/answering over specific data sources.

### 🤖 Agents:

Agents involve an LLM making decisions about which Actions to take, taking that Action, seeing an Observation, and repeating that until done. LangChain provides a standard interface for agents, a selection of agents to choose from, and examples of end-to-end agents.

### 🧠 Memory:

Memory refers to persisting state between calls of a chain/agent. LangChain provides a standard interface for memory, a collection of memory implementations, and examples of chains/agents that use memory.

### 🧐 Evaluation:

[BETA] Generative models are notoriously hard to evaluate with traditional metrics. One new way of evaluating them is using language models themselves to do the evaluation. LangChain provides some prompts/chains for assisting in this.


```{toctree}
:hidden:
:caption: LangChain

langchain
```
