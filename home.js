// JavaScript Document
// Form Submission Alert
function addFormSubmissionAlert() {
  var form = document.querySelector('#contactForm form');
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Thanks for reaching out! We will get back to you shortly.');
    form.reset();
  });
}

// Cancel Button Confirmation
function cancelForm() {
  var confirmation = confirm('Are you sure you want to cancel? Your input will be lost.');
  if (confirmation) {
    document.querySelector('#contactForm form').reset();
  }
}

function attachCancelConfirmation() {
  var cancelButton = document.querySelector('#contactForm button[type="button"]');
  cancelButton.addEventListener('click', cancelForm);
}

// Table Row Highlighting
function addTableRowHighlighting() {
  var rows = document.querySelectorAll('#portfolioTable tr:not(:first-child)'); 
  rows.forEach(function(row) {
    row.addEventListener('mouseenter', function() {
      row.style.backgroundColor = '#f0f0f0';  
    });
    row.addEventListener('mouseleave', function() {
      row.style.backgroundColor = ''; 
    });
  });
}

// Initialization function to run all the scripts
function init() {
  addFormSubmissionAlert();
  attachCancelConfirmation();
  addTableRowHighlighting();
}

// Run the init function when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', init);
