# Ignore All Previous Instructions? Investigating System, User, and Assistant Messages for Robust and Reliable LLM Agents

This is the official code used to run the experiments in the paper.

## Paper Info

### Authors

Rei Meguro, Zharizhal Ali, Swathi Selvam, Swathi Murali

### Abstract

>Large Language Models (LLMs) are typically prompted through structured conversations where messages carry explicit roles, such as system, user, or assistant. While prior research has highlighted the importance of system prompts for steering model behavior, little work has systematically examined how different role configurations affect model reliability across key dimensions such as robustness, prompt adherence, long-context memory, and tool-use accuracy. In this paper, we conduct a controlled evaluation of prompting strategies that vary the distribution of instructions across roles. For example, we compare the effectiveness of encoding a task specification in a single system prompt versus distributing it across system and user messages, or reinforcing it with assistant demonstrations. We also test adversarial scenarios in which user prompts attempt to override higher-priority instructions. Finally, we assess prompting strategies in agentic environments, exploring whether retaining past outputs as assistant messages or consolidating them into system instructions leads to more stable performance. Our findings provide actionable insights for designing robust multi-role prompts in real-world applications.

### [Paper Link](#abstract)
