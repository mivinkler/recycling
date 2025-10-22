// API-Endpunkt für Zeitreihen-Statistik
const el = document.getElementById('timeseriesChart');
const API_URL = el?.dataset.api;

document.addEventListener('DOMContentLoaded', () => {
  const form     = document.getElementById('filter-form');
  const canvas   = document.getElementById('timeseriesChart');
  const totalsEl = document.getElementById('totals');
  let chart = null;

  // Zahlformat (kg)
  const fmt = new Intl.NumberFormat('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0, useGrouping: false });

  // ---------- Label-Hilfen ----------
  const getISOWeek = (d) => {
    const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    const dayNum = date.getUTCDay() || 7;
    date.setUTCDate(date.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
    return Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
  };

  const labelForBucket = (iso, gran) => {
    const d = new Date(iso + 'T00:00:00');
    const y = d.getFullYear();
    const m = d.getMonth() + 1;
    const day = d.getDate();
    if (gran === 'day')     return `${String(day).padStart(2,'0')}.${String(m).padStart(2,'0')}.${y}`;
    if (gran === 'week')    return `KW ${getISOWeek(d)} ${y}`;
    if (gran === 'month')   return `${d.toLocaleString('de-DE', { month: 'short' })} ${y}`;
    if (gran === 'quarter') return `Q${Math.floor((m - 1) / 3) + 1} ${y}`;
    if (gran === 'year')    return String(y);
    return iso;
  };

  // ---------- Query-Parameter ----------
  const currentParams = () => {
    const get = (id) => document.getElementById(id)?.value;
    const p = new URLSearchParams();
    const cust = get('id_customer');
    const mat  = get('id_material');
    const from = get('id_date_from');
    const to   = get('id_date_to');
    if (cust) p.set('customer_id', cust);
    if (mat)  p.set('material_id', mat);
    if (from) p.set('from', from);
    if (to)   p.set('to', to);
    p.set('granularity', 'auto');
    return p.toString();
  };

  // ---------- Laden & Rendern ----------
  async function loadAndRender() {
    try {
      const resp = await fetch(`${API_URL}?${currentParams()}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      const gran    = data?.meta?.granularity || 'month';
      const buckets = Array.isArray(data?.buckets) ? data.buckets : [];
      const values  = Array.isArray(data?.series?.weight_kg) ? data.series.weight_kg.map(Number) : [];

      if (!buckets.length || !values.length) {
        totalsEl.textContent = 'Keine Daten für den gewählten Zeitraum/Filter.';
        if (chart) { chart.destroy(); chart = null; }
        return;
      }

      const labels = buckets.map(b => labelForBucket(b, gran));
      const total  = Number(data?.totals?.weight_kg ?? 0);
      totalsEl.textContent = `Gesamtgewicht: ${fmt.format(total)} kg (${labels[0]} – ${labels[labels.length - 1]})`;

      if (chart) { chart.destroy(); chart = null; }
      const ctx = canvas.getContext('2d');

      // Schrittweite bestimmen (10^n) und 2 zusätzliche Schritte oben hinzufügen
      const maxVal = Math.max(...values, 0);
      const step   = Math.pow(10, Math.floor(Math.log10(Math.max(1, maxVal))));
      const yMax   = Math.ceil(maxVal / step) * step + 2 * step; // ⬅️ z.B. 70000 -> 90000

      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            data: values,
            borderWidth: 2,
            borderColor: 'rgba(33, 150, 243, 1)',
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false,
          scales: {
            x: { grid: { drawBorder: false } },
            y: {
              beginAtZero: true,
              max: yMax,             // feste Obergrenze inkl. 2 Extra-Teilstriche
              ticks: {
                stepSize: step,      // z.B. 10000 => 0, 10000, …, 90000
                callback: (v) => fmt.format(v)
              },
              grid: { drawBorder: false }
            }
          },
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: (ctx) => `Gewicht: ${fmt.format(ctx.parsed.y)} kg` } }
          }
        }
      });
    } catch (e) {
      totalsEl.textContent = 'Fehler beim Laden der Daten.';
      if (chart) { chart.destroy(); chart = null; }
      console.error(e);
    }
  }

  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    loadAndRender();
  });

  // Initial laden
  loadAndRender();
});
