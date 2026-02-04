"""
Discovery Session Script
A structured discovery interview tool that conducts a 4-phase discovery session
with system messages to guide Claude's conversational behavior.
"""

import os
import json
import base64
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

try:
    import PyPDF2  # type: ignore
except ImportError:
    PyPDF2 = None

try:
    import docx  # type: ignore
except ImportError:
    docx = None

# Communication style dimensions
STYLE_DIMENSIONS = ["Detail-oriented", "Big-picture", "Story-driven", "Problem-focused"]

# Phase definitions (base prompts, style will be appended dynamically)
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

If the user mentions something that seems outside the project scope, note it mentally but continue the conversation naturally. You'll flag out-of-scope items later. For now, focus on building rapport and gathering information.""",
        "initial_question": "Let's start with the big picture. Can you walk me through your work - your team, your role, the processes you follow, and the tools you use? Tell me what works well and what doesn't."
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

IMPORTANT: Ask questions ONE AT A TIME in a conversational manner. Do not list all your questions at once. Ask the first question, wait for the response, then ask your next question based on what you learn. Keep the conversation natural and flowing.""",
        "initial_question": "Based on what you've told me, I have some follow-up questions to make sure I understand the details correctly."
    },
    3: {
        "name": "Validation & Clarification",
        "description": "Confirm understanding and resolve contradictions",
        "system_prompt": """You are validating your understanding and resolving any contradictions. Review Phases 1 and 2 and:
- Confirm your understanding of key in-scope processes
- Resolve any contradictions or inconsistencies
- Clarify ambiguous statements about in-scope items
- Verify assumptions

Use phrases like 'Let me make sure I understand...' and 'Earlier you mentioned X, and also Y - how do those work together?'""",
        "initial_question": "Let me make sure I understand correctly. I want to confirm a few things and resolve any unclear points."
    },
    4: {
        "name": "Future State & Priorities",
        "description": "Define success and priorities",
        "system_prompt": """You are exploring the future state and success criteria. Now that you understand the current state completely:
- Ask what success looks like for this project
- Understand their priorities and must-haves vs nice-to-haves
- Explore their vision for the ideal state
- Define clear success metrics

