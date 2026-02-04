================================================================================
DISCOVERY SESSION REPORT
Generated: 2026-01-23 14:24:09
================================================================================

# DISCOVERY SESSION REPORT
## Greek Tour Sales Company - Salesforce Sales Cloud Implementation

---

## 1. PROJECT SCOPE

**Brand new implementation of Salesforce Sales Cloud for a small Sales team (20 people)**

**In-Scope Objects:**
- Accounts
- Contacts
- Opportunities
- Leads
- Forecasts
- Tasks

**Sales Cycle:** Standard sales process, averaging 2 weeks with some deals extending to several months

---

## 2. CURRENT STATE FINDINGS

### Team Function & Structure

**Sales Organization:**
- 20-person sales team selling customized Greek tours
- 4 regional team leads (East, West, North, South) managing regional performance and coaching
- Field-based selling model with frequent in-person customer meetings at satellite offices, cafes, and parks
- Team members work from mobile devices with inconsistent WiFi access (offline periods of 2-4 hours)
- First-time CRM users with limited technology experience beyond "social media and Google search"
- Four-tier discount approval structure: 10% / 20% / 25% / 25%+ requiring escalation
- Team leads handle premium "white glove" package deals alongside management duties

**Reporting Hierarchy:**
- Sales Rep → Team Lead → Director → VP

**Geographic Focus:**
- Currently serving Greece-only tours
- Planning geographic expansion to additional countries (currently delayed due to operational infrastructure limitations)

### Current Tools & Systems

**Technology Stack:**
- **Outlook**: Email communication, task management, calendar events, lead queue groups (regional email addresses)
- **Spreadsheets**: Master pipeline tracker in SharePoint + numerous personal copies created when working offline
- **Word**: Quote document creation with manual versioning
- **SharePoint**: Customer folders and document storage (with significant duplication issues)
- **Excel**: Manual executive reporting template with pivot tables, formulas, and visualizations

