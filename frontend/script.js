const API_BASE_URL = "http://localhost:5001/api";

// Initialize dashboard
document.addEventListener("DOMContentLoaded", function () {
  checkHealthStatus();
});

// Check API health status
async function checkHealthStatus() {
  const statusIndicator = document.getElementById("statusIndicator");
  const statusDot = statusIndicator.querySelector(".status-dot");

  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (response.ok) {
      statusDot.classList.add("healthy");
      statusIndicator.innerHTML =
        '<span class="status-dot healthy"></span><span>API is healthy and running</span>';
    } else {
      throw new Error("API not healthy");
    }
  } catch (error) {
    statusDot.classList.add("error");
    statusIndicator.innerHTML =
      '<span class="status-dot error"></span><span>API connection failed</span>';
    console.error("Health check failed:", error);
  }
}

// Analyze single text
async function analyzeText() {
  const textInput = document.getElementById("textInput");
  const resultDiv = document.getElementById("textResult");
  const text = textInput.value.trim();

  if (!text) {
    showError(resultDiv, "Please enter some text to analyze.");
    return;
  }

  showLoading(resultDiv, "Analyzing sentiment...");

  try {
    const response = await fetch(`${API_BASE_URL}/analyze/sentiment`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: text }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    displayTextResult(resultDiv, data);
  } catch (error) {
    showError(resultDiv, "Failed to analyze text. Please try again.");
    console.error("Analysis error:", error);
  }
}

// Display single text result
function displayTextResult(container, data) {
  const sentimentClass = data.sentiment.toLowerCase();

  container.innerHTML = `
        <div class="sentiment-result ${sentimentClass}">
            <span class="sentiment-badge ${sentimentClass}">${data.sentiment}</span>
            <div>
                <strong>Text:</strong> "${data.text}"
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 0.9rem; color: #666;">
            Analyzed using ${data.method} method
        </div>
    `;
}

// Analyze Twitter sentiment
async function analyzeTwitter() {
  const keywordInput = document.getElementById("keywordInput");
  const tweetCount = document.getElementById("tweetCount");
  const resultsDiv = document.getElementById("twitterResults");

  const keyword = keywordInput.value.trim();
  const count = tweetCount.value;

  if (!keyword) {
    showError(resultsDiv, "Please enter a keyword to search.");
    return;
  }

  showLoading(resultsDiv, "Fetching and analyzing tweets...");

  try {
    const response = await fetch(
      `${API_BASE_URL}/twitter/sentiment?keyword=${encodeURIComponent(
        keyword
      )}&count=${count}`
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    displayTwitterResults(resultsDiv, data);
  } catch (error) {
    showError(resultsDiv, "Failed to fetch tweets. Please try again.");
    console.error("Twitter analysis error:", error);
  }
}

// Display Twitter results
function displayTwitterResults(container, data) {
  const stats = data.statistics;

  // Display statistics
  const statsGrid = `
        <div class="stats-grid">
            <div class="stat-card positive">
                <div class="stat-value">${stats.positive_percentage.toFixed(
                  1
                )}%</div>
                <div class="stat-label">Positive</div>
            </div>
            <div class="stat-card negative">
                <div class="stat-value">${stats.negative_percentage.toFixed(
                  1
                )}%</div>
                <div class="stat-label">Negative</div>
            </div>
            <div class="stat-card neutral">
                <div class="stat-value">${stats.neutral_percentage.toFixed(
                  1
                )}%</div>
                <div class="stat-label">Neutral</div>
            </div>
        </div>
        <div style="text-align: center; margin-bottom: 15px; color: #666;">
            Analyzed ${stats.total_tweets} tweets for "${data.keyword}"
        </div>
    `;

  // Display tweets
  let tweetsHTML = '<h3 style="margin-bottom: 15px;">Recent Tweets</h3>';
  data.tweets.forEach((tweet) => {
    const sentimentClass = tweet.sentiment.toLowerCase();
    tweetsHTML += `
            <div class="tweet-item ${sentimentClass}">
                <div class="tweet-text">${tweet.text}</div>
                <div class="tweet-meta">
                    <span>@${tweet.user}</span>
                    <span class="sentiment-badge ${sentimentClass}">${tweet.sentiment}</span>
                </div>
            </div>
        `;
  });

  container.innerHTML = `
        <div id="statsGrid">${statsGrid}</div>
        <div class="tweets-list" id="tweetsList">${tweetsHTML}</div>
    `;
}

// Load sentiment trends
async function loadTrends() {
  const trendKeyword = document.getElementById("trendKeyword");
  const keyword = trendKeyword.value.trim();

  if (!keyword) {
    alert("Please enter a keyword for trends.");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/twitter/trends?keyword=${encodeURIComponent(keyword)}`
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    updateTrendsChart(data);
    displayHourlyTrends(data);
  } catch (error) {
    console.error("Trends loading error:", error);
    alert("Failed to load trends. Please try again.");
  }
}

// Analyze batch texts
async function analyzeBatch() {
  const batchInput = document.getElementById("batchTextInput");
  const resultsDiv = document.getElementById("batchResults");
  const texts = batchInput.value
    .trim()
    .split("\n")
    .filter((text) => text.trim());

  if (texts.length === 0) {
    showError(resultsDiv, "Please enter some texts to analyze (one per line).");
    return;
  }

  showLoading(resultsDiv, "Analyzing batch texts...");

  try {
    const response = await fetch(`${API_BASE_URL}/analyze/batch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ texts: texts }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    displayBatchResults(resultsDiv, data);
  } catch (error) {
    showError(resultsDiv, "Failed to analyze batch texts. Please try again.");
    console.error("Batch analysis error:", error);
  }
}

// Display batch results
function displayBatchResults(container, data) {
  let resultsHTML = `
        <div style="margin-bottom: 15px;">
            <h3>Batch Analysis Results</h3>
            <div class="stats-grid" style="margin: 15px 0;">
                <div class="stat-card positive">
                    <div class="stat-value">${data.statistics.positive_percentage}%</div>
                    <div class="stat-label">Positive</div>
                </div>
                <div class="stat-card negative">
                    <div class="stat-value">${data.statistics.negative_percentage}%</div>
                    <div class="stat-label">Negative</div>
                </div>
                <div class="stat-card neutral">
                    <div class="stat-value">${data.statistics.neutral_percentage}%</div>
                    <div class="stat-label">Neutral</div>
                </div>
            </div>
        </div>
    `;

  data.results.forEach((result, index) => {
    const sentimentClass = result.sentiment.toLowerCase();
    resultsHTML += `
            <div class="sentiment-result ${sentimentClass}">
                <span class="sentiment-badge ${sentimentClass}">${
      result.sentiment
    }</span>
                <div>
                    <strong>Text ${index + 1}:</strong> "${result.text}"
                </div>
            </div>
        `;
  });

  container.innerHTML = resultsHTML;
}

// Utility functions
function showLoading(container, message) {
  container.innerHTML = `<div class="loading">${message}</div>`;
}

function showError(container, message) {
  container.innerHTML = `<div class="error">${message}</div>`;
}
