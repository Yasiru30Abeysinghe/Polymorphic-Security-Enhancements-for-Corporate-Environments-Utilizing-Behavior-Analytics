// block_downloads.js

// Function to toggle conditions visibility based on "Block all downloads" selection
function toggleConditions(hide) {
    const conditionSection = document.getElementById('condition-section');
    if (hide) {
        conditionSection.classList.add('hidden');
    } else {
        conditionSection.classList.remove('hidden');
    }
}

// Function to add a new condition row
function addCondition() {
    const conditionContainer = document.getElementById('condition-container');
    const newConditionRow = document.createElement('div');
    newConditionRow.classList.add('condition-row');
    
    newConditionRow.innerHTML = `
        <select name="conditionType[]">
            <option value="web_domain">Web-domains/URLs</option>
            <option value="file_type">File types</option>
            <option value="file_size">File size</option>
            <option value="time_limit">Time limit</option>
        </select>
        <input type="text" name="conditionValue[]" placeholder="Enter value">
        <button type="button" onclick="removeCondition(this)">-</button>
    `;
    conditionContainer.appendChild(newConditionRow);
}

// Function to remove a condition row
function removeCondition(button) {
    const row = button.parentElement;
    row.remove();
}
