// ============================================================
// INTERN AI
// Website + Flask ML Recommendation Engine
// ============================================================

const API_URL = "";

// ============================================================
// LOCAL STORAGE
// ============================================================

function getProfile() {
    const data = localStorage.getItem("internAIProfile");

    if (!data) {
        return null;
    }

    try {
        return JSON.parse(data);
    } catch (error) {
        console.error("Profile data error:", error);
        return null;
    }
}


function saveProfile(profile) {
    localStorage.setItem(
        "internAIProfile",
        JSON.stringify(profile)
    );
}


function getRecommendations() {
    const data =
        localStorage.getItem(
            "internAIRecommendations"
        );

    if (!data) {
        return null;
    }

    try {
        return JSON.parse(data);
    } catch (error) {
        console.error(
            "Recommendation data error:",
            error
        );

        return null;
    }
}


function saveRecommendations(data) {
    localStorage.setItem(
        "internAIRecommendations",
        JSON.stringify(data)
    );
}


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ============================================================
// BACKEND API
// ============================================================

async function callRecommendationAPI(
    profile,
    filters = {}
) {

    const requestData = {

        student: {

            name: profile.name || "",

            skills: profile.skills || "",

            domain: profile.domain || "",

            location: profile.location || "",

            preferred_duration:
                profile.preferred_duration || "",

            min_stipend:
                Number(profile.min_stipend || 0)
        },

        search_query:
            filters.search_query || "",

        selected_domain:
            filters.selected_domain || "",

        selected_location:
            filters.selected_location || "",

        include_remote:
            filters.include_remote !== false,

        min_stipend:
            Number(filters.min_stipend || 0),

        preferred_duration:
            filters.preferred_duration || "",

        top_n: 10
    };


    console.log(
        "Sending recommendation request:"
    );

    console.log(requestData);


    const response = await fetch(
        `${API_URL}/api/recommend`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body:
                JSON.stringify(requestData)
        }
    );


    if (!response.ok) {

        throw new Error(
            `Backend error: ${response.status}`
        );
    }


    const data =
        await response.json();


    console.log(
        "Recommendation response:",
        data
    );


    return data;
}


// ============================================================
// LOGIN / SIGN UP
// ============================================================

function setupAuthentication() {

    const authForm =
        document.getElementById("auth");

    if (!authForm) {
        return;
    }


    const title =
        document.getElementById("title");

    const sub =
        document.getElementById("sub");

    const submit =
        document.getElementById("submit");

    const switchButton =
        document.getElementById("switch");

    const switchText =
        document.getElementById("switchText");

    const showPassword =
        document.getElementById("show");

    const password =
        document.getElementById("pw");


    let signupMode = false;


    // --------------------------------------------------------
    // CHECK URL
    // login.html?signup=1
    // --------------------------------------------------------

    const params =
        new URLSearchParams(
            window.location.search
        );


    if (
        params.get("signup") === "1"
    ) {

        signupMode = true;

        updateAuthUI();
    }


    // --------------------------------------------------------
    // SHOW / HIDE PASSWORD
    // --------------------------------------------------------

    if (showPassword) {

        showPassword.addEventListener(
            "click",
            function() {

                if (
                    password.type ===
                    "password"
                ) {

                    password.type =
                        "text";

                    showPassword.textContent =
                        "Hide";

                } else {

                    password.type =
                        "password";

                    showPassword.textContent =
                        "Show";
                }
            }
        );
    }


    // --------------------------------------------------------
    // LOGIN / SIGNUP SWITCH
    // --------------------------------------------------------

    if (switchButton) {

        switchButton.addEventListener(
            "click",
            function(event) {

                event.preventDefault();

                signupMode =
                    !signupMode;

                updateAuthUI();
            }
        );
    }


    // --------------------------------------------------------
    // UPDATE LOGIN UI
    // --------------------------------------------------------

    function updateAuthUI() {

        if (signupMode) {

            title.textContent =
                "Create your account";

            sub.textContent =
                "Create an account to start finding internships.";

            submit.textContent =
                "Create account →";

            switchText.textContent =
                "Already have an account?";

            switchButton.textContent =
                "Sign in";

        } else {

            title.textContent =
                "Welcome back";

            sub.textContent =
                "Sign in to continue to your recommendations.";

            submit.textContent =
                "Sign in →";

            switchText.textContent =
                "Don't have an account?";

            switchButton.textContent =
                "Create one";
        }
    }


    // --------------------------------------------------------
    // SUBMIT
    // --------------------------------------------------------

    authForm.addEventListener(
        "submit",
        function(event) {

            event.preventDefault();


            const emailInput =
                authForm.querySelector(
                    'input[type="email"]'
                );


            const email =
                emailInput.value.trim();


            const passwordValue =
                password.value.trim();


            if (!email ||
                !passwordValue) {

                alert(
                    "Please enter your email and password."
                );

                return;
            }


            // ------------------------------------------------
            // DEMO AUTHENTICATION
            // ------------------------------------------------

            /*
             * This is currently frontend/demo authentication.
             * We are not creating a real user database yet.
             *
             * The login state is stored locally so the website
             * can continue to the profile page.
             */

            localStorage.setItem(
                "internAILoggedIn",
                "true"
            );


            localStorage.setItem(
                "internAIEmail",
                email
            );


            // ------------------------------------------------
            // SIGNUP
            // ------------------------------------------------

            if (signupMode) {

                alert(
                    "Account created successfully!"
                );

            } else {

                console.log(
                    "User signed in:",
                    email
                );
            }


            // ------------------------------------------------
            // GO TO PROFILE
            // ------------------------------------------------

            window.location.href =
                "profile.html";
        }
    );
}


