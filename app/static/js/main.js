// API endpoints
const API_URL = "http://localhost:5000/api";
const AUTH_URL = "http://localhost:5000/auth";

console.log("main.js loaded successfully!");

// Token management
function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function removeToken() {
  localStorage.removeItem("token");
}

// API calls
async function apiCall(endpoint, method = "GET", data = null) {
  const headers = {
    "Content-Type": "application/json",
  };

  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
    credentials: "include",
  };

  if (data) {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(endpoint, config);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("API call failed:", error);
    throw error;
  }
}

// Authentication
async function login(username, password) {
  try {
    const response = await apiCall(`${AUTH_URL}/login`, "POST", {
      username,
      password,
    });
    setToken(response.token);
    return response;
  } catch (error) {
    throw error;
  }
}

async function register(username, email, password) {
  try {
    return await apiCall(`${AUTH_URL}/register`, "POST", {
      username,
      email,
      password,
    });
  } catch (error) {
    throw error;
  }
}

function logout() {
  removeToken();
  window.location.href = "/login.html";
}

// Comic operations
async function getComics(page = 1, filters = {}) {
  const queryParams = new URLSearchParams({
    page,
    ...filters,
  });
  return await apiCall(`${API_URL}/comic?${queryParams}`);
}

async function getComic(comicId) {
  return await apiCall(`${API_URL}/comic/${comicId}`);
}

async function getChapter(comicId, chapterId) {
  return await apiCall(`${API_URL}/comic/${comicId}/chapter/${chapterId}`);
}

// User interface updates
function updateUI() {
  const token = getToken();
  const authLinks = document.querySelector(".auth-links");
  const userLinks = document.querySelector(".user-links");

  if (token) {
    authLinks?.classList.add("hidden");
    userLinks?.classList.remove("hidden");
  } else {
    authLinks?.classList.remove("hidden");
    userLinks?.classList.add("hidden");
  }
}

// Comic display functions
function createComicCard(comic) {
  return `
        <div class="comic-card">
            <img src="${comic.cover_image}" alt="${comic.title}" class="comic-cover">
            <div class="comic-info">
                <h3 class="comic-title">${comic.title}</h3>
                <p class="comic-author">by ${comic.author}</p>
                <div class="comic-stats">
                    <span>${comic.views} views</span>
                    <span>⭐ ${comic.rating}</span>
                </div>
                <a href="/comic.html?id=${comic.id}" class="btn btn-primary">Read</a>
            </div>
        </div>
    `;
}

function displayComics(comics) {
  const comicGrid = document.querySelector(".comic-grid");
  if (!comicGrid) return;

  comicGrid.innerHTML = comics.map(createComicCard).join("");
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  updateUI();

  // Login form
  const loginForm = document.getElementById("form-login");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;

      try {
        await login(username, password);
        window.location.href = "/";
      } catch (error) {
        alert("Login failed. Please check your credentials.");
      }
    });
  }

  // Register form
  const registerForm = document.getElementById("form-register");
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("username").value;
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      try {
        await register(username, email, password);
        alert("Registration successful! Please login.");
        window.location.href = "/login.html";
      } catch (error) {
        alert("Registration failed. Please try again.");
      }
    });
  }

  // Load comics on homepage
  if (
    window.location.pathname === "/" ||
    window.location.pathname === "/index.html"
  ) {
    getComics().then(displayComics).catch(console.error);
  }

  // Initialize ranking tabs with delay to ensure DOM is ready
  setTimeout(() => {
    console.log("DOM ready, initializing ranking tabs...");
    initRankingTabs();
  }, 100);

  // Initialize search functionality
  initializeSearch();
});

