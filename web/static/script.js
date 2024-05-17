// Your JavaScript code here

console.log("Initial orientation:", screen.orientation.type);

// Example to detect orientation changes
window.addEventListener("orientationchange", function() {
  console.log("Orientation changed to:", screen.orientation.type);
});
