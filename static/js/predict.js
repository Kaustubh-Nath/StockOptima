// StockOptima Prediction Form JS Helper
document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("predictionForm");
    const loadingOverlay = document.getElementById("loadingOverlay");

    if (form) {
        form.addEventListener("submit", function(e) {
            // Show the futuristic glassmorphic spinner overlay
            loadingOverlay.style.display = "flex";
            
            // Optionally, customize loading messages dynamically for flavor
            const messages = [
                "ML ENGINE RUNNING PREDICTIONS...",
                "SCALING INPUT FEATURES...",
                "EVALUATING DEMAND CORRELATIONS...",
                "CALCULATING STOCK ACTION REQS..."
            ];
            
            let messageIndex = 0;
            const textElement = loadingOverlay.querySelector(".loading-text");
            
            const interval = setInterval(() => {
                messageIndex = (messageIndex + 1) % messages.length;
                if (textElement) {
                    textElement.textContent = messages[messageIndex];
                }
            }, 600);
            
            // Let the form submit naturally
            // The loading overlay will block interactions until the new page loads.
        });
    }
});
