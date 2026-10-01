import json
import random
from datetime import date, datetime
from pathlib import Path

from utils.courses import category_for_course
from utils.content import list_content_for_course
from utils.course_question_data import (
    batch2_hs_ela_arts,
    batch4_science,
    batch5_social_lang_cultures_testprep,
    batch6_ap_sci_math_cs,
    batch7_ap_humanities,
    batch8_ib_courses,
)

from utils import db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RESULTS_FILE = DATA_DIR / "quiz_results.json"

# Generic per-category practice questions (one pool per COURSE_CATALOG category).
# These are general, honestly-labeled practice questions used to power the
# auto check-in/check-out quiz mechanic and the mastery graph.
CATEGORY_QUESTION_BANK = {
    "Elementary": [
        {"q": "How many sides does a triangle have?", "options": ["2", "3", "4", "5"], "correct": 1, "topic": "Shapes"},
        {"q": "What comes after the number 7?", "options": ["6", "8", "9", "5"], "correct": 1, "topic": "Counting"},
        {"q": "Which letter comes after 'C' in the alphabet?", "options": ["B", "D", "E", "A"], "correct": 1, "topic": "Alphabet"},
        {"q": "What color do you get when you mix red and white?", "options": ["Purple", "Pink", "Orange", "Brown"], "correct": 1, "topic": "Colors"},
        {"q": "How many days are in a week?", "options": ["5", "6", "7", "8"], "correct": 2, "topic": "Time"},
        {"q": "Which of these is a fruit?", "options": ["Carrot", "Apple", "Potato", "Broccoli"], "correct": 1, "topic": "Categories"},
        {"q": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "correct": 1, "topic": "Addition"},
        {"q": "Which season comes after winter?", "options": ["Summer", "Fall", "Spring", "Winter"], "correct": 2, "topic": "Seasons"},
    ],
    "Middle School": [
        {"q": "What is the value of x in 2x = 10?", "options": ["3", "5", "7", "10"], "correct": 1, "topic": "Pre-Algebra"},
        {"q": "What is the powerhouse of the cell?", "options": ["Nucleus", "Mitochondria", "Ribosome", "Cell wall"], "correct": 1, "topic": "Middle School Biology"},
        {"q": "What is the chemical formula for table salt?", "options": ["NaCl", "H2O", "CO2", "KCl"], "correct": 0, "topic": "Middle School Chemistry"},
        {"q": "What force is at work when a ball rolls down a hill?", "options": ["Magnetism", "Gravity", "Friction", "Tension"], "correct": 1, "topic": "Middle School Physics"},
        {"q": "What is the capital of Texas?", "options": ["Houston", "Austin", "Dallas", "San Antonio"], "correct": 1, "topic": "Texas History"},
        {"q": "Which safety equipment protects your eyes in a lab?", "options": ["Gloves", "Goggles", "Apron", "Mask"], "correct": 1, "topic": "Lab Safety"},
        {"q": "What layer of Earth do we live on?", "options": ["Core", "Mantle", "Crust", "Atmosphere"], "correct": 2, "topic": "Middle School Geography"},
        {"q": "What is the freezing point of water in Celsius?", "options": ["0", "32", "100", "-1"], "correct": 0, "topic": "Middle School Science"},
    ],
    "High School Grade Level": [
        {"q": "The Pythagorean theorem is used to find what?", "options": ["The area of a circle", "The sides of a right triangle", "The volume of a cube", "The slope of a line"], "correct": 1, "topic": "Geometry Review"},
        {"q": "Who wrote 'Romeo and Juliet'?", "options": ["Dickens", "Shakespeare", "Hemingway", "Austen"], "correct": 1, "topic": "Literature Review"},
        {"q": "What organelle contains a cell's DNA?", "options": ["Ribosome", "Nucleus", "Golgi body", "Vacuole"], "correct": 1, "topic": "Biology Review"},
        {"q": "In what year did World War II end?", "options": ["1943", "1945", "1947", "1950"], "correct": 1, "topic": "History Review"},
        {"q": "What is the boiling point of water in Fahrenheit?", "options": ["100", "180", "212", "250"], "correct": 2, "topic": "Science Review"},
        {"q": "What does GPA stand for?", "options": ["Grade Point Average", "General Point Average", "Grade Percent Average", "Graduation Point Average"], "correct": 0, "topic": "Academics"},
        {"q": "What is 20% of 150?", "options": ["20", "30", "35", "40"], "correct": 1, "topic": "Math Review"},
        {"q": "Which branch of the U.S. government interprets laws?", "options": ["Legislative", "Executive", "Judicial", "Regional"], "correct": 2, "topic": "Government Review"},
    ],
    "English & Language Arts": [
        {"q": "Which word is a synonym for 'happy'?", "options": ["Sad", "Joyful", "Angry", "Tired"], "correct": 1, "topic": "Vocabulary"},
        {"q": "What part of speech is the word 'quickly'?", "options": ["Noun", "Verb", "Adverb", "Adjective"], "correct": 2, "topic": "Grammar"},
        {"q": "What is the plural of 'child'?", "options": ["Childs", "Childes", "Children", "Childrens"], "correct": 2, "topic": "Grammar"},
        {"q": "What do you call the main character of a story?", "options": ["Antagonist", "Protagonist", "Narrator", "Author"], "correct": 1, "topic": "Literary Terms"},
        {"q": "Which sentence is punctuated correctly?", "options": ["Lets eat grandma", "Let's eat, Grandma", "Lets eat, grandma", "Let's eat grandma."], "correct": 1, "topic": "Punctuation"},
        {"q": "What is a metaphor?", "options": ["A direct comparison without 'like/as'", "A rhyme", "A question", "A summary"], "correct": 0, "topic": "Literary Devices"},
        {"q": "What is the term for a story told from the 'I' perspective?", "options": ["Third person", "First person", "Second person", "Omniscient"], "correct": 1, "topic": "Point of View"},
        {"q": "Which of these is an example of alliteration?", "options": ["She sells seashells", "The cat sat", "Time flies", "Better late than never"], "correct": 0, "topic": "Literary Devices"},
    ],
    "Math": [
        {"q": "What is 7 x 8?", "options": ["54", "56", "58", "64"], "correct": 1, "topic": "Multiplication"},
        {"q": "Solve for x: x + 5 = 12", "options": ["5", "6", "7", "17"], "correct": 2, "topic": "Basic Algebra"},
        {"q": "What is 3/4 as a decimal?", "options": ["0.34", "0.75", "0.43", "0.25"], "correct": 1, "topic": "Fractions/Decimals"},
        {"q": "What is the area of a rectangle with sides 4 and 6?", "options": ["10", "20", "24", "26"], "correct": 2, "topic": "Geometry"},
        {"q": "Simplify: 2(x + 3)", "options": ["2x + 3", "2x + 6", "x + 6", "2x + 5"], "correct": 1, "topic": "Algebra"},
        {"q": "What is the value of pi rounded to two decimals?", "options": ["3.12", "3.14", "3.16", "3.41"], "correct": 1, "topic": "Geometry"},
        {"q": "What is 15% of 200?", "options": ["15", "20", "30", "45"], "correct": 2, "topic": "Percentages"},
        {"q": "What is the slope of the line y = 3x + 2?", "options": ["1", "2", "3", "5"], "correct": 2, "topic": "Linear Equations"},
    ],
    "Science": [
        {"q": "What planet is known as the Red Planet?", "options": ["Venus", "Mars", "Jupiter", "Saturn"], "correct": 1, "topic": "Astronomy"},
        {"q": "What gas do plants absorb from the air?", "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"], "correct": 2, "topic": "Biology"},
        {"q": "What is the chemical symbol for water?", "options": ["H2O", "O2", "CO2", "HO2"], "correct": 0, "topic": "Chemistry"},
        {"q": "What force pulls objects toward Earth?", "options": ["Magnetism", "Friction", "Gravity", "Inertia"], "correct": 2, "topic": "Physics"},
        {"q": "Which organ pumps blood through the body?", "options": ["Lungs", "Heart", "Liver", "Kidney"], "correct": 1, "topic": "Anatomy"},
        {"q": "What is the smallest unit of life?", "options": ["Atom", "Cell", "Tissue", "Organ"], "correct": 1, "topic": "Biology"},
        {"q": "What state of matter has a fixed shape and volume?", "options": ["Gas", "Liquid", "Solid", "Plasma"], "correct": 2, "topic": "Chemistry"},
        {"q": "What is photosynthesis the process of?", "options": ["Animals breathing", "Plants making food from sunlight", "Water evaporating", "Rocks forming"], "correct": 1, "topic": "Biology"},
    ],
    "Social Studies": [
        {"q": "Who was the first President of the United States?", "options": ["Jefferson", "Washington", "Lincoln", "Adams"], "correct": 1, "topic": "US History"},
        {"q": "What document begins with 'We the People'?", "options": ["Declaration of Independence", "Bill of Rights", "US Constitution", "Magna Carta"], "correct": 2, "topic": "Government"},
        {"q": "Which continent is Egypt located on?", "options": ["Asia", "Africa", "Europe", "South America"], "correct": 1, "topic": "Geography"},
        {"q": "What branch of government makes laws?", "options": ["Executive", "Judicial", "Legislative", "Regional"], "correct": 2, "topic": "Government"},
        {"q": "What economic system is based on supply and demand in free markets?", "options": ["Socialism", "Capitalism", "Communism", "Feudalism"], "correct": 1, "topic": "Economics"},
        {"q": "What is the term for a government run by the people?", "options": ["Monarchy", "Democracy", "Dictatorship", "Oligarchy"], "correct": 1, "topic": "Government"},
        {"q": "Which ocean is the largest?", "options": ["Atlantic", "Indian", "Pacific", "Arctic"], "correct": 2, "topic": "Geography"},
        {"q": "What social science studies human behavior and society?", "options": ["Economics", "Sociology", "Geology", "Astronomy"], "correct": 1, "topic": "Sociology"},
    ],
    "World Languages": [
        {"q": "How do you say 'hello' in Spanish?", "options": ["Adios", "Hola", "Gracias", "Buenas"], "correct": 1, "topic": "Vocabulary"},
        {"q": "How do you say 'thank you' in French?", "options": ["Bonjour", "Au revoir", "Merci", "S'il vous plaît"], "correct": 2, "topic": "Vocabulary"},
        {"q": "What does 'auf Wiedersehen' mean in German?", "options": ["Good morning", "Goodbye", "Please", "Yes"], "correct": 1, "topic": "Vocabulary"},
        {"q": "How do you say 'goodbye' in Mandarin Chinese (pinyin)?", "options": ["Nǐ hǎo", "Zàijiàn", "Xièxiè", "Duìbùqǐ"], "correct": 1, "topic": "Vocabulary"},
        {"q": "What does 'amicus' mean in Latin?", "options": ["Enemy", "Friend", "Water", "House"], "correct": 1, "topic": "Latin Vocabulary"},
        {"q": "In ASL, what does a 'thumbs up' generally sign?", "options": ["Bad/No", "Good/Yes", "Stop", "Hello"], "correct": 1, "topic": "ASL Basics"},
        {"q": "How do you say 'please' in Spanish?", "options": ["Gracias", "Hola", "Por favor", "Adiós"], "correct": 2, "topic": "Vocabulary"},
    ],
    "Technology & Engineering": [
        {"q": "What does 'HTML' stand for?", "options": ["Hyper Trainer Marking Language", "HyperText Markup Language", "Hyperlink Text Markup Language", "Home Tool Markup Language"], "correct": 1, "topic": "Web Basics"},
        {"q": "What is a variable in programming?", "options": ["A fixed number", "A named storage for a value", "A type of loop", "An error"], "correct": 1, "topic": "Programming Basics"},
        {"q": "What does 'CPU' stand for?", "options": ["Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Core Processing Unit"], "correct": 0, "topic": "Computer Basics"},
        {"q": "What does 'AI' stand for?", "options": ["Automated Interface", "Artificial Intelligence", "Applied Informatics", "Analog Integration"], "correct": 1, "topic": "AI Basics"},
        {"q": "What is the main purpose of a firewall in cybersecurity?", "options": ["Speed up internet", "Block unauthorized access", "Store files", "Design websites"], "correct": 1, "topic": "Cybersecurity"},
        {"q": "In engineering, what does the design process typically start with?", "options": ["Building the final product", "Identifying the problem", "Selling the product", "Testing"], "correct": 1, "topic": "Engineering Principles"},
    ],
    "Fine Arts": [
        {"q": "On a musical staff, how many lines are there?", "options": ["3", "4", "5", "6"], "correct": 2, "topic": "Reading Music"},
        {"q": "Which family of instruments does the violin belong to?", "options": ["Brass", "Percussion", "String", "Woodwind"], "correct": 2, "topic": "Orchestra Music"},
        {"q": "What are the three primary colors in visual art?", "options": ["Red, Blue, Green", "Red, Yellow, Blue", "Orange, Green, Purple", "Black, White, Gray"], "correct": 1, "topic": "Studio Art"},
        {"q": "What is the term for shaping clay by hand or on a wheel?", "options": ["Painting", "Ceramics", "Weaving", "Sketching"], "correct": 1, "topic": "Ceramics & Sculpting"},
        {"q": "In music theory, how many notes are in a major scale?", "options": ["5", "6", "7", "8"], "correct": 2, "topic": "Music Theory"},
        {"q": "What is the technique of capturing images with a camera called?", "options": ["Sculpting", "Photography", "Animation", "Choir"], "correct": 1, "topic": "Digital Photography"},
        {"q": "In theater, what is a monologue?", "options": ["A song sung by a choir", "A speech by one character", "A dance with two people", "The stage crew"], "correct": 1, "topic": "Theater Arts"},
        {"q": "What part of a choir sings the lowest notes?", "options": ["Soprano", "Alto", "Tenor", "Bass"], "correct": 3, "topic": "Choir Music"},
    ],
    "Health & PE": [
        {"q": "How many bones are in the adult human body?", "options": ["186", "206", "226", "246"], "correct": 1, "topic": "Health & Wellness"},
        {"q": "What is the recommended way to warm up before exercise?", "options": ["Stretch cold muscles hard", "Light cardio and dynamic stretching", "Skip warming up", "Lift heavy weights first"], "correct": 1, "topic": "Physical Education"},
        {"q": "Which nutrient is the body's main source of energy?", "options": ["Protein", "Carbohydrates", "Vitamins", "Water"], "correct": 1, "topic": "Health & Wellness"},
        {"q": "What does 'reps' mean in weight training?", "options": ["Repetitions of an exercise", "Rest periods", "Resistance level", "Recovery plan"], "correct": 0, "topic": "Weight Training & Fitness"},
        {"q": "Which of these is a cardiovascular exercise?", "options": ["Bicep curls", "Running", "Static stretching", "Bench press"], "correct": 1, "topic": "Physical Education"},
        {"q": "How many hours of sleep are generally recommended for teens?", "options": ["4-5", "6-7", "8-10", "12-14"], "correct": 2, "topic": "Health & Wellness"},
        {"q": "What muscle group do squats primarily target?", "options": ["Biceps", "Legs and glutes", "Shoulders", "Abs only"], "correct": 1, "topic": "Weight Training & Fitness"},
    ],
    "AP Courses": [
        {"q": "In AP-level statistics, what does a 'p-value' help determine?", "options": ["The mean of a dataset", "The statistical significance of a result", "The sample size needed", "The standard deviation"], "correct": 1, "topic": "AP Statistics"},
        {"q": "Which AP course covers supply, demand, and market equilibrium at a national level?", "options": ["AP Microeconomics", "AP Macroeconomics", "AP Psychology", "AP Human Geography"], "correct": 1, "topic": "AP Economics"},
        {"q": "In AP Chemistry, what is Avogadro's number approximately equal to?", "options": ["6.02 x 10^23", "3.14 x 10^8", "9.8 x 10^2", "1.6 x 10^-19"], "correct": 0, "topic": "AP Chemistry"},
        {"q": "AP US History covers events primarily in which country's history?", "options": ["Canada", "United States", "United Kingdom", "Mexico"], "correct": 1, "topic": "AP US History"},
        {"q": "In AP Computer Science, what is an 'algorithm'?", "options": ["A type of variable", "A step-by-step procedure to solve a problem", "A hardware component", "A programming language"], "correct": 1, "topic": "AP Computer Science"},
        {"q": "In AP Biology, what process do cells use to divide for growth and repair?", "options": ["Meiosis", "Mitosis", "Photosynthesis", "Osmosis"], "correct": 1, "topic": "AP Biology"},
        {"q": "AP Physics 1 primarily uses what type of math?", "options": ["Calculus", "Algebra-based math", "Geometry only", "Statistics only"], "correct": 1, "topic": "AP Physics"},
        {"q": "In AP English Language, what is 'rhetoric' the study of?", "options": ["Grammar rules only", "Persuasive writing and speaking", "Poetry meter", "Spelling"], "correct": 1, "topic": "AP English"},
    ],
    "IB Courses": [
        {"q": "What are the three core components of the IB Diploma Programme?", "options": ["TOK, EE, CAS", "Math, Science, Art", "SAT, ACT, GPA", "IB, AP, Honors"], "correct": 0, "topic": "IB Diploma Core"},
        {"q": "What does 'TOK' stand for in the IB program?", "options": ["Test of Knowledge", "Theory of Knowledge", "Types of Knowledge", "Theme of Knowledge"], "correct": 1, "topic": "IB Diploma Core"},
        {"q": "In IB, what is the highest possible score on a single subject?", "options": ["5", "6", "7", "10"], "correct": 2, "topic": "IB Assessment"},
        {"q": "What does 'HL' stand for in IB course levels?", "options": ["High Level", "Higher Level", "Hard Level", "Honors Level"], "correct": 1, "topic": "IB Course Levels"},
        {"q": "The IB Extended Essay is approximately how many words?", "options": ["1,000", "2,500", "4,000", "6,000"], "correct": 2, "topic": "IB Diploma Core"},
        {"q": "What does 'CAS' stand for in the IB Diploma?", "options": ["Creativity, Activity, Service", "Culture, Art, Science", "Community, Achievement, Skills", "Critical Analysis Skills"], "correct": 0, "topic": "IB Diploma Core"},
        {"q": "IB Language B courses focus on what skill?", "options": ["Native language literature", "Learning an additional language", "Computer programming", "Visual arts"], "correct": 1, "topic": "IB Languages"},
        {"q": "What subject group do IB Biology, Chemistry, and Physics belong to?", "options": ["Group 3: Individuals and Societies", "Group 4: Sciences", "Group 5: Mathematics", "Group 6: The Arts"], "correct": 1, "topic": "IB Sciences"},
    ],
    "Test Prep & College Readiness": [
        {"q": "On the SAT, what is the highest possible total score?", "options": ["1200", "1600", "2400", "2000"], "correct": 1, "topic": "SAT Prep"},
        {"q": "What does the 'Reading' section of the SAT primarily test?", "options": ["Math formulas", "Reading comprehension and analysis", "Science experiments", "Foreign language"], "correct": 1, "topic": "SAT Prep (Reading)"},
        {"q": "On the ACT, how many sections are there in the core test?", "options": ["2", "3", "4", "5"], "correct": 2, "topic": "ACT Prep"},
        {"q": "What is a good strategy when you don't know an answer on a timed test with no guessing penalty?", "options": ["Leave it blank and move on", "Guess and move on", "Spend 10 minutes on it", "Skip the whole section"], "correct": 1, "topic": "Study Skills & Test Strategies"},
        {"q": "What does GPA stand for?", "options": ["Grade Point Average", "General Placement Average", "Graduate Progress Average", "Grade Percentage Average"], "correct": 0, "topic": "Get Ready for College"},
        {"q": "In test prep, what does 'POE' commonly refer to?", "options": ["Point of Entry", "Process of Elimination", "Practice of Essays", "Plan of Education"], "correct": 1, "topic": "Study Skills & Test Strategies"},
        {"q": "The Math section of the ACT tests knowledge through roughly what level?", "options": ["Pre-Algebra through Trigonometry", "Calculus only", "Statistics only", "Elementary arithmetic only"], "correct": 0, "topic": "ACT Prep (Math & Science)"},
        {"q": "What's a recommended way to reduce test anxiety before an exam?", "options": ["Cram all night", "Practice deep breathing and get good sleep", "Skip breakfast", "Avoid reviewing material"], "correct": 1, "topic": "Study Skills & Test Strategies"},
    ],
    "World Cultures": [
        {"q": "Which country is home to the Great Wall?", "options": ["Japan", "China", "India", "Vietnam"], "correct": 1, "topic": "Amazing Cultures (Asia)"},
        {"q": "The pyramids of Giza are located on which continent?", "options": ["South America", "Africa", "Europe", "Oceania"], "correct": 1, "topic": "Amazing Cultures (Africa)"},
        {"q": "Which South American country is known for Machu Picchu?", "options": ["Brazil", "Peru", "Argentina", "Chile"], "correct": 1, "topic": "Amazing Cultures (South America)"},
        {"q": "The Eiffel Tower is a famous landmark in which European country?", "options": ["Italy", "Spain", "France", "Germany"], "correct": 2, "topic": "Amazing Cultures (Europe)"},
        {"q": "Which is the largest country in North America by land area?", "options": ["United States", "Mexico", "Canada", "Cuba"], "correct": 2, "topic": "Amazing Cultures (North America)"},
        {"q": "Aboriginal peoples are indigenous to which region?", "options": ["Oceania & Australia", "North America", "Northern Europe", "East Asia"], "correct": 0, "topic": "Amazing Cultures (Oceania & Australia)"},
        {"q": "Which festival of lights is widely celebrated in India?", "options": ["Diwali", "Carnival", "Oktoberfest", "Nowruz"], "correct": 0, "topic": "Amazing Cultures (Asia)"},
        {"q": "Samba is a traditional dance and music style closely associated with which country?", "options": ["Mexico", "Brazil", "Egypt", "Thailand"], "correct": 1, "topic": "Amazing Cultures (South America)"},
    ],
    "General": [
        {"q": "What is the capital of the United States?", "options": ["New York", "Washington D.C.", "Los Angeles", "Chicago"], "correct": 1, "topic": "General Knowledge"},
        {"q": "How many days are in a leap year?", "options": ["365", "364", "366", "360"], "correct": 2, "topic": "General Knowledge"},
        {"q": "What color do you get mixing blue and yellow?", "options": ["Purple", "Green", "Orange", "Brown"], "correct": 1, "topic": "General Knowledge"},
    ],
}

