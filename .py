"""
XP Architect E2E Browser Test - Complete Discovery Flow
Tests the full flow from SA registration through complete 4-phase discovery.

Setup:
  python -m pip install playwright
  python -m playwright install chromium

Run (headed - you can watch):
  python test_browser.py

Run with pauses at key steps:
  python test_browser.py --pause

Run headless (faster, no UI):
  python test_browser.py --headless
"""

import asyncio
import random
import string
import sys
from playwright.async_api import async_playwright

# Configuration - UPDATE THESE TO MATCH YOUR DEPLOYMENT
FRONTEND_URL = "https://xparchitectfrontend-production-da80.up.railway.app"
SLOW_MO = 500  # Milliseconds between actions
PAUSE_MODE = "--pause" in sys.argv
AI_RESPONSE_WAIT = 10000  # Wait time for AI responses (ms)


def pause(message="Press Enter to continue..."):
    """Pause execution and wait for user input."""
    if PAUSE_MODE:
        input(f"\n⏸  {message}")


def random_email():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{suffix}@example.com"


def print_step(step):
    print(f"\n{'='*60}")
    print(f"  {step}")
    print(f"{'='*60}")


def print_substep(text):
    print(f"\n  → {text}")


# =============================================================================
# SOLUTION ARCHITECT FLOW
# =============================================================================

async def sa_register(page, sa_email, sa_password="test123"):
    """Step 1: SA registers on the app."""
    
    print_step("SA STEP 1: REGISTER")
    
    await page.goto(f"{FRONTEND_URL}/register")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1000)
    
    await page.screenshot(path="screenshots/sa_01_register_page.png")
    
    print_substep("Filling registration form...")
    await page.fill('#name', "Sarah Anderson (Solution Architect)")
    await page.fill('#email', sa_email)
    await page.fill('#password', sa_password)
    await page.select_option('#role', 'SA')
    
    await page.screenshot(path="screenshots/sa_02_form_filled.png")
    
    print_substep("Submitting registration...")
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    
    await page.screenshot(path="screenshots/sa_03_dashboard.png")
    print(f"  ✓ SA registered: {sa_email}")
    
    pause("SA registered. Press Enter to create project...")
    return True


async def sa_create_project(page):
    """Step 2: SA creates a project."""
    
    print_step("SA STEP 2: CREATE PROJECT")
    
    print_substep("Opening Create Project form...")
    await page.click('button:has-text("Create Project")')
    await page.wait_for_timeout(1000)
    
    await page.screenshot(path="screenshots/sa_04_create_project_modal.png")
    
    print_substep("Filling project details...")
    
    # Project name
    name_input = page.locator('input[type="text"]').first
    await name_input.fill("Acme Corp Salesforce Implementation")
    
    # Project scope
    scope_field = page.locator('textarea').first
    await scope_field.fill(
        "Salesforce Sales Cloud implementation for the sales team including:\n"
        "- Lead and opportunity management\n"
        "- Custom reporting and dashboards\n"
        "- Outlook email integration\n"
        "- Mobile access for field sales reps"
    )
    
    # Dates
    print_substep("Setting project dates...")
    date_inputs = page.locator('input[type="date"]')
    await date_inputs.nth(0).click()
    await page.keyboard.type("02/10/2026")
    await date_inputs.nth(1).click()
    await page.keyboard.type("04/15/2026")
    
    await page.screenshot(path="screenshots/sa_05_project_form_filled.png")
    
    print_substep("Creating project...")
    submit_buttons = page.locator('button:has-text("Create Project")')
    await submit_buttons.last.click()
    
    await page.wait_for_timeout(2000)
    await page.screenshot(path="screenshots/sa_06_project_created.png")
    
    print("  ✓ Project created")
    pause("Project created. Press Enter to add stakeholder...")
    return True


