let tasks = JSON.parse(localStorage.getItem("tasks")) || [];
let currentFilter = "all";

const taskInput = document.getElementById("taskInput");
const priority = document.getElementById("priority");
const taskList = document.getElementById("taskList");
const totalCount = document.getElementById("totalCount");
const pendingCount = document.getElementById("pendingCount");

document.getElementById("addBtn").addEventListener("click", addTask);

renderTasks();

function addTask() {

    const title = taskInput.value.trim();

    if(title === ""){
        alert("Enter task");
        return;
    }

    const task = {
        id: Date.now(),
        title: title,
        priority: priority.value,
        completed:false,
        date:new Date().toLocaleDateString()
    };

    tasks.push(task);

    saveTasks();

    taskInput.value="";

    renderTasks();
}

function renderTasks(){

    taskList.innerHTML="";

    let filtered = tasks;

    if(currentFilter==="pending"){
        filtered = tasks.filter(task=>!task.completed);
    }

    if(currentFilter==="completed"){
        filtered = tasks.filter(task=>task.completed);
    }

    filtered.forEach(task=>{

        const div=document.createElement("div");

        div.className="task";

        if(task.completed){
            div.classList.add("completed");
        }

        div.innerHTML=`
        <div class="left">

            <input type="checkbox"
            ${task.completed?"checked":""}
            onchange="toggleTask(${task.id})">

            <div>
                <span>${task.title}</span><br>

                <small class="date">${task.date}</small>
            </div>

            <span class="badge ${task.priority.toLowerCase()}">
            ${task.priority}
            </span>

        </div>

        <button class="deleteBtn"
        onclick="deleteTask(${task.id})">
        Delete
        </button>
        `;

        taskList.appendChild(div);

    });

    updateCounter();

}

function toggleTask(id){

    tasks = tasks.map(task=>{

        if(task.id===id){
            task.completed=!task.completed;
        }

        return task;

    });

    saveTasks();

    renderTasks();

}

function deleteTask(id){

    tasks = tasks.filter(task=>task.id!==id);

    saveTasks();

    renderTasks();

}

function filterTasks(type){

    currentFilter=type;

    renderTasks();

}

function updateCounter(){

    totalCount.textContent=tasks.length;

    pendingCount.textContent=tasks.filter(task=>!task.completed).length;

}

function saveTasks(){

    localStorage.setItem("tasks",JSON.stringify(tasks));

}