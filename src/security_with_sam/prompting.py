"""Fit a chat request into the running context without changing saved conversation history."""
from __future__ import annotations

import math
from typing import Callable, Sequence

# Allowance for chat-template wrapper tokens around each message (role markers, newlines).
MESSAGE_OVERHEAD_TOKENS = 8
# Headroom for template tokens not attributable to one message and for estimate error.
SAFETY_TOKENS = 64
# Retrieved passages may use at most this share of the room left after system prompt and question.
PASSAGE_SHARE = 0.6


class PromptTooLong(ValueError):
    pass


def estimate_tokens(text: str) -> int:
    """Conservative fallback (about 3 characters per token) when the engine cannot count tokens."""
    return math.ceil(len(text) / 3)


def passage_block(passages: Sequence[dict[str, object]]) -> str:
    body = "\n\n".join(
        f"SOURCE {index + 1} | {item['filename']} | page {item.get('page_number') or 'not applicable'}\n{item['passage']}"
        for index, item in enumerate(passages)
    )
    return f"UNTRUSTED SOURCE PASSAGES BEGIN\n{body}\nUNTRUSTED SOURCE PASSAGES END"


def build_messages(
    *,
    system_prompt: str,
    history: Sequence[dict[str, str]],
    question: str,
    context_size: int,
    max_output_tokens: int,
    passages: Sequence[dict[str, object]] = (),
    count_tokens: Callable[[str], int] = estimate_tokens,
) -> dict[str, object]:
    """Return messages that fit `context_size`, the passages actually included, and what was omitted.

    The system prompt and the current question are always included unchanged; if they cannot fit,
    PromptTooLong is raised instead of silently truncating the question. Passages stay in the single
    leading system message as untrusted data (some chat templates reject a second system message).
    History is added newest-first as whole messages and starts with a user turn.
    """
    budget = context_size - max_output_tokens - SAFETY_TOKENS

    def cost(text: str) -> int:
        return count_tokens(text) + MESSAGE_OVERHEAD_TOKENS

    fixed = cost(system_prompt) + cost(question)
    if fixed > budget:
        raise PromptTooLong(
            f"This message is too long for the current {context_size:,}-token context. "
            "Shorten it, or choose a larger context length in Settings."
        )
    used: list[dict[str, object]] = []
    passage_room = int((budget - fixed) * PASSAGE_SHARE)
    for item in passages:
        candidate = [*used, item]
        if count_tokens(passage_block(candidate)) <= passage_room:
            used = candidate
        else:
            break
    system_content = system_prompt + ("\n\n" + passage_block(used) if used else "")
    remaining = budget - cost(system_content) - cost(question)
    chosen: list[dict[str, str]] = []
    for message in reversed(history):
        needed = cost(message["content"])
        if needed > remaining:
            break
        chosen.insert(0, {"role": message["role"], "content": message["content"]})
        remaining -= needed
    while chosen and chosen[0]["role"] != "user":
        chosen.pop(0)
    messages = [{"role": "system", "content": system_content}, *chosen, {"role": "user", "content": question}]
    return {
        "messages": messages,
        "passages": used,
        "history_sent": len(chosen),
        "history_omitted": len(history) - len(chosen),
        "prompt_tokens_estimate": budget - remaining,
        "budget_tokens": budget,
    }