# Real, course-specific question pools sourced from actual web research (not
# invented), used in place of the generic category pool when available. Each
# entry cites where the underlying topic list came from.
COURSE_QUESTION_BANK = {
    "IB Biology": {
        "citation": (
            "Topic themes drawn from the IB Biology syllabus first examined May 2025 "
            "(Save My Exams: savemyexams.com/learning-hub/exam-guides/ib-biology-syllabus-update; "
            "RevisionDojo: revisiondojo.com/blog/what-to-expect-from-the-new-ib-biology-syllabus-2025)."
        ),
        "questions": [
            {"q": "Which of these are the four conceptual themes in the IB Biology syllabus (first exams 2025)?", "options": ["Molecules, Cells, Organisms, Ecosystems", "Atoms, Elements, Compounds, Mixtures", "Forces, Motion, Energy, Waves", "Grammar, Syntax, Semantics, Phonetics"], "correct": 0, "topic": "IB Biology Syllabus Structure"},
            {"q": "In Cell Biology, what structure controls what enters and exits a cell?", "options": ["Cell wall", "Plasma membrane", "Nucleolus", "Ribosome"], "correct": 1, "topic": "Cell Biology"},
            {"q": "In Molecular Biology, what type of biomolecule are enzymes primarily made of?", "options": ["Carbohydrates", "Lipids", "Proteins", "Nucleic acids"], "correct": 2, "topic": "Molecular Biology"},
            {"q": "In Genetics, what process copies DNA before cell division?", "options": ["Transcription", "Translation", "DNA replication", "Fermentation"], "correct": 2, "topic": "Genetics"},
            {"q": "In Physiology, which organ is the primary site of gas exchange in humans?", "options": ["Heart", "Lungs", "Liver", "Kidneys"], "correct": 1, "topic": "Physiology"},
            {"q": "In Ecology, what term describes the flow of energy from one trophic level to the next?", "options": ["Osmosis", "Energy transfer", "Mitosis", "Diffusion"], "correct": 1, "topic": "Ecology"},
            {"q": "In Evolution & Biodiversity, what is the process by which populations change over generations due to differential survival and reproduction?", "options": ["Natural selection", "Photosynthesis", "Homeostasis", "Meiosis only"], "correct": 0, "topic": "Evolution & Biodiversity"},
            {"q": "Compared to SL, what does HL extension content in IB Biology typically add?", "options": ["Less depth, fewer topics", "Additional depth and integrated extension areas", "No difference at all", "Only lab work, no theory"], "correct": 1, "topic": "IB Biology Syllabus Structure"},
        ],
    },
    "Pre school and below": {
        "questions": [
            {"q": "Which color is a banana?", "options": ["Red", "Yellow", "Blue", "Purple"], "correct": 1, "topic": "Colors"},
            {"q": "How many fingers are on one hand?", "options": ["3", "4", "5", "10"], "correct": 2, "topic": "Counting"},
            {"q": "Which shape has three sides?", "options": ["Circle", "Square", "Triangle", "Star"], "correct": 2, "topic": "Shapes"},
            {"q": "What sound does a cow make?", "options": ["Woof", "Meow", "Moo", "Quack"], "correct": 2, "topic": "Animal Sounds"},
            {"q": "Which one is bigger?", "options": ["A mouse", "An elephant", "A ball", "A shoe"], "correct": 1, "topic": "Size Comparison"},
            {"q": "What body part do you use to see?", "options": ["Ears", "Nose", "Eyes", "Feet"], "correct": 2, "topic": "Body Parts"},
            {"q": "Which number comes after 2?", "options": ["1", "2", "3", "4"], "correct": 2, "topic": "Counting"},
            {"q": "What color is the sky on a clear day?", "options": ["Green", "Blue", "Brown", "Black"], "correct": 1, "topic": "Colors"},
        ],
    },
    "Learning to read": {
        "questions": [
            {"q": "Which letter comes after B?", "options": ["A", "C", "D", "Z"], "correct": 1, "topic": "Alphabet"},
            {"q": "Which word rhymes with \"cat\"?", "options": ["Dog", "Hat", "Sun", "Cup"], "correct": 1, "topic": "Rhyming"},
            {"q": "What sound does the letter \"S\" usually make?", "options": ["/s/", "/b/", "/m/", "/t/"], "correct": 0, "topic": "Letter Sounds"},
            {"q": "Which of these is a common sight word?", "options": ["The", "Xylophone", "Rhinoceros", "Photosynthesis"], "correct": 0, "topic": "Sight Words"},
            {"q": "Which word means a small furry pet that says \"meow\"?", "options": ["Dog", "Cat", "Bird", "Fish"], "correct": 1, "topic": "Vocabulary"},
            {"q": "What is the first letter in the word \"sun\"?", "options": ["S", "U", "N", "T"], "correct": 0, "topic": "Beginning Sounds"},
            {"q": "Which sentence is written correctly?", "options": ["I like dogs.", "i like dogs", "I Like Dogs", "i Like dogs."], "correct": 0, "topic": "Sentence Basics"},
            {"q": "Which word is spelled correctly?", "options": ["Dog", "Dawg", "Dogg", "Doog"], "correct": 0, "topic": "Spelling"},
        ],
    },
    "Counting (k-2)": {
        "questions": [
            {"q": "What number comes after 9?", "options": ["8", "10", "11", "7"], "correct": 1, "topic": "Number Order"},
            {"q": "Count the dots: ooo oo — how many dots are there in total?", "options": ["3", "4", "5", "6"], "correct": 2, "topic": "Counting Objects"},
            {"q": "Which number is greater, 7 or 4?", "options": ["7", "4", "They are equal", "Cannot tell"], "correct": 0, "topic": "Comparing Numbers"},
            {"q": "What is 3 + 2?", "options": ["4", "5", "6", "7"], "correct": 1, "topic": "Simple Addition"},
            {"q": "Counting by 2s: 2, 4, 6, __?", "options": ["7", "8", "9", "10"], "correct": 1, "topic": "Skip Counting"},
            {"q": "What is 10 - 4?", "options": ["5", "6", "7", "4"], "correct": 1, "topic": "Simple Subtraction"},
            {"q": "Which number is between 5 and 7?", "options": ["4", "6", "8", "9"], "correct": 1, "topic": "Number Order"},
            {"q": "Counting by 10s: 10, 20, 30, __?", "options": ["35", "40", "45", "50"], "correct": 1, "topic": "Skip Counting"},
        ],
    },
    "Kindergarten": {
        "questions": [
            {"q": "Which shape has four equal sides?", "options": ["Triangle", "Circle", "Square", "Oval"], "correct": 2, "topic": "Shapes"},
            {"q": "What day comes after Monday?", "options": ["Sunday", "Tuesday", "Wednesday", "Friday"], "correct": 1, "topic": "Days of the Week"},
            {"q": "How many sides does a triangle have?", "options": ["2", "3", "4", "5"], "correct": 1, "topic": "Shapes"},
            {"q": "What is 1 + 1?", "options": ["1", "2", "3", "4"], "correct": 1, "topic": "Simple Addition"},
            {"q": "Which letter is a vowel?", "options": ["B", "C", "A", "D"], "correct": 2, "topic": "Alphabet/Vowels"},
            {"q": "What comes next in the pattern: red, blue, red, blue, __?", "options": ["red", "blue", "green", "yellow"], "correct": 0, "topic": "Patterns"},
            {"q": "How many days are in a week?", "options": ["5", "6", "7", "8"], "correct": 2, "topic": "Calendar"},
            {"q": "Counting to 10, what number comes right before 10?", "options": ["8", "9", "11", "7"], "correct": 1, "topic": "Counting to 10"},
        ],
    },
    "1st grade": {
        "questions": [
            {"q": "What is 8 + 5?", "options": ["12", "13", "14", "15"], "correct": 1, "topic": "Addition within 20"},
            {"q": "What is 15 - 7?", "options": ["7", "8", "9", "6"], "correct": 1, "topic": "Subtraction within 20"},
            {"q": "In the number 47, what digit is in the tens place?", "options": ["4", "7", "47", "0"], "correct": 0, "topic": "Place Value"},
            {"q": "What time does the clock show when the short hand is on 3 and the long hand is on 12?", "options": ["3:00", "12:03", "3:30", "12:30"], "correct": 0, "topic": "Telling Time"},
            {"q": "Which word is a noun?", "options": ["Run", "Jump", "Dog", "Happy"], "correct": 2, "topic": "Parts of Speech"},
            {"q": "Which shape has no corners?", "options": ["Square", "Triangle", "Circle", "Rectangle"], "correct": 2, "topic": "Shapes"},
            {"q": "What is 10 + 10?", "options": ["10", "20", "30", "100"], "correct": 1, "topic": "Addition within 20"},
            {"q": "Which coin is worth 1 cent?", "options": ["Nickel", "Dime", "Penny", "Quarter"], "correct": 2, "topic": "Money Basics"},
        ],
    },
    "2nd grade": {
        "questions": [
            {"q": "What is 45 + 26?", "options": ["61", "71", "81", "60"], "correct": 1, "topic": "Addition within 100"},
            {"q": "What is 90 - 37?", "options": ["43", "53", "63", "57"], "correct": 1, "topic": "Subtraction within 100"},
            {"q": "Skip count by 5s: 5, 10, 15, __?", "options": ["18", "20", "25", "30"], "correct": 1, "topic": "Skip Counting"},
            {"q": "How many cents are in a quarter?", "options": ["10", "20", "25", "50"], "correct": 2, "topic": "Money"},
            {"q": "What time is shown when the long hand is on the 6 and the short hand is between 4 and 5?", "options": ["4:30", "4:06", "5:30", "6:04"], "correct": 0, "topic": "Telling Time"},
            {"q": "Which word is the verb in \"The dog runs fast\"?", "options": ["dog", "runs", "fast", "the"], "correct": 1, "topic": "Parts of Speech"},
            {"q": "Using repeated addition (2+2+2), what is 3 x 2?", "options": ["4", "6", "8", "5"], "correct": 1, "topic": "Intro Multiplication"},
            {"q": "How many sides does a rectangle have?", "options": ["3", "4", "5", "6"], "correct": 1, "topic": "Shapes"},
        ],
    },
    "3rd grade": {
        "questions": [
            {"q": "What is 7 x 8?", "options": ["54", "56", "58", "64"], "correct": 1, "topic": "Multiplication Facts"},
            {"q": "What is 1/2 + 1/2?", "options": ["1/4", "1", "2", "1/2"], "correct": 1, "topic": "Fractions"},
            {"q": "What is the perimeter of a rectangle with sides 4 and 6?", "options": ["10", "20", "24", "14"], "correct": 1, "topic": "Perimeter"},
            {"q": "Which of these fractions is equal to one whole?", "options": ["1/2", "2/2", "3/4", "1/4"], "correct": 1, "topic": "Fractions"},
            {"q": "Which word is an adjective in \"The big red ball rolled\"?", "options": ["Rolled", "The", "Big", "Ball"], "correct": 2, "topic": "Parts of Speech"},
            {"q": "What is 100 ÷ 10?", "options": ["1", "10", "100", "1000"], "correct": 1, "topic": "Division Facts"},
            {"q": "What is the area of a rectangle with length 5 and width 3?", "options": ["8", "15", "16", "20"], "correct": 1, "topic": "Area"},
            {"q": "Which punctuation mark ends a question?", "options": ["Period", "Comma", "Question mark", "Exclamation point"], "correct": 2, "topic": "Grammar/Punctuation"},
        ],
    },
    "4th grade": {
        "questions": [
            {"q": "What is 23 x 4?", "options": ["88", "92", "96", "84"], "correct": 1, "topic": "Multi-digit Multiplication"},
            {"q": "What is 144 ÷ 12?", "options": ["10", "11", "12", "14"], "correct": 2, "topic": "Division"},
            {"q": "Which fraction is equivalent to 1/2?", "options": ["2/5", "2/4", "3/5", "2/3"], "correct": 1, "topic": "Equivalent Fractions"},
            {"q": "What is 0.5 written as a fraction?", "options": ["1/5", "1/2", "1/4", "5/100"], "correct": 1, "topic": "Decimals"},
            {"q": "Which of these is a prime number?", "options": ["4", "6", "7", "9"], "correct": 2, "topic": "Prime Numbers"},
            {"q": "On most maps, which direction is typically at the top?", "options": ["South", "North", "East", "West"], "correct": 1, "topic": "Map Skills"},
            {"q": "What is 3/4 - 1/4?", "options": ["1/4", "1/2", "3/4", "1"], "correct": 1, "topic": "Fractions"},
            {"q": "Which of these numbers rounds to 500 when rounded to the nearest hundred?", "options": ["449", "517", "560", "601"], "correct": 1, "topic": "Rounding"},
        ],
    },
    "5th grade": {
        "questions": [
            {"q": "What is 2/3 + 1/6?", "options": ["5/6", "3/9", "1/2", "5/9"], "correct": 0, "topic": "Adding Fractions"},
            {"q": "What is 0.75 written as a fraction in simplest form?", "options": ["3/4", "7/5", "75/10", "3/5"], "correct": 0, "topic": "Decimals to Fractions"},
            {"q": "Using order of operations, what is 3 + 4 x 2?", "options": ["14", "11", "10", "9"], "correct": 1, "topic": "Order of Operations"},
            {"q": "What is the volume of a cube with side length 3?", "options": ["9", "18", "27", "81"], "correct": 2, "topic": "Volume"},
            {"q": "How many degrees are in a right angle?", "options": ["45", "90", "180", "360"], "correct": 1, "topic": "Angles"},
            {"q": "What is 5.2 + 3.6?", "options": ["8.8", "7.8", "9.8", "8.6"], "correct": 0, "topic": "Adding Decimals"},
            {"q": "What is 4/5 written as a decimal?", "options": ["0.4", "0.45", "0.8", "0.75"], "correct": 2, "topic": "Fractions to Decimals"},
            {"q": "What is the least common multiple of 4 and 6?", "options": ["8", "10", "12", "24"], "correct": 2, "topic": "LCM"},
        ],
    },
    "Elementary Recap": {
        "questions": [
            {"q": "What is 6 x 7?", "options": ["36", "42", "48", "49"], "correct": 1, "topic": "Multiplication Review"},
            {"q": "Which word is a synonym for \"happy\"?", "options": ["Sad", "Joyful", "Angry", "Tired"], "correct": 1, "topic": "Vocabulary"},
            {"q": "What is 3/4 written as a decimal?", "options": ["0.34", "0.75", "0.43", "0.25"], "correct": 1, "topic": "Fractions Review"},
            {"q": "What is the capital of the United States?", "options": ["New York", "Washington D.C.", "Los Angeles", "Chicago"], "correct": 1, "topic": "Geography Review"},
            {"q": "Which of these is a complete sentence?", "options": ["Running fast.", "The dog ran fast.", "Fast dog.", "Ran."], "correct": 1, "topic": "Grammar Review"},
            {"q": "What is 100 - 45?", "options": ["45", "55", "65", "50"], "correct": 1, "topic": "Subtraction Review"},
            {"q": "What do plants need to make their own food?", "options": ["Soil only", "Sunlight, water, and carbon dioxide", "Only water", "Only sunlight"], "correct": 1, "topic": "Science Review"},
            {"q": "What is the plural of \"child\"?", "options": ["Childs", "Children", "Childes", "Child"], "correct": 1, "topic": "Grammar Review"},
        ],
    },
    "6th grade": {
        "questions": [
            {"q": "What is the ratio of 4 apples to 8 oranges in simplest form?", "options": ["1:2", "4:8", "2:1", "1:4"], "correct": 0, "topic": "Ratios"},
            {"q": "What is 25% of 80?", "options": ["15", "20", "25", "40"], "correct": 1, "topic": "Percentages"},
            {"q": "What is -5 + 8?", "options": ["-13", "3", "13", "-3"], "correct": 1, "topic": "Integers"},
            {"q": "On a coordinate plane, in which quadrant is the point (-3, 4)?", "options": ["I", "II", "III", "IV"], "correct": 1, "topic": "Coordinate Plane"},
            {"q": "What is 3^2?", "options": ["5", "6", "9", "12"], "correct": 2, "topic": "Exponents"},
            {"q": "Simplify: 5x + 3x", "options": ["8x", "15x", "8x^2", "2x"], "correct": 0, "topic": "Algebraic Expressions"},
            {"q": "What is the mean of 2, 4, 6, 8?", "options": ["4", "5", "6", "20"], "correct": 1, "topic": "Statistics"},
            {"q": "What is 7/10 written as a percent?", "options": ["7%", "70%", "17%", "0.7%"], "correct": 1, "topic": "Percentages"},
        ],
    },
    "7th grade": {
        "questions": [
            {"q": "Solve for x: x + 5 = 12", "options": ["5", "6", "7", "17"], "correct": 2, "topic": "One-step Equations"},
            {"q": "What is -3 x -4?", "options": ["-12", "12", "-7", "7"], "correct": 1, "topic": "Multiplying Integers"},
            {"q": "A recipe uses 2 cups of flour for 4 servings. How many cups are needed for 6 servings?", "options": ["3", "4", "5", "6"], "correct": 0, "topic": "Proportions"},
            {"q": "What is the probability of rolling a 4 on a fair six-sided die?", "options": ["1/2", "1/6", "1/4", "1/3"], "correct": 1, "topic": "Probability"},
            {"q": "What is 40% written as a decimal?", "options": ["0.4", "4.0", "0.04", "40"], "correct": 0, "topic": "Percent to Decimal"},
            {"q": "Simplify: -8 - (-3)", "options": ["-11", "-5", "5", "11"], "correct": 1, "topic": "Integer Operations"},
            {"q": "Which formula gives the circumference of a circle?", "options": ["πr^2", "2πr", "2r", "r^2"], "correct": 1, "topic": "Circles"},
            {"q": "Which of these is an example of a rational number?", "options": ["√2", "π", "1/2", "√3"], "correct": 2, "topic": "Number Systems"},
        ],
    },
    "8th grade": {
        "questions": [
            {"q": "Solve for x: 2x + 3 = 11", "options": ["3", "4", "5", "6"], "correct": 1, "topic": "Linear Equations"},
            {"q": "What is the slope of a line that rises 4 units for every 2 units it runs?", "options": ["1/2", "2", "4", "8"], "correct": 1, "topic": "Slope"},
            {"q": "Using the Pythagorean theorem, what is the hypotenuse of a right triangle with legs 3 and 4?", "options": ["5", "6", "7", "12"], "correct": 0, "topic": "Pythagorean Theorem"},
            {"q": "What is 2^3 x 2^2?", "options": ["2^5", "2^6", "4^5", "2^1"], "correct": 0, "topic": "Exponent Rules"},
            {"q": "Which of these sets of ordered pairs represents a function?", "options": ["{(1,2),(1,3)}", "{(1,2),(2,3)}", "{(2,1),(2,4)}", "{(1,1),(1,2)}"], "correct": 1, "topic": "Functions"},
            {"q": "What is the y-intercept of y = 3x + 7?", "options": ["3", "7", "-7", "0"], "correct": 1, "topic": "Linear Equations"},
            {"q": "Simplify: (x^2)(x^3)", "options": ["x^5", "x^6", "x^1", "2x^5"], "correct": 0, "topic": "Exponent Rules"},
            {"q": "What type of angle measures exactly 90 degrees?", "options": ["Acute", "Obtuse", "Right", "Straight"], "correct": 2, "topic": "Angles"},
        ],
    },
    "Middle school recap": {
        "questions": [
            {"q": "What is 6^2?", "options": ["12", "36", "64", "18"], "correct": 1, "topic": "Exponents Review"},
            {"q": "Solve for x: 3x = 21", "options": ["6", "7", "8", "9"], "correct": 1, "topic": "Equations Review"},
            {"q": "What is 3/8 written as a decimal?", "options": ["0.375", "0.38", "0.83", "0.325"], "correct": 0, "topic": "Fractions Review"},
            {"q": "Which part of speech describes an action?", "options": ["Noun", "Verb", "Adjective", "Preposition"], "correct": 1, "topic": "Grammar Review"},
            {"q": "What is the capital of Texas?", "options": ["Houston", "Dallas", "Austin", "San Antonio"], "correct": 2, "topic": "Geography Review"},
            {"q": "What gas do plants absorb during photosynthesis?", "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], "correct": 1, "topic": "Science Review"},
            {"q": "What is -7 + 10?", "options": ["3", "-3", "17", "-17"], "correct": 0, "topic": "Integers Review"},
            {"q": "Which war did the American colonies fight to win independence from Britain?", "options": ["Civil War", "Revolutionary War", "War of 1812", "World War I"], "correct": 1, "topic": "History Review"},
        ],
    },
    "Middle school math": {
        "questions": [
            {"q": "What is the mean of 5, 10, 15, 20, 25?", "options": ["10", "15", "20", "25"], "correct": 1, "topic": "Statistics"},
            {"q": "What is the median of 3, 9, 4, 8, 6?", "options": ["4", "6", "8", "9"], "correct": 1, "topic": "Statistics"},
            {"q": "Solve: 4(x + 2) = 20", "options": ["3", "4", "5", "6"], "correct": 0, "topic": "Equations"},
            {"q": "What is 5/6 ÷ 1/3?", "options": ["5/18", "2 1/2", "1 5/6", "3/2"], "correct": 1, "topic": "Dividing Fractions"},
            {"q": "What is the area of a triangle with base 8 and height 5?", "options": ["13", "20", "40", "45"], "correct": 1, "topic": "Area"},
            {"q": "Which of these numbers is irrational?", "options": ["0.5", "3", "√2", "4/5"], "correct": 2, "topic": "Number Systems"},
            {"q": "What is 15% of 200?", "options": ["15", "20", "30", "45"], "correct": 2, "topic": "Percentages"},
            {"q": "What is the mode of 2, 3, 3, 5, 7, 3?", "options": ["2", "3", "5", "7"], "correct": 1, "topic": "Statistics"},
        ],
    },
    "Pre-Algebra": {
        "questions": [
            {"q": "What is the value of x in x - 9 = 2?", "options": ["7", "9", "11", "-7"], "correct": 2, "topic": "One-step Equations"},
            {"q": "Which property is shown by a + b = b + a?", "options": ["Associative", "Commutative", "Distributive", "Identity"], "correct": 1, "topic": "Properties of Operations"},
            {"q": "Simplify: 3(x + 4)", "options": ["3x+4", "3x+12", "x+12", "7x"], "correct": 1, "topic": "Distributive Property"},
            {"q": "What is the absolute value of -9?", "options": ["-9", "0", "9", "18"], "correct": 2, "topic": "Integers"},
            {"q": "In 2 + 3 x (4 - 1), what should you calculate first?", "options": ["2 + 3", "4 - 1", "3 x 4", "2 x 3"], "correct": 1, "topic": "Order of Operations"},
            {"q": "What is 2/3 written as a percent (rounded to the nearest whole number)?", "options": ["33%", "50%", "67%", "75%"], "correct": 2, "topic": "Fractions/Percents"},
            {"q": "Which of these is a variable expression?", "options": ["5", "7+2", "3x + 1", "10"], "correct": 2, "topic": "Expressions"},
            {"q": "Solve: x/4 = 5", "options": ["1", "9", "20", "45"], "correct": 2, "topic": "One-step Equations"},
        ],
    },
    "Middle school biology": {
        "questions": [
            {"q": "What is the basic unit of life?", "options": ["Atom", "Cell", "Tissue", "Organ"], "correct": 1, "topic": "Cell Biology"},
            {"q": "Which organelle is known as the \"powerhouse of the cell\"?", "options": ["Nucleus", "Ribosome", "Mitochondria", "Chloroplast"], "correct": 2, "topic": "Cell Organelles"},
            {"q": "What do plants produce during photosynthesis?", "options": ["Carbon dioxide and water", "Oxygen and glucose", "Nitrogen and salt", "Only water"], "correct": 1, "topic": "Photosynthesis"},
            {"q": "What molecule carries genetic information in cells?", "options": ["RNA only", "Proteins", "DNA", "Lipids"], "correct": 2, "topic": "Genetics"},
            {"q": "Which of these is a producer in a food chain?", "options": ["Lion", "Grass", "Mushroom", "Eagle"], "correct": 1, "topic": "Ecosystems"},
            {"q": "What is the process by which a cell divides into two identical cells called?", "options": ["Meiosis", "Mitosis", "Photosynthesis", "Respiration"], "correct": 1, "topic": "Cell Division"},
            {"q": "Which body system is responsible for pumping blood?", "options": ["Digestive", "Respiratory", "Circulatory", "Skeletal"], "correct": 2, "topic": "Human Body Systems"},
            {"q": "What do we call organisms that break down dead material for energy?", "options": ["Producers", "Consumers", "Decomposers", "Predators"], "correct": 2, "topic": "Ecosystems"},
        ],
    },
    "Middle school chemistry": {
        "questions": [
            {"q": "What is the smallest unit of an element that retains its properties?", "options": ["Molecule", "Atom", "Cell", "Compound"], "correct": 1, "topic": "Atomic Structure"},
            {"q": "Which subatomic particle has a negative charge?", "options": ["Proton", "Neutron", "Electron", "Nucleus"], "correct": 2, "topic": "Atomic Structure"},
            {"q": "Water changing from liquid to gas is an example of what kind of change?", "options": ["Chemical change", "Physical change", "Nuclear change", "Genetic change"], "correct": 1, "topic": "Physical vs Chemical Change"},
            {"q": "What is the chemical symbol for oxygen?", "options": ["O", "Ox", "O2", "Og"], "correct": 0, "topic": "Periodic Table"},
            {"q": "Which of these is a mixture rather than a pure substance?", "options": ["Salt water", "Table salt", "Pure gold", "Distilled water"], "correct": 0, "topic": "Mixtures and Solutions"},
            {"q": "What are the three main states of matter?", "options": ["Solid, liquid, gas", "Solid, plasma, energy", "Liquid, gas, plasma", "Solid, gas, energy"], "correct": 0, "topic": "States of Matter"},
            {"q": "In the periodic table, elements in the same column are called what?", "options": ["Periods", "Groups", "Isotopes", "Compounds"], "correct": 1, "topic": "Periodic Table"},
            {"q": "Rusting of iron is an example of what type of change?", "options": ["Physical change", "Chemical change", "Phase change", "No change"], "correct": 1, "topic": "Physical vs Chemical Change"},
        ],
    },
    "Middle school Physics": {
        "questions": [
            {"q": "What is the term for a push or pull on an object?", "options": ["Energy", "Force", "Mass", "Motion"], "correct": 1, "topic": "Forces"},
            {"q": "According to Newton's First Law, an object at rest stays at rest unless acted on by what?", "options": ["Gravity only", "An unbalanced force", "Friction only", "Nothing, it never moves"], "correct": 1, "topic": "Newton's Laws"},
            {"q": "What unit is used to measure force?", "options": ["Watt", "Joule", "Newton", "Meter"], "correct": 2, "topic": "Units of Measurement"},
            {"q": "What type of energy does a moving object have?", "options": ["Potential energy", "Kinetic energy", "Chemical energy", "Thermal energy"], "correct": 1, "topic": "Energy"},
            {"q": "Which simple machine is a ramp, used to make lifting easier?", "options": ["Lever", "Pulley", "Inclined plane", "Wheel and axle"], "correct": 2, "topic": "Simple Machines"},
            {"q": "Newton's Third Law states that for every action there is what?", "options": ["No reaction", "An equal and opposite reaction", "A weaker reaction", "A delayed reaction"], "correct": 1, "topic": "Newton's Laws"},
            {"q": "What force pulls objects toward the center of the Earth?", "options": ["Friction", "Magnetism", "Gravity", "Tension"], "correct": 2, "topic": "Forces"},
            {"q": "Speed is calculated by dividing what by time?", "options": ["Mass", "Distance", "Force", "Energy"], "correct": 1, "topic": "Motion"},
        ],
    },
    "Middle school earth and environmental science": {
        "questions": [
            {"q": "What are the three main types of rock?", "options": ["Igneous, sedimentary, metamorphic", "Hard, soft, medium", "Big, small, tiny", "Old, new, ancient"], "correct": 0, "topic": "Rock Cycle"},
            {"q": "What is the process by which water moves from the ocean to the atmosphere and back called?", "options": ["Rock cycle", "Water cycle", "Carbon cycle", "Nitrogen cycle"], "correct": 1, "topic": "Water Cycle"},
            {"q": "Which layer of the Earth is at its very center?", "options": ["Crust", "Mantle", "Outer core", "Inner core"], "correct": 3, "topic": "Earth's Layers"},
            {"q": "What is the difference between weather and climate?", "options": ["They are the same thing", "Weather is day-to-day conditions; climate is long-term patterns", "Weather is long-term; climate is daily", "Climate only refers to temperature"], "correct": 1, "topic": "Weather and Climate"},
            {"q": "Which of these is a renewable energy source?", "options": ["Coal", "Natural gas", "Solar power", "Oil"], "correct": 2, "topic": "Natural Resources"},
            {"q": "What is erosion?", "options": ["The formation of new rock", "The wearing away and movement of soil or rock by wind or water", "The melting of ice caps only", "The growth of plants"], "correct": 1, "topic": "Erosion and Weathering"},
            {"q": "What causes the greenhouse effect on Earth?", "options": ["Ozone depletion only", "Gases trapping heat in the atmosphere", "Lack of sunlight", "Ocean currents alone"], "correct": 1, "topic": "Climate Science"},
            {"q": "What tool is used to measure earthquake magnitude?", "options": ["Barometer", "Thermometer", "Seismograph", "Anemometer"], "correct": 2, "topic": "Geology"},
        ],
    },
    "Lab safety": {
        "questions": [
            {"q": "What should you always wear to protect your eyes during a science experiment?", "options": ["Gloves", "Safety goggles", "A lab coat", "Earplugs"], "correct": 1, "topic": "Personal Protective Equipment"},
            {"q": "What should you do if a chemical spills on your skin?", "options": ["Ignore it", "Rinse the area with water immediately and tell your teacher", "Wait until the end of class", "Cover it with a bandage"], "correct": 1, "topic": "Emergency Procedures"},
            {"q": "Is it ever safe to eat or drink in a science lab?", "options": ["Yes, always", "Yes, if it's a snack", "No, never", "Only during lunch break"], "correct": 2, "topic": "General Lab Rules"},
            {"q": "What should you do before leaving the lab?", "options": ["Wash your hands", "Leave equipment out", "Take chemicals home", "Nothing special"], "correct": 0, "topic": "General Lab Rules"},
            {"q": "What document lists the hazards and safe handling information for a chemical?", "options": ["Recipe card", "Safety Data Sheet (SDS)", "Textbook", "Lab manual only"], "correct": 1, "topic": "Chemical Safety"},
            {"q": "If you notice broken glass in the lab, what should you do?", "options": ["Pick it up with bare hands", "Leave it and tell your teacher", "Sweep it under the table", "Throw it in the regular trash"], "correct": 1, "topic": "Emergency Procedures"},
            {"q": "Why should long hair be tied back in a lab?", "options": ["It looks neater", "To prevent it from catching fire or getting in chemicals", "It's not necessary", "To follow fashion rules"], "correct": 1, "topic": "Personal Safety"},
            {"q": "What should you do if you don't understand a lab instruction?", "options": ["Guess and continue", "Ask your teacher before proceeding", "Skip that step", "Copy a friend's work"], "correct": 1, "topic": "General Lab Rules"},
        ],
    },
    "Middle school history": {
        "questions": [
            {"q": "Which ancient civilization built the pyramids at Giza?", "options": ["Ancient Greece", "Ancient Egypt", "Ancient Rome", "Ancient China"], "correct": 1, "topic": "Ancient Civilizations"},
            {"q": "Which ancient civilization is credited with developing early democracy in Athens?", "options": ["Ancient Egypt", "Ancient Rome", "Ancient Greece", "Mesopotamia"], "correct": 2, "topic": "Ancient Civilizations"},
            {"q": "Who was the first President of the United States?", "options": ["Thomas Jefferson", "George Washington", "John Adams", "Abraham Lincoln"], "correct": 1, "topic": "American History"},
            {"q": "What document declared the American colonies' independence from Britain in 1776?", "options": ["The Constitution", "The Declaration of Independence", "The Bill of Rights", "The Magna Carta"], "correct": 1, "topic": "American Revolution"},
            {"q": "Which river was central to the development of Ancient Egyptian civilization?", "options": ["Amazon River", "Nile River", "Mississippi River", "Yangtze River"], "correct": 1, "topic": "Ancient Civilizations"},
            {"q": "Which ancient people developed one of the first writing systems, cuneiform, in Mesopotamia?", "options": ["Sumerians", "Aztecs", "Vikings", "Mayans"], "correct": 0, "topic": "Ancient Civilizations"},
            {"q": "Which empire was known for its extensive road system and the Colosseum?", "options": ["Ancient Egypt", "Roman Empire", "Persian Empire", "Ottoman Empire"], "correct": 1, "topic": "Ancient Civilizations"},
            {"q": "In what year did World War II end?", "options": ["1939", "1945", "1918", "1950"], "correct": 1, "topic": "World History"},
        ],
    },
    "Texas history": {
        "questions": [
            {"q": "In what year did Texas win its independence from Mexico?", "options": ["1821", "1836", "1845", "1861"], "correct": 1, "topic": "Texas Revolution"},
            {"q": "What famous 1836 battle in San Antonio is remembered with the phrase \"Remember the Alamo\"?", "options": ["Battle of San Jacinto", "Battle of the Alamo", "Battle of Gonzales", "Battle of Goliad"], "correct": 1, "topic": "Texas Revolution"},
            {"q": "Who led the Texian army to victory at the Battle of San Jacinto?", "options": ["Stephen F. Austin", "Sam Houston", "Davy Crockett", "Jim Bowie"], "correct": 1, "topic": "Texas Revolution"},
            {"q": "In what year did Texas become a U.S. state?", "options": ["1836", "1845", "1861", "1876"], "correct": 1, "topic": "Texas Statehood"},
            {"q": "What is the capital of Texas?", "options": ["Houston", "San Antonio", "Austin", "Dallas"], "correct": 2, "topic": "Texas Geography"},
            {"q": "Texas is sometimes called the \"Land of Six Flags\" because six governments have ruled over it. Which of these did NOT rule over Texas?", "options": ["Spain", "France", "Mexico", "Canada"], "correct": 3, "topic": "Texas History Overview"},
            {"q": "Which 1901 oil discovery near Beaumont sparked a major Texas oil boom?", "options": ["Spindletop", "Permian Basin", "Eagle Ford", "Barnett Shale"], "correct": 0, "topic": "Texas Oil History"},
            {"q": "Before joining the United States, Texas was briefly an independent nation known as what?", "options": ["The Republic of Texas", "The Texas Territory", "New Spain", "The Lone Star Colony"], "correct": 0, "topic": "Republic of Texas"},
        ],
    },
    "World cultures": {
        "questions": [
            {"q": "Which continent is Egypt located on?", "options": ["Asia", "Africa", "Europe", "South America"], "correct": 1, "topic": "World Geography"},
            {"q": "Which country is known for the traditional tea ceremony and originated sushi?", "options": ["China", "Japan", "India", "Korea"], "correct": 1, "topic": "Asian Cultures"},
            {"q": "What holiday celebrated in Mexico honors deceased loved ones with altars and marigolds?", "options": ["Cinco de Mayo", "Day of the Dead (Día de los Muertos)", "Three Kings Day", "Independence Day"], "correct": 1, "topic": "Latin American Traditions"},
            {"q": "Which language has the most native speakers worldwide?", "options": ["English", "Spanish", "Mandarin Chinese", "French"], "correct": 2, "topic": "World Languages"},
            {"q": "What is the traditional Indian festival of lights called?", "options": ["Holi", "Diwali", "Eid", "Ramadan"], "correct": 1, "topic": "South Asian Traditions"},
            {"q": "Which continent has the most countries?", "options": ["Asia", "Europe", "Africa", "South America"], "correct": 2, "topic": "World Geography"},
            {"q": "What is the name of the Islamic holy month of fasting?", "options": ["Diwali", "Hanukkah", "Ramadan", "Lent"], "correct": 2, "topic": "Religious Traditions"},
            {"q": "Which country is home to the ancient pyramids of Chichen Itza, built by the Maya civilization?", "options": ["Peru", "Mexico", "Egypt", "Guatemala"], "correct": 1, "topic": "Latin American Cultures"},
        ],
    },
    "Middle school geography": {
        "questions": [
            {"q": "How many continents are there?", "options": ["5", "6", "7", "8"], "correct": 2, "topic": "World Continents"},
            {"q": "What is the largest ocean on Earth?", "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"], "correct": 3, "topic": "Oceans"},
            {"q": "What imaginary line divides the Earth into Northern and Southern Hemispheres?", "options": ["Prime Meridian", "Equator", "Tropic of Cancer", "International Date Line"], "correct": 1, "topic": "Latitude and Longitude"},
            {"q": "Which lines on a map run east-west and measure distance north or south of the equator?", "options": ["Longitude lines", "Latitude lines", "Time zones", "Contour lines"], "correct": 1, "topic": "Map Skills"},
            {"q": "What is traditionally considered the longest river in the world?", "options": ["Amazon River", "Nile River", "Mississippi River", "Yangtze River"], "correct": 1, "topic": "Physical Geography"},
            {"q": "Which mountain range separates Europe from Asia in Russia?", "options": ["The Alps", "The Andes", "The Ural Mountains", "The Rockies"], "correct": 2, "topic": "Physical Geography"},
            {"q": "What do we call the imaginary lines on a map that measure distance east or west of the Prime Meridian?", "options": ["Latitude", "Longitude", "Equator", "Parallels"], "correct": 1, "topic": "Map Skills"},
            {"q": "Which desert is the largest hot desert in the world?", "options": ["Gobi Desert", "Sahara Desert", "Mojave Desert", "Kalahari Desert"], "correct": 1, "topic": "Physical Geography"},
        ],
    },
    "Algebra 1": {
        "questions": [
            {"q": "Solve for x: 3x - 7 = 14", "options": ["5", "7", "9", "21"], "correct": 1, "topic": "Solving Linear Equations"},
            {"q": "What is the slope of the line through (2, 3) and (6, 11)?", "options": ["2", "4", "0.5", "8"], "correct": 0, "topic": "Slope"},
            {"q": "Simplify: x^3 · x^5", "options": ["x^8", "x^15", "x^2", "2x^8"], "correct": 0, "topic": "Exponent Rules"},
            {"q": "Factor: x^2 + 5x + 6", "options": ["(x+2)(x+3)", "(x+1)(x+6)", "(x-2)(x-3)", "(x+6)(x-1)"], "correct": 0, "topic": "Factoring Quadratics"},
            {"q": "Solve the inequality: 2x + 3 < 11", "options": ["x < 4", "x > 4", "x < 7", "x < 8"], "correct": 0, "topic": "Linear Inequalities"},
            {"q": "In the equation y = mx + b, what does m represent?", "options": ["The slope", "The y-intercept", "The x-intercept", "The constant term"], "correct": 0, "topic": "Slope-Intercept Form"},
            {"q": "Evaluate f(x) = 2x^2 - 3 at x = 3", "options": ["15", "9", "21", "12"], "correct": 0, "topic": "Evaluating Functions"},
        ],
    },
    "Geometry": {
        "questions": [
            {"q": "What is the sum of the interior angles of a triangle?", "options": ["180°", "90°", "360°", "270°"], "correct": 0, "topic": "Triangle Angle Sum"},
            {"q": "A right triangle has legs of 3 and 4. What is the length of the hypotenuse?", "options": ["5", "6", "7", "25"], "correct": 0, "topic": "Pythagorean Theorem"},
            {"q": "What is the area of a circle with radius 4?", "options": ["16π", "8π", "4π", "32π"], "correct": 0, "topic": "Area of a Circle"},
            {"q": "Which of these is NOT a valid triangle congruence criterion?", "options": ["SSS", "SAS", "ASA", "AAA"], "correct": 3, "topic": "Triangle Congruence"},
            {"q": "When two parallel lines are cut by a transversal, corresponding angles are:", "options": ["Congruent", "Supplementary", "Complementary", "Perpendicular"], "correct": 0, "topic": "Parallel Lines and Angles"},
            {"q": "What is the sum of the interior angles of a hexagon?", "options": ["720°", "540°", "900°", "360°"], "correct": 0, "topic": "Polygon Angle Sum"},
            {"q": "What is the volume of a cylinder with radius 3 and height 5?", "options": ["45π", "15π", "30π", "90π"], "correct": 0, "topic": "Volume of a Cylinder"},
        ],
    },
    "Advanced Geometry": {
        "questions": [
            {"q": "Which is the correct statement of the Law of Cosines for side c?", "options": ["c² = a² + b² − 2ab·cos(C)", "c² = a² + b² + 2ab·cos(C)", "c² = a² − b²", "c² = a² + b²"], "correct": 0, "topic": "Law of Cosines"},
            {"q": "According to the Inscribed Angle Theorem, an inscribed angle is:", "options": ["Half the measure of the central angle subtending the same arc", "Equal to the central angle", "Twice the central angle", "Always 90°"], "correct": 0, "topic": "Circle Theorems"},
            {"q": "What is the equation of a circle with center (2, -3) and radius 5?", "options": ["(x−2)² + (y+3)² = 25", "(x+2)² + (y−3)² = 25", "(x−2)² + (y+3)² = 5", "(x−2)² − (y+3)² = 25"], "correct": 0, "topic": "Equation of a Circle"},
            {"q": "What is the distance between the points (1, 2) and (4, 6)?", "options": ["5", "7", "25", "4.5"], "correct": 0, "topic": "Distance Formula"},
            {"q": "A tangent line to a circle is always perpendicular to:", "options": ["The radius drawn to the point of tangency", "The diameter only", "Any chord", "The center"], "correct": 0, "topic": "Tangent Lines"},
            {"q": "Which transformation is an isometry (preserves distance and angle measure)?", "options": ["Rotation", "Dilation", "Horizontal stretch", "Non-uniform scaling"], "correct": 0, "topic": "Transformations"},
            {"q": "If two similar triangles have a scale factor of k, how does their area ratio compare?", "options": ["k²", "k", "2k", "k³"], "correct": 0, "topic": "Similarity and Area"},
        ],
    },
    "Algebra 2": {
        "questions": [
            {"q": "Solve: x^2 - 5x + 6 = 0", "options": ["x = 2 and x = 3", "x = 1 and x = 6", "x = -2 and x = -3", "x = 5 and x = 6"], "correct": 0, "topic": "Quadratic Equations"},
            {"q": "Simplify: i^2", "options": ["-1", "1", "i", "0"], "correct": 0, "topic": "Complex Numbers"},
            {"q": "What is log base 2 of 8?", "options": ["3", "2", "4", "8"], "correct": 0, "topic": "Logarithms"},
            {"q": "Solve for x: 2^x = 32", "options": ["5", "4", "6", "16"], "correct": 0, "topic": "Exponential Equations"},
            {"q": "What is the vertex of y = 2(x-3)^2 + 7?", "options": ["(3, 7)", "(-3, 7)", "(3, -7)", "(7, 3)"], "correct": 0, "topic": "Vertex Form"},
            {"q": "What is the sum of the first 4 terms of the geometric sequence 2, 6, 18, 54?", "options": ["80", "72", "54", "90"], "correct": 0, "topic": "Geometric Series"},
            {"q": "A rational function has a vertical asymptote where:", "options": ["The denominator equals zero (and the numerator doesn't)", "The numerator equals zero", "x = 0 always", "The function reaches its maximum"], "correct": 0, "topic": "Rational Functions"},
        ],
    },
    "Integrated Math I": {
        "questions": [
            {"q": "Solve the system: y = x + 2 and y = 2x - 1", "options": ["(3, 5)", "(1, 3)", "(-3, -1)", "(5, 3)"], "correct": 0, "topic": "Systems of Linear Equations"},
            {"q": "What does f(3) mean in function notation?", "options": ["The output of the function when x = 3", "The slope at x = 3", "It always equals 3", "The x-intercept"], "correct": 0, "topic": "Function Notation"},
            {"q": "A rigid transformation (translation, rotation, reflection) preserves:", "options": ["Size and shape (congruence)", "Only shape, not size", "Only size, not shape", "Neither"], "correct": 0, "topic": "Rigid Transformations"},
            {"q": "Which of these is a measure of the spread of a data set?", "options": ["Range", "Mean", "Median", "Mode"], "correct": 0, "topic": "One-Variable Statistics"},
            {"q": "The function y = 100(1.05)^t models what kind of change?", "options": ["Growth of 5% per time period", "Growth of 105% per period", "Decay of 5% per period", "Growth of 1.05% per period"], "correct": 0, "topic": "Exponential Growth"},
            {"q": "In the arithmetic sequence 4, 7, 10, 13, ..., what is the 10th term?", "options": ["31", "30", "34", "28"], "correct": 0, "topic": "Arithmetic Sequences"},
            {"q": "Solve: -2x + 5 ≤ 11", "options": ["x ≥ -3", "x ≤ -3", "x ≥ 3", "x ≤ 3"], "correct": 0, "topic": "Linear Inequalities"},
        ],
    },
    "Integrated Math II": {
        "questions": [
            {"q": "Solve: x^2 - 9 = 0", "options": ["x = 3 or x = -3", "x = 9", "x = -9", "x = 3 only"], "correct": 0, "topic": "Quadratic Equations"},
            {"q": "In a right triangle, sin(θ) equals:", "options": ["opposite/hypotenuse", "adjacent/hypotenuse", "opposite/adjacent", "hypotenuse/opposite"], "correct": 0, "topic": "Right Triangle Trigonometry"},
            {"q": "Two triangles are similar with corresponding sides in ratio 2:5. A side of the smaller triangle is 4. What is the corresponding side of the larger triangle?", "options": ["10", "8", "12.5", "20"], "correct": 0, "topic": "Similar Triangles"},
            {"q": "What is the probability of rolling a sum of 7 with two standard dice?", "options": ["1/6", "1/12", "1/36", "1/4"], "correct": 0, "topic": "Probability"},
            {"q": "To complete the square for x^2 + 6x, what constant should be added?", "options": ["9", "6", "3", "36"], "correct": 0, "topic": "Completing the Square"},
            {"q": "Simplify: √50", "options": ["5√2", "2√5", "10√5", "25√2"], "correct": 0, "topic": "Radicals"},
            {"q": "The perpendicular bisector of a chord always passes through:", "options": ["The center of the circle", "The midpoint of the radius", "A point on the circumference only", "The endpoint of the chord"], "correct": 0, "topic": "Circle Geometry"},
        ],
    },
    "Integrated Math III": {
        "questions": [
            {"q": "What is the degree of the polynomial 3x^4 - 2x^2 + 7?", "options": ["4", "2", "7", "3"], "correct": 0, "topic": "Polynomial Functions"},
            {"q": "Convert 180° to radians", "options": ["π", "π/2", "2π", "π/4"], "correct": 0, "topic": "Radians and the Unit Circle"},
            {"q": "Solve for x: log₃(x) = 4", "options": ["81", "12", "64", "34"], "correct": 0, "topic": "Logarithmic Functions"},
            {"q": "What is cos(60°)?", "options": ["1/2", "√3/2", "1", "√2/2"], "correct": 0, "topic": "Trigonometric Functions"},
            {"q": "A normal distribution is symmetric about:", "options": ["The mean", "The median only, not the mean", "The mode only", "The range"], "correct": 0, "topic": "Statistics and Normal Distribution"},
            {"q": "Simplify the rational expression (x^2 - 4)/(x - 2)", "options": ["x + 2", "x - 2", "x² - 2", "x + 4"], "correct": 0, "topic": "Rational Functions"},
            {"q": "A geometric sequence has first term 3 and common ratio 2. What is the 5th term?", "options": ["48", "24", "96", "16"], "correct": 0, "topic": "Sequences and Series"},
        ],
    },
    "Mathematical Models with Applications": {
        "questions": [
            {"q": "Using I = Prt, what is the simple interest on $2,000 at 5% annual rate for 3 years?", "options": ["$300", "$100", "$600", "$150"], "correct": 0, "topic": "Simple Interest"},
            {"q": "A car travels 240 miles using 8 gallons of gas. What is its fuel efficiency?", "options": ["30 mpg", "24 mpg", "32 mpg", "20 mpg"], "correct": 0, "topic": "Unit Rates"},
            {"q": "A population of 10,000 grows exponentially at 4% per year. Which expression models the population after t years?", "options": ["10,000(1.04)^t", "10,000(0.04)^t", "10,000 + 1.04t", "10,000(4)^t"], "correct": 0, "topic": "Exponential Modeling"},
            {"q": "Which graph type best displays the distribution of a large set of numeric data?", "options": ["Histogram", "Pie chart", "Line graph", "Flowchart"], "correct": 0, "topic": "Data Displays"},
            {"q": "A $60 item is discounted 25%. What is the sale price?", "options": ["$45", "$15", "$35", "$50"], "correct": 0, "topic": "Percent Applications"},
            {"q": "Convert 5 feet 8 inches to inches", "options": ["68 in", "60 in", "65 in", "72 in"], "correct": 0, "topic": "Unit Conversion"},
            {"q": "In the linear cost model y = 50 + 10x, what does the 10 represent?", "options": ["The rate of change (cost per unit)", "The starting fixed cost", "The total cost", "The number of units"], "correct": 0, "topic": "Linear Modeling"},
        ],
    },
    "Pre-Calculus": {
        "questions": [
            {"q": "What is the domain of f(x) = 1/(x - 4)?", "options": ["All real numbers except x = 4", "All real numbers", "x > 4 only", "All real numbers except x = 0"], "correct": 0, "topic": "Domain and Range"},
            {"q": "What is the Pythagorean trig identity sin²θ + cos²θ equal to?", "options": ["1", "0", "tan²θ", "2"], "correct": 0, "topic": "Trigonometric Identities"},
            {"q": "What is the period of y = sin(x)?", "options": ["2π", "π", "π/2", "4π"], "correct": 0, "topic": "Trigonometric Functions"},
            {"q": "Simplify: log(100), base 10", "options": ["2", "10", "100", "1"], "correct": 0, "topic": "Logarithms"},
            {"q": "A function is invertible (one-to-one) if it passes which test?", "options": ["The horizontal line test", "The vertical line test", "The origin symmetry test", "The midpoint test"], "correct": 0, "topic": "Inverse Functions"},
            {"q": "For the composite function (f∘g)(x), which is evaluated first?", "options": ["g(x) is evaluated first, then f is applied to the result", "f(x) is evaluated first, then g", "They are evaluated simultaneously", "Only f matters"], "correct": 0, "topic": "Composite Functions"},
            {"q": "What is the rectangular equivalent of the polar point (r, θ) = (2, π)?", "options": ["(-2, 0)", "(2, 0)", "(0, -2)", "(0, 2)"], "correct": 0, "topic": "Polar Coordinates"},
        ],
    },
    "Calculus": {
        "questions": [
            {"q": "What is the derivative of x^3?", "options": ["3x²", "x²", "3x", "x³/3"], "correct": 0, "topic": "Derivatives"},
            {"q": "What is lim(x→2) of (x² - 4)/(x - 2)?", "options": ["4", "0", "2", "Undefined"], "correct": 0, "topic": "Limits"},
            {"q": "What is ∫2x dx?", "options": ["x² + C", "2x² + C", "x²", "2 + C"], "correct": 0, "topic": "Integrals"},
            {"q": "What is the derivative of sin(x)?", "options": ["cos(x)", "-cos(x)", "-sin(x)", "sec²(x)"], "correct": 0, "topic": "Derivatives of Trig Functions"},
            {"q": "The Fundamental Theorem of Calculus connects which two concepts?", "options": ["Differentiation and integration", "Limits and continuity", "Series and sequences", "Vectors and derivatives"], "correct": 0, "topic": "Fundamental Theorem of Calculus"},
            {"q": "What does it mean for a function to be continuous at a point?", "options": ["The limit as x approaches the point equals the function's value there", "The derivative exists everywhere", "The function is always increasing", "The function has no maximum"], "correct": 0, "topic": "Continuity"},
            {"q": "Using the power rule, what is d/dx[5x^4]?", "options": ["20x³", "5x³", "20x⁴", "4x³"], "correct": 0, "topic": "Power Rule"},
        ],
    },
    "Finance": {
        "questions": [
            {"q": "In the compound interest formula A = P(1 + r/n)^(nt), what does r represent?", "options": ["The annual interest rate", "The number of years", "The principal amount", "The number of compounding periods"], "correct": 0, "topic": "Compound Interest"},
            {"q": "What does APR stand for?", "options": ["Annual Percentage Rate", "Annual Payment Return", "Average Percentage Rate", "Applied Principal Rate"], "correct": 0, "topic": "Loans and Credit"},
            {"q": "Diversification in investing primarily helps to:", "options": ["Reduce risk by spreading investments", "Guarantee higher returns", "Eliminate all investment risk", "Increase taxes owed"], "correct": 0, "topic": "Investing Basics"},
            {"q": "A higher credit score generally results in:", "options": ["Lower interest rates on loans", "Higher required down payments", "Automatic loan approval", "Higher taxes"], "correct": 0, "topic": "Credit Scores"},
            {"q": "What is the primary purpose of a budget?", "options": ["To plan and track income versus expenses", "To avoid paying taxes", "To increase debt", "To eliminate the need for savings"], "correct": 0, "topic": "Budgeting"},
            {"q": "If you invest $1,000 at 5% simple interest for 2 years, how much interest do you earn?", "options": ["$100", "$50", "$105", "$110"], "correct": 0, "topic": "Simple Interest"},
            {"q": "Which of these is generally considered a liquid asset?", "options": ["Cash in a checking account", "A house", "An unvested pension", "Fine art"], "correct": 0, "topic": "Assets and Liquidity"},
        ],
    },
    "Accounting": {
        "questions": [
            {"q": "What is the fundamental accounting equation?", "options": ["Assets = Liabilities + Equity", "Assets = Revenue - Expenses", "Equity = Assets + Liabilities", "Liabilities = Assets + Equity"], "correct": 0, "topic": "Accounting Equation"},
            {"q": "In double-entry accounting, an increase in an asset account is recorded as a:", "options": ["Debit", "Credit", "Neither", "Both a debit and a credit"], "correct": 0, "topic": "Debits and Credits"},
            {"q": "Which financial statement reports revenues and expenses over a period of time?", "options": ["Income statement", "Balance sheet", "Statement of cash flows", "Trial balance"], "correct": 0, "topic": "Financial Statements"},
            {"q": "The balance sheet reports a company's financial position at:", "options": ["A specific point in time", "The end of the fiscal year only", "The moment of a single transaction", "The average over the year"], "correct": 0, "topic": "Balance Sheet"},
            {"q": "Depreciation is used to:", "options": ["Allocate the cost of a tangible asset over its useful life", "Increase the value of an asset over time", "Record cash transactions only", "Eliminate liabilities"], "correct": 0, "topic": "Depreciation"},
            {"q": "What does GAAP stand for?", "options": ["Generally Accepted Accounting Principles", "Global Accounting and Auditing Practices", "General Assets and Asset Pricing", "Government Approved Accounting Policy"], "correct": 0, "topic": "Accounting Standards"},
            {"q": "Which of these is a liability?", "options": ["Accounts payable", "Cash", "Accounts receivable", "Equipment"], "correct": 0, "topic": "Assets vs. Liabilities"},
        ],
    },
    "Graphing and data": {
        "questions": [
            {"q": "Which type of graph is best for showing change over time?", "options": ["Line graph", "Pie chart", "Histogram", "Box plot"], "correct": 0, "topic": "Choosing Graph Types"},
            {"q": "Which graph is best used to show parts of a whole (percentages)?", "options": ["Pie chart", "Line graph", "Scatterplot", "Box plot"], "correct": 0, "topic": "Choosing Graph Types"},
            {"q": "What is the median of the data set: 3, 7, 9, 12, 15?", "options": ["9", "7", "12", "10"], "correct": 0, "topic": "Measures of Center"},
            {"q": "A scatterplot showing points trending upward from left to right shows what kind of correlation?", "options": ["Positive correlation", "Negative correlation", "No correlation", "Perfect causation"], "correct": 0, "topic": "Correlation"},
            {"q": "What is an outlier in a data set?", "options": ["A value significantly different from the rest of the data", "The average of the data set", "The most frequent value", "The middle value"], "correct": 0, "topic": "Outliers"},
            {"q": "The line of best fit on a scatterplot is used to:", "options": ["Model the trend/relationship between two variables", "Connect every data point exactly", "Show only the maximum value", "Replace the need for data"], "correct": 0, "topic": "Line of Best Fit"},
            {"q": "What is the mode of the data set: 2, 2, 3, 5, 7, 7, 7?", "options": ["7", "2", "5", "3"], "correct": 0, "topic": "Measures of Center"},
        ],
    },
    "Computer science": {
        "questions": [
            {"q": "What does CPU stand for?", "options": ["Central Processing Unit", "Computer Processing Unadapted", "Central Program Utility", "Core Processing Unit only"], "correct": 0, "topic": "Computer Hardware"},
            {"q": "What is the decimal value of the binary number 1011?", "options": ["11", "9", "13", "12"], "correct": 0, "topic": "Binary Numbers"},
            {"q": "A loop that repeats a specific number of times is typically called a:", "options": ["For loop", "If statement", "Function call", "Variable declaration"], "correct": 0, "topic": "Control Structures"},
            {"q": "What does an algorithm describe?", "options": ["A step-by-step procedure for solving a problem", "A type of hardware", "A programming language", "A database structure"], "correct": 0, "topic": "Algorithms"},
            {"q": "Which logical operator returns true only if both conditions are true?", "options": ["AND", "OR", "NOT", "XOR"], "correct": 0, "topic": "Boolean Logic"},
            {"q": "What is a variable in programming?", "options": ["A named storage location holding a value that can change", "A fixed value that never changes", "A type of loop", "An error message"], "correct": 0, "topic": "Variables and Data"},
            {"q": "Big-O notation is used to describe an algorithm's:", "options": ["Time or space complexity (efficiency)", "Programming language syntax", "File storage format", "Screen resolution"], "correct": 0, "topic": "Algorithm Efficiency"},
        ],
    },
    "Software programming": {
        "questions": [
            {"q": "What is a function/method primarily used for in programming?", "options": ["To group reusable code that performs a specific task", "To store a single value permanently", "To display the operating system version", "To connect to the internet only"], "correct": 0, "topic": "Functions"},
            {"q": "In most programming languages, array/list indexing typically starts at:", "options": ["0", "1", "-1", "10"], "correct": 0, "topic": "Arrays and Lists"},
            {"q": "What is the purpose of a version control system like Git?", "options": ["To track changes to code over time and enable collaboration", "To compile code into an executable", "To design user interfaces", "To encrypt source code"], "correct": 0, "topic": "Version Control"},
            {"q": "A syntax error occurs when:", "options": ["Code violates the grammar/rules of the programming language", "The program runs but produces the wrong output", "The computer overheats", "The internet connection is lost"], "correct": 0, "topic": "Debugging"},
            {"q": "What is recursion?", "options": ["A function that calls itself to solve a smaller instance of a problem", "A loop that never ends", "A variable that stores itself", "A type of syntax error"], "correct": 0, "topic": "Recursion"},
            {"q": "In object-oriented programming, a class is best described as:", "options": ["A blueprint for creating objects", "A single variable", "A loop structure", "A compiled binary file"], "correct": 0, "topic": "Object-Oriented Programming"},
            {"q": "What is debugging?", "options": ["The process of finding and fixing errors in code", "The process of writing documentation", "The process of deleting a program", "The process of compiling code only"], "correct": 0, "topic": "Debugging"},
        ],
    },
    "AI the future": {
        "questions": [
            {"q": "What is machine learning?", "options": ["A subset of AI where systems learn patterns from data rather than being explicitly programmed for every rule", "A robot that can physically walk", "A type of computer hardware", "A programming language"], "correct": 0, "topic": "What is AI"},
            {"q": "Which of these is a common real-world application of AI today?", "options": ["Recommendation systems (e.g., movie or shopping suggestions)", "Manually typed encyclopedia entries", "Printing a physical newspaper", "Hand-drawn maps"], "correct": 0, "topic": "AI Applications"},
            {"q": "What is a key concern regarding AI systems trained on biased data?", "options": ["They can produce biased or unfair outcomes", "They always become perfectly fair over time", "They cannot be used for decision-making", "They stop working once bias is introduced"], "correct": 0, "topic": "AI Ethics and Bias"},
            {"q": "What does 'training data' refer to in machine learning?", "options": ["The dataset used to teach a model to recognize patterns", "The final report generated by an AI", "The hardware running the AI", "The user interface of an app"], "correct": 0, "topic": "How AI Learns"},
            {"q": "Which best describes a large language model (LLM) like the ones powering modern chatbots?", "options": ["A model trained on large amounts of text to predict and generate human-like language", "A robot with physical arms and legs", "A database of pre-written human answers only", "A search engine index"], "correct": 0, "topic": "Large Language Models"},
            {"q": "Why is human oversight often recommended for AI systems used in high-stakes decisions (e.g., hiring, medical diagnosis)?", "options": ["Because AI can make mistakes or reflect biased data, so human review helps catch errors", "Because AI is always 100% accurate", "Because AI systems require no accountability", "Because law requires AI to make every final decision"], "correct": 0, "topic": "AI and Human Oversight"},
            {"q": "What term describes AI systems trained for one narrow task (e.g., image recognition) rather than general intelligence?", "options": ["Narrow AI (or weak AI)", "Artificial general intelligence (AGI)", "Quantum computing", "Superintelligence"], "correct": 0, "topic": "Types of AI"},
        ],
    },
    "Engineering principals": {
        "questions": [
            {"q": "What is typically the first step in the engineering design process?", "options": ["Identify/define the problem", "Build the final product", "Sell the product", "Patent the idea"], "correct": 0, "topic": "Engineering Design Process"},
            {"q": "Which simple machine is a ramp that reduces the force needed to raise an object?", "options": ["Inclined plane", "Lever", "Pulley", "Wheel and axle"], "correct": 0, "topic": "Simple Machines"},
            {"q": "In engineering, 'load' refers to:", "options": ["The force or weight a structure must support", "The color of a material", "The cost of a project", "The speed of assembly"], "correct": 0, "topic": "Structural Loads"},
            {"q": "What is the purpose of building and testing a prototype?", "options": ["To evaluate and improve a design before final production", "To skip the design process", "To finalize pricing only", "To avoid testing"], "correct": 0, "topic": "Prototyping and Testing"},
            {"q": "A material's ability to return to its original shape after being deformed is called:", "options": ["Elasticity", "Density", "Conductivity", "Viscosity"], "correct": 0, "topic": "Materials Science"},
            {"q": "Which shape is commonly used in structural engineering (e.g., bridge trusses) because it distributes force efficiently?", "options": ["Triangle", "Circle", "Rectangle", "Pentagon"], "correct": 0, "topic": "Structural Design"},
            {"q": "What does 'tolerance' mean in engineering design?", "options": ["The allowable amount a measurement can vary and still be acceptable", "The maximum weight a structure can ever hold", "The cost margin of a project", "The time allowed to finish a project"], "correct": 0, "topic": "Design Tolerances"},
        ],
    },
    "Web Design & Development": {
        "questions": [
            {"q": "What does HTML stand for?", "options": ["HyperText Markup Language", "High-Level Text Machine Language", "Hyperlink and Text Markup Level", "Home Tool Markup Language"], "correct": 0, "topic": "HTML Basics"},
            {"q": "What is the primary purpose of CSS in web development?", "options": ["To style and control the visual presentation of a web page", "To structure the content semantically", "To handle server-side database queries", "To manage domain name registration"], "correct": 0, "topic": "CSS Basics"},
            {"q": "In the CSS box model, which order (from inside out) is correct?", "options": ["Content, padding, border, margin", "Margin, border, padding, content", "Padding, content, margin, border", "Border, content, padding, margin"], "correct": 0, "topic": "CSS Box Model"},
            {"q": "What does 'responsive design' mean?", "options": ["A design that adapts to different screen sizes and devices", "A site that loads only on desktop computers", "A design using only black and white colors", "A website with no images"], "correct": 0, "topic": "Responsive Design"},
            {"q": "JavaScript is primarily used in web development to:", "options": ["Add interactivity and dynamic behavior to a page", "Define the page's structure only", "Style the page's colors and fonts", "Store the website's domain name"], "correct": 0, "topic": "JavaScript Basics"},
            {"q": "What HTTP status code typically indicates a 'page not found' error?", "options": ["404", "200", "301", "500"], "correct": 0, "topic": "HTTP Basics"},
            {"q": "Which HTML tag is used to create a hyperlink?", "options": ["<a>", "<link>", "<href>", "<p>"], "correct": 0, "topic": "HTML Elements"},
        ],
    },
    "Cybersecurity Fundamentals": {
        "questions": [
            {"q": "What is phishing?", "options": ["A scam that tricks users into revealing sensitive information, often via fake emails", "A type of computer virus that only affects mobile phones", "A method for encrypting files", "A firewall configuration setting"], "correct": 0, "topic": "Phishing"},
            {"q": "What does a firewall do?", "options": ["Monitors and controls network traffic based on security rules", "Physically cools down computer hardware", "Speeds up an internet connection", "Stores backup copies of files"], "correct": 0, "topic": "Firewalls"},
            {"q": "Which of these makes a password stronger?", "options": ["Using a long mix of uppercase, lowercase, numbers, and symbols", "Using your birthdate", "Using the word 'password'", "Using the same short word for every account"], "correct": 0, "topic": "Password Security"},
            {"q": "What is two-factor authentication (2FA)?", "options": ["A security process requiring two different forms of verification to access an account", "A password that is exactly two characters long", "A type of firewall", "A backup storage method"], "correct": 0, "topic": "Authentication"},
            {"q": "Encryption is used to:", "options": ["Convert data into a coded form that unauthorized users can't easily read", "Delete data permanently", "Speed up data transmission", "Compress files to save space"], "correct": 0, "topic": "Encryption"},
            {"q": "What is malware?", "options": ["Malicious software designed to damage, disrupt, or gain unauthorized access to a system", "A type of antivirus program", "A hardware component", "A network cable"], "correct": 0, "topic": "Malware"},
            {"q": "Social engineering attacks primarily exploit:", "options": ["Human trust and psychology rather than technical flaws", "Only outdated hardware", "Only weak Wi-Fi signals", "Only unencrypted websites"], "correct": 0, "topic": "Social Engineering"},
        ],
    },
    "Robotics & Automation": {
        "questions": [
            {"q": "What is an actuator in a robotic system?", "options": ["A component that converts energy into physical motion or action", "A component that senses light levels only", "A type of computer memory", "A wireless communication protocol"], "correct": 0, "topic": "Actuators"},
            {"q": "What is the role of a sensor in a robot?", "options": ["To detect and measure information about the environment or the robot's state", "To physically move the robot's joints", "To provide electrical power only", "To store the robot's programming code"], "correct": 0, "topic": "Sensors"},
            {"q": "A feedback control loop compares the actual output to the desired output and:", "options": ["Adjusts the system to reduce the difference (error)", "Ignores the difference completely", "Shuts the system down permanently", "Only records the difference for later review"], "correct": 0, "topic": "Feedback Control Loops"},
            {"q": "'Degrees of freedom' in a robotic arm refers to:", "options": ["The number of independent ways the arm can move", "The number of sensors installed", "The robot's maximum speed", "The robot's total weight"], "correct": 0, "topic": "Robotic Motion"},
            {"q": "Automation refers to:", "options": ["Technology performing tasks with minimal human intervention", "Any task performed manually by a human", "A type of sensor", "A robot's physical appearance"], "correct": 0, "topic": "Automation Concepts"},
            {"q": "What does a PLC (Programmable Logic Controller) commonly do in industrial automation?", "options": ["Controls machinery/processes based on programmed logic and sensor input", "Physically assembles robots by hand", "Provides electricity to an entire factory", "Replaces the need for any programming"], "correct": 0, "topic": "Industrial Automation"},
            {"q": "A closed-loop control system differs from an open-loop system because it:", "options": ["Uses feedback to continuously adjust its output", "Never uses sensors", "Cannot be automated", "Only works with human input at every step"], "correct": 0, "topic": "Control Systems"},
        ],
    },
    "Physical Education (PE)": {
        "questions": [
            {"q": "Which of these is NOT one of the five components of health-related physical fitness?", "options": ["Reaction time", "Cardiorespiratory endurance", "Muscular strength", "Flexibility"], "correct": 0, "topic": "Components of Fitness"},
            {"q": "What does the 'F' in the FITT principle stand for?", "options": ["Frequency", "Force", "Fatigue", "Flexibility"], "correct": 0, "topic": "FITT Principle"},
            {"q": "Why is a warm-up important before exercise?", "options": ["It gradually raises heart rate and prepares muscles, reducing injury risk", "It replaces the need to stretch afterward", "It is only needed for professional athletes", "It automatically burns the most calories of the workout"], "correct": 0, "topic": "Warm-Up and Injury Prevention"},
            {"q": "Cardiorespiratory endurance primarily measures:", "options": ["How efficiently the heart and lungs supply oxygen during sustained activity", "How much weight a person can lift once", "How flexible a person's joints are", "How fast a person can react to a stimulus"], "correct": 0, "topic": "Cardiorespiratory Endurance"},
            {"q": "In basketball, how many players from each team are on the court at one time?", "options": ["5", "6", "7", "4"], "correct": 0, "topic": "Sport Rules"},
            {"q": "What is the purpose of a cool-down after exercise?", "options": ["To gradually lower heart rate and help the body recover", "To increase heart rate further", "To skip stretching entirely", "To replace the warm-up entirely"], "correct": 0, "topic": "Cool-Down and Recovery"},
            {"q": "Muscular endurance is best defined as:", "options": ["The ability of a muscle to perform repeated contractions over time without fatiguing", "The maximum weight a muscle can lift one time", "The size of a muscle", "The flexibility of a joint"], "correct": 0, "topic": "Muscular Endurance"},
        ],
    },
    "Health & Wellness": {
        "questions": [
            {"q": "Which of the following is a macronutrient the body needs in large amounts?", "options": ["Protein", "Vitamin C", "Iron", "Calcium"], "correct": 0, "topic": "Nutrition"},
            {"q": "How many hours of sleep per night are generally recommended for teenagers?", "options": ["8-10 hours", "3-4 hours", "12-14 hours", "5-6 hours"], "correct": 0, "topic": "Sleep"},
            {"q": "What is a healthy way to manage stress?", "options": ["Regular physical activity, deep breathing, and adequate rest", "Avoiding sleep entirely", "Skipping meals", "Isolating from all support systems"], "correct": 0, "topic": "Stress Management"},
            {"q": "Why is staying hydrated important for the body?", "options": ["Water supports temperature regulation, digestion, and cell function", "Water has no real effect on the body", "Only athletes need to stay hydrated", "Hydration only matters in hot weather"], "correct": 0, "topic": "Hydration"},
            {"q": "Which of these is considered one of the main dimensions of overall wellness?", "options": ["Emotional wellness", "Only physical wellness matters", "Financial wellness has no connection to health", "Wellness is a single, one-dimensional concept"], "correct": 0, "topic": "Dimensions of Wellness"},
            {"q": "Washing hands regularly primarily helps prevent:", "options": ["The spread of germs and infectious disease", "Muscle soreness", "Poor eyesight", "High blood pressure"], "correct": 0, "topic": "Disease Prevention"},
            {"q": "A balanced diet generally includes a variety of:", "options": ["Fruits, vegetables, proteins, whole grains, and healthy fats", "Only sugary snacks", "A single food group eaten repeatedly", "No carbohydrates at all"], "correct": 0, "topic": "Nutrition"},
        ],
    },
    "Weight Training & Fitness": {
        "questions": [
            {"q": "What does 'progressive overload' mean in weight training?", "options": ["Gradually increasing weight, reps, or intensity over time", "Lifting the same weight forever", "Skipping rest days entirely", "Only doing cardio exercises"], "correct": 0, "topic": "Progressive Overload"},
            {"q": "A squat primarily targets which muscle group?", "options": ["Quadriceps and glutes", "Biceps", "Triceps", "Chest"], "correct": 0, "topic": "Muscle Groups and Exercises"},
            {"q": "In weight training terminology, a 'rep' (repetition) refers to:", "options": ["One complete movement of an exercise", "A full workout session", "A rest day", "The heaviest weight you can lift"], "correct": 0, "topic": "Training Terminology"},
            {"q": "Why is rest and recovery important between weight training sessions targeting the same muscle group?", "options": ["Muscles need time to repair and rebuild, which is when strength gains occur", "Rest has no effect on muscle growth", "More training without rest always builds muscle faster", "Recovery only matters for beginners"], "correct": 0, "topic": "Rest and Recovery"},
            {"q": "What is the primary purpose of a spotter during heavy weightlifting (e.g., bench press)?", "options": ["To help ensure safety and assist if the lifter cannot complete the lift", "To count reps only", "To add extra weight to the bar", "To time the workout"], "correct": 0, "topic": "Safety in Weight Training"},
            {"q": "A bicep curl's lifting phase is an example of which type of muscle contraction?", "options": ["Concentric contraction", "Isometric contraction", "Eccentric contraction", "Static contraction"], "correct": 0, "topic": "Muscle Contractions"},
            {"q": "What does a proper warm-up before weight training help reduce?", "options": ["The risk of injury", "The number of reps needed", "The total weight that can be lifted", "The need for good form"], "correct": 0, "topic": "Warm-Up and Safety"},
        ],
    },
}


