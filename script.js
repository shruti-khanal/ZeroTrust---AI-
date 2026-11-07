// ==================================================
// GLOBAL VARIABLES
// ==================================================

let currentUsername = "";

let currentLatitude = null;

let currentLongitude = null;

let currentAccuracy = null;


// ==================================================
// COURSE INFORMATION
// ==================================================

const courseData = {

    bca: {

        title:
            "BCA - Bachelor of Computer Applications",

        program:
            "Undergraduate Computer Applications Program",

        duration:
            "3 Years",

        subjects:
            "Programming, Data Structures, Database Management, Computer Networks, Web Development, Operating Systems and Artificial Intelligence",

        careers:
            "Software Developer, Web Developer, Database Administrator, Data Analyst, Cybersecurity Professional and IT Support",

        description:
            "BCA is an undergraduate program focused on computer applications, programming and information technology.",

        about:
            "The program develops programming and problem-solving skills and introduces students to modern areas of computing. GEU's Department of Computer Applications lists Bachelor of Computer Applications as a 3-year undergraduate program."

    },


    bba: {

        title:
            "BBA - Bachelor of Business Administration",

        program:
            "Undergraduate Management Program",

        duration:
            "Undergraduate Program",

        subjects:
            "Management, Marketing, Business Communication, Accounting, Economics, Human Resource Management and Business Strategy",

        careers:
            "Business Executive, Marketing Executive, HR Executive, Operations Executive, Entrepreneur and Management Trainee",

        description:
            "BBA is an undergraduate management program designed to develop business and management knowledge.",

        about:
            "The program focuses on business fundamentals and management practices. GEU's Department of Management Studies primarily hosts the Bachelor of Business Administration program."

    },


    mca: {

        title:
            "MCA - Master of Computer Applications",

        program:
            "Postgraduate Computer Applications Program",

        duration:
            "2 Years",

        subjects:
            "Full Stack Development, Computer Networks, Programming, Operating Systems, Advanced DBMS, Software Engineering, Data Structures and Artificial Intelligence",

        careers:
            "Software Developer, Full Stack Developer, Data Analyst, Cloud Professional, Software Engineer and IT Consultant",

        description:
            "MCA is a postgraduate program focused on advanced computer applications and software development.",

        about:
            "GEU's MCA curriculum includes areas such as Full Stack Development, Computer Networks, Programming, Advanced Operating Systems, Advanced Database Management Systems, Software Engineering and Data Structures."

    },


    mba: {

        title:
            "MBA - Master of Business Administration",

        program:
            "Postgraduate Management Program",

        duration:
            "2 Years",

        subjects:
            "Marketing, Finance, Human Resource Management, Business Strategy, Operations, Economics and Organizational Behaviour",

        careers:
            "Marketing Manager, Financial Analyst, HR Manager, Business Consultant, Operations Manager and Business Development Manager",

        description:
            "MBA is a postgraduate management program designed to develop business, leadership and decision-making skills.",

        about:
            "GEU's Department of Management Studies offers the MBA program and focuses on management education, research and industry-oriented learning."

    },


    bcom: {

        title:
            "B.Com - Bachelor of Commerce",

        program:
            "Undergraduate Commerce Program",

        duration:
            "Undergraduate Program",

        subjects:
            "Accounting, Economics, Business Law, Finance, Taxation, Management and Business Communication",

        careers:
            "Accountant, Financial Executive, Tax Assistant, Banking Professional, Business Executive and Finance Associate",

        description:
            "B.Com is an undergraduate commerce program focused on accounting, finance, business and commerce.",

        about:
            "Graphic Era offers commerce programs including Bachelor of Commerce and Bachelor of Commerce Honours variants."

    }

};


// ==================================================
// REGISTER
// ==================================================

