const form = document.getElementById("registerForm");
const message = document.getElementById("message");

form.addEventListener("submit", async function (e) {
    e.preventDefault();
    console.log("Form Submitted");
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (password !== confirmPassword) {
        message.style.color = "red";
        message.innerText = "Password and Confirm Password do not match.";
        return;
    }

    const data = {
        full_name: document.getElementById("fullname").value,
        roll: document.getElementById("roll").value,
        semester: document.getElementById("semester").value,
        edu_email: document.getElementById("edu-email").value,
        mobile: document.getElementById("mobile").value,
        password: password,
        confirm_password: confirmPassword
    };

    try {
        const response = await skillBridgeApi.request("/api/v1/auth/register", {
            method: "POST",
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            message.style.color = "green";
            message.innerText = result.message;

            form.reset();

            setTimeout(() => {
                window.location.href = "login.html";
            }, 1500);

        } else {
            message.style.color = "red";
            message.innerText = result.detail || "Registration failed.";
        }

    } catch (error) {
        message.style.color = "red";
        message.innerText = "Cannot connect to server.";
    }
});