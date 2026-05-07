# Popo-Job-Agent 🤖

A multi-agent AI system for job application research. Given a job title and company name, it autonomously researches the role, drafts a tailored cover letter, analyses skills gaps, and generates likely interview questions.

Built with LangGraph · GPT-4o · Tavily Search · LangSmith monitoring · Streamlit

---

## Architecture

```
User input (job title + company + profile)
        ↓
  Orchestrator (LangGraph StateGraph)
        ↓
  ┌─────────────────────────────────┐
  │  Researcher Agent               │
  │  · Web search (Tavily)          │
  │  · JD scraper (BeautifulSoup)   │
  │  · Company background search    │
  └─────────────────────────────────┘
        ↓
  ┌─────────────────────────────────┐
  │  Writer Agent                   │
  │  · Cover letter (GPT-4o)        │
  │  · Skills gap analysis          │
  │  · Interview questions          │
  └─────────────────────────────────┘
        ↓
  ┌─────────────────────────────────┐
  │  Responsible AI Layer           │
  │  · Confidence scoring           │
  │  · Hallucination flags          │
  │  · Source citation check        │
  └─────────────────────────────────┘
        ↓
  Output package (Streamlit UI)
```

## Skills demonstrated

- **Agentic AI workflows** — LangGraph ReAct pattern with stateful multi-step planning
- **Multi-agent systems** — Researcher + Writer sub-agents with shared state
- **Responsible AI** — Confidence scoring, hallucination flagging, source citations
- **Model monitoring** — LangSmith tracing for latency, errors, and output quality
- **Tool use** — Tavily search API, web scraping as agent tools
- **MLOps** — Docker, GitHub Actions CI/CD

## Setup

```bash
git clone https://github.com/popolome/Popo-Job-Agent
cd Popo-Job-Agent

cp .env.example .env
# Edit .env with your API keys

pip install -r requirements.txt
```

### API keys needed
| Key | Where to get |
|-----|-------------|
| `OPENAI_API_KEY` | platform.openai.com |
| `TAVILY_API_KEY` | app.tavily.com (free tier available) |
| `LANGCHAIN_API_KEY` | smith.langchain.com (free tier available) |

## Run

```bash
# Streamlit UI
streamlit run ui/app.py

# CLI test
python graph.py

# Docker
docker build -t popo-job-agent .
docker run -p 8501:8501 --env-file .env popo-job-agent
```

## Project structure

```
Popo-Job-Agent/
├── graph.py                  # Main LangGraph orchestrator
├── agents/
│   ├── researcher.py         # Researcher agent node
│   ├── writer.py             # Writer agent node
│   └── responsible_ai.py     # Responsible AI layer node
├── tools/
│   └── researcher_tools.py   # Tavily search + JD scraper tools
├── utils/
│   └── state.py              # Shared JobAgentState schema
├── ui/
│   └── app.py                # Streamlit frontend
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Author

Jun Kit Mak · [github.com/popolome](https://github.com/popolome) · [LinkedIn](https://www.linkedin.com/in/jun-kit-mak-611b4b108/)
