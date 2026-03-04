# <img src="/frontend/logo.svg" alt="Conversation Canvas Logo" width="32" align="left"> Conversation Canvas

## The Structured Conversational Mapping Layer

**Before AI can guide human conversation, conversational state must be made legible.**

Real-time conversational state mapping for live coaching sessions.

Unstructured transcript input → spatially mapped, confidence-gated state.  
No automated coaching decisions.

![AI](https://img.shields.io/badge/AI-Human--in--the--Loop-blue)
![System](https://img.shields.io/badge/System-Workflow%20Intelligence-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-teal)
![Frontend](https://img.shields.io/badge/Frontend-Next.js-teal)

---

## Architectural Layers (V1)

### Extraction
- Phrase extraction  
- Confidence ≥ 0.6  
- Max two phrases per utterance (cross-quadrant only)

### Classification
- DOQ quadrant assignment  
- Confidence ≥ 0.7  
- Below threshold → list-only

### Ranking
- Exact recurrence (normalized match)

### Spatial Mapping
- Quadrant as structural map  
- Recurrence drives radial proximity  
- Inline quadrant override

---

## Design Principles

- Human authority preserved  
- Deterministic over opaque  
- Structured memory over transcript storage  
- Ambient awareness over dashboard noise  

---

## Architecture

- **Frontend:** React / Next.js  
- **Backend:** FastAPI  
- **AI Layer:** Extraction + classification pipelines  
- **Storage:** Structured session objects only  

---

## Strategic Intent

Foundational conversational mapping layer of the Paloma ecosystem.
