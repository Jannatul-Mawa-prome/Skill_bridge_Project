from app.database.connection import SessionLocal
from app.models.community import Community
from app.models.roadmap import Roadmap, Module, Task


def create_roadmap(
    db,
    community_name,
    roadmap_title,
    roadmap_description,
    modules_data
):
    # Community খুঁজে বের করা
    community = (
        db.query(Community)
        .filter(Community.name == community_name)
        .first()
    )

    if not community:
        print(f"Community not found: {community_name}")
        return

    # আগে থেকেই roadmap আছে কিনা check
    existing_roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.community_id == community.id)
        .first()
    )

    if existing_roadmap:
        print(f"Roadmap already exists for: {community_name}")
        return

    # Roadmap তৈরি
    roadmap = Roadmap(
        community_id=community.id,
        title=roadmap_title,
        description=roadmap_description,
        total_modules=len(modules_data)
    )

    db.add(roadmap)
    db.flush()

    # Modules তৈরি
    for module_data in modules_data:

        module = Module(
            roadmap_id=roadmap.id,
            order=module_data["order"],
            title=module_data["title"],
            description=module_data["description"]
        )

        db.add(module)
        db.flush()

        # Tasks তৈরি
        for task_order, task_title in enumerate(
            module_data["tasks"],
            start=1
        ):

            task = Task(
                module_id=module.id,
                order=task_order,
                title=task_title
            )

            db.add(task)

    db.commit()

    print(f"Roadmap created successfully: {community_name}")


def seed_roadmaps():

    db = SessionLocal()

    try:

        # ==================================================
        # PROGRAMMING ROADMAP
        # ==================================================

        programming_modules = [

            {
                "order": 1,
                "title": "Programming Fundamentals",
                "description": "Learn the basic building blocks of programming.",
                "tasks": [
                    "Variables",
                    "Data Types",
                    "Input & Output",
                    "Operators"
                ]
            },

            {
                "order": 2,
                "title": "Conditions & Loops",
                "description": "Master decision making and repetition in programs.",
                "tasks": [
                    "If / Else",
                    "Switch",
                    "For Loop",
                    "While Loop"
                ]
            },

            {
                "order": 3,
                "title": "Functions",
                "description": "Learn how to create reusable and organized code.",
                "tasks": [
                    "Function Basics",
                    "Parameters",
                    "Return Values",
                    "Recursion"
                ]
            },

            {
                "order": 4,
                "title": "Data Structures",
                "description": "Learn important data structures used in programming.",
                "tasks": [
                    "Arrays",
                    "Linked List",
                    "Stack",
                    "Queue"
                ]
            },

            {
                "order": 5,
                "title": "Algorithms",
                "description": "Learn searching, sorting and algorithmic thinking.",
                "tasks": [
                    "Searching",
                    "Sorting",
                    "Binary Search",
                    "Algorithm Complexity"
                ]
            },

            {
                "order": 6,
                "title": "Problem Solving",
                "description": "Apply your programming knowledge to real problems.",
                "tasks": [
                    "Problem Analysis",
                    "Brute Force",
                    "Optimization",
                    "Practice Problems"
                ]
            }

        ]


        create_roadmap(
            db=db,
            community_name="Programming",
            roadmap_title="Beginner → Intermediate Programming",
            roadmap_description=(
                "A structured programming roadmap "
                "from beginner to intermediate level."
            ),
            modules_data=programming_modules
        )


        # ==================================================
        # WEB DEVELOPMENT ROADMAP
        # ==================================================

        web_modules = [

            {
                "order": 1,
                "title": "HTML Fundamentals",
                "description": "Learn semantic HTML and website structure.",
                "tasks": [
                    "HTML Elements",
                    "Forms",
                    "Semantic HTML",
                    "Tables"
                ]
            },

            {
                "order": 2,
                "title": "CSS & Responsive Design",
                "description": "Create beautiful responsive layouts using CSS.",
                "tasks": [
                    "CSS Basics",
                    "Flexbox",
                    "Grid",
                    "Responsive Design"
                ]
            },

            {
                "order": 3,
                "title": "JavaScript Fundamentals",
                "description": "Add interactivity and dynamic behavior to websites.",
                "tasks": [
                    "Variables",
                    "Functions",
                    "DOM",
                    "Events"
                ]
            },

            {
                "order": 4,
                "title": "Frontend Frameworks",
                "description": "Learn modern frontend development with React.",
                "tasks": [
                    "React Basics",
                    "Components",
                    "Props",
                    "State"
                ]
            },

            {
                "order": 5,
                "title": "Backend Development",
                "description": "Learn how to build APIs and backend applications.",
                "tasks": [
                    "Node.js",
                    "Express",
                    "REST API",
                    "Authentication"
                ]
            },

            {
                "order": 6,
                "title": "Databases",
                "description": "Learn SQL and NoSQL databases.",
                "tasks": [
                    "SQL Basics",
                    "PostgreSQL",
                    "MongoDB",
                    "Database Relationships"
                ]
            },

            {
                "order": 7,
                "title": "Full Stack Projects",
                "description": "Build complete full-stack web applications.",
                "tasks": [
                    "Project Planning",
                    "Frontend Integration",
                    "Backend Integration",
                    "Deployment"
                ]
            }

        ]


        create_roadmap(
            db=db,
            community_name="Web Development",
            roadmap_title="Beginner → Full Stack Developer",
            roadmap_description=(
                "A structured roadmap from frontend "
                "fundamentals to full-stack development."
            ),
            modules_data=web_modules
        )

    finally:

        db.close()


if __name__ == "__main__":
    seed_roadmaps()