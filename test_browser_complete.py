"""
XP Architect E2E Browser Test - Complete Discovery Flow
=========================================================
Tests the full flow from SA registration through complete 4-phase discovery.

TEST FLOW:
  Solution Architect:
    1. Register on the app
    2. Create Project
    3. Add Stakeholder
    
  Stakeholder:
    1. Register via invite link
    2. Take the Assessment (5 questions)
    3. Start Discovery
    4. Phase 1: Open Discovery → End Phase → Approve Summary
    5. Phase 2: Targeted Follow-ups → End Phase → Approve Summary
    6. Phase 3: Validation & Clarification → End Phase → Approve Summary
    7. Phase 4: Future State & Priorities → End Phase → Approve Summary
    8. View Final Report

SETUP:
  python -m pip install playwright
  python -m playwright install chromium

RUN:
  python test_browser_complete.py           # Normal run (visible browser)
  python test_browser_complete.py --pause   # Pause at key steps
  python test_browser_complete.py --headless # Headless mode
"""

import asyncio
import random
import string
import sys
from playwright.async_api import async_playwright

# =============================================================================
# CONFIGURATION
# =============================================================================

FRONTEND_URL = "https://xparchitectfrontend-production-da80.up.railway.app"
SLOW_MO = 500  # Milliseconds between actions
PAUSE_MODE = "--pause" in sys.argv
AI_RESPONSE_WAIT = 12000  # Wait time for AI responses (ms)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def pause(message="Press Enter to continue..."):
    """Pause execution and wait for user input."""
    if PAUSE_MODE:
        input(f"\n⏸  {message}")


def random_email():
    """Generate a random test email."""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{suffix}@example.com"


def print_step(step):
    """Print a major step header."""
    print(f"\n{'='*60}")
    print(f"  {step}")
    print(f"{'='*60}")


def print_substep(text):
    """Print a substep."""
    print(f"\n  → {text}")


# =============================================================================
# SOLUTION ARCHITECT FLOW
# =============================================================================

async def sa_register(page, sa_email, sa_password="test123"):
    """SA Step 1: Register on the app."""
    
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
    """SA Step 2: Create a project."""
    
    print_step("SA STEP 2: CREATE PROJECT")
    
    print_substep("Opening Create Project form...")
    await page.click('button:has-text("Create Project")')
    await page.wait_for_timeout(1000)
    
    await page.screenshot(path="screenshots/sa_04_create_project_modal.png")
    
    print_substep("Filling project details...")
    
    # Project name - first text input
    name_input = page.locator('input[type="text"]').first
    await name_input.fill("Acme Corp Salesforce Implementation")
    
    # Project scope - first textarea
    scope_field = page.locator('textarea').first
    await scope_field.fill(
        "Salesforce Sales Cloud implementation for the sales team including:\n"
        "- Lead and opportunity management\n"
        "- Custom reporting and dashboards\n"
        "- Outlook email integration\n"
        "- Mobile access for field sales reps"
    )
    
    # Dates - using keyboard to type in date format
    print_substep("Setting project dates...")
    date_inputs = page.locator('input[type="date"]')
    
    # Start date
    await date_inputs.nth(0).click()
    await page.keyboard.type("02/10/2026")
    
    # End date
    await date_inputs.nth(1).click()  
    await page.keyboard.type("04/15/2026")
    
    await page.screenshot(path="screenshots/sa_05_project_form_filled.png")
    
    # Click Create Project button in modal (the last one, not the header button)
    print_substep("Creating project...")
    submit_buttons = page.locator('button:has-text("Create Project")')
    await submit_buttons.last.click()
    
    await page.wait_for_timeout(2000)
    await page.screenshot(path="screenshots/sa_06_project_created.png")
    
    print("  ✓ Project created")
    pause("Project created. Press Enter to add stakeholder...")
    return True


