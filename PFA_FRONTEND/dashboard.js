document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("expenseForm");
    const table = document.getElementById("expensesTable");
    const totalAmount = document.getElementById("totalAmount");
    const logoutBtn = document.getElementById("logoutBtn");
    const previousPageBtn = document.getElementById("previousPageBtn");
    const nextPageBtn = document.getElementById("nextPageBtn");
    const pageCounter = document.getElementById("pageCounter")

    let expenses = [];
    let currentPage = 1;
    let totalPages = 1;

    let chartInstance = null;

    checkAuth();
    loadCategories();

    function saveExpenses() {
        localStorage.setItem("expenses", JSON.stringify(expenses));
    }

    function renderExpenses() {
        table.innerHTML = "";
        let total = 0;
        pageCounter.textContent = `${currentPage} / ${totalPages}`

        expenses.forEach((expense, index) => {
            total += parseFloat(expense.amount);

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${expense.expense_category.name}</td>
                <td>${expense.description || "-"}</td>
                <td>${expense.amount} zł</td>
                <td>${new Date(expense.date).toLocaleDateString("pl-PL")}</td>
                <td>
                    <button class="delete-btn" data-id="${expense.id}">
                        Usuń
                    </button>
                </td>
            `;

            table.appendChild(row);
        });

        totalAmount.textContent = total.toFixed(2);
    }

    table.addEventListener("click", async (e) => {
        if (e.target.classList.contains("delete-btn")) {

            const expenseId = e.target.dataset.id;

            try {
                const response = await fetch(
                    `/api/v1/dashboard/delete_expense/${expenseId}`,
                    {
                        method: "DELETE",
                        credentials: "include"
                    }
                );

                if (!response.ok) {
                    throw new Error("Błąd usuwania");
                }
                
                await getUserExpenses(currentPage);

            } catch (err) {
                console.error(err);
            }
        }
    });


    logoutBtn.addEventListener("click", () => {
        window.location.href = "/auth/logout";
    });


    nextPageBtn.addEventListener("click", () => {
        getUserExpenses(currentPage + 1)
    })
    previousPageBtn.addEventListener("click", () => {
        if (currentPage > 1) {
            getUserExpenses(currentPage - 1)
        }
    })

    async function deleteExpense(expenseId) {
        try {
            const response = await fetch(`/api/v1/delete_expense/${expenseId}`, {
                method: 'DELETE',
                headers: { "Content-Type": "application/json" }
            })
            if (!response.ok) {
                throw new Error("Błąd przy usuwaniu");
            }

            console.log("Usunięto");
            renderExpenses()

        } catch (err) {
            console.log('eror {}', err)
        }
    }

    async function checkMe() {
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
                `/api/v1/dashboard/get_expenses_page?page=${page}&size=10`,
                { credentials: "include" }
            );

            if (!response.ok) {
                throw new Error("Failed to fetch expenses");
            }

            const data = await response.json();
            expenses = data.items;

            if (expenses.length > 0) {
                currentPage = data.page;
                totalPages = data.total_pages;
                renderExpenses();
            }


        } catch (err) {
            console.error("Error fetching expenses:", err);
        }
    }



    async function getCategories() {
        try {
            response = await fetch("/api/v1/dashboard/get_expense_categories",
                { credentials: "include" });
            if (!response.ok) {
                throw new Error("Erorr")
            }
            return await response.json();

        } catch (err) {
            console.log(`popsulo sie: ${err}`)
        }
    }

    async function loadCategories() {
        const select = document.getElementById("category")
        const categories = await getCategories()
        categories.forEach(c => {
            const option = document.createElement("option");
            option.value = c.id
            option.textContent = c.name
            select.appendChild(option);
        })

        const chartSelect = document.getElementById("chartCategory");

        categories.forEach(c => {
            const option = document.createElement("option");
            option.value = c.id;
            option.textContent = c.name;
            chartSelect.appendChild(option);
        });
    }

    function getExpenseFormData() {
        const amount = parseFloat(document.getElementById("amount").value);
        const date = document.getElementById("date").value;
        const categoryId = parseInt(document.getElementById("category").value);
        const description = document.getElementById("description").value.trim();

        return {
            amount: amount,
            date: date,
            category_id: categoryId,
            description: description
        };
    }

    document.getElementById("expenseForm").addEventListener("submit", async (e) => {
        e.preventDefault();

        const expenseData = getExpenseFormData();
        console.log(expenseData)
        const response = await fetch("/api/v1/dashboard/add_expense", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify(expenseData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log("Backend error:", errorText);
            return;
        }

        console.log("Dodano wydatek");
    });

    async function loadChartData() {
        const categoryId = document.getElementById("chartCategory").value;
        const dateFrom = document.getElementById("chartDateFrom").value;
        const dateTo = document.getElementById("chartDateTo").value;

        const params = new URLSearchParams();

        if (categoryId) params.append("category_id", categoryId);
        if (dateFrom) params.append("date_from", dateFrom);
        if (dateTo) params.append("date_to", dateTo);

        const response = await fetch(
            `/api/v1/dashboard/dashboard_user_chart?${params.toString()}`,
            { credentials: "include" }
        );

        if (!response.ok) {
            console.error("Błąd pobierania wykresu");
            return;
        }

        const result = await response.json();
        renderChart(result.data);
    }


    function renderChart(data) {
        const ctx = document.getElementById("expensesChart").getContext("2d");

        const labels = data.map(item =>
            new Date(item.date).toLocaleDateString("pl-PL")
        );

        const values = data.map(item => item.amount);

        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Wydatki",
                    data: values,
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59,130,246,0.1)",
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: "#e5e7eb" }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: "#9ca3af" }
                    },
                    y: {
                        ticks: { color: "#9ca3af" }
                    }
                }
            }
        });
    }



    document.getElementById("loadChartBtn")
        .addEventListener("click", loadChartData);


});

