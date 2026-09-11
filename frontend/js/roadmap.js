document.addEventListener("DOMContentLoaded", async () => {

    const communityList = document.getElementById("communityList");

    // =========================
    // CHECK LOGIN
    // =========================

    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "login.html";
        return;
    }


    // =========================
    // LOAD MY COMMUNITIES
    // =========================

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/api/v1/communities/my-communities",
            {
                method: "GET",

                headers: {
                    "Accept": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            }
        );


        // =========================
        // UNAUTHORIZED
        // =========================

        if (response.status === 401) {

            localStorage.removeItem("access_token");
            localStorage.removeItem("user_id");
            localStorage.removeItem("edu_email");
            localStorage.removeItem("full_name");

            window.location.href = "login.html";

            return;
        }


        // =========================
        // OTHER ERROR
        // =========================

        if (!response.ok) {
            throw new Error(
                `HTTP error: ${response.status}`
            );
        }


        const communities = await response.json();

        console.log("My communities:", communities);


        // Clear loading

        communityList.innerHTML = "";


        // =========================
        // NO COMMUNITY
        // =========================

        if (!communities || communities.length === 0) {

            communityList.innerHTML = `
                <div class="no-community">

                    <div class="no-community-icon">
                        📚
                    </div>

                    <h3>No Communities Yet</h3>

                    <p>
                        You haven't joined any community yet.
                    </p>

                </div>
            `;

            return;
        }


        // =========================
        // CREATE CARDS
        // =========================

        communities.forEach(community => {

            let icon = "💻";

            let topics = [];


            // =========================
            // PROGRAMMING
            // =========================

            if (
                community.name
                    .toLowerCase()
                    .includes("programming")
            ) {

                icon = "💻";

                topics = [
                    "C++",
                    "Python",
                    "DSA",
                    "Problem Solving"
                ];

            }


            // =========================
            // WEB DEVELOPMENT
            // =========================

            else if (
                community.name
                    .toLowerCase()
                    .includes("web")
            ) {

                icon = "🌐";

                topics = [
                    "HTML",
                    "CSS",
                    "JavaScript",
                    "React",
                    "Backend"
                ];

            }


            // =========================
            // CREATE CARD
            // =========================

            const card = document.createElement("div");

            card.className = "community-card";


            card.innerHTML = `

                <div class="card-top">

                    <div class="community-icon">
                        ${icon}
                    </div>

                    <div class="arrow-icon">
                        →
                    </div>

                </div>


                <div class="card-content">

                    <h3>
                        ${community.name}
                    </h3>


                    <p class="community-card-description">

                        ${
                            community.description ||
                            "Continue your learning journey with this community."
                        }

                    </p>


                    <!-- TOPICS -->

                    <div class="topics">

                        ${
                            topics
                                .map(topic => `<span>${topic}</span>`)
                                .join("")
                        }

                    </div>


                    <!-- STATS -->

                    <div class="community-stats">

                        <div class="stat">

                            <i class="fa-solid fa-users"></i>

                            <div>

                                <strong>
                                    ${community.active_members_count}
                                </strong>

                                <small>
                                    Members
                                </small>

                            </div>

                        </div>


                        <div class="stat">

                            <i class="fa-solid fa-trophy"></i>

                            <div>

                                <strong>
                                    ${community.challenges_count || 0}
                                </strong>

                                <small>
                                    Challenges
                                </small>

                            </div>

                        </div>

                    </div>


                    <!-- CONTINUE BUTTON -->

                    <button
                        type="button"
                        class="continue-btn"
                    >

                        Continue Learning

                        <span>→</span>

                    </button>

                </div>

            `;


            // =========================
            // CONTINUE BUTTON CLICK
            // =========================

            const continueButton =
                card.querySelector(".continue-btn");


            continueButton.addEventListener(
                "click",
                () => {

                    console.log(
                        "Selected community:",
                        community.id,
                        community.name
                    );


                    // Programming

                    if (
                        community.name
                            .toLowerCase()
                            .includes("programming")
                    ) {

                        window.location.href =
                            `programming_dashboard.html?id=${community.id}`;

                        return;
                    }


                    // Web Development

                    if (
                        community.name
                            .toLowerCase()
                            .includes("web")
                    ) {

                        window.location.href =
                            `web_development_dashboard.html?id=${community.id}`;

                        return;
                    }


                    alert(
                        "Dashboard is not available for this community yet."
                    );

                }
            );


            // =========================
            // ADD CARD
            // =========================

            communityList.appendChild(card);

        });


    } catch (error) {

        console.error(
            "Community loading error:",
            error
        );


        communityList.innerHTML = `

            <div class="no-community">

                <div class="no-community-icon">
                    ⚠️
                </div>

                <h3>
                    Failed to Load Communities
                </h3>

                <p>
                    Please try again later.
                </p>

            </div>

        `;

    }

});