def get_doctors(city):

    doctors = {

        "Pune": [

            {
                "name": "Dr. Priya Sharma",
                "specialist": "Hematologist",
                "hospital": "Ruby Hall Clinic",
                "phone": "+91 9876543210",
                "address": "Sassoon Road, Pune"
            },

            {
                "name": "Dr. Amit Kulkarni",
                "specialist": "Blood Specialist",
                "hospital": "Jehangir Hospital",
                "phone": "+91 9123456780",
                "address": "Bund Garden, Pune"
            }
        ],

        "Mumbai": [

            {
                "name": "Dr. Neha Verma",
                "specialist": "Hematologist",
                "hospital": "Lilavati Hospital",
                "phone": "+91 9988776655",
                "address": "Bandra West, Mumbai"
            }
        ],

        "Bangalore": [

            {
                "name": "Dr. Rahul Shetty",
                "specialist": "Blood Specialist",
                "hospital": "Manipal Hospital",
                "phone": "+91 9876501234",
                "address": "Old Airport Road, Bangalore"
            }
        ]
    }

    return doctors.get(city, [
        {
            "name": "Dr. Default",
            "specialist": "General Physician",
            "hospital": "City Hospital",
            "phone": "+91 9000000000",
            "address": city
        }
    ])