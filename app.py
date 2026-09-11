<!DOCTYPE html>
<html lang="ka">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Logistics Analytics</title>
  <!-- Chart.js გრაფიკებისთვის -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    /* 1. დარქ მოუდის და ლაით მოუდის ცვლადები */
    :root {
      --bg-body: #f3f4f6;
      --bg-sidebar: #ffffff;
      --bg-card: #ffffff;
      --text-main: #1f2937;
      --text-muted: #6b7280;
      --border-color: #e5e7eb;
      --tab-active-bg: #e0e7ff;
      --tab-active-text: #4f46e5;
      --btn-danger: #ef4444;
    }

    body.dark-mode {
      --bg-body: #111827;
      --bg-sidebar: #1f2937;
      --bg-card: #374151;
      --text-main: #f9fafb;
      --text-muted: #9ca3af;
      --border-color: #4b5563;
      --tab-active-bg: #3730a3;
      --tab-active-text: #e0e7ff;
      --btn-danger: #f87171;
    }

    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: var(--bg-body);
      color: var(--text-main);
      display: flex;
      height: 100vh;
      transition: background-color 0.3s, color 0.3s;
    }

    /* --- Sidebar (გასწორებული დარქ მოუდი) --- */
    .sidebar {
      width: 280px;
      background-color: var(--bg-sidebar);
      border-right: 1px solid var(--border-color);
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 15px;
      transition: background-color 0.3s;
    }

    .filter-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* ერთიანად წაშლის ღილაკი */
    .clear-all-btn {
      background-color: transparent;
      color: var(--btn-danger);
      border: 1px solid var(--btn-danger);
      padding: 5px 10px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      transition: 0.2s;
    }
    .clear-all-btn:hover {
      background-color: var(--btn-danger);
      color: white;
    }

    .filter-tags-container {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .filter-tag {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background-color: var(--btn-danger);
      color: white;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 14px;
    }

    .filter-tag span { cursor: pointer; font-weight: bold; }

    /* --- Main Content --- */
    .main-content {
      flex: 1;
      padding: 30px;
      overflow-y: auto;
    }

    /* 4. გასწორებული Tab ღილაკები */
    .tabs-container {
      display: flex;
      gap: 10px;
      border-bottom: 2px solid var(--border-color);
      padding-bottom: 10px;
      margin-bottom: 20px;
    }

    .tab-btn {
      background: transparent;
      color: var(--text-muted);
      border: none;
      padding: 10px 20px;
      font-size: 16px;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .tab-btn:hover {
      background-color: var(--bg-card);
    }

    /* ლამაზი აქტიური ღილაკი ცუდი ლურჯი მართკუთხედის ნაცვლად */
    .tab-btn.active {
      background-color: var(--tab-active-bg);
      color: var(--tab-active-text);
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 3. გრაფიკის ველი */
    .chart-section {
      display: none;
      background-color: var(--bg-card);
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .chart-section.active {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    .chart-container {
      position: relative;
      height: 300px;
      width: 100%;
    }

    /* Theme Toggle */
    .theme-toggle {
      position: absolute;
      top: 20px;
      right: 20px;
      padding: 10px;
      border-radius: 8px;
      cursor: pointer;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-main);
    }
  </style>
</head>
<body class="dark-mode">

  <button class="theme-toggle" onclick="toggleTheme()">🌓 თემის შეცვლა</button>

  <!-- მარცხენა პანელი (Sidebar) -->
  <aside class="sidebar">
    <div class="filter-header">
      <h3>⚙️ ფილტრი & ძებნა</h3>
      <!-- ერთიანად წაშლის ღილაკი -->
      <button class="clear-all-btn" onclick="clearAllFilters()">✖ ყველას წაშლა</button>
    </div>
    
    <div class="filter-tags-container" id="filterContainer">
      <div class="filter-tag">📍 საფრანგეთი → ფოთი <span onclick="this.parentElement.remove()">×</span></div>
      <div class="filter-tag">🏢 Caucasus Express <span onclick="this.parentElement.remove()">×</span></div>
      <div class="filter-tag">📦 თევზის საკვები <span onclick="this.parentElement.remove()">×</span></div>
    </div>
  </aside>

  <!-- მთავარი კონტენტი -->
  <main class="main-content">
    
    <!-- Tab მენიუ -->
    <div class="tabs-container">
      <button class="tab-btn" onclick="switchTab('table')">📋 ცხრილი</button>
      <button class="tab-btn active" onclick="switchTab('chart')">📊 გრაფიკი</button>
      <button class="tab-btn" onclick="switchTab('map')">🗺️ რუკა</button>
    </div>

    <!-- გრაფიკის სექცია (რომელიც ცარიელი იყო) -->
    <div id="chartView" class="chart-section active">
      <div style="grid-column: span 2;">
        <h2>📊 ვიზუალური ანალიტიკა</h2>
      </div>
      <div class="chart-container">
        <canvas id="priceChart"></canvas>
      </div>
      <div class="chart-container">
        <canvas id="transitChart"></canvas>
      </div>
    </div>

  </main>

  <script>
    // დარქ მოუდის მართვა
    function toggleTheme() {
      document.body.classList.toggle('dark-mode');
    }

    // ფილტრების ერთიანად წაშლა
    function clearAllFilters() {
      const container = document.getElementById('filterContainer');
      container.innerHTML = ''; 
    }

    // Tab-ების მართვა
    function switchTab(tabName) {
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      event.currentTarget.classList.add('active');
      
      // აქ შეგიძლიათ დაამატოთ ლოგიკა სხვა სექციების (ცხრილი/რუკა) გამოსაჩენად
      if(tabName === 'chart') {
        document.getElementById('chartView').classList.add('active');
      } else {
        document.getElementById('chartView').classList.remove('active');
      }
    }

    // Chart.js გრაფიკების ინიციალიზაცია (ცარიელი ველის შესავსებად)
    window.onload = function() {
      // ფასების შედარების გრაფიკი
      new Chart(document.getElementById('priceChart'), {
        type: 'bar',
        data: {
          labels: ['GeoLogistics', 'Orient', 'Caucasus'],
          datasets: [{
            label: '💰 ფასი ($)',
            data: [2800, 3100, 3600],
            backgroundColor: '#4f46e5',
            borderRadius: 6
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });

      // ტრანზიტის დროის გრაფიკი
      new Chart(document.getElementById('transitChart'), {
        type: 'line',
        data: {
          labels: ['GeoLogistics', 'Orient', 'Caucasus'],
          datasets: [{
            label: '⏱ ტრანზიტის დრო (დღე)',
            data: [22, 17, 19],
            borderColor: '#f59e0b',
            tension: 0.4,
            fill: true,
            backgroundColor: 'rgba(245, 158, 11, 0.2)'
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }
  </script>
</body>
</html>
