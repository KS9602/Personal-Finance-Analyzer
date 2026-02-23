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

    checkAuth();


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
                <td>${expense.date}</td>
                <td>${expense.expense_category.name}</td>
                <td>${expense.description || "-"}</td>
                <td>${expense.amount} zł</td>
                <td>${expense.date} zł</td>
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


    nextPageBtn.addEventListener("click", () => {
        getUserExpenses(currentPage + 1)
    })
    previousPageBtn.addEventListener("click", () =>{
        if(currentPage > 1){
            getUserExpenses(currentPage - 1)
        }
    })


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
            `/api/v1/dashboard/get_expenses_page?page=${page}&size=10`,
            { credentials: "include" }
        );

        if (!response.ok) {
            throw new Error("Failed to fetch expenses");
        }

        const data = await response.json();

        // 🔥 PODMIENIASZ lokalną listę
        expenses = data.items;


        if(expenses.length > 0){
            currentPage = data.page;
            totalPages = data.total_pages;
            renderExpenses();
        }


    } catch (err) {
        console.error("Error fetching expenses:", err);
    }
}

async function addExpense(params) {
    
}


});

