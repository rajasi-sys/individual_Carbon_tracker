// ============================================================
// EcoQuest — Main Application Entry Point & Module Orchestrator
// ============================================================

// Module Imports
import { initAuth, updateAuthUI } from "./modules/auth.js";
import { initProfile } from "./modules/profile.js";
import { initLogger } from "./modules/logger.js";
import { initStats } from "./modules/stats.js";
import { initForest } from "./modules/forest.js";

// Section IDs corresponding to each dashboard tab
const TAB_SECTIONS = [
    "profileSection",
    "loggerSection",
    "statsSection",
    "forestSection"
];

/**
 * Switches the visible dashboard tab and updates active button styling.
 * @param {string} targetSectionId - The ID of the section to show.
 */
function switchTab(targetSectionId) {
    // Hide all dashboard tab sections
    TAB_SECTIONS.forEach(id => {
        const section = document.getElementById(id);
        if (section) section.classList.add("hidden");
    });

    // Show the selected tab section
    const target = document.getElementById(targetSectionId);
    if (target) target.classList.remove("hidden");

    // Update active styling on tab buttons
    document.querySelectorAll(".tab-btn").forEach(btn => {
        if (btn.getAttribute("data-tab") === targetSectionId) {
            btn.classList.add("bg-green-600", "text-white");
            btn.classList.remove("text-green-700");
        } else {
            btn.classList.remove("bg-green-600", "text-white");
            btn.classList.add("text-green-700");
        }
    });
}

/**
 * Attaches click listeners to all tab navigation buttons.
 */
function setupTabNavigation() {
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-tab");
            if (targetId) switchTab(targetId);
        });
    });
}

/**
 * Manages header-level UI elements that react to auth state changes
 * (logout button visibility, tab nav visibility).
 */
function setupAuthUIListeners() {
    const logoutBtn = document.getElementById("logoutBtn");
    const tabNav = document.getElementById("tabNav");

    window.addEventListener("user-logged-in", () => {
        if (logoutBtn) logoutBtn.classList.remove("hidden");
        if (tabNav) tabNav.classList.remove("hidden");
        // Default to the first tab on login
        switchTab("profileSection");
    });

    window.addEventListener("user-logged-out", () => {
        if (logoutBtn) logoutBtn.classList.add("hidden");
        if (tabNav) tabNav.classList.add("hidden");
    });
}

// ============================================================
// DOM Ready — Initialize All Modules
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize authentication (login, register, logout listeners)
    initAuth();

    // 2. Initialize profile onboarding and bill upload handlers
    initProfile();

    // 3. Initialize daily emissions logger and zero-emission toggle
    initLogger();

    // 4. Initialize analytics, ROI, and solution board listeners
    initStats();

    // 5. Initialize virtual forest, badges, and leaderboard
    initForest();

    // 6. Set up tab navigation switching
    setupTabNavigation();

    // 7. Set up auth-aware header UI listeners
    setupAuthUIListeners();

    // 8. Check current JWT token status and render the correct view
    updateAuthUI();

    // 9. Default the date picker to today's date
    const logDate = document.getElementById("logDate");
    if (logDate) {
        logDate.value = new Date().toISOString().split("T")[0];
    }

    console.log("🌱 EcoQuest initialized successfully.");
});
