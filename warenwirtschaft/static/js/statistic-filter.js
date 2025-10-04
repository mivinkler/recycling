document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('filter-form');
  const chartEl = document.getElementById('timeseriesChart');
  const totalsEl = document.getElementById('totals');

  let chart;
  const fmtNumber = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 2 });

  function getISOWeek(dt) {
    const d = new Date(Date.UTC(dt.getFullYear(), dt.getMonth(), dt.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
    return Math.ceil((((d - yearStart) / 86400000) + 1)/7);
  }

  function labelForBucket(iso, granularity) {
    const d = new Date(iso + 'T00:00:00');
    const y = d.getFullYear();
    const m = d.getMonth() + 1;
    const day = d.getDate();
    if (granularity === 'day') return `${String(day).padStart(2,'0')}.${String(m).padStart(2,'0')}.${y}`;
    if (granularity === 'week') return `KW ${getISOWeek(d)} ${y}`;
    if (granularity === 'month') return `${d.toLocaleString('de-DE', { month: 'short' })} ${y}`;
    if (granularity === 'quarter') return `Q${Math.floor((m-1)/3)+1} ${y}`;
    if (granularity === 'year') return String(y);
    return iso;
  }

  function currentParams() {
    const params = new URLSearchParams();
    const cust = document.getElementById('id_customer')?.value;
    const mat = document.getElementById('id_material')?.value;
    const from = document.getElementById('id_date_from')?.value;
    const to = document.getElementById('id_date_to')?.value;
    if (cust) params.set('customer_id', cust);
    if (mat) params.set('material_id', mat);
    if (from) params.set('from', from);
    if (to) params.set('to', to);
    params.set('granularity', 'auto'); // 🇩🇪 automatische Auflösung
    return params.toString();
  }

  async function loadDataAndRender() {
    const qs = currentParams();
    const apiUrl = document.getElementById('page-vars')?.dataset.apiUrl;
    if (!apiUrl) { console.error('API URL not found'); return; }
    const resp = await fetch(`${apiUrl}?${qs}`);
    if (!resp.ok) { totalsEl.textContent = 'Fehler beim Laden der Daten.'; return; }
    const data = await resp.json();

    // 👉 отладка: увидим массивы и их длины
    console.debug('timeseries raw:', data);
    const gran = data?.meta?.granularity || 'month';
    const buckets = Array.isArray(data.buckets) ? data.buckets : [];
    const values  = Array.isArray(data?.series?.weight_kg) ? data.series.weight_kg.map(Number) : [];

    if (!buckets.length || !values.length) {
      totalsEl.textContent = 'Keine Daten für den gewählten Zeitraum/Filter.';
      if (chart) { chart.destroy(); chart = null; }
      return;
    }

    const labels = buckets.map(b => labelForBucket(b, gran));
    const total = Number(data?.totals?.weight_kg ?? 0);
    totalsEl.textContent = `Gesamtgewicht: ${fmtNumber.format(total)} kg (${labels[0]} – ${labels[labels.length-1]})`;

    // 👉 если график уже был — уничтожим, чтобы исключить артефакты
    if (chart) { chart.destroy(); chart = null; }

    // ⚠️ получаем 2D-контекст явно — самый надёжный путь
    const ctx = chartEl.getContext('2d');

    chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Gewicht (kg)',
          data: values,
          borderWidth: 1,
          backgroundColor: 'rgba(33, 150, 243, 0.6)',
          borderColor: '#2196f3'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        scales: {
          x: { title: { display: true, text: 'Zeit' } },
          y: {
            title: { display: true, text: 'Gewicht (kg)' },
            beginAtZero: true,
            grace: '10%',
            ticks: { callback: (v) => new Intl.NumberFormat('de-DE').format(v) }
          }
        },
        plugins: {
          legend: { display: true },
          tooltip: {
            callbacks: {
              label: (ctx) => `Gewicht: ${fmtNumber.format(ctx.parsed.y)} kg`
            }
          }
        }
      }
    });

    // 👉 финальная отладка: убедимся, что Chart получил числа
    console.debug('chart labels:', chart.data.labels);
    console.debug('chart values:', chart.data.datasets[0].data);
  }



  form.addEventListener('submit', (e) => {
    e.preventDefault();
    loadDataAndRender();
  });

  // 🇩🇪 Initial laden
  loadDataAndRender();
});