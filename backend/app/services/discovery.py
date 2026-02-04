"""Discovery session service: style assessment, phase prompts, summaries, report, out-of-scope detection.

Refactored from backend/discovery_session.py to work with database models and API.
"""

from typing import Any

from anthropic import Anthropic

from app.config import get_settings

# Communication style dimensions (option order A,B,C,D in assessment)
STYLE_DIMENSIONS = ["Detail-oriented", "Big-picture", "Story-driven", "Problem-focused"]

PHASES = {
    1: {
        "name": "Open Discovery",
        "description": "Conversational & exploratory - your team, processes, tools, what works and what doesn't",
        "system_prompt": """You are conducting an open, conversational discovery interview. Your goal is to understand the complete picture of the user's work.

Ask them to walk you through:
- Their team and role
- Their day-to-day work and processes
- Tools and systems they use
- What works well and what doesn't
- Any frustrations or challenges
- What they wish was different

Be conversational and follow interesting threads naturally. Don't rigidly separate topics - let them tell their story. Ask follow-up questions when something interesting comes up. Capture everything they mention about current state, pain points, and desired outcomes.

If the user mentions something that seems outside the project scope, note it mentally but continue the conversation naturally. You'll flag out-of-scope items later. For now, focus on building rapport and gathering information.

CRITICAL CONVERSATION RULE: Ask a maximum of TWO questions per message. Acknowledge what the user shared, make observations or connections, then ask one or two follow-up questions. Keep it conversational and warm - like a thoughtful colleague having a genuine dialogue, not a robotic interview. If you have more questions, save them for after the user responds.""",
        "initial_question": "Let's start with the big picture. Can you walk me through your work - your team, your role, the processes you follow, and the tools you use? Tell me what works well and what doesn't.",
    },
    2: {
        "name": "Targeted Follow-ups",
        "description": "Gap-filling for in-scope topics only",
        "system_prompt": """You are conducting targeted follow-up questions based on Phase 1.

Project Scope: {scope}

CRITICAL: Your follow-up questions must focus ONLY on topics that are IN-SCOPE for this project. Review the Phase 1 conversation and identify gaps ONLY in scope-relevant areas:

IN-SCOPE FOLLOW-UPS (ask these):
- Processes directly related to the project scope
- Tools and systems that will be affected by or integrated with the project
- Pain points that the project is intended to solve
- Team interactions and handoffs within the scope boundary
- Data flows and integrations relevant to the project

OUT-OF-SCOPE (do NOT ask about these):
- Processes, tools, or pain points unrelated to the stated project scope
- Systems that won't be touched by this project
- Team functions outside the project boundary
- "Nice to know" information that doesn't impact the project

EXCEPTION - Scope Expansion Candidates:
If an out-of-scope item mentioned in Phase 1 appears CRITICAL to project success (meaning the project would fail or be significantly compromised without addressing it), you may ask ONE brief clarifying question to gather enough detail for a scope expansion recommendation. Frame it as: "You mentioned [item]. This seems like it could impact our project. Can you briefly explain how it connects to [in-scope process]?"

Before asking any question, mentally check: "Is this directly relevant to the project scope?" If not, skip it.

Ask specific, focused questions referencing Phase 1: "You mentioned X, can you tell me more about..."

Keep this phase efficient - only fill critical gaps for IN-SCOPE topics.

IMPORTANT: Ask questions ONE AT A TIME in a conversational manner. Do not list all your questions at once. Ask the first question, wait for the response, then ask your next question based on what you learn. Keep the conversation natural and flowing.

CRITICAL CONVERSATION RULE: Ask a maximum of TWO questions per message. Acknowledge what the user shared, make observations or connections, then ask one or two follow-up questions. Keep it conversational and warm - like a thoughtful colleague having a genuine dialogue, not a robotic interview. If you have more questions, save them for after the user responds.""",
        "initial_question": "Based on what you've told me, I have some follow-up questions to make sure I understand the details correctly.",
    },
    3: {
        "name": "Validation & Clarification",
        "description": "Confirm understanding and resolve contradictions",
        "system_prompt": """You are validating your understanding and resolving any contradictions. Review Phases 1 and 2 and:
- Confirm your understanding of key in-scope processes
- Resolve any contradictions or inconsistencies
- Clarify ambiguous statements about in-scope items
- Verify assumptions

Use phrases like 'Let me make sure I understand...' and 'Earlier you mentioned X, and also Y - how do those work together?'

CRITICAL CONVERSATION RULE: Ask a maximum of TWO questions per message. Acknowledge what the user shared, make observations or connections, then ask one or two follow-up questions. Keep it conversational and warm - like a thoughtful colleague having a genuine dialogue, not a robotic interview. If you have more questions, save them for after the user responds.""",
        "initial_question": "Let me make sure I understand correctly. I want to confirm a few things and resolve any unclear points.",
    },
    4: {
        "name": "Future State & Priorities",
        "description": "Define success and priorities",
        "system_prompt": """You are exploring the future state and success criteria. Now that you understand the current state completely:
- Ask what success looks like for this project
- Understand their priorities and must-haves vs nice-to-haves
- Explore their vision for the ideal state
- Define clear success metrics

Be forward-looking and solution-oriented.

CRITICAL CONVERSATION RULE: Ask a maximum of TWO questions per message. Acknowledge what the user shared, make observations or connections, then ask one or two follow-up questions. Keep it conversational and warm - like a thoughtful colleague having a genuine dialogue, not a robotic interview. If you have more questions, save them for after the user responds.""",
        "initial_question": "Now that I understand where things are today, let's talk about where you want to be. What does success look like for this project? What are your must-haves?",
    },
}


