document.getElementById('survey-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = {};
    formData.forEach((value, key) => {
        if (key.includes('Recycling') || key.includes('Cooking')) {
            data[key] = value === 'True' ? true : parseInt(value);
        } else {
            data[key] = value;
        }
    });
    
    const response = await fetch('/predict-individual', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });

    function unescapeHTML(html) {
        const txt = document.createElement("textarea");
        txt.innerHTML = html;
        return txt.value;
    }

    if (response.ok) {
        const result = await response.json();
        document.getElementById('result').innerHTML = `<span class="result-label">User's monthly carbon footprint is:</span><br><span class="result-value"><br><br>${(result.prediction / 1000).toFixed(2)} tons</span>`;
        document.getElementById('credit').innerHTML = `<span class="result-label">User's monthly credits are:</span><br><span class="result-value"><br><br>${(result.prediction / 1000).toFixed(2)}</span>`;
        document.getElementById('heat').innerHTML = `<span class="result-label">The heat produced is:</span><br><span class="result-value"><br><br>${((result.prediction / 1000) * 33.4).toFixed(2)} GJ</span>`;
        document.getElementById('trees').innerHTML = `<span class="result-label">Number of trees user owe:</span><br><span class="result-value"><br><br>${result.trees}</span>`;

       
        const suggestions = result.suggestions
            .split('\n')
            .map(line => `<p>${line.trim()}</p>`)
            .join('');
        document.getElementById('result_recommend').innerHTML = `<span class="result-label">Suggestions:</span><br><span class="result-value">${unescapeHTML(suggestions)}</span>`;
    }
});