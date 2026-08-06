document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.querySelector(".auth-form");
    const submitBtn = document.querySelector(".signup-submit-btn");

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const fullName = document.getElementById("fullname").value.trim();
            const roll = document.getElementById("roll").value.trim();
            const semester = document.getElementById("semester").value;
            const eduEmail = document.getElementById("edu-email").value.trim();
            const mobile = document.getElementById("mobile").value.trim();
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm-password").value;

            if (password !== confirmPassword) {
                alert("Passwords do not match!");
                return;
            }

            const payload = {
                full_name: fullName,
                roll: roll,
                semester: semester,
                edu_email: eduEmail,
                mobile: mobile,
                password: password,
                confirm_password: confirmPassword
            };

            const originalBtnText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = "Registering...";

            try {
                const response = await fetch("http://127.0.0.1:8000/api/v1/auth/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    alert(result.message || "Registration successful!");
                    window.location.href = "login.html";
                } else {
                    const errorMsg = result.detail || result.message || "Registration failed. Please check your data.";
                    alert("Error: " + (typeof errorMsg === "object" ? JSON.stringify(errorMsg) : errorMsg));
                }
            } catch (error) {
                console.error("API Error:", error);
                alert("Could not connect to server. Make sure backend API is running.");
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;
            }
        });
    }
});