// ============================================================
// PROFILE PAGE
// ============================================================

function setupProfilePage() {

    const profileForm =
        document.getElementById("profile");

    if (!profileForm) {
        return;
    }


    const existingProfile =
        getProfile();


    // --------------------------------------------------------
    // Existing profile
    // --------------------------------------------------------

    if (existingProfile) {

        setField(
            profileForm,
            "name",
            existingProfile.name
        );

        setField(
            profileForm,
            "email",
            existingProfile.email
        );

        setField(
            profileForm,
            "education",
            existingProfile.education
        );

        setField(
            profileForm,
            "branch",
            existingProfile.branch
        );

        setField(
            profileForm,
            "experience",
            existingProfile.experience
        );

        setField(
            profileForm,
            "domain",
            existingProfile.domain
        );

        setField(
            profileForm,
            "skills",
            existingProfile.skills
        );

        setField(
            profileForm,
            "projects",
            existingProfile.projects
        );

        setField(
            profileForm,
            "certifications",
            existingProfile.certifications
        );

        setField(
            profileForm,
            "location",
            existingProfile.location
        );

        setField(
            profileForm,
            "duration",
            existingProfile.preferred_duration
        );

        setField(
            profileForm,
            "stipend",
            existingProfile.min_stipend
        );
    }


    // --------------------------------------------------------
    // Skill suggestion buttons
    // --------------------------------------------------------

    const suggestionButtons =
        document.querySelectorAll(
            ".suggestions button"
        );


    const skillsInput =
        profileForm.querySelector(
            '[name="skills"]'
        );


    suggestionButtons.forEach(
        function(button) {

            button.addEventListener(
                "click",
                function() {

                    if (!skillsInput) {
                        return;
                    }


                    let skill =
                        button.textContent
                            .replace("+", "")
                            .trim();


                    let current =
                        skillsInput.value
                            .trim();


                    if (!current) {

                        skillsInput.value =
                            skill;

                        return;
                    }


                    const existingSkills =
                        current
                            .split(",")
                            .map(
                                item =>
                                    item
                                        .trim()
                                        .toLowerCase()
                            );


                    if (
                        !existingSkills.includes(
                            skill.toLowerCase()
                        )
                    ) {

                        skillsInput.value =
                            current +
                            ", " +
                            skill;
                    }
                }
            );
        }
    );


    // --------------------------------------------------------
    // SAVE PROFILE
    // --------------------------------------------------------

    profileForm.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();


            const formData =
                new FormData(
                    profileForm
                );


            const profile = {

                name:
                    formData.get("name") ||
                    "",

                email:
                    formData.get("email") ||
                    localStorage.getItem(
                        "internAIEmail"
                    ) ||
                    "",

                education:
                    formData.get("education") ||
                    "",

                branch:
                    formData.get("branch") ||
                    "",

                experience:
                    formData.get("experience") ||
                    "",

                domain:
                    formData.get("domain") ||
                    "",

                skills:
                    formData.get("skills") ||
                    "",

                projects:
                    formData.get("projects") ||
                    "",

                certifications:
                    formData.get(
                        "certifications"
                    ) ||
                    "",

                location:
                    formData.get("location") ||
                    "",

                preferred_duration:
                    formData.get("duration") ||
                    "",

                min_stipend:
                    Number(
                        formData.get("stipend") ||
                        0
                    )
            };


            console.log(
                "Saving profile:",
                profile
            );


            saveProfile(profile);


            const savedMessage =
                document.getElementById(
                    "saved"
                );


            if (savedMessage) {

                savedMessage.textContent =
                    "Profile saved ✓";
            }


            // ------------------------------------------------
            // Ask ML backend for first recommendations
            // ------------------------------------------------

            try {

                const data =
                    await callRecommendationAPI(
                        profile,
                        {
                            search_query: "",

                            selected_domain:
                                profile.domain,

                            selected_location:
                                profile.location,

                            include_remote:
                                true,

                            min_stipend:
                                profile.min_stipend,

                            preferred_duration:
                                profile.preferred_duration
                        }
                    );


                saveRecommendations(
                    data
                );


                console.log(
                    "Initial recommendations saved."
                );


            } catch (error) {

                console.error(
                    "Could not get initial recommendations:",
                    error
                );

                /*
                 * Do not block the user from entering
                 * the dashboard if backend temporarily
                 * fails.
                 */
            }


            // ------------------------------------------------
            // Dashboard
            // ------------------------------------------------

            setTimeout(
                function() {

                    window.location.href =
                        "dashboard.html";

                },
                500
            );
        }
    );
}


