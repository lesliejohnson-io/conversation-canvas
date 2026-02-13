# 🕊️ Paloma Session Canvas

**Structured Intelligence for Solution-Focused Coaching**

Paloma Session Canvas is a live-session intelligence layer designed specifically for **solution-focused coaches**.

It captures client utterances in real time, maps them to the **Dialogic Orientation Quadrant (DOQ)**, detects miracle and exception signals, and extracts high-integrity client language for reflective use.

Session Canvas is the first architectural layer of the broader **Paloma ecosystem** — an agentic coaching infrastructure grounded in coach-validated data.

---

## Why This?

Coaches listen deeply, but live sessions create cognitive load:

- Tracking orientation  
- Noticing exceptions  
- Remembering exact client language  
- Spotting miracle openings  
- Holding structure without breaking presence  

Session Canvas reduces cognitive friction without interrupting flow.

---

## 🎯 V1 Scope

Version 1 focuses on three core capabilities:

1. **Real-Time DOQ Tagging**
2. **Miracle & Exception Detection**
3. **Verbatim Phrase Extraction**

Everything else is intentionally excluded.

---

## Core Capabilities

### 1️⃣ Real-Time DOQ Tagging

Each utterance is:

- Classified into a DOQ quadrant  
- Assigned a confidence score  
- Given a lightweight rationale  
- Editable by the coach (human override)  

**Goal:**  
Provide ambient orientation awareness without distraction.

---

### 2️⃣ Miracle & Exception Detection

The system identifies solution-building openings in real time.

#### Miracle Signals
- Desired future language  
- “If this were different…”  
- “What I want instead…”  

#### Exception Signals
- “There was a time…”  
- “Sometimes it works when…”  
- Breaks in problem continuity  

**Goal:**  
Highlight solution movement ideas as they emerge.

---

### 3️⃣ Verbatim Phrase Extraction

The system extracts and ranks:

- Metaphors  
- Identity statements  
- Desire language  
- Constraint language  
- Strength/resource markers  

#### Extraction Rules

- Verbatim quotes to capture client language.  
- Link phrases to source utterances.  
- Deduplicate intelligently.  
- Allow coach pinning.  
- Never generate new language without traceability.  

**Goal:**  
Build a trusted “Client Language Bank” for reflection and future recall.

---

## Live Session UX Model

Three-pane minimalist interface:

| Utterance Stream | Orientation Pulse | Phrase Bank |
|------------------|------------------|-------------|

### Utterance Stream
- Timestamped entries  
- Subtle DOQ chip  
- Confidence shown on hover  
- Expandable rationale  

### Orientation Pulse
- Ambient DOQ balance indicator  
- Minimal percentages  
- No dashboard overload  

### Phrase Bank
- Top-ranked quotes visible  
- Miracle / Exception tags  
- Coach pinning  
- Source-linked trace  

**Design principle:**

> If the coach must read more than five words, it’s too much.

---

## 🔐 Hybrid Transcript Model

Session data is stored as:

- Encrypted full transcript (optional retention policy)  
- Structured utterance objects (primary memory layer)  
- Coach-confirmed phrases (trusted memory)  
- DOQ orientation summary  

Structured data is prioritized for long-term use.  
Full transcript is secondary and privacy-aware.

---

## 🏗️ System Architecture (V1)

```mermaid
flowchart LR
  A[Utterance Capture] --> B[Preprocessing / Cleaning]
  B --> C[DOQ Classifier]
  B --> D[Miracle & Exception Detector]
  B --> E[Phrase Extractor]
  C --> F[DOQ Tag + Confidence]
  D --> G[Signal Tags]
  E --> H[Ranked Phrase Bank]
  F --> I[Coach Review]
  G --> I
  H --> I
  I --> J[Structured Session Memory]
````

---

## Data Model

### Utterance

```json
{
  "id": "uuid",
  "timestamp": "ISO-8601",
  "raw_text": "string",
  "cleaned_text": "string",
  "doq_quadrant": "string",
  "doq_confidence": "float",
  "signal_tags": ["miracle", "exception"],
  "phrase_ids": ["uuid"]
}
```

### Phrase

```json
{
  "id": "uuid",
  "quote": "string",
  "type": "metaphor | miracle | exception | strength | constraint",
  "source_utterance_ids": ["uuid"],
  "coach_pinned": true
}
```

### Session

```json
{
  "session_id": "uuid",
  "utterances": [],
  "phrases": [],
  "orientation_summary": {},
  "coach_overrides": [],
  "export_object": {}
}
```

---

## Intelligence Components (V1)

### DOQ Classifier

* Lightweight LLM or fine-tuned model
* Confidence scoring
* Short rationale generation
* Human override priority

### Miracle / Exception Detector

* Pattern detection (semantic + keyword hybrid)
* Confidence thresholding
* Non-intrusive tagging

### Phrase Extractor

* Semantic chunking
* Ranking by:

  * Emotional intensity
  * Uniqueness
  * Reusability
  * Deduplication across sessions

---

## Longitudinal Vision (Future)

* Orientation shift tracking across sessions
* Repeated metaphor surfacing
* Scaling anchor tracking
* Exception density analysis
* Memory feed for Paloma between sessions

This becomes the structured substrate for agentic coaching support outside live sessions.

---

## Strategic Intent

Session Canvas creates:

* Coach-validated conversational structure
* High-integrity language memory
* Labeled orientation data
* A defensible dataset for agentic evolution

It is the first layer of coaching intelligence infrastructure.

---

## Tech Stack

### Frontend

* React / Next.js
* Tailwind 
* Realtime streaming support

### Backend

* Python (FastAPI) or Node
* Structured session object storage
* Encrypted transcript layer

### AI Layer

* LLM API (classification + extraction)
* Lightweight prompt templates
* Future fine-tuning dataset preparation

### Storage

* Structured session database (Supabase)
* Encrypted transcript blob store

---

## 🧪 Guiding Principle

Human-in-the-loop is non-negotiable.

AI suggests.
Coach decides.
Memory is built from validated structure.
