"""
pipeline.py — The core agentic system.

ARCHITECTURE:
  Three agents wired together using LangGraph.
  State is a typed dict that flows from node to node — each agent reads
  what it needs and writes its output back into the same state object.

  [Data Agent] → [Analysis Agent] → [CTA Agent]

LANGGRAPH CONCEPTS:
  - StateGraph: the graph that holds all nodes (agents)
  - Node: a Python function that takes state, does work, returns updated state
  - Edge: a directed connection between nodes
  - State: a shared TypedDict that all nodes read from and write to
"""

import json
from typing import TypedDict, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from mock_data import get_pixel_events


# ============================================================
# STATE — the "memory" that flows between agents
# ============================================================
# Think of this as the shared clipboard for the pipeline.
# Each agent adds its results here for the next agent to read.

class PipelineState(TypedDict):
    raw_events: List[dict]       # set by Data Agent
    segments:   List[dict]       # set by Analysis Agent
    messages:   List[dict]       # set by CTA Agent


# ============================================================
# LLM — shared model, all agents use this
# ============================================================

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


# ============================================================
# AGENT 1 — Data Agent
# Role: fetch & normalize raw pixel events
# In a real system: would call an API, query a DB, etc.
# ============================================================

def data_agent(state: PipelineState) -> PipelineState:
    print("\n🔍 [Data Agent] Fetching pixel events...")

    events, _customers = get_pixel_events()

    # Group events by customer for a cleaner summary
    by_customer = {}
    for e in events:
        cid = e["customer_id"]
        by_customer.setdefault(cid, []).append(e)

    print(f"   → {len(events)} events across {len(by_customer)} customers")

    return {**state, "raw_events": events}


# ============================================================
# AGENT 2 — Analysis Agent
# Role: interpret behavior, segment each customer
# This is where the LLM earns its keep — it reads raw events
# and makes a judgment about intent that would be hard to
# encode as rules.
# ============================================================

def analysis_agent(state: PipelineState) -> PipelineState:
    print("\n🧠 [Analysis Agent] Analyzing customer behavior...")

    events_json = json.dumps(state["raw_events"], indent=2)

    response = llm.invoke([
        SystemMessage(content="""You are a marketing analyst specializing in behavioral segmentation.

Given raw pixel events from a landing page, analyze each customer's behavior
and assign them to one of three segments:

  HIGH_INTENT   — Multiple visits OR CTA click OR scroll >70% AND time >120s
  MEDIUM_INTENT — Single visit, moderate engagement (30–70% scroll, 30–120s), viewed pricing
  LOW_INTENT    — Bounced quickly (<25% scroll OR <20s on page, no meaningful action)

For each unique customer_id, return a JSON array entry:
{
  "customer_id":  "...",
  "name":         "...",
  "phone":        "...",
  "segment":      "HIGH_INTENT | MEDIUM_INTENT | LOW_INTENT",
  "signals":      ["key behavioral signals that drove this classification"],
  "reasoning":    "one sentence explaining your call"
}

Return ONLY a valid JSON array. No markdown, no extra text."""),
        HumanMessage(content=f"Pixel events:\n{events_json}")
    ])

    try:
        segments = json.loads(response.content)
    except json.JSONDecodeError:
        # Graceful fallback if model adds markdown fences
        raw = response.content.strip().removeprefix("```json").removesuffix("```").strip()
        segments = json.loads(raw)

    for s in segments:
        print(f"   → {s['name']}: {s['segment']}  |  {s['reasoning']}")

    return {**state, "segments": segments}


# ============================================================
# AGENT 3 — CTA Agent
# Role: generate a personalized WhatsApp message per customer
# Different segments get fundamentally different tones.
# ============================================================

def cta_agent(state: PipelineState) -> PipelineState:
    print("\n✍️  [CTA Agent] Crafting WhatsApp messages...")

    segments_json = json.dumps(state["segments"], indent=2)

    response = llm.invoke([
        SystemMessage(content="""You are a conversion copywriter. 
Write a personalized WhatsApp message for each customer based on their behavioral segment.

Tone guidelines by segment:
  HIGH_INTENT   — Direct, urgency, concrete offer. Max 2 short sentences. They're ready.
  MEDIUM_INTENT — Lead with value, soft CTA, build curiosity. They need a nudge.
  LOW_INTENT    — Re-engage with a question or a free resource. Zero hard sell. Plant a seed.

Rules:
  - Use the customer's first name
  - Keep it under 160 characters
  - Sound human, not like a newsletter
  - No emoji overload (max 1)

Return a JSON array:
[{
  "customer_id": "...",
  "name":        "...",
  "phone":       "...",
  "segment":     "...",
  "message":     "..."
}]

Return ONLY valid JSON. No extra text."""),
        HumanMessage(content=f"Customer segments:\n{segments_json}")
    ])

    try:
        messages = json.loads(response.content)
    except json.JSONDecodeError:
        raw = response.content.strip().removeprefix("```json").removesuffix("```").strip()
        messages = json.loads(raw)

    return {**state, "messages": messages}


# ============================================================
# GRAPH — wire the agents into a pipeline
# ============================================================

def build_pipeline():
    """
    Creates and compiles the LangGraph pipeline.

    Graph structure:
      data_agent → analysis_agent → cta_agent → END

    This is a simple linear pipeline. LangGraph also supports:
      - Conditional edges (route based on output)
      - Parallel branches (fan-out / fan-in)
      - Cycles (retry loops, human-in-the-loop)
    """
    graph = StateGraph(PipelineState)

    # Add nodes (agents)
    graph.add_node("data_agent",     data_agent)
    graph.add_node("analysis_agent", analysis_agent)
    graph.add_node("cta_agent",      cta_agent)

    # Wire them in sequence
    graph.set_entry_point("data_agent")
    graph.add_edge("data_agent",     "analysis_agent")
    graph.add_edge("analysis_agent", "cta_agent")
    graph.add_edge("cta_agent",      END)

    return graph.compile()
