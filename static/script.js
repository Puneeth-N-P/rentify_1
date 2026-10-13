const locationData = {

    "Karnataka": {

        "Bangalore": [
            "Whitefield",
            "Electronic City",
            "Marathahalli",
            "HSR Layout",
            "Koramangala",
            "Indiranagar",
            "Jayanagar"
        ],

        "Mysore": [
            "Vijayanagar",
            "Kuvempunagar",
            "Hebbal",
            "Saraswathipuram",
            "Jayalakshmipuram"
        ]

    },


    "Tamil Nadu": {

        "Chennai": [
            "Velachery",
            "T Nagar",
            "Adyar",
            "Anna Nagar",
            "Tambaram"
        ]

    },


    "Maharashtra": {

        "Mumbai": [
            "Andheri",
            "Bandra",
            "Powai",
            "Thane",
            "Borivali"
        ]

    },


    "Kerala": {

        "Ernakulam": [
            "Kakkanad",
            "Edappally",
            "Aluva",
            "Vyttila"
        ]

    },


    "Telangana": {

        "Hyderabad": [
            "Gachibowli",
            "Madhapur",
            "Kondapur",
            "Hitech City",
            "Banjara Hills"
        ]

    }

};


const stateSelect =
    document.getElementById("state");

const districtSelect =
    document.getElementById("district");

const locationSelect =
    document.getElementById("location");


/* ================= STATE CHANGE ================= */

stateSelect.addEventListener("change", function () {

    const state = this.value;

    districtSelect.innerHTML =
        '<option value="">Select District</option>';

    locationSelect.innerHTML =
        '<option value="">Select Location</option>';


    if (state && locationData[state]) {

        const districts =
            Object.keys(locationData[state]);


        districts.forEach(function (district) {

            const option =
                document.createElement("option");

            option.value = district;

            option.textContent = district;

            districtSelect.appendChild(option);

        });

    }

});


/* ================= DISTRICT CHANGE ================= */

districtSelect.addEventListener("change", function () {

    const state = stateSelect.value;

    const district = this.value;

    locationSelect.innerHTML =
        '<option value="">Select Location</option>';


    if (
        state &&
        district &&
        locationData[state] &&
        locationData[state][district]
    ) {

        const locations =
            locationData[state][district];


        locations.forEach(function (location) {

            const option =
                document.createElement("option");

            option.value = location;

            option.textContent = location;

            locationSelect.appendChild(option);

        });

    }

});


/* ================= SCROLL ================= */

function scrollToSearch() {

    document
        .getElementById("search")
        .scrollIntoView({
            behavior: "smooth"
        });

}


/* ================= LOCATION CARDS ================= */

function selectLocation(state) {

    scrollToSearch();

    setTimeout(function () {

        stateSelect.value = state;

        stateSelect.dispatchEvent(
            new Event("change")
        );

    }, 500);

}