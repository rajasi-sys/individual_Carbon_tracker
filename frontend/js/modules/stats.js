import { api } from "../api.js";
import { getCurrencySymbol } from "./profile.js";

function renderStats(data) {
    if (!data) return;

    // Normalize: /emissions/lock-daily uses total_emissions_kg_co2 and city_daily_avg_kg_co2
    // while /user/stats doesn't include these fields directly.
    const totalEmissions = data.total_emissions_kg_co2 ?? data.total_emissions ?? null;
    const cityAvg = data.city_daily_avg_kg_co2 ?? data.city_benchmark ?? null;

    // Total Daily Footprint
    const statTotalEmissions = document.getElementById("statTotalEmissions");
    if (statTotalEmissions && totalEmissions !== null) {
        statTotalEmissions.textContent = `${totalEmissions.toFixed(2)} kg CO2`;
    }

    // City Benchmark Comparison
    const statCityBenchmark = document.getElementById("statCityBenchmark");
    if (statCityBenchmark && totalEmissions !== null && cityAvg !== null) {
        const diff = totalEmissions - cityAvg;
        const diffText = diff > 0
            ? `${diff.toFixed(2)} kg above city avg`
            : `${Math.abs(diff).toFixed(2)} kg below city avg`;
        statCityBenchmark.textContent = diffText;
    }

    // Financial ROI Cards (only available from lock-daily response)
    if (data.financials) {
        const currencySymbol = getCurrencySymbol(data.city_name || "Default");

        const statMonthlySpend = document.getElementById("statMonthlySpend");
        if (statMonthlySpend) {
            statMonthlySpend.textContent = `${currencySymbol}${data.financials.monthly_spend || 0}`;
        }

        const statMonthlySavings = document.getElementById("statMonthlySavings");
        if (statMonthlySavings) {
            statMonthlySavings.textContent = `${currencySymbol}${data.financials.monthly_savings || 0}`;
        }

        const statYearlyROI = document.getElementById("statYearlyROI");
        if (statYearlyROI) {
            statYearlyROI.textContent = `${currencySymbol}${data.financials.yearly_roi || 0}`;
        }
    }

    // Activity Breakdown
    const breakdownContainer = document.getElementById("emissionsBreakdownContainer");
    if (breakdownContainer && data.breakdown) {
        breakdownContainer.innerHTML = "";
        for (const [sector, amount] of Object.entries(data.breakdown)) {
            const item = document.createElement("div");
            item.className = "breakdown-item";
            item.innerHTML = `<strong>${sector}:</strong> ${parseFloat(amount).toFixed(2)} kg CO2`;
            breakdownContainer.appendChild(item);
        }

        // Pass breakdown to solutions renderer
        renderSolutions(data.breakdown);
    }
}

function renderSolutions(breakdown) {
    const solutionsContainer = document.getElementById("solutionsContainer");
    if (!solutionsContainer) return;
    
    solutionsContainer.innerHTML = "";

    const alternatives = {
        electricity: "Switch to LED / Solar",
        car: "Switch to Electric Vehicle / Public Transit",
        flight: "Opt for train travel / offset emissions",
        lpg: "Use induction cooking / energy efficient appliances",
        meat: "Try plant-based meals",
        petrol: "Switch to Electric Vehicle / Public Transit",
        diesel: "Switch to Electric Vehicle / Public Transit",
        bus: "Walk or cycle for shorter distances"
    };

    for (const [sector, amount] of Object.entries(breakdown)) {
        if (parseFloat(amount) > 0) {
            // Find a matching actionable alternative
            let alternative = "Look for greener alternatives";
            for (const key of Object.keys(alternatives)) {
                if (sector.toLowerCase().includes(key)) {
                    alternative = alternatives[key];
                    break;
                }
            }

            const card = document.createElement("div");
            card.className = "solution-card side-by-side";
            // Render side-by-side comparison cards
            card.innerHTML = `
                <div class="solution-what-you-did">
                    <h4>What You Did</h4>
                    <p>${sector}: ${parseFloat(amount).toFixed(2)} kg CO2</p>
                </div>
                <div class="solution-what-you-can-do">
                    <h4>What You Can Do</h4>
                    <p>${alternative}</p>
                </div>
            `;
            solutionsContainer.appendChild(card);
        }
    }
}

async function refreshUserStats() {
    try {
        const data = await api.get("/user/stats");
        renderStats(data);
    } catch (error) {
        console.error("Failed to fetch user stats:", error);
    }
}

function initStats() {
    // Listen for emissions logged event
    window.addEventListener("daily-entry-locked", (e) => {
        if (e.detail) {
            renderStats(e.detail);
        }
    });

    // Listen for profile or auth updates to fetch fresh stats
    window.addEventListener("profile-updated", () => {
        refreshUserStats();
    });

    window.addEventListener("user-logged-in", () => {
        refreshUserStats();
    });
}

export { initStats, renderStats, refreshUserStats };
