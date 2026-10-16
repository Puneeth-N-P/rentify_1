// ================= SMOOTH SCROLL & SEARCH FOCUS =================
function scrollToSearch() {
    const searchSection = document.getElementById("search");
    if (searchSection) {
        searchSection.scrollIntoView({ behavior: "smooth" });
    }
}

function selectLocation(stateName, districtName = null) {
    const stateSelect = document.getElementById("state");
    const districtSelect = document.getElementById("district");

    if (stateSelect) {
        stateSelect.value = stateName;
        stateSelect.dispatchEvent(new Event('change', { bubbles: true }));

        if (districtName) {
            setTimeout(() => {
                if (districtSelect) {
                    districtSelect.value = districtName;
                    districtSelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }, 400);
        }

        scrollToSearch();
    }
}

// ================= DYNAMIC DROPDOWNS (STATE -> DISTRICT -> LOCATION) =================
document.addEventListener("DOMContentLoaded", () => {
    const stateSelect = document.getElementById("state");
    const districtSelect = document.getElementById("district");
    const locationSelect = document.getElementById("location");

    if (stateSelect) {
        stateSelect.addEventListener("change", function () {
            const selectedState = this.value;
            
            districtSelect.innerHTML = '<option value="">Select District</option>';
            locationSelect.innerHTML = '<option value="">Select Location</option>';

            if (!selectedState) return;

            fetch(`/get_districts/${encodeURIComponent(selectedState)}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(district => {
                        const option = document.createElement("option");
                        option.value = district;
                        option.textContent = district;
                        districtSelect.appendChild(option);
                    });
                })
                .catch(err => console.error("Error loading districts:", err));
        });
    }

    if (districtSelect) {
        districtSelect.addEventListener("change", function () {
            const selectedDistrict = this.value;
            
            locationSelect.innerHTML = '<option value="">Select Location</option>';

            if (!selectedDistrict) return;

            fetch(`/get_locations/${encodeURIComponent(selectedDistrict)}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(location => {
                        const option = document.createElement("option");
                        option.value = location;
                        option.textContent = location;
                        locationSelect.appendChild(option);
                    });
                })
                .catch(err => console.error("Error loading locations:", err));
        });
    }
});

// ================= HERO IMAGE AUTO-SLIDESHOW (2 SECONDS) =================
const heroImages = [
    "/static/images/house1.jpg",
    "/static/images/house2.jpg",
    "/static/images/house3.jpg",
    "/static/images/house4.jpg",
    "/static/images/house5.jpg",
    "/static/images/house6.jpg",
    "/static/images/house7.jpg",
    "/static/images/house8.jpg",
    "/static/images/house9.jpg",
    "/static/images/house10.jpg"
];

let currentHeroIndex = 0;
const heroImgElement = document.getElementById("hero-house-img");

if (heroImgElement) {
    setInterval(() => {
        currentHeroIndex = (currentHeroIndex + 1) % heroImages.length;
        heroImgElement.src = heroImages[currentHeroIndex];
    }, 2000);
}