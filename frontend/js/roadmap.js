document.addEventListener("DOMContentLoaded", async () => {
    const list = document.getElementById("communityList");
    if (!skillBridgeApi.getToken()) {
        window.location.href = "login.html";
        return;
    }
    try {
        const response = await skillBridgeApi.request("/api/v1/communities/my-communities");
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }
        if (!response.ok) throw new Error(`Community request failed: ${response.status}`);
        const communities = await skillBridgeApi.parseJson(response);
        list.innerHTML = "";
        if (!communities.length) {
            list.innerHTML = "<div class=\"no-community\"><h3>No Communities Yet</h3><p>You haven't joined any community yet.</p></div>";
            return;
        }
        communities.forEach((community) => {
            const name = community.name || "Community";
            const lowerName = name.toLowerCase();
            const card = document.createElement("div");
            card.className = "community-card";
            card.innerHTML = `
                <div class="card-top"><div class="community-icon">${lowerName.includes("web") ? "🌐" : "💻"}</div><div class="arrow-icon">→</div></div>
                <div class="card-content">
                    <h3>${name}</h3>
                    <p class="community-card-description">${community.description || "Continue your learning journey with this community."}</p>
                    <div class="community-stats"><div class="stat"><strong>${community.active_members_count || 0}</strong><small>Members</small></div><div class="stat"><strong>${community.challenges_count || 0}</strong><small>Challenges</small></div></div>
                    <button type="button" class="continue-btn">Continue Learning <span>→</span></button>
                </div>`;
            card.querySelector(".continue-btn").addEventListener("click", () => {
                if (lowerName.includes("programming")) {
                    window.location.href = `programming_dashboard.html?id=${community.id}`;
                } else if (lowerName.includes("web")) {
                    window.location.href = `web_development_dashboard.html?id=${community.id}`;
                } else {
                    alert("Dashboard is not available for this community yet.");
                }
            });
            list.appendChild(card);
        });
    } catch (error) {
        console.error("Community loading error:", error);
        list.innerHTML = "<div class=\"no-community\"><h3>Failed to Load Communities</h3><p>Please try again later.</p></div>";
    }
});