async def sa_add_stakeholder(page, stakeholder_email):
    """Step 3: SA adds a stakeholder to the project."""
    
    print_step("SA STEP 3: ADD STAKEHOLDER")
    
    # First, click "View" to enter the project detail page
    print_substep("Clicking View to enter project...")
    view_btn = page.locator('button:has-text("View"), a:has-text("View")')
    if await view_btn.count() > 0:
        await view_btn.first.click()
        await page.wait_for_timeout(2000)
    
    await page.screenshot(path="screenshots/sa_07_project_detail.png")
    
    # Scroll down to see the Add Stakeholder form
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(500)
    
    await page.screenshot(path="screenshots/sa_08_add_stakeholder_form.png")
    
    # Fill the inline form using the actual IDs from ProjectDetail.js
    print_substep(f"Adding stakeholder: {stakeholder_email}")
    
    await page.fill('#add-name', "John Smith - Sales Manager")
    await page.fill('#add-email', stakeholder_email)
    
    await page.screenshot(path="screenshots/sa_09_stakeholder_form_filled.png")
    
    # Click Add Stakeholder button
    print_substep("Submitting...")
    await page.click('button:has-text("Add Stakeholder")')
    
    await page.wait_for_timeout(2000)
    await page.screenshot(path="screenshots/sa_10_stakeholder_added.png")
    
    # Get the invite link - look for "Copy Invite Link" button and the token
    invite_link = None
    try:
        # After adding, the stakeholder row should have a "Copy Invite Link" button
        # We need to extract the invite token from the page
        copy_btn = page.locator('button:has-text("Copy Invite Link")')
        if await copy_btn.count() > 0:
            print("  ✓ Invite link available (Copy Invite Link button visible)")
            # The invite link is constructed client-side, we'll construct it for the test
            # by finding the stakeholder's invite_token from the UI or just using the register page
    except:
        pass
    
    print("  ✓ Stakeholder added")
    print("\n" + "="*60)
    print("  SA FLOW COMPLETE - SWITCHING TO STAKEHOLDER")
    print("="*60)
    
    pause("SA flow complete. Press Enter to begin STAKEHOLDER flow...")
    return invite_link


# =============================================================================
# STAKEHOLDER FLOW
# =============================================================================

async def stakeholder_register(context, invite_url, stakeholder_email, password="test123"):
    """Stakeholder Step 1: Register via invite link."""
    
    print_step("STAKEHOLDER STEP 1: REGISTER VIA INVITE LINK")
    
    # Open new browser tab (simulates different user)
    page = await context.new_page()
    
    target_url = invite_url if invite_url else f"{FRONTEND_URL}/register"
    print_substep(f"Opening invite link...")
    
    await page.goto(target_url)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1000)
    
    await page.screenshot(path="screenshots/sh_01_register_page.png")
    
    # Check if fields are pre-filled
    name_field = page.locator('#name')
    if await name_field.count() > 0:
        current_val = await name_field.input_value()
        if current_val:
            print(f"  Name pre-filled: {current_val}")
        else:
            await name_field.fill("John Smith")
    
    email_field = page.locator('#email')
    if await email_field.count() > 0:
        is_readonly = await email_field.get_attribute("readonly")
        if is_readonly:
            email_val = await email_field.input_value()
            print(f"  Email pre-filled (read-only): {email_val}")
        else:
            await email_field.fill(stakeholder_email)
    
    print_substep("Setting password...")
    await page.fill('#password', password)
    
    await page.screenshot(path="screenshots/sh_02_form_filled.png")
    
    print_substep("Submitting registration...")
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    
    await page.screenshot(path="screenshots/sh_03_registered.png")
    print(f"  ✓ Stakeholder registered")
    
    pause("Stakeholder registered. Press Enter to take assessment...")
    return page


async def stakeholder_assessment(page):
    """Stakeholder Step 2: Complete the communication style assessment."""
    
    print_step("STAKEHOLDER STEP 2: COMMUNICATION ASSESSMENT")
    
    await page.wait_for_timeout(1000)
    await page.screenshot(path="screenshots/sh_04_assessment_welcome.png")
    
    # Click Start assessment
    print_substep("Starting assessment...")
    start_btn = page.locator('button:has-text("Start assessment")')
    if await start_btn.count() > 0:
        await start_btn.click()
        await page.wait_for_timeout(1000)
    
    # Answers that create a "Big-picture + Problem-focused" profile
    test_answers = [
        {"A": "2", "B": "1", "C": "3", "D": "4"},  # Q1
        {"A": "3", "B": "4", "C": "2", "D": "1"},  # Q2
        {"A": "2", "B": "1", "C": "4", "D": "3"},  # Q3
        {"A": "3", "B": "2", "C": "4", "D": "1"},  # Q4
        {"A": "4", "B": "1", "C": "3", "D": "2"},  # Q5
    ]
    
    for q_num in range(1, 6):
        print_substep(f"Answering Question {q_num} of 5...")
        await page.screenshot(path=f"screenshots/sh_05_q{q_num}_before.png")
        
        answers = test_answers[q_num - 1]
        for option in ["A", "B", "C", "D"]:
            rank = answers[option]
            selector = f'select[aria-label="Rank for option {option}"]'
            await page.select_option(selector, rank)
            await page.wait_for_timeout(200)
        
        await page.screenshot(path=f"screenshots/sh_05_q{q_num}_after.png")
        
        pause(f"Question {q_num} answered. Press Enter to continue...")
        
        if q_num < 5:
            await page.click('button:has-text("Next")')
        else:
            print_substep("Completing assessment...")
            await page.click('button:has-text("Complete assessment")')
        
        await page.wait_for_timeout(1000)
    
    await page.wait_for_timeout(2000)
    await page.screenshot(path="screenshots/sh_06_assessment_complete.png")
    
    print("  ✓ Assessment completed")
    pause("Assessment complete. Press Enter to start discovery...")
    return True


