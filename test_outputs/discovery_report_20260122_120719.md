================================================================================
DISCOVERY SESSION REPORT
Generated: 2026-01-22 14:11:51
================================================================================

# DISCOVERY SESSION REPORT

## PROJECT SCOPE
Fix a support ticket routing problem that we are having in Salesforce.

---

## CURRENT STATE FINDINGS

### Team Function & Structure
- **Team Composition:**
  - 50 Tier 1 support representatives
  - 10 Tier 2 support representatives
  - Tier 1 supervisors oversee operations
  - Reports to VP of Customer Success

- **Volume:**
  - Approximately 300 support requests per day
  - 90% of cases require product information lookup

- **Team Function:**
  - Tier 1 performs initial triage on all support tickets
  - Tier 1 resolves straightforward issues or routes to appropriate teams
  - Tier 2 handles outlier cases that don't fit standard routing paths

### Current Tools & Systems
- **Salesforce Service Cloud:** Primary case management system
  - Contains customer account information
  - Contains basic product names only (no detailed product information)
  - Connected to Jira (details of integration unknown)

- **ALEX (Home-grown product tool):**
  - Contains comprehensive product information including:
    - Bill of Materials (BOM)
    - Subscription packages
    - Current product versions
    - Known critical issues
    - Update windows
    - Product lifecycle status
    - Decommission plans
  - Updated via Jira feed with minimal delay (few minutes)
  - Data is always accurate and current
  - Has tightly integrated connection with Product Development's Jira