document
    .getElementById("registerButton")
    .addEventListener(
        "click",
        async function () {

            const name =
                document
                    .getElementById("registerName")
                    .value
                    .trim();


            const username =
                document
                    .getElementById("registerUsername")
                    .value
                    .trim();


            const password =
                document
                    .getElementById("registerPassword")
                    .value;


            const response =
                await fetch(
                    "/register",
                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify({

                                name:
                                    name,

                                username:
                                    username,

                                password:
                                    password

                            })

                    }
                );


            const data =
                await response.json();


            document
                .getElementById("registerMessage")
                .textContent =
                    data.message;

        }
    );


// ==================================================
// LOGIN
// ==================================================

document
    .getElementById("loginButton")
    .addEventListener(
        "click",
        async function () {

            const username =
                document
                    .getElementById("loginUsername")
                    .value
                    .trim();


            const password =
                document
                    .getElementById("loginPassword")
                    .value;


            const response =
                await fetch(
                    "/login",
                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify({

                                username:
                                    username,

                                password:
                                    password

                            })

                    }
                );


            const data =
                await response.json();


            const attempts =
                data.failed_attempts || 0;


            document
                .getElementById(
                    "login-attempt-status"
                )
                .textContent =
                    "Failed login attempts: "
                    + attempts
                    + " / 3";


            document
                .getElementById(
                    "access-attempt-status"
                )
                .textContent =
                    "Failed login attempts: "
                    + attempts
                    + " / 3";


            if (data.blocked) {

                document
                    .getElementById(
                        "loginMessage"
                    )
                    .textContent =
                        data.message;

                return;
            }


            if (data.success) {

                currentUsername =
                    username;


                document
                    .getElementById(
                        "loginMessage"
                    )
                    .textContent =
                        "Login successful.";


                document
                    .getElementById(
                        "login-section"
                    )
                    .style
                    .display =
                        "none";


                document
                    .getElementById(
                        "register-section"
                    )
                    .style
                    .display =
                        "none";


                document
                    .getElementById(
                        "access-section"
                    )
                    .style
                    .display =
                        "block";


                return;
            }


            document
                .getElementById(
                    "loginMessage"
                )
                .textContent =
                    data.message
                    + " Failed attempts: "
                    + attempts
                    + " / 3";

        }
    );


// ==================================================
// LIVE LOCATION
// ==================================================

function getLiveLocation() {

    return new Promise(
        function (resolve) {

            const status =
                document
                    .getElementById(
                        "location-status"
                    );


            if (!navigator.geolocation) {

                status.textContent =
                    "Location is not supported by this browser.";

                resolve(false);

                return;
            }


            status.textContent =
                "Requesting current location...";


            navigator.geolocation.getCurrentPosition(

                function (position) {

                    currentLatitude =
                        position.coords.latitude;


                    currentLongitude =
                        position.coords.longitude;


                    currentAccuracy =
                        position.coords.accuracy;


                    status.textContent =
                        "Location captured successfully. "
                        + "Accuracy: "
                        + Math.round(
                            currentAccuracy
                        )
                        + " meters.";


                    resolve(true);

                },


                function () {

                    status.textContent =
                        "Location permission was not provided.";

                    resolve(false);

                },


                {

                    enableHighAccuracy:
                        true,

                    timeout:
                        10000,

                    maximumAge:
                        0

                }

            );

        }
    );
}


// ==================================================
// SHOW UNIVERSITY DASHBOARD
// ==================================================

function showUniversityDashboard() {

    document
        .getElementById(
            "access-section"
        )
        .style
        .display =
            "none";


    document
        .getElementById(
            "medium-verification-section"
        )
        .style
        .display =
            "none";


    document
        .getElementById(
            "university-dashboard"
        )
        .style
        .display =
            "block";


    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

}


// ==================================================
// REQUEST ACCESS
// ==================================================

