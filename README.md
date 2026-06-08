# Marketing Agent POC

A minimal agentic system that reads landing page pixel events, segments customers by intent, and generates personalized WhatsApp CTAs — built to teach the core patterns of agentic AI.

---

## What it does

```
Pixel Events (mock)
       ↓
  [Data Agent]       → fetches & normalizes raw events
       ↓
[Analysis Agent]     → LLM segments customers by behavior (HIGH / MEDIUM / LOW intent)
       ↓
  [CTA Agent]        → LLM writes a personalized WhatsApp message per segment
       ↓
  Console output     (or swap for real WhatsApp API)
```

---

## Agentic concepts you'll see here

| Concept | Where it appears |
|---|---|
| **State** | `PipelineState` TypedDict in `pipeline.py` — the shared object all agents read from and write to |
| **Nodes (agents)** | `data_agent`, `analysis_agent`, `cta_agent` — each is a plain Python function |
| **Edges** | `graph.add_edge(...)` calls — define the execution order |
| **LLM as a reasoning step** | Analysis Agent doesn't use rules — the LLM interprets signals |
| **Structured output** | Agents ask the LLM to return JSON, then parse it back into Python |
| **Separation of concerns** | Each agent has one job; none knows about the others |

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your OpenAI key
cp .env.example .env
# edit .env and paste your key

# 3. Run
cd src
python main.py
```

---

## Expected output

```
🔍 [Data Agent] Fetching pixel events...
   → 6 events across 3 customers

🧠 [Analysis Agent] Analyzing customer behavior...
   → Sofia Andersen: HIGH_INTENT   | 3 visits + CTA click signals purchase readiness
   → Marcus Veil:    MEDIUM_INTENT | Single visit, viewed pricing, moderate scroll
   → Elena Moro:     LOW_INTENT    | 8-second bounce, minimal scroll

✍️  [CTA Agent] Crafting WhatsApp messages...

=======================================================
  GENERATED WHATSAPP MESSAGES
=======================================================

🔥  Sofia Andersen  (+45 12 34 56 78)
   Segment : HIGH_INTENT
   Message : Sofia, your free trial is one click away — grab it before tonight. 🚀

🌡️  Marcus Veil  (+45 87 65 43 21)
   Segment : MEDIUM_INTENT
   Message : Hey Marcus, you checked out our pricing — want a quick walkthrough of what's included?

❄️  Elena Moro  (+45 11 22 33 44)
   Segment : LOW_INTENT
   Message : Hey Elena, curious what brought you to our page? Happy to share something useful.
```

---

## How to extend this

**Add a real data source** — replace `get_pixel_events()` in `data_agent` with an API call to your analytics platform (Segment, Amplitude, custom DB).

**Add conditional routing** — use `add_conditional_edges` in LangGraph to skip CTA generation for LOW_INTENT customers, or route them to a different nurture flow.

**Add a human-in-the-loop step** — insert an `approval_node` between Analysis and CTA that pauses and waits for a human to confirm segments before messages go out.

**Actually send the messages** — replace the console print in `main.py` with a Twilio or Meta Business API call.

**Add memory** — store segments in a DB and check previous visit history before re-segmenting, so customers don't get the same message twice.

---

## File structure

```
marketing-agent-poc/
├── requirements.txt
├── .env.example
├── README.md
└── src/
    ├── mock_data.py    # simulated pixel events
    ├── pipeline.py     # all three agents + LangGraph graph
    └── main.py         # entry point
```
