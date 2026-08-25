import { api } from "../api.js";

const inputIds = [
    "logElec", 
    "logPetrol", 
    "logDiesel", 
    "logBus", 
    "logFlight", 
    "logLPG", 
    "logMeals"
];

function setupZeroEmissionToggle() {
    const zeroToggle = document.getElementById("zeroToggle");
    // Assuming there might be a badge with ID zeroBadge to highlight
    const zeroBadge = document.getElementById("zeroBadge"); 
    
    if (!zeroToggle) return;

    zeroToggle.addEventListener("change", (e) => {
        const isChecked = e.target.checked;

        inputIds.forEach(id => {
            const inputEl = document.getElementById(id);
            if (inputEl) {
                inputEl.disabled = isChecked;
                if (isChecked) {
                    inputEl.value = "0";
                }
            }
        });

        if (zeroBadge) {
            if (isChecked) {
                zeroBadge.classList.add("highlight"); 
                zeroBadge.style.display = "block"; // Example logic to highlight
            } else {
                zeroBadge.classList.remove("highlight");
            }
        }
    });
}

async function handleLockDaily() {
    const zeroToggle = document.getElementById("zeroToggle")?.checked || false;
    let logDate = document.getElementById("logDate")?.value;
    
    // Default to today (YYYY-MM-DD) if no date is provided
    if (!logDate) {
        logDate = new Date().toISOString().split("T")[0];
    }

    let payload = {
        date_str: logDate,
        is_zero_emission: zeroToggle,
    };

    if (zeroToggle) {
        payload.electricity_kwh = 0.0;
        payload.petrol_car_km = 0.0;
        payload.diesel_car_km = 0.0;
        payload.bus_km = 0.0;
        payload.flight_km = 0.0;
        payload.lpg_cylinder = 0.0;
        payload.meat_meals = 0;
    } else {
        const getFloatVal = (id) => {
            const val = document.getElementById(id)?.value;
            const parsed = parseFloat(val);
            return isNaN(parsed) ? 0.0 : parsed;
        };

        const getIntVal = (id) => {
            const val = document.getElementById(id)?.value;
            const parsed = parseInt(val, 10);
            return isNaN(parsed) ? 0 : parsed;
        };

        payload.electricity_kwh = getFloatVal("logElec");
        payload.petrol_car_km = getFloatVal("logPetrol");
        payload.diesel_car_km = getFloatVal("logDiesel");
        payload.bus_km = getFloatVal("logBus");
        payload.flight_km = getFloatVal("logFlight");
        payload.lpg_cylinder = getFloatVal("logLPG");
        payload.meat_meals = getIntVal("logMeals");
    }

    try {
        const responseData = await api.post("/emissions/lock-daily", payload);
        alert("Daily entry locked successfully!");

        // Dispatch custom event with the response payload
        window.dispatchEvent(new CustomEvent("daily-entry-locked", {
            detail: responseData
        }));

    } catch (error) {
        console.error("Lock Daily Error:", error);
        alert("Failed to lock daily entry: " + error.message);
    }
}

function initLogger() {
    setupZeroEmissionToggle();

    const lockDailyBtn = document.getElementById("lockDailyBtn");
    if (lockDailyBtn) {
        lockDailyBtn.addEventListener("click", (e) => {
            e.preventDefault();
            handleLockDaily();
        });
    }
}

export { initLogger, handleLockDaily, setupZeroEmissionToggle };