document
    .getElementById("requestAccess")
    .addEventListener(
        "click",
        async function () {

            const resource =
                document
                    .getElementById(
                        "resource"
                    )
                    .value
                    .trim();


            const device =
                document
                    .getElementById(
                        "device"
                    )
                    .value;


            if (!resource) {

                document
                    .getElementById(
                        "result"
                    )
                    .textContent =
                        "Please enter a resource name.";

                return;
            }


            const locationAvailable =
                await getLiveLocation();


            if (!locationAvailable) {

                document
                    .getElementById(
                        "result"
                    )
                    .textContent =
                        "Access request stopped because location permission was not provided.";

                return;
            }


            const response =
                await fetch(
                    "/analyze-risk",
                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify({

                                username:
                                    currentUsername,

                                resource:
                                    resource,

                                device:
                                    device,

                                latitude:
                                    currentLatitude,

                                longitude:
                                    currentLongitude,

                                location_accuracy:
                                    currentAccuracy

                            })

                    }
                );


            const data =
                await response.json();


            if (
                data.login_attempts
                !== undefined
            ) {

                document
                    .getElementById(
                        "access-attempt-status"
                    )
                    .textContent =
                        "Failed login attempts: "
                        + data.login_attempts
                        + " / 3";

            }


            // ==================================================
            // MEDIUM RISK
            // ==================================================

            if (
                data.verification_required
            ) {

                document
                    .getElementById(
                        "access-section"
                    )
                    .style
                    .display =
                        "none";


                document
                    .getElementById(
                        "medium-verification-section"
                    )
                    .style
                    .display =
                        "block";


                document
                    .getElementById(
                        "medium-verification-message"
                    )
                    .textContent =
                        "Verification required. Enter the OTP.";


                alert(
                    "Demo Verification OTP: "
                    + data.demo_otp
                );


                return;
            }


            // ==================================================
            // LOW RISK
            // ==================================================

            if (
                data.risk === "LOW"
                &&
                data.decision === "ACCESS ALLOWED"
            ) {

                showUniversityDashboard();

                return;
            }


            // ==================================================
            // HIGH RISK
            // ==================================================

            const result =
                document
                    .getElementById(
                        "result"
                    );


            result.innerHTML =

                "<h3>Risk Analysis Result</h3>"

                + "<p><strong>Risk Level:</strong> "
                + data.risk
                + "</p>"

                + "<p><strong>Risk Score:</strong> "
                + data.risk_score
                + "</p>"

                + "<p><strong>Decision:</strong> "
                + data.decision
                + "</p>";


            if (data.alert_message) {

                result.innerHTML +=

                    "<p><strong>Alert:</strong> "
                    + data.alert_message
                    + "</p>";

            }

        }
    );


// ==================================================
// MEDIUM RISK OTP
// ==================================================

document
    .getElementById("verifyMediumOtp")
    .addEventListener(
        "click",
        async function () {

            const otp =
                document
                    .getElementById(
                        "mediumOtp"
                    )
                    .value
                    .trim();


            if (otp.length !== 6) {

                document
                    .getElementById(
                        "medium-verification-message"
                    )
                    .textContent =
                        "Please enter the 6-digit OTP.";

                return;
            }


            const response =
                await fetch(
                    "/verify-medium-risk",
                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify({

                                username:
                                    currentUsername,

                                otp:
                                    otp

                            })

                    }
                );


            const data =
                await response.json();


            const message =
                document
                    .getElementById(
                        "medium-verification-message"
                    );


            message.textContent =
                data.message;


            if (data.success) {

                message.textContent =
                    "✅ ACCESS GRANTED AFTER VERIFICATION";


                setTimeout(
                    function () {

                        showUniversityDashboard();

                    },
                    1000
                );

            }

        }
    );


// ==================================================
// COURSE CARD CLICK
// ==================================================

document
    .querySelectorAll(".course-card")
    .forEach(
        function (card) {

            card.addEventListener(
                "click",
                function () {

                    const course =
                        card.dataset.course;


                    openCourseDetails(
                        course
                    );

                }
            );

        }
    );


// ==================================================
// OPEN COURSE DETAILS
// ==================================================

