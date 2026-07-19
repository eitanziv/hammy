"""Agent-facing documentation templates written by `hammy init`.

HAMMY_MD is the single source of truth for how an AI agent should use the
Hammy MCP tools in an indexed project. Users reference it from their own
CLAUDE.md / AGENTS.md / .cursorrules / CONTEXT.md so Hammy never has to
touch those files. SKILL_MD is a thin Claude Code skill that triggers on
code-navigation phrasing and points back to HAMMY.md.

Tool names and parameters here must stay in sync with hammy.mcp.server.
"""

from __future__ import annotations

REFERENCE_LINE = (
    "This project is indexed by the `hammy` MCP server. "
    "Read HAMMY.md before navigating, searching, or modifying code."
)

HAMMY_MD = """\
# HAMMY.md — Codebase Intelligence for AI Agents

This project is indexed by [Hammy](https://github.com/dvnc0/hammy), an MCP server
(`hammy`) that maintains a pre-built symbol graph, call graph, and VCS history for
this codebase. Prefer Hammy tools over grep and file-by-file reading for code
questions: they answer from a parsed index, so results are complete, structured,
and never confuse a real call with a comment or string.

## Tool routing — pick by what you're doing

| You want to... | Call | Instead of |
|---|---|---|
| Get oriented in the project | `index_status` | listing directories |
| Understand a directory | `module_summary(directory)` | opening every file in it |
| See what's in one file | `ast_query(file_path)` | reading the whole file |
| Investigate one symbol (definition + callers + callees + history) | `explain_symbol(name)` | grep + reading several files |
| Get definitions for names you already know | `lookup_symbol(names=[...])` — up to 20 per call | grepping for each one |
| Find a symbol when unsure of spelling | `search_symbols(query)` | grep -i |
| Find code by what it does, name unknown | `search_code_hybrid(query)` | guessing keywords with grep |
| Find symbols by shape (visibility, params, complexity) | `structural_search(...)` | not possible with grep |
| "Where is this called?" | `find_usages(symbol_name)` | grep (matches strings/comments, misses the containing function) |
| "What breaks if I change this?" | `impact_analysis(symbol_name)` | hoping you found everything |
| "Is this risky to touch?" | `hotspot_score(file_filter=...)` | guessing |
| Risk-rate a diff or PR | `pr_diff(working_tree=True)` | eyeballing the diff |
| Link frontend calls to backend endpoints | `find_bridges()` | tracing URLs by hand |
| Find dev warnings (TODO, "don't touch") | `search_comments(...)` | grep TODO |
| File history, ownership, stability | `git_log`, `git_blame`, `file_churn` | raw git commands |

For `find_usages` and `impact_analysis`, pass the **bare** function/method name
(`charge`, not `PaymentService::charge`) — call expressions only contain the bare name.

## Recommended workflow

1. **Session start:** call `index_status` — confirms the index is live and shows
   what languages and how many symbols are indexed. If the memory tools are
   available, also call `recall_context(query=...)`: a prior session or sub-agent
   may have already researched your task.
2. **Before modifying any function:** `impact_analysis` (blast radius), then
   `hotspot_score` (risk level).
3. **After any significant finding** (entry point located, dependency mapped,
   risk identified): `store_context(key, content)` immediately, so future
   sessions don't repeat the work.
4. **After editing files:** call `reindex` if searches start returning stale results.

## When to fall back to grep / reading files

Config files, docs, data files, languages not in the index (check
`index_status`), or when a Hammy search comes back empty. For everything else,
the index is faster and more reliable.
"""

SKILL_MD = """\
---
name: hammy
description: Navigate and analyze this codebase using the Hammy MCP server (symbol graph, call graph, VCS history). Use for any code-navigation or code-risk question — finding where a function is called or defined, understanding an unfamiliar module or directory, tracing dependencies, assessing the blast radius or risk of a change, reviewing a diff or PR, or searching for code by description when the symbol name is unknown. Prefer this over grep, glob, or reading files one by one whenever the question is about code structure, callers, dependencies, history, or risk.
---

# Hammy codebase intelligence

This project is indexed by the `hammy` MCP server. Read `HAMMY.md` in the project
root for the full tool routing table. Core rules:

1. Answer code-structure questions from the index, not grep:
   callers → `find_usages` (bare name, no `Class::` prefix) · one symbol in depth →
   `explain_symbol` · a directory → `module_summary` · known names →
   `lookup_symbol(names=[...])` · description only → `search_code_hybrid`.
2. Before modifying any function: `impact_analysis` (blast radius) +
   `hotspot_score` (risk).
3. Start sessions with `index_status`; check `recall_context` for prior research;
   save significant findings with `store_context`.
4. Fall back to grep/reading files only for unindexed content (docs, config,
   other languages) or when Hammy returns nothing.
"""
