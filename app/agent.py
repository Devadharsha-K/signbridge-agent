import os
import re
import json
import logging
from typing import Any, Dict

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import AgentTool, FunctionTool
from google.adk.tools.mcp_tool.mcp_toolset import StdioConnectionParams, StdioServerParameters, McpToolset
from google.genai import types

from app.config import config

# Ensure Vertex AI is disabled to use Gemini API Key
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Initialize MCP Toolset to connect to app.mcp_server
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "python", "-m", "app.mcp_server"],
        )
    )
)

# Shared Gemini Model instance
model_instance = Gemini(
    model=config.model,
    retry_options=types.HttpRetryOptions(attempts=config.max_iterations),
)

# ---------------------------------------------------------------------------
# Specialized Sub-Agent 1: Translator Agent
# ---------------------------------------------------------------------------
translator_agent = LlmAgent(
    name="translator_agent",
    model=model_instance,
    instruction=(
        "You are an expert Sign Language Translator. Your job is to translate between Spoken English "
        "and ASL Gloss notation. Use the provided MCP dictionary lookup and grammar checking tools to verify "
        "handshapes, movements, locations, and Topic-Comment syntax structures."
    ),
    tools=[mcp_toolset],
)

# ---------------------------------------------------------------------------
# Specialized Sub-Agent 2: Accessibility Agent
# ---------------------------------------------------------------------------
accessibility_agent = LlmAgent(
    name="accessibility_agent",
    model=model_instance,
    instruction=(
        "You are an Accessibility & Output Formatting Specialist. Your job is to format translations and captions "
        "for display devices (e.g. visual captions, high-contrast mode, tactical haptics). Use the MCP accessibility_formatter "
        "tool when requested."
    ),
    tools=[mcp_toolset],
)

# ---------------------------------------------------------------------------
# Security Checkpoint & Audit Logging Function Tools (Phase 4)
# ---------------------------------------------------------------------------
logger = logging.getLogger("SignBridgeSecurityAudit")
logging.basicConfig(level=logging.INFO)

def security_checkpoint(user_input: str) -> str:
    """Run security audit checkpoint on user input: PII scrubbing, prompt injection detection, and structured logging."""
    audit_log = {"event": "security_checkpoint", "input_len": len(user_input), "severity": "INFO", "alerts": []}
    clean_input = user_input
    
    # 1. PII Scrubbing (Email, Phone, SSN)
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    
    if re.search(email_pattern, clean_input) or re.search(phone_pattern, clean_input) or re.search(ssn_pattern, clean_input):
        clean_input = re.sub(email_pattern, "[REDACTED_EMAIL]", clean_input)
        clean_input = re.sub(phone_pattern, "[REDACTED_PHONE]", clean_input)
        clean_input = re.sub(ssn_pattern, "[REDACTED_SSN]", clean_input)
        audit_log["alerts"].append("PII_DETECTED_AND_SCRUBBED")
        audit_log["severity"] = "WARNING"
        
    # 2. Prompt Injection Detection
    injection_keywords = ["ignore previous instructions", "system prompt", "disregard instructions", "bypass security"]
    is_injection = any(keyword in user_input.lower() for keyword in injection_keywords)
    if is_injection:
        audit_log["alerts"].append("PROMPT_INJECTION_ATTEMPT")
        audit_log["severity"] = "CRITICAL"
        logger.warning(f"AUDIT_LOG: {json.dumps(audit_log)}")
        return "SECURITY ALERT: Potential prompt injection detected. Request blocked by SignBridge security policy."
        
    logger.info(f"AUDIT_LOG: {json.dumps(audit_log)}")
    return f"Security checkpoint passed cleanly. Sanitized input: '{clean_input}'"

def request_human_verification(action_details: str) -> str:
    """Request human-in-the-loop verification for sensitive translation outputs or medical/emergency terminology."""
    return f"HUMAN-IN-THE-LOOP CHECKPOINT: Verification requested for [{action_details}]. Please confirm accuracy."

# ---------------------------------------------------------------------------
# Orchestrator / Root Agent (Phase 2)
# ---------------------------------------------------------------------------
root_agent = LlmAgent(
    name="root_agent",
    model=model_instance,
    instruction=(
        "You are the SignBridge Orchestrator Agent. You facilitate communication between deaf/hard-of-hearing individuals "
        "and hearing users. Always run the `security_checkpoint` tool on user queries first. "
        "Delegate translation requests to `translator_agent` using its agent tool, and delegate accessibility/formatting requests "
        "to `accessibility_agent`. For sensitive or medical/emergency terms, invoke `request_human_verification`."
    ),
    tools=[
        FunctionTool(security_checkpoint),
        FunctionTool(request_human_verification),
        AgentTool(agent=translator_agent),
        AgentTool(agent=accessibility_agent),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
