# 🕊️ Paloma Session Canvas  
### Real-Time AI Session Intelligence for Coaching Workflows

Paloma Session Canvas is a human-in-the-loop AI system that structures live coaching conversations into actionable insights.

It captures dialogue in real time, classifies conversational orientation, detects solution-building signals, and extracts high-integrity client language without interrupting session flow.

The goal: reduce cognitive load while preserving coach presence, judgment, and control.

---

## Core Capabilities (V1)

- **Real-Time Orientation Tagging**  
  Classifies each utterance and provides lightweight confidence scoring with human override.

- **Solution Signal Detection**  
  Identifies emerging “miracle” and “exception” patterns as they occur.

- **Verbatim Phrase Extraction**  
  Extracts meaningful client language into a structured, traceable phrase bank.

Everything else is intentionally excluded in V1.

---

## System Design Principles

- Human-in-the-loop is non-negotiable  
- AI suggests; the coach decides  
- Structured memory over raw transcript dependence  
- Ambient awareness, not dashboard overload  

If the coach must read more than five words, it’s too much.

---

## Architecture Overview

- **Frontend:** React / Next.js  
- **Backend:** Python (FastAPI)  
- **AI Layer:** LLM classification + extraction pipelines  
- **Storage:** Structured session objects + encrypted transcript layer  

Session data is stored as structured utterances, ranked phrases, and orientation summaries to create a high-integrity dataset for future agentic evolution.

---

## Strategic Intent

Session Canvas is the first architectural layer in the broader Paloma ecosystem, building validated conversational structure for AI-assisted coaching intelligence.
