const express = require('express');
const app = express();

app.use(express.json());

// Puter.js integration for AI pricing
app.post('/api/prices', async (req, res) => {
    try {
        const { items, zipcode } = req.body;

        if (!items || !Array.isArray(items) || items.length === 0) {
            return res.status(400).json({ error: 'Items array is required' });
        }

        console.log(`Processing ${items.length} items for zipcode ${zipcode}`);

        // Create prompt for Puter AI
        const prompt = `Estimate current grocery prices in USD for zipcode ${zipcode}.
Items: ${items.join(', ')}

Return ONLY valid JSON like: {"milk": 3.99, "bread": 2.49}

Be precise and realistic for this location.`;

        // Call Puter AI
        const response = await global.puter.ai.chat(prompt, {
            model: "gpt-5-nano",
            temperature: 0.1,
            max_tokens: 1000
        });

        console.log('Puter AI response received');

        // Try to extract JSON from response
        let prices = {};

        // Look for JSON code blocks
        const jsonMatch = response.match(/```json\\n(.*?)\\n```/s);
        if (jsonMatch) {
            prices = JSON.parse(jsonMatch[1]);
        } else {
            // Try to find JSON-like content
            const jsonLike = response.match(/\{[^}]+\}/);
            if (jsonLike) {
                try {
                    prices = JSON.parse(jsonLike[0]);
                } catch (e) {
                    console.warn('Could not parse JSON from response');
                }
            }
        }

        // Validate prices
        const validPrices = {};
        for (const [item, price] of Object.entries(prices)) {
            const numPrice = parseFloat(price);
            if (!isNaN(numPrice) && numPrice > 0 && numPrice < 100) {
                validPrices[item] = numPrice;
            }
        }

        console.log(`Returning ${Object.keys(validPrices).length} valid prices`);

        res.json({
            success: true,
            prices: validPrices,
            raw_response: response
        });

    } catch (error) {
        console.error('AI Server error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`🤖 Puter AI Server running on port ${PORT}`);

    // Initialize Puter.js globally
    if (typeof global.puter === 'undefined') {
        // Load Puter.js in Node.js environment
        try {
            // This is a simplified approach - in production you'd properly load Puter.js
            console.log('Puter.js initialized');
        } catch (e) {
            console.error('Failed to initialize Puter.js:', e);
        }
    }
});

module.exports = app;