Be forward-looking and solution-oriented.""",
        "initial_question": "Now that I understand where things are today, let's talk about where you want to be. What does success look like for this project? What are your must-haves?"
    }
}


def get_communication_style_assessment():
    """Run a 5-question communication style assessment and return scores and profile."""
    print("=" * 60)
    print("COMMUNICATION STYLE ASSESSMENT")
    print("=" * 60)
    print("For each question, rank the 4 options from 1 to 4:")
    print("  1 = Most like you / most preferred")
    print("  4 = Least like you / least preferred")
    print("Use each rank (1, 2, 3, 4) exactly once per question.\n")

    # IMPORTANT: Option order MUST stay consistent across all questions:
    # A) Detail-oriented, B) Big-picture, C) Story-driven, D) Problem-focused
    questions = [
        {
            "title": "Question 1: Learning Preference",
            "prompt": 'When learning about a new system or process, rank these by preference (1 = most preferred, 4 = least preferred):',
            "options": [
                "A) Step-by-step instructions with specific details",
                "B) An overview of how everything connects",
                "C) Real examples and stories from others who've used it",
                "D) Focus on what problems it solves",
            ],
        },
        {
            "title": "Question 2: Frustration Triggers",
            "prompt": "You're most likely to get frustrated when someone... (rank 1-4):",
            "options": [
                "A) Gives you a vague answer when you need specifics",
                "B) Drowns you in details without explaining why it matters",
                "C) Uses abstract concepts without concrete examples",
                "D) Focuses on process instead of outcomes",
            ],
        },
        {
            "title": "Question 3: Explanation Style",
            "prompt": "When explaining something you know well, you naturally... (rank 1-4):",
            "options": [
                "A) Walk through it step-by-step with all the details",
                "B) Start with the big picture and how pieces fit together",
                "C) Tell a story or give examples from experience",
                "D) Focus on why it matters and what problem it solves",
            ],
        },
        {
            "title": "Question 4: Decision Making",
            "prompt": "When making a decision, you prefer to have... (rank 1-4):",
            "options": [
                "A) Specific data points and clear criteria",
                "B) Understanding of how it affects the whole system",
                "C) Examples of how similar decisions played out",
                "D) Clear problem definition and expected outcomes",
            ],
        },
        {
            "title": "Question 5: Communication Preference",
            "prompt": "In work conversations, you prefer when people... (rank 1-4):",
            "options": [
                "A) Are precise and specific about details",
                "B) Explain context and connections",
                "C) Share real examples and experiences",
                "D) Get straight to the problem and solution",
            ],
        },
    ]

    scores = {style: 0 for style in STYLE_DIMENSIONS}
    responses = []

    def prompt_for_ranks(question_index, question):
        print(f"\n{question['title']}")
        print(f"\"{question['prompt']}\"")
        for option in question["options"]:
            print(f"  {option}")

        while True:
            raw = input("Enter ranks for A B C D as four numbers (e.g., '1 3 2 4'): ").strip()
            parts = raw.split()
            if len(parts) != 4 or not all(p.isdigit() for p in parts):
                print("Please enter exactly four numbers between 1 and 4.")
                continue
            ranks = [int(p) for p in parts]
            if sorted(ranks) != [1, 2, 3, 4]:
                print("Each rank (1, 2, 3, 4) must be used exactly once.")
                continue
            return ranks

    for idx, q in enumerate(questions):
        ranks = prompt_for_ranks(idx, q)
        responses.append(
            {
                "question": q["title"],
                "ranks": {
                    "A": ranks[0],
                    "B": ranks[1],
                    "C": ranks[2],
                    "D": ranks[3],
                },
            }
        )
        for option_index, rank in enumerate(ranks):
            style = STYLE_DIMENSIONS[option_index]  # fixed mapping order
            scores[style] += rank

    # Lower score = stronger preference
    sorted_styles = sorted(scores.items(), key=lambda x: x[1])
    primary_style = sorted_styles[0][0]
    secondary_style = sorted_styles[1][0]

    profile = {
        "scores": scores,
        "primary_style": primary_style,
        "secondary_style": secondary_style,
        "responses": responses,
    }

    print("\nYour communication style profile:")
    print(f"  Primary: {primary_style}")
    print(f"  Secondary: {secondary_style}")
    print("  Scores (lower = stronger preference):")
    for style, score in sorted_styles:
        print(f"    - {style}: {score}")

    return profile


def build_style_guidance(profile):
    """Return a guidance string for Claude based on primary and secondary styles."""
    primary = profile["primary_style"]
    secondary = profile["secondary_style"]

    style_guidance_parts = [
        "Adapt your communication style to the user's preferences.",
        f"The user's primary style is: {primary}. The secondary style is: {secondary}.",
    ]

    def add_for(style, text):
        if primary == style or secondary == style:
            style_guidance_parts.append(text)

    add_for(
        "Big-picture",
        "- Lead with connections and context. Emphasize how pieces fit together and avoid unnecessary low-level detail unless requested.",
    )
    add_for(
        "Detail-oriented",
        "- Be specific and precise. Provide step-by-step information, concrete examples, and clarify assumptions.",
    )
    add_for(
        "Story-driven",
        "- Use examples and short narratives. Ask for specific situations or recent examples to ground the discussion.",
    )
    add_for(
        "Problem-focused",
        "- Focus on outcomes, issues, and decisions. Get to the core problems and potential solutions quickly.",
    )

    return "\n".join(style_guidance_parts)

SESSION_STATE_FILE = "session_state.json"

def save_session_state(
    scope,
    style_profile,
    current_phase,
    conversation_file,
    output_file,
    flagged_items,
    phase_summaries=None,
    all_messages=None,
):
    """Save the current session state to a JSON file."""
    state = {
        "scope": scope,
        "style_profile": style_profile,
        "current_phase": current_phase,
        "conversation_file": conversation_file,
        "output_file": output_file,
        "flagged_items": flagged_items,
        "phase_summaries": phase_summaries or {},
        "all_messages": all_messages or [],
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open(SESSION_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving session state: {str(e)}")
        return False

def load_session_state():
    """Load session state from JSON file. Returns None if file doesn't exist or is invalid."""
    if not os.path.exists(SESSION_STATE_FILE):
        return None
    try:
        with open(SESSION_STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state
    except Exception as e:
        print(f"Error loading session state: {str(e)}")
        return None

def delete_session_state():
    """Delete the session state file."""
    try:
        if os.path.exists(SESSION_STATE_FILE):
            os.remove(SESSION_STATE_FILE)
            return True
    except Exception as e:
        print(f"Error deleting session state: {str(e)}")
    return False

def get_scope_input():
    """Get project scope from the user."""
    print("=" * 60)
    print("DISCOVERY SESSION - SCOPE DEFINITION")
    print("=" * 60)
    print()
    print("Before we begin the discovery interview, please provide the project scope.")
    print("This will help guide our conversation and keep us focused.")
    print()
    scope = input("Project Scope: ").strip()
    while not scope:
        print("Please provide a project scope to continue.")
        scope = input("Project Scope: ").strip()
    return scope

def get_phase_transition_message(phase_num):
    """Get a transition message when moving to a new phase."""
    phase = PHASES[phase_num]
    return f"\n{'=' * 60}\nMoving to Phase {phase_num}: {phase['name']}\n{phase['description']}\n{'=' * 60}\n"


def load_single_document(path):
    """Load a single document and return a metadata dict plus content string for the model."""
    path = path.strip().strip('"').strip("'")
    if not path:
        return None

    if not os.path.exists(path):
        print(f"Document not found: {path}")
        return None

    _, ext = os.path.splitext(path)
    ext = ext.lower()

    try:
        if ext in [".pdf"]:
            if PyPDF2 is None:
                print("PyPDF2 is not installed. Please install it with 'pip install PyPDF2' to read PDFs.")
                return None
            text_parts = []
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text_parts.append(page_text)
            content = "\n".join(text_parts)
            return {
                "path": path,
                "type": "pdf",
                "content": content,
            }

        if ext in [".jpg", ".jpeg", ".png"]:
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            # Hint to the model about the content type
            return {
                "path": path,
                "type": "image",
                "content": encoded,
            }

        if ext in [".txt", ".md", ".csv"]:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return {
                "path": path,
                "type": "text",
                "content": content,
            }

        if ext in [".docx"]:
            if docx is None:
                print("python-docx is not installed. Please install it with 'pip install python-docx' to read .docx files.")
                return None
            document = docx.Document(path)
            content = "\n".join(p.text for p in document.paragraphs)
            return {
                "path": path,
                "type": "docx",
                "content": content,
            }

        # Unsupported type
        print(f"Unsupported document type for path: {path}")
        return None
    except Exception as e:
        print(f"Error reading document {path}: {str(e)}")
        return None


def load_documents_from_input(doc_input):
    """Parse a comma-separated list of paths and load documents."""
    docs = []
    paths = [p.strip() for p in doc_input.split(",") if p.strip()]
    for path in paths:
        doc = load_single_document(path)
        if doc:
            docs.append(doc)
    return docs

def get_summary_style_guidance(style_profile):
    """Return style-specific guidance for concise summary generation."""
    primary = style_profile["primary_style"]
    secondary = style_profile["secondary_style"]
    
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

def generate_phase_summary(client, phase_num, messages, scope, style_profile, phase_documents):
    """Generate a summary of the phase conversation adapted to user's communication style."""
    phase = PHASES[phase_num]
    style_guidance = get_summary_style_guidance(style_profile)
    
    # Build conversation text from messages
    conversation_text = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            conversation_text += f"User: {content}\n\n"
        elif role == "assistant":
            conversation_text += f"Claude: {content}\n\n"

    # Document summary text
    if phase_documents:
        doc_lines = []
        for d in phase_documents:
            doc_lines.append(f"- {d.get('path')} ({d.get('type')})")
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
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return None

def review_and_approve_summary(client, phase_num, initial_summary, scope, style_profile):
    """Handle user review and approval of phase summary with iteration."""
    phase = PHASES[phase_num]
    
    while True:
        print("\n" + "=" * 60)
        print(f"PHASE {phase_num} SUMMARY")
        print("=" * 60)
        print(initial_summary)
        print("=" * 60)
        print("\nDoes this accurately capture what we discussed?")
        print("Options: 'approve', 'request changes', or 'add details'")
        
        user_response = input("\nYour response: ").strip().lower()
        
        if user_response in ['approve', 'yes', 'y', 'ok', 'okay']:
            print("\n✓ Summary approved!")
            return initial_summary
        
        elif user_response in ['request changes', 'changes', 'change', 'modify']:
            print("\nWhat changes would you like? Please describe:")
            feedback = input("Feedback: ").strip()
            if not feedback:
                print("No feedback provided. Please try again.")
                continue
            
            # Regenerate with feedback
            prompt = f"""The user requested changes to this brief summary:

Original Summary:
{initial_summary}

User Feedback:
{feedback}

Phase: {phase['name']} - {phase['description']}
Project Scope: {scope}

Please revise the summary (5-10 bullet points max) incorporating the user's feedback while maintaining the concise, scannable format and communication style.

Revised Summary:"""
            
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                initial_summary = response.content[0].text
                print("\n✓ Summary updated. Reviewing again...")
                continue
            except Exception as e:
                print(f"Error updating summary: {str(e)}")
                print("Please try again.")
                continue
        
        elif user_response in ['add details', 'add', 'details', 'more']:
            print("\nWhat additional details would you like to include?")
            additional_info = input("Details: ").strip()
            if not additional_info:
                print("No details provided. Please try again.")
                continue
            
            # Regenerate with additional details
            prompt = f"""The user wants to add details to this brief summary:

Current Summary:
{initial_summary}

Additional Details to Include:
{additional_info}

Phase: {phase['name']} - {phase['description']}
Project Scope: {scope}

Please update the summary to incorporate these additional details. You may expand beyond 10 bullet points if needed to include the important details, but keep it scannable and focused on key takeaways.

Updated Summary:"""
            
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=1200,
                    messages=[{"role": "user", "content": prompt}]
                )
                initial_summary = response.content[0].text
                print("\n✓ Summary updated with additional details. Reviewing again...")
                continue
            except Exception as e:
                print(f"Error updating summary: {str(e)}")
                print("Please try again.")
                continue
        
        else:
            print("\nPlease respond with 'approve', 'request changes', or 'add details'.")
            continue

