document.addEventListener("DOMContentLoaded", async () => {
    const token = skillBridgeApi.getToken();
    const communityId = new URLSearchParams(window.location.search).get("id");
    document.querySelectorAll('[href="#projects"], [href="#leaderboard"]').forEach((element) => element.remove());
    document.querySelectorAll("#projects, #leaderboard").forEach((element) => element.remove());
    document.querySelectorAll(".stat-card:nth-child(4)").forEach((element) => element.remove());
    if (!token) {
        window.location.href = "login.html";
        return;
    }
    if (!communityId) {
        window.location.href = "community.html";
        return;
    }

    const setText = (selector, value) => {
        const element = document.querySelector(selector);
        if (element) element.textContent = value;
    };
    const setWidth = (selector, value) => {
        const element = document.querySelector(selector);
        if (element) element.style.width = `${value}%`;
    };
    const escapeHtml = (value) => {
        const element = document.createElement("div");
        element.textContent = value ?? "";
        return element.innerHTML;
    };
    const roadmapTimeline = document.querySelector(".roadmap-timeline");
    const resourceList = document.querySelector("#resources .resource-list");
    if (roadmapTimeline) roadmapTimeline.innerHTML = "<p>Loading roadmap...</p>";
    if (resourceList) resourceList.innerHTML = "<p>Loading resources...</p>";

    try {
        const response = await skillBridgeApi.request(
            `/api/v1/communities/${communityId}/dashboard`
        );
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }
        if (response.status === 403) {
            window.location.href =
                `web_development_community_exp.html?id=${communityId}`;
            return;
        }
        if (!response.ok) throw new Error(`Dashboard request failed: ${response.status}`);

        const dashboard = await skillBridgeApi.parseJson(response);
        const progress = dashboard.stats.roadmap_progress_percentage;
        setText(".profile-info strong", dashboard.user_name);
        setText(".welcome-section h1", `Welcome back, ${dashboard.user_name}!`);
        setText(".sidebar-community strong", dashboard.community.name);
        setText(".breadcrumb strong", dashboard.community.name);
        setText(".stat-card:nth-child(1) strong", `${progress}%`);
        setWidth(".stat-card:nth-child(1) .mini-progress > div", progress);
        setText(".stat-card:nth-child(2) strong", `${dashboard.stats.current_streak_days} Days`);
        setText(".stat-card:nth-child(3) strong", `${dashboard.stats.completed_tasks_count} Tasks`);
        setText(".overall-progress strong", `${progress}%`);
        setWidth(".roadmap-progress-fill", progress);
        if (dashboard.roadmap) {
            setText(".roadmap-title h3", dashboard.roadmap.title);
            setText(".roadmap-title span", `${dashboard.roadmap.total_modules} Modules • ${dashboard.roadmap.total_tasks} Tasks`);
            renderRoadmap(dashboard.roadmap.modules);
        } else if (roadmapTimeline) {
            roadmapTimeline.innerHTML = "<p>No roadmap is available yet.</p>";
        }
        renderResources(dashboard.resources || []);
        renderContent(dashboard);
    } catch (error) {
        console.error("Web Development dashboard error:", error);
        setText(".welcome-section p", "Unable to load your dashboard right now.");
    }

    function renderRoadmap(modules) {
        const timeline = document.querySelector(".roadmap-timeline");
        if (!timeline) return;
        timeline.innerHTML = modules.map((module, index) => {
            const statusClass = module.status === "completed" ? "completed" : module.status === "in_progress" ? "current" : "locked";
            const icon = module.status === "completed" ? "fa-check" : module.status === "in_progress" ? "fa-play" : "fa-lock";
            const status = module.status === "in_progress" ? "In Progress" : module.status[0].toUpperCase() + module.status.slice(1);
            const tasks = module.tasks.map((task) => `<span class="${task.is_completed ? "done" : ""}" data-task-id="${task.id}"><i class="fa-${task.is_completed ? "solid fa-check" : "regular fa-circle"}"></i> ${escapeHtml(task.title)}</span>`).join("");
            return `<div class="roadmap-item ${statusClass}"><div class="timeline-dot"><i class="fa-solid ${icon}"></i></div><div class="roadmap-item-content"><div class="module-heading"><div><span class="module-number">MODULE ${String(index + 1).padStart(2, "0")}</span><h3>${escapeHtml(module.title)}</h3></div><span class="module-status ${statusClass}-status">${status}</span></div><p>${escapeHtml(module.description || "")}</p><div class="module-tasks">${tasks}</div></div></div>`;
        }).join("");
        timeline.querySelectorAll("[data-task-id]").forEach((task) => {
            task.addEventListener("click", async () => {
                const completed = task.classList.contains("done");
                const response = await skillBridgeApi.request(`/api/v1/roadmaps/tasks/${task.dataset.taskId}/progress`, { method: "PUT", body: JSON.stringify({ is_completed: !completed }) });
                if (!response.ok) return;
                task.classList.toggle("done", !completed);
                task.querySelector("i").className = !completed ? "fa-solid fa-check" : "fa-regular fa-circle";
                window.location.reload();
            });
        });
    }

    function renderResources(resources) {
        const list = document.querySelector("#resources .resource-list");
        if (!list) return;
        if (!resources.length) {
            list.innerHTML = "<p>No resources are available yet.</p>";
            return;
        }
        list.innerHTML = resources.map((resource) => `
            <div class="resource-item">
                <div class="resource-icon blue-bg">
                    <i class="fa-solid fa-book-open"></i>
                </div>
                <div>
                    <h3>${escapeHtml(resource.title)}</h3>
                    <span>${escapeHtml(resource.resource_type)} • ${escapeHtml(resource.difficulty || "All levels")}</span>
                </div>
                <button type="button" aria-label="Open ${escapeHtml(resource.title)}"
                    data-resource-url="${escapeHtml(resource.url)}">
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </button>
            </div>
        `).join("");
        list.querySelectorAll("[data-resource-url]").forEach((button) => {
            button.addEventListener("click", () => {
                window.open(button.dataset.resourceUrl, "_blank", "noopener,noreferrer");
            });
        });
    }

    function renderContent(dashboard) {
        const challengeList = document.querySelector("#challenges .challenge-list");
        if (challengeList) {
            challengeList.innerHTML = dashboard.challenges.length
                ? dashboard.challenges.map((challenge) => `<div class="challenge-item" data-challenge-id="${challenge.id}"><div class="challenge-icon"><i class="fa-solid fa-code"></i></div><div class="challenge-info"><h3>${escapeHtml(challenge.title)}</h3><span>${escapeHtml(challenge.difficulty)} • ${challenge.xp_reward} XP</span></div><button type="button" class="challenge-action">${challenge.user_status === "completed" ? "Completed" : "Complete"}</button></div>`).join("")
                : "<p>No active challenges right now.</p>";
            challengeList.querySelectorAll("[data-challenge-id]").forEach((item) => {
                item.querySelector(".challenge-action").addEventListener("click", async () => {
                    const response = await skillBridgeApi.request(`/api/v1/communities/${communityId}/challenges/${item.dataset.challengeId}/complete`, { method: "POST" });
                    if (response.ok) item.querySelector(".challenge-action").textContent = "Completed";
                });
            });
        }
        const discussionList = document.querySelector("#discussions .discussion-list");
        if (discussionList) discussionList.innerHTML = dashboard.discussions.length
            ? dashboard.discussions.map((discussion) => `<div class="discussion-item"><div class="discussion-avatar">?</div><div class="discussion-info"><h3>${escapeHtml(discussion.title)}</h3><span>${discussion.reply_count} replies</span></div></div>`).join("")
            : "<p>No discussions yet.</p>";
        const announcement = document.querySelector("#announcements");
        const latestAnnouncement = dashboard.announcements[0];
        if (announcement) {
            announcement.querySelector("h3").textContent = latestAnnouncement?.title || "No announcements yet";
            announcement.querySelector("p").textContent = latestAnnouncement?.content || "There are no new community announcements.";
        }
        const membersGrid = document.querySelector("#members .members-grid");
        if (membersGrid) membersGrid.innerHTML = dashboard.members.length
            ? dashboard.members.map((member) => `<div class="member-card"><div class="member-avatar">${escapeHtml(member.name.charAt(0).toUpperCase())}</div><strong>${escapeHtml(member.name)}</strong><span>${escapeHtml(member.role)}</span></div>`).join("")
            : "<p>No members to display.</p>";
        const eventList = document.querySelector("#events .event-list");
        if (eventList) {
            eventList.innerHTML = dashboard.events.length ? dashboard.events.map((event) => {
                const date = new Date(event.event_date);
                return `<div class="event-item" data-event-id="${event.id}"><div class="event-date"><strong>${date.getDate()}</strong><span>${date.toLocaleString("en", { month: "short" }).toUpperCase()}</span></div><div class="event-info"><h3>${escapeHtml(event.title)}</h3><p>${escapeHtml(event.description || "")}</p><span>${date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</span></div><button type="button" class="event-action">${event.is_registered ? "Registered" : "Join Event"}</button></div>`;
            }).join("") : "<p>No upcoming events.</p>";
            eventList.querySelectorAll("[data-event-id]").forEach((item) => {
                item.querySelector(".event-action").addEventListener("click", async () => {
                    const response = await skillBridgeApi.request(`/api/v1/communities/${communityId}/events/${item.dataset.eventId}/register`, { method: "POST" });
                    if (response.ok) item.querySelector(".event-action").textContent = "Registered";
                });
            });
        }
    }

});