// ============================================================
// FORM FIELD HELPER
// ============================================================

function setField(
    form,
    name,
    value
) {

    if (
        value === null ||
        value === undefined
    ) {
        return;
    }


    const field =
        form.querySelector(
            `[name="${name}"]`
        );


    if (field) {

        field.value =
            value;
    }
}


// ============================================================
// DASHBOARD
// ============================================================

function setupDashboard() {

    const jobsContainer =
        document.getElementById("jobs");

    const findButton =
        document.getElementById("find");

    const searchInput =
        document.getElementById("q");

    const domainSelect =
        document.getElementById("domain");

    const locationSelect =
        document.getElementById("loc");

    const stipendInput =
        document.getElementById(
            "sidebarStipend"
        );

    const durationSelect =
        document.getElementById(
            "sidebarDuration"
        );

    const remoteCheckbox =
        document.getElementById(
            "remoteCheck"
        );

    const count =
        document.getElementById("count");


    // Not dashboard
    if (!jobsContainer) {
        return;
    }


    const profile =
        getProfile();


    if (!profile) {

        window.location.href =
            "profile.html";

        return;
    }


    // --------------------------------------------------------
    // Put profile preferences into dashboard
    // --------------------------------------------------------

    if (
        profile.domain &&
        domainSelect
    ) {

        selectMatchingOption(
            domainSelect,
            profile.domain
        );
    }


    if (
        profile.location &&
        locationSelect
    ) {

        selectMatchingOption(
            locationSelect,
            profile.location
        );
    }


    if (
        profile.min_stipend &&
        stipendInput
    ) {

        stipendInput.value =
            profile.min_stipend;
    }


    if (
        profile.preferred_duration &&
        durationSelect
    ) {

        selectMatchingOption(
            durationSelect,
            profile.preferred_duration
        );
    }


    // --------------------------------------------------------
    // Load saved recommendations
    // --------------------------------------------------------

    const saved =
        getRecommendations();


    if (saved) {

        const recommendations =
            saved.recommendations ||
            saved.results ||
            [];


        renderJobs(
            recommendations,
            jobsContainer,
            count
        );
    }


    // --------------------------------------------------------
    // FIND MATCHES BUTTON
    // --------------------------------------------------------

    if (findButton) {

        findButton.addEventListener(
            "click",
            async function() {

                await findMatches();
            }
        );
    }


    // --------------------------------------------------------
    // ENTER IN SEARCH
    // --------------------------------------------------------

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function(event) {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    findMatches();
                }
            }
        );
    }


    // --------------------------------------------------------
    // FIND MATCHES
    // --------------------------------------------------------

    async function findMatches() {

        const currentProfile =
            getProfile();


        if (!currentProfile) {

            alert(
                "Please complete your profile first."
            );

            return;
        }


        const searchQuery =
            searchInput
                ? searchInput.value.trim()
                : "";


        const selectedDomain =
            domainSelect
                ? domainSelect.value
                : "";


        const selectedLocation =
            locationSelect
                ? locationSelect.value
                : "";


        const minStipend =
            stipendInput
                ? Number(
                    stipendInput.value || 0
                )
                : 0;


        const duration =
            durationSelect
                ? durationSelect.value
                : "";


        const includeRemote =
            remoteCheckbox
                ? remoteCheckbox.checked
                : true;


        // ----------------------------------------------------
        // Loading
        // ----------------------------------------------------

        if (findButton) {

            findButton.disabled =
                true;

            findButton.dataset.oldText =
                findButton.textContent;

            findButton.textContent =
                "Finding...";
        }


        jobsContainer.innerHTML = `

            <div class="empty">

                <h3>
                    Finding your best matches...
                </h3>

                <p>
                    InternAI is analyzing your
                    profile against the internship dataset.
                </p>

            </div>
        `;


        try {

            const data =
                await callRecommendationAPI(
                    currentProfile,
                    {

                        search_query:
                            searchQuery,

                        selected_domain:
                            selectedDomain,

                        selected_location:
                            selectedLocation,

                        include_remote:
                            includeRemote,

                        min_stipend:
                            minStipend,

                        preferred_duration:
                            duration
                    }
                );


            saveRecommendations(
                data
            );


            const recommendations =
                data.recommendations ||
                data.results ||
                [];


            renderJobs(
                recommendations,
                jobsContainer,
                count
            );


        } catch (error) {

            console.error(
                "Recommendation error:",
                error
            );


            jobsContainer.innerHTML = `

                <div class="empty">

                    <h3>
                        Could not connect to InternAI
                    </h3>

                    <p>
                        Make sure the Python backend
                        is running on port 5000.
                    </p>

                    <p>
                        Then click
                        <b>Find matches</b>
                        again.
                    </p>

                </div>
            `;
        }


        finally {

            if (findButton) {

                findButton.disabled =
                    false;

                findButton.textContent =
                    findButton.dataset.oldText ||
                    "Find matches →";
            }
        }
    }
}


