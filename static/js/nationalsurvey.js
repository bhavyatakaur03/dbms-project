document.getElementById('data-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = {};
    formData.forEach((value, key) => (data[key] = value));
    
    const response = await fetch('/predictnational', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    
    const result = await response.json();
    document.getElementById('result1').innerHTML =`<span class="result-label">Your Footprint is(per capita per year): </span><br><span class="result-value"><br><br>${result.prediction} tons</span>`;
    document.getElementById('result_recommend').innerHTML =`<span class="result-label">Suggestions:</span><br><span class="result-value">${result.suggestions.replace(/\n/g, '<br>')}</span>`;
    document.getElementById('credit').innerHTML =`<span class="result-label">Your monthly credits are:</span><br><span class="result-value"><br><br>${(result.prediction).toFixed(2)}</span>`;
    document.getElementById('heat').innerHTML =`<span class="result-label">the heat produced is:</span><br><span class="result-value"><br><br>${(((result.prediction).toFixed(2))*33.4).toFixed(2)}GJ</span>`;
    document.getElementById('trees').innerHTML =`<span class="result-label">the number of trees you owe:</span><br><span class="result-value"><br><br>${result.trees}</span>`;
});
