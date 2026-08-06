document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.querySelector(".auth-form");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirm-password");

    if (registerForm) {
        registerForm.addEventListener("submit", (e) => {
            e.preventDefault();
            
            if (password.value !== confirmPassword.value) {
                alert("Passwords do not match!");
                return;
            }

            // TODO: Implement registration API call
            console.log("Registration form submitted");
        });
    }
});