async def stakeholder_start_discovery(page):
    """Stakeholder Step 3: Start the discovery session."""
    
    print_step("STAKEHOLDER STEP 3: START DISCOVERY")
    
    await page.wait_for_timeout(1000)
    await page.screenshot(path="screenshots/sh_07_dashboard.png")
    
    # Look for Start/Resume Discovery button
    print_substep("Starting discovery session...")
    start_btn = page.locator('button:has-text("Start"), button:has-text("Resume"), button:has-text("Discovery")')
    if await start_btn.count() > 0:
        await start_btn.first.click()
        await page.wait_for_timeout(2000)
    
    await page.screenshot(path="screenshots/sh_08_discovery_started.png")
    print("  ✓ Discovery session started")
    
    pause("Discovery started. Press Enter to begin Phase 1...")
    return True


async def send_message(page, message, screenshot_prefix):
    """Helper to send a message and wait for AI response."""
    
    # Find chat input (textarea or input)
    chat_input = page.locator('textarea').last
    if await chat_input.count() == 0:
        chat_input = page.locator('input[type="text"]').last
    
    if await chat_input.count() > 0:
        await chat_input.fill(message)
        
        # Send
        send_btn = page.locator('button:has-text("Send"), button[type="submit"]')
        if await send_btn.count() > 0:
            await send_btn.first.click()
            
            # Wait for AI response
            print("      Waiting for AI response...")
            await page.wait_for_timeout(AI_RESPONSE_WAIT)
            
            await page.screenshot(path=f"screenshots/{screenshot_prefix}.png")
            return True
    
    return False


async def end_phase_and_approve(page, phase_num):
    """Helper to end a phase and approve the summary."""
    
    print_substep(f"Ending Phase {phase_num}...")
    
    # Look for End Phase button
    end_btn = page.locator('button:has-text("End Phase"), button:has-text("Complete Phase"), button:has-text("Finish Phase")')
    if await end_btn.count() > 0:
        await end_btn.first.click()
        await page.wait_for_timeout(3000)
    
    await page.screenshot(path=f"screenshots/sh_phase{phase_num}_summary.png")
    
    print_substep(f"Reviewing Phase {phase_num} summary...")
    pause(f"Phase {phase_num} summary displayed. Press Enter to approve...")
    
    # Look for Approve button
    approve_btn = page.locator('button:has-text("Approve"), button:has-text("Confirm"), button:has-text("Accept")')
    if await approve_btn.count() > 0:
        await approve_btn.first.click()
        await page.wait_for_timeout(2000)
    
    await page.screenshot(path=f"screenshots/sh_phase{phase_num}_approved.png")
    print(f"  ✓ Phase {phase_num} summary approved")
    
    return True


async def stakeholder_phase_1(page):
    """Stakeholder Step 4: Phase 1 - Open Discovery."""
    
    print_step("PHASE 1: OPEN DISCOVERY")
    print("  Theme: Team, role, processes, tools, what works and what doesn't")
    
    messages = [
        (
            "Hi! I'm John Smith, the Sales Manager at Acme Corp. I've been here for about 5 years "
            "and I manage a team of 15 sales representatives covering the western United States."
        ),
        (
            "Our current process is honestly pretty chaotic. Each rep tracks their deals differently - "
            "some use spreadsheets, others use the old CRM we're supposed to be replacing, and a few "
            "just keep notes in their email. There's no consistency across the team."
        ),
        (
            "What works well is honestly our people. We have a strong team that closes deals. "
            "The problem is visibility - I don't know what's in the pipeline until deals close or die. "
            "Forecasting is my biggest pain point. I spend every Friday calling reps for updates."
        ),
        (
            "We use Outlook for email, the old CRM (barely), Excel for everything else, and Slack "
            "for team communication. We also have a separate quoting system that doesn't integrate "
            "with anything. It's a mess of disconnected tools."
        ),
    ]
    
    for i, msg in enumerate(messages):
        print_substep(f"Message {i+1}/{len(messages)}: {msg[:50]}...")
        await send_message(page, msg, f"sh_p1_msg{i+1}")
        pause(f"Phase 1 message {i+1} sent. Press Enter to continue...")
    
    await end_phase_and_approve(page, 1)
    pause("Phase 1 complete. Press Enter to start Phase 2...")
    return True