PHASE_COMPLETION_INSTRUCTION = (
    "When you feel you have gathered sufficient information for this phase, end your response with "
    "the marker [PHASE_COMPLETE]. Before this marker, summarize what you've learned and confirm with "
    "the user: \"I think I have a good understanding of this topic so far. Before we move on, is there "
    "anything else you'd like to add about this area?\""
)


def _get_client() -> Anthropic:
    """Return Anthropic client using config API key."""
    settings = get_settings()
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def calculate_style_profile(responses: list[dict]) -> dict[str, Any]:
    """Compute scores and primary/secondary style from assessment responses.

    responses: list of {question: str, ranks: {A, B, C, D}} where A=Detail-oriented, B=Big-picture, C=Story-driven, D=Problem-focused.
    Lower score = stronger preference.
    """
    scores = {style: 0 for style in STYLE_DIMENSIONS}
    for r in responses:
        ranks = r.get("ranks", {})
        # ranks keys A,B,C,D map to STYLE_DIMENSIONS[0..3]
        for i, key in enumerate(["A", "B", "C", "D"]):
            if i < len(STYLE_DIMENSIONS) and key in ranks:
                scores[STYLE_DIMENSIONS[i]] += ranks[key]
    sorted_styles = sorted(scores.items(), key=lambda x: x[1])
    primary = sorted_styles[0][0]
    secondary = sorted_styles[1][0]
    return {
        "scores": scores,
        "primary_style": primary,
        "secondary_style": secondary,
        "responses": responses,
    }


def build_style_guidance(profile: dict[str, Any]) -> str:
    """Return a guidance string for Claude based on primary and secondary styles."""
    primary = profile.get("primary_style", "")
    secondary = profile.get("secondary_style", "")
    parts = [
        "Adapt your communication style to the user's preferences.",
        f"The user's primary style is: {primary}. The secondary style is: {secondary}.",
    ]

    def add_for(style: str, text: str) -> None:
        if primary == style or secondary == style:
            parts.append(text)

    add_for("Big-picture", "- Lead with connections and context. Emphasize how pieces fit together and avoid unnecessary low-level detail unless requested.")
    add_for("Detail-oriented", "- Be specific and precise. Provide step-by-step information, concrete examples, and clarify assumptions.")
    add_for("Story-driven", "- Use examples and short narratives. Ask for specific situations or recent examples to ground the discussion.")
    add_for("Problem-focused", "- Focus on outcomes, issues, and decisions. Get to the core problems and potential solutions quickly.")
    return "\n".join(parts)


def get_summary_style_guidance(style_profile: dict[str, Any]) -> str:
    """Return style-specific guidance for concise summary generation."""
    primary = style_profile.get("primary_style", "")
    secondary = style_profile.get("secondary_style", "")
    guidance = f"Generate a BRIEF, scannable summary (5-10 bullet points max) adapted to the user's communication style. Primary: {primary}, Secondary: {secondary}.\n\n"
    guidance += "Focus on KEY takeaways only - highlights that can be quickly reviewed and validated.\n\n"
    if primary == "Detail-oriented" or secondary == "Detail-oriented":
        guidance += "Style: Each bullet should include specific details, metrics, or concrete facts. Be precise but concise.\n"
    if primary == "Big-picture" or secondary == "Big-picture":
        guidance += "Style: Each bullet should show connections and how pieces fit together. Emphasize relationships.\n"
    if primary == "Story-driven" or secondary == "Story-driven":
        guidance += "Style: Each bullet should include brief examples or context. Keep the narrative concise.\n"
    if primary == "Problem-focused" or secondary == "Problem-focused":
        guidance += "Style: Each bullet should focus on impact, challenges, and outcomes. Emphasize why things matter.\n"
    return guidance


