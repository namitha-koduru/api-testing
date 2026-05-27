const token =
    localStorage.getItem("token");


async function addTask() {

    const title =
        document.getElementById("title").value;

    const description =
        document.getElementById("description").value;

    const response = await fetch(
        "http://127.0.0.1:5000/api/tasks",
        {
            method: "POST",

            headers: {

                "Content-Type": "application/json",

                "Authorization":
                    `Bearer ${token}`
            },

            body: JSON.stringify({
                title,
                description
            })
        }
    );

    const data = await response.json();

    alert(data.message);

    getTasks();
}


async function getTasks() {

    const response = await fetch(
        "http://127.0.0.1:5000/api/tasks",
        {
            method: "GET",

            headers: {

                "Authorization":
                    `Bearer ${token}`
            }
        }
    );

    const tasks = await response.json();

    let output = "";

    tasks.forEach(task => {

        output += `

            <div>

                <h3>${task.title}</h3>

                <p>${task.description}</p>

                <p>Status: ${task.status}</p>

            </div>

            <hr>

        `;
    });

    document.getElementById("tasks").innerHTML =
        output;
}