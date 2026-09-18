# Term 1 - Week 2: Loops & Functions

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


## 2. Hackathon prototype → [hackathon/](hackathon/)

*Project title:*
Flow State

*My pair partner:*
Domile Zukaite

*Tool we had to use:*
n8n

*SDG we had to address:*
SDG 3: Good Health and Well-being

*What problem does it solve, and for whom?*
Flow State helps busy students and young professionals who want to exercise but struggle to fit physical activity around changing schedules, weather conditions, and daily energy levels. It reduces the effort required to decide when to exercise and whether a run or a walk is more appropriate.

*What did you build?*
We built an automated n8n workflow that asks the user to complete a short daily survey about their mood and energy. It checks their Google Calendar and the local weather forecast, uses AI to select a suitable free time and activity, adds the plan to their calendar, and sends them a confirmation email.

*Link to the live thing (if any):*
[Add the workflow export, GitHub file, deployed form, or video demo link here]

*How do I run it?*

1. Import the workflow into n8n.
2. Connect the required Google Calendar, Gmail, weather API, and AI credentials.
3. Update the location and calendar settings if necessary.
4. Activate the workflow.
5. Submit the daily mood and energy form.
6. The workflow will check the user’s calendars and weather conditions, choose an appropriate activity and free time, create a calendar event, and email the final plan.

*Who did what?*
We worked together to brainstorm the idea, define the problem, and decide how the automation should work. Felix completed most of the technical development, including building and connecting the n8n workflow. Domile contributed to the planning and design decisions and created the presentation explaining the problem, solution, workflow, SDG relevance, and ethical risks. We tested and refined the overall concept together.

*Ethical reflection – what are the risks of your tool? Who could it harm?*
Flow State uses sensitive information, including mood, energy, location, and calendar availability, so poor data security could expose private details about the user. Incorrect weather information or an inaccurate AI decision could also result in an unsuitable or unsafe activity recommendation. A delayed or failed workflow might tell the user that an event has been scheduled when it has not. To reduce these risks, the system should collect only the data it needs, protect account credentials, validate the AI’s response, clearly confirm whether calendar creation succeeded, and allow users to reject any suggestion. Flow State should only support everyday activity planning. It should not provide medical advice or replace help from a trusted person or healthcare professional when a user is injured, unwell, or experiencing serious distress.

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
Algorithms and especially AI calls can never be fully trusted. They have to be regulated and verified before using them in a production environment. For example, for our project we filtered out genuinely dangerous weather conditions before handing the data over to the AI, aswell as checking if the spot the AI picked is actually safe to hand to the user.

**Where does this connect to "AI for Good"?**
Similar to the algorithms shown in the lecture (like face recognition working better for certain skin tones), although in a smaller scale, our product could harm people instead of improving their lives if we just released it unchecked. For products to do genuine good for all users, they need to thoroughly tested on all edge cases. This way we can make sure that it does not actually harm any potential user group.
