document.addEventListener("DOMContentLoaded", async () => {

    const loginBtn = document.getElementById("loginBtn");
    const registerBtn = document.getElementById("registerBtn");
    const logoutBtn = document.getElementById("logoutBtn");
    const demoForm = document.getElementById("demoForm");
    const chartsContainer = document.getElementById("chartsContainer");
    const authContainer = document.querySelector(".auth-buttons");

    async function checkAuth() {
        try {
            const response = await fetch("/auth/is_logged", {
                credentials: "include"
            });
            console.log("Auth check status:", response.status);
            if (!response.ok) {
                showLoggedOut();
                return;
            }
            console.log("Auth check response status:", response.status);
            const data = await response.json();
            console.log("Auth check response:", data);
            if (data.authenticated) {
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
        logoutBtn.style.display = "inline-block";
    }

    function showLoggedOut() {
        loginBtn.style.display = "inline-block";
        registerBtn.style.display = "inline-block";
        logoutBtn.style.display = "none";
    }

    await checkAuth();


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

});
