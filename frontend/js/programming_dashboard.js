document.addEventListener("DOMContentLoaded", async () => {
    const api = window.skillBridgeApi;
    const token = api.getToken();
    const urlParams = new URLSearchParams(window.location.search);
    const communityId = urlParams.get("id");

    // Hide projects if not part of current backend schema
    document.querySelectorAll('[href="#projects"]').forEach(el => el.remove());
    document.querySelectorAll('#projects').forEach(el => el.remove());

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
    const challengeList = document.querySelector("#challenges .challenge-list");
    const discussionList = document.querySelector("#discussions .discussion-list");
    const membersGrid = document.querySelector("#members .members-grid");
    const eventList = document.querySelector("#events .event-list");

    if (roadmapTimeline) roadmapTimeline.innerHTML = "<p style='color:#64748b; padding:16px;'>Loading roadmap modules...</p>";
    if (resourceList) resourceList.innerHTML = "<p style='color:#64748b; padding:16px;'>Loading resources...</p>";
    if (challengeList) challengeList.innerHTML = "<p style='color:#64748b; padding:16px;'>Loading challenges...</p>";

    async function fetchDashboard() {
        try {
            const response = await api.request(`/api/v1/communities/${communityId}/dashboard`);
            if (response.status === 401) {
                window.location.href = "login.html";
                return null;
            }
            if (response.status === 403) {
                window.location.href = `programming_community_exp.html?id=${communityId}`;
                return null;
            }
            if (!response.ok) throw new Error(`Dashboard request failed: ${response.status}`);

            return await api.parseJson(response);
        } catch (error) {
            console.error("Programming dashboard error:", error);
            setText(".welcome-section p", "Unable to load dashboard data right now.");
            return null;
        }
    }

    const dashboard = await fetchDashboard();
    if (!dashboard) return;

    renderDashboard(dashboard);

    function renderDashboard(data) {
        const progress = data.stats.roadmap_progress_percentage || 0;
        const userName = data.user_name || "Student";
        const initial = userName.charAt(0).toUpperCase();

        // 1. Header & Navigation Profile
        setText(".profile-info strong", userName);
        const profileAvatar = document.querySelector(".profile-avatar");
        if (profileAvatar) profileAvatar.textContent = initial;

        setText(".welcome-section h1", `Welcome back, ${userName}! 👋`);
        setText(".sidebar-community strong", data.community.name);
        setText(".breadcrumb strong", data.community.name);
        setText(".sidebar-community span", `${data.community.active_members_count || 0} Members`);

        // 2. Stats Grid (Preserving all 4 cards dynamically)
        setText(".stat-card:nth-child(1) strong", `${progress}%`);
        setWidth(".stat-card:nth-child(1) .mini-progress > div", progress);
        setText(".stat-card:nth-child(2) strong", `${data.stats.current_streak_days || 0} Days`);
        setText(".stat-card:nth-child(3) strong", `${data.stats.completed_tasks_count || 0} Tasks`);

        const statCard4 = document.querySelector(".stat-card:nth-child(4)");
        if (statCard4) {
            const icon = statCard4.querySelector(".stat-icon i");
            if (icon) icon.className = "fa-solid fa-trophy";
            statCard4.querySelector("span").textContent = "Active Challenges";
            statCard4.querySelector("strong").textContent = `${data.challenges ? data.challenges.length : 0}`;
            const subtext = statCard4.querySelector("small");
            if (subtext) subtext.textContent = "Available now";
        }

        // 3. Sidebar Menu Badges
        const challengeMenuCount = document.querySelector('.sidebar-link[href="#challenges"] .menu-count');
        if (challengeMenuCount) {
            challengeMenuCount.textContent = `${data.challenges ? data.challenges.length : 0}`;
        }

        // 4. Roadmap Section
        setText(".overall-progress strong", `${progress}%`);
        setWidth(".roadmap-progress-fill", progress);

        if (data.roadmap && data.roadmap.modules && data.roadmap.modules.length > 0) {
            setText(".roadmap-title h3", data.roadmap.title);
            setText(
                ".roadmap-title span",
                `${data.roadmap.total_modules} Modules • ${data.roadmap.total_tasks} Tasks`
            );
            renderRoadmap(data.roadmap.modules);
        } else {
            setText(".roadmap-title h3", "Roadmap Coming Soon");
            setText(".roadmap-title span", "Curriculum being prepared");
            if (roadmapTimeline) {
                roadmapTimeline.innerHTML = `
                    <div style="text-align: center; padding: 36px 20px; color: #64748b;">
                        <i class="fa-solid fa-map-location-dot" style="font-size: 32px; color: #94a3b8; margin-bottom: 10px;"></i>
                        <p style="font-weight: 500;">No roadmap modules published yet.</p>
                        <small>Curriculum added from the Admin Panel will appear here automatically.</small>
                    </div>
                `;
            }
        }

        // 5. Challenges
        renderChallenges(data.challenges || []);

        // 6. Resources
        renderResources(data.resources || []);

        // 7. Discussions
        renderDiscussions(data.discussions || []);

        // 8. Announcements
        renderAnnouncements(data.announcements || []);

        // 9. Members & Leaderboard
        renderMembers(data.members || []);

        // 10. Events
        renderEvents(data.events || []);
    }

    // ============================================
    // RENDER ROADMAP TIMELINE
    // ============================================
    function renderRoadmap(modules) {
        if (!roadmapTimeline) return;

        roadmapTimeline.innerHTML = modules.map((module, index) => {
            const statusClass = module.status === "completed"
                ? "completed"
                : module.status === "in_progress" ? "current" : "locked";

            const icon = module.status === "completed"
                ? "fa-check"
                : module.status === "in_progress" ? "fa-play" : "fa-lock";

            const statusLabel = module.status === "in_progress"
                ? "In Progress"
                : module.status[0].toUpperCase() + module.status.slice(1);

            const tasks = (module.tasks || []).map((task) => `
                <span class="${task.is_completed ? "done" : ""}" data-task-id="${task.id}" style="cursor: pointer;" title="Click to toggle completion">
                    <i class="fa-${task.is_completed ? "solid fa-check" : "regular fa-circle"}"></i>
                    ${escapeHtml(task.title)}
                </span>
            `).join("");

            return `
                <div class="roadmap-item ${statusClass}">
                    <div class="timeline-dot"><i class="fa-solid ${icon}"></i></div>
                    <div class="roadmap-item-content">
                        <div class="module-heading">
                            <div>
                                <span class="module-number">MODULE ${String(index + 1).padStart(2, "0")}</span>
                                <h3>${escapeHtml(module.title)}</h3>
                            </div>
                            <span class="module-status ${statusClass}-status">${statusLabel}</span>
                        </div>
                        <p>${escapeHtml(module.description || "")}</p>
                        
                        <div class="module-progress-row" style="margin: 10px 0;">
                            <div class="small-progress" style="background:#e2e8f0; height:6px; border-radius:999px; overflow:hidden; flex:1;">
                                <div style="width: ${module.progress_percentage || 0}%; height:100%; background:#2563eb; transition: width 0.3s ease;"></div>
                            </div>
                            <span style="font-size: 11px; font-weight: 700; color: #64748b; margin-left: 8px;">${module.progress_percentage || 0}%</span>
                        </div>

                        <div class="module-tasks">${tasks || "<small style='color:#94a3b8;'>No tasks listed</small>"}</div>
                    </div>
                </div>
            `;
        }).join("");

        // Attach click handlers to toggle task completion
        roadmapTimeline.querySelectorAll("[data-task-id]").forEach((taskEl) => {
            taskEl.addEventListener("click", async () => {
                const taskId = taskEl.dataset.taskId;
                const isCompleted = taskEl.classList.contains("done");

                try {
                    const res = await api.request(
                        `/api/v1/roadmaps/tasks/${taskId}/progress`,
                        {
                            method: "PUT",
                            body: JSON.stringify({ is_completed: !isCompleted })
                        }
                    );
                    if (res.ok) {
                        // Refresh dashboard to recalculate all module progress & overall stats
                        const updated = await fetchDashboard();
                        if (updated) renderDashboard(updated);
                    }
                } catch (err) {
                    console.error("Task progress update error:", err);
                }
            });
        });
    }

    // ============================================
    // RENDER CHALLENGES
    // ============================================
    function renderChallenges(challenges) {
        if (!challengeList) return;
        if (!challenges.length) {
            challengeList.innerHTML = "<p style='color:#64748b; padding:16px;'>No active challenges right now. Challenges created in the Admin Panel will appear here.</p>";
            return;
        }

        challengeList.innerHTML = challenges.map((challenge) => `
            <div class="challenge-item" data-challenge-id="${challenge.id}">
                <div class="challenge-icon"><i class="fa-solid fa-code"></i></div>
                <div class="challenge-info">
                    <h3>${escapeHtml(challenge.title)}</h3>
                    <span>${escapeHtml(challenge.difficulty)} • ${challenge.xp_reward} XP</span>
                </div>
                <button type="button" class="challenge-action ${challenge.user_status === "completed" ? "done-btn" : ""}" style="border:none; cursor:pointer; font-weight:600; padding:6px 12px; border-radius:6px;">
                    ${challenge.user_status === "completed" ? "Completed ✓" : "Complete"}
                </button>
            </div>
        `).join("");

        challengeList.querySelectorAll("[data-challenge-id]").forEach((item) => {
            const btn = item.querySelector(".challenge-action");
            if (btn && !btn.classList.contains("done-btn")) {
                btn.addEventListener("click", async () => {
                    const res = await api.request(
                        `/api/v1/communities/${communityId}/challenges/${item.dataset.challengeId}/complete`,
                        { method: "POST" }
                    );
                    if (res.ok) {
                        btn.textContent = "Completed ✓";
                        btn.classList.add("done-btn");
                    }
                });
            }
        });
    }

    // ============================================
    // RENDER RESOURCES
    // ============================================
    function renderResources(resources) {
        if (!resourceList) return;
        if (!resources.length) {
            resourceList.innerHTML = "<p style='color:#64748b; padding:16px;'>No resources available yet.</p>";
            return;
        }

        const iconForType = (type) => {
            const t = (type || "").toLowerCase();
            if (t.includes("video")) return { icon: "fa-video", bg: "green-bg" };
            if (t.includes("pdf")) return { icon: "fa-file-pdf", bg: "blue-bg" };
            if (t.includes("article")) return { icon: "fa-newspaper", bg: "purple-bg" };
            return { icon: "fa-link", bg: "blue-bg" };
        };

        resourceList.innerHTML = resources.map((res) => {
            const meta = iconForType(res.resource_type);
            return `
                <div class="resource-item">
                    <div class="resource-icon ${meta.bg}">
                        <i class="fa-solid ${meta.icon}"></i>
                    </div>
                    <div>
                        <h3>${escapeHtml(res.title)}</h3>
                        <span>${escapeHtml(res.resource_type)} • ${escapeHtml(res.difficulty || "All Levels")}</span>
                    </div>
                    <button type="button" aria-label="Open ${escapeHtml(res.title)}" data-resource-url="${escapeHtml(res.url)}">
                        <i class="fa-solid fa-arrow-up-right-from-square"></i>
                    </button>
                </div>
            `;
        }).join("");

        resourceList.querySelectorAll("[data-resource-url]").forEach((button) => {
            button.addEventListener("click", () => {
                window.open(button.dataset.resourceUrl, "_blank", "noopener,noreferrer");
            });
        });
    }

    // ============================================
    // RENDER DISCUSSIONS
    // ============================================
    function renderDiscussions(discussions) {
        if (!discussionList) return;
        if (!discussions.length) {
            discussionList.innerHTML = "<p style='color:#64748b; padding:16px;'>No community discussions yet.</p>";
            return;
        }

        discussionList.innerHTML = discussions.map((d) => `
            <div class="discussion-item">
                <div class="discussion-avatar">${escapeHtml(d.title.charAt(0).toUpperCase())}</div>
                <div class="discussion-info">
                    <h3>${escapeHtml(d.title)}</h3>
                    <span>${d.reply_count} replies • Community Forum</span>
                </div>
            </div>
        `).join("");
    }

    // ============================================
    // RENDER ANNOUNCEMENTS
    // ============================================
    function renderAnnouncements(announcements) {
        const announcementSection = document.querySelector("#announcements");
        if (!announcementSection) return;

        const latest = announcements[0];
        if (latest) {
            announcementSection.querySelector("h3").textContent = latest.title;
            announcementSection.querySelector("p").textContent = latest.content;
            const btn = announcementSection.querySelector(".announcement-btn");
            if (btn) btn.style.display = "flex";
        } else {
            announcementSection.querySelector("h3").textContent = "Welcome to the Community";
            announcementSection.querySelector("p").textContent = "There are no new broadcast announcements at this time.";
            const btn = announcementSection.querySelector(".announcement-btn");
            if (btn) btn.style.display = "none";
        }
    }

    // ============================================
    // RENDER MEMBERS & LEADERBOARD
    // ============================================
    function renderMembers(members) {
        if (membersGrid) {
            if (!members.length) {
                membersGrid.innerHTML = "<p style='color:#64748b; padding:16px;'>No members enrolled yet.</p>";
            } else {
                membersGrid.innerHTML = members.map((m) => `
                    <div class="member-card">
                        <div class="member-avatar">${escapeHtml(m.name.charAt(0).toUpperCase())}</div>
                        <strong>${escapeHtml(m.name)}</strong>
                        <span>${escapeHtml(m.role || "Member")}</span>
                    </div>
                `).join("");
            }
        }

        // Dynamically populate leaderboard with active community members
        const leaderboardList = document.querySelector("#leaderboard .leaderboard-list");
        if (leaderboardList && members.length > 0) {
            const ranks = ["gold", "silver", "bronze"];
            leaderboardList.innerHTML = members.slice(0, 4).map((m, idx) => `
                <div class="leader-row ${idx === 3 ? 'current-user' : ''}">
                    <span class="rank ${ranks[idx] || ''}">${idx + 1}</span>
                    <div class="leader-avatar">${escapeHtml(m.name.charAt(0).toUpperCase())}</div>
                    <div class="leader-name">
                        <strong>${escapeHtml(m.name)}</strong>
                        <span>${(4 - idx) * 450 + 500} XP</span>
                    </div>
                </div>
            `).join("");
        }
    }

    // ============================================
    // RENDER EVENTS
    // ============================================
    function renderEvents(events) {
        if (!eventList) return;
        if (!events.length) {
            eventList.innerHTML = "<p style='color:#64748b; padding:16px;'>No upcoming events scheduled.</p>";
            return;
        }

        eventList.innerHTML = events.map((e) => {
            const date = new Date(e.event_date);
            const day = date.getDate() || "25";
            const month = date.toLocaleString("en", { month: "short" }).toUpperCase();
            const time = date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });

            return `
                <div class="event-item" data-event-id="${e.id}">
                    <div class="event-date">
                        <strong>${day}</strong>
                        <span>${month}</span>
                    </div>
                    <div class="event-info">
                        <h3>${escapeHtml(e.title)}</h3>
                        <p>${escapeHtml(e.description || "")}</p>
                        <span><i class="fa-regular fa-clock"></i> ${time}</span>
                    </div>
                    <button type="button" class="event-action" style="border:none; cursor:pointer; padding:6px 12px; border-radius:6px;">
                        ${e.is_registered ? "Registered ✓" : "Join Event"}
                    </button>
                </div>
            `;
        }).join("");

        eventList.querySelectorAll("[data-event-id]").forEach((item) => {
            const btn = item.querySelector(".event-action");
            if (btn && !btn.textContent.includes("✓")) {
                btn.addEventListener("click", async () => {
                    const res = await api.request(
                        `/api/v1/communities/${communityId}/events/${item.dataset.eventId}/register`,
                        { method: "POST" }
                    );
                    if (res.ok) {
                        btn.textContent = "Registered ✓";
                    }
                });
            }
        });
    }

    // Continue Learning scroll button
    document.querySelector(".continue-btn")?.addEventListener("click", () => {
        document.getElementById("roadmap")?.scrollIntoView({ behavior: "smooth" });
    });

    // Dashboard Logout
    document.getElementById("dashboardLogoutBtn")?.addEventListener("click", (e) => {
        e.preventDefault();
        api.clearSession();
        window.location.href = "login.html";
    });
});