// Ranking tabs functionality
function initRankingTabs() {
  console.log("Initializing ranking tabs...");
  const rankingTabs = document.querySelectorAll("#ranking-tabs .nav-link");
  console.log("Found ranking tabs:", rankingTabs.length);

  if (rankingTabs.length === 0) {
    console.warn("No ranking tabs found! Check if #ranking-tabs exists in DOM");
    return;
  }

  // Load default ranking data (Top Tháng) on page load
  setTimeout(() => {
    console.log("Loading default ranking data...");
    loadRankingData("top-thang");
  }, 500);

  rankingTabs.forEach((tab, index) => {
    console.log(`Adding event listener to tab ${index}:`, tab.textContent);
    tab.addEventListener("click", function (e) {
      e.preventDefault();
      console.log(
        "Tab clicked:",
        this.textContent,
        "href:",
        this.getAttribute("href")
      );

      // Remove active class from all tabs
      rankingTabs.forEach((t) => {
        t.classList.remove("active", "text-white");
        t.classList.add("text-white-50");
      });

      // Add active class to clicked tab
      this.classList.add("active", "text-white");
      this.classList.remove("text-white-50");

      // Load ranking data for selected tab
      const tabType = this.getAttribute("href").substring(1);
      console.log("Loading ranking data for tab type:", tabType);
      loadRankingData(tabType);
    });
  });
}

async function loadRankingData(type) {
  console.log("Loading ranking data for:", type);

  // Mapping tab types to API periods
  const periodMap = {
    "top-thang": "thang",
    "top-tuan": "tuan",
    "top-ngay": "ngay",
  };

  const period = periodMap[type];
  if (!period) {
    console.error("Invalid ranking type:", type);
    return;
  }

  try {
    // Show loading state
    const rankingContent = document.querySelector(".ranking-content");
    if (rankingContent) {
      rankingContent.innerHTML = `
        <div class="text-center p-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Đang tải...</span>
          </div>
          <div class="mt-2">Đang tải dữ liệu...</div>
        </div>
      `;
    }

    // Fetch ranking data from API
    const response = await fetch(`/api/ranking/${period}`);
    const result = await response.json();

    if (result.success) {
      updateRankingUI(result.data);
    } else {
      throw new Error(result.error || "Failed to load ranking data");
    }
  } catch (error) {
    console.error("Error loading ranking data:", error);

    // Show error state
    const rankingContent = document.querySelector(".ranking-content");
    if (rankingContent) {
      rankingContent.innerHTML = `
        <div class="text-center text-muted p-4">
          <i class="fas fa-exclamation-triangle mb-2"></i>
          <div>Không thể tải dữ liệu xếp hạng</div>
          <small>Vui lòng thử lại sau</small>
        </div>
      `;
    }
  }
}

function updateRankingUI(rankingData) {
  const rankingContent = document.querySelector(".ranking-content");
  if (!rankingContent) return;

  if (rankingData.length === 0) {
    rankingContent.innerHTML =
      '<p class="text-center text-muted p-3">Chưa có dữ liệu xếp hạng</p>';
    return;
  }

  let html = "";

  rankingData.forEach((comic, index) => {
    const rank = comic.rank;
    const topClass = rank <= 3 ? ` top-${rank}` : "";

    let badgeClass = "bg-light text-dark";
    if (rank === 1) badgeClass = "bg-warning text-dark fw-bold";
    else if (rank === 2) badgeClass = "bg-secondary fw-bold";
    else if (rank === 3) badgeClass = "bg-danger fw-bold";

    const viewsFormatted =
      comic.views < 1000000
        ? comic.views.toLocaleString()
        : `${(comic.views / 1000000).toFixed(1)}M`;

    const titleTruncated =
      comic.title.length > 20
        ? comic.title.substring(0, 20) + "..."
        : comic.title;

    html += `
      <div class="ranking-item d-flex align-items-center p-3${topClass}">
        <div class="ranking-number me-3">
          <span class="badge ${badgeClass}">${String(rank).padStart(
      2,
      "0"
    )}</span>
        </div>
        <div class="ranking-image me-3">
          <img src="${comic.cover_image}" alt="${
      comic.title
    }" class="ranking-thumb">
        </div>
        <div class="ranking-info flex-grow-1">
          <h6 class="ranking-title mb-1" title="${comic.title}">
            <a href="/comics/${comic.id}" class="text-decoration-none">
              ${titleTruncated}
            </a>
          </h6>
          <small class="text-muted d-block">Chapter ${
            comic.chapters_count || 0
          }</small>
          <div class="ranking-views">
            <i class="fas fa-eye text-muted"></i>
            <span class="ms-1">${viewsFormatted}</span>
          </div>
        </div>
      </div>
      ${index < rankingData.length - 1 ? '<hr class="my-0">' : ""}
    `;
  });

  rankingContent.innerHTML = html;
}

