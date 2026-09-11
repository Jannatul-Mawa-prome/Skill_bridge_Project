// ============================================
// MOBILE MENU
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    const mobileMenu = document.getElementById("mobileMenu");
    const navLinks = document.getElementById("navLinks");

    if (mobileMenu && navLinks) {

        mobileMenu.addEventListener("click", () => {

            navLinks.classList.toggle("active");
            mobileMenu.classList.toggle("open");

        });

    }

});


// ============================================
// USER MENU + LOGOUT
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    const fullName = localStorage.getItem("full_name");

    const loginBtn = document.getElementById("loginBtn");
    const signupBtn = document.getElementById("signupBtn");

    const userMenu = document.getElementById("userMenu");
    const userName = document.getElementById("userName");
    const userMenuBtn = document.getElementById("userMenuBtn");
    const logoutBtn = document.getElementById("logoutBtn");


    // ========================================
    // USER IS LOGGED IN
    // ========================================

    if (fullName) {

        if (loginBtn) {
            loginBtn.style.display = "none";
        }

        if (signupBtn) {
            signupBtn.style.display = "none";
        }

        if (userMenu) {
            userMenu.style.display = "block";
        }

        if (userName) {
            userName.textContent = fullName;
        }


        // ====================================
        // OPEN / CLOSE USER DROPDOWN
        // ====================================

        if (userMenuBtn) {

            userMenuBtn.addEventListener("click", (e) => {

                e.stopPropagation();

                userMenu.classList.toggle("active");

            });

        }


        // ====================================
        // CLOSE DROPDOWN WHEN CLICKING OUTSIDE
        // ====================================

        document.addEventListener("click", () => {

            if (userMenu) {
                userMenu.classList.remove("active");
            }

        });


        // ====================================
        // LOGOUT
        // ====================================

        if (logoutBtn) {

            logoutBtn.addEventListener("click", () => {

                localStorage.removeItem("access_token");
                localStorage.removeItem("user_id");
                localStorage.removeItem("edu_email");
                localStorage.removeItem("full_name");

                window.location.href = "index.html";

            });

        }

    }

});


// ============================================
// ROADMAP NAVIGATION
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    const roadmapLink = document.getElementById("roadmapLink");

    if (!roadmapLink) {
        return;
    }


    roadmapLink.addEventListener("click", (e) => {

        e.preventDefault();


        // =====================================
        // CHECK LOGIN
        // =====================================

        const token = localStorage.getItem("access_token");


        // =====================================
        // NOT LOGGED IN
        // =====================================

        if (!token) {

            window.location.href = "login.html";

            return;
        }


        // =====================================
        // LOGGED IN
        // =====================================

        window.location.href = "roadmap.html";

    });

});