- **Other Systems:**
  - Experience Cloud portal (customer-facing)
  - Jira (Product Development's primary tool)

### Departments & Partners
- **Finance:** Handles billing-related issues
- **Product Development:** Handles complex product issues; primarily works in Jira
- **Account Managers:** Handle account-related issues (non-billing)
- **IT Team:** Currently exploring ALEX-Salesforce integration options
- **CTO or designate:** Technical decision-maker for system integrations

### Day-to-Day Processes

**Current Case Workflow:**
1. Support request arrives in Salesforce
2. Tier 1 rep performs initial triage
3. For product-related cases (majority), rep opens ALEX
4. Rep searches ALEX by product name or product number
5. Rep navigates through multiple tabs to find needed information
6. Rep copies information from ALEX
7. Rep pastes information into Salesforce Description field
8. Rep manually fills out additional required case fields using copied data
9. Rep either:
   - Resolves the case
   - Escalates to Tier 2
   - Routes to Finance queue
   - Routes to Product Development queue
   - Routes to specific Account Manager

**ALEX Lookup Process:**
- Search may return multiple results (bundles, inactive products, delayed status products)
- Reps identify the correct active product
- Navigate through multiple tabs to gather information
- Most critical tabs: Critical Issues and Versions
- Some reps copy-paste multiple times (back and forth); others compile in notepad first

**Case Categorization:**
- Sometimes customer selects case type at creation
- Most often Tier 1 categorizes after triage
- Main product-related case types:
  - Critical Issues and Updates
  - New Bugs
  - UI/UX
  - Version

**Team-Specific Handling:**
- **Access Issues:** Tier 1 resolves in Salesforce (Experience Cloud user accounts)
- **Billing Issues:** Routed to Finance
- **Account Issues:** Routed to Account Managers
- **Product Issues:** May stay with Tier 1/2 or route to Product Development
- **Finance and Account Managers:** Also use ALEX for lookups
- **Product Development:** Does very little in Salesforce; works primarily in Jira

### Current Workflows

**Average Handle Time:**
- Current: ~5 minutes per Tier 1 case
- Estimated without ALEX friction: ~3 minutes per case
- Potential time savings: 600 minutes (10 hours) daily across team

**Data Entry Challenges:**
- Information pasted into Description field is inconsistent
- Manual extraction from Description to populate other required fields
- No standardized format across reps
- Product information in Salesforce is unreliable for reporting purposes

**Routing Patterns:**
- Cases forwarded to team queues (Finance, Product Development)
- Account Manager cases forwarded to specific individuals based on account assignment
- Tier 2 receives outliers that don't fit other routing paths

---

## PAIN POINTS

### Key Frustrations

**System Context Switching:**
- Reps must switch between Salesforce and ALEX on 90% of cases
- Described as "very frustrating and time consuming"
- Significantly impacts workflow efficiency

**Manual Copy-Paste Workflow:**
- Described as "a pain" and "really sucks"
- Requires navigating multiple tabs in ALEX
- Most reps make multiple round-trips between systems
- Time-consuming and interrupts focus

**Data Quality Issues:**
- Copy-paste process is prone to errors
- Inconsistent data capture across different reps
- Some reps more diligent than others about correcting errors
- Product information in Salesforce is unreliable for analysis

### Challenges & Blockers

**Downstream Impact of Errors:**
- Wrong subscription package information copied into tickets
- Account Managers may create upgrade proposals with incorrect subscription types
- Errors cascade through multiple teams
- Some team members catch errors, others don't (due to attention, motivation, or workload)

**High-Impact Error Examples:**
- Customers given wrong subscription information (particularly lower-priced products)
- Account Managers don't realize mistake until metrics arrive
- Difficult to approach customer to correct pricing after the fact
- Damages customer relationships and impacts revenue
- Frequency: Approximately once per quarter

**Metrics and Reporting Limitations:**
- Cannot reliably track performance by product type
- Current metrics based on inconsistent data
- Team "best guesses" on product-related analytics
- Limited visibility into actual performance patterns

**Workload Pressure:**
- Reps described as "overworked"
- Contributing factors:
  - Time spent on ALEX-Salesforce workflow
  - Inefficiencies with ALEX data access
  - Takes approximately twice as long to handle cases

### What Slows Them Down

**ALEX Navigation:**
- Multiple tabs required to gather complete information
- Must identify correct product among multiple results
- Different status products (active, inactive, delayed, bundles) appear in search
- Tab-by-tab information gathering

**Manual Data Transfer:**
- Copy information from ALEX
- Paste into Salesforce Description field
- Extract relevant pieces to populate individual case fields
- No automation or data flow between systems

**Case Aging:**
- Cases shouldn't age in Tier 1 but occasionally do
- Primary aging occurs in Product Development queue
- Due to complexity or timing of scheduled update patches

**Lack of Field Standardization:**
- Different teams need different information on cases
- All fields visible to all teams creates clutter
- No progressive disclosure based on case routing
- Acknowledged as area needing improvement (though initially considered out of scope)

---

## SUCCESS CRITERIA

### Ideal State Vision

**Integrated Customer View:**
- Look up customer account in Salesforce
- See all relevant customer data including product information
- No need to access separate ALEX system
- All information in one place

**Automated Field Population:**
- When case is created, relevant fields auto-populate
- Data pulled based on case type and product type
- Only relevant information populated (not everything)
- Eliminates manual copy-paste completely

**Progressive Case Layouts:**
- Tier 1 sees basic fields needed for their role plus relevant ALEX product data
- When routed to Finance, Finance-specific fields appear
- When routed to Account Management, Account Management-specific fields appear
- Product Development works primarily in Jira (minimal Salesforce needs)
- Keeps interface clean and focused for each team

**Quick Access for Complex Cases:**
- Tier 2 can access additional ALEX product details directly from case
- Link or embedded view to full product record
- No need to leave Salesforce and navigate ALEX tabs

**Foundation for AI Agent:**
- Executive timeline: End of year implementation
- Customer-facing agent accessible from website and Experience Cloud portal
- Would replace majority of Tier 1 representatives
- Retain handful of Tier 1 supervisors to manage AI agents
- Phase 1: Replicate Tier 1 functionality (triage, resolve, route)
- Future phases: May expand into Finance and Account Manager functions

### Success Metrics

**Primary Metrics:**
- **Handle time** reduction (target: 5 minutes → 3 minutes per case)
- **First contact resolution** rate (cases resolved by Tier 1 without escalation)
- **Average case age** (particularly for Product Development cases)
- **Number of closed cases per rep**

**Reporting Dimensions:**
- By case type
- By product type (for product-related cases)
- Currently impossible due to unreliable product data

**Data Quality Improvements:**
- Consistent product information capture
- Reliable metrics for analysis
- Ability to track performance patterns by product

### What Would Be a Win

**For Support Team (Immediate):**
- Elimination of ALEX-Salesforce context switching
- No more manual copy-paste workflow
- Faster case handling (estimated 2 minutes saved per case = 10 hours/day team capacity)
- Reduced errors in product information
- Better data for performance tracking

**For Other Teams:**
- Finance and Account Managers receive cases with accurate, consistent product data
- Product Development has what they need in Jira (minimal Salesforce impact)
- All teams see only relevant fields for their function

**For AI Agent Initiative (Strategic):**
- Integration enables chatbot to access both Salesforce and ALEX data
- Without integration, chatbot cannot function appropriately
- Without integration, would still require manual Tier 1 work
- Integration is described as "critical for the chatbot implementation in order to have maximum value"

**Risk Reduction:**
- Fewer quarterly pricing errors impacting customer relationships and revenue
- Less dependency on individual rep diligence
- More consistent customer experience

---

## RECOMMENDED SCOPE ADDITIONS

### 1. ALEX-Salesforce Data Integration
**What:** Build integration to automatically populate relevant ALEX product data into Salesforce cases based on case type and product selection.

**Why this should be included:**
- **Directly addresses root cause:** The ticket routing problem is compounded by lack of product context. Reps cannot route effectively without accessing ALEX, which creates the 90% context-switching rate and associated delays.
- **Enables accurate routing decisions:** Tier 1 needs product information (current version, critical issues, update windows, lifecycle status) to determine correct routing destination. Without this data in Salesforce, routing decisions are based on incomplete information.
- **Measurable efficiency gain:** Estimated 2 minutes saved per case × 300 cases/day = 10 hours of daily capacity returned to the team. This is significant ROI for a routing improvement project.
- **Prevents downstream routing errors:** Quarterly pricing errors occur because incomplete/incorrect product data leads to wrong routing or wrong information passed to Account Managers and Finance. Integration eliminates this error vector.
- **Foundation for sustainable solution:** Any routing improvements will be undermined if reps continue jumping to ALEX mid-workflow. Integration ensures routing improvements actually stick.

### 2. Smart Field Population Based on Case Type and Product
**What:** Auto-populate only the ALEX fields relevant to specific case type/product combination when case is created or categorized.

**Why this should be included:**
- **Reduces routing decision time:** Tier 1 currently spends time determining what information to copy from ALEX. Automated population based on case type (Critical Issues and Updates, New Bugs, UI/UX, Version) speeds triage and routing.
- **Improves routing accuracy:** Consistent, complete data ensures routing decisions are based on full context rather than whatever the rep remembered to copy.
- **Eliminates manual field population:** Reps currently copy to Description field, then manually extract to populate required case fields. This double-handling creates routing delays and errors.
- **Supports multiple routing paths:** Finance, Account Managers, and Product Development all need product context when cases arrive. Auto-population ensures routed cases arrive with complete information for next-step decisions.

### 3. Progressive Case Layout Based on Routing
**What:** Configure case layouts to show Tier 1-relevant fields initially, then expose additional team-specific fields when routed to Finance, Account Management, or other queues.

**Why this should be included:**
- **Improves routing workflow clarity:** When Tier 1 routes a case, the receiving team immediately sees the fields they need without clutter from irrelevant fields. This speeds their response time.
- **Reduces routing errors:** Clear field organization helps each team quickly verify they received the right type of case, reducing mis-routing bounce-backs.
- **Supports handoff quality:** Each team knows exactly what information they're responsible for completing, improving case progression through routing stages.
- **User adoption advantage:** Clean, role-appropriate interfaces reduce training burden and increase likelihood of correct routing usage.
- **Acknowledged need:** User stated this "would be really nice" and is an area that "really needs improvement," indicating existing pain with current routing handoffs.

### 4. Tier 2 Deep-Dive Access to ALEX Data
**What:** Provide embedded or linked access to full ALEX product details from Salesforce case for Tier 2 representatives handling complex escalations.

**Why this should be included:**
- **Prevents routing reversals:** Tier 2 handles outlier cases that don't fit standard routing. If they lack access to deeper product data, they may need to send cases back to Tier 1 or make incorrect routing decisions to other departments.
- **Reduces escalation cycle time:** Case aging is already an issue (particularly with Product Development). Tier 2 having immediate access to full product context prevents additional routing loops and delays.
- **Supports complex routing decisions:** Outlier cases by definition require more context to route correctly. Tier 2 needs comprehensive product information to make sophisticated routing judgments.
- **Minimal scope addition:** Leverage same integration built for Tier 1, just expose additional ALEX data through link/embedded view rather than limited field population.

---

## OTHER OUT-OF-SCOPE MENTIONS

### 1. AI Agent/Chatbot Development
**What was mentioned:** Building a customer-facing AI agent to replace Tier 1 representatives, accessible from website and Experience Cloud portal, with implementation target of end of year.

**Why NOT to include in current scope:**
- This is a separate, substantial project with its own requirements, timeline, and stakeholder approval process
- Current project should focus on fixing the routing problem and establishing the data foundation
- User explicitly stated chatbot build "is not part of this project" and they're "not sure exactly when the chatbot build project will kick off"
- Discovery information will inform future chatbot requirements, but chatbot build should be Phase 2
- Including it now would dramatically expand scope, timeline, and budget beyond a routing fix
- Better approach: Solve routing problem and integration now, which creates foundation for future chatbot implementation

### 2. Jira-ALEX Integration Exploration
**What was mentioned:** Product Development has existing Jira-ALEX integration; Salesforce connects to Jira somehow; unclear technical details.

**Why NOT to include in current scope:**
- User stated they are "not technical" and multiple times said "you'd have to talk to someone from Product Development"
- This is technical discovery work, not a solution requirement
- May inform the technical approach to ALEX-Salesforce integration, but doesn't need to be a deliverable
- IT team is already exploring ALEX-Salesforce integration options
- Better approach: Technical team investigates as part of solution design, not as scope item

### 3. Data Standardization and Quality Improvement Initiative
**What was mentioned:** Need for improved standardization around how reps format and document information; current Description field usage is inconsistent; acknowledged area needing improvement.

**Why NOT to include in current scope:**
- User explicitly stated: "Yeah, so that's one place we really need to improve. I don't think it's part of this project though."
- This is a training, change management, and data governance initiative
- Auto-population of fields (which IS recommended for scope) will largely solve this issue automatically
- Remaining standardization work is better handled through operational excellence/training programs
- Better approach: Auto-population eliminates most of the problem; address remaining gaps through operations team

### 4. Finance and Account Manager Workflow Optimization
**What was mentioned:** Finance and Account Managers need different data subsets; they also experience ALEX friction; future chatbot phases might expand to handle their functions.

**Why NOT to include in current scope:**
- Project scope is specifically about support ticket routing problem
- Finance and Account Manager improvements are separate workstreams
- User indicated their needs are "another question I can't answer for sure" - would require separate discovery
- They benefit from Tier 1 routing improvements (receiving cases with better data) without dedicated workflow changes
- Better approach: Include them as stakeholder interviews for current project; their specific workflow optimization is future phase

### 5. Comprehensive Metrics and Analytics Dashboard
**What was mentioned:** Desire to track handle time, first contact resolution, case age, cases per rep by case type and product type; current metrics unreliable due to data quality.

**Why NOT to include in current scope:**
- Metrics tracking is an outcome of the routing and integration improvements, not a requirement itself
- Salesforce has native reporting capabilities that will work once data

================================================================================
END OF REPORT
================================================================================