def _shuffle_options(entry: dict) -> dict:
    """Reshuffles each question's option order so the correct answer isn't
    predictably at a fixed index (several generated batches always placed
    the correct answer first)."""
    for q in entry.get("questions", []):
        correct_text = q["options"][q["correct"]]
        shuffled = list(q["options"])
        random.shuffle(shuffled)
        q["options"] = shuffled
        q["correct"] = shuffled.index(correct_text)
    return entry


for _batch_module in (
    batch2_hs_ela_arts,
    batch4_science,
    batch5_social_lang_cultures_testprep,
    batch6_ap_sci_math_cs,
    batch7_ap_humanities,
    batch8_ib_courses,
):
    for _course_name, _entry in _batch_module.DATA.items():
        COURSE_QUESTION_BANK[_course_name] = _entry

for _entry in COURSE_QUESTION_BANK.values():
    _shuffle_options(_entry)

MASTERY_BANDS = [
    (0, 50, "Remediation", "#F4A6A6"),
    (51, 85, "Meets", "#8FE3EF"),
    (86, 100, "Mastery", "#B7E4C7"),
]


def mastery_band(score_pct: float) -> tuple[str, str]:
    for low, high, label, color in MASTERY_BANDS:
        if low <= score_pct <= high:
            return label, color
    return "Remediation", MASTERY_BANDS[0][3]


