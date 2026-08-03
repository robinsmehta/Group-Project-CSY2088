// js/config.js — API Configuration
//
// This file defines the base URL for all API calls.
// Every other JS file imports this constant so that if the
// backend port or domain ever changes, you only need to
// update it in ONE place — right here.

// The base URL for all backend API requests.
// This project is intended to run through the Flask server on 127.0.0.1:5001.
// The frontend is served from the same origin, so session cookies can be
// same-site and authenticated requests will work correctly.
const API_BASE_URL = "http://127.0.0.1:5001/api";