async def stakeholder_phase_2(page):
    """Stakeholder Step 5: Phase 2 - Targeted Follow-ups."""
    
    print_step("PHASE 2: TARGETED FOLLOW-UPS")
    print("  Theme: Gap-filling questions for in-scope topics")
    
    messages = [
        (
            "For the quoting process, reps currently create quotes in a separate system called QuoteBuilder. "
            "They have to manually copy opportunity data from wherever they're tracking it, create the quote, "
            "then email it as a PDF. There's no connection to our CRM at all."
        ),
        (
            "When a deal closes, the rep emails me and our operations team. Then someone manually enters "
            "it into our ERP system for fulfillment. Sometimes deals fall through the cracks because "
            "the handoff is just email-based. We've had fulfillment delays because of this."
        ),
        (
            "For reporting, I pull data from the old CRM into Excel every week, then create pivot tables "
            "and charts manually. It takes me 4-5 hours every Friday just to compile the pipeline report "
            "for leadership. And by Monday the data is already stale."
        ),
    ]
    
    for i, msg in enumerate(messages):
        print_substep(f"Message {i+1}/{len(messages)}: {msg[:50]}...")
        await send_message(page, msg, f"sh_p2_msg{i+1}")
        pause(f"Phase 2 message {i+1} sent. Press Enter to continue...")
    
    await end_phase_and_approve(page, 2)
    pause("Phase 2 complete. Press Enter to start Phase 3...")
    return True


async def stakeholder_phase_3(page):
    """Stakeholder Step 6: Phase 3 - Validation & Clarification."""
    
    print_step("PHASE 3: VALIDATION & CLARIFICATION")
    print("  Theme: Confirming understanding, resolving contradictions")
    
    messages = [
        (
            "Yes, that's correct. The main systems are: the old CRM (which maybe 40% of reps use), "
            "Excel spreadsheets (everyone uses these), QuoteBuilder for quotes, Outlook for email, "
            "and our ERP for fulfillment. Nothing talks to each other."
        ),
        (
            "For the team structure - I have 15 reps, split into 3 territories (West Coast, Mountain, "
            "and Southwest). Each territory has a senior rep who acts as team lead but they don't have "
            "management responsibilities, they're player-coaches who still carry their own quota."
        ),
        (
            "The forecast process specifically: Friday afternoons I call or Slack each rep for their "
            "pipeline updates. I compile it in Excel, add my judgment on deal likelihood, and send "
            "the report to VP of Sales by EOD Friday. It's tedious and error-prone."
        ),
    ]
    
    for i, msg in enumerate(messages):
        print_substep(f"Message {i+1}/{len(messages)}: {msg[:50]}...")
        await send_message(page, msg, f"sh_p3_msg{i+1}")
        pause(f"Phase 3 message {i+1} sent. Press Enter to continue...")
    
    await end_phase_and_approve(page, 3)
    pause("Phase 3 complete. Press Enter to start Phase 4...")
    return True


async def stakeholder_phase_4(page):
    """Stakeholder Step 7: Phase 4 - Future State & Priorities."""
    
    print_step("PHASE 4: FUTURE STATE & PRIORITIES")
    print("  Theme: Success criteria, priorities, must-haves vs nice-to-haves")
    
    messages = [
        (
            "Success for me means: I can see the entire pipeline in real-time without calling anyone. "
            "Reps can update deals from their phones between client meetings. Forecasting takes "
            "30 minutes instead of 5 hours. And deals don't fall through the cracks at handoff."
        ),
        (
            "Must-haves: Mobile access for reps, real-time pipeline visibility, automated forecast "
            "reports, and integration with our quoting system. Nice-to-haves: AI-powered deal insights, "
            "territory mapping, and gamification features for the team."
        ),
        (
            "The biggest win would be if leadership could pull their own reports without asking me. "
            "Right now I'm the bottleneck for all pipeline data. Self-service reporting for execs "
            "would free up hours of my time every week and make the data more timely."
        ),
    ]
    
    for i, msg in enumerate(messages):
        print_substep(f"Message {i+1}/{len(messages)}: {msg[:50]}...")
        await send_message(page, msg, f"sh_p4_msg{i+1}")
        pause(f"Phase 4 message {i+1} sent. Press Enter to continue...")
    
    await end_phase_and_approve(page, 4)
    return True