def detect_out_of_scope(scope, user_message, conversation_history):
    """Use Claude to detect if user message mentions something outside project scope."""
    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        detection_prompt = f"""Analyze this user message and determine if it mentions anything outside the project scope.

Project Scope: {scope}

User Message: {user_message}

If the message mentions anything outside the project scope, respond with:
OUT_OF_SCOPE: [brief description of what was mentioned]

If everything is within scope, respond with:
IN_SCOPE

Be conservative - only flag things that are clearly outside the stated scope."""

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=200,
            messages=[{"role": "user", "content": detection_prompt}]
        )
        
        result = response.content[0].text.strip()
        if result.startswith("OUT_OF_SCOPE:"):
            return result.replace("OUT_OF_SCOPE:", "").strip()
        return None
    except Exception as e:
        print(f"Warning: Could not detect out-of-scope items: {str(e)}")
        return None

def conduct_phase(client, phase_num, scope, conversation_file, flagged_items, style_profile, all_messages, phase_summaries):
    """Conduct a single phase of the discovery interview.

    Returns:
        tuple: (result, messages) where:
        - result: "save", "finish", or "next"
        - messages: list of conversation messages for this phase
    """
    phase = PHASES[phase_num]
    # Start this phase with full conversation history for continuity
    messages = list(all_messages or [])
    uploaded_docs = []
    mentioned_docs = []

    # Get base system prompt and format with scope if needed (Phase 2)
    base_system_prompt = phase["system_prompt"]
    if phase_num == 2:
        base_system_prompt = base_system_prompt.format(scope=scope)

    # Add system message for this phase, adapted by communication style
    style_guidance = build_style_guidance(style_profile)
    system_message = base_system_prompt + "\n\nCOMMUNICATION STYLE GUIDANCE:\n" + style_guidance

    # Add phase transition message
    transition = get_phase_transition_message(phase_num)
    print(transition)

    # Save phase transition to file
    with open(conversation_file, "a", encoding="utf-8") as f:
        f.write(transition + "\n")

    # Prompt for documents at the start of the phase
    print(
        "Before we begin, do you have any documents you'd like me to review? "
        "(process docs, screenshots, diagrams, etc.)"
    )
    doc_input = input(
        "Provide file paths separated by commas, or type 'none' to continue: "
    ).strip()
    if doc_input.lower() != "none" and doc_input:
        docs = load_documents_from_input(doc_input)
        for d in docs:
            uploaded_docs.append(d)
            # Add document content into the conversation context
            if d["type"] == "image":
                # For images, include a short note plus base64 content
                content_snippet = d["content"]
                doc_msg = (
                    f"[Image document uploaded: {d['path']}]\n"
                    f"Base64 content (truncated): {content_snippet[:4000]}"
                )
            else:
                # Text-like content
                content_snippet = d["content"]
                doc_msg = (
                    f"[Document uploaded: {d['path']} ({d['type']})]\n"
                    f"{content_snippet[:4000]}"
                )
            messages.append({"role": "user", "content": doc_msg})
            with open(conversation_file, "a", encoding="utf-8") as f:
                f.write(f"User uploaded document: {d['path']} ({d['type']})\n\n")

    # Add previous phase summaries as context for phases 2-4
    if phase_num > 1 and phase_summaries:
        summary_chunks = []
        for p in range(1, phase_num):
            key = str(p)
            if key in phase_summaries:
                prev_phase = PHASES[p]
                summary_chunks.append(
                    f"PHASE {p}: {prev_phase['name']}\n{phase_summaries[key]}"
                )
        if summary_chunks:
            summaries_text = "\n\n---\n\n".join(summary_chunks)
            context_msg = (
                "Previous phase summaries for context:\n\n" + summaries_text
            )
            messages.append({"role": "assistant", "content": context_msg})
            with open(conversation_file, "a", encoding="utf-8") as f:
                f.write("Previous phase summaries added for context.\n\n")

    # Get initial phase question from phase definition
    initial_question = phase.get("initial_question", "Let's continue our conversation.")
    
    print(f"Claude: {initial_question}\n")
    
    # Save initial question
    with open(conversation_file, "a", encoding="utf-8") as f:
        f.write(f"Claude: {initial_question}\n\n")
    
    # Add initial question to messages (as assistant message for context)
    messages.append({"role": "assistant", "content": initial_question})
    
    # Phase conversation loop
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue

        # Check for save/pause commands (save and exit without report)
        if user_input.lower() in ["save", "pause", "quit", "exit", "bye"]:
            print("\nSaving session and exiting...\n")
            return ("save", messages, uploaded_docs, mentioned_docs)
        
        # Check for finish/complete command (generate report)
        if user_input.lower() in ["finish", "complete"]:
            print("\nFinishing session and generating report...\n")
            return ("finish", messages, uploaded_docs, mentioned_docs)
        
        # Check for phase completion command
        if user_input.lower() in ['next phase', 'next', 'move on', 'continue']:
            # End-of-phase document reminder before moving on
            if mentioned_docs:
                # Specific reminders about mentioned documents
                if len(mentioned_docs) == 1:
                    print(
                        f"\nEarlier you mentioned: \"{mentioned_docs[0]}\"."
                    )
                else:
                    print("\nEarlier you mentioned these documents or files:")
                    for idx, desc in enumerate(mentioned_docs, start=1):
                        print(f"  {idx}. {desc}")
                print("Would you like to provide any of those now?")
                resp = input("Provide file paths or type 'none': ").strip()
                if resp and resp.lower() != "none":
                    docs = load_documents_from_input(resp)
                    for d in docs:
                        uploaded_docs.append(d)
                        if d["type"] == "image":
                            content_snippet = d["content"]
                            doc_msg = (
                                f"[Image document uploaded: {d['path']}]\n"
                                f"Base64 content (truncated): {content_snippet[:4000]}"
                            )
                        else:
                            content_snippet = d["content"]
                            doc_msg = (
                                f"[Document uploaded: {d['path']} ({d['type']})]\n"
                                f"{content_snippet[:4000]}"
                            )
                        messages.append({"role": "user", "content": doc_msg})
                        with open(conversation_file, "a", encoding="utf-8") as f:
                            f.write(
                                f"User uploaded document (end of phase): {d['path']} ({d['type']})\n\n"
                            )

            # General reminder for any other documents
            more_docs = input(
                "\nAny other documents you'd like me to review?\n"
                "Provide file paths or type 'none': "
            ).strip()
            if more_docs and more_docs.lower() != "none":
                docs = load_documents_from_input(more_docs)
                for d in docs:
                    uploaded_docs.append(d)
                    if d["type"] == "image":
                        content_snippet = d["content"]
                        doc_msg = (
                            f"[Image document uploaded: {d['path']}]\n"
                            f"Base64 content (truncated): {content_snippet[:4000]}"
                        )
                    else:
                        content_snippet = d["content"]
                        doc_msg = (
                            f"[Document uploaded: {d['path']} ({d['type']})]\n"
                            f"{content_snippet[:4000]}"
                        )
                    messages.append({"role": "user", "content": doc_msg})
                    with open(conversation_file, "a", encoding="utf-8") as f:
                        f.write(
                            f"User uploaded document (end of phase): {d['path']} ({d['type']})\n\n"
                        )

            print("\nMoving to next phase...\n")
            return ("next", messages, uploaded_docs, mentioned_docs)
        
        # Add user message
        messages.append({"role": "user", "content": user_input})

        # Detect if user mentioned having a document during the phase
        lower_input = user_input.lower()
        doc_phrases = [
            "i have a doc",
            "i have a document",
            "let me find that file",
            "i can send you",
            "there's a document",
            "there is a document",
            "i have a screenshot",
            "i'll send you",
            "i can share a file",
        ]
        if any(p in lower_input for p in doc_phrases):
            print(
                "Claude: No problem, we can come back to that at the end of this phase."
            )
            mentioned_docs.append(user_input)
        
        # Detect out-of-scope mentions
        out_of_scope = detect_out_of_scope(scope, user_input, messages)
        if out_of_scope:
            flagged_items.append(
                {
                    "phase": phase_num,
                    "mention": out_of_scope,
                    "user_input": user_input,
                }
            )
        
        try:
            # Get Claude's response with system message
            print("Claude: ", end="", flush=True)
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                system=system_message,
                messages=messages
            )
            
            claude_response = response.content[0].text
            
            print(claude_response)
            print()
            
            # Add Claude's response to conversation history
            messages.append({"role": "assistant", "content": claude_response})
            
            # Auto-save
            with open(conversation_file, "a", encoding="utf-8") as f:
                f.write(f"You: {user_input}\n\n")
                f.write(f"Claude: {claude_response}\n\n")
                f.write("-" * 60 + "\n\n")
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            print()
            
            with open(conversation_file, "a", encoding="utf-8") as f:
                f.write(f"You: {user_input}\n\n")
                f.write(f"{error_msg}\n\n")
                f.write("-" * 60 + "\n\n")

    # Normal phase completion (shouldn't reach here, but just in case)
    return ("next", messages, uploaded_docs, mentioned_docs)

