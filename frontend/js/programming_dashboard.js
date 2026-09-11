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
                // Not authenticated or not a member
                window.location.href = `programming_community_exp.html?id=${communityId}`;
                return;
            }
            throw new Error("Failed to load dashboard data");
        }

        const data = await response.json();

        // Update welcome message
        const welcomeHeading = document.querySelector(".welcome-section h1");
        if (welcomeHeading) {
            welcomeHeading.innerText = `Welcome back, ${data.user_name}! 👋`;
        }

        // Update Stats
        const statCards = document.querySelectorAll(".stat-card");
        if (statCards.length >= 4) {
            // Roadmap Progress
            statCards[0].querySelector("strong").innerText = `${data.stats.roadmap_progress_percentage}%`;
            statCards[0].querySelector(".mini-progress > div").style.width = `${data.stats.roadmap_progress_percentage}%`;
            
            // Current Streak
            statCards[1].querySelector("strong").innerText = `${data.stats.current_streak_days} Days`;
            
            // Completed Tasks
            statCards[2].querySelector("strong").innerText = `${data.stats.completed_tasks_count} Tasks`;
            
            // Community Rank
            statCards[3].querySelector("strong").innerText = `#${data.stats.community_rank}`;
        }

        // Update Roadmap Progress in the roadmap card
        if (data.roadmap) {
            const overallProgressElement = document.querySelector(".overall-progress strong");
            if (overallProgressElement) {
                overallProgressElement.innerText = `${data.stats.roadmap_progress_percentage}%`;
            }
            
            const roadmapProgressFill = document.querySelector(".roadmap-progress-fill");
            if (roadmapProgressFill) {
                roadmapProgressFill.style.width = `${data.stats.roadmap_progress_percentage}%`;
            }

            // Note: Dynamically generating the entire roadmap timeline can be complex.
            // For now, we update the stats. In a full implementation, you'd iterate 
            // over data.roadmap.modules and data.roadmap.modules[i].tasks to create
            // the DOM elements in .roadmap-timeline.
        }

    } catch (error) {
        console.error("Dashboard fetch error:", error);
    }
});
