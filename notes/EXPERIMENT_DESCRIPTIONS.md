# Experiment Descriptions

## Experiment 2: Adversarial Robustness

**Task:** Adversarial GLUE, which encompasses sentiment analysis, duplicate detection, and entailment analysis. The inputs for this task are modified at various levels: character, word, sentence, or semantic.

**Input:** The experiment uses either 1 or 2 input sentences, with the exact number depending on the specific task being performed.

**Goal:** The primary objective of this experiment is to investigate whether a clear separation between the task definition and the data used can enhance a model's robustness against adversarial attacks.

---

## Experiment 3: Sequential Tool Calling

**Task:** Tool selection, where the model must identify the next tool to call given a user query, tool definition, and prior tool call history.

**Input:** The experiment uses a user query and tool schema definition that includes the expected next tool name and a list of prior tool calls already executed.

**Goal:** The primary objective of this experiment is to investigate whether models can accurately track tool-calling state and correctly determine the next tool when prior calls are presented as assistant message history.

---

## Experiment 4: Multi-Turn Instruction Adherence

**Task:** Parameter extraction, where the model must extract API parameters from a user query in a conversation that includes a previous assistant response with generic seed values.

**Input:** The experiment uses a user query and tool schema definition. Multi-turn variants include an initial dummy query, an assistant response with seed values, and then the actual query requiring real extraction.

**Goal:** The primary objective of this experiment is to investigate whether models can ignore previous assistant responses and follow new instructions, or if they copy seed values from earlier turns.
