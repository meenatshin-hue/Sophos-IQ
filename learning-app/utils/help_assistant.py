FAQ = [
    (["log in", "login", "log on", "password", "can't sign in", "cant sign in"],
     "To log in, use the username and password you created at sign-up on the Home page. "
     "You must create an account before you can log in, and only one account is allowed per Gmail address."),
    (["create account", "sign up", "signup", "register"],
     "Go to the Home page and open the 'Create Account' tab. You'll need a Gmail address, "
     "a username, a password, your school district, grade level, and location."),
    (["course", "grade", "class", "subject"],
     "Head to 'Select Course' in the sidebar to browse courses by category and pick one. "
     "Your current course is saved to your account automatically."),
    (["quiz", "test", "score", "mastery", "percent"],
     "Quizzes appear automatically when you open a course (check-in) and when you finish "
     "for the day (check-out). Your scores show up as colored bars on the 'View Mastery' page, "
     "along with a walkthrough of what to review."),
    (["forum", "chat", "message", "reply", "comment"],
     "Each course has its own Forum. Click 'New Chat' to start a discussion, or open an "
     "existing chat to reply, vote on polls, and give it a thumbs up."),
    (["friend"],
     "You can send a friend request by clicking the 🙂 Friend button next to someone's name "
     "in the Forum. Once they accept, you'll see them on your Friends tab and Account page."),
    (["club"],
     "Visit 'Student Owned Clubs' to create a club (name, related course, description) or join "
     "an existing one. Each club has its own private forum and member-added lessons."),
    (["add content", "upload content", "create content", "lesson"],
     "Only Administrator accounts can add content to a course page, from the 'Add Content' page. "
     "Students in a club can add lessons to that club from the club's page."),
    (["profile picture", "picture", "photo", "avatar"],
     "Go to 'Your Account' to upload or change your profile picture, and to edit your bio and hobbies."),
    (["administrator", "admin"],
     "Account type (Student or Administrator) is set when you create your account and can't be "
     "changed afterward. Contact your school if this needs to change."),
]

FALLBACK = (
    "I'm not sure about that one yet! Try rephrasing your question, or post it in the Forum "
    "for your course — other students and administrators can help too."
)


def answer(question: str) -> str:
    q = question.lower()
    for keywords, response in FAQ:
        if any(k in q for k in keywords):
            return response
    return FALLBACK
