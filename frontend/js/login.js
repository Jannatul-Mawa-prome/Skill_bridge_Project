document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector(".auth-form");

    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();
            // TODO: Implement login API call
            console.log("Login form submitted");
        });
    }
});
