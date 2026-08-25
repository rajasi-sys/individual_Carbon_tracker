import { api } from "../api.js";

function renderVirtualForest(statsData) {
    if (!statsData) return;

    // The backend might nest gamification fields or return them flat.
    const gameData = statsData.gamification || statsData;

    const {
        xp = 0,
        level = 1,
        streak_count = 0,
        // /emissions/lock-daily uses tree_stage + no icon at top level; /user/stats has tree_icon
        tree_stage = 1,
        tree_icon = "🌱"
    } = gameData;

    const treeIconEl = document.getElementById("treeIcon");
    if (treeIconEl) treeIconEl.textContent = tree_icon;

    const treeStageLabelEl = document.getElementById("treeStageLabel");
    if (treeStageLabelEl) treeStageLabelEl.textContent = `Stage ${tree_stage}: ${tree_icon}`;

    const streakCountEl = document.getElementById("streakCount");
    if (streakCountEl) streakCountEl.textContent = streak_count;

    const userXpEl = document.getElementById("userXP");
    if (userXpEl) userXpEl.textContent = xp;

    const userLevelEl = document.getElementById("userLevel");
    if (userLevelEl) userLevelEl.textContent = level;

    const xpProgressBarEl = document.getElementById("xpProgressBar");
    if (xpProgressBarEl) {
        const progressPercent = ((xp % 500) / 500) * 100;
        xpProgressBarEl.style.width = `${progressPercent}%`;
    }

    // /user/stats returns 'badges'; normalize both possible keys
    const badgesList = gameData.badges || gameData.unlocked_badges;
    if (badgesList) {
        renderBadges(badgesList);
    }
}

async function fetchAndRenderLeaderboard() {
    const tableBody = document.getElementById("leaderboardTableBody");
    if (!tableBody) return;

    try {
        const users = await api.get("/leaderboard");
        tableBody.innerHTML = ""; // Clear existing table rows

        if (!users || users.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;">No leaderboard data available.</td></tr>`;
            return;
        }

        // Only iterate over the top 10 users
        const topUsers = users.slice(0, 10);

        topUsers.forEach((user, index) => {
            const rank = index + 1;
            const tr = document.createElement("tr");

            // Apply special highlight styling for top 3
            if (rank === 1) tr.classList.add("rank-gold");
            else if (rank === 2) tr.classList.add("rank-silver");
            else if (rank === 3) tr.classList.add("rank-bronze");

            const rankBadge = rank <= 3 ? `<strong>#${rank}</strong>` : `#${rank}`;
            const treeIcon = user.tree_icon || "🌱";
            const name = user.name || "EcoWarrior";
            const city = user.city || "Global";
            const xp = user.xp || 0;
            const level = user.level || 1;
            const streak = user.streak_count || 0;

            tr.innerHTML = `
                <td>${rankBadge}</td>
                <td style="font-size: 1.5rem;">${treeIcon}</td>
                <td>${name}</td>
                <td>${city}</td>
                <td>${xp} XP</td>
                <td>Lvl ${level}</td>
                <td>🔥 ${streak}</td>
            `;

            tableBody.appendChild(tr);
        });

    } catch (error) {
        console.error("Leaderboard Fetch Error:", error);
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:red;">Failed to load leaderboard.</td></tr>`;
    }
}

function renderBadges(badgesList) {
    const badgesContainer = document.getElementById("badgesContainer");
    if (!badgesContainer) return;

    badgesContainer.innerHTML = "";

    if (!badgesList || badgesList.length === 0) {
        badgesContainer.innerHTML = "<p>No badges unlocked yet. Keep logging to earn rewards!</p>";
        return;
    }

    badgesList.forEach(badge => {
        const card = document.createElement("div");
        card.className = "badge-card";
        
        let dateStr = "Recently";
        if (badge.unlocked_at) {
            try {
                dateStr = new Date(badge.unlocked_at).toLocaleDateString();
            } catch (e) {}
        }

        card.innerHTML = `
            <div class="badge-icon">${badge.icon || "🏅"}</div>
            <div class="badge-info">
                <h4>${badge.name || "Achievement Badge"}</h4>
                <p>${badge.description || "Earned for sustainable actions."}</p>
                <small>Unlocked: ${dateStr}</small>
            </div>
        `;

        badgesContainer.appendChild(card);
    });
}

function initForest() {
    // Initial fetch of the leaderboard
    fetchAndRenderLeaderboard();

    // Re-fetch and update when relevant events occur
    window.addEventListener("daily-entry-locked", (e) => {
        fetchAndRenderLeaderboard();
        if (e.detail) {
            // Normalize lock-daily field names to match /user/stats shape
            const lockData = e.detail;
            const normalized = {
                ...lockData,
                xp: lockData.total_xp ?? lockData.xp ?? 0,
                streak_count: lockData.streak_days ?? lockData.streak_count ?? 0,
            };
            renderVirtualForest(normalized);
        }
    });

    window.addEventListener("user-logged-in", async () => {
        fetchAndRenderLeaderboard();
        try {
            const data = await api.get("/user/stats");
            renderVirtualForest(data);
        } catch(e) {
            console.error("Failed to fetch user stats on login for forest UI:", e);
        }
    });

    window.addEventListener("profile-updated", async () => {
        fetchAndRenderLeaderboard();
        try {
            const data = await api.get("/user/stats");
            renderVirtualForest(data);
        } catch(e) {
            console.error("Failed to fetch user stats on profile update:", e);
        }
    });
}

export { initForest, renderVirtualForest, fetchAndRenderLeaderboard, renderBadges };
