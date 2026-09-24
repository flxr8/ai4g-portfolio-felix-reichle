# Term 1 - Week 3: Lists & Dictionaries

---

## 1. Homework & workshop assignments -> [`homework/`](homework/)

**What was the assignment?**

**What did I hand in?**
_List the files, or link to them. Notebook exports, screenshots, scripts._

**What did I find difficult, and how did I solve it?**

### Checklist
- [ ] My workshop / homework files are in `homework/`
- [ ] Everything runs without errors, or I explained what does not and why

---


## 2. Hackathon prototype -> [`hackathon/`](hackathon/)

> Your tool and your SDG for this hackathon are announced at the **start of Friday's class**.
> Write them down here once you know them.

**Project title:**
Rebuild

**My pair partner:**
Lili Tárnok

**Tool we had to use:**
Google Gemini API

**SDG we had to address:**
SDG 10: Reduced Inequalities

**What problem does it solve, and for whom?**
Rebuild is for someone going through a major disruptive life transition: released from prison, newly arrived in a different country, fleeing an abusive relationship, or recently homeless. They're all dealing with the same underlying situation. Several urgent, paperwork-heavy problems at once (ID, housing, income, healthcare, legal obligations), no obvious order to tackle them in, and this hits right when they have the least capacity to figure that order out, before a fixed address, a job, or family nearby exists to fall back on. And the scale is real, not assumed: formerly incarcerated people are almost 10 times more likely to be homeless than the general public (2% vs. roughly 0.2%), largely because they leave custody without the ID or address history that housing and job applications require ([Prison Policy Initiative](https://www.prisonpolicy.org/reports/housing.html)). Rebuild assumes you don't already have stable housing or a support network handling this kind of admin for you, and it hands off to an actual caseworker, lawyer or doctor the moment its own confidence runs out.

SDG 10 (target 10.2, social and economic inclusion "irrespective of status"; target 10.3, equal opportunity and reduced inequality of outcome) is really about exactly this: people end up excluded because the systems around them assume a continuity they've just lost.

**What did you build?**
A free Streamlit web app. You type a free-text description of your situation, no forms, no dropdowns. That text goes to Gemini along with a system prompt giving it a fixed seven-domain taxonomy and a strict JSON schema to follow. It classifies which domains actually apply and returns an ordered set of steps with dependencies and urgency, and the app validates that in code before showing anything: dropping hallucinated domains, fixing broken dependency references, untangling cycles. What comes out is a checklist grouped by domain, sorted by urgency, with an "Explain this" button per step and an "Update my plan" flow that re-runs the same Gemini call with new context while keeping whatever's already been completed.

Gemini does the actual classification and planning work here. There's no rule-based way to map arbitrary free text onto the right subset of seven domains in a sensible order, so without it the app can't turn "I just got out and have nowhere to stay" into a plan at all. A single static checklist or a search engine can't do this either, because everyone's situation activates a different subset of domains in a different order, so one generic checklist is either useless to most people or overwhelming to everyone. The same system prompt also forbids Gemini from inventing organisation names, phone numbers or legal requirements it can't verify, it says "look up X in your area" instead, and every message gets screened for crisis language before any plan gets generated.

**Link to the live thing (if any):**
- **Live demo:** https://rebuild-nq5nwmyxtv2ak6efhsybx9.streamlit.app/

**How do I run it?**
1. Open the live demo link above, **or** run it locally: clone this repo, `cd` into `hackathon/rebuild`, `pip install -r requirements.txt`, copy `.env.example` to `.env` and add a free key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey), then `streamlit run app.py`.
2. Describe your situation in the text box and click "Build my plan" - Gemini classifies which domains are relevant and returns an ordered checklist.
3. Tick off steps as you go, click "Explain this" for a plain-language walkthrough of any step, or "Update my plan" when something changes.

**How would it scale?** Right now it runs on one free-tier Gemini key (20-500 requests/day depending on model) and a local JSON file for storage, which is fine for a demo but not for real users. A production version would need a real database instead of a JSON file, paid API quota (or a self-hosted open model) to handle real traffic reliably, and proper authentication instead of a bare session ID. Probably the most important piece though is a partnership with local NGOs or 211-style services to actually maintain the location-specific resource data this app deliberately doesn't try to generate itself.

**Who did what?**
We worked together to brainstorm the idea, define the problem, and decide how the product should work. Felix completed most of the technical development, including building and deploying the streamlit app. Lili contributed to the planning and design decisions and created the presentation explaining the problem, solution, SDG relevance, and ethical risks. We tested and refined the overall concept together.

**Ethical reflection - what are the risks of your tool? Who could it harm?**
The biggest risk is Gemini confidently inventing something specific, a phone number, an organisation, a legal requirement, that someone acts on without being able to check it, right when they're already stretched thin. That's why the system prompt bans fabricating those details, and why nothing from the model gets trusted blindly: every response is validated in code, and malformed JSON, invented dependencies between steps, or off-taxonomy content all get caught and repaired before a user sees them.

The second risk came out of real testing. The free-tier model does not create a valid plan on every call, failing the rest with either a truncated response or a technically valid but empty plan. For most apps that's an annoyance. For the people this app is actually for, limited data, limited patience, often in genuine crisis, an unpredictable failure costs more, which makes it an equity problem.

Third: people are asked to describe things like criminal records, immigration status and health conditions, and right now this prototype stores that in plaintext with no encryption and no real login, a session ID works as a bearer token with no expiry. That's disclosed openly in the app, but it wouldn't be acceptable for anything beyond a prototype without encryption at rest, real authentication and a proper retention policy.

Last, the app runs a keyword-based crisis-language check before generating any plan, tuned to flag more often rather than less. A keyword list will still miss people, and sometimes it'll interrupt someone who didn't need it, which is why real crisis line numbers stay visible on every screen, not just when that check fires. The next step would be connecting it to an actual human-staffed regional crisis line directory instead of the current hand-picked, mostly US/English list. A keyword match is only useful if what it points to is actually reachable.

### Checklist
- [ ] Prototype code (or export / workflow file) is in `hackathon/`
- [ ] This week's slides are in `hackathon/`
- [ ] The prototype actually runs, and I wrote down how to run it
- [ ] Ethical reflection written above

---

## 3. Presentation -> [`presentation/`](presentation/)

*Only fill this in for the week your group was selected to present. You need at least **one** of these across the whole term.*

- [ ] My group presented in this week
- [ ] Slides are in `presentation/`
- [ ] Proof of the live demo is in `presentation/` (recording, screenshots, or link)

**How did it go? What would I do differently next time?**

---

## 4. Reflection

**What is the most important thing I learned this week?**
The most important thing I learned is that there is a long way between succesfully calling an AI API and actually building an application surrounding the AI. There are lots of safeguards and mechanisms to consider to go from getting answers to single question to having a full workflow.

**Where does this connect to "AI for Good"?**
For me the connection is pretty specific. The same flexibility that makes Gemini useful, turning messy free text into a structured plan, is also what makes it risky for exactly this user group, because a confident wrong answer about a legal deadline or a shelter's number costs more for someone with no slack to double-check it than it would for almost anyone else. Reducing inequality here mostly meant getting the AI to admit what it doesn't know: refusing to make up specifics, asking a clarifying question when it needed more information, and failing loudly when something broke so the user actually saw it.
