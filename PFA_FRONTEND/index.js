document.addEventListener("DOMContentLoaded", async () => {

    const loginBtn = document.getElementById("loginBtn");
    const registerBtn = document.getElementById("registerBtn");
    const logoutBtn = document.getElementById("logoutBtn");
    const demoForm = document.getElementById("demoForm");
    const chartsContainer = document.getElementById("chartsContainer");
    const authContainer = document.querySelector(".auth-buttons");
    const dashboardBtn = document.getElementById("dashboardBtn");

    async function checkAuth() {
        try {
            const data = await checkMe();
            console.log("Auth check response:", data);
            if (!!data) {
                console.log("User is authenticated");
                showLoggedIn();
            } else {
                showLoggedOut();
            }

        } catch (e) {
            console.error("Error during auth check:", e);
            showLoggedOut();
        } finally {
            if (authContainer) {
                authContainer.style.visibility = "visible";
            }
        }
    }

    function showLoggedIn() {
        loginBtn.style.display = "none";
        registerBtn.style.display = "none";
        dashboardBtn.style.display = "inline-block";
        logoutBtn.style.display = "inline-block";
    }

    function showLoggedOut() {
        loginBtn.style.display = "inline-block";
        registerBtn.style.display = "inline-block";
        logoutBtn.style.display = "none";
        dashboardBtn.style.display = "none";
    }

    await checkAuth();

    dashboardBtn.addEventListener("click", () => {
        console.log("Dashboard button clicked");
        switchToDashboard()
    });

    loginBtn.addEventListener("click", () => {
        window.location.href = "/auth/login";
    });
    registerBtn.addEventListener("click", () => {
        window.location.href = "/auth/login";
    });
    logoutBtn.addEventListener("click", () => {
        window.location.href = "/auth/logout";
    });


    demoForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(demoForm);

        try {
            await fakeRequest(Object.fromEntries(formData.entries()));
            chartsContainer.innerText = "Dane przesłane — tu pojawią się wykresy.";
        } catch (err) {
            alert("Błąd podczas wysyłania danych");
        }
    });

    function fakeRequest(data) {
        return new Promise((resolve) => {
            setTimeout(() => resolve({ status: "ok", data }), 800);
        });
    }

    async function checkMe(){
        try {
            const response = await fetch("/auth/me", {
                credentials: "include"
            });
            if (!response.ok) {
                return false;
            }
            const data = await response.json();
            if (data && data.authenticated) {
                return true;
            } else {
                return false;
            }

        } catch (err) {
            console.error("Error fetching user info:", err);
        }
    }

    async function switchToDashboard() {
        const data = await checkMe();
        console.log("Dashboard auth check:", data);
        if (!!data) {
            window.location.href = "/dashboard.html";
        } else {
            window.location.href = "/auth/login";
        }
    }


});
