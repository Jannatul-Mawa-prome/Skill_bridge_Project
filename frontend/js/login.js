document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector(".auth-form");

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const email = document.getElementById("login-id").value.trim();
            const password = document.getElementById("password").value;

            try {
                const response = await fetch(
                    "http://127.0.0.1:8000/api/v1/auth/login",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            edu_email: email,
                            password: password
                        })
                    }
                );

                const data = await response.json();

                // Wrong email/password
                if (!response.ok) {
                    alert(data.detail || "Login failed.");
                    return;
                }

                // Successful login
                localStorage.setItem("user_id", data.user_id);
                localStorage.setItem("edu_email", data.edu_email);
                localStorage.setItem("full_name", data.full_name);

                // Go to home page
                window.location.href = "index.html";

            } catch (error) {
                console.error("Login error:", error);
                alert("Could not connect to API.");
            }
        });
    }
});