// ============================================================
// SELECT OPTION
// ============================================================

function selectMatchingOption(
    select,
    value
) {

    const wanted =
        String(value)
            .trim()
            .toLowerCase();


    for (
        const option of select.options
    ) {

        if (
            option.value
                .trim()
                .toLowerCase() ===
            wanted
        ) {

            select.value =
                option.value;

            return;
        }
    }
}


// ============================================================
// RENDER JOBS
// ============================================================

function renderJobs(
    recommendations,
    container,
    countElement
) {

    if (
        !recommendations ||
        recommendations.length === 0
    ) {

        container.innerHTML = `

            <div class="empty">

                <h3>
                    No matches found
                </h3>

                <p>
                    Try changing your search,
                    location, domain or stipend.
                </p>

            </div>
        `;


        if (countElement) {

            countElement.textContent =
                "0 internships found";
        }


        return;
    }


    container.innerHTML = "";


    recommendations.forEach(
        function(job, index) {

            const card =
                createJobCard(
                    job,
                    index
                );


            container.appendChild(
                card
            );
        }
    );


    if (countElement) {

        countElement.textContent =
            `${recommendations.length} AI matches found`;
    }
}


// ============================================================
// CREATE JOB CARD
// ============================================================

function createJobCard(
    job,
    index
) {

    const card =
        document.createElement("article");


    card.className =
        "job";


    // --------------------------------------------------------
    // Values
    // --------------------------------------------------------

    const title =
        job.internship_title ||
        job.title ||
        "Internship";


    const company =
        job.company_name ||
        job.company ||
        "Company";


    const location =
        job.location ||
        "Location unavailable";


    const duration =
        job.duration ||
        "Duration unavailable";


    const stipend =
        job.stipend ||
        "Stipend unavailable";


    let match =
        Number(
            job.match_percentage
        );


    if (
        !Number.isFinite(match)
    ) {

        match =
            Number(
                job.match_score || 0
            ) * 100;
    }


    const requiredSkills =
        job.skills_required ||
        "Not available";


    const matchedSkills =
        Array.isArray(
            job.matched_skills
        )
            ? job.matched_skills
            : [];


    const missingSkills =
        Array.isArray(
            job.missing_skills
        )
            ? job.missing_skills
            : [];


    const skillScore =
        Number(
            job.skill_score || 0
        ) * 100;


    const domainScore =
        Number(
            job.domain_score || 0
        ) * 100;


    const locationScore =
        Number(
            job.location_score || 0
        ) * 100;


    const mlScore =
        Number(
            job.ml_relevance || 0
        ) * 100;


    // --------------------------------------------------------
    // Icon color
    // --------------------------------------------------------

    const colors = [
        "purple",
        "teal",
        "orange",
        "blue"
    ];


    const color =
        colors[
            index % colors.length
        ];


    // --------------------------------------------------------
    // Skills
    // --------------------------------------------------------

    let matchedHTML = "";


    if (
        matchedSkills.length > 0
    ) {

        matchedHTML = `

            <p>
                <b>✓ Matched:</b>
                ${escapeHTML(
                    matchedSkills.join(", ")
                )}
            </p>
        `;
    }


    let missingHTML = "";


    if (
        missingSkills.length > 0
    ) {

        missingHTML = `

            <p>
                <b>Missing:</b>
                ${escapeHTML(
                    missingSkills.join(", ")
                )}
            </p>
        `;
    }


    // --------------------------------------------------------
    // CARD
    // --------------------------------------------------------

    card.innerHTML = `

        <div class="ico ${color}">
            ${index + 1}
        </div>


        <div>

            <h3>

                ${escapeHTML(title)}

                <button
                    type="button"
                    class="save-job"
                    title="Save internship"
                >
                    ♡
                </button>

            </h3>


            <small>
                ${escapeHTML(company)}
                ·
                ${escapeHTML(location)}
                ·
                ${escapeHTML(duration)}
            </small>


            <div class="tags">

                💰 ${escapeHTML(stipend)}

                &nbsp;&nbsp; | &nbsp;&nbsp;

                Required:
                ${escapeHTML(requiredSkills)}

            </div>


            <p>
                <b>Why it matches:</b>
                ${escapeHTML(
                    buildReason(
                        matchedSkills,
                        locationScore,
                        domainScore
                    )
                )}
            </p>


            ${matchedHTML}

            ${missingHTML}


            <p>

                Skills:
                ${Math.round(skillScore)}%

                &nbsp; · &nbsp;

                Domain:
                ${Math.round(domainScore)}%

                &nbsp; · &nbsp;

                Location:
                ${Math.round(locationScore)}%

                &nbsp; · &nbsp;

                AI:
                ${Math.round(mlScore)}%

            </p>

        </div>


        <div class="score">

            ${Math.round(match)}%

            <small>
                AI match
            </small>

        </div>

    `;


    // --------------------------------------------------------
    // SAVE BUTTON
    // --------------------------------------------------------

    const saveButton =
        card.querySelector(
            ".save-job"
        );


    if (saveButton) {

        saveButton.addEventListener(
            "click",
            function() {

                saveJob(
                    job,
                    saveButton
                );
            }
        );
    }


    return card;
}