**Data Quality Issues:**
- No single source of truth for customer information
- Duplicate customer folders in SharePoint (people don't search before creating)
- Duplicate lead assignments (multiple people claiming same opportunity)
- Pipeline discrepancies from personal spreadsheet copies syncing inconsistently
- Inconsistent activity documentation living primarily in email threads
- Historical data has variable quality due to inconsistent logging habits over 3 years

### Departments & Partners

**Marketing:**
- Operating on Marketing Cloud (first team to move to Salesforce)
- Receives leads through regional email addresses feeding Outlook groups
- Runs promotional campaigns through temporary email groups
- Needs visibility into campaign attribution and deal outcomes
- Sends post-booking 5-question survey via email (currently monitored through daily spreadsheet review)
- Tracks customer travel interests beyond Greece to identify expansion opportunities

**Finance:**
- Provides quarterly price lists shared via Excel file in SharePoint
- Email notifications sent when new pricing is available
- Pricing must lock at quote creation to honor commitments when quarterly updates occur mid-deal

**Customer Support:**
- Needs advance visibility into upcoming bookings for service preparation
- Currently receives email notifications when deals close
- Account Managers take over post-sale with clean handoff (sales involvement ends)
- Scheduled for Salesforce onboarding in next project phase

**Third-Party Booking Department:**
- External company handling post-sale booking logistics
- Currently receives information via email: customer details + package information + manually-generated booking number
- Not planned for Salesforce access at this time
- Future vision includes direct integration with booking vendor for upsell/cross-sell opportunities

### Day-to-Day Processes

**Lead Intake & Assignment:**
- Leads arrive via regional email inbox groups
- Current model: "free-for-all" where salespeople self-select opportunities first-come-first-served
- Creates uneven distribution favoring faster responders
- Results in duplicate assignments when multiple people claim same opportunity
- White glove package leads either auto-route by email source or discovered mid-process, triggering team lead notification

**Sales Activities:**
- Review tour option requested in initial lead email
- Conduct needs discovery: group vs. intimate tours, budget, duration, vacation preferences
- Create initial quote in Word document stored in SharePoint customer folder
- Iterate on quotes based on customer feedback (creating multiple Word document versions)
- Track quote status in spreadsheet (only status field updated, no change tracking)
- Navigate discount approvals (4 tiers) with variable urgency including 2-hour SLA for white glove deals
- Finalize booking at 50% deposit + signature
- Hand off to booking department with customer info, package details, and booking number

**Activity Documentation:**
- Inconsistent and informal
- Lives primarily in email threads
- Sporadic use of Outlook tasks and calendar events depending on individual preferences
- Deal context resides in individual salespeople's heads
- Creates business risk when team members leave or are unavailable

### Current Workflows

**Lead to Opportunity Flow:**
- High volume of unqualified leads mixed with qualified opportunities
- No systematic qualification process before leads enter pipeline
- Creates pipeline inflation and unclear visibility

**Quote Management:**
- Manual Word document creation from Finance pricing spreadsheet
- Copy/paste approach for new versions with manual version numbering and dating
- No systematic tracking of what changed or why
- Customers occasionally request to see previous quote versions (uncommon)
- Quote revisions can involve any combination: pricing, itinerary, dates, or package changes

**Approval Process:**
- Discount approvals managed through informal follow-up
- Coordination challenge with variable urgency
- White glove deals require 2-hour SLA
- High-probability deals often need same-day approvals
- Current process lacks formal notification and escalation

**Forecasting:**
- Quarterly and annual forecasts presented monthly
- Emphasis on best-case deals
- Current forecast accuracy: 50-60%
- Confidence gap undermines leadership decision-making

**Win/Loss Tracking:**
- Deals marked as lost with occasional brief notes
- No consistent capture of loss reasons
- Missing opportunity to understand competitive losses, pricing issues, or patterns

**Booking Handoff:**
- Auto-notification to third-party booking department upon deal won
- Manual lookup and increment of booking number (risk of duplicates when multiple deals close simultaneously)
- Email notification to Customer Support for service preparation

---

## 3. PAIN POINTS

### Key Frustrations

**Fragmented Customer View:**
- "Having to go back and forth between systems and not having a clear picture and understanding of our customer"
- Customer information scattered across Outlook, spreadsheets, Word documents, SharePoint folders
- Impossible to deliver personalized service when context is fragmented
- Sales team spends time hunting for information instead of selling

**Business Risk from Lost Context:**
- Deal knowledge lives in individual email threads and salespeople's heads
- Nearly impossible for someone to take over opportunities when team member leaves or is unavailable
- No systematic handoff process or documentation standards

**Stale Data Driving Decisions:**
- Leadership makes decisions based on yesterday's information
- Manual Excel reporting delivers daily snapshots that are already outdated
- Need real-time visibility instead of point-in-time extracts
- Current forecast accuracy of 50-60% creates confidence gap

**Reporting Nightmare:**
- Data discrepancies between master spreadsheet and personal copies
- Pipeline accuracy undermined by sync conflicts
- Manual data extraction and Excel template manipulation for executive reports
- Someone must manually create reports using pivot tables and formulas daily

### Challenges & Blockers

**Lead Distribution Inequity:**
- Free-for-all model favors faster responders
- Uneven opportunity distribution across team
- Duplicate assignments when multiple people claim same lead
- No systematic routing or fairness mechanism

**Document Management Chaos:**
- SharePoint folder duplication (people don't search before creating new folders)
- Multiple Word document versions with no change tracking
- Can't identify patterns in quote revisions
- No visibility into what changed between versions or why

**Mobile/Offline Dysfunction:**
- Salespeople working offline create personal spreadsheet copies
- Inconsistent sync creates pipeline discrepancies
- Field-based sellers need mobile-first functionality
- Inconsistent WiFi at satellite offices compounds problems

**Manual Process Inefficiency:**
- Campaign attribution through manual spreadsheet entries
- Daily monitoring of spreadsheet to trigger post-booking surveys
- Manual booking number lookup/increment (duplicate risk)
- Manual quote versioning without change history
- Manual data extraction for reporting

**Approval Coordination:**
- Four-tier discount approvals managed informally
- Variable urgency creates coordination challenge
- White glove 2-hour SLA difficult to meet without formal escalation
- Same-day needs for high-probability deals risk being missed

### What Slows Them Down

**System Context-Switching:**
- Constant movement between Outlook, spreadsheets, Word, SharePoint, and email
- Productivity drain from tool-hopping instead of selling
- Each system holds different pieces of customer puzzle

**Data Quality Issues:**
- Time spent resolving duplicate customer folders
- Reconciling pipeline discrepancies from offline work
- Tracking down deal context from email threads
- Investigating duplicate lead assignments

**Manual Administrative Burden:**
- Creating new Word document versions manually
- Updating spreadsheet status fields
- Looking up last booking number and incrementing
- Extracting data for executive reports
- Following up informally on pending approvals

**Lack of Pattern Visibility:**
- Can't analyze why quotes are revised
- Minimal win/loss tracking to understand competitive position
- No systematic loss reason capture
- Missing insights on pricing issues or competitive losses

**Expansion Blockers:**
- "We can barely keep track of Greece"
- Current operational chaos prevents geographic growth
- Lack of scalable infrastructure delays business strategy
- Company has postponed expansion opportunities due to system limitations

---

## 4. SUCCESS CRITERIA

### Ideal State Vision

**Operational Infrastructure for Growth:**
- Salesforce implementation enables geographic expansion beyond Greece
- Scalable system that can handle multiple countries/regions without recreating spreadsheet chaos
- Single source of truth for all customer information and sales activities
- Foundation for future booking vendor integration to enable upsell/cross-sell opportunities

**360° Customer View:**
- Complete customer context accessible in one place
- All interactions, documents, quotes, and history visible without system-switching
- Enable personalized service through comprehensive customer understanding
- Support retention strategy as foundation for cross-sell when new countries launch

**Real-Time Business Intelligence:**
- Leadership can make strategic decisions based on current data, not yesterday's snapshots
- Eliminate manual reporting gymnastics
- Self-service access to pipeline visibility and performance metrics
- Confidence in data accuracy across the organization

**Equitable, Systematic Operations:**
- Fair lead distribution replacing free-for-all model
- Structured approval workflows with appropriate urgency and escalation
- Standardized quote management with change tracking and pattern visibility
- Consistent activity documentation that captures deal context

**Mobile-First Field Selling:**
- Full CRM functionality available offline during 2-4 hour customer meetings
- Eliminate spreadsheet sync conflicts that create pipeline discrepancies
- Support satellite office work with inconsistent WiFi
- Enable productivity from anywhere

### Success Metrics

**Priority 1: Pipeline Confidence**
- Real-time pipeline visibility across all levels (rep, team lead, director, VP)
- Quarterly forecast accuracy improvement: from 50-60% to 80-90%
- Confidence gap eliminated enabling strategic planning vs. reactive fire-fighting

**Priority 2: Effortless Performance Tracking**
- Win/loss ratios with structured loss reasons visible to team leads and leadership
- Average sales cycle length monitoring
- Deal size analysis
- Stage conversion tracking
- Activity volume and outcomes correlation
- No more pivot table gymnastics or manual data extraction

**Priority 3: Quality-Adjusted Competition**
- Regional leaderboard rankings incorporating deal complexity and upsell behavior
- Not just volume-based metrics
- Recognition of substantial strategic deals vs. quick low-value transactions
- Drive healthy competition that rewards maximizing customer value

**Priority 4: Customer Relationship Foundation**
- Complete interaction history accessible for personalized service
- Deal context survives team member transitions
- Upsell/cross-sell pattern identification
- Retention data supporting future expansion revenue

### What Would Be a Win

**90-Day Success Marker:**
- Forecast accuracy at 80-90% with full pipeline confidence
- 100% team transition from spreadsheets to Salesforce
- Measurable validation of investment
- Leadership enabled to plan strategically with reliable data

**Day-One Non-Negotiables (Must Be Bulletproof at Launch):**
- Discount approval workflow (4-tier with urgency handling)
- Quote versioning with change tracking
- Lead scoring (rule-based foundation: responsive + budget + dates = high probability)
- Einstein AI pattern analysis activated (leadership purchased Einstein licenses expecting early value)

**Acceptable Temporary Compromises:**
- Manual reporting tolerated during initial phase: "I can't trust the reporting until the core is solid"
- Phased rollout approach that prioritizes data quality over dashboards
- Progressive feature disclosure for technology-hesitant first-time CRM users

**Adoption Success Requirements:**
- 30-day hard cutover timeline (non-negotiable)
- Role-appropriate simplified views for first-time CRM users
- Clear visual guidance and intuitive design
- Friction-reducing features over enforcement (encourage through design)
- Robust support: training + peer champions + office hours during weeks 1-2
- One-click Outlook integration for manual email logging (rep controls business-relevant capture)
- Vacation status auto-pausing lead assignment with team visibility
- Gentle activity tracking encouragement before layering mandatory fields

**Long-Term Vision:**
- Direct integration with booking vendor closing full customer lifecycle
- Salesforce as Phase 1 of larger ecosystem transformation
- Multi-country expansion operational capability
- Automated upsell/cross-sell opportunity identification

---

## 5. RECOMMENDED SCOPE ADDITIONS

### High-Priority Additions

**1. Lead Management & Routing Automation**

**Why Include:** The current "free-for-all" lead assignment model creates three critical problems that undermine the entire sales operation: uneven distribution favoring faster responders, duplicate assignments when multiple people claim the same lead, and white glove package deals being missed or delayed. Without systematic lead routing at go-live, the team will simply replicate their broken process in Salesforce. Implementing regional round-robin routing based on email inbox source, automated white glove package identification and team lead assignment, and vacation-aware assignment blocking solves immediate pain while supporting their four-team structure and premium deal handling requirements.

**Specific Requirements:**
- Regional round-robin routing based on email inbox source (not customer location)
- Automatic white glove package detection and team lead assignment
- Vacation status flag that auto-pauses lead assignment with regional team visibility
- Duplicate lead prevention logic
- Lead holding area for qualification before opportunity conversion (standard leads)
- White glove leads auto-convert and route to team leads

**2. Quote Management with Change Tracking**

**Why Include:** Quote revisions are a core part of every sales cycle, and the current Word document versioning approach eliminates visibility into what changed and why. The team explicitly stated "It would be incredibly useful if we could have visibility into what changed and why. We could possibly identify patterns that way." Without proper quote management, they lose the ability to analyze whether pricing, itinerary changes, dates, or package modifications drive most revisions—insights critical for sales strategy and coaching. Additionally, pricing must lock at quote creation to honor commitments when Finance releases quarterly updates mid-deal. While full CPQ may be overkill, implementing Salesforce standard Quotes with version tracking, change history, and locked pricing directly solves a documented pain point and enables the pattern analysis leadership wants.

**Specific Requirements:**
- Salesforce standard Quotes object with line items
- Quote versioning with change history tracking
- Pricing lock at quote creation (not dynamic current pricing)
- Ability to clone quotes for revisions with visible change log
- Version numbering and date stamping
- Quote approval workflow integration (discount tiers)

**3. Discount Approval Workflow**

**Why Include:** The four-tier discount approval structure (10% / 20% / 25% / 25%+) with variable urgency is a confirmed day-one non-negotiable from the validation phase. White glove deals require 2-hour SLA and high-probability deals often need same-day approvals—both impossible with the current informal follow-up coordination approach. Without formal approval workflow at launch, the team risks lost deals when urgent approvals are missed, creates inconsistent discount practices, and loses the audit trail for pricing decisions. This is explicitly listed as one of three critical workflows that "must be bulletproof at launch" and directly ties to both standard and premium deal processes.

**Specific Requirements:**
- Four-tier approval structure: 10% / 20% / 25% / 25%+
- Urgency flag with SLA tracking (2-hour for white glove, same-day for high-probability)
- Escalation logic when approvals are pending beyond SLA
- Mobile-accessible approval interface for managers
- Approval history and audit trail
- Integration with quote locking mechanism

**4. Document Management & SharePoint Integration**

**Why Include:** The user explicitly stated "We just want to be able to access all customer files in Salesforce. We don't want to have to continuously go back and forth between systems. The more we can do in Salesforce the better." Document fragmentation is identified as a core pain point—the team needs to access quotes, correspondence, contracts, customer-provided info, and photos currently scattered in SharePoint. They're also experiencing significant operational problems with duplicate folder creation because "people don't search before creating new folders." Without addressing document consolidation, Salesforce becomes just another system to check rather than the single source of truth they desperately need. The technical SharePoint integration approach should be determined with IT, but establishing Salesforce Files as the access point

================================================================================
END OF REPORT
================================================================================
