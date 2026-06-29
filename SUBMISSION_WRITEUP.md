# SignBridge Agent — Submission Write-Up 🤟

## 🎯 Problem Statement
Over 430 million people globally experience disabling hearing loss. Communication between Deaf/Hard-of-Hearing (DHH) individuals and hearing individuals often suffers due to structural differences between spoken languages and sign languages (such as American Sign Language - ASL). Spoken languages rely on auditory-vocal structures, whereas sign languages utilize spatial, non-manual markers (facial expressions), and distinct Topic-Comment grammatical rules. Traditional direct translators fail to convey accurate ASL gloss syntax or physical sign parameters (handshapes, locations, movements), leading to misunderstandings, especially in emergency or healthcare scenarios.

## 💡 Solution Architecture
SignBridge Agent is an intelligent, multi-agent accessibility system engineered with Google's Agent Development Kit (ADK 2.0). It combines specialized sub-agents with a Model Context Protocol (MCP) server, strict security audit controls, and human-in-the-loop verification checkpoints to deliver accurate, respectful, and accessible translation and output formatting.

```
+--------------------------------------------------------------------------+
|                            SIGNBRIDGE AGENT                              |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   |                       Security Checkpoint                        |   |
|   |          (PII Redaction + Prompt Injection Detection)            |   |
|   +------------------------------------------------------------------+   |
|                                    |                                     |
|                                    v                                     |
|   +------------------------------------------------------------------+   |
|   |                     Root Orchestrator Agent                      |   |
|   +------------------------------------------------------------------+   |
|                        /                        \                        |
|                       v                          v                       |
|   +--------------------------+        +--------------------------+   |
|   |     translator_agent     |        |   accessibility_agent    |   |
|   |  (ASL Gloss & Grammar)   |        |   (Formatting & Display) |   |
|   +--------------------------+        +--------------------------+   |
|                 \                                /                       |
|                  +---------------+--------------+                        |
|                                  |                                       |
|                                  v                                       |
|   +------------------------------------------------------------------+   |
|   |                    SignBridge MCP Server                         |   |
|   |  (dictionary_lookup, grammar_checker, accessibility_formatter)   |   |
|   +------------------------------------------------------------------+   |
+--------------------------------------------------------------------------+
```

---

## 🚀 Key Concepts & ADK Implementation

1. **ADK Multi-Agent Architecture (`app/agent.py`)**:
   - Uses `root_agent` as an orchestrator equipped with `AgentTool` instances delegating tasks to specialized sub-agents (`translator_agent` and `accessibility_agent`).
2. **Model Context Protocol (MCP) (`app/mcp_server.py`)**:
   - Standalone MCP server running over stdio transport exposing 4 domain tools: `dictionary_lookup`, `grammar_checker`, `accessibility_formatter`, and `sign_phrase_builder`.
   - Wired seamlessly into agents using `google.adk.tools.McpToolset`.
3. **Security & Governance Checkpoint (`app/agent.py`)**:
   - `security_checkpoint` function tool executes automated PII scrubbing (emails, phone numbers, SSNs) and prompt injection keyword detection.
   - Outputs structured JSON audit logs categorized by severity level (`INFO`, `WARNING`, `CRITICAL`).
4. **Human-In-The-Loop (HITL) Verification**:
   - `request_human_verification` tool enables explicit pauses for sensitive medical, legal, or emergency translations requiring human validator approval.
5. **Agents CLI & Developer Tooling**:
   - Scaffolded using `google-agents-cli` version 0.5.1 with pinned dependencies for reliable local dev and deployment.

---

## 🔒 Security Design

Security is paramount when handling personal and accessibility communications:
- **PII Scrubbing**: Regex patterns automatically detect and mask emails, phone numbers, and social security numbers prior to translation processing.
- **Prompt Injection Defense**: Scans input for common jailbreak/override phrases, halting execution and emitting a `CRITICAL` severity audit event if detected.
- **Structured JSON Auditing**: Log lines are emitted in JSON format for compatibility with Cloud Logging and SIEM monitoring tools.

---

## ⚙️ MCP Server Tools

- `dictionary_lookup(term)`: Provides handshape, movement, and physical location metadata for ASL terms.
- `grammar_checker(gloss_text)`: Validates Topic-Comment structures, time indicator placement, and facial expression requirements.
- `accessibility_formatter(text, mode)`: Transforms output into accessible modalities (visual captions, high contrast, tactical haptics).
- `sign_phrase_builder(english_phrase)`: Synthesizes initial ASL gloss sequences from spoken English.

---

## 🌟 Impact & Value Statement

SignBridge Agent empowers Deaf and Hard-of-Hearing individuals by providing reliable, context-aware translation tools that honor sign language grammar and accessibility needs. By integrating security audit trails and human verification, it provides a safe foundation for deployment in public services, education, and healthcare settings.