function openCourseDetails(
    course
) {

    const data =
        courseData[course];


    if (!data) {

        return;
    }


    document
        .getElementById(
            "course-title"
        )
        .textContent =
            data.title;


    document
        .getElementById(
            "course-description"
        )
        .textContent =
            data.description;


    document
        .getElementById(
            "course-program"
        )
        .textContent =
            data.program;


    document
        .getElementById(
            "course-duration"
        )
        .textContent =
            data.duration;


    document
        .getElementById(
            "course-subjects"
        )
        .textContent =
            data.subjects;


    document
        .getElementById(
            "course-careers"
        )
        .textContent =
            data.careers;


    document
        .getElementById(
            "course-about"
        )
        .textContent =
            data.about;


    document
        .querySelector(
            ".course-grid"
        )
        .style
        .display =
            "none";


    document
        .getElementById(
            "course-details"
        )
        .style
        .display =
            "block";


    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

}


// ==================================================
// BACK TO COURSES
// ==================================================

document
    .getElementById(
        "backToCourses"
    )
    .addEventListener(
        "click",
        function () {

            document
                .getElementById(
                    "course-details"
                )
                .style
                .display =
                    "none";


            document
                .querySelector(
                    ".course-grid"
                )
                .style
                .display =
                    "grid";

        }
    );


// ==================================================
// SECURITY DASHBOARD
// ==================================================

document
    .getElementById("dashboardButton")
    .addEventListener(
        "click",
        async function () {

            const response =
                await fetch(
                    "/dsa-information"
                );


            const data =
                await response.json();


            document
                .getElementById(
                    "dashboard"
                )
                .style
                .display =
                    "block";


            document
                .getElementById(
                    "hashTable"
                )
                .textContent =
                    JSON.stringify(
                        data.data.users,
                        null,
                        2
                    );


            document
                .getElementById(
                    "accessGraph"
                )
                .textContent =
                    JSON.stringify(
                        data.data.access_graph,
                        null,
                        2
                    );


            document
                .getElementById(
                    "priorityQueue"
                )
                .textContent =
                    JSON.stringify(
                        data.data.priority_queue,
                        null,
                        2
                    );

        }
    );


// ==================================================
// SECURITY ALERTS
// ==================================================

document
    .getElementById("alertsButton")
    .addEventListener(
        "click",
        async function () {

            const response =
                await fetch(
                    "/security-alerts"
                );


            const data =
                await response.json();


            const container =
                document.getElementById(
                    "alerts"
                );


            container.innerHTML = "";


            if (
                data.alerts.length === 0
            ) {

                container.innerHTML =
                    "<p>No security alerts.</p>";

                return;
            }


            data.alerts.forEach(
                function (alert) {

                    const div =
                        document.createElement(
                            "div"
                        );


                    div.className =
                        "alert-card";


                    div.innerHTML =

                        "<strong>"
                        + alert.risk_level
                        + "</strong><br>"

                        + alert.alert_message
                        + "<br>"

                        + "User: "
                        + alert.username
                        + "<br>"

                        + "Resource: "
                        + alert.resource
                        + "<br>"

                        + "Score: "
                        + alert.risk_score;


                    container.appendChild(
                        div
                    );

                }
            );

        }
    );


// ==================================================
// ACCESS HISTORY
// ==================================================

document
    .getElementById("historyButton")
    .addEventListener(
        "click",
        async function () {

            const response =
                await fetch(
                    "/access-history"
                );


            const data =
                await response.json();


            const table =
                document.getElementById(
                    "historyTable"
                );


            table.innerHTML = "";


            data.history.forEach(
                function (item) {

                    const row =
                        document.createElement(
                            "tr"
                        );


                    row.innerHTML =

                        "<td>"
                        + item.username
                        + "</td>"

                        + "<td>"
                        + item.resource
                        + "</td>"

                        + "<td>"
                        + item.device
                        + "</td>"

                        + "<td>"
                        + item.login_attempts
                        + "</td>"

                        + "<td>"
                        + item.risk_level
                        + "</td>"

                        + "<td>"
                        + item.risk_score
                        + "</td>"

                        + "<td>"
                        + item.decision
                        + "</td>"

                        + "<td>"
                        + (
                            item.latitude
                            ?? "-"
                        )
                        + "</td>"

                        + "<td>"
                        + (
                            item.longitude
                            ?? "-"
                        )
                        + "</td>";


                    table.appendChild(
                        row
                    );

                }
            );

        }
    );
