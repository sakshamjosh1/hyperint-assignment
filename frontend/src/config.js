// src/config.js
// If VITE_API_BASE is set, use it; otherwise use empty string so requests are relative
export const API_BASE = import.meta.env.VITE_API_BASE || ''
