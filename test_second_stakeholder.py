"""
Test Script: Add Second Stakeholder (Sales Rep)
================================================
Run this AFTER test_browser_complete.py to add a second stakeholder 
for consolidated report testing.

This adds a Sales Representative perspective to complement the 
Sales Manager's view, creating good overlap and contrast for the
consolidated discovery report.

SETUP:
  Make sure test_browser_complete.py has run successfully first.
  Note the SA email that was created.

RUN:
  python test_second_stakeholder.py
  python test_second_stakeholder.py --pause  # Pause at key steps
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
SLOW_MO = 500
PAUSE_MODE = "--pause" in sys.argv
AI_RESPONSE_WAIT = 12000

# Second stakeholder details (Sales Rep perspective)
STAKEHOLDER_2 = {
    "name": "Mike Chen - Sales Representative",
    "title": "Senior Sales Representative"
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def pause(message="Press Enter to continue..."):
    if PAUSE_MODE:
        input(f"\n⏸  {message}")

def random_email():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_salesrep_{suffix}@example.com"

def print_step(step):
    print(f"\n{'='*60}")
    print(f"  {step}")
    print(f"{'='*60}")

def print_substep(text):
    print(f"\n  → {text}")

# =============================================================================
# MAIN TEST FLOW
# =============================================================================

async def main():
    print_step("SECOND STAKEHOLDER TEST - SALES REP PERSPECTIVE")
    print("""
  This script adds a Sales Representative to the Acme Corp project.
  
  The Sales Rep will provide field-level perspective on:
    - Day-to-day data entry challenges  
    - Mobile access needs for field sales
    - Customer interaction tracking
    - The quoting process from the rep's view
    
  This creates good contrast with the Sales Manager's management view
  for the consolidated discovery report.
    """)
    
    # Get SA credentials from first test
    sa_email = input("Enter SA email from first test: ").strip()
    sa_password = "test123"
    
    stakeholder_email = random_email()
    
    print(f"\n  SA Email: {sa_email}")
    print(f"  New Stakeholder Email: {stakeholder_email}")
    
    pause("Ready to start. Press Enter to begin...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=SLOW_MO
        )
        
        # =================================================================
        # SA: LOGIN AND ADD SECOND STAKEHOLDER
        # =================================================================
        print_step("SA: ADD SECOND STAKEHOLDER")
        
        sa_context = await browser.new_context(viewport={"width": 1400, "height": 900})
        sa_page = await sa_context.new_page()
        
        print_substep("Logging in as SA...")
        await sa_page.goto(f"{FRONTEND_URL}/")
        await sa_page.wait_for_load_state("networkidle")
        await sa_page.wait_for_timeout(1000)
        
        await sa_page.fill('#email', sa_email)
        await sa_page.fill('#password', sa_password)
        await sa_page.click('button[type="submit"]')
        await sa_page.wait_for_load_state("networkidle")
        await sa_page.wait_for_timeout(2000)
        
        await sa_page.screenshot(path="screenshots/sh2_01_sa_dashboard.png")
        print("  ✓ SA logged in")
        
        # Open existing project
        print_substep("Opening existing project...")
        view_btn = sa_page.locator('button:has-text("View")')
        if await view_btn.count() > 0:
            await view_btn.first.click()
            await sa_page.wait_for_timeout(2000)
        
        await sa_page.screenshot(path="screenshots/sh2_02_project_detail.png")
        
        # Scroll to add stakeholder form
        await sa_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await sa_page.wait_for_timeout(500)
        
        # Add second stakeholder
        print_substep(f"Adding stakeholder: {STAKEHOLDER_2['name']}")
        await sa_page.fill('#add-name', STAKEHOLDER_2['name'])
        await sa_page.fill('#add-email', stakeholder_email)
        await sa_page.click('button:has-text("Add Stakeholder")')
        await sa_page.wait_for_timeout(3000)
        
        await sa_page.screenshot(path="screenshots/sh2_03_stakeholder_added.png")
        print(f"  ✓ Stakeholder added: {stakeholder_email}")
        
        # Capture invite link
        print_substep("Capturing invite link...")
        invite_link = None
        
        # Try clipboard interception
        copy_btn = sa_page.locator('button:has-text("Copy Invite Link")')
        if await copy_btn.count() > 0:
            try:
                invite_link = await sa_page.evaluate("""
                    () => {
                        return new Promise((resolve) => {
                            const originalWriteText = navigator.clipboard.writeText.bind(navigator.clipboard);
                            navigator.clipboard.writeText = async (text) => {
                                navigator.clipboard.writeText = originalWriteText;
                                resolve(text);
                                return originalWriteText(text);
                            };
                            setTimeout(() => resolve(null), 2000);
                        });
                    }
                """)
                
                await copy_btn.last.click()
                await sa_page.wait_for_timeout(1000)
                
                if not invite_link:
                    invite_link = await sa_page.evaluate("navigator.clipboard.readText()")
            except:
                pass
        
        # Fallback: search page content
        if not invite_link:
            all_text = await sa_page.content()
            import re
            match = re.search(r'https?://[^\s"<>]+register[^\s"<>]*token=[^\s"<>]+', all_text)
            if match:
                invite_link = match.group(0)
        
        if invite_link:
            print(f"  ✓ Invite link captured: {invite_link[:60]}...")
        else:
            print("  ⚠ Could not capture invite link automatically")
            invite_link = input("  Paste the invite link manually: ").strip()
        
        await sa_context.close()
        
        # =================================================================
        # STAKEHOLDER 2: REGISTRATION
        # =================================================================
        print_step("STAKEHOLDER 2: REGISTRATION")
        
        sh_context = await browser.new_context(viewport={"width": 1400, "height": 900})
        sh_page = await sh_context.new_page()
        
        print_substep("Opening invite link...")
        await sh_page.goto(invite_link)
        await sh_page.wait_for_load_state("networkidle")
        await sh_page.wait_for_timeout(2000)
        
        await sh_page.screenshot(path="screenshots/sh2_04_register_page.png")
        
        print_substep("Filling registration form...")
        await sh_page.fill('#name', STAKEHOLDER_2['name'])
        await sh_page.fill('#title', STAKEHOLDER_2['title'])
        await sh_page.fill('#password', 'test123')
        await sh_page.fill('#confirmPassword', 'test123')
        await sh_page.click('button[type="submit"]')
        
        await sh_page.wait_for_load_state("networkidle")
        await sh_page.wait_for_timeout(2000)
        await sh_page.screenshot(path="screenshots/sh2_05_registered.png")
        print(f"  ✓ Registered as {STAKEHOLDER_2['name']}")
        
        pause("Registration complete. Press Enter for assessment...")
        
        # =================================================================
        # STAKEHOLDER 2: COMMUNICATION ASSESSMENT
        # =================================================================
        print_step("STAKEHOLDER 2: ASSESSMENT")
        print("  Using Big-picture + Problem-focused style (different from first stakeholder)")
        
        # Different assessment answers - Big-picture primary, Problem-focused secondary
        assessment_answers = [
            {"A": "3", "B": "1", "C": "4", "D": "2"},  # Q1
            {"A": "4", "B": "1", "C": "3", "D": "2"},  # Q2
            {"A": "3", "B": "1", "C": "4", "D": "2"},  # Q3
            {"A": "4", "B": "1", "C": "3", "D": "2"},  # Q4
            {"A": "3", "B": "1", "C": "4", "D": "2"},  # Q5
        ]
        
        for q_num in range(1, 6):
            print_substep(f"Question {q_num}...")
            
            await sh_page.wait_for_timeout(1000)
            await sh_page.screenshot(path=f"screenshots/sh2_q{q_num}_before.png")
            
            answers = assessment_answers[q_num - 1]
            
            for option, rank in answers.items():
                selector = f'select[aria-label="Rank for option {option}"]'
                try:
                    await sh_page.select_option(selector, rank)
                    print(f"    Option {option}: Rank {rank}")
                except Exception as e:
                    print(f"    ⚠ Could not select rank for {option}: {e}")
                await sh_page.wait_for_timeout(200)
            
            await sh_page.screenshot(path=f"screenshots/sh2_q{q_num}_after.png")
            
            if q_num < 5:
                await sh_page.click('button:has-text("Next")')
            else:
                await sh_page.click('button:has-text("Complete assessment")')
            
            await sh_page.wait_for_timeout(1000)
        
        await sh_page.wait_for_timeout(2000)
        await sh_page.screenshot(path="screenshots/sh2_06_assessment_complete.png")
        print("  ✓ Assessment complete (Big-picture / Problem-focused)")
        
        pause("Assessment complete. Press Enter to start discovery...")
        
        # =================================================================
        # STAKEHOLDER 2: START DISCOVERY
        # =================================================================
        print_step("STAKEHOLDER 2: START DISCOVERY")
        
        await sh_page.wait_for_timeout(1000)
        
        discovery_btn = sh_page.locator('button:has-text("Begin Discovery"), button:has-text("Start Discovery")')
        if await discovery_btn.count() > 0:
            await discovery_btn.first.click()
            await sh_page.wait_for_timeout(3000)
            
            # Enable demo mode
            current_url = sh_page.url
            await sh_page.goto(current_url + ('&' if '?' in current_url else '?') + 'demo=true')
            await sh_page.wait_for_timeout(1000)
        
        await sh_page.screenshot(path="screenshots/sh2_07_discovery_started.png")
        print("  ✓ Discovery started (demo mode)")
        
        # =================================================================
        # HELPER FUNCTIONS
        # =================================================================
        
        async def send_message(text, screenshot_name):
            chat_input = sh_page.locator('textarea').last
            if await chat_input.count() > 0:
                await chat_input.fill(text)
                await sh_page.wait_for_timeout(300)
                send_btn = sh_page.locator('button:has-text("Send")')
                if await send_btn.count() > 0:
                    await send_btn.first.click()
                    print("      Waiting for AI response...")
                    await sh_page.wait_for_timeout(AI_RESPONSE_WAIT)
                    await sh_page.screenshot(path=f"screenshots/{screenshot_name}.png")
        
        async def end_phase_and_approve(phase_num):
            print_substep(f"Ending Phase {phase_num}...")
            
            end_btn = sh_page.locator('button:has-text("End Phase")')
            if await end_btn.count() > 0:
                await end_btn.first.click()
                await sh_page.wait_for_timeout(1000)
            
            confirm_btn = sh_page.locator('button:has-text("Yes, continue"), button:has-text("Yes")')
            if await confirm_btn.count() > 0:
                await confirm_btn.first.click()
            
            print_substep("Waiting for summary...")
            approve_btn = sh_page.locator('button:has-text("Approve")')
            try:
                await approve_btn.wait_for(state="visible", timeout=60000)
            except:
                print("  ⚠ Approve button didn't appear")
            
            await sh_page.wait_for_timeout(1000)
            await sh_page.screenshot(path=f"screenshots/sh2_phase{phase_num}_summary.png")
            
            pause(f"Phase {phase_num} summary. Press Enter to approve...")
            
            if await approve_btn.count() > 0:
                await approve_btn.first.evaluate("el => el.click()")
                await sh_page.wait_for_timeout(2000)
            
            print(f"  ✓ Phase {phase_num} complete")
            
            if phase_num < 4:
                print_substep("Waiting for break offer...")
                await sh_page.wait_for_timeout(8000)
                await sh_page.screenshot(path=f"screenshots/sh2_phase{phase_num}_break.png")
                
                await send_message("Ready to continue", f"sh2_phase{phase_num}_continue")
                await sh_page.wait_for_timeout(3000)
                
                begin_btn = sh_page.locator('button:has-text("Begin Phase")')
                if await begin_btn.count() > 0:
                    await begin_btn.first.click()
                    await sh_page.wait_for_timeout(3000)
        
        # =================================================================
        # PHASE 1: OPEN DISCOVERY (Sales Rep Perspective)
        # =================================================================
        print_step("PHASE 1: OPEN DISCOVERY")
        print("  Sales Rep perspective - field-level view")
        
        phase1_messages = [
            (
                "Hey, I'm Mike Chen, one of the sales reps on John's team. I've been "
                "with Acme Corp for about 3 years, covering the Northern California "
                "territory. I spend most of my time out in the field meeting customers "
                "and prospects - probably 60% travel, 40% office."
            ),
            (
                "My day-to-day is a lot of customer visits, demos, and follow-up calls. "
                "The biggest challenge is that when I'm on the road, I basically can't "
                "access our systems properly. The old CRM doesn't work on mobile at all, "
                "so I end up taking notes on paper or in my phone's notes app and then "
                "entering everything when I get back to the office."
            ),
            (
                "Honestly, the double data entry is killing my productivity. I estimate "
                "I spend 5-6 hours a week just transferring notes from the field into "
                "various systems. And half the time I forget details by then. It's also "
                "why my pipeline data is never current - John's always asking for updates "
                "but the system doesn't reflect reality."
            ),
            (
                "What does work is our team communication on Slack. I can quickly ping "
                "John or other reps for help. But for customer data, I'm constantly "
                "emailing myself or texting myself info that should just be in one place. "
                "I also really struggle with the quoting tool - I can't create quotes "
                "from my laptop when I'm at a customer site."
            ),
        ]
        
        for i, msg in enumerate(phase1_messages):
            print_substep(f"Message {i+1}/{len(phase1_messages)}")
            print(f"      \"{msg[:50]}...\"")
            await send_message(msg, f"sh2_p1_msg{i+1}")
            pause(f"Message {i+1} sent. Press Enter to continue...")
        
        await end_phase_and_approve(1)
        
        # =================================================================
        # PHASE 2: TARGETED FOLLOW-UPS (Sales Rep Details)
        # =================================================================
        print_step("PHASE 2: TARGETED FOLLOW-UPS")
        print("  Diving deeper into field rep workflows")
        
        phase2_messages = [
            (
                "When I'm at a customer meeting, I need access to their purchase history, "
                "any open issues or tickets, and my previous notes. Right now I screenshot "
                "stuff before I leave the office and hope I grabbed everything. If a customer "
                "asks about something I didn't prepare for, I have to say 'let me get back "
                "to you' which doesn't look great."
            ),
            (
                "The quoting process is painful. I have to remote desktop into my office "
                "computer to access the quoting tool, which barely works on hotel WiFi. "
                "Or I call our sales ops person and ask them to generate a quote for me, "
                "but that adds a day to the process. Customers want quotes on the spot."
            ),
            (
                "For tracking my deals, I use a personal spreadsheet because the CRM is "
                "too clunky. I update my spreadsheet daily, then batch update the CRM "
                "maybe once a week before our team meeting. I know John gets frustrated "
                "that the system isn't current, but entering the same info twice is "
                "just not sustainable."
            ),
            (
                "When I close a deal, the handoff to implementation is also messy. I have "
                "to email a bunch of people, fill out a form in SharePoint, and then "
                "manually update the CRM. There's no single place to hand off customer "
                "requirements to the delivery team."
            ),
        ]
        
        for i, msg in enumerate(phase2_messages):
            print_substep(f"Message {i+1}/{len(phase2_messages)}")
            print(f"      \"{msg[:50]}...\"")
            await send_message(msg, f"sh2_p2_msg{i+1}")
            pause(f"Message {i+1} sent. Press Enter to continue...")
        
        await end_phase_and_approve(2)
        
        # =================================================================
        # PHASE 3: VALIDATION & CLARIFICATION
        # =================================================================
        print_step("PHASE 3: VALIDATION & CLARIFICATION")
        print("  Confirming understanding")
        
        phase3_messages = [
            (
                "Yeah, that's exactly right. The core problem is that I'm disconnected "
                "from our systems when I'm with customers, which is when I need them most. "
                "Mobile access is absolutely critical for me."
            ),
            (
                "Correct - I'd say about 30% of my time is wasted on administrative work "
                "that could be eliminated with better tools. That's time I could be "
                "spending with customers or prospecting new accounts."
            ),
            (
                "The duplicate data entry and the quoting access are the two biggest "
                "pain points. If I could enter data once from my phone and generate "
                "quotes from anywhere, that alone would be transformative."
            ),
        ]
        
        for i, msg in enumerate(phase3_messages):
            print_substep(f"Message {i+1}/{len(phase3_messages)}")
            print(f"      \"{msg[:50]}...\"")
            await send_message(msg, f"sh2_p3_msg{i+1}")
            pause(f"Message {i+1} sent. Press Enter to continue...")
        
        await end_phase_and_approve(3)
        
        # =================================================================
        # PHASE 4: FUTURE STATE & PRIORITIES
        # =================================================================
        print_step("PHASE 4: FUTURE STATE & PRIORITIES")
        print("  Success criteria from field rep view")
        
        phase4_messages = [
            (
                "Success for me is simple: I want to be able to do my entire job from "
                "my phone or laptop, wherever I am. Pull up customer info before a meeting, "
                "take notes during, update the system immediately after, and send a quote "
                "before I leave the parking lot."
            ),
            (
                "Must-haves: mobile app that actually works, one-click access to customer "
                "360 view, and mobile quoting. Nice-to-haves would be route planning for "
                "my customer visits and automated activity logging from my calendar and email."
            ),
            (
                "If I could get back even 3 hours a week from administrative work, that's "
                "basically another half-day of selling. Multiply that across our 15 reps "
                "and you're talking about real revenue impact. That's how I'd measure success - "
                "less admin time, more customer time."
            ),
        ]
        
        for i, msg in enumerate(phase4_messages):
            print_substep(f"Message {i+1}/{len(phase4_messages)}")
            print(f"      \"{msg[:50]}...\"")
            await send_message(msg, f"sh2_p4_msg{i+1}")
            pause(f"Message {i+1} sent. Press Enter to continue...")
        
        await end_phase_and_approve(4)
        
        # =================================================================
        # VIEW FINAL REPORT
        # =================================================================
        print_step("STAKEHOLDER 2: FINAL REPORT")
        
        await sh_page.wait_for_timeout(3000)
        await sh_page.screenshot(path="screenshots/sh2_final_01.png")
        
        report_btn = sh_page.locator('button:has-text("View Report"), button:has-text("View Discovery Report")')
        if await report_btn.count() > 0:
            await report_btn.first.click()
            await sh_page.wait_for_timeout(5000)
        
        await sh_page.screenshot(path="screenshots/sh2_final_02_report.png")
        print("  ✓ Stakeholder 2 discovery complete!")
        
        pause("Final report displayed. Press Enter to view consolidated report...")
        
        await sh_context.close()
        
        # =================================================================
        # SA: VIEW CONSOLIDATED REPORT
        # =================================================================
        print_step("SA: CONSOLIDATED REPORT")
        print("  Now we'll see both stakeholders' findings combined!")
        
        sa_context2 = await browser.new_context(viewport={"width": 1400, "height": 900})
        sa_page2 = await sa_context2.new_page()
        
        print_substep("Logging in as SA...")
        await sa_page2.goto(f"{FRONTEND_URL}/")
        await sa_page2.fill('#email', sa_email)
        await sa_page2.fill('#password', sa_password)
        await sa_page2.click('button[type="submit"]')
        await sa_page2.wait_for_load_state("networkidle")
        await sa_page2.wait_for_timeout(2000)
        
        # Open project
        view_btn = sa_page2.locator('button:has-text("View")')
        if await view_btn.count() > 0:
            await view_btn.first.click()
            await sa_page2.wait_for_timeout(2000)
        
        await sa_page2.screenshot(path="screenshots/sh2_sa_project_both_stakeholders.png")
        print("  ✓ Project now shows both stakeholders")
        
        # Generate consolidated report
        print_substep("Generating consolidated report...")
        consolidated_btn = sa_page2.locator('button:has-text("Generate Consolidated Report"), button:has-text("Consolidated Report")')
        
        if await consolidated_btn.count() > 0:
            await consolidated_btn.first.click()
            
            print("      Waiting for AI to synthesize both interviews...")
            await sa_page2.wait_for_timeout(25000)  # May take longer with 2 stakeholders
            
            await sa_page2.screenshot(path="screenshots/sh2_consolidated_01_top.png")
            
            # Scroll through the report
            for i in range(2, 6):
                await sa_page2.evaluate("window.scrollBy(0, 600)")
                await sa_page2.wait_for_timeout(500)
                await sa_page2.screenshot(path=f"screenshots/sh2_consolidated_0{i}.png")
            
            print("  ✓ Consolidated report captured!")
            print("""
      The consolidated report should show:
        - Common pain points (disconnected systems, lack of visibility)
        - Role-specific issues (manager vs rep perspectives)  
        - Crossovers (same quoting tool frustration from both)
        - Combined success criteria
            """)
        else:
            print("  ⚠ Consolidated report button not found")
        
        pause("Consolidated report complete. Press Enter to finish...")
        
        await sa_context2.close()
        await browser.close()
        
        # =================================================================
        # TEST COMPLETE
        # =================================================================
        print_step("✓ TEST COMPLETE!")
        print(f"""
  Second stakeholder added successfully!
  
  Project now has two stakeholders with different perspectives:
    1. John Smith (Sales Manager) - Management view
       - Pipeline visibility, forecasting, team consistency
       
    2. Mike Chen (Sales Rep) - Field view  
       - Mobile access, data entry, quoting on the road
  
  Common themes for consolidated report:
    ✓ Disconnected tools (both mentioned)
    ✓ Quoting system issues (both frustrated)
    ✓ CRM not meeting needs (both work around it)
    ✓ Data quality problems (caused by rep workarounds)
  
  Screenshots saved in ./screenshots/sh2_*.png
  
  Test accounts:
    SA:           {sa_email} / test123
    Stakeholder 2: {stakeholder_email} / test123
        """)

if __name__ == "__main__":
    asyncio.run(main())