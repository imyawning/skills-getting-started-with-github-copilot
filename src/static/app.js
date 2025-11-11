document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      // Add a cache-busting query param to avoid stale cached responses
      const response = await fetch(`/activities?ts=${Date.now()}`);
      const activities = await response.json();

  // Clear loading message
  activitiesList.innerHTML = "";
  // Reset activity select to the placeholder to avoid duplicate options on refresh
  activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsHTML = details.participants && details.participants.length
          ? `<div class="participants"><strong>Participants:</strong><ul>${details.participants.map(p => `<li><span class="participant-name">${p}</span><button class="participant-remove" data-activity="${encodeURIComponent(name)}" data-email="${encodeURIComponent(p)}" title="Remove participant" aria-label="Remove ${p}">✖</button></li>`).join("")}</ul></div>`
          : `<div class="participants empty"><em>No participants yet</em></div>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities so the participants list updates immediately
        // (cache-busted inside fetchActivities)
        fetchActivities();
        // Also append to the DOM immediately as a fallback in case the
        // refreshed fetch returns a cached/stale value in some browsers.
        setTimeout(() => {
          try {
            // find the activity card and append the participant if missing
            const cards = Array.from(document.querySelectorAll('.activity-card'));
            const card = cards.find(c => (c.querySelector('h4') || {}).textContent === activity);
            if (card) {
              const participantsContainer = card.querySelector('.participants');
              if (participantsContainer) {
                const ul = participantsContainer.querySelector('ul');
                if (ul) {
                  // if participant not already present, append
                  const exists = Array.from(ul.querySelectorAll('.participant-name')).some(sp => sp.textContent === email);
                  if (!exists) {
                    const li = document.createElement('li');
                    li.innerHTML = `<span class="participant-name">${email}</span><button class="participant-remove" data-activity="${encodeURIComponent(activity)}" data-email="${encodeURIComponent(email)}" title="Remove participant" aria-label="Remove ${email}">✖</button>`;
                    ul.appendChild(li);
                  }
                } else {
                  // if there was an empty message, replace it with a list
                  participantsContainer.innerHTML = `<strong>Participants:</strong><ul><li><span class="participant-name">${email}</span><button class="participant-remove" data-activity="${encodeURIComponent(activity)}" data-email="${encodeURIComponent(email)}" title="Remove participant" aria-label="Remove ${email}">✖</button></li></ul>`;
                }
                // update availability text
                const av = card.querySelector('p strong') || card.querySelector('p');
                // find the availability paragraph by text
                const pNodes = Array.from(card.querySelectorAll('p'));
                const availP = pNodes.find(p => p.textContent.includes('Availability'));
                if (availP) {
                  // parse current spots and decrement if possible
                  const match = availP.textContent.match(/(\d+) spots left/);
                  if (match) {
                    const current = parseInt(match[1], 10);
                    if (!Number.isNaN(current) && current > 0) {
                      availP.innerHTML = `<strong>Availability:</strong> ${current - 1} spots left`;
                    }
                  }
                }
              }
            }
          } catch (e) {
            // silent fallback — main refresh already in progress
            console.error('Fallback DOM update failed', e);
          }
        }, 200);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Delegate click events for removing participants
  activitiesList.addEventListener("click", async (event) => {
    const btn = event.target.closest(".participant-remove");
    if (!btn) return;

    const encodedActivity = btn.dataset.activity;
    const encodedEmail = btn.dataset.email;
    const activity = decodeURIComponent(encodedActivity);
    const email = decodeURIComponent(encodedEmail);

    if (!confirm(`Remove ${email} from ${activity}?`)) return;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/participants?email=${encodeURIComponent(email)}`,
        { method: "DELETE" }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message || `${email} removed`;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");
        // Refresh activities to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "Failed to remove participant";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
