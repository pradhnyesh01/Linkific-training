"""
state.py
Shared state that flows through the entire multi-agent pipeline.

Every agent receives the full ResearchState, reads what it needs,
writes its output to the appropriate field, and returns the updated state.

Flow:
  topic
    → [Researcher]  → search_results
    → [Analyzer]    → analysis
    → [Critic]      → critique
    → [Writer]      → final_report
"""

from dataclasses import dataclass, field

@dataclass
class ResearchState:
    # Input
    topic: str

    # Agent outputs (populated as pipeline progresses)
    search_results: list[dict] = field(default_factory=list)  # Researcher
    analysis:       str        = ""                            # Analyzer
    critique:       str        = ""                            # Critic
    final_report:   str        = ""                            # Writer

    # Metadata
    status: str       = "pending"   # pending → researching → analyzing → critiquing → writing → done
    log:    list[str] = field(default_factory=list)   # one line per agent run

    def add_log(self, agent_name: str, message: str):
        entry = f"[{agent_name}] {message}"
        self.log.append(entry)
        print(entry)
