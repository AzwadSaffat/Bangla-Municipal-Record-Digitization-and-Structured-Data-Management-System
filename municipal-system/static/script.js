// Minimal UI interactions can be extended later for richer workflows.
document.addEventListener('DOMContentLoaded', () => {
  const flashMessages = document.querySelectorAll('[data-auto-dismiss]');
  flashMessages.forEach((el) => setTimeout(() => el.remove(), 4000));
});
