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

// "Summarizing..."
window.addEventListener("load", () => {
  const processForm = document.getElementById('process_form');
  const loadingSummary = document.getElementById('loading_summary');
  let clickedButton = null;

  // Track which button was clicked
  document.querySelectorAll("#process_form button[type='submit']").forEach(button => {
    button.addEventListener("click", event => {
      clickedButton = event.target;
    });
  });

  processForm.addEventListener("submit", event => {
    const selected = processForm.querySelectorAll("input[name='selected_articles']:checked");

    if (selected.length === 0) {
      return;
    }
    
    if (clickedButton && clickedButton.value === "summarize") {
      const confirmed = confirm("Are you sure you want to summarize the selected articles?");
      if (!confirmed) {
        event.preventDefault();
        return;
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
      loadingSummary.style.display = "block";
    } else if (clickedButton && clickedButton.value === "blog") {
      // Another confirmation and loader for blog post
    }
  });
});
