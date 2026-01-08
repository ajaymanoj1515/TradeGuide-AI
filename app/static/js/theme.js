document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('theme-toggle');
    const body = document.body;
    const icon = toggleBtn.querySelector('i');

    // 1. Load Saved Theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        body.classList.add('light-mode');
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
        updateChartTheme('light');
    }

    // 2. Toggle Event
    toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        body.classList.toggle('light-mode');
        
        const isLight = body.classList.contains('light-mode');
        
        // Update Icon
        if (isLight) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
            localStorage.setItem('theme', 'light');
            updateChartTheme('light');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
            localStorage.setItem('theme', 'dark');
            updateChartTheme('dark');
        }
    });
});

// Helper: Update Plotly Chart if it exists
function updateChartTheme(theme) {
    const chart = document.getElementById('plotly-chart') || document.getElementById('chart');
    if (!chart) return;

    const update = {
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'font.color': theme === 'light' ? '#333' : '#fff',
        'xaxis.gridcolor': theme === 'light' ? '#eee' : '#333',
        'yaxis.gridcolor': theme === 'light' ? '#eee' : '#333'
    };
    
    // Plotly might not be loaded yet, so try-catch
    try { Plotly.relayout(chart, update); } catch (e) {}
}