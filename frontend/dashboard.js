// Chart initialization and management
let sentimentChart = null;

// Initialize chart
function initializeChart() {
  const ctx = document.getElementById("sentimentChart").getContext("2d");

  sentimentChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Positive",
          data: [],
          borderColor: "#4CAF50",
          backgroundColor: "rgba(76, 175, 80, 0.1)",
          tension: 0.4,
          fill: true,
        },
        {
          label: "Negative",
          data: [],
          borderColor: "#f44336",
          backgroundColor: "rgba(244, 67, 54, 0.1)",
          tension: 0.4,
          fill: true,
        },
        {
          label: "Neutral",
          data: [],
          borderColor: "#ff9800",
          backgroundColor: "rgba(255, 152, 0, 0.1)",
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Sentiment Trends Over Time",
          font: {
            size: 16,
          },
        },
        tooltip: {
          mode: "index",
          intersect: false,
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: "Time",
          },
        },
        y: {
          title: {
            display: true,
            text: "Number of Tweets",
          },
          min: 0,
        },
      },
    },
  });
}

// Update trends chart with new data
function updateTrendsChart(data) {
  if (!sentimentChart) {
    initializeChart();
  }

  const hourlyData = data.hourly_sentiment;
  const labels = hourlyData.map((item) => item.hour);
  const positiveData = hourlyData.map((item) => item.positive);
  const negativeData = hourlyData.map((item) => item.negative);
  const neutralData = hourlyData.map((item) => item.neutral);

  sentimentChart.data.labels = labels;
  sentimentChart.data.datasets[0].data = positiveData;
  sentimentChart.data.datasets[1].data = negativeData;
  sentimentChart.data.datasets[2].data = neutralData;

  sentimentChart.update();
}

// Display hourly trends
function displayHourlyTrends(data) {
  const hourlyTrendsDiv = document.getElementById("hourlyTrends");
  const currentSentiment = data.current_sentiment;

  let trendsHTML = "<h3>Current Sentiment Distribution</h3>";

  // Current sentiment cards
  trendsHTML += `
        <div class="stats-grid" style="margin: 15px 0;">
            <div class="stat-card positive">
                <div class="stat-value">${currentSentiment.positive || 0}</div>
                <div class="stat-label">Positive</div>
            </div>
            <div class="stat-card negative">
                <div class="stat-value">${currentSentiment.negative || 0}</div>
                <div class="stat-label">Negative</div>
            </div>
            <div class="stat-card neutral">
                <div class="stat-value">${currentSentiment.neutral || 0}</div>
                <div class="stat-label">Neutral</div>
            </div>
        </div>
    `;

  // Hourly trends
  trendsHTML += "<h3>Hourly Trends</h3>";
  data.hourly_sentiment.forEach((hour) => {
    const total = hour.positive + hour.negative + hour.neutral;
    trendsHTML += `
            <div class="hour-trend">
                <div style="font-weight: bold; margin-bottom: 5px;">${hour.hour}</div>
                <div style="color: #4CAF50;">↑ ${hour.positive} pos</div>
                <div style="color: #f44336;">↓ ${hour.negative} neg</div>
                <div style="color: #ff9800;">→ ${hour.neutral} neu</div>
                <div style="margin-top: 5px; font-size: 0.8rem; color: #666;">Total: ${total}</div>
            </div>
        `;
  });

  hourlyTrendsDiv.innerHTML = trendsHTML;
}

// Auto-refresh functionality
let autoRefreshInterval = null;

function startAutoRefresh(keyword, interval = 60000) {
  // 1 minute
  stopAutoRefresh();
  autoRefreshInterval = setInterval(() => {
    if (keyword) {
      loadTrendsForKeyword(keyword);
    }
  }, interval);
}

function stopAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", function () {
  initializeChart();

  // Add event listeners for Enter key
  document
    .getElementById("textInput")
    .addEventListener("keypress", function (e) {
      if (e.key === "Enter" && e.ctrlKey) {
        analyzeText();
      }
    });

  document
    .getElementById("keywordInput")
    .addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        analyzeTwitter();
      }
    });

  document
    .getElementById("trendKeyword")
    .addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        loadTrends();
      }
    });
});