// Live Search Functionality
let searchTimeout;
let searchCache = {};

function initializeSearch() {
  const searchInput = document.getElementById("search-input");
  const searchSuggestions = document.getElementById("search-suggestions");

  if (!searchInput || !searchSuggestions) return;

  searchInput.addEventListener("input", function () {
    const query = this.value.trim();

    // Clear previous timeout
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    // Hide suggestions if query is too short
    if (query.length < 2) {
      searchSuggestions.style.display = "none";
      return;
    }

    // Check cache first
    if (searchCache[query]) {
      displaySearchSuggestions(searchCache[query]);
      return;
    }

    // Debounce search
    searchTimeout = setTimeout(() => {
      performLiveSearch(query);
    }, 300);
  });

  // Hide suggestions when clicking outside
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".search-container")) {
      searchSuggestions.style.display = "none";
    }
  });

  // Handle keyboard navigation
  searchInput.addEventListener("keydown", function (e) {
    const suggestions = searchSuggestions.querySelectorAll(".suggestion-item");
    let activeIndex = Array.from(suggestions).findIndex((item) =>
      item.classList.contains("active")
    );

    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (activeIndex < suggestions.length - 1) {
        if (activeIndex >= 0)
          suggestions[activeIndex].classList.remove("active");
        suggestions[activeIndex + 1].classList.add("active");
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (activeIndex > 0) {
        suggestions[activeIndex].classList.remove("active");
        suggestions[activeIndex - 1].classList.add("active");
      }
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (activeIndex >= 0) {
        suggestions[activeIndex].click();
      } else {
        document.getElementById("search-form").submit();
      }
    }
  });
}

async function performLiveSearch(query) {
  try {
    const response = await fetch(
      `/comics/api/search?q=${encodeURIComponent(query)}&limit=5`
    );
    const result = await response.json();

    if (result.success) {
      searchCache[query] = result.data;
      displaySearchSuggestions(result.data);
    } else {
      console.error("Search error:", result.error);
    }
  } catch (error) {
    console.error("Search request failed:", error);
  }
}

function displaySearchSuggestions(comics) {
  const searchSuggestions = document.getElementById("search-suggestions");

  if (comics.length === 0) {
    searchSuggestions.innerHTML = `
      <div class="dropdown-item text-muted text-center py-3">
        <i class="fas fa-search"></i> Không tìm thấy kết quả
      </div>
    `;
  } else {
    let html = "";
    comics.forEach((comic) => {
      html += `
        <a href="/comics/${
          comic.id
        }" class="dropdown-item suggestion-item py-2 border-bottom">
          <div class="d-flex align-items-center">
            <img src="${comic.cover_image}" alt="${comic.title}" 
                 class="me-3 rounded" style="width: 40px; height: 50px; object-fit: cover;">
            <div class="flex-grow-1">
              <div class="fw-semibold text-dark">${comic.title}</div>
              <div class="text-muted small">
                <span class="me-2"><i class="fas fa-user"></i> ${
                  comic.author
                }</span>
                <span class="me-2"><i class="fas fa-tag"></i> ${
                  comic.genre
                }</span>
                <span><i class="fas fa-eye"></i> ${comic.views.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </a>
      `;
    });

    html += `
      <div class="dropdown-item text-center py-2 bg-light">
        <small class="text-muted">Nhấn Enter để xem tất cả kết quả</small>
      </div>
    `;

    searchSuggestions.innerHTML = html;
  }

  searchSuggestions.style.display = "block";
}
