let chart = null;
const BACKEND = 'http://localhost:8000/api/events';

function parseTrace(payload) {
    const hops = [];
    const avg_rtts = [];
    const labs = [];
    console.log(payload);
    payload.path.forEach(hop => {
        hops.push(hop.hop);
        const rtt = (hop.rtt_ms.length ? 
                        hop.rtt_ms.reduce((a,b)=>a+b,0)/hop.rtt_ms.length
                        : null);
        avg_rtts.push(rtt);
        labs.push(hop.ips.length ? hop.ips[0] : 'unknown')});
    return {hops, avg_rtts, labs};
}


function renderChart(hops, avg_rtts, labs) {
    const ctx = document.getElementById('traceChart').getContext('2d');

    if (chart) {
        chart.data.labels = hops;
        chart.data.datasets[0].data = avg_rtts;
        chart.options.plugins.tooltip.callbacks.label = function(context) {
            const hopIndex = context.dataIndex;
            const avg_rtt = avg_rtts[hopIndex] ? avg_rtts[hopIndex].toFixed(2) : 'N/A';
            const lab = labs[hopIndex] || '';
            const [domain_name, raw_ip]= lab.split('(');
            const ip = raw_ip ? raw_ip.slice(0, -1) : 'N/A';
            return [`RTT: ${avg_rtt} ms`, `Domain: ${domain_name}`, `IP: ${ip}`];
        };
        chart.update();
    } else {
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: hops,
                datasets: [{
                    label: 'average RTT (ms)',
                    data: avg_rtts,
                    fill: false,
                    // borderColor: 'blue',
                    tension: 0.1,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: 'red'
             }]},
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const hopIndex = context.dataIndex;
                                const avg_rtt = avg_rtts[hopIndex] ? avg_rtts[hopIndex].toFixed(2) : 'N/A';
                                const lab = labs[hopIndex] || '';
                                const [domain_name, raw_ip]= lab.split('(');
                                const ip = raw_ip ? raw_ip.slice(0, -1) : 'N/A';
                                return [`RTT: ${avg_rtt} ms`,
                                        `Domain: ${domain_name}`,
                                        `IP: ${ip}`];
                            }}}}}});
    }
}

document.getElementById('startTrace').addEventListener('click', async () => {
    try {
        const target = document.getElementById('traceTarget').value;
        document.getElementById('status').textContent = 'Loading...';
        const res = await fetch(`${BACKEND}/traceroute?target=${encodeURIComponent(target)}`);
        if (!res.ok) throw new Error('network response was not ok');
        const data = await res.json();
        const {hops, avg_rtts, labs} = parseTrace(data.metadata);
        renderChart(hops, avg_rtts, labs);
        document.getElementById('status').textContent = `Traceroute completes at ${data.ts}`;
    } catch (err) {
        document.getElementById('status').textContent = `Encountered error: ${err}`;
    }
});

