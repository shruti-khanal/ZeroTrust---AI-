const form = document.getElementById("accessForm");


if (form) {

    form.addEventListener("submit", async function(event) {

        event.preventDefault();


        // Collect form data

        const data = {

            userId:
                document.getElementById("userId").value,

            department:
                document.getElementById("department").value,

            role:
                document.getElementById("role").value,

            device:
                document.getElementById("device").value,

            os:
                document.getElementById("os").value,

            resource:
                document.getElementById("resource").value,

            sensitivity:
                document.getElementById("sensitivity").value,

            loginTime:
                document.getElementById("loginTime").value,

            failedAttempts:
                Number(
                    document.getElementById("failedAttempts").value
                ),

            activity:
                document.getElementById("activity").value,

            location:
                document.getElementById("location").value

        };


        try {

            // Send data to Python backend

            const response = await fetch(
                "http://127.0.0.1:5000/analyze",
                {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(data)

                }
            );


            // Convert response to JSON

            const result =
                await response.json();


            console.log("Backend response:", result);


            // Combine original data with result

            const finalResult = {

                ...data,

                riskScore: result.riskScore,

                riskLevel: result.riskLevel,

                decision: result.decision

            };


            // Store result

            localStorage.setItem(
                "riskResult",
                JSON.stringify(finalResult)
            );


            // Open dashboard

            window.location.href =
                "dashboard.html";


        } catch (error) {

            console.error(
                "Backend connection error:",
                error
            );


            alert(
                "Unable to connect to ZeroTrust AI server."
            );

        }

    });

}