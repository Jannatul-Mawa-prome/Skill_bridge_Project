document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const communityId = params.get("community_id") || params.get("id");

    if (!communityId) {
        alert("Community ID missing.");
        window.location.href = "community.html";
        return;
    }

    try {
        const response = await fetch(
            `http://127.0.0.1:8000/api/v1/communities/${communityId}/dashboard`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                alert("You are not authorized to view this dashboard.");
                window.location.href = `web_development_community_exp.html?id=${communityId}`;
                return;
            }
            throw new Error("Failed to load dashboard data");
        }

        const dashboard = await response.json();

        const welcomeTitle = document.querySelector(".welcome-section h1");
        if (welcomeTitle && dashboard.user_name) {
            welcomeTitle.innerHTML = `Welcome back, ${dashboard.user_name}! 👋`;
        }

        const profileStrong = document.querySelector(".profile-info strong");
        if (profileStrong && dashboard.user_name) {
            profileStrong.textContent = dashboard.user_name;
        }

        const breadcrumbStrong = document.querySelector(".breadcrumb strong");
        if (breadcrumbStrong && dashboard.community_name) {
            breadcrumbStrong.textContent = dashboard.community_name;
        }

        const sidebarStrong = document.querySelector(".sidebar-community strong");
        if (sidebarStrong && dashboard.community_name) {
            sidebarStrong.textContent = dashboard.community_name;
        }

        if (dashboard.stats) {
            const progress = dashboard.stats.roadmap_progress_percentage || 0;

            const progressText = document.querySelector(".overall-progress strong");
            if (progressText) progressText.textContent = `${progress}%`;

            const progressBar = document.querySelector(".roadmap-progress-fill");
            if (progressBar) progressBar.style.width = `${progress}%`;

            const statCards = document.querySelectorAll(".stat-card");
            if (statCards.length >= 4) {
                statCards[0].querySelector("strong").textContent = `${progress}%`;
                statCards[0].querySelector(".mini-progress > div").style.width = `${progress}%`;
                statCards[1].querySelector("strong").textContent = `${dashboard.stats.current_streak_days} Days`;
                statCards[2].querySelector("strong").textContent = `${dashboard.stats.completed_tasks_count} Tasks`;
                statCards[3].querySelector("strong").textContent = `#${dashboard.stats.community_rank}`;
            }
        }

        if (dashboard.roadmap) {
            const roadmapTitle = document.querySelector(".roadmap-title h3");
            if (roadmapTitle) roadmapTitle.textContent = dashboard.roadmap.title;

            const roadmapMeta = document.querySelector(".roadmap-title span");
            if (roadmapMeta) {
                roadmapMeta.textContent = `${dashboard.roadmap.total_modules} Modules • ${dashboard.roadmap.total_tasks} Tasks`;
            }

            const roadmapTimeline = document.querySelector(".roadmap-timeline");
            if (roadmapTimeline && dashboard.roadmap.modules) {
                roadmapTimeline.innerHTML = dashboard.roadmap.modules.map((module, index) => {
                    const isCompleted = module.status === "completed";
                    const isCurrent = module.status === "in_progress";
                    const itemClass = isCompleted ? "completed" : isCurrent ? "current" : "locked";
                    const icon = isCompleted ? "fa-check" : isCurrent ? "fa-play" : "fa-lock";
                    const statusLabel = isCompleted ? "Completed" : isCurrent ? "In Progress" : "Locked";
                    const statusClass = isCompleted ? "completed-status" : isCurrent ? "current-status" : "locked-status";

                    const taskHtml = (module.tasks || []).map(task => {
                        const doneClass = task.is_completed ? "done" : "";
                        const iconClass = task.is_completed ? "fa-solid fa-check" : "fa-regular fa-circle";
                        return `
                            <span class="${doneClass}">
                                <i class="${iconClass}"></i>
                                ${task.title}
                            </span>
                        `;
                    }).join("");

                    const progressBlock = isCurrent ? `
                        <div class="module-progress-row">
                            <div class="small-progress">
                                <div style="width: ${module.progress_percentage}%"></div>
                            </div>
                            <span>${module.progress_percentage}%</span>
                        </div>
                    ` : "";

                    const action = isCurrent ? `
                        <button class="module-btn">
                            Continue Module
                            <i class="fa-solid fa-arrow-right"></i>
                        </button>
                    ` : "";

                    return `
                        <div class="roadmap-item ${itemClass}">
                            <div class="timeline-dot">
                                <i class="fa-solid ${icon}"></i>
                            </div>
                            <div class="roadmap-item-content">
                                <div class="module-heading">
                                    <div>
                                        <span class="module-number">MODULE ${String(index + 1).padStart(2, "0")}</span>
                                        <h3>${module.title}</h3>
                                    </div>
                                    <span class="module-status ${statusClass}">${statusLabel}</span>
                                </div>
                                <p>${module.description || "Continue your learning path."}</p>
                                ${progressBlock}
                                <div class="module-tasks">${taskHtml}</div>
                                ${action}
                            </div>
                        </div>
                    `;
                }).join("");
            }
        }

        const resourceList = document.querySelector(".resource-list");
        if (resourceList) {
            resourceList.innerHTML = (dashboard.resources || []).map(resource => {
                const badgeClass = resource.resource_type === "PDF" ? "blue-bg" : resource.resource_type === "Video" ? "green-bg" : "purple-bg";
                const icon = resource.resource_type === "PDF" ? "fa-file-code" : resource.resource_type === "Video" ? "fa-video" : "fa-link";
                return `
                    <div class="resource-item">
                        <div class="resource-icon ${badgeClass}">
                            <i class="fa-solid ${icon}"></i>
                        </div>
                        <div>
                            <h3>${resource.title}</h3>
                            <span>${resource.resource_type} • ${resource.difficulty || "General"}</span>
                        </div>
                        <a href="${resource.url}" target="_blank" rel="noopener noreferrer" aria-label="Open resource">
                            <button type="button">
                                <i class="fa-solid fa-arrow-up-right-from-square"></i>
                            </button>
                        </a>
                    </div>
                `;
            }).join("") || '<div class="resource-item"><div><h3>No resources available</h3><span>Check back later.</span></div></div>';
        }

        const announcementCard = document.querySelector(".announcement-card");
        if (announcementCard && dashboard.announcements && dashboard.announcements.length > 0) {
            const announcement = dashboard.announcements[0];
            const titleEl = announcementCard.querySelector(".announcement-content h3");
            const bodyEl = announcementCard.querySelector(".announcement-content p");
            if (titleEl) titleEl.textContent = announcement.title;
            if (bodyEl) bodyEl.textContent = announcement.content;
        }

    } catch (error) {
        console.error("Dashboard error:", error);
        alert("Server error. Please try again.");
    }
});
