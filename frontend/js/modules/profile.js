import { api } from "../api.js";

// Dynamic Currency Mapping
const CITY_CURRENCY_MAP = {
    "Mumbai": "₹",
    "Delhi": "₹",
    "London": "£",
    "New York": "$",
    "Default": "₹"
};

function getCurrencySymbol(cityName) {
    return CITY_CURRENCY_MAP[cityName] || CITY_CURRENCY_MAP["Default"];
}

// Demographic Profile Handler
async function handleSaveProfile() {
    const name = document.getElementById("profName")?.value;
    const age = document.getElementById("profAge")?.value;
    const gender = document.getElementById("profGender")?.value;
    const city = document.getElementById("profCity")?.value;
    const household = document.getElementById("profHousehold")?.value;

    const payload = {
        name: name,
        age: parseInt(age, 10),
        gender: gender,
        city: city,
        household_size: parseInt(household, 10)
    };

    try {
        await api.post("/user/profile", payload);
        alert("Profile updated successfully!");

        // Update global UI currency symbols across all cost display elements
        const symbol = getCurrencySymbol(city);
        const currencyElements = document.querySelectorAll(".currency-symbol");
        currencyElements.forEach(el => {
            el.textContent = symbol;
        });

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent("profile-updated", {
            detail: { city: city, currencySymbol: symbol }
        }));

    } catch (error) {
        console.error("Save Profile Error:", error);
        alert("Failed to update profile: " + error.message);
    }
}

// Utility Bill Upload Handler
async function handleUploadBill() {
    const fileInput = document.getElementById("billFile");
    
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert("Please select a bill image/PDF first.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
        await api.upload("/user/upload-bill", formData);
        alert("Bill uploaded successfully!");
    } catch (error) {
        console.error("Upload Bill Error:", error);
        alert("Failed to upload bill: " + error.message);
    }
}

// Module Initialization
function initProfile() {
    const saveProfileBtn = document.getElementById("saveProfileBtn");
    const uploadBillBtn = document.getElementById("uploadBillBtn");

    if (saveProfileBtn) {
        saveProfileBtn.addEventListener("click", (e) => {
            e.preventDefault();
            handleSaveProfile();
        });
    }

    if (uploadBillBtn) {
        uploadBillBtn.addEventListener("click", (e) => {
            e.preventDefault();
            handleUploadBill();
        });
    }
}

export { initProfile, handleSaveProfile, handleUploadBill, getCurrencySymbol };
