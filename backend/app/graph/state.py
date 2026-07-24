"""Graph state and the delta-merge reducer.

The single most important design decision in this project lives here.

Tools never return the *whole* form. They return a **delta** — only the fields
they are confident about. `merge_dict` folds that delta into the existing form,
skipping null/empty values. Because the reducer merges rather than replaces,
an edit like "the batch number is BMX24602" can only ever *add/overwrite* the
batch field; every other field is structurally preserved. Preservation is a
property of the data flow, not of a prompt we hope the model obeys.
"""
from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages


def merge_dict(old: dict | None, new: dict | None) -> dict:
    """Reducer: merge `new` into `old`, ignoring null / blank values.

    Skipping blanks means a delta can never accidentally wipe a field by
    sending an empty string for it.
    """
    merged = dict(old or {})
    for key, value in (new or {}).items():
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        if isinstance(value, list) and len(value) == 0:
            continue
        merged[key] = value
    return merged


class ComplaintState(TypedDict, total=False):
    # Conversation history (add_messages appends, giving multi-turn memory).
    messages: Annotated[list, add_messages]

    # Per-invocation inputs.
    source: str                       # "chat" | "document"
    document_text: Optional[str]

    # Router output.
    intent: str                       # log | edit | document | question

    # Persistent, delta-merged state (survives across turns via the checkpointer).
    form: Annotated[dict, merge_dict]
    risk: Annotated[dict, merge_dict]

    # Per-invocation outputs.
    reply: str
    changed_fields: list
    model_used: str