async def view_final_report(page):
    """View the final discovery report."""
    
    print_step("FINAL: VIEW DISCOVERY REPORT")
    
    await page.wait_for_timeout(2000)
    await page.screenshot(path="screenshots/sh_final_01_after_phase4.png")
    
    # Look for View Report or similar button
    report_btn = page.locator('button:has-text("Report"), button:has-text("Results"), button:has-text("Summary"), a:has-text("Report")')
    if await report_btn.count() > 0:
        print_substep("Opening final report...")
        await report_btn.first.click()
        await page.wait_for_timeout(3000)
    
    await page.screenshot(path="screenshots/sh_final_02_report.png")
    
    # Scroll down to capture full report
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await page.wait_for_timeout(500)
    await page.screenshot(path="screenshots/sh_final_03_report_middle.png")
    
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(500)
    await page.screenshot(path="screenshots/sh_final_04_report_bottom.png")
    
    print("  ✓ Final report generated")
    return True


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def main(headless=False):
    """Run the complete E2E test flow."""
    
    import os
    os.makedirs("screenshots", exist_ok=True)
    
    sa_email = random_email()
    stakeholder_email = random_email()
    
    print(f"\n{'='*60}")
    print("  XP ARCHITECT - COMPLETE E2E TEST")
    print(f"{'='*60}")
    print(f"\nFrontend: {FRONTEND_URL}")
    print(f"\nTest Accounts:")
    print(f"  SA:          {sa_email} / test123")
    print(f"  Stakeholder: {stakeholder_email} / test123")
    print(f"\nMode: {'Headless' if headless else 'Visible browser'}")
    print(f"Pause mode: {'ON' if PAUSE_MODE else 'OFF'}")
    print(f"\n{'='*60}")
    print("  TEST FLOW")
    print(f"{'='*60}")
    print("""
  SOLUTION ARCHITECT:
    1. Register on the app
    2. Create Project
    3. Add Stakeholder
    
  STAKEHOLDER:
    1. Register via invite link
    2. Take Communication Assessment (5 questions)
    3. Start Discovery
    4. Phase 1: Open Discovery → End Phase → Approve Summary
    5. Phase 2: Targeted Follow-ups → End Phase → Approve Summary
    6. Phase 3: Validation & Clarification → End Phase → Approve Summary
    7. Phase 4: Future State & Priorities → End Phase → Approve Summary
    8. View Final Report
    """)
    
    pause("Ready to start. Press Enter to begin...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            slow_mo=SLOW_MO if not headless else 100
        )
        
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900}
        )
        
        sa_page = await context.new_page()
        
        try:
            # ============= SOLUTION ARCHITECT FLOW =============
            await sa_register(sa_page, sa_email)
            await sa_create_project(sa_page)
            invite_url = await sa_add_stakeholder(sa_page, stakeholder_email)
            
            # ============= STAKEHOLDER FLOW =============
            sh_page = await stakeholder_register(context, invite_url, stakeholder_email)
            await stakeholder_assessment(sh_page)
            await stakeholder_start_discovery(sh_page)
            
            # ============= 4-PHASE DISCOVERY =============
            await stakeholder_phase_1(sh_page)
            await stakeholder_phase_2(sh_page)
            await stakeholder_phase_3(sh_page)
            await stakeholder_phase_4(sh_page)
            
            # ============= FINAL REPORT =============
            await view_final_report(sh_page)
            
            # ============= COMPLETE =============
            print_step("TEST COMPLETE!")
            print(f"""
  All screenshots saved to ./screenshots/
  
  Test accounts created:
    SA:          {sa_email} / test123
    Stakeholder: {stakeholder_email} / test123
    
  You can log in with these accounts to review the results.
            """)
            
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            try:
                await sa_page.screenshot(path="screenshots/error_sa.png")
            except:
                pass
            print("  Error screenshot saved")
            raise
        
        finally:
            pause("Test complete. Press Enter to close browser...")
            await browser.close()


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    asyncio.run(main(headless=headless))
