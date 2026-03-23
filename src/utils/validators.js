function isValidEmail(email) {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}

function isValidPriority(priority) {
  return ["p0", "p1", "p2", "p3"].includes(priority);
}

function isValidStatus(status) {
  return ["todo", "in_progress", "review", "done"].includes(status);
}

function sanitizeString(str) {
  if (typeof str !== "string") return str;
  return str.trim().slice(0, 500);
}

module.exports = { isValidEmail, isValidPriority, isValidStatus, sanitizeString };
