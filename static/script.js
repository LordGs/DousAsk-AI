document.getElementById("user-input").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {
    let userInputField = document.getElementById("user-input");
    let userInput = userInputField.value.trim();
    if (!userInput) return;

    let chatBox = document.getElementById("chat-box");

    // Display user's message
    let userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);

    // Display loading message
    let loadingMessage = document.createElement("div");
    loadingMessage.className = "bot-message loading";
    loadingMessage.textContent = "Typing...";
    chatBox.appendChild(loadingMessage);
    
    // Smooth scroll to bottom after user message
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });

    // Send API request to Flask
    fetch("https://dousask.onrender.com/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // Replace newlines with <br> for proper rendering
        loadingMessage.classList.remove("loading");
        loadingMessage.innerHTML = data.answer.replace(/\n/g, "<br>");

        // Smooth scroll to bottom after bot response
        setTimeout(() => {
            chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });
        }, 100);
    })
    .catch(error => {
        console.error("Error:", error);
        loadingMessage.classList.remove("loading");
        loadingMessage.textContent = "Sorry, an error occurred.";
    });

    // Clear input and keep focus
    userInputField.value = "";
    userInputField.focus();
}



function toggleSidebar() {
    var sidebar = document.querySelector('.sidebar');
    var mainContent = document.querySelector('.main-content');
    var topbar = document.querySelector('.topbar');

    //variables
    var sidebarWidth = getComputedStyle(document.documentElement).getPropertyValue('--sidebar-width').trim() || '300px';

    sidebar.classList.toggle('active');

    if (sidebar.classList.contains('active')) {
        mainContent.style.marginLeft = sidebarWidth;
        mainContent.style.width = `calc(100% - ${sidebarWidth})`;
        topbar.style.marginLeft = sidebarWidth;
    } else {
        mainContent.style.marginLeft = '0';
        mainContent.style.width = '100%';
        topbar.style.marginLeft = '0';
    }
}

