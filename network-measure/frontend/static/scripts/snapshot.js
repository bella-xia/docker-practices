document.addEventListener("DOMContentLoaded", () => {

  const BACKEND = "http://localhost:8000/api/events";
  const ctx = document.getElementById("latencyChart").getContext("2d");

  const labels = ["ICMP", "DNS", "TCP", "TLS", "HTTP", "HTTPS"];

  const chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
                    label: 'Handshake / Setup',
                    data: [],
                  },
                  {
                    label: 'TTFB',
                    data: [],
                  },
                  {
                    label: 'Content Transfer',
                    data: [],
                  }]
    },
    options: {
      // animation: false,
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true }
     }
    }
  });

  const v = x => (typeof x === "number" ? x : null);

  async function refresh() {
    try {
      const res = await fetch(`${BACKEND}/snapshot`);
      const d = await res.json();

      document.getElementById("status").textContent =
        `Last update: ${d.ts || "n/a"}`;

      if (d?.data) {
        chart.data.datasets[0].data = [
          v(d.data.ping?.latency_ms),
          v(d.data.dns?.latency_ms),
          v(d.data.tcp_connect?.latency_ms),
          v(d.data.tls_handshake?.latency_ms),
          0, 0];
        chart.data.datasets[1].data = [
        0, 0, 0, 0,
        v(d.data.http?.metadata?.ttfb_ms),
        v(d.data.https?.metadata?.ttfb_ms)
        ];
        chart.data.datasets[2].data = [
        0, 0, 0, 0,
        v(d.data.http?.metadata?.content_ms),
        v(d.data.https?.metadata?.content_ms)
        ];
        chart.update();
      }
    } catch (e) {
      console.error(e);
      document.getElementById("status").textContent =
        "Backend not reachable";
    }
  }

  refresh();
  setInterval(refresh, 5000);
});
