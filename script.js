async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  const message = input.value.trim();
  if (!message) return;

  // Display user's message
  chatBox.innerHTML += `<div class="user-msg">${message}</div>`;
  input.value = "";

  // Auto-scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }), // ✅ matches backend
    });

    if (!res.ok) throw new Error("Network error");

    const data = await res.json();

    // Display bot response
    chatBox.innerHTML += `<div class="bot-msg">${data.reply}</div>`;

    // Auto-scroll again
    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (error) {
    chatBox.innerHTML += `<div class="bot-msg error">⚠️ Something went wrong. Please try again.</div>`;
  }
}

// Send message when user presses Enter
document.getElementById("user-input").addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});
