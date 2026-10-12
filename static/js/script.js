/*==========================================================
        AI QUESTION PAPER GENERATOR
        Premium Login Script
        MANTRALOOK WORLD
==========================================================*/

document.addEventListener("DOMContentLoaded", function () {

    /*======================================================
                    PASSWORD TOGGLE
    ======================================================*/

    const passwordInput = document.getElementById("password");

    const togglePassword = document.getElementById("togglePassword");

    if (passwordInput && togglePassword) {

        togglePassword.addEventListener("click", function () {

            if (passwordInput.type === "password") {

                passwordInput.type = "text";

                this.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';

            } else {

                passwordInput.type = "password";

                this.innerHTML = '<i class="fa-solid fa-eye"></i>';

            }

        });

    }

    /*======================================================
                    INPUT ANIMATION
    ======================================================*/

    const inputs = document.querySelectorAll(".input-box input");

    inputs.forEach(input => {

        input.addEventListener("focus", function () {

            this.parentElement.style.transform = "scale(1.02)";

        });

        input.addEventListener("blur", function () {

            this.parentElement.style.transform = "scale(1)";

        });

    });

    /*======================================================
                    LOGIN CARD FADE
    ======================================================*/

    const loginCard = document.querySelector(".login-card");

    if (loginCard) {

        loginCard.style.opacity = "0";

        loginCard.style.transform = "translateY(40px)";

        setTimeout(() => {

            loginCard.style.transition = "all .8s ease";

            loginCard.style.opacity = "1";

            loginCard.style.transform = "translateY(0)";

        }, 200);

    }

    /*======================================================
                    ROBOT HOVER EFFECT
    ======================================================*/

    const robot = document.querySelector(".robot");

    if (robot) {

        robot.addEventListener("mouseenter", function () {

            robot.style.transform = "scale(1.05)";

        });

        robot.addEventListener("mouseleave", function () {

            robot.style.transform = "scale(1)";

        });

    }
    /*======================================================
                    LOGIN BUTTON LOADING
    ======================================================*/

    const loginForm = document.querySelector("form");

    const loginButton = document.querySelector(".login-btn");

    if (loginForm && loginButton) {

        loginForm.addEventListener("submit", function () {

            loginButton.disabled = true;

            loginButton.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Signing In...';

        });

    }

    /*======================================================
                    AUTO HIDE ALERT
    ======================================================*/

    const alertBox = document.querySelector(".alert");

    if (alertBox) {

        setTimeout(() => {

            alertBox.style.transition = "all .5s ease";

            alertBox.style.opacity = "0";

            alertBox.style.transform = "translateY(-15px)";

            setTimeout(() => {

                alertBox.remove();

            }, 500);

        }, 4000);

    }

    /*======================================================
                    LOGIN CARD TILT EFFECT
    ======================================================*/

    if (loginCard) {

        loginCard.addEventListener("mousemove", function (e) {

            const rect = loginCard.getBoundingClientRect();

            const x = e.clientX - rect.left;

            const y = e.clientY - rect.top;

            const rotateX = ((y / rect.height) - 0.5) * -8;

            const rotateY = ((x / rect.width) - 0.5) * 8;

            loginCard.style.transform =
                `perspective(1000px)
                 rotateX(${rotateX}deg)
                 rotateY(${rotateY}deg)`;

        });

        loginCard.addEventListener("mouseleave", function () {

            loginCard.style.transform =
                "perspective(1000px) rotateX(0deg) rotateY(0deg)";

        });

    }

    /*======================================================
                    ENTER KEY SUPPORT
    ======================================================*/

    document.addEventListener("keydown", function (event) {

        if (event.key === "Enter" && loginForm) {

            loginForm.requestSubmit();

        }

    });

    /*======================================================
                    CONSOLE BRANDING
    ======================================================*/

    console.clear();

    console.log(
        "%cAI Question Paper Generator",
        "color:#D4AF37;font-size:20px;font-weight:bold;"
    );

    console.log(
        "%cDeveloped by MANTRALOOK WORLD",
        "color:#ffffff;font-size:14px;"
    );

});   // DOMContentLoaded Ends

/*==========================================================
                    SCRIPT LOADED
==========================================================*/

console.log(
    "%cScript Loaded Successfully ✔",
    "color:lime;font-size:15px;font-weight:bold;"
);


// Navigate one step back inside the application.
// If the page was opened directly, fall back to the supplied app URL.
function goBackInApp(event, fallbackUrl) {
    event.preventDefault();

    const referrer = document.referrer;
    const sameOrigin = referrer && new URL(referrer, window.location.origin).origin === window.location.origin;

    if (sameOrigin && window.history.length > 1) {
        window.history.back();
    } else {
        window.location.href = fallbackUrl;
    }
}
