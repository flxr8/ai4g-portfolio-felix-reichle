export type Difficulty = 1 | 2 | 3;

export interface Flashcard {
  dutch: string;
  english: string;
  explanation: string;
  example: string;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface Lesson {
  id: string;
  title: string;
  description: string;
  difficulty: Difficulty;
  flashcards: Flashcard[];
  quiz: QuizQuestion[];
}

export interface Topic {
  id: string;
  title: string;
  description: string;
  icon: string;
  lessons: Lesson[];
}

export interface Category {
  id: string;
  title: string;
  description: string;
  color: string;
  accentColor: string;
  topics: Topic[];
}

export interface Badge {
  id: string;
  title: string;
  description: string;
  icon: string;
}

export const categories: Category[] = [
  {
    id: 'school-systems',
    title: 'School Systems and Assignments',
    description: 'Learn the Dutch words for grades, deadlines, course platforms and more.',
    color: 'primary',
    accentColor: 'sky',
    topics: [
      {
        id: 'grades-assessments',
        title: 'Grades and Assessments',
        description: 'Understand how grading works at Dutch universities.',
        icon: 'GraduationCap',
        lessons: [
          {
            id: 'grades-l1',
            title: 'Grades and Assessments — Beginner',
            description: 'Start with the most common grading words you will see on your assignments.',
            difficulty: 1,
            flashcards: [
              {
                dutch: 'Cijfer',
                english: 'Grade / mark',
                explanation: 'A cijfer is the number you receive for an assignment or exam, usually between 1 and 10.',
                example: 'Ik heb een hoog cijfer voor mijn essay gekregen. (I got a high grade for my essay.)',
              },
              {
                dutch: 'Voldoende',
                english: 'Passing grade (sufficient)',
                explanation: 'A voldoende means your grade is good enough to pass. In the Netherlands, a 5.5 or higher is usually a voldoende.',
                example: 'Een 6 is een voldoende. (A 6 is a passing grade.)',
              },
              {
                dutch: 'Onvoldoende',
                english: 'Failing grade (insufficient)',
                explanation: 'An onvoldoende means your grade is below the passing threshold. You may need to retake the assignment.',
                example: 'Een 4 is een onvoldoende. (A 4 is a failing grade.)',
              },
              {
                dutch: 'Beoordeling',
                english: 'Assessment / evaluation',
                explanation: 'A beoordeling is the overall evaluation of your work, often including written feedback.',
                example: 'De beoordeling van mijn presentatie was positief. (The assessment of my presentation was positive.)',
              },
              {
                dutch: 'Herkansing',
                english: 'Resit / retake',
                explanation: 'A herkansing is a second chance to pass an exam or assignment you failed the first time.',
                example: 'Ik doe mee aan de herkansing van het tentamen. (I am taking the resit of the exam.)',
              },
              {
                dutch: 'Geslaagd',
                english: 'Passed',
                explanation: 'Geslaagd means you have passed a course, exam or your entire programme.',
                example: 'Ik ben geslaagd voor het tentamen! (I passed the exam!)',
              },
              {
                dutch: 'Zakken',
                english: 'To fail (an exam)',
                explanation: 'Zakken means you did not pass an exam or course and may need to retake it.',
                example: 'Hij is gezakt voor wiskunde. (He failed maths.)',
              },
            ],
            quiz: [
              {
                question: 'What does "voldoende" mean?',
                options: ['A failing grade', 'A passing grade', 'A resit', 'An assessment'],
                correctIndex: 1,
                explanation: '"Voldoende" means sufficient or a passing grade — usually a 5.5 or higher in the Netherlands.',
              },
              {
                question: 'You scored a 4 on your exam. What is this?',
                options: ['A voldoende', 'A herkansing', 'An onvoldoende', 'A beoordeling'],
                correctIndex: 2,
                explanation: 'A 4 is below the passing threshold of 5.5, so it is an "onvoldoende" (failing grade).',
              },
              {
                question: 'What is a "herkansing"?',
                options: [
                  'A type of assessment',
                  'A second chance to retake an exam',
                  'A high grade',
                  'A written evaluation',
                ],
                correctIndex: 1,
                explanation: 'A "herkansing" is a resit — a second opportunity to pass an exam or assignment.',
              },
              {
                question: 'Your teacher says: "De beoordeling is positief." What does this mean?',
                options: [
                  'The evaluation is positive',
                  'The resit is tomorrow',
                  'The grade is failing',
                  'The exam is cancelled',
                ],
                correctIndex: 0,
                explanation: '"Beoordeling" means assessment or evaluation. "Positief" means positive.',
              },
              {
                question: 'Which word means "passed"?',
                options: ['Zakken', 'Geslaagd', 'Onvoldoende', 'Cijfer'],
                correctIndex: 1,
                explanation: '"Geslaagd" means you have passed. "Zakken" is the opposite — to fail.',
              },
            ],
          },
          {
            id: 'grades-l2',
            title: 'Grades and Assessments — Developing',
            description: 'Go deeper into assessment types, study credits and grading systems.',
            difficulty: 2,
            flashcards: [
              {
                dutch: 'Studiepunten',
                english: 'Study credits (ECTS)',
                explanation: 'Studiepunten are credits you earn for completing courses. In the Netherlands, a full year is worth 60 ECTS credits.',
                example: 'Voor dit vak krijg je 5 studiepunten. (You earn 5 credits for this course.)',
              },
              {
                dutch: 'Tentamen',
                english: 'Exam',
                explanation: 'A tentamen is a formal written exam, usually at the end of a course period.',
                example: 'Het tentamen is volgende week vrijdag. (The exam is next Friday.)',
              },
              {
                dutch: 'Deeltoets',
                english: 'Partial exam / mid-term test',
                explanation: 'A deeltoets is a smaller test during the course that counts toward your final grade.',
                example: 'De eerste deeltoets ging goed. (The first partial exam went well.)',
              },
              {
                dutch: 'Weging',
                english: 'Weighting (how much something counts)',
                explanation: 'Weging describes how much each assignment or exam counts toward your final grade.',
                example: 'De weging van het essay is 40%. (The essay weighting is 40%.)',
              },
              {
                dutch: 'Compenseren',
                english: 'To compensate (a grade)',
                explanation: 'Compenseren means a good grade in one subject can make up for a slightly lower grade in another.',
                example: 'Een 8 compenseert een 5. (An 8 compensates a 5.)',
              },
              {
                dutch: 'Cum laude',
                english: 'With distinction (honours)',
                explanation: 'Cum laude is a Latin term used in the Netherlands to mark a degree completed with distinction.',
                example: 'Zij is cum laude geslaagd. (She graduated with distinction.)',
              },
            ],
            quiz: [
              {
                question: 'What are "studiepunten"?',
                options: ['Exam grades', 'Study credits (ECTS)', 'Homework points', 'Class attendance'],
                correctIndex: 1,
                explanation: '"Studiepunten" are ECTS study credits. A full academic year in the Netherlands equals 60 credits.',
              },
              {
                question: 'What is a "deeltoets"?',
                options: [
                  'A final exam',
                  'A partial exam during the course',
                  'A resit',
                  'A group project',
                ],
                correctIndex: 1,
                explanation: 'A "deeltoets" is a partial or mid-term test that counts toward your final grade.',
              },
              {
                question: 'Your syllabus says: "De weging is 50%." What does "weging" mean?',
                options: [
                  'The exam date',
                  'How much it counts toward your final grade',
                  'The number of credits',
                  'The passing threshold',
                ],
                correctIndex: 1,
                explanation: '"Weging" is the weighting — how much a particular assignment or exam counts toward the final grade.',
              },
              {
                question: 'What does "compenseren" mean in a grading context?',
                options: [
                  'To cancel an exam',
                  'A good grade makes up for a lower one',
                  'To retake a test',
                  'To submit late work',
                ],
                correctIndex: 1,
                explanation: '"Compenseren" means a higher grade in one course can compensate for a slightly lower grade in another.',
              },
              {
                question: 'What does "cum laude" indicate?',
                options: [
                  'A failed course',
                  'A degree completed with distinction',
                  'A resit opportunity',
                  'An attendance requirement',
                ],
                correctIndex: 1,
                explanation: '"Cum laude" is a distinction awarded to students who graduate with strong results.',
              },
            ],
          },
          {
            id: 'grades-l3',
            title: 'Grades and Assessments — Confident',
            description: 'Master advanced grading terms and academic regulations.',
            difficulty: 3,
            flashcards: [
              {
                dutch: 'Eisen van de examencommissie',
                english: 'Requirements of the examination board',
                explanation: 'The examencommissie sets the rules for assessments, resits and whether you meet graduation requirements.',
                example: 'De eisen van de examencommissie staan in de studiegids. (The examination board requirements are in the study guide.)',
              },
              {
                dutch: 'Goedkeuring',
                english: 'Approval',
                explanation: 'Goedkeuring is formal approval, for example for a thesis topic or an elective course.',
                example: 'Je hebt goedkeuring nodig voor je scriptieonderwerp. (You need approval for your thesis topic.)',
              },
              {
                dutch: 'Vrijstelling',
                english: 'Exemption / waiver',
                explanation: 'A vrijstelling means you are excused from taking a course because you already completed an equivalent elsewhere.',
                example: 'Ik heb vrijstelling gekregen voor statistiek. (I got an exemption for statistics.)',
              },
              {
                dutch: 'Bindend studieadvies (BSA)',
                english: 'Binding study advice',
                explanation: 'A BSA is a formal recommendation at the end of your first year. If you earn too few credits, you may be required to leave the programme.',
                example: 'Met minder dan 42 studiepunten krijg je een negatief BSA. (With fewer than 42 credits you get a negative BSA.)',
              },
              {
                dutch: 'Inlevertermijn',
                english: 'Submission deadline period',
                explanation: 'The inlevertermijn is the window during which you must submit your work for it to be accepted.',
                example: 'De inlevertermijn sluit om 23:59. (The submission window closes at 23:59.)',
              },
            ],
            quiz: [
              {
                question: 'What does the "examencommissie" do?',
                options: [
                  'Teaches classes',
                  'Sets rules for assessments and graduation requirements',
                  'Organises social events',
                  'Manages course schedules',
                ],
                correctIndex: 1,
                explanation: 'The "examencommissie" (examination board) sets the rules for assessments, resits and graduation requirements.',
              },
              {
                question: 'What is a "vrijstelling"?',
                options: [
                  'A type of exam',
                  'An exemption from taking a course',
                  'A failing grade',
                  'A resit opportunity',
                ],
                correctIndex: 1,
                explanation: 'A "vrijstelling" is an exemption — you do not need to take a course because you already completed an equivalent.',
              },
              {
                question: 'What is a "Bindend studieadvies" (BSA)?',
                options: [
                  'A recommendation for a scholarship',
                  'A formal advice that can require you to leave the programme if you earn too few credits',
                  'A grade improvement plan',
                  'A course selection guide',
                ],
                correctIndex: 1,
                explanation: 'A BSA is a binding study advice given after the first year. Too few credits can mean you must leave the programme.',
              },
              {
                question: 'You need "goedkeuring" for your thesis topic. What does this mean?',
                options: [
                  'You need formal approval',
                  'You need a resit',
                  'You need an exemption',
                  'You need extra credits',
                ],
                correctIndex: 0,
                explanation: '"Goedkeuring" means formal approval — in this case, your thesis topic must be approved.',
              },
              {
                question: 'What is an "inlevertermijn"?',
                options: [
                  'A grading scale',
                  'The submission deadline window',
                  'A type of exam',
                  'A study credit',
                ],
                correctIndex: 1,
                explanation: 'The "inlevertermijn" is the period during which you must submit your work for it to be accepted.',
              },
            ],
          },
        ],
      },
      {
        id: 'deadlines-submissions',
        title: 'Deadlines and Submissions',
        description: 'Learn the words you need for handing in work on time.',
        icon: 'CalendarClock',
        lessons: [
          {
            id: 'deadlines-l1',
            title: 'Deadlines and Submissions — Beginner',
            description: 'Learn the essential words for deadlines and handing in assignments.',
            difficulty: 1,
            flashcards: [
              {
                dutch: 'Deadline',
                english: 'Deadline',
                explanation: 'A deadline is the latest date and time by which you must submit your work.',
                example: 'De deadline is morgen om 12:00. (The deadline is tomorrow at 12:00.)',
              },
              {
                dutch: 'Inleveren',
                english: 'To hand in / submit',
                explanation: 'Inleveren means to submit your assignment, usually online through a course platform.',
                example: 'Ik moet mijn essay vandaag inleveren. (I have to hand in my essay today.)',
              },
              {
                dutch: 'Opdracht',
                english: 'Assignment / task',
                explanation: 'An opdracht is a piece of work you must complete for a course.',
                example: 'Dit is een moeilijke opdracht. (This is a difficult assignment.)',
              },
              {
                dutch: 'Te laat',
                english: 'Too late / late',
                explanation: 'Te laat means your work is submitted after the deadline, which may affect your grade.',
                example: 'Je bent te laat met inleveren. (You are late with submitting.)',
              },
              {
                dutch: 'Uitstel',
                english: 'Extension / postponement',
                explanation: 'Uitstel is extra time to finish your work. You usually need to ask for it in advance.',
                example: 'Kan ik uitstel krijgen voor de opdracht? (Can I get an extension for the assignment?)',
              },
              {
                dutch: 'Verslag',
                english: 'Report',
                explanation: 'A verslag is a written report, often based on research or a project.',
                example: 'Ik moet een verslag schrijven over mijn stage. (I have to write a report about my internship.)',
              },
            ],
            quiz: [
              {
                question: 'What does "inleveren" mean?',
                options: ['To study', 'To hand in / submit', 'To grade', 'To attend'],
                correctIndex: 1,
                explanation: '"Inleveren" means to hand in or submit your assignment, usually through an online platform.',
              },
              {
                question: 'You need more time for your assignment. What do you ask for?',
                options: ['Een verslag', 'Een deadline', 'Uitstel', 'Een opdracht'],
                correctIndex: 2,
                explanation: '"Uitstel" is an extension — extra time to complete your assignment, usually requested in advance.',
              },
              {
                question: 'What is an "opdracht"?',
                options: ['A grade', 'An assignment or task', 'A deadline', 'A report'],
                correctIndex: 1,
                explanation: 'An "opdracht" is an assignment or task you must complete for a course.',
              },
              {
                question: 'Your teacher says your work is "te laat." What does this mean?',
                options: ['Too long', 'Too late', 'Too short', 'Too easy'],
                correctIndex: 1,
                explanation: '"Te laat" means too late — your work was submitted after the deadline.',
              },
              {
                question: 'What is a "verslag"?',
                options: ['A report', 'A deadline', 'An exam', 'A credit'],
                correctIndex: 0,
                explanation: 'A "verslag" is a written report, often based on research or a project.',
              },
            ],
          },
          {
            id: 'deadlines-l2',
            title: 'Deadlines and Submissions — Developing',
            description: 'Learn about group submissions, plagiarism checks and feedback.',
            difficulty: 2,
            flashcards: [
              {
                dutch: 'Groepsopdracht',
                english: 'Group assignment',
                explanation: 'A groepsopdracht is an assignment you complete together with other students.',
                example: 'De groepsopdracht moet volgende week klaar zijn. (The group assignment must be finished next week.)',
              },
              {
                dutch: 'Plagiaat',
                english: 'Plagiarism',
                explanation: 'Plagiaat is using someone else\'s work without giving credit. Universities take this very seriously.',
                example: 'Plagiaat kan leiden tot een onvoldoende. (Plagiarism can lead to a failing grade.)',
              },
              {
                dutch: 'Bronvermelding',
                english: 'Citation / referencing',
                explanation: 'Bronvermelding is listing the sources you used in your work. It is required to avoid plagiarism.',
                example: 'Je moet altijd een goede bronvermelding maken. (You must always include proper citations.)',
              },
              {
                dutch: 'Feedback',
                english: 'Feedback',
                explanation: 'Feedback is commentary from your teacher on your work, explaining what went well and what to improve.',
                example: 'De feedback op mijn verslag was heel nuttig. (The feedback on my report was very useful.)',
              },
              {
                dutch: 'Conceptversie',
                english: 'Draft version',
                explanation: 'A conceptversie is a first or rough version of your work that is not yet finished.',
                example: 'Dit is nog een conceptversie van mijn scriptie. (This is still a draft of my thesis.)',
              },
              {
                dutch: 'Nakijken',
                english: 'To mark / grade (by teacher)',
                explanation: 'Nakijken is what a teacher does when they review and grade your work.',
                example: 'De docent kijkt de tentamens dit weekend na. (The teacher will mark the exams this weekend.)',
              },
            ],
            quiz: [
              {
                question: 'What is a "groepsopdracht"?',
                options: ['A solo exam', 'A group assignment', 'A type of grade', 'A deadline extension'],
                correctIndex: 1,
                explanation: 'A "groepsopdracht" is a group assignment — work you complete together with other students.',
              },
              {
                question: 'What does "plagiaat" mean?',
                options: ['A good grade', 'Plagiarism', 'A group project', 'A resit'],
                correctIndex: 1,
                explanation: '"Plagiaat" is plagiarism — using someone else\'s work without proper credit. Universities take it very seriously.',
              },
              {
                question: 'What is "bronvermelding"?',
                options: ['A type of exam', 'Citation / referencing of sources', 'A group assignment', 'A deadline'],
                correctIndex: 1,
                explanation: '"Bronvermelding" is citing your sources — listing where your information came from to avoid plagiarism.',
              },
              {
                question: 'Your teacher is "de opdrachten aan het nakijken." What are they doing?',
                options: [
                  'Writing new assignments',
                  'Marking / grading your work',
                  'Extending a deadline',
                  'Organising a group project',
                ],
                correctIndex: 1,
                explanation: '"Nakijken" means to mark or grade — the teacher is reviewing and grading your assignments.',
              },
              {
                question: 'What is a "conceptversie"?',
                options: ['A final version', 'A draft version', 'A graded version', 'A resit'],
                correctIndex: 1,
                explanation: 'A "conceptversie" is a draft — a first, unfinished version of your work.',
              },
            ],
          },
          {
            id: 'deadlines-l3',
            title: 'Deadlines and Submissions — Confident',
            description: 'Handle formal submission rules, appeals and academic integrity.',
            difficulty: 3,
            flashcards: [
              {
                dutch: 'Fraude',
                english: 'Academic fraud / cheating',
                explanation: 'Fraude covers cheating, plagiarism and other forms of academic dishonesty. It can lead to serious consequences.',
                example: 'Fraude tijdens een tentamen heeft zware gevolgen. (Cheating during an exam has serious consequences.)',
              },
              {
                dutch: 'Bezwaar maken',
                english: 'To file an objection / appeal',
                explanation: 'Bezwaar maken is the formal process of objecting to a grade or decision you disagree with.',
                example: 'Ik wil bezwaar maken tegen mijn cijfer. (I want to appeal against my grade.)',
              },
              {
                dutch: 'Hoorzitting',
                english: 'Hearing (formal meeting)',
                explanation: 'A hoorziting is a formal meeting where you can explain your side during an appeal or complaint procedure.',
                example: 'De hoorziting is volgende week donderdag. (The hearing is next Thursday.)',
              },
              {
                dutch: 'Uitslag',
                english: 'Result (of an exam)',
                explanation: 'The uitslag is the official published result of an exam or assessment.',
                example: 'De uitslag van het tentamen is bekend. (The exam result has been published.)',
              },
              {
                dutch: 'Inhaaltoets',
                english: 'Catch-up test',
                explanation: 'An inhaaltoets is an extra test opportunity, often for students who missed the original due to illness.',
                example: 'Er is een inhaaltoets voor studenten die ziek waren. (There is a catch-up test for students who were ill.)',
              },
            ],
            quiz: [
              {
                question: 'What does "bezwaar maken" mean?',
                options: [
                  'To submit an assignment',
                  'To file a formal objection / appeal',
                  'To ask for an extension',
                  'To join a group project',
                ],
                correctIndex: 1,
                explanation: '"Bezwaar maken" is the formal process of objecting to a grade or decision you disagree with.',
              },
              {
                question: 'What is a "hoorzitting"?',
                options: [
                  'A type of exam',
                  'A formal hearing where you explain your side',
                  'A group meeting',
                  'A deadline extension',
                ],
                correctIndex: 1,
                explanation: 'A "hoorziting" is a formal hearing — a meeting where you can present your case during an appeal or complaint.',
              },
              {
                question: 'What does "uitslag" mean in an academic context?',
                options: ['A delay', 'The official exam result', 'A resit', 'A draft'],
                correctIndex: 1,
                explanation: 'The "uitslag" is the official published result of an exam or assessment.',
              },
              {
                question: 'You were ill during the exam. What might you be offered?',
                options: ['Een herkansing', 'Een inhaaltoets', 'Een vrijstelling', 'Een bezwaar'],
                correctIndex: 1,
                explanation: 'An "inhaaltoets" is a catch-up test, often for students who missed the original exam due to illness.',
              },
              {
                question: 'What is "fraude" in a university setting?',
                options: [
                  'A type of assignment',
                  'Academic fraud / cheating',
                  'A grading method',
                  'A study credit',
                ],
                correctIndex: 1,
                explanation: '"Fraude" is academic fraud — cheating, plagiarism or other dishonest behaviour during assessments.',
              },
            ],
          },
        ],
      },
      {
        id: 'platforms-schedules',
        title: 'Course Platforms and Schedules',
        description: 'Navigate digital learning environments and timetables.',
        icon: 'Monitor',
        lessons: [
          {
            id: 'platforms-l1',
            title: 'Course Platforms and Schedules — Beginner',
            description: 'Learn the basic words for schedules, materials and online platforms.',
            difficulty: 1,
            flashcards: [
              {
                dutch: 'Rooster',
                english: 'Schedule / timetable',
                explanation: 'A rooster is your weekly timetable showing when and where your classes take place.',
                example: 'Het rooster verandert elke week. (The schedule changes every week.)',
              },
              {
                dutch: 'Lesmateriaal',
                english: 'Course materials',
                explanation: 'Lesmateriaal is everything you need for your lessons: slides, readings, videos and more.',
                example: 'Het lesmateriaal staat op Canvas. (The course materials are on Canvas.)',
              },
              {
                dutch: 'Hoorcollege',
                english: 'Lecture',
                explanation: 'A hoorcollege is a large lecture where a professor presents information to many students at once.',
                example: 'Het hoorcollege begint om 9:00. (The lecture starts at 9:00.)',
              },
              {
                dutch: 'Werkgroep',
                english: 'Workgroup / seminar',
                explanation: 'A werkgroep is a smaller, interactive class where you discuss and practise the material.',
                example: 'In de werkgroep oefenen we met cases. (In the workgroup we practise with cases.)',
              },
              {
                dutch: 'Lokaal',
                english: 'Classroom / room',
                explanation: 'A lokaal is the physical room where your class takes place.',
                example: 'Het lokaal is op de derde verdieping. (The classroom is on the third floor.)',
              },
              {
                dutch: 'Online platform',
                english: 'Online learning platform',
                explanation: 'An online platform like Canvas or Brightspace is where you find materials, submit work and see grades.',
                example: 'Je vindt de opdrachten op het online platform. (You can find the assignments on the online platform.)',
              },
            ],
            quiz: [
              {
                question: 'What is a "rooster"?',
                options: ['A lecture', 'A schedule / timetable', 'A classroom', 'An assignment'],
                correctIndex: 1,
                explanation: 'A "rooster" is your schedule or timetable showing when and where your classes take place.',
              },
              {
                question: 'What is a "hoorcollege"?',
                options: ['A small seminar', 'A large lecture', 'An online quiz', 'A deadline'],
                correctIndex: 1,
                explanation: 'A "hoorcollege" is a large lecture where a professor presents to many students at once.',
              },
              {
                question: 'What is a "werkgroep"?',
                options: [
                  'A large lecture',
                  'A small interactive workgroup or seminar',
                  'A type of exam',
                  'A grading system',
                ],
                correctIndex: 1,
                explanation: 'A "werkgroep" is a smaller, interactive class where you discuss and practise the course material.',
              },
              {
                question: 'Where can you find "lesmateriaal"?',
                options: ['Only in the library', 'On the online platform', 'In the exam', 'In the classroom only'],
                correctIndex: 1,
                explanation: '"Lesmateriaal" (course materials) is typically found on the online learning platform like Canvas or Brightspace.',
              },
              {
                question: 'What is a "lokaal"?',
                options: ['A schedule', 'A classroom / room', 'A lecture', 'A platform'],
                correctIndex: 1,
                explanation: 'A "lokaal" is the physical classroom or room where your class takes place.',
              },
            ],
          },
          {
            id: 'platforms-l2',
            title: 'Course Platforms and Schedules — Developing',
            description: 'Learn about course enrolment, announcements and digital submission.',
            difficulty: 2,
            flashcards: [
              {
                dutch: 'Inschrijven',
                english: 'To enrol / register',
                explanation: 'Inschrijven means to register for a course, often through an online system like OSIRIS.',
                example: 'Je moet je vandaag inschrijven voor het vak. (You have to enrol for the course today.)',
              },
              {
                dutch: 'Uitschrijven',
                english: 'To deregister / unenrol',
                explanation: 'Uitschrijven means to remove yourself from a course before a certain deadline.',
                example: 'Je kunt je tot friday uitschrijven. (You can deregister until Friday.)',
              },
              {
                dutch: 'Mededeling',
                english: 'Announcement',
                explanation: 'A mededeling is a message from your teacher or faculty, often posted on the online platform.',
                example: 'Er is een nieuwe mededeling op Canvas. (There is a new announcement on Canvas.)',
              },
              {
                dutch: 'Digitaal inleveren',
                english: 'To submit digitally',
                explanation: 'Digitaal inleveren means uploading your assignment through the online platform.',
                example: 'Je moet digitaal inleveren via Brightspace. (You must submit digitally via Brightspace.)',
              },
              {
                dutch: 'Werkcollege',
                english: 'Practical / tutorial',
                explanation: 'A werkcollege is a hands-on session where you apply what you learned in the lectures.',
                example: 'Tijdens het werkcollege werken we in groepjes. (During the practical we work in small groups.)',
              },
              {
                dutch: 'Zelfstudie',
                english: 'Self-study',
                explanation: 'Zelfstudie is the time you spend studying on your own outside of scheduled classes.',
                example: 'Je moet ongeveer 10 uur zelfstudie per week doen. (You should do about 10 hours of self-study per week.)',
              },
            ],
            quiz: [
              {
                question: 'What does "inschrijven" mean?',
                options: ['To submit work', 'To enrol / register for a course', 'To grade an exam', 'To attend a lecture'],
                correctIndex: 1,
                explanation: '"Inschrijven" means to enrol or register for a course, usually through an online system.',
              },
              {
                question: 'What is a "mededeling"?',
                options: ['A grade', 'An announcement', 'A deadline', 'A classroom'],
                correctIndex: 1,
                explanation: 'A "mededeling" is an announcement — a message from your teacher or faculty, often on the online platform.',
              },
              {
                question: 'What does "digitaal inleveren" mean?',
                options: [
                  'To hand in a physical copy',
                  'To submit digitally via an online platform',
                  'To register for a course',
                  'To attend a lecture',
                ],
                correctIndex: 1,
                explanation: '"Digitaal inleveren" means to submit your work digitally by uploading it through the online platform.',
              },
              {
                question: 'What is a "werkcollege"?',
                options: ['A lecture', 'A hands-on practical session', 'An exam', 'An announcement'],
                correctIndex: 1,
                explanation: 'A "werkcollege" is a practical or tutorial — a hands-on session where you apply what you learned in lectures.',
              },
              {
                question: 'What is "zelfstudie"?',
                options: ['A group project', 'Self-study on your own time', 'A type of exam', 'A lecture format'],
                correctIndex: 1,
                explanation: '"Zelfstudie" is self-study — time you spend studying independently outside of scheduled classes.',
              },
            ],
          },
          {
            id: 'platforms-l3',
            title: 'Course Platforms and Schedules — Confident',
            description: 'Manage your study planning, electives and academic calendar.',
            difficulty: 3,
            flashcards: [
              {
                dutch: 'Keuzevak',
                english: 'Elective course',
                explanation: 'A keuzevak is a course you choose yourself, as opposed to a mandatory (verplicht) course.',
                example: 'Filosofie is mijn keuzevak dit semester. (Philosophy is my elective this semester.)',
              },
              {
                dutch: 'Verplicht vak',
                english: 'Mandatory / compulsory course',
                explanation: 'A verplicht vak is a course every student in your programme must take.',
                example: 'Statistiek is een verplicht vak. (Statistics is a compulsory course.)',
              },
              {
                dutch: 'Studieplanning',
                english: 'Study planning',
                explanation: 'Studieplanning is how you organise your time and tasks across the semester to meet all deadlines.',
                example: 'Goede studieplanning helpt je stress te voorkomen. (Good study planning helps you avoid stress.)',
              },
              {
                dutch: 'Academisch jaar',
                english: 'Academic year',
                explanation: 'The academisch jaar runs from September to July and is divided into semesters or quarters.',
                example: 'Het academisch jaar start in september. (The academic year starts in September.)',
              },
              {
                dutch: 'Blok',
                english: 'Block / term (quarter)',
                explanation: 'A blok is a short teaching period, often 8 to 10 weeks. Many Dutch universities use a blok system.',
                example: 'In blok 1 hebben we drie vakken. (In block 1 we have three courses.)',
              },
            ],
            quiz: [
              {
                question: 'What is a "keuzevak"?',
                options: ['A mandatory course', 'An elective course you choose', 'A resit', 'A type of exam'],
                correctIndex: 1,
                explanation: 'A "keuzevak" is an elective — a course you choose yourself, as opposed to a mandatory course.',
              },
              {
                question: 'What is a "verplicht vak"?',
                options: ['An elective', 'A mandatory / compulsory course', 'A group project', 'A deadline'],
                correctIndex: 1,
                explanation: 'A "verplicht vak" is a mandatory course that every student in your programme must take.',
              },
              {
                question: 'What is "studieplanning"?',
                options: [
                  'A type of exam',
                  'How you organise your study time and tasks',
                  'A course platform',
                  'A grading system',
                ],
                correctIndex: 1,
                explanation: '"Studieplanning" is study planning — organising your time and tasks across the semester.',
              },
              {
                question: 'What is a "blok"?',
                options: ['A full year', 'A short teaching period (block/quarter)', 'A type of exam', 'An elective'],
                correctIndex: 1,
                explanation: 'A "blok" is a short teaching period, often 8-10 weeks. Many Dutch universities use this system.',
              },
              {
                question: 'When does the "academisch jaar" typically start in the Netherlands?',
                options: ['January', 'September', 'April', 'November'],
                correctIndex: 1,
                explanation: 'The "academisch jaar" (academic year) typically starts in September and runs until July.',
              },
            ],
          },
        ],
      },
    ],
  },
  {
    id: 'classroom-teachers',
    title: 'Classroom and Teachers',
    description: 'Learn how to follow instructions, talk to lecturers and ask for help.',
    color: 'accent',
    accentColor: 'amber',
    topics: [
      {
        id: 'classroom-instructions',
        title: 'Classroom Instructions',
        description: 'Understand the instructions your teachers give during class.',
        icon: 'Presentation',
        lessons: [
          {
            id: 'classroom-l1',
            title: 'Classroom Instructions — Beginner',
            description: 'Learn the most common instructions you will hear in a Dutch classroom.',
            difficulty: 1,
            flashcards: [
              {
                dutch: 'Luister goed',
                english: 'Listen carefully',
                explanation: 'Luister goed is what a teacher says when they want everyone to pay attention.',
                example: 'Luister goed, ik leg het nu uit. (Listen carefully, I will explain it now.)',
              },
              {
                dutch: 'Maak groepjes',
                english: 'Form groups',
                explanation: 'Maak groepjes means the teacher wants you to divide into small groups for an activity.',
                example: 'Maak groepjes van drie personen. (Form groups of three people.)',
              },
              {
                dutch: 'Open je boek op pagina…',
                english: 'Open your book to page…',
                explanation: 'This instruction tells you which page to open in your textbook or reader.',
                example: 'Open je boek op pagina 42. (Open your book to page 42.)',
              },
              {
                dutch: 'Maak aantekeningen',
                english: 'Take notes',
                explanation: 'Maak aantekeningen means you should write down important points during the lesson.',
                example: 'Maak aantekeningen tijdens de uitleg. (Take notes during the explanation.)',
              },
              {
                dutch: 'Zet je telefoon uit',
                english: 'Turn off your phone',
                explanation: 'Zet je telefoon uit is a request to silence or switch off your phone during class.',
                example: 'Zet je telefoon uit tijdens het tentamen. (Turn off your phone during the exam.)',
              },
              {
                dutch: 'Aanwezigheid',
                english: 'Attendance',
                explanation: 'Aanwezigheid refers to whether you are present in class. Some courses require a minimum attendance.',
                example: 'De aanwezigheid is verplicht. (Attendance is mandatory.)',
              },
            ],
            quiz: [
              {
                question: 'Your teacher says "Maak groepjes." What should you do?',
                options: ['Leave the classroom', 'Form small groups', 'Open your book', 'Take notes'],
                correctIndex: 1,
                explanation: '"Maak groepjes" means to form small groups for an activity.',
              },
              {
                question: 'What does "Maak aantekeningen" mean?',
                options: ['Open your book', 'Take notes', 'Turn off your phone', 'Listen carefully'],
                correctIndex: 1,
                explanation: '"Maak aantekeningen" means to take notes — write down important points during the lesson.',
              },
              {
                question: 'What does "Aanwezigheid is verplicht" mean?',
                options: ['Attendance is optional', 'Attendance is mandatory', 'The exam is starting', 'Groups are required'],
                correctIndex: 1,
                explanation: '"Aanwezigheid" means attendance. "Verplicht" means mandatory, so attendance is required.',
              },
              {
                question: 'Your teacher says "Luister goed." What are they asking?',
                options: ['To speak louder', 'To listen carefully', 'To form groups', 'To leave the room'],
                correctIndex: 1,
                explanation: '"Luister goed" means listen carefully — the teacher wants everyone to pay attention.',
              },
              {
                question: 'What does "Zet je telefoon uit" mean?',
                options: ['Turn on your phone', 'Turn off your phone', 'Call someone', 'Send a message'],
                correctIndex: 1,
                explanation: '"Zet je telefoon uit" means turn off your phone — usually requested during class or exams.',
              },
            ],
          },
          {
            id: 'classroom-l2',
            title: 'Classroom Instructions — Developing',
            description: 'Follow more complex classroom instructions and group dynamics.',
            difficulty: 2,
            flashcards: [
              {
                dutch: 'Werk samen',
                english: 'Work together',
                explanation: 'Werk samen means you should collaborate with your classmates on a task.',
                example: 'Werk samen aan de casus. (Work together on the case study.)',
              },
              {
                dutch: 'Presenteer je bevindingen',
                english: 'Present your findings',
                explanation: 'Presenteer je bevindingen means you should share your results with the class.',
                example: 'Presenteer je bevindingen aan de groep. (Present your findings to the group.)',
              },
              {
                dutch: 'Denk na over',
                english: 'Think about / reflect on',
                explanation: 'Denk na over means the teacher wants you to consider or reflect on a topic.',
                example: 'Denk na over de ethische kanten. (Think about the ethical aspects.)',
              },
              {
                dutch: 'Lever je bijdrage',
                english: 'Contribute / give your input',
                explanation: 'Lever je bijdrage means you should actively participate and share your ideas.',
                example: 'Iedereen moet zijn bijdrage leveren. (Everyone must contribute.)',
              },
              {
                dutch: 'Houd je aan de tijd',
                english: 'Stick to the time / keep to the time',
                explanation: 'Houd je aan de tijd means you should finish within the time limit given.',
                example: 'Houd je aan de tijd tijdens de presentatie. (Stick to the time during the presentation.)',
              },
              {
                dutch: 'Stel jezelf voor',
                english: 'Introduce yourself',
                explanation: 'Stel jezelf voor means to say your name and a bit about yourself to the group.',
                example: 'Stel jezelf voor aan de groep. (Introduce yourself to the group.)',
              },
            ],
            quiz: [
              {
                question: 'Your teacher says "Presenteer je bevindingen." What should you do?',
                options: [
                  'Write a report',
                  'Present your findings to the class',
                  'Form groups',
                  'Take notes',
                ],
                correctIndex: 1,
                explanation: '"Presenteer je bevindingen" means to present your findings — share your results with the class.',
              },
              {
                question: 'What does "Lever je bijdrage" mean?',
                options: ['Submit your work', 'Contribute / give your input', 'Take notes', 'Listen carefully'],
                correctIndex: 1,
                explanation: '"Lever je bijdrage" means to contribute — actively participate and share your ideas.',
              },
              {
                question: 'What does "Houd je aan de tijd" mean?',
                options: ['Arrive on time', 'Stick to the time limit', 'Skip the task', 'Work alone'],
                correctIndex: 1,
                explanation: '"Houd je aan de tijd" means to stick to the time — finish within the time limit given.',
              },
              {
                question: 'What does "Denk na over" mean?',
                options: ['Forget about', 'Think about / reflect on', 'Submit', 'Present'],
                correctIndex: 1,
                explanation: '"Denk na over" means to think about or reflect on a topic.',
              },
              {
                question: 'What does "Stel jezelf voor" mean?',
                options: ['Sit down', 'Introduce yourself', 'Leave the room', 'Form a group'],
                correctIndex: 1,
                explanation: '"Stel jezelf voor" means to introduce yourself — say your name and a bit about yourself.',
              },
            ],
          },
          {
            id: 'classroom-l3',
            title: 'Classroom Instructions — Confident',
            description: 'Handle advanced classroom scenarios and peer feedback.',
            difficulty: 3,
            flashcards: [
              {
                dutch: 'Bespreek de uitkomsten',
                english: 'Discuss the outcomes',
                explanation: 'Bespreken means to discuss. The teacher wants the class to talk about the results together.',
                example: 'We bespreken de uitkomsten na de pauze. (We will discuss the outcomes after the break.)',
              },
              {
                dutch: 'Geef elkaar feedback',
                english: 'Give each other feedback',
                explanation: 'Geef elkaar feedback means students should review and comment on each other\'s work.',
                example: 'Geef elkaar feedback op de conceptversies. (Give each other feedback on the drafts.)',
              },
              {
                dutch: 'Verdedig je standpunt',
                english: 'Defend your viewpoint / argument',
                explanation: 'Verdedig je standpunt means you should explain and support your opinion with arguments.',
                example: 'Verdedig je standpunt met voorbeelden. (Defend your viewpoint with examples.)',
              },
              {
                dutch: 'Samenvatten',
                english: 'To summarise',
                explanation: 'Samenvatten means to give a short overview of the main points.',
                example: 'Kun je de tekst samenvatten? (Can you summarise the text?)',
              },
              {
                dutch: 'Trek conclusies',
                english: 'Draw conclusions',
                explanation: 'Trek conclusies means to state what you learned or decided based on the information.',
                example: 'Trek conclusies uit de data. (Draw conclusions from the data.)',
              },
            ],
            quiz: [
              {
                question: 'What does "Bespreken de uitkomsten" mean?',
                options: [
                  'Submit the outcomes',
                  'Discuss the outcomes together',
                  'Ignore the outcomes',
                  'Grade the outcomes',
                ],
                correctIndex: 1,
                explanation: '"Bespreken" means to discuss. The teacher wants the class to talk about the results together.',
              },
              {
                question: 'What does "Geef elkaar feedback" mean?',
                options: [
                  'Ask the teacher for feedback',
                  'Give each other feedback on your work',
                  'Skip the feedback step',
                  'Submit without feedback',
                ],
                correctIndex: 1,
                explanation: '"Geef elkaar feedback" means students should review and comment on each other\'s work.',
              },
              {
                question: 'What does "Verdedig je standpunt" mean?',
                options: [
                  'Change your opinion',
                  'Defend your viewpoint with arguments',
                  'Submit your work',
                  'Summarise the text',
                ],
                correctIndex: 1,
                explanation: '"Verdedig je standpunt" means to defend your viewpoint — explain and support your opinion with arguments.',
              },
              {
                question: 'What does "Samenvatten" mean?',
                options: ['To expand', 'To summarise', 'To submit', 'To discuss'],
                correctIndex: 1,
                explanation: '"Samenvatten" means to summarise — give a short overview of the main points.',
              },
              {
                question: 'What does "Trek conclusies" mean?',
                options: ['Postpone a decision', 'Draw conclusions', 'Start a debate', 'Take notes'],
                correctIndex: 1,
                explanation: '"Trek conclusies" means to draw conclusions — state what you learned or decided based on the information.',
              },
            ],
          },
        ],
      },
      {
        id: 'talking-to-lecturers',
        title: 'Talking to Lecturers',
        description: 'Communicate politely with your professors and teachers.',
        icon: 'MessageCircle',
        lessons: [
          {
            id: 'talking-l1',
            title: 'Talking to Lecturers — Beginner',
            description: 'Learn polite phrases for approaching and addressing your lecturers.',
            difficulty: 1,
            flashcards: [
              {
                dutch: 'Mag ik een vraag stellen?',
                english: 'May I ask a question?',
                explanation: 'This is a polite way to ask for permission before asking something in class.',
                example: 'Mag ik een vraag stellen over de opdracht? (May I ask a question about the assignment?)',
              },
              {
                dutch: 'Ik begrijp het niet',
                english: 'I don\'t understand',
                explanation: 'Use this when you need the teacher to explain something again or more slowly.',
                example: 'Ik begrijp het niet helemaal. (I don\'t quite understand.)',
              },
              {
                dutch: 'Kunt u dat herhalen?',
                english: 'Could you repeat that?',
                explanation: 'A polite way to ask the teacher to say something again.',
                example: 'Kunt u dat herhalen, alstublieft? (Could you repeat that, please?)',
              },
              {
                dutch: 'Hoe spel je dat?',
                english: 'How do you spell that?',
                explanation: 'Use this when you need to know the spelling of a Dutch word.',
                example: 'Hoe spel je "tentamen"? (How do you spell "tentamen"?)',
              },
              {
                dutch: 'Ik begrijp de instructie nog niet',
                english: 'I still don\'t understand the instruction',
                explanation: 'Use this when the explanation was not clear enough and you need more help.',
                example: 'Ik begrijp de instructie nog niet. Kunt u het uitleggen? (I still don\'t understand the instruction. Could you explain it?)',
              },
              {
                dutch: 'Spreekt u Engels?',
                english: 'Do you speak English?',
                explanation: 'A polite way to ask if the teacher can switch to English if your Dutch is not yet strong enough.',
                example: 'Spreekt u Engels? Mijn Nederlands is nog niet zo goed. (Do you speak English? My Dutch isn\'t that good yet.)',
              },
            ],
            quiz: [
              {
                question: 'You want to ask something in class. What do you say first?',
                options: [
                  'Ik begrijp het niet',
                  'Mag ik een vraag stellen?',
                  'Spreekt u Engels?',
                  'Hoe spel je dat?',
                ],
                correctIndex: 1,
                explanation: '"Mag ik een vraag stellen?" means "May I ask a question?" — a polite way to ask for permission first.',
              },
              {
                question: 'You didn\'t catch what the teacher said. What do you ask?',
                options: [
                  'Kunt u dat herhalen?',
                  'Mag ik een vraag stellen?',
                  'Ik begrijp het niet',
                  'Spreekt u Engels?',
                ],
                correctIndex: 0,
                explanation: '"Kunt u dat herhalen?" means "Could you repeat that?" — a polite way to ask the teacher to say it again.',
              },
              {
                question: 'What does "Ik begrijp het niet" mean?',
                options: ['I understand it', 'I don\'t understand', 'Please repeat', 'I have a question'],
                correctIndex: 1,
                explanation: '"Ik begrijp het niet" means "I don\'t understand" — use it when you need more explanation.',
              },
              {
                question: 'What does "Spreekt u Engels?" mean?',
                options: ['Do you speak Dutch?', 'Do you speak English?', 'Can you repeat?', 'Can I ask?'],
                correctIndex: 1,
                explanation: '"Spreekt u Engels?" means "Do you speak English?" — useful if your Dutch is not yet strong enough.',
              },
              {
                question: 'You need to know how to write a word. What do you ask?',
                options: [
                  'Hoe spel je dat?',
                  'Mag ik een vraag stellen?',
                  'Kunt u dat herhalen?',
                  'Ik begrijp het niet',
                ],
                correctIndex: 0,
                explanation: '"Hoe spel je dat?" means "How do you spell that?" — use it when you need the spelling of a word.',
              },
            ],
          },
          {
            id: 'talking-l2',
            title: 'Talking to Lecturers — Developing',
            description: 'Ask for clarification, examples and email communication.',
            difficulty: 2,
            flashcards: [
              {
                dutch: 'Kunt u dit nog een keer uitleggen?',
                english: 'Could you explain this once more?',
                explanation: 'A polite way to ask the teacher to go over something again.',
                example: 'Kunt u dit nog een keer uitleggen? Ik snap het niet helemaal. (Could you explain this once more? I don\'t quite get it.)',
              },
              {
                dutch: 'Heeft u een voorbeeld?',
                english: 'Do you have an example?',
                explanation: 'Use this to ask for a concrete example to help you understand.',
                example: 'Heeft u een voorbeeld van een goede opdracht? (Do you have an example of a good assignment?)',
              },
              {
                dutch: 'Waar kan ik de opdracht inleveren?',
                english: 'Where can I submit the assignment?',
                explanation: 'Use this to ask where or how to hand in your work.',
                example: 'Waar kan ik de opdracht inleveren? Op Canvas? (Where can I submit the assignment? On Canvas?)',
              },
              {
                dutch: 'Wanneer is de deadline?',
                english: 'When is the deadline?',
                explanation: 'A simple and essential question to ask when you are unsure about a due date.',
                example: 'Wanneer is de deadline voor het verslag? (When is the deadline for the report?)',
              },
              {
                dutch: 'Ik stuur u een e-mail',
                english: 'I will send you an email',
                explanation: 'Use this to let a teacher know you will follow up by email.',
                example: 'Ik stuur u een e-mail na de les. (I will send you an email after class.)',
              },
              {
                dutch: 'Geachte heer/mevrouw',
                english: 'Dear sir/madam',
                explanation: 'This is the formal way to start an email to a teacher in Dutch.',
                example: 'Geachte heer/mevrouw, ik heb een vraag over de opdracht. (Dear sir/madam, I have a question about the assignment.)',
              },
            ],
            quiz: [
              {
                question: 'You want the teacher to explain something again. What do you say?',
                options: [
                  'Wanneer is de deadline?',
                  'Kunt u dit nog een keer uitleggen?',
                  'Heeft u een voorbeeld?',
                  'Ik stuur u een e-mail',
                ],
                correctIndex: 1,
                explanation: '"Kunt u dit nog een keer uitleggen?" means "Could you explain this once more?" — a polite request to go over something again.',
              },
              {
                question: 'You want to know where to hand in your work. What do you ask?',
                options: [
                  'Waar kan ik de opdracht inleveren?',
                  'Wanneer is de deadline?',
                  'Heeft u een voorbeeld?',
                  'Ik begrijp het niet',
                ],
                correctIndex: 0,
                explanation: '"Waar kan ik de opdracht inleveren?" means "Where can I submit the assignment?" — asking where or how to hand in work.',
              },
              {
                question: 'How do you formally start an email to a teacher in Dutch?',
                options: [
                  'Hallo!',
                  'Geachte heer/mevrouw',
                  'Beste docent',
                  'Hoi!',
                ],
                correctIndex: 1,
                explanation: '"Geachte heer/mevrouw" is the formal way to start an email to a teacher in Dutch.',
              },
              {
                question: 'What does "Heeft u een voorbeeld?" mean?',
                options: [
                  'Do you have an example?',
                  'When is the deadline?',
                  'Could you repeat that?',
                  'I will send an email',
                ],
                correctIndex: 0,
                explanation: '"Heeft u een voorbeeld?" means "Do you have an example?" — useful when you need a concrete example to understand.',
              },
              {
                question: 'What does "Wanneer is de deadline?" mean?',
                options: ['Where is the class?', 'When is the deadline?', 'What is the grade?', 'Who is the teacher?'],
                correctIndex: 1,
                explanation: '"Wanneer is de deadline?" means "When is the deadline?" — an essential question about due dates.',
              },
            ],
          },
          {
            id: 'talking-l3',
            title: 'Talking to Lecturers — Confident',
            description: 'Handle formal communication, office hours and academic discussions.',
            difficulty: 3,
            flashcards: [
              {
                dutch: 'Spreekuur',
                english: 'Office hours / consultation hour',
                explanation: 'A spreekuur is a set time when the teacher is available for questions, either in person or online.',
                example: 'Het spreekuur is op woensdag van 14:00 tot 15:00. (Office hours are on Wednesday from 14:00 to 15:00.)',
              },
              {
                dutch: 'Ik zou graag een afspraak maken',
                english: 'I would like to make an appointment',
                explanation: 'A polite, formal way to request a meeting with your teacher.',
                example: 'Ik zou graag een afspraak maken met u. (I would like to make an appointment with you.)',
              },
              {
                dutch: 'Kunt u mij verwijzen naar relevante literatuur?',
                english: 'Could you point me to relevant literature?',
                explanation: 'A formal way to ask the teacher for recommended reading or sources.',
                example: 'Kunt u mij verwijzen naar relevante literatuur voor mijn scriptie? (Could you point me to relevant literature for my thesis?)',
              },
              {
                dutch: 'Ik waardeer uw feedback',
                english: 'I appreciate your feedback',
                explanation: 'A polite phrase to thank a teacher for their comments on your work.',
                example: 'Ik waardeer uw feedback op mijn verslag. (I appreciate your feedback on my report.)',
              },
              {
                dutch: 'Met vriendelijke groet',
                english: 'Kind regards',
                explanation: 'The standard formal way to close an email in Dutch, similar to "Kind regards" in English.',
                example: 'Met vriendelijke groet, [naam] (Kind regards, [name])',
              },
            ],
            quiz: [
              {
                question: 'What is a "spreekuur"?',
                options: [
                  'A type of exam',
                  'Office hours / a set time for student questions',
                  'A group assignment',
                  'A lecture format',
                ],
                correctIndex: 1,
                explanation: 'A "spreekuur" is office hours — a set time when the teacher is available for questions, in person or online.',
              },
              {
                question: 'You want to formally request a meeting. What do you say?',
                options: [
                  'Ik begrijp het niet',
                  'Ik zou graag een afspraak maken',
                  'Wanneer is de deadline?',
                  'Heeft u een voorbeeld?',
                ],
                correctIndex: 1,
                explanation: '"Ik zou graag een afspraak maken" means "I would like to make an appointment" — a polite, formal request.',
              },
              {
                question: 'How do you formally close an email in Dutch?',
                options: ['Tot ziens!', 'Met vriendelijke groet', 'Doei!', 'Hoi!'],
                correctIndex: 1,
                explanation: '"Met vriendelijke groet" is the standard formal way to close an email in Dutch, like "Kind regards".',
              },
              {
                question: 'What does "Kunt u mij verwijzen naar relevante literatuur?" mean?',
                options: [
                  'Could you repeat the lecture?',
                  'Could you point me to relevant literature?',
                  'Could you extend the deadline?',
                  'Could you grade my work?',
                ],
                correctIndex: 1,
                explanation: 'This means "Could you point me to relevant literature?" — a formal way to ask for recommended reading.',
              },
              {
                question: 'What does "Ik waardeer uw feedback" mean?',
                options: [
                  'I disagree with your feedback',
                  'I appreciate your feedback',
                  'I need more feedback',
                  'I will ignore your feedback',
                ],
                correctIndex: 1,
                explanation: '"Ik waardeer uw feedback" means "I appreciate your feedback" — a polite way to thank a teacher.',
              },
            ],
          },
        ],
      },
      {
        id: 'asking-questions-help',
        title: 'Asking Questions and Requesting Help',
        description: 'Know how to ask for help and support at university.',
        icon: 'HelpCircle',
        lessons: [
          {
            id: 'asking-l1',
            title: 'Asking Questions and Requesting Help — Beginner',
            description: 'Learn the essential phrases for asking for help.',
            difficulty: 1,
            flashcards: [
              {
                dutch: 'Ik heb hulp nodig',
                english: 'I need help',
                explanation: 'A simple and direct way to say you need assistance.',
                example: 'Ik heb hulp nodig met de opdracht. (I need help with the assignment.)',
              },
              {
                dutch: 'Kunt u mij helpen?',
                english: 'Can you help me?',
                explanation: 'A polite way to ask someone — usually a teacher or staff member — for help.',
                example: 'Kunt u mij helpen met dit formulier? (Can you help me with this form?)',
              },
              {
                dutch: 'Waar is…?',
                english: 'Where is…?',
                explanation: 'A useful question pattern for finding rooms, buildings or offices on campus.',
                example: 'Waar is de bibliotheek? (Where is the library?)',
              },
              {
                dutch: 'Hoe werkt dit?',
                english: 'How does this work?',
                explanation: 'Use this when you do not understand how something — a platform, a tool or a process — functions.',
                example: 'Hoe werkt het online platform? (How does the online platform work?)',
              },
              {
                dutch: 'Ik weet het niet',
                english: 'I don\'t know',
                explanation: 'A simple phrase to say you are unsure or do not have the answer.',
                example: 'Ik weet het niet, sorry. (I don\'t know, sorry.)',
              },
              {
                dutch: 'Kunt u langzamer praten?',
                english: 'Could you speak more slowly?',
                explanation: 'A polite way to ask the teacher to slow down so you can follow better.',
                example: 'Kunt u iets langzamer praten, alstublieft? (Could you speak a bit more slowly, please?)',
              },
            ],
            quiz: [
              {
                question: 'What does "Ik heb hulp nodig" mean?',
                options: ['I have a question', 'I need help', 'I am finished', 'I understand'],
                correctIndex: 1,
                explanation: '"Ik heb hulp nodig" means "I need help" — a simple and direct way to ask for assistance.',
              },
              {
                question: 'You cannot find the library. What do you ask?',
                options: ['Hoe werkt dit?', 'Waar is de bibliotheek?', 'Ik weet het niet', 'Ik heb hulp nodig'],
                correctIndex: 1,
                explanation: '"Waar is de bibliotheek?" means "Where is the library?" — using the "Waar is…?" pattern.',
              },
              {
                question: 'The teacher is speaking too fast. What do you say?',
                options: [
                  'Kunt u langzamer praten?',
                  'Ik weet het niet',
                  'Waar is…?',
                  'Hoe werkt dit?',
                ],
                correctIndex: 0,
                explanation: '"Kunt u langzamer praten?" means "Could you speak more slowly?" — a polite request to slow down.',
              },
              {
                question: 'What does "Hoe werkt dit?" mean?',
                options: ['Where is this?', 'How does this work?', 'Who is this?', 'When is this?'],
                correctIndex: 1,
                explanation: '"Hoe werkt dit?" means "How does this work?" — useful when you do not understand a tool or process.',
              },
              {
                question: 'What does "Kunt u mij helpen?" mean?',
                options: ['Can you repeat?', 'Can you help me?', 'Can you speak slowly?', 'Can you grade this?'],
                correctIndex: 1,
                explanation: '"Kunt u mij helpen?" means "Can you help me?" — a polite way to ask for assistance.',
              },
            ],
          },
          {
            id: 'asking-l2',
            title: 'Asking Questions and Requesting Help — Developing',
            description: 'Ask for extensions, clarification and study support.',
            difficulty: 2,
            flashcards: [
              {
                dutch: 'Kan ik uitstel krijgen?',
                english: 'Can I get an extension?',
                explanation: 'A direct way to ask for more time on an assignment.',
                example: 'Kan ik uitstel krijgen voor de deadline? (Can I get an extension for the deadline?)',
              },
              {
                dutch: 'Ik heb meer uitleg nodig',
                english: 'I need more explanation',
                explanation: 'Use this to say the current explanation was not enough and you need more detail.',
                example: 'Ik heb meer uitleg nodig over dit onderwerp. (I need more explanation about this topic.)',
              },
              {
                dutch: 'Waar kan ik extra materiaal vinden?',
                english: 'Where can I find extra materials?',
                explanation: 'Use this to ask for additional readings or resources to study.',
                example: 'Waar kan ik extra materiaal vinden voor dit vak? (Where can I find extra materials for this course?)',
              },
              {
                dutch: 'Is er een werkgroep voor dit vak?',
                english: 'Is there a workgroup for this course?',
                explanation: 'Use this to ask if there are smaller practice sessions you can join.',
                example: 'Is er een werkgroep voor dit vak? (Is there a workgroup for this course?)',
              },
              {
                dutch: 'Kan ik de slides krijgen?',
                english: 'Can I get the slides?',
                explanation: 'A common request to ask for the lecture slides, often for review.',
                example: 'Kan ik de slides van de les krijgen? (Can I get the slides from the lesson?)',
              },
              {
                dutch: 'Ik mis een les',
                english: 'I will miss a class',
                explanation: 'Use this to inform the teacher you cannot attend a particular session.',
                example: 'Ik mis een les volgende week door een afspraak. (I will miss a class next week due to an appointment.)',
              },
            ],
            quiz: [
              {
                question: 'You need more time on your assignment. What do you ask?',
                options: [
                  'Kan ik uitstel krijgen?',
                  'Kan ik de slides krijgen?',
                  'Is er een werkgroep?',
                  'Ik mis een les',
                ],
                correctIndex: 0,
                explanation: '"Kan ik uitstel krijgen?" means "Can I get an extension?" — a direct way to ask for more time.',
              },
              {
                question: 'What does "Ik heb meer uitleg nodig" mean?',
                options: [
                  'I need more explanation',
                  'I need more time',
                  'I need the slides',
                  'I need to miss class',
                ],
                correctIndex: 0,
                explanation: '"Ik heb meer uitleg nodig" means "I need more explanation" — the current explanation was not enough.',
              },
              {
                question: 'You want the lecture slides. What do you ask?',
                options: [
                  'Waar kan ik extra materiaal vinden?',
                  'Kan ik de slides krijgen?',
                  'Is er een werkgroep?',
                  'Kan ik uitstel krijgen?',
                ],
                correctIndex: 1,
                explanation: '"Kan ik de slides krijgen?" means "Can I get the slides?" — a common request for lecture slides.',
              },
              {
                question: 'What does "Ik mis een les" mean?',
                options: ['I missed the exam', 'I will miss a class', 'I finished a class', 'I am late'],
                correctIndex: 1,
                explanation: '"Ik mis een les" means "I will miss a class" — use it to inform the teacher you cannot attend.',
              },
              {
                question: 'You want to know if there are practice sessions. What do you ask?',
                options: [
                  'Is er een werkgroep voor dit vak?',
                  'Kan ik de slides krijgen?',
                  'Waar is de bibliotheek?',
                  'Ik weet het niet',
                ],
                correctIndex: 0,
                explanation: '"Is er een werkgroep voor dit vak?" means "Is there a workgroup for this course?" — asking about practice sessions.',
              },
            ],
          },
          {
            id: 'asking-l3',
            title: 'Asking Questions and Requesting Help — Confident',
            description: 'Navigate student support services, mentors and formal requests.',
            difficulty: 3,
            flashcards: [
              {
                dutch: 'Studieadviseur',
                english: 'Study advisor / academic counsellor',
                explanation: 'A studieadviseur is a staff member who helps you with study planning, personal issues and academic choices.',
                example: 'Ik heb een afspraak met de studieadviseur. (I have an appointment with the study advisor.)',
              },
              {
                dutch: 'Decaan',
                english: 'Dean (student dean / counsellor)',
                explanation: 'A decaan helps with formal complaints, disputes and serious personal circumstances affecting your studies.',
                example: 'Je kunt naar de decaan als je een conflict hebt. (You can go to the dean if you have a conflict.)',
              },
              {
                dutch: 'Bijzondere omstandigheden',
                english: 'Special / extenuating circumstances',
                explanation: 'Bijzondere omstandigheden are personal situations (illness, family issues) that may justify extensions or exceptions.',
                example: 'Bij bijzondere omstandigheden kun je uitstel vragen. (In special circumstances you can request an extension.)',
              },
              {
                dutch: 'Gemachtigde',
                english: 'Authorised representative',
                explanation: 'A gemachtigde is someone who officially represents you, for example on a complaint or appeal.',
                example: 'Je kunt een gemachtigde meenemen naar de hoorzitting. (You can bring an authorised representative to the hearing.)',
              },
              {
                dutch: 'Verzoek tot goedkeuring',
                english: 'Request for approval',
                explanation: 'A formal request — for example, to approve a course choice, a thesis plan or an exception.',
                example: 'Mijn verzoek tot goedkeuring is ingediend. (My request for approval has been submitted.)',
              },
            ],
            quiz: [
              {
                question: 'Who helps with study planning and personal academic issues?',
                options: ['De decaan', 'De studieadviseur', 'De docent', 'De examinator'],
                correctIndex: 1,
                explanation: 'The "studieadviseur" (study advisor) helps with study planning, personal issues and academic choices.',
              },
              {
                question: 'You have a formal conflict at university. Who can help?',
                options: ['De studieadviseur', 'De decaan', 'De werkgroepdocent', 'De mentor'],
                correctIndex: 1,
                explanation: 'The "decaan" (student dean) helps with formal complaints, disputes and serious personal circumstances.',
              },
              {
                question: 'What are "bijzondere omstandigheden"?',
                options: [
                  'Special / extenuating circumstances',
                  'Normal study routines',
                  'Group project rules',
                  'Exam results',
                ],
                correctIndex: 0,
                explanation: '"Bijzondere omstandigheden" are special or extenuating circumstances (illness, family issues) that may justify exceptions.',
              },
              {
                question: 'What is a "gemachtigde"?',
                options: [
                  'A type of exam',
                  'An authorised representative',
                  'A study advisor',
                  'A group leader',
                ],
                correctIndex: 1,
                explanation: 'A "gemachtigde" is an authorised representative — someone who officially represents you, e.g. at a hearing.',
              },
              {
                question: 'What is a "verzoek tot goedkeuring"?',
                options: [
                  'A request for approval',
                  'A request for an extension',
                  'A type of exam',
                  'A grade appeal',
                ],
                correctIndex: 0,
                explanation: 'A "verzoek tot goedkeuring" is a formal request for approval — for example, of a course choice or thesis plan.',
              },
            ],
          },
        ],
      },
    ],
  },
];

export const badges: Badge[] = [
  {
    id: 'first-lesson',
    title: 'First Lesson',
    description: 'Complete your first lesson.',
    icon: 'BookOpen',
  },
  {
    id: 'quick-learner',
    title: 'Quick Learner',
    description: 'Score 80% or higher on any quiz.',
    icon: 'Zap',
  },
  {
    id: 'perfect-score',
    title: 'Perfect Score',
    description: 'Get 100% on a quiz.',
    icon: 'Award',
  },
  {
    id: 'classroom-ready',
    title: 'Classroom Ready',
    description: 'Complete all Classroom and Teachers lessons.',
    icon: 'MessageCircle',
  },
  {
    id: 'assignment-expert',
    title: 'Assignment Expert',
    description: 'Complete all School Systems and Assignments lessons.',
    icon: 'GraduationCap',
  },
  {
    id: 'campus-champion',
    title: 'Campus Dutch Champion',
    description: 'Complete every lesson in the app.',
    icon: 'Trophy',
  },
];

export function getAllLessons(): { lesson: Lesson; topic: Topic; category: Category }[] {
  const result: { lesson: Lesson; topic: Topic; category: Category }[] = [];
  for (const category of categories) {
    for (const topic of category.topics) {
      for (const lesson of topic.lessons) {
        result.push({ lesson, topic, category });
      }
    }
  }
  return result;
}

export function getLessonById(id: string): { lesson: Lesson; topic: Topic; category: Category } | undefined {
  return getAllLessons().find((item) => item.lesson.id === id);
}

export function getRecommendedLesson(
  completedLessons: string[],
  unlockedLessons: string[],
  lastLessonId: string | null
): { lesson: Lesson; topic: Topic; category: Category } | undefined {
  const all = getAllLessons();
  // If there's a last lesson, try the next one in sequence
  if (lastLessonId) {
    const idx = all.findIndex((item) => item.lesson.id === lastLessonId);
    if (idx !== -1 && idx + 1 < all.length) {
      const next = all[idx + 1];
      if (unlockedLessons.includes(next.lesson.id)) {
        return next;
      }
    }
  }
  // Otherwise, find the first unlocked and incomplete lesson
  const next = all.find(
    (item) => unlockedLessons.includes(item.lesson.id) && !completedLessons.includes(item.lesson.id)
  );
  if (next) return next;
  // Fall back to first lesson
  return all[0];
}
