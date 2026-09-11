document.addEventListener("DOMContentLoaded", () => {
    const api = window.skillBridgeApi;
    if (!api.getToken()) {
        window.location.href = "login.html";
        return;
    }
    const feedback = document.getElementById("feedback");
    const setFeedback = (message, error = false) => {
        feedback.textContent = message;
        feedback.style.color = error ? "#991b1b" : "#166534";
    };
    const escape = (value) => {
        const node = document.createElement("div");
        node.textContent = value ?? "";
        return node.innerHTML;
    };
    const request = async (path, options) => {
        const response = await api.request(`/api/v1/admin${path}`, options);
        if (response.status === 401) return window.location.href = "login.html";
        if (response.status === 403) throw new Error("Administrator access is required.");
        if (!response.ok) throw new Error(`Request failed (${response.status})`);
        return response.status === 204 ? null : api.parseJson(response);
    };
    const action = (label, path, method, id) =>
        `<button class="action ${method === "DELETE" ? "danger" : ""}" data-method="${method}" data-path="${path}" data-id="${id}">${label}</button>`;

    async function load() {
        try {
            document.getElementById("adminStatus").textContent = "Administrator";
            const [overview, users, communities, memberships, roadmaps, resources, announcements] =
                await Promise.all(["/overview", "/users", "/communities", "/memberships", "/roadmaps", "/resources", "/announcements"].map((path) => request(path)));
            renderStats(overview);
            renderUsers(users);
            renderCommunities(communities);
            renderMemberships(memberships);
            renderRoadmaps(roadmaps);
            renderResources(resources);
            renderAnnouncements(announcements);
        } catch (error) {
            document.getElementById("adminStatus").textContent = "Access denied";
            setFeedback(error.message, true);
        }
    }
    function renderStats(data) {
        const labels = { users:"Users", active_users:"Active users", communities:"Communities", memberships:"Memberships", roadmaps:"Roadmaps", modules:"Modules", tasks:"Tasks", resources:"Resources", announcements:"Announcements" };
        document.getElementById("statsGrid").innerHTML = Object.entries(labels).map(([key,label]) => `<div class="stat"><span>${label}</span><strong>${data[key] ?? 0}</strong></div>`).join("");
    }
    function renderUsers(items) {
        document.getElementById("usersTable").innerHTML = items.map((user) => `<tr><td>${escape(user.profile?.full_name || user.edu_email)}<br><small>${escape(user.edu_email)}</small></td><td>${escape(user.profile?.department || "—")}</td><td>${user.is_active ? "Active" : "Disabled"}</td><td>${user.is_admin ? "Yes" : "No"}</td><td>${action(user.is_active ? "Disable" : "Enable", `/users/${user.id}/status`, "PATCH", user.id)}</td></tr>`).join("");
    }
    function renderCommunities(items) {
        document.getElementById("communitiesTable").innerHTML = items.map((item) => `<tr><td><strong>${escape(item.name)}</strong><br><small>${escape(item.description || "")}</small></td><td>${item.active_members_count}</td><td>${item.is_active ? "Active" : "Disabled"}</td><td>${action(item.is_active ? "Disable" : "Enable", `/communities/${item.id}/status`, "PATCH", item.id)}</td></tr>`).join("");
    }
    function renderMemberships(items) {
        document.getElementById("membershipsTable").innerHTML = items.map((item) => `<tr><td>${item.id}</td><td>${item.user_id}</td><td>${item.community_id}</td><td>${escape(item.role)}</td><td>${item.is_active ? "Active" : "Inactive"}</td><td>${action(item.is_active ? "Remove" : "Activate", `/memberships/${item.id}/status`, "PATCH", item.id)}</td></tr>`).join("");
    }
    function renderRoadmaps(items) {
        document.getElementById("roadmapsTable").innerHTML = items.map((item) => `<tr><td>${escape(item.title)}</td><td>${item.community_id}</td><td>${item.total_modules}</td><td>${action("Delete", `/roadmaps/${item.id}`, "DELETE", item.id)}</td></tr>`).join("");
    }
    function renderResources(items) {
        document.getElementById("resourcesTable").innerHTML = items.map((item) => `<tr><td>${escape(item.title)}</td><td>${escape(item.resource_type)}</td><td>${escape(item.difficulty || "—")}</td><td>${action("Delete", `/resources/${item.id}`, "DELETE", item.id)}</td></tr>`).join("");
    }
    function renderAnnouncements(items) {
        document.getElementById("announcementsTable").innerHTML = items.map((item) => `<tr><td>${escape(item.title)}</td><td>${item.community_id}</td><td>${new Date(item.created_at).toLocaleDateString()}</td><td>${action("Delete", `/announcements/${item.id}`, "DELETE", item.id)}</td></tr>`).join("");
    }
    document.addEventListener("click", async (event) => {
        const button = event.target.closest("[data-method]");
        if (!button) return;
        if (!confirm("Apply this administrative change?")) return;
        try {
            const body = button.dataset.method === "DELETE" ? undefined : JSON.stringify({ is_active: button.textContent.includes("Enable") });
            await request(button.dataset.path, { method: button.dataset.method, body });
            setFeedback("Change saved.");
            await load();
        } catch (error) { setFeedback(error.message, true); }
    });
    document.getElementById("userSearch").addEventListener("input", async (event) => {
        try { renderUsers(await request(`/users?search=${encodeURIComponent(event.target.value)}`)); } catch (error) { setFeedback(error.message, true); }
    });
    document.querySelectorAll("[data-refresh]").forEach((button) => button.addEventListener("click", load));
    document.getElementById("logoutButton").addEventListener("click", () => { api.clearSession(); window.location.href = "login.html"; });
    load();
});