// ============================================================
// MATCH REASON
// ============================================================

function buildReason(
    matchedSkills,
    locationScore,
    domainScore
) {

    const reasons = [];


    if (
        matchedSkills.length > 0
    ) {

        reasons.push(
            `${matchedSkills.length} required skill${matchedSkills.length > 1 ? "s" : ""} match your profile`
        );
    }


    if (
        domainScore >= 80
    ) {

        reasons.push(
            "your domain matches"
        );
    }


    if (
        locationScore >= 80
    ) {

        reasons.push(
            "your location preference matches"
        );
    }


    if (
        reasons.length === 0
    ) {

        return "recommended using the AI matching signals in your profile";
    }


    return reasons.join(", ");
}


// ============================================================
// SAVE JOB
// ============================================================

function saveJob(job, button) {

    let savedJobs = [];

    const existing =
        localStorage.getItem("internAISavedJobs");

    if (existing) {

        try {

            savedJobs = JSON.parse(existing);

            if (!Array.isArray(savedJobs)) {
                savedJobs = [];
            }

        } catch (error) {

            console.error(
                "Could not read saved jobs:",
                error
            );

            savedJobs = [];
        }
    }


    // --------------------------------------------------------
    // CHECK IF ALREADY SAVED
    // --------------------------------------------------------

    const alreadySaved =
        savedJobs.some(function(item) {

            return (
                item.internship_title ===
                    job.internship_title
                &&
                item.company_name ===
                    job.company_name
            );

        });


    // --------------------------------------------------------
    // REMOVE FROM SAVED
    // --------------------------------------------------------

    if (alreadySaved) {

        savedJobs =
            savedJobs.filter(function(item) {

                return !(
                    item.internship_title ===
                        job.internship_title
                    &&
                    item.company_name ===
                        job.company_name
                );

            });


        localStorage.setItem(
            "internAISavedJobs",
            JSON.stringify(savedJobs)
        );


        button.textContent = "♡";
        button.style.color = "";


        console.log(
            "Removed from saved:",
            job.internship_title
        );

        return;
    }


    // --------------------------------------------------------
    // ADD TO SAVED
    // --------------------------------------------------------

    savedJobs.push(job);


    localStorage.setItem(
        "internAISavedJobs",
        JSON.stringify(savedJobs)
    );


    button.textContent = "♥";
    button.style.color = "#6c4df6";


    console.log(
        "Saved internship:",
        job.internship_title
    );


    console.log(
        "Total saved:",
        savedJobs.length
    );
}



