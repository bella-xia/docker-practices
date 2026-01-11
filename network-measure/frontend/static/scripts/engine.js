const BACKEND = 'http://localhost:8000/api/events';

document.getElementById('startMeasure').addEventListener('click', async () => {
    try {
        const target = document.getElementById('measureTarget').value;
        const res = await fetch(`${BACKEND}/start`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ target }),
        });
        const j = await res.json();
        if (!res.ok) throw new Error('Start measurement request failed');
        document.getElementById('status').textContent = `Started measurement for target ${target} at ${j.ts}`;
    } catch (err) {
        document.getElementById('status').textContent = `Encounters error: ${err}`;
    }
   
});

document.getElementById('pauseMeasure').addEventListener('click', async () => {
    try {
        const res = await fetch(`${BACKEND}/pause`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
        });
        const j = await res.json();
        if (!res.ok) throw new Error('Pause measurement request failed');
        document.getElementById('status').textContent = `Paused measurement at ${j.ts}`;
    } catch (err) {
    document.getElementById('status').textContent = `Encounters error: ${err}`;
    }
});

document.getElementById('clearMeasure').addEventListener('click', async () => {
    try {
        const res = await fetch(`${BACKEND}/clear`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
        });
        const j = await res.json();
        if (!res.ok) throw new Error('Clear measurement request failed');
        document.getElementById('status').textContent = `Cleared measurement at ${j.ts}`;
    } catch (err) {
    document.getElementById('status').textContent = `Encounters error: ${err}`;
    }
});