def get_phase_system_prompt(phase_num: int, scope: str, style_profile: dict[str, Any] | None) -> str:
    """Return full system prompt for a phase (base + scope if phase 2 + style guidance)."""
    phase = PHASES.get(phase_num, PHASES[1])
    base = phase["system_prompt"]
    if phase_num == 2:
        base = base.format(scope=scope)
    if style_profile:
        style_guidance = build_style_guidance(style_profile)
        base = base + "\n\nCOMMUNICATION STYLE GUIDANCE:\n" + style_guidance
    # Add phase completion behavior instructions for all phases
    base = base + "\n\nPHASE COMPLETION BEHAVIOR:\n" + PHASE_COMPLETION_INSTRUCTION
    return base


def get_phase_transition_message(phase_num: int) -> str:
    """Return transition message when moving to a new phase."""
    phase = PHASES.get(phase_num, PHASES[1])
    return f"\n{'=' * 60}\nMoving to Phase {phase_num}: {phase['name']}\n{phase['description']}\n{'=' * 60}\n"


def get_phase_initial_question(phase_num: int) -> str:
    """Return the initial question for a phase."""
    phase = PHASES.get(phase_num, PHASES[1])
    return phase.get("initial_question", "Let's continue our conversation.")


def generate_phase_summary(
    phase_num: int,
    messages: list[dict],
    scope: str,
    style_profile: dict[str, Any] | None,
    phase_documents: list[dict] | None = None,
) -> str | None:
    """Generate a brief summary of the phase conversation. Returns summary text or None on error."""
    phase_documents = phase_documents or []
    phase = PHASES.get(phase_num, PHASES[1])
    style_guidance = get_summary_style_guidance(style_profile or {"primary_style": "", "secondary_style": ""})

    conversation_text = ""
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            conversation_text += f"User: {content}\n\n"
        elif role == "assistant":
            conversation_text += f"Claude: {content}\n\n"

    if phase_documents:
        doc_lines = [f"- {d.get('path', '')} ({d.get('type', '')})" for d in phase_documents]
        documents_text = "\n".join(doc_lines)
    else:
        documents_text = "None provided in this phase."

    prompt = f"""Create a BRIEF, scannable summary of this discovery phase conversation.

Phase: {phase['name']} - {phase['description']}
Project Scope: {scope}

Conversation:
{conversation_text}

Documents provided in this phase:
{documents_text}

{style_guidance}

IMPORTANT: Create a concise summary with 5-10 bullet points maximum that:
- Captures only the KEY takeaways and highlights
- Is easy to quickly review and validate
- Still adapts to the user's communication style (detail-oriented gets specifics, big-picture gets connections, etc.) but keeps it brief
- Focuses on what matters most, not everything that was said

The goal is: "Here are the highlights - anything missing or wrong?" not "Here's everything you said."

Do NOT create a comprehensive narrative. Keep it brief and scannable.

Summary (5-10 bullet points):"""

    try:
        client = _get_client()
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception:
        return None


def review_and_approve_summary(
    phase_num: int,
    initial_summary: str,
    scope: str,
    style_profile: dict[str, Any] | None,
    action: str,
    feedback: str | None = None,
) -> str | None:
    """Handle one approval step: approve (return None = done), request_changes, or add_details. Returns revised summary text or None if approved (no revision needed)."""
    phase = PHASES.get(phase_num, PHASES[1])
    if action == "approve":
        return None  # caller stores initial_summary as approved

    client = _get_client()
    if action == "request_changes" and feedback:
        prompt = f"""The user requested changes to this brief summary:

Original Summary:
{initial_summary}

User Feedback:
{feedback}

Phase: {phase['name']} - {phase['description']}
Project Scope: {scope}

Please revise the summary (5-10 bullet points max) incorporating the user's feedback while maintaining the concise, scannable format and communication style.

Revised Summary:"""
    elif action == "add_details" and feedback:
        prompt = f"""The user wants to add details to this brief summary:

Current Summary:
{initial_summary}

Additional Details to Include:
{feedback}

Phase: {phase['name']} - {phase['description']}
Project Scope: {scope}

Please update the summary to incorporate these additional details. You may expand beyond 10 bullet points if needed to include the important details, but keep it scannable and focused on key takeaways.

Updated Summary:"""
    else:
        return initial_summary

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception:
        return initial_summary