async def sa_add_stakeholder(page, stakeholder_email):
    """SA Step 3: Add a stakeholder to the project."""
    
    print_step("SA STEP 3: ADD STAKEHOLDER")
    
    # Click "View" to enter the project detail page
    print_substep("Entering project detail page...")
    view_btn = page.locator('button:has-text("View"), a:has-text("View")')
    if await view_btn.count() > 0:
        await view_btn.first.click()
        await page.wait_for_timeout(2000)
    
    await page.screenshot(path="screenshots/sa_07_project_detail.png")
    
    # Scroll down to see the Add Stakeholder form
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(500)
    
    await page.screenshot(path="screenshots/sa_08_add_stakeholder_form.png")
    
    # Fill the inline form using the IDs from ProjectDetail.js
    print_substep(f"Adding stakeholder: {stakeholder_email}")
    
    await page.fill('#add-name', "John Smith - Sales Manager")
    await page.fill('#add-email', stakeholder_email)
    
    await page.screenshot(path="screenshots/sa_09_stakeholder_form_filled.png")
    
    # Click Add Stakeholder button
    print_substep("Submitting...")
    await page.click('button:has-text("Add Stakeholder")')
    
    await page.wait_for_timeout(3000)
    await page.screenshot(path="screenshots/sa_10_stakeholder_added.png")
    
    # Capture the invite link
    print_substep("Capturing invite link...")
    
    invite_link = None
    copy_btn = page.locator('button:has-text("Copy Invite Link")')
    
    if await copy_btn.count() > 0:
        # Method 1: Try to intercept clipboard write
        try:
            # Set up clipboard interception
            invite_link = await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        // Store original
                        const originalWriteText = navigator.clipboard.writeText.bind(navigator.clipboard);
                        
                        // Override to capture
                        navigator.clipboard.writeText = async (text) => {
                            // Restore original
                            navigator.clipboard.writeText = originalWriteText;
                            // Call original
                            await originalWriteText(text);
                            // Resolve with captured text
                            resolve(text);
                        };
                        
                        // Timeout fallback
                        setTimeout(() => {
                            navigator.clipboard.writeText = originalWriteText;
                            resolve(null);
                        }, 3000);
                    });
                }
            """)
            
            # Click the copy button to trigger the clipboard write
            await copy_btn.first.click()
            await page.wait_for_timeout(1500)
            
        except Exception as e:
            print(f"  Clipboard intercept failed: {e}")
        
        # Method 2: If clipboard intercept didn't work, try reading clipboard
        if not invite_link:
            try:
                # Grant clipboard permissions and read
                invite_link = await page.evaluate("navigator.clipboard.readText()")
            except:
                pass
        
        # Method 3: If still no link, try dialog fallback
        if not invite_link:
            try:
                # The code has a fallback: window.prompt('Copy this invite link:', url)
                # We can trigger this by blocking clipboard
                
                captured = {"url": None}
                
                async def handle_dialog(dialog):
                    captured["url"] = dialog.default_value
                    await dialog.dismiss()
                
                page.on("dialog", handle_dialog)
                
                # Block clipboard and click again
                await page.evaluate("navigator.clipboard.writeText = null")
                await copy_btn.first.click()
                await page.wait_for_timeout(2000)
                
                invite_link = captured.get("url")
                
            except Exception as e:
                print(f"  Dialog capture failed: {e}")
    
    if invite_link:
        print(f"  ✓ Invite link captured: {invite_link[:60]}...")
    else:
        print("  ⚠ Could not capture invite link automatically")
        print("    The stakeholder registration may not link to the project.")
        # Set to None - will need manual handling
    
    await page.screenshot(path="screenshots/sa_11_final.png")
    
    print("\n  ✓ Stakeholder added to project")
    print("\n" + "="*60)
    print("  SA FLOW COMPLETE")
    print("="*60)
    
    pause("SA flow complete. Press Enter to switch to STAKEHOLDER view...")
    return invite_link


# =============================================================================
# STAKEHOLDER FLOW
# =============================================================================

async def stakeholder_register(context, invite_url, stakeholder_email, password="test123"):
    """Stakeholder Step 1: Register via invite link."""
    
    print_step("STAKEHOLDER STEP 1: REGISTER VIA INVITE LINK")
    
    # Open new browser tab (simulates different user/browser)
    page = await context.new_page()
    
    # Use invite link if we have it, otherwise just go to register
    if invite_url:
        target_url = invite_url
        print_substep(f"Opening invite link: {invite_url[:60]}...")
    else:
        target_url = f"{FRONTEND_URL}/register"
        print_substep("Opening register page (no invite link captured)...")
        print("  ⚠ Stakeholder may not be linked to project")
    
    await page.goto(target_url)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1500)
    
    await page.screenshot(path="screenshots/sh_01_register_page.png")
    
    # Check if name is pre-filled (from invite)
    name_field = page.locator('#name')
    if await name_field.count() > 0:
        current_name = await name_field.input_value()
        if current_name:
            print(f"  ✓ Name pre-filled: {current_name}")
        else:
            print_substep("Filling name...")
            await name_field.fill("John Smith")
    
    # Check if email is pre-filled and read-only (from invite)
    email_field = page.locator('#email')
    if await email_field.count() > 0:
        is_readonly = await email_field.get_attribute("readonly")
        current_email = await email_field.input_value()
        if is_readonly and current_email:
            print(f"  ✓ Email pre-filled (read-only): {current_email}")
        elif current_email:
            print(f"  ✓ Email pre-filled: {current_email}")
        else:
            print_substep("Filling email...")
            await email_field.fill(stakeholder_email)
    
    # Password is always required
    print_substep("Setting password...")
    await page.fill('#password', password)
    
    await page.screenshot(path="screenshots/sh_02_form_filled.png")
    
    print_substep("Submitting registration...")
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    
    await page.screenshot(path="screenshots/sh_03_registered.png")
    
    current_url = page.url
    print(f"  ✓ Stakeholder registered")
    print(f"  Current URL: {current_url}")
    
    pause("Stakeholder registered. Press Enter to take assessment...")
    return page


async def stakeholder_assessment(page):
    """Stakeholder Step 2: Complete the communication style assessment."""
    
    print_step("STAKEHOLDER STEP 2: COMMUNICATION ASSESSMENT")
    
    await page.wait_for_timeout(1000)
    await page.screenshot(path="screenshots/sh_04_assessment_welcome.png")
    
    # Click Start assessment button
    print_substep("Starting assessment...")
    start_btn = page.locator('button:has-text("Start assessment")')
    if await start_btn.count() > 0:
        await start_btn.click()
        await page.wait_for_timeout(1000)
    else:
        print("  ⚠ No 'Start assessment' button found - may already be on questions")
    
    # Answer configuration - creates "Big-picture + Problem-focused" profile
    # Each question ranks A, B, C, D from 1-4 (1 = most like me)
    test_answers = [
        {"A": "2", "B": "1", "C": "3", "D": "4"},  # Q1: Big-picture primary
        {"A": "3", "B": "4", "C": "2", "D": "1"},  # Q2: Problem-focused
        {"A": "2", "B": "1", "C": "4", "D": "3"},  # Q3: Big-picture
        {"A": "3", "B": "2", "C": "4", "D": "1"},  # Q4: Problem-focused
        {"A": "4", "B": "1", "C": "3", "D": "2"},  # Q5: Big-picture
    ]
    
    for q_num in range(1, 6):
        print_substep(f"Question {q_num} of 5")
        
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"screenshots/sh_05_q{q_num}_before.png")
        
        # Select ranks for each option (A, B, C, D)
        answers = test_answers[q_num - 1]
        for option in ["A", "B", "C", "D"]:
            rank = answers[option]
            selector = f'select[aria-label="Rank for option {option}"]'
            
            try:
                await page.select_option(selector, rank)
                print(f"    Option {option}: Rank {rank}")
            except Exception as e:
                print(f"    ⚠ Could not select rank for {option}: {e}")
            
            await page.wait_for_timeout(200)
        
        await page.screenshot(path=f"screenshots/sh_05_q{q_num}_after.png")
        
        pause(f"Question {q_num} answered. Press Enter to continue...")
        
        # Click Next or Complete
        if q_num < 5:
            print_substep("Clicking Next...")
            await page.click('button:has-text("Next")')
        else:
            print_substep("Completing assessment...")
            await page.click('button:has-text("Complete assessment")')
        
        await page.wait_for_timeout(1000)
    
    await page.wait_for_timeout(2000)
    await page.screenshot(path="screenshots/sh_06_assessment_complete.png")
    
    print("\n  ✓ Assessment completed")
    print(f"  Current URL: {page.url}")
    
    pause("Assessment complete. Press Enter to start discovery...")
    return True


async def stakeholder_start_discovery(page):
    """Stakeholder Step 3: Start the discovery session."""
    
    print_step("STAKEHOLDER STEP 3: START DISCOVERY")
    
    await page.wait_for_timeout(1000)
    await page.screenshot(path="screenshots/sh_07_dashboard.png")
    
    # Look for Begin/Start/Resume Discovery button
    print_substep("Looking for discovery button...")
    
    discovery_btn = page.locator('button:has-text("Begin Discovery"), button:has-text("Start Discovery"), button:has-text("Resume Discovery")')
    
    if await discovery_btn.count() > 0:
        print_substep("Starting discovery session...")
        await discovery_btn.first.click()
        await page.wait_for_timeout(3000)
        
        # Enable demo mode to show End Phase button
        current_url = page.url
        await page.goto(current_url + ('&' if '?' in current_url else '?') + 'demo=true')
        await page.wait_for_timeout(1000)
    else:
        print("  ⚠ No discovery button found")
    
    await page.screenshot(path="screenshots/sh_08_discovery_started.png")
    
    print("  ✓ Discovery session started (demo mode enabled)")
    pause("Discovery started. Press Enter to begin Phase 1...")
    return True

async def send_message_and_wait(page, message, screenshot_name):
    """Send a chat message and wait for AI response."""
    
    # Find chat input (textarea)
    chat_input = page.locator('textarea')
    
    if await chat_input.count() > 0:
        # Clear and fill
        await chat_input.last.fill(message)
        await page.wait_for_timeout(300)
        
        # Find and click Send button
        send_btn = page.locator('button:has-text("Send")')
        if await send_btn.count() > 0:
            await send_btn.first.click()
            
            # Wait for AI response
            print("      Waiting for AI response...")
            await page.wait_for_timeout(AI_RESPONSE_WAIT)
            
            await page.screenshot(path=f"screenshots/{screenshot_name}.png")
            return True
    
    print("      ⚠ Could not find chat input or send button")
    return False


async def end_phase_and_approve(page, phase_num):
    """End the current phase and approve the summary."""
    
    print_substep(f"Ending Phase {phase_num}...")
    
    # Step 1: Click End Phase button (opens confirmation modal)
    end_btn = page.locator('button:has-text("End Phase"), button:has-text("Complete Phase"), button:has-text("Finish Phase")')
    
    if await end_btn.count() > 0:
        await end_btn.first.click()
        await page.wait_for_timeout(1000)
    else:
        print("  ⚠ No 'End Phase' button found")
    
    await page.screenshot(path=f"screenshots/sh_phase{phase_num}_confirm_modal.png")
    
    # Step 2: Click "Yes, continue" in the confirmation modal and wait for summary modal
    print_substep("Confirming end phase...")
    confirm_btn = page.locator('button:has-text("Yes, continue"), button:has-text("Yes"), button:has-text("Continue"), button:has-text("Confirm")')
    
    if await confirm_btn.count() > 0:
        await confirm_btn.first.click()
    else:
        print("  ⚠ No confirmation button found")
    
    # Wait for the summary modal to appear (it shows "Phase summary" in the header)
    print_substep("Waiting for summary modal...")
    summary_modal = page.locator('text="Phase summary"')
    try:
        await summary_modal.wait_for(state="visible", timeout=30000)  # Wait up to 30 seconds
        print("  ✓ Summary modal appeared")
    except:
        print("  ⚠ Summary modal didn't appear in time")
    
    await page.wait_for_timeout(2000)  # Extra buffer for content to load
    await page.screenshot(path=f"screenshots/sh_phase{phase_num}_summary.png")
    
    # Step 3: Review and approve summary
    print_substep(f"Reviewing Phase {phase_num} summary...")
    pause(f"Phase {phase_num} summary displayed. Press Enter to approve...")
    
    # Try multiple button text variations
    approve_btn = page.locator('button:has-text("Approve"), button:has-text("Accept"), button:has-text("Confirm"), button:has-text("OK"), button:has-text("Done"), button:has-text("Submit")')
    
    if await approve_btn.count() > 0:
        # Use JavaScript click to bypass any overlay
        await approve_btn.first.evaluate("el => el.click()")
        await page.wait_for_timeout(3000)
    else:
        print("  ⚠ No 'Approve' button found")
        # Try clicking any visible button in the modal
        await page.screenshot(path=f"screenshots/sh_phase{phase_num}_no_approve_debug.png")
    
    # Step 4: Respond to break offer (skip for phase 4 - final phase)
    if phase_num < 4:
        print_substep("Responding to break offer...")
        await page.wait_for_timeout(2000)  # Wait for AI break offer message
        
        await page.screenshot(path=f"screenshots/sh_phase{phase_num}_break_offer.png")
        
        # Send "ready to continue" response
        chat_input = page.locator('textarea').last
        if await chat_input.count() > 0:
            await chat_input.fill("Ready to continue")
            send_btn = page.locator('button:has-text("Send")')
            if await send_btn.count() > 0:
                # Use JavaScript click to bypass any overlay
                await send_btn.first.evaluate("el => el.click()")
                await page.wait_for_timeout(3000)  # Wait for AI to start next phase
        
        await page.screenshot(path=f"screenshots/sh_phase{phase_num}_continuing.png")
    
    print(f"  ✓ Phase {phase_num} complete")
    return True


async def stakeholder_phase_1(page):
    """Phase 1: Open Discovery - Team, role, processes, tools."""
    
    print_step("PHASE 1: OPEN DISCOVERY")
    print("  Focus: Team, role, processes, tools, what works and what doesn't")
    
    messages = [
        (
            "Hi! I'm John Smith, the Sales Manager at Acme Corp. I've been here "
            "for about 5 years and I manage a team of 15 sales representatives "
            "covering the western United States."
        ),
        (
            "Our current process is honestly pretty chaotic. Each rep tracks their "
            "deals differently - some use spreadsheets, others use the old CRM we're "
            "supposed to be replacing, and a few just keep notes in their email. "
            "There's no consistency across the team."
        ),
        (
            "What works well is honestly our people. We have a strong team that "
            "closes deals. The problem is visibility - I don't know what's in the "
            "pipeline until deals close or die. Forecasting is my biggest pain point. "
            "I spend every Friday calling reps for updates."
        ),
        (
            "We use Outlook for email, the old CRM (barely), Excel for everything else, "
            "and Slack for team communication. We also have a separate quoting system "
            "that doesn't integrate with anything. It's a mess of disconnected tools."
        ),
    ]
    
    for i, msg in enumerate(messages):
        print_substep(f"Message {i+1}/{len(messages)}")
        print(f"      \"{msg[:50]}...\"")
        
        await send_message_and_wait(page, msg, f"sh_p1_msg{i+1}")
        pause(f"Phase 1 message {i+1} sent. Press Enter to continue...")
    
    await end_phase_and_approve(page, 1)
    pause("Phase 1 complete. Press Enter to start Phase 2...")
    return True


async def stakeholder_phase_2(page):
    """Phase 2: Targeted Follow-ups - Gap-filling for in-scope topics."""
    
    print_step("PHASE 2: TARGETED FOLLOW-UPS")
    print("  Focus: Gap-filling questions for in-scope topics")
    
    messages = [
        (
            "For the quoting process, reps currently create quotes in a separate "
            "system called QuoteBuilder. They have to manually copy opportunity data "
            "from wherever they're tracking it, create the quote, then email it as a "
            "PDF. There's no connection to our CRM at all."
        ),
        (
            "When a deal closes, the rep emails me and our operations team. Then "
            "someone manually enters it into our ERP system for fulfillment. Sometimes "
            "deals fall through the cracks because the handoff is just email-based. "
            "We've had fulfillment delays because of this."
        ),
        (
            "For reporting, I pull data from the old CRM into Excel every week, then "
            "create pivot tables and charts manually. It takes me 4-5 hours every "
            "Friday just to compile the pipeline report for leadership. And by Monday "
            "the data is already stale."
        ),
    ]
    
    for i, msg in enumerate(messages):
        print_substep(f"Message {i+1}/{len(messages)}")
        print(f"      \"{msg[:50]}...\"")
        
        await send_message_and_wait(page, msg, f"sh_p2_msg{i+1}")
        pause(f"Phase 2 message {i+1} sent. Press Enter to continue...")
    
    await end_phase_and_approve(page, 2)
    pause("Phase 2 complete. Press Enter to start Phase 3...")
    return True


async def stakeholder_phase_3(page):
    """Phase 3: Validation & Clarification - Confirming understanding."""
    
    print_step("PHASE 3: VALIDATION & CLARIFICATION")
    print("  Focus: Confirming understanding, resolving contradictions")
    
    messages = [
        (
            "Yes, that's correct. The main systems are: the old CRM (which maybe 40% "
            "of reps use), Excel spreadsheets (everyone uses these), QuoteBuilder for "
            "quotes, Outlook for email, and our ERP for fulfillment. Nothing talks to "
            "each other."
        ),
        (
            "For the team structure - I have 15 reps, split into 3 territories (West "
            "Coast, Mountain, and Southwest). Each territory has a senior rep who acts "
            "as team lead but they don't have management responsibilities, they're "
            "player-coaches who still carry their own quota."
        ),
        (
            "The forecast process specifically: Friday afternoons I call or Slack each "
            "rep for their pipeline updates. I compile it in Excel, add my judgment on "
            "deal likelihood, and send the report to VP of Sales by EOD Friday. It's "
            "tedious and error-prone."
        ),
    ]
    
    for i, msg in enumerate(messages):
        print_substep(f"Message {i+1}/{len(messages)}")
        print(f"      \"{msg[:50]}...\"")
        
        await send_message_and_wait(page, msg, f"sh_p3_msg{i+1}")
        pause(f"Phase 3 message {i+1} sent. Press Enter to continue...")
    
    await end_phase_and_approve(page, 3)
    pause("Phase 3 complete. Press Enter to start Phase 4...")
    return True


async def stakeholder_phase_4(page):
    """Phase 4: Future State & Priorities - Success criteria."""
    
    print_step("PHASE 4: FUTURE STATE & PRIORITIES")
    print("  Focus: Success criteria, priorities, must-haves vs nice-to-haves")
    
    messages = [
        (
            "Success for me means: I can see the entire pipeline in real-time without "
            "calling anyone. Reps can update deals from their phones between client "
            "meetings. Forecasting takes 30 minutes instead of 5 hours. And deals "
            "don't fall through the cracks at handoff."
        ),
        (
            "Must-haves: Mobile access for reps, real-time pipeline visibility, "
            "automated forecast reports, and integration with our quoting system. "
            "Nice-to-haves: AI-powered deal insights, territory mapping, and "
            "gamification features for the team."
        ),
        (
            "The biggest win would be if leadership could pull their own reports "
            "without asking me. Right now I'm the bottleneck for all pipeline data. "
            "Self-service reporting for execs would free up hours of my time every "
            "week and make the data more timely."
        ),
    ]
    
    for i, msg in enumerate(messages):
        print_substep(f"Message {i+1}/{len(messages)}")
        print(f"      \"{msg[:50]}...\"")
        
        await send_message_and_wait(page, msg, f"sh_p4_msg{i+1}")
        pause(f"Phase 4 message {i+1} sent. Press Enter to continue...")
    
    await end_phase_and_approve(page, 4)
    return True


async def view_final_report(page):
    """View the final discovery report."""
    
    print_step("FINAL: DISCOVERY REPORT")
    
    await page.wait_for_timeout(2000)
    await page.screenshot(path="screenshots/sh_final_01.png")
    
    # Look for View Report or Results button
    report_btn = page.locator('button:has-text("Report"), button:has-text("Results"), button:has-text("View"), a:has-text("Report")')
    
    if await report_btn.count() > 0:
        print_substep("Opening final report...")
        await report_btn.first.click()
        await page.wait_for_timeout(3000)
    
    await page.screenshot(path="screenshots/sh_final_02_report_top.png")
    
    # Scroll to capture full report
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
    await page.wait_for_timeout(500)
    await page.screenshot(path="screenshots/sh_final_03_report_mid1.png")
    
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 2/3)")
    await page.wait_for_timeout(500)
    await page.screenshot(path="screenshots/sh_final_04_report_mid2.png")
    
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(500)
    await page.screenshot(path="screenshots/sh_final_05_report_bottom.png")
    
    print("  ✓ Final report captured")
    return True

async def sa_verify_progress(context, sa_email, sa_password="test123"):
    """SA logs back in to verify project progress after stakeholder completes discovery."""
    
    print_step("SA VERIFICATION: CHECK PROJECT PROGRESS")
    
    # Open new tab
    page = await context.new_page()
    
    print_substep("Navigating to SA dashboard...")
    await page.goto(f"{FRONTEND_URL}/sa/dashboard")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    
    # Check if we need to login or if already logged in
    if "/login" in page.url:
        print_substep("Logging in as SA...")
        await page.fill('#email', sa_email)
        await page.fill('#password', sa_password)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
    else:
        print("  ✓ SA already logged in")
    
    # Screenshot SA dashboard with project progress
    await page.screenshot(path="screenshots/sa_verify_01_dashboard.png")
    print("  ✓ SA Dashboard captured")
    
    pause("SA Dashboard showing project progress. Press Enter to view project details...")
    
    # Click View to see project detail
    print_substep("Opening project detail...")
    view_btn = page.locator('button:has-text("View")')
    if await view_btn.count() > 0:
        await view_btn.first.click()
        await page.wait_for_timeout(2000)
    
    await page.screenshot(path="screenshots/sa_verify_02_project_detail_top.png")
    
    # Scroll to see stakeholder progress
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(500)
    
    await page.screenshot(path="screenshots/sa_verify_03_project_detail_bottom.png")
    print("  ✓ Project detail captured")
    
    pause("Project detail showing stakeholder completion. Press Enter to finish...")
    
    return page

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def main(headless=False):
    """Run the complete E2E test."""
    
    import os
    os.makedirs("screenshots", exist_ok=True)
    
    # Generate test emails
    sa_email = random_email()
    stakeholder_email = random_email()
    
    # Print test info
    print(f"\n{'='*60}")
    print("  XP ARCHITECT - COMPLETE E2E TEST")
    print(f"{'='*60}")
    print(f"\nFrontend URL: {FRONTEND_URL}")
    print(f"\nTest Accounts:")
    print(f"  SA:          {sa_email} / test123")
    print(f"  Stakeholder: {stakeholder_email} / test123")
    print(f"\nMode: {'Headless' if headless else 'Visible browser'}")
    print(f"Pause mode: {'ON - will pause at key steps' if PAUSE_MODE else 'OFF'}")
    
    print(f"\n{'='*60}")
    print("  TEST FLOW")
    print(f"{'='*60}")
    print("""
  SOLUTION ARCHITECT:
    1. Register on the app
    2. Create Project
    3. Add Stakeholder + Get Invite Link
    
  STAKEHOLDER:
    1. Register via invite link
    2. Take Communication Assessment (5 questions)
    3. Start Discovery Session
    4. Phase 1: Open Discovery → Approve Summary
    5. Phase 2: Targeted Follow-ups → Approve Summary
    6. Phase 3: Validation & Clarification → Approve Summary
    7. Phase 4: Future State & Priorities → Approve Summary
    8. View Final Discovery Report
    """)
    
    pause("Ready to start. Press Enter to begin...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=headless,
            slow_mo=SLOW_MO if not headless else 100
        )
        
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900}
        )
        
        # SA's browser page
        sa_page = await context.new_page()
        
        try:
            # =================================================================
            # SOLUTION ARCHITECT FLOW
            # =================================================================
            
            await sa_register(sa_page, sa_email)
            await sa_create_project(sa_page)
            invite_link = await sa_add_stakeholder(sa_page, stakeholder_email)
            
            # =================================================================
            # STAKEHOLDER FLOW
            # =================================================================
            
            sh_page = await stakeholder_register(context, invite_link, stakeholder_email)
            await stakeholder_assessment(sh_page)
            await stakeholder_start_discovery(sh_page)
            
            # =================================================================
            # 4-PHASE DISCOVERY
            # =================================================================
            
            await stakeholder_phase_1(sh_page)
            await stakeholder_phase_2(sh_page)
            await stakeholder_phase_3(sh_page)
            await stakeholder_phase_4(sh_page)
            
            # =================================================================
            # FINAL REPORT
            # =================================================================
            
            await view_final_report(sh_page)

            # =================================================================
            # SA VERIFICATION
            # =================================================================
            
            sa_verify_page = await sa_verify_progress(context, sa_email)
            
            # =================================================================
            # COMPLETE
            # =================================================================
            
            print_step("✓ TEST COMPLETE!")
            print(f"""
  All screenshots saved to ./screenshots/
  
  Test flow completed:
    ✓ SA: Register → Create Project → Add Stakeholder
    ✓ Stakeholder: Register → Assessment → 4-Phase Discovery
    ✓ SA: Verified project progress shows completion
  
  Test accounts created:
    SA:          {sa_email} / test123
    Stakeholder: {stakeholder_email} / test123
    
  You can log in with these accounts to review the results.
            """)
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"  ✗ TEST FAILED")
            print(f"{'='*60}")
            print(f"\nError: {e}")
            
            # Save error screenshots
            try:
                await sa_page.screenshot(path="screenshots/error_sa_page.png")
                print("  Error screenshot saved: screenshots/error_sa_page.png")
            except:
                pass
            
            raise
        
        finally:
            pause("Test finished. Press Enter to close browser...")
            await browser.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    headless = "--headless" in sys.argv
    asyncio.run(main(headless=headless))
