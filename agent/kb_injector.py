"""
Oracle Forge — KB Injector (Selective)
Injects only relevant KB context for the current dataset, within a safe size budget.

Priority order (highest to lowest):
  1. Corrections for this specific dataset
  2. Join key glossary (always needed for cross-DB joins)
  3. DAB failure categories (structural — always useful)
  4. Dataset-specific schema description
  5. Unstructured field inventory
  6. Domain term definitions
  7. pass1_scoring (least critical at query time)

Hard budget: 18000 chars (safe margin below the 25KB Claude Code cap,
leaving room for schema hints from --use_hints which add ~3-5KB per dataset).
"""
import re
from pathlib import Path

AGENT_DIR = Path(__file__).parent
KB_DIR = AGENT_DIR.parent / "kb"
KB_CORRECTIONS = KB_DIR / "corrections" / "corrections.md"
KB_DOMAIN_DIR = KB_DIR / "domain"

# Safe injection budget — leaves headroom for --use_hints schema (~3-5KB)
BUDGET = 18_000

# Priority order for domain docs — most critical first
DOMAIN_PRIORITY = [
    "join-key-glossary",
    "dab-failure-categories",
    "dab_schema_descriptions",
    "unstructured-field-inventory",
    "domain_term_definitions",
    "pass1_scoring",
]


def load_corrections_for_dataset(dataset: str) -> str:
    """
    Layer 3: Load only corrections relevant to the current dataset.
    Falls back to all corrections if dataset not specified.
    """
    if not KB_CORRECTIONS.exists():
        return ""
    content = KB_CORRECTIONS.read_text().strip()
    if not content or not dataset:
        return f"\n\n## PAST FAILURES AND FIXES\n{content}" if content else ""

    # Split into individual correction blocks
    blocks = re.split(r'\n(?=---\n\n## Correction)', content)
    header = blocks[0] if not blocks[0].startswith('---') else ""
    correction_blocks = [b for b in blocks if '## Correction' in b]

    # Keep corrections for this dataset + generic corrections (no dataset tag)
    relevant = []
    for block in correction_blocks:
        block_lower = block.lower()
        if f"dataset:** {dataset}" in block_lower or \
           f"dataset: {dataset}" in block_lower or \
           "dataset:**" not in block_lower:
            relevant.append(block)

    if not relevant:
        # No dataset-specific corrections — inject all (they're small)
        relevant = correction_blocks

    combined = header + "\n\n---\n\n".join(relevant)
    return f"\n\n## PAST FAILURES AND FIXES (read before answering)\n{combined}"


def load_domain_selective(budget_remaining: int) -> str:
    """
    Layer 2: Load domain docs in priority order, stopping when budget is exhausted.
    """
    if not KB_DOMAIN_DIR.exists():
        return ""

    # Build lookup of available docs
    available = {
        f.stem: f for f in KB_DOMAIN_DIR.glob("*.md")
        if f.name != "CHANGELOG.md"
    }

    # Load in priority order, skip if over budget
    parts = []
    used = 0
    skipped = []

    for name in DOMAIN_PRIORITY:
        if name not in available:
            continue
        content = available[name].read_text().strip()
        entry = f"### {name}\n{content}"
        if used + len(entry) <= budget_remaining:
            parts.append(entry)
            used += len(entry)
        else:
            skipped.append(f"{name} ({len(entry)} chars)")

    # Any docs not in priority list — add if budget allows
    for stem, path in available.items():
        if stem in DOMAIN_PRIORITY:
            continue
        content = path.read_text().strip()
        entry = f"### {stem}\n{content}"
        if used + len(entry) <= budget_remaining:
            parts.append(entry)
            used += len(entry)
        else:
            skipped.append(f"{stem} ({len(entry)} chars)")

    if skipped:
        print(f"[Oracle Forge] KB budget: skipped {len(skipped)} doc(s): {', '.join(skipped)}")

    if not parts:
        return ""
    return "\n\n## DOMAIN KNOWLEDGE\n" + "\n\n".join(parts)


def build_kb_context(dataset: str = "") -> str:
    """
    Build selective KB context within BUDGET chars.
    Corrections for the current dataset are loaded first (highest priority).
    Domain docs fill remaining budget in priority order.
    """
    # Layer 3 first — corrections are highest priority
    corrections = load_corrections_for_dataset(dataset)
    corrections_size = len(corrections)

    # Remaining budget for Layer 2
    domain_budget = BUDGET - corrections_size
    domain = load_domain_selective(domain_budget)

    total = corrections_size + len(domain)
    print(f"[Oracle Forge] KB injected: {total} chars "
          f"(corrections={corrections_size}, domain={len(domain)}, budget={BUDGET})")

    return domain + corrections


# ── Monkey-patch DataAgent.__init__ ──────────────────────────────────────────
import common_scaffold.DataAgent as _da  # noqa: E402
_original_init = _da.DataAgent.__init__


def _patched_init(self, query_dir, db_description, db_config_path, deployment_name, **kwargs):
    # Extract dataset name from query_dir path (e.g. query_yelp/query1 → yelp)
    dataset = ""
    for part in Path(str(query_dir)).parts:
        if part.startswith("query_"):
            dataset = part.replace("query_", "")
            break

    kb_context = build_kb_context(dataset)
    enriched_description = db_description + kb_context
    _original_init(self, query_dir, enriched_description, db_config_path, deployment_name, **kwargs)


_da.DataAgent.__init__ = _patched_init
