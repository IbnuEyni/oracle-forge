# Oracle Forge — BLOOM Team
**TRP1 FDE Programme · April 2026**

A production-grade natural language data analytics agent evaluated on the
DataAgentBench (DAB) benchmark — 54 queries, 12 datasets, 9 domains.

## Team
| Name | Email | Role |
|------|-------|------|
| Efrata Wolde | ephratawolde990@gmail.com | Signal Corps |
| Abdurahim Miftah | abdugreat3@gmail.com | Signal Corps |
| Ermiyas Bitew | ermiyasbitew239@gmail.com | - |
| Nebiyou Abebe | nebiyouabebe6@gmail.com | Intelligence Officer |
| Amir Ahmedin | shuaibahmedin@gmail.com | Driver |
| Ruth Solomon | ruthsoll87@gmail.com | Intelligence Officer |

## Server
- Host: `bloom.10academy.org`
- Connect: `ssh trp-bloom`
- Shared session: `tmux attach -t oracle-forge`

## Setup
```bash
git clone https://github.com/IbnuEyni/oracle-forge.git
cd oracle-forge
git clone https://github.com/ucbepic/DataAgentBench.git
cd DataAgentBench
python3 -m venv .venv && source .venv/bin/activate
pip install -r ../requirements.txt
cp .env.example .env  # fill in API keys and DB config
```

## Project Structure
```
oracle-forge/
├── agent/          # Oracle Forge agent source
├── kb/             # Knowledge Base (architecture, domain, evaluation, corrections)
├── eval/           # Evaluation harness and score logs
├── probes/         # Adversarial probe library
├── planning/       # AI-DLC Inception documents
├── utils/          # Shared utilities
├── signal/         # Signal Corps engagement log
├── results/        # DAB results JSON and score logs
└── DataAgentBench/ # Benchmark repo (gitignored)
```

## Benchmark Target
- Dataset: DataAgentBench (54 queries, 12 datasets)
- Current best: 54.3% (PromptQL + Gemini-3.1-Pro)
- Our target: Beat 38% pass@1 baseline
