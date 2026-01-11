document.addEventListener("DOMContentLoaded", () => {

  const BACKEND = "http://localhost:8000/api/events";
  const PROBES = "?ps=ping&ps=dns&ps=tcp_connect&ps=tls_handshake&ps=http&ps=https";
  const ctx = document.getElementById("recentChart").getContext("2d");
  const DATA_LABELS = ['ping', 'dns', 'tcp_connect', 'tls_handshake', 'http', 'https'];
  const chart = new Chart(ctx,
        {type: 'line',
            data:  {labels: [],
                    datasets: DATA_LABELS.map(label => ({
        label: label, data: [], tension: 0.2, spanGaps: true})),
            options: {
                      animation: false,
                      scales: {
                            x: { title: { display: true, text: 'Time' }},
                            y: { title: { display: true, text: 'Latency (ms)' }}}}}
 });
  
  const v = x => (typeof x === "number" ? x : null);

  async function refresh() {
    try {
      const res = await fetch(`${BACKEND}/recent${PROBES}`);
      const d = await res.json();
 
      document.getElementById("status").textContent =
        `Last update: ${d.ts || "n/a"}`;

      if (d?.data ?? null) {

          chart.data.labels = [];
          chart.data.datasets.forEach(ds => ds.data = []);

          const payload = d.data;
          payload.forEach(entry => {
              chart.data.labels.push(new Date(entry.ts).toLocaleTimeString('en-GB'));
          });

          DATA_LABELS.forEach((probe, idx) => {
              payload.forEach(entry => {
                  chart.data.datasets[idx].data.push(
                    entry.data?.[probe]?.latency_ms ?? null
                  );
              });
          });
      
        chart.update();

      }} catch (e) {
      console.error(e);
      document.getElementById("status").textContent =
        "Backend not reachable";
 }}

  refresh();
  setInterval(refresh, 5000);
});
