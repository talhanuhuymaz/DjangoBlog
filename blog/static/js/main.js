// Function to toggle theme
function toggleTheme() {
  const body = document.body;
  const isDark = body.classList.toggle("dark-theme");
  const icons = document.querySelectorAll("#theme-icon, #theme-icon-mobile");

  icons.forEach((icon) => {
    if (isDark) {
      icon.classList.remove("fa-moon");
      icon.classList.add("fa-sun");
    } else {
      icon.classList.remove("fa-sun");
      icon.classList.add("fa-moon");
    }
  });

  // Save preference
  localStorage.setItem("theme", isDark ? "dark" : "light");
}

// Function to show post modal
function showPostModal(postId) {
  const modalId = `postModal${postId}`;
  const modal = new bootstrap.Modal(document.getElementById(modalId));
  modal.show();
}

// Function to handle post likes
function likePost(button, csrfToken) {
  const postId = button.dataset.postId;

  fetch("/like/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": csrfToken,
    },
    body: `post_id=${postId}`,
  })
    .then((response) => response.json())
    .then((data) => {
      // Update like button state
      if (data.liked) {
        button.classList.add("liked");
      } else {
        button.classList.remove("liked");
      }
      // Update likes count
      button.querySelector(".likes-count").textContent = data.likes_count;
    })
    .catch((error) => console.error("Error:", error));
}

// Function to handle follow/unfollow
function toggleFollow(button, csrfToken) {
  const username = button.dataset.username;

  fetch(`/toggle_follow/${username}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": csrfToken,
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        // Update all follow buttons for this user
        document
          .querySelectorAll(`.follow-button[data-username="${username}"]`)
          .forEach((btn) => {
            if (data.is_following) {
              btn.classList.remove("btn-primary");
              btn.classList.add("btn-outline-primary");
              btn.querySelector("i").classList.remove("fa-user-plus");
              btn.querySelector("i").classList.add("fa-user-minus");
              btn.querySelector(".follow-text").textContent = "Unfollow";
            } else {
              btn.classList.remove("btn-outline-primary");
              btn.classList.add("btn-primary");
              btn.querySelector("i").classList.remove("fa-user-minus");
              btn.querySelector("i").classList.add("fa-user-plus");
              btn.querySelector(".follow-text").textContent = "Follow";
            }
          });
      }
    })
    .catch((error) => console.error("Error:", error));
}

// Initialize theme on page load
document.addEventListener("DOMContentLoaded", function () {
  // Apply saved theme preference
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.classList.add("dark-theme");
    document
      .querySelectorAll("#theme-icon, #theme-icon-mobile")
      .forEach((icon) => {
        icon.classList.remove("fa-moon");
        icon.classList.add("fa-sun");
      });
  }

  // Handle tab functionality if present
  const searchForm = document.getElementById("searchForm");
  if (searchForm) {
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get("tab");
    const postId = urlParams.get("post");

    // Set initial active tab
    const hash = tabParam
      ? `#${tabParam}`
      : window.location.hash || "#following";
    const tab = document.querySelector(`[data-bs-target="${hash}"]`);
    if (tab) {
      tab.click();
    }

    // Update hidden input when tabs change
    const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabs.forEach((tab) => {
      tab.addEventListener("shown.bs.tab", function (event) {
        const activeTab = event.target
          .getAttribute("data-bs-target")
          .replace("#", "");
        document.getElementById("currentTab").value = activeTab;

        // Update URL with current tab
        const url = new URL(window.location);
        url.searchParams.set("tab", activeTab);
        if (postId) {
          url.searchParams.set("post", postId);
        }
        window.history.replaceState({}, "", url);
      });
    });

    // Auto-open post modal if ?post=ID is present
    if (postId) {
      setTimeout(function () {
        showPostModal(postId);
      }, 400);
    }
  }
});
