document.addEventListener("DOMContentLoaded", async () => {

    const communityGrid =
        document.querySelector(".community-grid");

    if (!communityGrid) {
        console.error("Community grid not found.");
        return;
    }


    // =====================================================
    // GET LOGIN TOKEN
    // =====================================================

    const token =
        localStorage.getItem("access_token");


    // =====================================================
    // LOAD ALL COMMUNITIES
    // =====================================================

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/api/v1/communities",
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );


        if (!response.ok) {

            throw new Error(
                `Failed to fetch communities: ${response.status}`
            );

        }


        const communities =
            await response.json();


        console.log(
            "COMMUNITIES FROM BACKEND:",
            communities
        );


        // Clear existing cards

        communityGrid.innerHTML = "";


        // =====================================================
        // NO COMMUNITY
        // =====================================================

        if (
            !communities ||
            communities.length === 0
        ) {

            communityGrid.innerHTML = `
                <div class="no-community">

                    <h3>
                        No communities available
                    </h3>

                    <p>
                        Please check again later.
                    </p>

                </div>
            `;

            return;
        }


        // =====================================================
        // CREATE COMMUNITY CARDS
        // =====================================================

        for (const community of communities) {

            console.log(
                "Community:",
                community.name,
                "ID:",
                community.id
            );


            // -------------------------------------------------
            // COMMUNITY TYPE
            // -------------------------------------------------

            const communityName =
                community.name.toLowerCase();


            const isProgramming =
                communityName.includes("programming");


            const isWebDevelopment =
                communityName.includes("web development") ||
                communityName.includes("web");


            // -------------------------------------------------
            // ICON
            // -------------------------------------------------

            const iconClass =
                isProgramming
                    ? "fa-code"
                    : "fa-globe";


            // -------------------------------------------------
            // EXPLORE PAGE
            // -------------------------------------------------

            let explorePage = "#";


            if (isProgramming) {

                explorePage =
                    `programming_community_exp.html?id=${community.id}`;

            }

            else if (isWebDevelopment) {

                explorePage =
                    `web_development_community_exp.html?id=${community.id}`;

            }


            // =================================================
            // CHECK MEMBERSHIP
            // =================================================

            let isMember = false;


            if (token) {

                try {

                    const membershipResponse =
                        await fetch(
                            `http://127.0.0.1:8000/api/v1/communities/${community.id}/membership`,
                            {
                                method: "GET",

                                headers: {
                                    "Accept": "application/json",
                                    "Authorization":
                                        `Bearer ${token}`
                                }
                            }
                        );


                    // -----------------------------------------
                    // TOKEN INVALID
                    // -----------------------------------------

                    if (
                        membershipResponse.status === 401
                    ) {

                        console.log(
                            "Token expired or invalid."
                        );

                        localStorage.removeItem(
                            "access_token"
                        );

                        localStorage.removeItem(
                            "user_id"
                        );

                        localStorage.removeItem(
                            "edu_email"
                        );

                        localStorage.removeItem(
                            "full_name"
                        );

                        window.location.href =
                            "login.html";

                        return;
                    }


                    // -----------------------------------------
                    // MEMBERSHIP RESPONSE
                    // -----------------------------------------

                    if (membershipResponse.ok) {

                        const membershipData =
                            await membershipResponse.json();


                        isMember =
                            membershipData.is_member === true;


                        console.log(
                            "Membership:",
                            community.name,
                            isMember
                        );

                    }

                }

                catch (membershipError) {

                    console.error(
                        "Membership check failed:",
                        membershipError
                    );

                }

            }


            // =================================================
            // BUTTON TEXT
            // =================================================

            let buttonText =
                "Explore Community";


            if (isMember) {

                buttonText =
                    "Your Dashboard";

            }


            // =================================================
            // CREATE TOPICS
            // =================================================

            let topicsHtml = "";


            if (
                community.topics &&
                community.topics.length > 0
            ) {

                topicsHtml = `
                    <div class="topics">

                        ${community.topics
                            .map(topic => `
                                <span>
                                    ${topic}
                                </span>
                            `)
                            .join("")}

                    </div>
                `;

            }


            // =================================================
            // CREATE CARD
            // =================================================

            const card =
                document.createElement("div");


            card.className =
                "community-card";


            card.innerHTML = `

                <div class="card-top">

                    <div class="community-icon">

                        <i class="fa-solid ${iconClass}"></i>

                    </div>


                    <span class="community-status">

                        <i class="fa-solid fa-circle"></i>

                        Active

                    </span>

                </div>


                <div class="card-content">

                    <h3>
                        ${community.name}
                    </h3>


                    <p>

                        ${
                            community.description ||
                            "Join this community to learn and grow."
                        }

                    </p>


                    ${topicsHtml}


                    <div class="community-stats">


                        <div class="stat">

                            <i class="fa-solid fa-users"></i>

                            <div>

                                <strong>
                                    ${community.active_members_count}+
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


                    <a
                        href="#"
                        class="explore-btn"
                    >

                        ${buttonText}

                        <i class="fa-solid fa-arrow-right"></i>

                    </a>


                </div>

            `;


            // =================================================
            // BUTTON
            // =================================================

            const button =
                card.querySelector(".explore-btn");


            button.addEventListener(
                "click",
                (event) => {

                    event.preventDefault();


                    // =========================================
                    // NOT LOGGED IN
                    // =========================================

                    if (!token) {

                        console.log(
                            "User is not logged in."
                        );

                        window.location.href =
                            "login.html";

                        return;
                    }


                    // =========================================
                    // MEMBER
                    // =========================================

                    if (isMember) {

                        console.log(
                            "User is a member of:",
                            community.name
                        );


                        // -------------------------------
                        // PROGRAMMING DASHBOARD
                        // -------------------------------

                        if (isProgramming) {

                            window.location.href =
                                `programming_dashboard.html?id=${community.id}`;

                            return;
                        }


                        // -------------------------------
                        // WEB DEVELOPMENT DASHBOARD
                        // -------------------------------

                        if (isWebDevelopment) {

                            window.location.href =
                                `web_development_dashboard.html?id=${community.id}`;

                            return;
                        }


                        alert(
                            "Dashboard is not available for this community yet."
                        );

                        return;
                    }


                    // =========================================
                    // NOT MEMBER
                    // =========================================

                    console.log(
                        "User is not a member of:",
                        community.name
                    );


                    if (explorePage !== "#") {

                        window.location.href =
                            explorePage;

                        return;
                    }


                    alert(
                        "Community page is not available yet."
                    );

                }
            );


            // =================================================
            // ADD CARD TO GRID
            // =================================================

            communityGrid.appendChild(card);

        }


    }

    // =====================================================
    // ERROR
    // =====================================================

    catch (error) {

        console.error(
            "Error loading communities:",
            error
        );


        communityGrid.innerHTML = `

            <div class="no-community">

                <h3>
                    Failed to load communities
                </h3>

                <p>
                    Please try again later.
                </p>

            </div>

        `;

    }

});