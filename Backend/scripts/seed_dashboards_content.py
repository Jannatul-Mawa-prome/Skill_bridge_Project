"""
Seed script to populate initial meaningful content for:
1. Programming Community (ID: 2)
2. Web Development Community (ID: 3)
and ensure administrator access.
"""

from datetime import datetime, timedelta
import os
import sys

# Ensure Backend directory is on sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.connection import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.profile import Profile
from app.models.community import Community, CommunityMembership
from app.models.roadmap import Roadmap, Module, Task, UserTaskProgress
from app.models.challenge import Challenge
from app.models.resource import Resource
from app.models.announcement import Announcement
from app.models.event import Event
from app.models.discussion import Discussion


def seed_data():
    db = SessionLocal()
    print("Starting dashboard & admin content seeding...")

    try:
        # ========================================================
        # 1. ADMIN USER & TEST USERS
        # ========================================================
        admin_email = "admin@skillbridge.edu"
        admin_user = db.query(User).filter_by(edu_email=admin_email).first()
        if not admin_user:
            admin_user = User(
                edu_email=admin_email,
                password_hash=hash_password("Admin@12345"),
                is_verified=True,
                is_active=True,
                is_admin=True,
            )
            admin_profile = Profile(
                full_name="Platform Admin",
                roll="ADMIN-001",
                semester="N/A",
                mobile="01700000000",
                department="Computer Science & Engineering",
                university="DUET",
                bio="Platform Administrator for SkillBridge",
            )
            admin_user.profile = admin_profile
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"Created dedicated admin: {admin_email} (password: Admin@12345)")
        else:
            admin_user.is_admin = True
            admin_user.is_active = True
            db.commit()
            print(f"Updated existing admin user: {admin_email}")

        # Also ensure jm.promeei51@gmail.com and 2204029@student.duet.ac.bd have admin access for easy testing
        for test_email in ["jm.promeei51@gmail.com", "2204029@student.duet.ac.bd"]:
            u = db.query(User).filter_by(edu_email=test_email).first()
            if u:
                u.is_admin = True
                u.is_active = True
                print(f"Granted admin rights to: {test_email}")
        db.commit()

        author_id = admin_user.id

        # ========================================================
        # 2. COMMUNITIES
        # ========================================================
        prog_comm = db.query(Community).filter(Community.name.ilike("%programming%")).first()
        web_comm = db.query(Community).filter(Community.name.ilike("%web%")).first()

        if not prog_comm:
            prog_comm = Community(
                name="Programming Community",
                description="Learn programming, master data structures and algorithms, and solve problems together.",
                active_members_count=2,
                is_active=True
            )
            db.add(prog_comm)
            db.commit()
            db.refresh(prog_comm)

        if not web_comm:
            web_comm = Community(
                name="Web Development Community",
                description="Build modern web applications with HTML, CSS, JavaScript, React, and backend APIs.",
                active_members_count=2,
                is_active=True
            )
            db.add(web_comm)
            db.commit()
            db.refresh(web_comm)

        print(f"Target Communities: {prog_comm.name} (ID: {prog_comm.id}), {web_comm.name} (ID: {web_comm.id})")

        # Ensure admin has approved memberships in both
        for c in [prog_comm, web_comm]:
            m = db.query(CommunityMembership).filter_by(user_id=admin_user.id, community_id=c.id).first()
            if not m:
                m = CommunityMembership(
                    user_id=admin_user.id,
                    community_id=c.id,
                    role="admin",
                    status="approved",
                    streak=7,
                    is_active=True,
                )
                db.add(m)
        db.commit()

        # ========================================================
        # 3. PROGRAMMING COMMUNITY CONTENT
        # ========================================================
        # Roadmap
        prog_roadmap = db.query(Roadmap).filter_by(community_id=prog_comm.id).first()
        if not prog_roadmap:
            prog_roadmap = Roadmap(
                community_id=prog_comm.id,
                title="Programming & Problem Solving Roadmap",
                description="A structured 4-stage path covering fundamentals, modular programming, data structures, and algorithms.",
                total_modules=4,
            )
            db.add(prog_roadmap)
            db.commit()
            db.refresh(prog_roadmap)
        else:
            prog_roadmap.title = "Programming & Problem Solving Roadmap"
            prog_roadmap.description = "A structured 4-stage path covering fundamentals, modular programming, data structures, and algorithms."
            prog_roadmap.total_modules = 4
            db.commit()

        # Clean existing modules to seed full 4 modules cleanly
        existing_mods = db.query(Module).filter_by(roadmap_id=prog_roadmap.id).all()
        for mod in existing_mods:
            db.delete(mod)
        db.commit()

        prog_modules_data = [
            {
                "order": 1,
                "title": "Programming Fundamentals",
                "description": "Master variables, memory allocation, data types, operators, and basic I/O.",
                "tasks": [
                    "Variables, Memory & Data Types",
                    "Operators, Expressions & Precedence",
                    "Conditionals (if/else, switch)",
                    "Loops & Iterations (for, while)",
                ]
            },
            {
                "order": 2,
                "title": "Functions & Modular Code",
                "description": "Learn reusable code structure, parameter passing, return values, and recursion.",
                "tasks": [
                    "Function Declarations & Prototypes",
                    "Pass by Value vs Pass by Reference",
                    "Scope, Lifetime & Static Variables",
                    "Recursion & Call Stack Basics",
                ]
            },
            {
                "order": 3,
                "title": "Data Structures Essentials",
                "description": "Essential collections for organizing and storing data efficiently.",
                "tasks": [
                    "Arrays & Dynamic Vectors",
                    "Strings & String Manipulation",
                    "Stacks & Queues (LIFO & FIFO)",
                    "Hash Tables, Dictionaries & Sets",
                ]
            },
            {
                "order": 4,
                "title": "Algorithms & Problem Solving",
                "description": "Searching, sorting, two pointers, and time/space complexity analysis.",
                "tasks": [
                    "Linear & Binary Search Algorithms",
                    "Bubble, Selection & Merge Sort",
                    "Two Pointers & Sliding Window Technique",
                    "Asymptotic Notation & Big-O Analysis",
                ]
            }
        ]

        for m_data in prog_modules_data:
            mod = Module(
                roadmap_id=prog_roadmap.id,
                order=m_data["order"],
                title=m_data["title"],
                description=m_data["description"],
            )
            db.add(mod)
            db.commit()
            db.refresh(mod)
            for t_idx, task_title in enumerate(m_data["tasks"], start=1):
                task = Task(module_id=mod.id, order=t_idx, title=task_title)
                db.add(task)
        db.commit()
        print(f"Seeded 4 modules and 16 tasks for {prog_comm.name}")

        # Mark first 2 tasks completed for admin user to show live progress
        first_tasks = (
            db.query(Task)
            .join(Module, Task.module_id == Module.id)
            .filter(Module.roadmap_id == prog_roadmap.id)
            .order_by(Module.order, Task.order)
            .limit(2)
            .all()
        )
        for t in first_tasks:
            progress = db.query(UserTaskProgress).filter_by(user_id=admin_user.id, task_id=t.id).first()
            if not progress:
                db.add(UserTaskProgress(user_id=admin_user.id, task_id=t.id, is_completed=True, completed_at=datetime.utcnow()))
        db.commit()

        # Challenges for Programming
        db.query(Challenge).filter_by(community_id=prog_comm.id).delete()
        prog_challenges = [
            Challenge(
                community_id=prog_comm.id,
                title="Two Sum Problem",
                description="Given an array of integers and an integer target, return indices of the two numbers that add up to target.",
                difficulty="Easy",
                xp_reward=100,
                deadline=datetime.utcnow() + timedelta(days=4),
                is_active=True,
            ),
            Challenge(
                community_id=prog_comm.id,
                title="Reverse a String In-Place",
                description="Write a function that reverses an array of characters in O(1) extra space.",
                difficulty="Easy",
                xp_reward=100,
                deadline=datetime.utcnow() + timedelta(days=7),
                is_active=True,
            ),
            Challenge(
                community_id=prog_comm.id,
                title="Valid Matching Parentheses",
                description="Given a string containing just brackets, determine if the input string is valid using a stack.",
                difficulty="Medium",
                xp_reward=150,
                deadline=datetime.utcnow() + timedelta(days=10),
                is_active=True,
            ),
            Challenge(
                community_id=prog_comm.id,
                title="Merge Two Sorted Linked Lists",
                description="Merge two sorted singly linked lists into a single sorted list and return its head.",
                difficulty="Medium",
                xp_reward=200,
                deadline=datetime.utcnow() + timedelta(days=14),
                is_active=True,
            ),
        ]
        db.add_all(prog_challenges)

        # Resources for Programming
        db.query(Resource).filter_by(community_id=prog_comm.id).delete()
        prog_resources = [
            Resource(
                community_id=prog_comm.id,
                title="C++ & Python Standard Library Reference",
                resource_type="PDF",
                difficulty="Beginner",
                url="https://en.cppreference.com/w/",
                description="Complete quick-reference cheat sheet for standard functions, containers, and methods.",
            ),
            Resource(
                community_id=prog_comm.id,
                title="Python Problem Solving & DSA Masterclass",
                resource_type="Video",
                difficulty="Beginner",
                url="https://www.youtube.com/results?search_query=dsa+in+python",
                description="Comprehensive video series breaking down algorithms from scratch with visual diagrams.",
            ),
            Resource(
                community_id=prog_comm.id,
                title="Algorithmic Thinking & Complexity Guide",
                resource_type="Article",
                difficulty="Intermediate",
                url="https://www.geeksforgeeks.org/analysis-of-algorithms-set-1-asymptotic-analysis/",
                description="Deep dive into Big-O time and space complexity analysis with real-world examples.",
            ),
            Resource(
                community_id=prog_comm.id,
                title="LeetCode Problem Solving Patterns",
                resource_type="Link",
                difficulty="Intermediate",
                url="https://leetcode.com/explore/",
                description="Interactive problem sets grouped by fundamental algorithmic design patterns.",
            ),
        ]
        db.add_all(prog_resources)

        # Announcements for Programming
        db.query(Announcement).filter_by(community_id=prog_comm.id).delete()
        prog_announcements = [
            Announcement(
                community_id=prog_comm.id,
                author_id=author_id,
                title="Weekly Problem Solving Contest is Live!",
                content="Test your skills in this week's timed coding contest. Complete challenges and climb the leaderboard!",
            ),
            Announcement(
                community_id=prog_comm.id,
                author_id=author_id,
                title="Welcome to the Programming Community!",
                content="Start tracking your learning path through our newly launched 4-module roadmap. Don't forget to keep up your streak!",
            ),
        ]
        db.add_all(prog_announcements)

        # Events for Programming
        db.query(Event).filter_by(community_id=prog_comm.id).delete()
        prog_events = [
            Event(
                community_id=prog_comm.id,
                title="Live DSA & Problem Solving Workshop",
                description="Interactive mentor session walking through recursion, stacks, and binary search.",
                event_date=datetime.utcnow() + timedelta(days=5, hours=3),
                status="upcoming",
            ),
            Event(
                community_id=prog_comm.id,
                title="Weekend Competitive Programming Sprint",
                description="A fast-paced 2-hour problem solving sprint with live scoring and discussion.",
                event_date=datetime.utcnow() + timedelta(days=12, hours=4),
                status="upcoming",
            ),
        ]
        db.add_all(prog_events)

        # Discussions for Programming
        db.query(Discussion).filter_by(community_id=prog_comm.id).delete()
        prog_discussions = [
            Discussion(
                community_id=prog_comm.id,
                author_id=author_id,
                title="How should beginners start learning DSA for competitive programming?",
                content="What are the best resources and problems to start with after getting comfortable with loops and functions?",
                reply_count=8,
            ),
            Discussion(
                community_id=prog_comm.id,
                author_id=author_id,
                title="Best practices for mastering recursion and backtracking",
                content="Tips on how to formulate the base case and draw recursive decision trees effectively.",
                reply_count=5,
            ),
            Discussion(
                community_id=prog_comm.id,
                author_id=author_id,
                title="Two Pointers vs Sliding Window: Key differences",
                content="A quick summary of when to use fixed-size versus dynamic-size sliding windows.",
                reply_count=3,
            ),
        ]
        db.add_all(prog_discussions)
        db.commit()

        # ========================================================
        # 4. WEB DEVELOPMENT COMMUNITY CONTENT
        # ========================================================
        # Roadmap
        web_roadmap = db.query(Roadmap).filter_by(community_id=web_comm.id).first()
        if not web_roadmap:
            web_roadmap = Roadmap(
                community_id=web_comm.id,
                title="Full-Stack Web Development Roadmap",
                description="A structured path from HTML/CSS layouts through modern JavaScript, React, and FastAPI backends.",
                total_modules=4,
            )
            db.add(web_roadmap)
            db.commit()
            db.refresh(web_roadmap)
        else:
            web_roadmap.title = "Full-Stack Web Development Roadmap"
            web_roadmap.description = "A structured path from HTML/CSS layouts through modern JavaScript, React, and FastAPI backends."
            web_roadmap.total_modules = 4
            db.commit()

        # Clean existing modules
        existing_web_mods = db.query(Module).filter_by(roadmap_id=web_roadmap.id).all()
        for mod in existing_web_mods:
            db.delete(mod)
        db.commit()

        web_modules_data = [
            {
                "order": 1,
                "title": "Modern HTML5 & Responsive CSS",
                "description": "Build accessible markup, fluid responsive layouts, Flexbox and Grid systems.",
                "tasks": [
                    "Semantic HTML5 Elements & Web Accessibility",
                    "CSS Flexbox Layouts & Alignment",
                    "CSS Grid Systems & Template Areas",
                    "Responsive Design & Media Queries",
                ]
            },
            {
                "order": 2,
                "title": "JavaScript Mastery & DOM",
                "description": "Master ES6+ syntax, asynchronous programming, DOM manipulation, and browser APIs.",
                "tasks": [
                    "ES6+ Syntax, Scope, Destructuring & Arrow Functions",
                    "DOM Manipulation & Event Listeners",
                    "Async JavaScript, Promises & Fetch API",
                    "Web Storage (localStorage & sessionStorage)",
                ]
            },
            {
                "order": 3,
                "title": "Frontend Frameworks & UI Design",
                "description": "Component architecture, state management, client-side routing, and styling.",
                "tasks": [
                    "Component-Based UI Architecture",
                    "Managing State & Props with Hooks",
                    "Client-Side Routing & Navigation",
                    "Utility-First Styling with Tailwind CSS",
                ]
            },
            {
                "order": 4,
                "title": "Backend Integration & APIs",
                "description": "RESTful endpoints, database modeling, and authentication security.",
                "tasks": [
                    "RESTful API Principles & HTTP Request Methods",
                    "Server Routing & Controllers with FastAPI",
                    "Database Modeling with PostgreSQL & SQLAlchemy",
                    "User Authentication & JWT Security",
                ]
            }
        ]

        for m_data in web_modules_data:
            mod = Module(
                roadmap_id=web_roadmap.id,
                order=m_data["order"],
                title=m_data["title"],
                description=m_data["description"],
            )
            db.add(mod)
            db.commit()
            db.refresh(mod)
            for t_idx, task_title in enumerate(m_data["tasks"], start=1):
                task = Task(module_id=mod.id, order=t_idx, title=task_title)
                db.add(task)
        db.commit()
        print(f"Seeded 4 modules and 16 tasks for {web_comm.name}")

        # Mark first 3 tasks completed for admin user
        first_web_tasks = (
            db.query(Task)
            .join(Module, Task.module_id == Module.id)
            .filter(Module.roadmap_id == web_roadmap.id)
            .order_by(Module.order, Task.order)
            .limit(3)
            .all()
        )
        for t in first_web_tasks:
            progress = db.query(UserTaskProgress).filter_by(user_id=admin_user.id, task_id=t.id).first()
            if not progress:
                db.add(UserTaskProgress(user_id=admin_user.id, task_id=t.id, is_completed=True, completed_at=datetime.utcnow()))
        db.commit()

        # Challenges for Web Development
        db.query(Challenge).filter_by(community_id=web_comm.id).delete()
        web_challenges = [
            Challenge(
                community_id=web_comm.id,
                title="Responsive Landing Page Challenge",
                description="Build a responsive, mobile-first product landing page using semantic HTML5 and CSS Flexbox/Grid.",
                difficulty="Easy",
                xp_reward=100,
                deadline=datetime.utcnow() + timedelta(days=5),
                is_active=True,
            ),
            Challenge(
                community_id=web_comm.id,
                title="Interactive Task Tracker with LocalStorage",
                description="Create a task manager application supporting add, edit, toggle, delete, and persistent storage.",
                difficulty="Easy",
                xp_reward=150,
                deadline=datetime.utcnow() + timedelta(days=8),
                is_active=True,
            ),
            Challenge(
                community_id=web_comm.id,
                title="Weather Dashboard with Fetch API",
                description="Fetch weather data from an API, handle loading and error states, and render dynamic weather cards.",
                difficulty="Medium",
                xp_reward=200,
                deadline=datetime.utcnow() + timedelta(days=12),
                is_active=True,
            ),
            Challenge(
                community_id=web_comm.id,
                title="Full-Stack JWT Authentication Flow",
                description="Implement a complete signup/login form with client validation, JWT bearer token storage, and auth guard.",
                difficulty="Hard",
                xp_reward=300,
                deadline=datetime.utcnow() + timedelta(days=18),
                is_active=True,
            ),
        ]
        db.add_all(web_challenges)

        # Resources for Web Development
        db.query(Resource).filter_by(community_id=web_comm.id).delete()
        web_resources = [
            Resource(
                community_id=web_comm.id,
                title="MDN Web Docs - HTML, CSS & JavaScript",
                resource_type="Link",
                difficulty="Beginner",
                url="https://developer.mozilla.org/en-US/",
                description="The industry standard documentation for web standards, browser APIs, and best practices.",
            ),
            Resource(
                community_id=web_comm.id,
                title="Modern JavaScript from Scratch Video Course",
                resource_type="Video",
                difficulty="Beginner",
                url="https://www.youtube.com/results?search_query=modern+javascript+course",
                description="Complete video course covering ES6+, DOM manipulation, event loops, and async/await.",
            ),
            Resource(
                community_id=web_comm.id,
                title="CSS Grid & Flexbox Visual Cheat Sheet",
                resource_type="PDF",
                difficulty="Beginner",
                url="https://css-tricks.com/snippets/css/a-guide-to-flexbox/",
                description="Visual reference guide detailing all container and item properties with diagrams.",
            ),
            Resource(
                community_id=web_comm.id,
                title="FastAPI & Modern RESTful API Handbook",
                resource_type="Article",
                difficulty="Intermediate",
                url="https://fastapi.tiangolo.com/tutorial/",
                description="Step-by-step guide to designing performant REST APIs with Python, Pydantic, and SQLAlchemy.",
            ),
        ]
        db.add_all(web_resources)

        # Announcements for Web Development
        db.query(Announcement).filter_by(community_id=web_comm.id).delete()
        web_announcements = [
            Announcement(
                community_id=web_comm.id,
                author_id=author_id,
                title="Frontend Hackathon Announced!",
                content="Build a creative single-page application using modern web technologies. Submissions close at the end of the month!",
            ),
            Announcement(
                community_id=web_comm.id,
                author_id=author_id,
                title="New Web Development Roadmap Released!",
                content="Check out our newly structured 4-module roadmap covering HTML, CSS, JavaScript, React, and Backend integration.",
            ),
        ]
        db.add_all(web_announcements)

        # Events for Web Development
        db.query(Event).filter_by(community_id=web_comm.id).delete()
        web_events = [
            Event(
                community_id=web_comm.id,
                title="Hands-on Workshop: Building with React & Tailwind",
                description="Live interactive coding session translating a design mockup into a clean responsive component.",
                event_date=datetime.utcnow() + timedelta(days=6, hours=2),
                status="upcoming",
            ),
            Event(
                community_id=web_comm.id,
                title="Web Performance & SEO Best Practices",
                description="Learn Core Web Vitals, image optimization, Lighthouse audits, and server-side rendering strategies.",
                event_date=datetime.utcnow() + timedelta(days=15, hours=1),
                status="upcoming",
            ),
        ]
        db.add_all(web_events)

        # Discussions for Web Development
        db.query(Discussion).filter_by(community_id=web_comm.id).delete()
        web_discussions = [
            Discussion(
                community_id=web_comm.id,
                author_id=author_id,
                title="Flexbox vs CSS Grid: What are your rules of thumb?",
                content="When do you prefer 1D Flexbox layouts over 2D Grid layouts in modern responsive websites?",
                reply_count=9,
            ),
            Discussion(
                community_id=web_comm.id,
                author_id=author_id,
                title="State management in 2026: React Context vs Zustand",
                content="Sharing experiences comparing lightweight state libraries versus built-in React hooks.",
                reply_count=6,
            ),
            Discussion(
                community_id=web_comm.id,
                author_id=author_id,
                title="FastAPI + PostgreSQL: Best project structures for scaling",
                content="How do you organize your schemas, repositories, and API routers for maintainability?",
                reply_count=4,
            ),
        ]
        db.add_all(web_discussions)
        db.commit()

        # Update community active member counts
        for c in [prog_comm, web_comm]:
            count = db.query(CommunityMembership).filter_by(community_id=c.id, is_active=True).count()
            c.active_members_count = count
        db.commit()

        print("Seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