def get_citation(course: str) -> str | None:
    entry = COURSE_QUESTION_BANK.get(course)
    return entry.get("citation") if entry else None


def _bank_for_course(course: str) -> list[dict]:
    if course in COURSE_QUESTION_BANK:
        bank = list(COURSE_QUESTION_BANK[course]["questions"])
    else:
        category = category_for_course(course)
        bank = list(CATEGORY_QUESTION_BANK.get(category, []))

    if len(bank) < 3:
        bank = bank + CATEGORY_QUESTION_BANK["General"]
    return bank


def generate_quiz(course: str, username: str | None = None) -> list[dict]:
    bank = _bank_for_course(course)

    exclude_texts = set()
    if username:
        today = date.today().isoformat()
        for r in get_results_for_course(username, course):
            if r["date"][:10] == today:
                exclude_texts.update(q["question"] for q in r["questions"])

    available = [q for q in bank if q["q"] not in exclude_texts]
    if len(available) < 3:
        available = bank  # not enough unseen questions left today; allow repeats

    content_count = len(list_content_for_course(course))
    num_questions = max(1, min(15, content_count if content_count > 0 else 5))
    num_questions = min(num_questions, len(available))
    return random.sample(available, num_questions)


def _load_results() -> dict:
    return db.load("quiz_results")


