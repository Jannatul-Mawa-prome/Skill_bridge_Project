(() => {
    const API_BASE_URL = "http://127.0.0.1:8000";
    const SESSION_KEYS = ["access_token", "user_id", "edu_email", "full_name"];

    const clearSession = () => {
        SESSION_KEYS.forEach((key) => localStorage.removeItem(key));
    };

    const request = async (path, options = {}) => {
        const headers = new Headers(options.headers || {});
        headers.set("Accept", "application/json");

        if (options.body && !headers.has("Content-Type")) {
            headers.set("Content-Type", "application/json");
        }

        const token = localStorage.getItem("access_token");
        if (token) {
            headers.set("Authorization", `Bearer ${token}`);
        }

        const url = (path.startsWith("http://") || path.startsWith("https://"))
            ? path
            : `${API_BASE_URL}${path.startsWith('/') ? path : '/' + path}`;

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (response.status === 401) {
            clearSession();
        }

        return response;
    };

    window.skillBridgeApi = {
        request,
        clearSession,
        getToken: () => localStorage.getItem("access_token"),
        parseJson: async (response) => {
            const text = await response.text();
            return text ? JSON.parse(text) : null;
        }
    };
})();
