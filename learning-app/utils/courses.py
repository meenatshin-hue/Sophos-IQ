from collections import OrderedDict

# The full available-courses catalog, grouped for browsing. Each course name is
# used directly as the classification key for content, forums, and mastery data.
COURSE_CATALOG = OrderedDict([
    ("Elementary", [
        "Pre school and below", "Learning to read", "Counting (k-2)", "Kindergarten",
        "1st grade", "2nd grade", "3rd grade", "4th grade", "5th grade", "Elementary Recap",
    ]),
    ("Middle School", [
        "6th grade", "7th grade", "8th grade", "Middle school recap", "Middle school math",
        "Pre-Algebra", "Middle school biology", "Middle school chemistry", "Middle school Physics",
        "Middle school earth and environmental science", "Lab safety", "Middle school history",
        "Texas history", "World cultures", "Middle school geography",
    ]),
    ("High School Grade Level", [
        "9th grade", "10th grade", "11th grade", "12th grade",
    ]),
    ("English & Language Arts", [
        "English I (Intro to Literature)", "English II (World Literature)",
        "English III (American Literature)", "English IV (British Literature)", "Grammar",
        "Shakespearean Studies", "Creative writing", "Debate", "Public Speaking",
        "Journalism & Media Studies", "Yearbook Production",
    ]),
    ("Math", [
        "Algebra 1", "Geometry", "Advanced Geometry", "Algebra 2", "Integrated Math I",
        "Integrated Math II", "Integrated Math III", "Mathematical Models with Applications",
        "Pre-Calculus", "Calculus", "Finance", "Accounting", "Graphing and data",
    ]),
    ("Science", [
        "Biology", "Chemistry", "Physics", "Conceptual Physics",
        "Integrated Physics and Chemistry (IPC)", "Earth Science", "Environmental Science",
        "Helping our environment", "Forensic sciences", "Health science", "Neurology",
        "NASA and space", "Botany", "Genetics", "Microbiology", "Bio chemistry",
        "Introduction to Medical Careers", "Advanced Medical Sciences", "Anatomy & Physiology",
        "Marine Biology", "Astronomy", "Meteorology", "Zoology",
    ]),
    ("Social Studies", [
        "World History", "American history", "Government", "Study of laws", "Economics",
        "Psychology", "Human Behavior", "Sociology", "Philosophy", "High school geography",
        "Political speaking and thinking",
    ]),
    ("World Languages", [
        "Spanish", "French", "German", "Mandarin Chinese", "Latin", "Sign language (ASL)",
    ]),
    ("Technology & Engineering", [
        "Computer science", "Software programming", "AI the future", "Engineering principals",
        "Web Design & Development", "Cybersecurity Fundamentals", "Robotics & Automation",
    ]),
    ("Fine Arts", [
        "Reading music", "Reading music 2", "Band music", "Orchestra music", "Choir music",
        "Music Theory", "Studio Art 1", "Ceramics & Sculpting", "Digital Photography",
        "Theater Arts & Drama", "Dance",
    ]),
    ("Health & PE", [
        "Physical Education (PE)", "Health & Wellness", "Weight Training & Fitness",
    ]),
    ("AP Courses", [
        "AP Research", "AP Seminar", "AP Art History", "AP Music Theory",
        "AP Studio Art: 2-D Design", "AP Studio Art: 3-D Design", "AP Studio Art: Drawing",
        "AP English Language and Composition", "AP English Literature and Composition",
        "AP Comparative Government and Politics", "AP European History", "AP Human Geography",
        "AP Macroeconomics", "AP Microeconomics", "AP Psychology",
        "AP United States Government and Politics", "AP United States History",
        "AP World History: Modern", "AP Calculus AB", "AP Calculus BC",
        "AP Computer Science A", "AP Computer Science Principles", "AP Precalculus",
        "AP Statistics", "AP Biology", "AP Chemistry", "AP Environmental Science",
        "AP Physics 1: Algebra-Based", "AP Physics 2: Algebra-Based",
        "AP Physics C: Electricity and Magnetism", "AP Physics C: Mechanics",
        "AP African American Studies", "AP Chinese Language and Culture",
        "AP French Language and Culture", "AP German Language and Culture",
        "AP Italian Language and Culture", "AP Japanese Language and Culture", "AP Latin",
        "AP Spanish Language and Culture", "AP Spanish Literature and Culture",
    ]),
    ("IB Courses", [
        "IB Language A: Literature", "IB Language A: Language and Literature",
        "IB Language B (Spanish, French, German, Mandarin)", "IB Classical Languages",
        "IB Business Management", "IB Economics", "IB Geography", "IB History",
        "IB Global Politics", "IB Philosophy", "IB Psychology",
        "IB Social and Cultural Anthropology", "IB World Religions", "IB Biology",
        "IB Chemistry", "IB Physics", "IB Design Technology",
        "IB Environmental Systems and Societies", "IB Sports, Exercise and Health Science",
        "IB Computer Science", "IB Mathematics: Analysis and Approaches",
        "IB Mathematics: Applications and Interpretation", "IB Statistics", "IB Dance",
        "IB Music", "IB Film", "IB Theatre", "IB Visual Arts",
    ]),
    ("Test Prep & College Readiness", [
        "Sat prep (reading)", "Sat prep (math)", "ACT Prep (English & Reading)",
        "ACT Prep (Math & Science)", "Get ready for college", "Study Skills & Test Strategies",
        "Tips for teaching",
    ]),
    ("World Cultures", [
        "The amazing cultures (North America)", "The amazing cultures (South America)",
        "The amazing cultures (Africa)", "The amazing cultures (Europe)",
        "The amazing cultures (Asia)", "The amazing cultures (Oceania & Australia)",
    ]),
])


def all_course_keys() -> list[str]:
    keys = []
    for courses in COURSE_CATALOG.values():
        keys.extend(courses)
    return keys


def category_for_course(course: str) -> str | None:
    for category, courses in COURSE_CATALOG.items():
        if course in courses:
            return category
    return None