def _save_results(data: dict) -> None:
    db.save("quiz_results", data)


def has_taken_today(username: str, course: str, quiz_type: str) -> bool:
    results = _load_results()
    today = date.today().isoformat()
    for r in results.get(username, {}).get(course, []):
        if r["quiz_type"] == quiz_type and r["date"][:10] == today:
            return True
    return False


def record_quiz_result(username: str, course: str, quiz_type: str, questions: list[dict], answers: list[int]) -> dict:
    total = len(questions)
    correct = sum(1 for q, a in zip(questions, answers) if a == q["correct"])
    score_pct = round((correct / total) * 100, 1) if total else 0.0

    results = _load_results()
    user_results = results.setdefault(username, {})
    course_results = user_results.setdefault(course, [])
    entry = {
        "quiz_type": quiz_type,
        "date": datetime.now().isoformat(),
        "score_pct": score_pct,
        "correct": correct,
        "total": total,
        "questions": [
            {
                "question": q["q"],
                "topic": q["topic"],
                "correct_answer": q["options"][q["correct"]],
                "chosen_answer": q["options"][a] if 0 <= a < len(q["options"]) else "No answer",
                "was_correct": a == q["correct"],
            }
            for q, a in zip(questions, answers)
        ],
    }
    course_results.append(entry)
    _save_results(results)
    return entry


