document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("expenseForm");
    const table = document.getElementById("expensesTable");
    const totalAmount = document.getElementById("totalAmount");
    const logoutBtn = document.getElementById("logoutBtn");

    let expenses = [];
    checkAuth();


    function saveExpenses() {
        localStorage.setItem("expenses", JSON.stringify(expenses));
    }

    function renderExpenses() {
        table.innerHTML = "";
        let total = 0;

        expenses.forEach((expense, index) => {
            total += parseFloat(expense.amount);

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${expense.date}</td>
                <td>${expense.category}</td>
                <td>${expense.description || "-"}</td>
                <td>${expense.amount} zł</td>
                <td><button class="delete-btn" data-index="${index}">Usuń</button></td>
            `;

            table.appendChild(row);
        });

        totalAmount.textContent = total.toFixed(2);
    }

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const newExpense = {
            amount: document.getElementById("amount").value,
            date: document.getElementById("date").value,
            category: document.getElementById("category").value,
            description: document.getElementById("description").value
        };

        expenses.push(newExpense);
        saveExpenses();
        renderExpenses();
        form.reset();
    });

    table.addEventListener("click", (e) => {
        if (e.target.classList.contains("delete-btn")) {
            const index = e.target.getAttribute("data-index");
            expenses.splice(index, 1);
            saveExpenses();
            renderExpenses();
        }
    });

    logoutBtn.addEventListener("click", () => {
        window.location.href = "/auth/logout";
    });

    renderExpenses();




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
        await getUserExpenses();
        return true;
    } else {
        return false;
    }

} catch (err) {
    console.error("Error fetching user info:", err);
}
}

    async function checkAuth() {
        try {
            const data = await checkMe();
            console.log("Auth check response:", data);
            if (!data) {
                window.location.href = "/";
            } 

        } catch (e) {
            console.error("Error during auth check:", e);
            window.location.href = "/";
        } 
    }

async function getUserExpenses(page = 1) {
    try {
        const response = await fetch(
            `/api/v1/dashboard/get_expenses?page=${page}&size=10`,
            { credentials: "include" }
        );

        if (!response.ok) {
            throw new Error("Failed to fetch expenses");
        }

        const data = await response.json();

        // 🔥 PODMIENIASZ lokalną listę
        expenses = data.items;

        renderExpenses();

    } catch (err) {
        console.error("Error fetching expenses:", err);
    }
}

});

