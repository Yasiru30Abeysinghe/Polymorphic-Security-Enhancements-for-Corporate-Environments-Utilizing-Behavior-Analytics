const puppeteer = require('puppeteer');

async function getExtensionId(extensionName) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    const searchUrl = `https://chrome.google.com/webstore/search/${encodeURIComponent(extensionName)}`;
    await page.goto(searchUrl, { waitUntil: 'networkidle2' });

    try {
        // Wait for the new selector based on the class 'q6LNgd'
        await page.waitForSelector('a.q6LNgd', { timeout: 60000 });
        const extensionUrl = await page.$eval('a.q6LNgd', element => element.href);
        
        // Extract the extension ID from the URL
        const extensionId = extensionUrl.split('/').pop();
        await browser.close();
        return extensionId; // Only return the ID
    } catch (error) {
        await browser.close();
        return null;
    }
}

// Get the extension name from command line arguments
const extensionName = process.argv[2];

if (extensionName) {
    getExtensionId(extensionName).then(extensionId => {
        if (extensionId) {
            console.log(extensionId); // Only log the extension ID
        } else {
            console.error('Extension ID not found.');
        }
    });
} else {
    console.error("No extension name provided.");
}

