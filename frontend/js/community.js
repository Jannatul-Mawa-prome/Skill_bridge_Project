document.addEventListener("DOMContentLoaded", async () => {
    const list = document.getElementById("communityList");
    if (!skillBridgeApi.getToken()) {
        window.location.href = "login.html";
        return;
    }
    list.innerHTML = "<p>Loading communities...</p>";
    try {
        const [communitiesResponse, membershipsResponse] = await Promise.all([
            skillBridgeApi.request("/api/v1/communities"),
            skillBridgeApi.request("/api/v1/communities/my-communities")
        ]);

        if (communitiesResponse.status === 401 || membershipsResponse.status === 401) {
            window.location.href = "login.html";
            return;
        }
        if (!communitiesResponse.ok) {
            throw new Error(`Community request failed: ${communitiesResponse.status}`);
        }
        if (!membershipsResponse.ok) {
            throw new Error(`Membership request failed: ${membershipsResponse.status}`);
        }

        const communities = await skillBridgeApi.parseJson(communitiesResponse);
        const joinedCommunities = await skillBridgeApi.parseJson(membershipsResponse);
        const joinedIds = new Set(joinedCommunities.map((community) => community.id));

        list.innerHTML = communities.map((community) => {
            const joined = joinedIds.has(community.id);
            const name = escapeHtml(community.name);
            const description = escapeHtml(
                community.description || "Continue your learning journey with this community."
            );
            const topics = (community.topics || [])
                .map((topic) => `<span>${escapeHtml(topic)}</span>`)
                .join("");
            const destination = joined
                ? dashboardFor(community)
                : joinPageFor(community);
            const buttonLabel = joined ? "Your Dashboard" : "Explore Community";
            const icon = community.name.toLowerCase().includes("web")
                ? "fa-globe"
                : "fa-code";
            const cardClass = community.name.toLowerCase().includes("web")
                ? "web-card"
                : "programming-card";
            const iconClass = community.name.toLowerCase().includes("web")
                ? "web-icon"
                : "programming-icon";

            return `
                <div class="community-card ${cardClass}">
                    <div class="card-top">
                        <div class="community-icon ${iconClass}">
                            <i class="fa-solid ${icon}"></i>
                        </div>
                        <span class="community-status">
                            <i class="fa-solid fa-circle"></i>
                            Active
                        </span>
                    </div>
                    <div class="card-content">
                        <h3>${name}</h3>
                        <p>${description}</p>
                        <div class="topics">${topics}</div>
                        <div class="community-stats">
                            <div class="stat">
                                <i class="fa-solid fa-users"></i>
                                <div>
                                    <strong>${community.active_members_count || 0}</strong>
                                    <small>Members</small>
                                </div>
                            </div>
                            <div class="stat">
                                <i class="fa-solid fa-trophy"></i>
                                <div>
                                    <strong>${community.challenges_count || 0}</strong>
                                    <small>Challenges</small>
                                </div>
                            </div>
                        </div>
                        <a href="${destination}" class="explore-btn">
                            ${buttonLabel}
                            <i class="fa-solid fa-arrow-right"></i>
                        </a>
                    </div>
                </div>
            `;
        }).join("");
    } catch (error) {
        console.error("Community loading error:", error);
        list.innerHTML = "<p>Unable to load communities.</p>";
    }
});

function dashboardFor(community) {
    const name = community.name.toLowerCase();
    if (name.includes("programming")) {
        return `programming_dashboard.html?id=${community.id}`;
    }
    if (name.includes("web")) {
        return `web_development_dashboard.html?id=${community.id}`;
    }
    return `roadmap.html?id=${community.id}`;
}

function joinPageFor(community) {
    const name = community.name.toLowerCase();
    if (name.includes("programming")) {
        return `programming_community_exp.html?id=${community.id}`;
    }
    if (name.includes("web")) {
        return `web_development_community_exp.html?id=${community.id}`;
    }
    return `community_details.html?id=${community.id}`;
}

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value;
    return element.innerHTML;
}
