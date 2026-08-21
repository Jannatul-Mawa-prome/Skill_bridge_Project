document.addEventListener("DOMContentLoaded", () => {
    const mobileMenu = document.getElementById('mobileMenu');
    const navLinks = document.getElementById('navLinks');

    if (mobileMenu && navLinks) {
        mobileMenu.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileMenu.classList.toggle('open');
        });
    }
});

document.addEventListener("DOMContentLoaded", () => {

    const fullName = localStorage.getItem("full_name");

    const loginBtn = document.getElementById("loginBtn");
    const signupBtn = document.getElementById("signupBtn");

    const userMenu = document.getElementById("userMenu");
    const userName = document.getElementById("userName");
    const userMenuBtn = document.getElementById("userMenuBtn");
    const logoutBtn = document.getElementById("logoutBtn");

    // If user is logged in
    if (fullName) {

        loginBtn.style.display = "none";
        signupBtn.style.display = "none";

        userMenu.style.display = "block";
        userName.textContent = fullName;

        // Open / close dropdown
        userMenuBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            userMenu.classList.toggle("active");
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", () => {
            userMenu.classList.remove("active");
        });

        // Logout
        logoutBtn.addEventListener("click", () => {

            localStorage.removeItem("user_id");
            localStorage.removeItem("edu_email");
            localStorage.removeItem("full_name");

            window.location.href = "index.html";
        });
    }
});
