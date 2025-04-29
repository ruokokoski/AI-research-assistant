const hideFlashMessage = () => {
  const flashMessages = document.getElementById("flash-messages");
  if (flashMessages) {
      setTimeout(() => {
          flashMessages.style.display = "none";
      }, 5000);
  }
}
window.addEventListener("load", hideFlashMessage);

// Hakuominaisuuden flash-message "Searching..."
window.addEventListener("load", () => {
  document.getElementById('search_form').onsubmit = () => {
      document.getElementById('loading_message').style.display = 'block';
  };
});