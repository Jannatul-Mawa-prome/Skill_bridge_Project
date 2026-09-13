document.addEventListener("DOMContentLoaded", () => {
    const api = window.skillBridgeApi;

    if (!api.getToken()) {
        window.location.href = "login.html";
        return;
    }

    const feedback = document.getElementById("feedback");
    const setFeedback = (message, error = false) => {
        feedback.textContent = message;
        feedback.className = `feedback show ${error ? "error" : "success"}`;
        setTimeout(() => {
            feedback.className = "feedback";
        }, 5000);
    };

    const escapeHtml = (value) => {
        const node = document.createElement("div");
        node.textContent = value ?? "";
        return node.innerHTML;
    };

    const request = async (path, options = {}) => {
        const response = await api.request(`/api/v1/admin${path}`, options);
        if (response.status === 401) {
            window.location.href = "login.html";
            return null;
        }
        if (response.status === 403) {
            document.getElementById("adminStatus").textContent = "Access denied";
            document.getElementById("adminStatus").className = "status error";
            throw new Error("Administrator privileges are required to view this panel.");
        }
        if (!response.ok) {
            let errorMsg = `Request failed (${response.status})`;
            try {
                const errData = await api.parseJson(response);
                if (errData && errData.detail) errorMsg = errData.detail;
            } catch (_) {}
            throw new Error(errorMsg);
        }
        return response.status === 204 ? null : api.parseJson(response);
    };

    let loadedCommunities = [];
    let activeRoadmapForManagement = null;

    // ============================================
    // LOAD ALL DATA
    // ============================================
    async function loadAll() {
        try {
            document.getElementById("adminStatus").textContent = "Administrator Verified";
            document.getElementById("adminStatus").className = "status";

            const [
                overview,
                users,
                communities,
                joinRequests,
                roadmaps,
                resources,
                announcements,
                challenges,
                events,
                memberships
            ] = await Promise.all([
                request("/overview"),
                request("/users"),
                request("/communities"),
                request("/join-requests"),
                request("/roadmaps"),
                request("/resources"),
                request("/announcements"),
                request("/challenges"),
                request("/events"),
                request("/memberships")
            ]);

            loadedCommunities = communities || [];
            populateCommunitySelects(loadedCommunities);

            renderStats(overview || {});
            renderCommunities(communities || []);
            renderJoinRequests(joinRequests || []);
            renderRoadmaps(roadmaps || []);
            renderResources(resources || []);
            renderAnnouncements(announcements || []);
            renderChallenges(challenges || []);
            renderEvents(events || []);
            renderMemberships(memberships || []);
            renderUsers(users || []);
        } catch (error) {
            setFeedback(error.message, true);
        }
    }

    function populateCommunitySelects(communities) {
        const selects = [
            document.getElementById("roadmapCommunitySelect"),
            document.getElementById("resourceCommunitySelect"),
            document.getElementById("announcementCommunitySelect"),
            document.getElementById("challengeCommunitySelect"),
            document.getElementById("eventCommunitySelect")
        ];

        const optionsHtml = communities.map(c => 
            `<option value="${c.id}">${escapeHtml(c.name)}</option>`
        ).join("");

        selects.forEach(select => {
            if (select) {
                select.innerHTML = optionsHtml || '<option value="">No communities available</option>';
            }
        });
    }

    // ============================================
    // RENDER METRICS & OVERVIEW
    // ============================================
    function renderStats(data) {
        const labels = {
            users: "Total Users",
            active_users: "Active Users",
            communities: "Communities",
            pending_join_requests: "Pending Approvals",
            roadmaps: "Roadmaps",
            modules: "Modules",
            tasks: "Tasks",
            challenges: "Challenges",
            resources: "Resources",
            events: "Upcoming Events",
            announcements: "Announcements"
        };

        const grid = document.getElementById("statsGrid");
        if (grid) {
            grid.innerHTML = Object.entries(labels).map(([key, label]) => `
                <div class="stat">
                    <span>${label}</span>
                    <strong>${data[key] ?? 0}</strong>
                </div>
            `).join("");
        }

        const badge = document.getElementById("pendingRequestsBadge");
        if (badge) {
            const count = data.pending_join_requests || 0;
            badge.textContent = count;
            badge.style.display = count > 0 ? "inline-block" : "none";
        }
    }

    // ============================================
    // RENDER COMMUNITIES
    // ============================================
    function renderCommunities(items) {
        const tbody = document.getElementById("communitiesTable");
        if (!tbody) return;
        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--text-muted);">No communities found.</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(c => `
            <tr>
                <td>
                    <strong>${escapeHtml(c.name)}</strong>
                    <br><small style="color: var(--text-muted);">${escapeHtml(c.description || "No description provided.")}</small>
                </td>
                <td><strong>${c.active_members_count}</strong> members</td>
                <td>
                    <span class="badge ${c.is_active ? 'badge-success' : 'badge-danger'}">
                        ${c.is_active ? 'Active' : 'Disabled'}
                    </span>
                </td>
                <td>
                    <div style="display: flex; gap: 6px;">
                        <button class="btn btn-secondary action" data-edit-community="${c.id}" data-name="${escapeHtml(c.name)}" data-desc="${escapeHtml(c.description || '')}">
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                        <button class="action ${c.is_active ? 'danger' : 'success'}" data-toggle-community-status="${c.id}" data-status="${c.is_active}">
                            ${c.is_active ? 'Disable' : 'Enable'}
                        </button>
                    </div>
                </td>
            </tr>
        `).join("");
    }

    // ============================================
    // RENDER JOIN REQUESTS
    // ============================================
    function renderJoinRequests(items) {
        const tbody = document.getElementById("joinRequestsTable");
        if (!tbody) return;
        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: var(--text-muted); padding: 24px;">No pending join requests at this time.</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(req => {
            const answersHtml = (req.answers || []).map(a => {
                let ans = a.answer;
                if (Array.isArray(ans)) ans = ans.join(", ");
                return `<div><strong>${escapeHtml(a.question_key)}:</strong> ${escapeHtml(String(ans))}</div>`;
            }).join("") || "<small style='color: var(--text-muted);'>No answers provided</small>";

            const student = escapeHtml(req.student_name || "Applicant");
            const email = escapeHtml(req.student_email);
            const roll = escapeHtml(req.student_roll || "—");
            const dept = escapeHtml(req.department || req.semester || "—");
            const dateStr = new Date(req.joined_at).toLocaleString();

            return `
                <tr>
                    <td>
                        <strong>${student}</strong>
                        <br><small style="color: var(--text-muted);">${email}</small>
                    </td>
                    <td>
                        <strong>Roll:</strong> ${roll}
                        <br><small>${dept}</small>
                    </td>
                    <td><span class="badge badge-info">${escapeHtml(req.community_name)}</span></td>
                    <td style="max-width: 320px; font-size: 12.5px;">${answersHtml}</td>
                    <td><small>${dateStr}</small></td>
                    <td>
                        <div style="display:flex; gap:6px;">
                            <button class="btn btn-primary action" data-approve-request="${req.membership_id}">
                                <i class="fa-solid fa-check"></i> Approve
                            </button>
                            <button class="action danger" data-reject-request="${req.membership_id}">
                                <i class="fa-solid fa-xmark"></i> Reject
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("");
    }

    // ============================================
    // RENDER ROADMAPS
    // ============================================
    function renderRoadmaps(items) {
        const tbody = document.getElementById("roadmapsTable");
        if (!tbody) return;
        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--text-muted);">No roadmaps created yet.</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(r => {
            const comm = loadedCommunities.find(c => c.id === r.community_id);
            const commName = comm ? comm.name : `Community #${r.community_id}`;

            return `
                <tr>
                    <td>
                        <strong>${escapeHtml(r.title)}</strong>
                        <br><small style="color: var(--text-muted);">${escapeHtml(r.description || '')}</small>
                    </td>
                    <td><span class="badge badge-info">${escapeHtml(commName)}</span></td>
                    <td><strong>${r.total_modules}</strong> Modules</td>
                    <td>
                        <div style="display: flex; gap: 6px;">
                            <button class="btn btn-secondary action" data-manage-roadmap="${r.id}" data-title="${escapeHtml(r.title)}">
                                <i class="fa-solid fa-list-check"></i> Modules & Tasks
                            </button>
                            <button class="action danger" data-delete-roadmap="${r.id}">
                                <i class="fa-solid fa-trash"></i> Delete
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("");
    }

    // ============================================
    // ROADMAP MODULES & TASKS MANAGEMENT
    // ============================================
    async function openManageRoadmap(roadmapId, title) {
        activeRoadmapForManagement = roadmapId;
        document.getElementById("manageModulesTitle").textContent = `Curriculum: ${title}`;
        document.getElementById("manageModulesModal").classList.add("active");
        document.getElementById("addModuleForm").style.display = "none";
        document.getElementById("addTaskForm").style.display = "none";
        await loadRoadmapTree(roadmapId);
    }

    async function loadRoadmapTree(roadmapId) {
        const tree = document.getElementById("roadmapModulesTree");
        tree.innerHTML = "<p style='color: var(--text-muted);'>Loading curriculum modules and tasks...</p>";

        try {
            const modules = await request(`/roadmaps/${roadmapId}/modules`) || [];
            if (!modules.length) {
                tree.innerHTML = `
                    <div style="text-align:center; padding: 24px; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1;">
                        <p style="color: var(--text-muted); margin-bottom: 8px;">No modules defined for this roadmap yet.</p>
                        <small>Click "Add Module" above to start building the curriculum.</small>
                    </div>
                `;
                return;
            }

            // Fetch tasks for each module concurrently
            const modulesWithTasks = await Promise.all(modules.map(async (m) => {
                const tasks = await request(`/modules/${m.id}/tasks`) || [];
                return { ...m, tasks };
            }));

            // Sort modules by order
            modulesWithTasks.sort((a, b) => a.order - b.order);

            tree.innerHTML = modulesWithTasks.map((mod, idx) => {
                const sortedTasks = (mod.tasks || []).sort((a, b) => a.order - b.order);
                const tasksHtml = sortedTasks.map(t => `
                    <div class="task-row">
                        <span><strong>#${t.order}</strong> ${escapeHtml(t.title)}</span>
                        <button class="action danger" data-delete-task="${t.id}" style="padding: 2px 7px; font-size: 11px;">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                `).join("") || "<small style='color: var(--text-muted); padding: 4px 0;'>No tasks in this module yet.</small>";

                return `
                    <div class="module-card">
                        <div class="module-header">
                            <div>
                                <span class="badge badge-info" style="margin-right: 6px;">Module ${String(idx + 1).padStart(2, '0')}</span>
                                <span class="module-title">${escapeHtml(mod.title)}</span>
                                <small style="display:block; color: var(--text-muted); margin-top: 2px;">${escapeHtml(mod.description || '')}</small>
                            </div>
                            <div style="display: flex; gap: 6px;">
                                <button class="btn btn-secondary action" data-open-add-task="${mod.id}" data-mod-title="${escapeHtml(mod.title)}">
                                    <i class="fa-solid fa-plus"></i> Task
                                </button>
                                <button class="action danger" data-delete-module="${mod.id}">
                                    <i class="fa-solid fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="task-list">
                            ${tasksHtml}
                        </div>
                    </div>
                `;
            }).join("");
        } catch (err) {
            tree.innerHTML = `<p style="color: var(--danger);">Failed to load modules: ${escapeHtml(err.message)}</p>`;
        }
    }

    // ============================================
    // RENDER RESOURCES
    // ============================================
    function renderResources(items) {
        const tbody = document.getElementById("resourcesTable");
        if (!tbody) return;
        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: var(--text-muted);">No resources added yet.</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(r => {
            const comm = loadedCommunities.find(c => c.id === r.community_id);
            const commName = comm ? comm.name : `#${r.community_id}`;
            return `
                <tr>
                    <td>
                        <strong>${escapeHtml(r.title)}</strong>
                        <br><small style="color: var(--text-muted);">${escapeHtml(r.description || '')}</small>
                    </td>
                    <td><span class="badge badge-info">${escapeHtml(commName)}</span></td>
                    <td><span class="badge">${escapeHtml(r.resource_type)}</span></td>
                    <td>${escapeHtml(r.difficulty || 'All Levels')}</td>
                    <td>
                        <a href="${escapeHtml(r.url)}" target="_blank" rel="noopener noreferrer" style="color: var(--primary); text-decoration: none; font-size: 13px;">
                            Link <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 10px;"></i>
                        </a>
                    </td>
                    <td>
                        <button class="action danger" data-delete-resource="${r.id}">
                            <i class="fa-solid fa-trash"></i> Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join("");
    }

    // ============================================
    // RENDER ANNOUNCEMENTS
    // ============================================
    function renderAnnouncements(items) {
        const tbody = document.getElementById("announcementsTable");
        if (!tbody) return;
        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--text-muted);">No announcements published yet.</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(a => {
            const comm = loadedCommunities.find(c => c.id === a.community_id);
            const commName = comm ? comm.name : `#${a.community_id}`;
            const dateStr = new Date(a.created_at).toLocaleDateString();

            return `
                <tr>
                    <td>
                        <strong>${escapeHtml(a.title)}</strong>
                        <br><small style="color: var(--text-muted);">${escapeHtml(a.content)}</small>
                    </td>
                    <td><span class="badge badge-info">${escapeHtml(commName)}</span></td>
                    <td><small>${dateStr}</small></td>
                    <td>
                        <button class="action danger" data-delete-announcement="${a.id}">
                            <i class="fa-solid fa-trash"></i> Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join("");
    }

    // ============================================
    // RENDER CHALLENGES
    // ============================================
    function renderChallenges(items) {
        const tbody = document.getElementById("challengesTable");
        if (!tbody) return;
        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: var(--text-muted);">No challenges added yet.</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(c => {
            const comm = loadedCommunities.find(comm => comm.id === c.community_id);
            const commName = comm ? comm.name : `#${c.community_id}`;
            const deadline = c.deadline ? new Date(c.deadline).toLocaleDateString() : "No deadline";

            return `
                <tr>
                    <td>
                        <strong>${escapeHtml(c.title)}</strong>
                        <br><small style="color: var(--text-muted);">${escapeHtml(c.description || '')}</small>
                    </td>
                    <td><span class="badge badge-info">${escapeHtml(commName)}</span></td>
                    <td><span class="badge badge-warning">${escapeHtml(c.difficulty)}</span></td>
                    <td><strong>${c.xp_reward}</strong> XP</td>
                    <td><small>${deadline}</small></td>
                    <td>
                        <button class="action danger" data-delete-challenge="${c.id}">
                            <i class="fa-solid fa-trash"></i> Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join("");
    }

    // ============================================
    // RENDER EVENTS
    // ============================================
    function renderEvents(items) {
        const tbody = document.getElementById("eventsTable");
        if (!tbody) return;
        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--text-muted);">No events scheduled yet.</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(e => {
            const comm = loadedCommunities.find(comm => comm.id === e.community_id);
            const commName = comm ? comm.name : `#${e.community_id}`;
            const dateStr = new Date(e.event_date).toLocaleString();

            return `
                <tr>
                    <td>
                        <strong>${escapeHtml(e.title)}</strong>
                        <br><small style="color: var(--text-muted);">${escapeHtml(e.description || '')}</small>
                    </td>
                    <td><span class="badge badge-info">${escapeHtml(commName)}</span></td>
                    <td><small>${dateStr}</small></td>
                    <td><span class="badge badge-success">${escapeHtml(e.status)}</span></td>
                    <td>
                        <button class="action danger" data-delete-event="${e.id}">
                            <i class="fa-solid fa-trash"></i> Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join("");
    }

    // ============================================
    // RENDER MEMBERSHIPS
    // ============================================
    function renderMemberships(items) {
        const tbody = document.getElementById("membershipsTable");
        if (!tbody) return;
        tbody.innerHTML = items.map(m => `
            <tr>
                <td>#${m.id}</td>
                <td>User #${m.user_id}</td>
                <td>Community #${m.community_id}</td>
                <td><span class="badge">${escapeHtml(m.role)}</span></td>
                <td><span class="badge ${m.status === 'approved' ? 'badge-success' : 'badge-warning'}">${escapeHtml(m.status)}</span></td>
                <td><span class="badge ${m.is_active ? 'badge-success' : 'badge-danger'}">${m.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="action ${m.is_active ? 'danger' : 'success'}" data-toggle-membership-status="${m.id}" data-status="${m.is_active}">
                        ${m.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                </td>
            </tr>
        `).join("");
    }

    // ============================================
    // RENDER USERS
    // ============================================
    function renderUsers(items) {
        const tbody = document.getElementById("usersTable");
        if (!tbody) return;
        tbody.innerHTML = items.map(u => `
            <tr>
                <td>
                    <strong>${escapeHtml(u.profile?.full_name || u.edu_email)}</strong>
                    <br><small style="color: var(--text-muted);">${escapeHtml(u.edu_email)}</small>
                </td>
                <td>
                    <strong>Roll:</strong> ${escapeHtml(u.profile?.roll || '—')}<br>
                    <small>${escapeHtml(u.profile?.department || '—')}, ${escapeHtml(u.profile?.semester || '—')}</small>
                </td>
                <td><span class="badge ${u.is_active ? 'badge-success' : 'badge-danger'}">${u.is_active ? 'Active' : 'Disabled'}</span></td>
                <td><span class="badge ${u.is_admin ? 'badge-info' : ''}">${u.is_admin ? 'Administrator' : 'Student'}</span></td>
                <td>
                    <button class="action ${u.is_active ? 'danger' : 'success'}" data-toggle-user-status="${u.id}" data-status="${u.is_active}">
                        ${u.is_active ? 'Disable' : 'Enable'}
                    </button>
                </td>
            </tr>
        `).join("");
    }

    // ============================================
    // MODAL OPEN / CLOSE CONTROLS
    // ============================================
    function closeModal(modal) {
        if (modal) modal.classList.remove("active");
    }

    document.querySelectorAll("[data-close]").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".modal-overlay").forEach(closeModal);
        });
    });

    document.querySelectorAll(".modal-overlay").forEach(overlay => {
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) closeModal(overlay);
        });
    });

    // Open Add Community Modal
    const openAddCommunityBtn = document.getElementById("openAddCommunityBtn");
    if (openAddCommunityBtn) {
        openAddCommunityBtn.addEventListener("click", () => {
            document.getElementById("communityModalTitle").textContent = "New Community";
            document.getElementById("communityEditId").value = "";
            document.getElementById("communityName").value = "";
            document.getElementById("communityDescription").value = "";
            document.getElementById("communityModal").classList.add("active");
        });
    }

    // Open Add Roadmap Modal
    const openAddRoadmapBtn = document.getElementById("openAddRoadmapBtn");
    if (openAddRoadmapBtn) {
        openAddRoadmapBtn.addEventListener("click", () => {
            document.getElementById("roadmapTitle").value = "";
            document.getElementById("roadmapDescription").value = "";
            document.getElementById("roadmapModal").classList.add("active");
        });
    }

    // Open Add Resource Modal
    const openAddResourceBtn = document.getElementById("openAddResourceBtn");
    if (openAddResourceBtn) {
        openAddResourceBtn.addEventListener("click", () => {
            document.getElementById("resourceTitle").value = "";
            document.getElementById("resourceUrl").value = "";
            document.getElementById("resourceDescription").value = "";
            document.getElementById("resourceModal").classList.add("active");
        });
    }

    // Open Add Announcement Modal
    const openAddAnnouncementBtn = document.getElementById("openAddAnnouncementBtn");
    if (openAddAnnouncementBtn) {
        openAddAnnouncementBtn.addEventListener("click", () => {
            document.getElementById("announcementTitle").value = "";
            document.getElementById("announcementContent").value = "";
            document.getElementById("announcementModal").classList.add("active");
        });
    }

    // Open Add Challenge Modal
    const openAddChallengeBtn = document.getElementById("openAddChallengeBtn");
    if (openAddChallengeBtn) {
        openAddChallengeBtn.addEventListener("click", () => {
            document.getElementById("challengeTitle").value = "";
            document.getElementById("challengeDescription").value = "";
            document.getElementById("challengeModal").classList.add("active");
        });
    }

    // Open Add Event Modal
    const openAddEventBtn = document.getElementById("openAddEventBtn");
    if (openAddEventBtn) {
        openAddEventBtn.addEventListener("click", () => {
            document.getElementById("eventTitle").value = "";
            document.getElementById("eventDescription").value = "";
            document.getElementById("eventModal").classList.add("active");
        });
    }

    // Toggle Add Module Form
    const openAddModuleBtn = document.getElementById("openAddModuleBtn");
    const addModuleForm = document.getElementById("addModuleForm");
    if (openAddModuleBtn && addModuleForm) {
        openAddModuleBtn.addEventListener("click", () => {
            addModuleForm.style.display = addModuleForm.style.display === "none" ? "block" : "none";
            document.getElementById("addTaskForm").style.display = "none";
        });
        document.getElementById("cancelModuleBtn").addEventListener("click", () => {
            addModuleForm.style.display = "none";
        });
    }

    // Cancel Add Task
    const cancelTaskBtn = document.getElementById("cancelTaskBtn");
    if (cancelTaskBtn) {
        cancelTaskBtn.addEventListener("click", () => {
            document.getElementById("addTaskForm").style.display = "none";
        });
    }

    // ============================================
    // FORM SUBMISSIONS
    // ============================================

    // 1. Community Form (Create / Edit)
    document.getElementById("communityForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = document.getElementById("communityEditId").value;
        const name = document.getElementById("communityName").value.trim();
        const description = document.getElementById("communityDescription").value.trim();

        try {
            if (id) {
                await request(`/communities/${id}`, {
                    method: "PUT",
                    body: JSON.stringify({ name, description })
                });
                setFeedback("Community updated successfully.");
            } else {
                await request("/communities", {
                    method: "POST",
                    body: JSON.stringify({ name, description, is_active: true })
                });
                setFeedback("Community created successfully.");
            }
            closeModal(document.getElementById("communityModal"));
            await loadAll();
        } catch (err) {
            setFeedback(err.message, true);
        }
    });

    // 2. Roadmap Form (Create)
    document.getElementById("roadmapForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const community_id = parseInt(document.getElementById("roadmapCommunitySelect").value);
        const title = document.getElementById("roadmapTitle").value.trim();
        const description = document.getElementById("roadmapDescription").value.trim();

        try {
            await request("/roadmaps", {
                method: "POST",
                body: JSON.stringify({ community_id, title, description })
            });
            setFeedback("Roadmap created successfully.");
            closeModal(document.getElementById("roadmapModal"));
            await loadAll();
        } catch (err) {
            setFeedback(err.message, true);
        }
    });

    // 3. Module Form (Create under active roadmap)
    document.getElementById("addModuleForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!activeRoadmapForManagement) return;
        const order = parseInt(document.getElementById("moduleOrder").value);
        const title = document.getElementById("moduleTitle").value.trim();
        const description = document.getElementById("moduleDescription").value.trim();

        try {
            await request(`/roadmaps/${activeRoadmapForManagement}/modules`, {
                method: "POST",
                body: JSON.stringify({ order, title, description })
            });
            setFeedback("Module added successfully.");
            document.getElementById("addModuleForm").reset();
            document.getElementById("addModuleForm").style.display = "none";
            await loadRoadmapTree(activeRoadmapForManagement);
            await loadAll();
        } catch (err) {
            setFeedback(err.message, true);
        }
    });

    // 4. Task Form (Create under target module)
    document.getElementById("addTaskForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const module_id = parseInt(document.getElementById("targetModuleId").value);
        const order = parseInt(document.getElementById("taskOrder").value);
        const title = document.getElementById("taskTitle").value.trim();

        try {
            await request(`/modules/${module_id}/tasks`, {
                method: "POST",
                body: JSON.stringify({ order, title })
            });
            setFeedback("Task added successfully.");
            document.getElementById("addTaskForm").reset();
            document.getElementById("addTaskForm").style.display = "none";
            await loadRoadmapTree(activeRoadmapForManagement);
            await loadAll();
        } catch (err) {
            setFeedback(err.message, true);
        }
    });

    // 5. Resource Form (Create)
    document.getElementById("resourceForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const community_id = parseInt(document.getElementById("resourceCommunitySelect").value);
        const title = document.getElementById("resourceTitle").value.trim();
        const resource_type = document.getElementById("resourceType").value;
        const difficulty = document.getElementById("resourceDifficulty").value;
        const url = document.getElementById("resourceUrl").value.trim();
        const description = document.getElementById("resourceDescription").value.trim();

        try {
            await request("/resources", {
                method: "POST",
                body: JSON.stringify({ community_id, title, resource_type, difficulty, url, description })
            });
            setFeedback("Resource added successfully.");
            closeModal(document.getElementById("resourceModal"));
            await loadAll();
        } catch (err) {
            setFeedback(err.message, true);
        }
    });

    // 6. Announcement Form (Create)
    document.getElementById("announcementForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const community_id = parseInt(document.getElementById("announcementCommunitySelect").value);
        const title = document.getElementById("announcementTitle").value.trim();
        const content = document.getElementById("announcementContent").value.trim();

        try {
            await request("/announcements", {
                method: "POST",
                body: JSON.stringify({ community_id, title, content })
            });
            setFeedback("Announcement published successfully.");
            closeModal(document.getElementById("announcementModal"));
            await loadAll();
        } catch (err) {
            setFeedback(err.message, true);
        }
    });

    // 7. Challenge Form (Create)
    document.getElementById("challengeForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const community_id = parseInt(document.getElementById("challengeCommunitySelect").value);
        const title = document.getElementById("challengeTitle").value.trim();
        const difficulty = document.getElementById("challengeDifficulty").value;
        const xp_reward = parseInt(document.getElementById("challengeXp").value) || 100;
        const description = document.getElementById("challengeDescription").value.trim();

        try {
            await request("/challenges", {
                method: "POST",
                body: JSON.stringify({
                    community_id,
                    title,
                    difficulty,
                    xp_reward,
                    description,
                    is_active: true
                })
            });
            setFeedback("Challenge created successfully.");
            closeModal(document.getElementById("challengeModal"));
            await loadAll();
        } catch (err) {
            setFeedback(err.message, true);
        }
    });

    // 8. Event Form (Create)
    document.getElementById("eventForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const community_id = parseInt(document.getElementById("eventCommunitySelect").value);
        const title = document.getElementById("eventTitle").value.trim();
        const event_date = document.getElementById("eventDate").value;
        const status = document.getElementById("eventStatus").value;
        const description = document.getElementById("eventDescription").value.trim();

        try {
            await request("/events", {
                method: "POST",
                body: JSON.stringify({
                    community_id,
                    title,
                    event_date,
                    status,
                    description
                })
            });
            setFeedback("Event scheduled successfully.");
            closeModal(document.getElementById("eventModal"));
            await loadAll();
        } catch (err) {
            setFeedback(err.message, true);
        }
    });

    // ============================================
    // GLOBAL CLICK DISPATCHER (ACTIONS & DELETIONS)
    // ============================================
    document.addEventListener("click", async (event) => {
        const target = event.target.closest("button");
        if (!target) return;

        // Edit Community
        if (target.dataset.editCommunity) {
            const id = target.dataset.editCommunity;
            document.getElementById("communityModalTitle").textContent = "Edit Community";
            document.getElementById("communityEditId").value = id;
            document.getElementById("communityName").value = target.dataset.name || "";
            document.getElementById("communityDescription").value = target.dataset.desc || "";
            document.getElementById("communityModal").classList.add("active");
            return;
        }

        // Toggle Community Status
        if (target.dataset.toggleCommunityStatus) {
            const id = target.dataset.toggleCommunityStatus;
            const currentActive = target.dataset.status === "true";
            try {
                await request(`/communities/${id}/status`, {
                    method: "PATCH",
                    body: JSON.stringify({ is_active: !currentActive })
                });
                setFeedback(`Community ${!currentActive ? 'enabled' : 'disabled'}.`);
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Approve Join Request
        if (target.dataset.approveRequest) {
            const id = target.dataset.approveRequest;
            try {
                await request(`/join-requests/${id}/approve`, { method: "POST" });
                setFeedback("Student join request approved!");
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Reject Join Request
        if (target.dataset.rejectRequest) {
            const id = target.dataset.rejectRequest;
            if (!confirm("Reject this student's join request?")) return;
            try {
                await request(`/join-requests/${id}/reject`, { method: "POST" });
                setFeedback("Join request rejected.");
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Manage Roadmap
        if (target.dataset.manageRoadmap) {
            openManageRoadmap(parseInt(target.dataset.manageRoadmap), target.dataset.title);
            return;
        }

        // Open Add Task for Module
        if (target.dataset.openAddTask) {
            const modId = target.dataset.openAddTask;
            const modTitle = target.dataset.modTitle;
            document.getElementById("targetModuleId").value = modId;
            document.getElementById("addTaskHeader").textContent = `Add Task to: ${modTitle}`;
            document.getElementById("addTaskForm").style.display = "block";
            document.getElementById("addModuleForm").style.display = "none";
            document.getElementById("taskTitle").focus();
            return;
        }

        // Delete Task
        if (target.dataset.deleteTask) {
            if (!confirm("Delete this task?")) return;
            try {
                await request(`/tasks/${target.dataset.deleteTask}`, { method: "DELETE" });
                setFeedback("Task deleted.");
                if (activeRoadmapForManagement) await loadRoadmapTree(activeRoadmapForManagement);
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Delete Module
        if (target.dataset.deleteModule) {
            if (!confirm("Delete this module and all its tasks?")) return;
            try {
                await request(`/modules/${target.dataset.deleteModule}`, { method: "DELETE" });
                setFeedback("Module deleted.");
                if (activeRoadmapForManagement) await loadRoadmapTree(activeRoadmapForManagement);
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Delete Roadmap
        if (target.dataset.deleteRoadmap) {
            if (!confirm("Delete this entire roadmap including all modules and tasks?")) return;
            try {
                await request(`/roadmaps/${target.dataset.deleteRoadmap}`, { method: "DELETE" });
                setFeedback("Roadmap deleted.");
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Delete Resource
        if (target.dataset.deleteResource) {
            if (!confirm("Delete this resource?")) return;
            try {
                await request(`/resources/${target.dataset.deleteResource}`, { method: "DELETE" });
                setFeedback("Resource deleted.");
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Delete Announcement
        if (target.dataset.deleteAnnouncement) {
            if (!confirm("Delete this announcement?")) return;
            try {
                await request(`/announcements/${target.dataset.deleteAnnouncement}`, { method: "DELETE" });
                setFeedback("Announcement deleted.");
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Delete Challenge
        if (target.dataset.deleteChallenge) {
            if (!confirm("Delete this challenge?")) return;
            try {
                await request(`/challenges/${target.dataset.deleteChallenge}`, { method: "DELETE" });
                setFeedback("Challenge deleted.");
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Delete Event
        if (target.dataset.deleteEvent) {
            if (!confirm("Delete this event?")) return;
            try {
                await request(`/events/${target.dataset.deleteEvent}`, { method: "DELETE" });
                setFeedback("Event deleted.");
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Toggle Membership Status
        if (target.dataset.toggleMembershipStatus) {
            const id = target.dataset.toggleMembershipStatus;
            const currentActive = target.dataset.status === "true";
            try {
                await request(`/memberships/${id}/status`, {
                    method: "PATCH",
                    body: JSON.stringify({ is_active: !currentActive })
                });
                setFeedback(`Membership ${!currentActive ? 'activated' : 'deactivated'}.`);
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }

        // Toggle User Status
        if (target.dataset.toggleUserStatus) {
            const id = target.dataset.toggleUserStatus;
            const currentActive = target.dataset.status === "true";
            try {
                await request(`/users/${id}/status`, {
                    method: "PATCH",
                    body: JSON.stringify({ is_active: !currentActive })
                });
                setFeedback(`User ${!currentActive ? 'enabled' : 'disabled'}.`);
                await loadAll();
            } catch (err) { setFeedback(err.message, true); }
            return;
        }
    });

    // Search Users
    const userSearch = document.getElementById("userSearch");
    if (userSearch) {
        let debounceTimer;
        userSearch.addEventListener("input", (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                try {
                    const query = encodeURIComponent(e.target.value.trim());
                    const users = await request(`/users?search=${query}`);
                    renderUsers(users || []);
                } catch (err) { setFeedback(err.message, true); }
            }, 300);
        });
    }

    // Refresh Button
    document.querySelectorAll("[data-refresh]").forEach(btn => {
        btn.addEventListener("click", loadAll);
    });

    // Sidebar active highlighting
    const sidebarNavLinks = document.querySelectorAll(".admin-sidebar nav a");
    sidebarNavLinks.forEach(link => {
        link.addEventListener("click", () => {
            sidebarNavLinks.forEach(l => l.classList.remove("active"));
            link.classList.add("active");
        });
    });

    // Logout
    document.getElementById("logoutButton")?.addEventListener("click", () => {
        api.clearSession();
        window.location.href = "login.html";
    });

    // Initial load
    loadAll();
});
