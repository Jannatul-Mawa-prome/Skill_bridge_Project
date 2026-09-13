document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const communityId = urlParams.get('community_id') || urlParams.get('id');

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/communities/${communityId}/dashboard`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                window.location.href = `programming_community_exp.html?id=${communityId}`;
                return;
            }
            throw new Error("Failed to load dashboard data");
        }

        const data = await response.json();

        const welcomeHeading = document.querySelector(".welcome-section h1");
        if (welcomeHeading) {
            welcomeHeading.innerText = `Welcome back, ${data.user_name}! 👋`;
        }

        const breadcrumbStrong = document.querySelector(".breadcrumb strong");
        if (breadcrumbStrong) {
            breadcrumbStrong.innerText = data.community_name || "Programming";
        }

        const sidebarCommunityStrong = document.querySelector(".sidebar-community strong");
        if (sidebarCommunityStrong) {
            sidebarCommunityStrong.innerText = data.community_name || "Programming";
        }

        const statCards = document.querySelectorAll(".stat-card");
        if (statCards.length >= 4) {
            statCards[0].querySelector("strong").innerText = `${data.stats.roadmap_progress_percentage}%`;
            statCards[0].querySelector(".mini-progress > div").style.width = `${data.stats.roadmap_progress_percentage}%`;

            statCards[1].querySelector("strong").innerText = `${data.stats.current_streak_days} Days`;
            statCards[2].querySelector("strong").innerText = `${data.stats.completed_tasks_count} Tasks`;
            statCards[3].querySelector("strong").innerText = `#${data.stats.community_rank}`;
        }

        const roadmapTitle = document.querySelector(".roadmap-title h3");
        if (roadmapTitle && data.roadmap) {
            roadmapTitle.innerText = data.roadmap.title;
        }

        const roadmapMeta = document.querySelector(".roadmap-title span");
        if (roadmapMeta && data.roadmap) {
            roadmapMeta.innerText = `${data.roadmap.total_modules} Modules • ${data.roadmap.total_tasks} Tasks`;
        }

        const overallProgress = document.querySelector(".overall-progress strong");
        if (overallProgress) {
            overallProgress.innerText = `${data.stats.roadmap_progress_percentage}%`;
        }

        const roadmapProgressFill = document.querySelector(".roadmap-progress-fill");
        if (roadmapProgressFill) {
            roadmapProgressFill.style.width = `${data.stats.roadmap_progress_percentage}%`;
        }

        const roadmapTimeline = document.querySelector(".roadmap-timeline");
        if (roadmapTimeline && data.roadmap && data.roadmap.modules) {
            roadmapTimeline.innerHTML = data.roadmap.modules.map((module, moduleIndex) => {
                const isCompleted = module.status === "completed";
                const isCurrent = module.status === "in_progress";
                const itemClass = isCompleted ? "completed" : isCurrent ? "current" : "locked";
                const icon = isCompleted ? "fa-check" : isCurrent ? "fa-play" : "fa-lock";
                const statusLabel = isCompleted ? "Completed" : isCurrent ? "In Progress" : "Locked";
                const taskItems = module.tasks.map(task => {
                    const doneClass = task.is_completed ? "done" : "";
                    const iconClass = task.is_completed ? "fa-solid fa-check" : "fa-regular fa-circle";
                    return `
                        <span class="${doneClass}">
                            <i class="${iconClass}"></i>
                            ${task.title}
                        </span>
                    `;
                }).join("");

                const progressRow = isCurrent ? `
                    <div class="module-progress-row">
                        <div class="small-progress">
                            <div style="width: ${module.progress_percentage}%"></div>
                        </div>
                        <span>${module.progress_percentage}%</span>
                    </div>
                ` : "";

                const actionButton = isCurrent ? `
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
                                    <span class="module-number">MODULE ${String(moduleIndex + 1).padStart(2, '0')}</span>
                                    <h3>${module.title}</h3>
                                </div>
                                <span class="module-status ${isCompleted ? 'completed-status' : isCurrent ? 'current-status' : 'locked-status'}">${statusLabel}</span>
                            </div>
                            <p>${module.description || 'Continue your learning path.'}</p>
                            ${progressRow}
                            <div class="module-tasks">${taskItems}</div>
                            ${actionButton}
                        </div>
                    </div>
                `;
            }).join("");
        }

        const resourceList = document.querySelector(".resource-list");
        if (resourceList) {
            resourceList.innerHTML = (data.resources || []).map(resource => {
                const badgeClass = resource.resource_type === "PDF" ? "blue-bg" : resource.resource_type === "Video" ? "green-bg" : "purple-bg";
                const icon = resource.resource_type === "PDF" ? "fa-file-code" : resource.resource_type === "Video" ? "fa-video" : "fa-link";
                return `
                    <div class="resource-item">
                        <div class="resource-icon ${badgeClass}">
                            <i class="fa-solid ${icon}"></i>
                        </div>
                        <div>
                            <h3>${resource.title}</h3>
                            <span>${resource.resource_type} • ${resource.difficulty || 'General'}</span>
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
        if (announcementCard && data.announcements && data.announcements.length > 0) {
            const announcement = data.announcements[0];
            const titleEl = announcementCard.querySelector(".announcement-content h3");
            const bodyEl = announcementCard.querySelector(".announcement-content p");
            if (titleEl) titleEl.innerText = announcement.title;
            if (bodyEl) bodyEl.innerText = announcement.content;
        }

    } catch (error) {
        console.error("Dashboard fetch error:", error);
    }
});