// ============================================================
// SAVED / WISHLIST
// ============================================================

function setupSavedJobs() {

    const savedLink =
        document.getElementById("savedLink");

    const jobsContainer =
        document.getElementById("jobs");

    const count =
        document.getElementById("count");

    const findButton =
        document.getElementById("find");


    if (!savedLink || !jobsContainer) {
        return;
    }


    savedLink.addEventListener(
        "click",
        function(event) {

            event.preventDefault();


            // ------------------------------------------------
            // HIGHLIGHT SAVED
            // ------------------------------------------------

            const navLinks =
                document.querySelectorAll("header nav a");

            navLinks.forEach(function(link) {

                link.classList.remove("active");

            });


            savedLink.classList.add("active");


            // ------------------------------------------------
            // RESET FIND BUTTON
            // ------------------------------------------------

            if (findButton) {

                findButton.disabled = false;

                findButton.textContent =
                    "Find matches →";

            }


            // ------------------------------------------------
            // GET SAVED JOBS
            // ------------------------------------------------

            const savedData =
                localStorage.getItem(
                    "internAISavedJobs"
                );


            let savedJobs = [];


            if (savedData) {

                try {

                    savedJobs =
                        JSON.parse(savedData);


                    if (!Array.isArray(savedJobs)) {
                        savedJobs = [];
                    }

                } catch (error) {

                    console.error(
                        "Saved jobs data error:",
                        error
                    );

                    savedJobs = [];
                }
            }


            // ------------------------------------------------
            // NO SAVED JOBS
            // ------------------------------------------------

            if (savedJobs.length === 0) {

                jobsContainer.innerHTML = `

                    <div class="empty">

                        <h3>
                            No saved internships
                        </h3>

                        <p>
                            Save internships you like
                            and they will appear here.
                        </p>

                    </div>

                `;


                if (count) {

                    count.textContent =
                        "0 saved internships";

                }

                return;
            }


            // ------------------------------------------------
            // DISPLAY SAVED JOBS
            // ------------------------------------------------

            jobsContainer.innerHTML = "";


            savedJobs.forEach(
                function(job, index) {

                    const card =
                        createJobCard(
                            job,
                            index
                        );


                    // Make saved internships show ♥
                    const saveButton =
                        card.querySelector(
                            ".save-job"
                        );


                    if (saveButton) {

                        saveButton.textContent =
                            "♥";

                        saveButton.style.color =
                            "#6c4df6";
                    }


                    jobsContainer.appendChild(
                        card
                    );

                }
            );


            // ------------------------------------------------
            // UPDATE COUNT
            // ------------------------------------------------

            if (count) {

                count.textContent =
                    `${savedJobs.length} saved internships`;

            }

        }
    );
}



// ============================================================
// BACKEND HEALTH CHECK
// ============================================================

async function checkBackend() {

    try {

        const response =
            await fetch(
                `${API_URL}/api/health`
            );


        if (!response.ok) {

            throw new Error(
                "Backend unavailable"
            );

        }


        const data =
            await response.json();


        console.log(
            "InternAI backend is online:",
            data
        );


        return true;


    } catch (error) {

        console.warn(
            "InternAI backend is not reachable."
        );


        return false;
    }
}



// ============================================================
// INITIALIZE
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        console.log(
            "InternAI website loaded."
        );


        setupAuthentication();

        setupProfilePage();

        setupDashboard();

        setupSavedJobs();

        checkBackend();

    }
);