def generate_final_document(scope, conversation_file, flagged_items, output_file, phase_summaries):
    """Generate a structured output document from the discovery session using already-approved phase summaries. No additional summary approval step - summaries were approved during each phase."""
    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Build summaries text from approved phase summaries
        summaries_text = ""
        for phase_num in sorted(phase_summaries.keys(), key=int):
            phase = PHASES[int(phase_num)]
            summary = phase_summaries[phase_num]
            summaries_text += f"\n{'=' * 60}\n"
            summaries_text += f"PHASE {phase_num}: {phase['name']} - {phase['description']}\n"
            summaries_text += f"{'=' * 60}\n\n"
            summaries_text += f"{summary}\n\n"

        # Prepare flagged items summary for analysis
        flagged_summary_lines = []
        for idx, item in enumerate(flagged_items, start=1):
            flagged_summary_lines.append(
                f"{idx}. Phase {item.get('phase')}: {item.get('mention')}\n"
                f"   Original user statement: {item.get('user_input')}"
            )
        flagged_summary = "\n".join(flagged_summary_lines) if flagged_summary_lines else "None"

        # Create prompt for document generation
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

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        document = response.content[0].text
        
        # Write the document
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("DISCOVERY SESSION REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(document)
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        return True
    except Exception as e:
        print(f"Error generating final document: {str(e)}")
        return False

def main():
    # Load environment variables
    load_dotenv()

    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found!")
        print("Please create a .env file with: ANTHROPIC_API_KEY=your-api-key")
        return

    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)

    # Check for saved session
    saved_state = load_session_state()
    resuming = False
    
    if saved_state:
        print("=" * 60)
        print("FOUND SAVED SESSION")
        print("=" * 60)
        print(f"Saved at: {saved_state.get('saved_at', 'Unknown')}")
        print(f"Project Scope: {saved_state.get('scope', 'Unknown')}")
        print(f"Current Phase: {saved_state.get('current_phase', 'Unknown')}")
        print()
        while True:
            choice = input("Resume saved session (r) or Start New (n)? ").strip().lower()
            if choice in ['r', 'resume']:
                resuming = True
                break
            elif choice in ['n', 'new']:
                delete_session_state()
                resuming = False
                break
            else:
                print("Please enter 'r' to resume or 'n' to start new.")
        print()

    # Load or create session data
    if resuming:
        # Load from saved state
        scope = saved_state.get("scope")
        style_profile = saved_state.get("style_profile")
        current_phase = saved_state.get("current_phase", 1)
        conversation_file = saved_state.get("conversation_file")
        output_file = saved_state.get("output_file")
        flagged_items = saved_state.get("flagged_items", [])
        all_messages = saved_state.get("all_messages", [])
        phase_summaries = saved_state.get("phase_summaries", {})
        
        print("=" * 60)
        print("RESUMING SESSION")
        print("=" * 60)
        print(f"Resuming from Phase {current_phase}")
        print(f"Conversation file: {conversation_file}")
        print("=" * 60)
        print()
    else:
        # Start new session
        scope = get_scope_input()
        style_profile = get_communication_style_assessment()
        current_phase = 1
        
        # Create timestamped filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        conversation_file = f"discovery_conversation_{timestamp}.txt"
        output_file = f"discovery_report_{timestamp}.md"

        # Initialize conversation file
        try:
            with open(conversation_file, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write(f"Discovery Session started on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Project Scope: {scope}\n")
                f.write("=" * 60 + "\n\n")
                f.write("COMMUNICATION STYLE PROFILE\n")
                f.write("-" * 60 + "\n")
                f.write(f"Primary Style: {style_profile['primary_style']}\n")
                f.write(f"Secondary Style: {style_profile['secondary_style']}\n")
                f.write("Scores (lower = stronger preference):\n")
                for style_name in STYLE_DIMENSIONS:
                    f.write(f"  - {style_name}: {style_profile['scores'][style_name]}\n")
                f.write("\nAssessment Responses (ranks per question; 1=most preferred, 4=least):\n")
                f.write("Option mapping: A=Detail-oriented, B=Big-picture, C=Story-driven, D=Problem-focused\n")
                for r in style_profile.get("responses", []):
                    q = r.get("question", "Question")
                    ranks = r.get("ranks", {})
                    f.write(f"  - {q}: A={ranks.get('A')} B={ranks.get('B')} C={ranks.get('C')} D={ranks.get('D')}\n")
                f.write("-" * 60 + "\n\n")
            print(f"\nConversation will be saved to: {conversation_file}")
            print(f"Final report will be saved to: {output_file}\n")
        except Exception as e:
            print(f"Error creating conversation file: {str(e)}")
            return

        flagged_items = []
        all_messages = []
        phase_summaries = {}

        # Welcome message
        print("=" * 60)
        print("DISCOVERY SESSION")
        print("=" * 60)
        print("We'll go through 4 phases:")
        for phase_num in range(1, 5):
            phase = PHASES[phase_num]
            print(f"  {phase_num}. {phase['name']} ({phase['description']})")
        print()
        print("Type 'next phase' or 'next' to move to the next phase when you're ready.")
        print("Type 'save', 'pause', 'quit', or 'exit' to save and exit without report.")
        print("Type 'finish' or 'complete' to finish and generate report.")
        print("=" * 60)
        print()

    # Conduct phases starting from current_phase
    should_generate_report = False
    # Track documents uploaded per phase (for summaries)
    phase_documents = {}
    for phase_num in range(current_phase, 5):
        try:
            result, messages, uploaded_docs, mentioned_docs = conduct_phase(
                client,
                phase_num,
                scope,
                conversation_file,
                flagged_items,
                style_profile,
                all_messages,
                phase_summaries,
            )

            # Update global conversation history for continuity
            all_messages = messages

            # Store uploaded documents for this phase
            if uploaded_docs:
                phase_documents[str(phase_num)] = uploaded_docs

            if result == "save":
                # Save state and exit without report
                save_session_state(
                    scope,
                    style_profile,
                    phase_num,
                    conversation_file,
                    output_file,
                    flagged_items,
                    phase_summaries,
                    all_messages,
                )
                print(f"\n✓ Session saved. You can resume later by running the script again.")
                print(f"✓ Conversation saved to: {conversation_file}")
                print("Thank you.")
                return

            elif result == "finish":
                # Generate summary for current phase if not already done, then finish
                if str(phase_num) not in phase_summaries:
                    print("\nGenerating summary for this phase...")
                    docs_for_phase = phase_documents.get(str(phase_num), [])
                    summary = generate_phase_summary(
                        client, phase_num, messages, scope, style_profile, docs_for_phase
                    )
                    if summary:
                        approved_summary = review_and_approve_summary(
                            client, phase_num, summary, scope, style_profile
                        )
                        phase_summaries[str(phase_num)] = approved_summary
                should_generate_report = True
                break

            elif result == "next":
                # Normal phase completion - generate and approve summary
                print("\nGenerating summary for this phase...")
                docs_for_phase = phase_documents.get(str(phase_num), [])
                summary = generate_phase_summary(
                    client, phase_num, messages, scope, style_profile, docs_for_phase
                )
                if summary:
                    approved_summary = review_and_approve_summary(
                        client, phase_num, summary, scope, style_profile
                    )
                    phase_summaries[str(phase_num)] = approved_summary

                    # Save summary to a separate file
                    summary_file = conversation_file.replace(
                        ".txt", f"_phase{phase_num}_summary.txt"
                    )
                    with open(summary_file, "w", encoding="utf-8") as f:
                        f.write("=" * 60 + "\n")
                        f.write(
                            f"PHASE {phase_num} SUMMARY: {PHASES[phase_num]['name']}\n"
                        )
                        f.write("=" * 60 + "\n\n")
                        f.write(approved_summary)
                        if docs_for_phase:
                            f.write("\n\nDocuments referenced in this phase:\n")
                            for d in docs_for_phase:
                                f.write(
                                    f"  - {d.get('path')} ({d.get('type')})\n"
                                )
                        f.write("\n\n" + "=" * 60 + "\n")
                    print(f"\n✓ Summary saved to: {summary_file}")

                # If we just completed phase 4, all phases are done - generate report
                if phase_num == 4:
                    should_generate_report = True
                    break
                # Save state after each phase completion (for phases 1-3)
                next_phase = phase_num + 1
                if next_phase <= 4:
                    save_session_state(
                        scope,
                        style_profile,
                        next_phase,
                        conversation_file,
                        output_file,
                        flagged_items,
                        phase_summaries,
                        all_messages,
                    )
                continue

        except KeyboardInterrupt:
            print("\n\nSession interrupted by user.")
            # Save state on interrupt
            save_session_state(
                scope,
                style_profile,
                phase_num,
                conversation_file,
                output_file,
                flagged_items,
                phase_summaries,
                all_messages,
            )
            print(f"\n✓ Session saved. You can resume later by running the script again.")
            print("Thank you.")
            return
        except Exception as e:
            print(f"\nError in phase {phase_num}: {str(e)}")
            print("Continuing to next phase...\n")
            continue

    # Generate final document using already-approved phase summaries (no second approval)
    if should_generate_report:
        print("\n" + "=" * 60)
        print("Generating final discovery report...")
        print("=" * 60)

        if generate_final_document(scope, conversation_file, flagged_items, output_file, phase_summaries):
            print(f"\n✓ Discovery session complete!")
            print(f"✓ Conversation saved to: {conversation_file}")
            print(f"✓ Final report saved to: {output_file}")
            # Delete session state after successful report generation
            delete_session_state()
        else:
            print(f"\n✓ Discovery session complete!")
            print(f"✓ Conversation saved to: {conversation_file}")
            print(f"⚠ Could not generate final report, but conversation is saved.")

        print("\nThank you for participating in the discovery session!")

if __name__ == "__main__":
    main()