def get_results_for_course(username: str, course: str) -> list[dict]:
    results = _load_results()
    return results.get(username, {}).get(course, [])


def get_all_courses_with_results(username: str) -> list[str]:
    results = _load_results()
    return list(results.get(username, {}).keys())


# ---------- Practice quizzes (a new one every day) and 7-day unit tests ----------

UNIT_TEST_EVERY_DAYS = 7
UNIT_TEST_MIN_QUESTIONS = 10
UNIT_TEST_MAX_QUESTIONS = 20
PRACTICE_QUESTIONS = 5
PRACTICE_DAYS_SHOWN = 7


def _wide_pool(course: str) -> list[dict]:
    """Course questions first, then same-category questions, de-duplicated."""
    seen, pool = set(), []
    sources = list(_bank_for_course(course))
    category = category_for_course(course)
    sources += CATEGORY_QUESTION_BANK.get(category, [])
    for q in sources:
        if q["q"] not in seen:
            seen.add(q["q"])
            pool.append(q)
    return sorted(pool, key=lambda q: q["q"])


def practice_quiz_type(day: date) -> str:
    return f"practice-{day.isoformat()}"


def generate_practice_quiz(course: str, day: date) -> list[dict]:
    """The same day always gives the same questions; each day picks a new mix."""
    pool = _wide_pool(course)
    rng = random.Random(f"{course}|practice|{day.isoformat()}")
    return rng.sample(pool, min(PRACTICE_QUESTIONS, len(pool)))


