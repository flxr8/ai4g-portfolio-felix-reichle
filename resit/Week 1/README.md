# Term 1 - Week 1: Python Basics & Flow Control

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

**Project title:** Campus Dutch

**My pair partner:** Rayna Jong

**Tool we had to use:** Bolt.new

**SDG we had to address:** SDG 4 – Quality Education (target 4.5: equal access to education; target 4.3: equal access to quality tertiary education)

**Live app:** https://campus-dutch-learnin-gf93.bolt.host/ · **Demo video:** https://youtu.be/0QLnrnBSYq0?si=SPjnhd8SDPF-OeT3 · **Code:** [`hackathon/campus-dutch-main/`](hackathon/campus-dutch-main/)


### The problem

International students in the Netherlands can study in English, but the institution around them often still runs in Dutch: student regulations, administrative emails, portal pages, grading terms and the way teachers phrase instructions. A student who misreads a word like *herkansing* (resit), *inschrijven* (register) or *uiterste inleverdatum* (final deadline) can miss a resit registration or a deadline without realising it.

**How big is it?**
* **129,764 international degree students** were enrolled at Dutch research universities and universities of applied sciences in 2025-26, **17% of all students** (27% at research universities, 9% at universities of applied sciences) ([Nuffic, *International Students in the Netherlands 2026*](https://www.nuffic.nl/en/node/2102)).
* At universities of applied sciences, **80% of bachelor's programmes are taught exclusively in Dutch** ([Nuffic 2026](https://www.nuffic.nl/en/node/2102)). International students on English-taught programmes are therefore a minority inside institutions whose staff, administration and regulations work in Dutch by default.
* **International students drop out more often.** At research universities, 12% of international first-year students drop out, against 3% of Dutch first-year students ([Nuffic 2026](https://www.nuffic.nl/en/node/2102)). Language is not the only reason, but it is one we can do something about.
* **Students want to learn Dutch, but the courses on offer do not fit them.** In a national survey, about 60% of international students said they would like to learn Dutch, but language courses were generally too expensive ([DutchNews, 2019](https://www.dutchnews.nl/news/2019/06/three-in-four-foreign-students-miss-contacts-with-the-dutch)).

**The gap.** Apps such as Duolingo teach everyday conversation (ordering coffee, introducing yourself). University language courses usually start with general A1 Dutch and cost time and money. Neither teaches the small, specific vocabulary of academic administration that a student needs *in their first weeks*.

### Who it is for

**Intended users:** first- and second-year international students on an English-taught programme at a Dutch university or university of applied sciences.
* **Dutch level:** none to A2. The same practical content works for both, because it is vocabulary for recognising words, not grammar for speaking.
* **Situation:** comfortable in English, busy with a full study load, often also new to the country (housing, registration, bank). They do not have time for a full language course.
* **Conditions of use:** on a phone, in short sessions of 5–10 minutes between classes or on the train. No account, no installation.
* **Motivation:** they stick with something that pays off immediately ("now I understand that email"), not with a long course.

**Not intended for:**
* students on Dutch-taught programmes (they need academic writing in Dutch, not word recognition);
* people who want to *speak* Dutch in daily life (Duolingo or a language course fits them better);
* students already at B1 or higher (the content will be too easy);
* staff, and students who need to understand legal documents in detail (for example an appeal against an exam board decision): the app helps them *recognise* that a message is important, not replace the official text or an adviser.

### What we built

A web app that teaches the Dutch words and phrases of academic life with flashcards, quizzes and spaced repetition.

**Content.** 2 categories → 6 topics → 3 levels each (Beginner, Developing, Confident) = 18 lessons with 104 flashcards and 91 quiz questions in total.

| Category | Topics |
|---|---|
| School Systems and Assignments | Grades and Assessments · Deadlines and Submissions · Course Platforms and Schedules |
| Classroom and Teachers | Classroom Instructions · Talking to Lecturers · Asking Questions and Requesting Help |

**What the user does, step by step:**
1. **Pick a lesson.** The Beginner level of every topic is open from the start.
2. **Study the flashcards.** Each card shows the Dutch word, the English meaning, a short explanation of how it works at a Dutch university and an example sentence. Example: *Herkansing* – "Resit / retake" – "A second chance to pass an exam you failed the first time" – *Ik doe mee aan de herkansing van het tentamen.*
3. **Take the quiz the next day.** The quiz of a lesson opens one day after you first study it, so you have   to *recall* the words instead of reading them back. Each question shows an explanation after you answer.
4. **Unlock the next level.** A score of 80% or more opens the next level. 60% or more opens the other lessons at the same level in that category.
5. **Review daily.** Every card sits in one of 5 Leitner boxes. A correct answer moves it up a box, and it comes back after 1 → 3 → 7 → 14 → 30 days. A wrong answer sends it back to box 1 (tomorrow). "Today's Review" mixes all due cards from all topics.
6. **Track progress.** A progress page, a "word of the day" and 6 badges (for example *First Lesson*, *Perfect Score*).

**Output:** the student recognises the key words in a real email, portal page or exam notice, and the review schedule keeps them from forgetting them after a week.

Progress is stored in the browser (`localStorage`): no account, no server, no personal data leaves the device.

<!-- TODO: flow diagram or 3–4 screenshots: lesson → flashcard → quiz → review queue -->

**Why the locks?** Quizzes open the day after a lesson is first studied, and higher levels open only after the level below is passed. This is deliberate: spread-out practice is remembered much longer than cramming in one session. To see the app as a student a few days in, switch on **Demo** (top right). Demo mode fills in realistic progress, so you see completed lessons, open quizzes, a review queue and earned badges; some higher levels are still locked, just as they would be for a real student at that point. The [demo video](TODO) shows what taking a quiz looks like in demo mode.

### How Bolt was used

Bolt.new generated and deployed the whole app (React, TypeScript, Tailwind) from our prompts. We decided what it should do: the topics and levels, the learn → next-day quiz → review loop, the unlock thresholds, the Leitner intervals and the demo mode. We then described each of these to Bolt step by step and tested the result after every change, asking for fixes where it did not behave as intended.

What did not work: we started adding support for more interface languages, but generating all content in several languages used too many Bolt tokens. The language selector is therefore not functional yet; the app is English → Dutch only.

### Why this solution fits the problem

* **Why not a glossary or Google Translate?** They only help once you already know that a message is important and stop to look it up. The risk is the email you skim and do not recognise as a deadline. Recognising the words *at a glance* needs repeated practice, and spaced repetition is a well-known way to make vocabulary stick.
* **Why not Duolingo or a Dutch course?** They teach general Dutch from the start and take months before they reach words like *herkansing* or *inschrijven*. Our users need about a hundred specific words now.
* **Why this format for this user?** Short lessons and one daily review queue fit the 5–10 minute gaps of a busy student; no account means no barrier to start; a phone browser is enough.

### How would it scale?

The app itself is static and runs in any browser, so more users cost almost nothing. The real work is the content: terms differ between universities and universities of applied sciences, and between institutions. A next version would offer content packs per institution, written or checked by its international office or student advisers, with each phrase linked to the official source (for example the institution's Teaching and Examination Regulations). An account would let progress move between devices.

### How do I run it?

* **Online:** open https://campus-dutch-learnin-gf93.bolt.host/ and switch on **Demo** (top right) to see a student with a few days of progress. Switch it off to start as a new student.
* **Locally:** in [`hackathon/campus-dutch-main/`](hackathon/campus-dutch-main/) run `npm install` and then `npm run dev`, and open the address it prints (usually http://localhost:5173). Requires Node.js 18 or newer.

### Who did what?

We created the base of the project together on Friday. We both came up with small changes to further improve the app. Rayna implemented those while Felix focused on creating our slides. We both took turns doing the final polish of the project.

### Ethical reflection

**Who is excluded, and what does the app assume?**
* **Language:** the interface and explanations are English only. Students whose English is weak (for example some students from outside the EU) face two foreign languages at once, the students who struggle most.
* **Device and internet:** it assumes a smartphone or laptop with internet. Progress is saved in one browser, so a student who switches devices, uses a shared computer or clears their browser data loses their progress.
* **Prior knowledge:** it assumes the Dutch higher-education system is the one described. Words and procedures differ between universities and universities of applied sciences and between institutions, and our phrases were chosen by us, not checked against any one institution's regulations. A student can learn a term that their own school uses differently.
* **Accessibility:** there is no audio and we did not test it with screen readers, so visually impaired students may not be able to use it.

**How can it be used for the wrong reasons?**
* **As an excuse not to translate.** A university could point to an app like this instead of making its regulations and emails available in English. That shifts the burden onto the students with the least power, and makes the exclusion described above worse.
* **As a replacement for the official text.** A student who finished the app may feel ready and skip reading the regulations or asking an adviser. The highest-stakes moments (resit registration, appeals, the binding study advice) are exactly where a half-understood word costs the most: a missed resit can delay graduation, and for non-EU students a study delay can affect their residence permit.

**What we did and would do next:**
* **Done:** the app teaches *recognition* ("this is a resit message, act on it"), not legal detail, and it stores no personal data (no account, nothing leaves the browser).
* **Next:** add a visible note on high-stakes cards (resit, deadline, appeal, binding study advice): "Always check the official regulations or ask your study adviser"; link each phrase to the official source of the institution it was checked against; have a student adviser or international office review the content before real use; state clearly on the welcome page that the app supports, and does not replace, translated information from the university.

### Checklist
- [x] Prototype code (or export / workflow file) is in `hackathon/`
- [x] This week's slides are in `presentation/`
- [x] The prototype actually runs, and I wrote down how to run it
- [x] Ethical reflection written above

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

Compacting a broad concept into concrete features and prompts to both make the project solve a specific problem and save tokens.

**Where does this connect to "AI for Good"?**
Focussing on what the user actually needs instead of just throwing every possible feature into an app makes it more likely to actually have impact.