def generate_final_report(
    phase_summaries: dict[str, Any],
    scope: str,
    flagged_items: list[dict],
) -> str:
    """Generate the final discovery report text from approved phase summaries and flagged items."""
    summaries_text = ""
    phase_keys = [k for k in phase_summaries.keys() if str(k).isdigit()]
    for phase_num in sorted(phase_keys, key=int):
        phase = PHASES.get(int(phase_num), PHASES[1])
        summary = phase_summaries.get(phase_num, "")
        if isinstance(summary, str):
            summaries_text += f"\n{'=' * 60}\n"
            summaries_text += f"PHASE {phase_num}: {phase['name']} - {phase['description']}\n"
            summaries_text += f"{'=' * 60}\n\n"
            summaries_text += f"{summary}\n\n"

    flagged_summary_lines = []
    for idx, item in enumerate(flagged_items, start=1):
        flagged_summary_lines.append(
            f"{idx}. Phase {item.get('phase')}: {item.get('mention')}\n"
            f"   Original user statement: {item.get('user_input')}"
        )
    flagged_summary = "\n".join(flagged_summary_lines) if flagged_summary_lines else "None"

    prompt = f"""You are creating a structured discovery session report. Use the approved phase summaries below as your primary source material.

Project Scope: {scope}

Approved Phase Summaries (user-reviewed and approved):
{summaries_text}

Flagged Out-of-Scope Mentions Detected During Conversation:
{flagged_summary}

Create a structured document with the following sections:

1. PROJECT SCOPE
   - [The project scope as provided]

2. CURRENT STATE FINDINGS (Phases 1 & 2)
   - Team Function & Structure
   - Current Tools & Systems
   - Departments & Partners
   - Day-to-Day Processes
   - Current Workflows

3. PAIN POINTS (Phase 3)
   - Key Frustrations
   - Challenges & Blockers
   - What Slows Them Down

4. SUCCESS CRITERIA (Phase 4)
   - Ideal State Vision
   - Success Metrics
   - What Would Be a Win

5. RECOMMENDED SCOPE ADDITIONS
   - Items that were out-of-scope during the conversation but WOULD be beneficial to add to the project scope.
   - For each item, explain clearly WHY including it would add value. Consider whether it would improve efficiency, solve related problems, create better outcomes, or add significant business value.

6. OTHER OUT-OF-SCOPE MENTIONS
   - Items that were mentioned but are not clearly beneficial to include in scope, or are better handled separately.

In your analysis of flagged items, be thoughtful and selective. Only recommend scope additions where there is a clear, defensible benefit to the project.

Format this as a clear, professional document. Use bullet points and clear headings."""

    try:
        client = _get_client()
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception:
        return "Error generating report."


def get_assistant_reply(system_prompt: str, messages: list[dict]) -> str:
    """Single turn: send messages to Claude with system prompt, return assistant reply text."""
    client = _get_client()

    # Filter to valid messages and ensure proper alternation
    valid_messages = []
    last_role = None

    for m in messages:
        role = m.get("role")
        content = m.get("content", "").strip()

        if not content or role not in ["user", "assistant"]:
            continue

        # Skip if same role as last (Claude needs alternating roles)
        if role == last_role:
            continue

        valid_messages.append({"role": role, "content": content})
        last_role = role

    # If conversation starts with assistant, remove it (will be in system prompt context)
    if valid_messages and valid_messages[0]["role"] == "assistant":
        valid_messages.pop(0)

    # If no messages or empty after filtering, add a starter
    if not valid_messages:
        valid_messages = [{"role": "user", "content": "Please continue."}]

    # If last message is from assistant, add a user prompt to continue
    if valid_messages and valid_messages[-1]["role"] == "assistant":
        valid_messages.append({"role": "user", "content": "Please continue."})

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=system_prompt,
        messages=valid_messages,
    )

    # Handle empty response
    if not response.content:
        return "I'm ready to continue our conversation. Where would you like to pick up?"

    return response.content[0].text


def detect_out_of_scope(scope: str, message: str) -> str | None:
    """Detect if user message mentions something outside project scope. Returns description string or None if in scope."""
    detection_prompt = f"""Analyze this user message and determine if it mentions anything outside the project scope.

Project Scope: {scope}

User Message: {message}

If the message mentions anything outside the project scope, respond with:
OUT_OF_SCOPE: [brief description of what was mentioned]

If everything is within scope, respond with:
IN_SCOPE

Be conservative - only flag things that are clearly outside the stated scope."""

    try:
        client = _get_client()
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=200,
            messages=[{"role": "user", "content": detection_prompt}],
        )
        result = response.content[0].text.strip()
        if result.startswith("OUT_OF_SCOPE:"):
            return result.replace("OUT_OF_SCOPE:", "").strip()
        return None
    except Exception:
        return None
