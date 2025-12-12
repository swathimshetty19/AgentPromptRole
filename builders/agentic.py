"""
Builder functions for Experiment 3: Agentic Decision-Making with Long Context

Tests different ways of encoding history/previous outputs:
1. assistant_history: Retain past outputs as assistant messages (conversation history)
2. system_summary: Consolidate past outputs into system prompt as summary
3. mixed: Some history in system, some as assistant messages
4. user_only_history: All history in user messages
"""

def assistant_history(task_description, history, current_query):
    """
    Variant: Retain past outputs as assistant messages (conversation history)
    This simulates a natural conversation where each tool call/output is an assistant message.
    """
    messages = []
    
    # Initial system prompt with task description
    messages.append({
        "role": "system",
        "content": task_description
    })
    
    # Build conversation history: user query -> assistant output pairs
    for i, step in enumerate(history):
        if "user_query" in step:
            messages.append({
                "role": "user",
                "content": step["user_query"]
            })
        if "assistant_output" in step:
            messages.append({
                "role": "assistant",
                "content": step["assistant_output"]
            })
    
    # Current query
    messages.append({
        "role": "user",
        "content": current_query
    })
    
    return messages


def system_summary(task_description, history, current_query):
    """
    Variant: Consolidate past outputs into system prompt as summary
    This tests if summarizing history in system prompt is more effective.
    """
    # Summarize history into a concise format
    history_summary = "Previous interactions:\n"
    for i, step in enumerate(history, 1):
        if "user_query" in step and "assistant_output" in step:
            history_summary += f"{i}. Q: {step['user_query'][:100]}... A: {step['assistant_output'][:100]}...\n"
        elif "assistant_output" in step:
            history_summary += f"{i}. {step['assistant_output'][:150]}...\n"
    
    messages = [
        {
            "role": "system",
            "content": f"{task_description}\n\n{history_summary}"
        },
        {
            "role": "user",
            "content": current_query
        }
    ]
    
    return messages


def mixed(task_description, history, current_query):
    """
    Variant: Hybrid approach - recent history as assistant messages, older as system summary
    This tests if a combination is optimal.
    """
    messages = []
    
    # Split history: older half in system, recent half as assistant messages
    split_point = len(history) // 2
    older_history = history[:split_point]
    recent_history = history[split_point:]
    
    # Summarize older history
    if older_history:
        older_summary = "Earlier interactions:\n"
        for i, step in enumerate(older_history, 1):
            if "assistant_output" in step:
                older_summary += f"{i}. {step['assistant_output'][:100]}...\n"
        
        messages.append({
            "role": "system",
            "content": f"{task_description}\n\n{older_summary}"
        })
    else:
        messages.append({
            "role": "system",
            "content": task_description
        })
    
    # Recent history as assistant messages
    for step in recent_history:
        if "user_query" in step:
            messages.append({
                "role": "user",
                "content": step["user_query"]
            })
        if "assistant_output" in step:
            messages.append({
                "role": "assistant",
                "content": step["assistant_output"]
            })
    
    # Current query
    messages.append({
        "role": "user",
        "content": current_query
    })
    
    return messages


def user_only_history(task_description, history, current_query):
    """
    Variant: All history in user messages (no assistant messages)
    This tests if user-only encoding is sufficient.
    """
    # Build history as a single user message
    history_text = "Previous context:\n"
    for i, step in enumerate(history, 1):
        if "user_query" in step and "assistant_output" in step:
            history_text += f"Step {i}: {step['user_query']} → {step['assistant_output']}\n"
        elif "assistant_output" in step:
            history_text += f"Step {i}: {step['assistant_output']}\n"
    
    messages = [
        {
            "role": "user",
            "content": f"{task_description}\n\n{history_text}\n\nCurrent task: {current_query}"
        }
    ]
    
    return messages


VARIANTS = {
    "assistant_history": assistant_history,
    "system_summary": system_summary,
    "mixed": mixed,
    "user_only_history": user_only_history,
}