def unit_test_type(k: int) -> str:
    return f"unit-test-{k}"


def unit_test_periods_due(join_date: date, today: date) -> list[int]:
    """Unit test k unlocks join_date + 7*k days. Returns every unlocked k, newest last."""
    if today <= join_date:
        return []
    return list(range(1, (today - join_date).days // UNIT_TEST_EVERY_DAYS + 1))


def generate_unit_test(course: str, k: int) -> list[dict]:
    pool = _wide_pool(course)
    count = max(UNIT_TEST_MIN_QUESTIONS, min(UNIT_TEST_MAX_QUESTIONS, len(pool)))
    count = min(count, len(pool))
    rng = random.Random(f"{course}|unit|{k}")
    return rng.sample(pool, count)


def has_taken_type(username: str, course: str, quiz_type: str) -> bool:
    return any(r["quiz_type"] == quiz_type for r in get_results_for_course(username, course))


def label_for(quiz_type: str, date_str: str = "") -> str:
    if quiz_type == "check-in":
        return "Check-in"
    if quiz_type == "check-out":
        return "Check-out"
    if quiz_type.startswith("practice-"):
        return "Practice " + _short_date(quiz_type[len("practice-"):])
    if quiz_type.startswith("unit-test-"):
        return "Unit Test " + quiz_type[len("unit-test-"):]
    return quiz_type.title()


def _short_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d").replace(" 0", " ")
    except ValueError:
        return iso
