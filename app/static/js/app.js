// FIFA Player Recommendation System - JavaScript Application

// Global state
let currentGender = 'male';
let currentSection = 'home';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeGenderToggle();
    initializeAutocomplete();
    loadStats();
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Show section
            const sectionName = link.dataset.section;
            showSection(sectionName);
        });
    });
}

function showSection(sectionName) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionName;
    }
}

// Gender toggle
function initializeGenderToggle() {
    const genderBtns = document.querySelectorAll('.gender-btn');
    
    genderBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            genderBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentGender = btn.dataset.gender;
            
            showToast(`Switched to ${currentGender} players`, 'success');
        });
    });
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('total-male-players').textContent = 
                data.male.total_players.toLocaleString();
            document.getElementById('total-female-players').textContent = 
                data.female.total_players.toLocaleString();
            document.getElementById('top-male-player').textContent = 
                data.male.top_rated;
            document.getElementById('top-female-player').textContent = 
                data.female.top_rated;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Search players
async function searchPlayers() {
    const query = document.getElementById('search-query').value.trim();
    const position = document.getElementById('search-position').value;
    const minOverall = document.getElementById('search-min-overall').value;
    const maxOverall = document.getElementById('search-max-overall').value;
    const nation = document.getElementById('search-nation').value.trim();
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                gender: currentGender,
                query: query || undefined,
                position: position || undefined,
                min_overall: minOverall ? parseInt(minOverall) : undefined,
                max_overall: maxOverall ? parseInt(maxOverall) : undefined,
                nation: nation || undefined,
                limit: 50
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.players);
            showToast(`Found ${data.count} player(s)`, 'success');
        } else {
            showToast(data.error || 'Search failed', 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

function displaySearchResults(players) {
    const container = document.getElementById('search-results');
    
    if (!players || players.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>No players found</h3>
                <p>Try adjusting your search filters</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="results-header">
            <h3>Search Results</h3>
            <p class="results-count">${players.length} player(s) found</p>
        </div>
        <div class="player-grid">
            ${players.map(player => createPlayerCard(player)).join('')}
        </div>
    `;
}

// Get recommendations
async function getRecommendations() {
    const playerName = document.getElementById('recommend-player').value.trim();
    const count = parseInt(document.getElementById('recommend-count').value) || 10;
    const samePosition = document.getElementById('recommend-same-position').checked;
    
    if (!playerName) {
        showToast('Please enter a player name', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                gender: currentGender,
                player_name: playerName,
                n_recommendations: count,
                same_position: samePosition
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayRecommendations(data.source_player, data.recommendations);
            showToast(`Found ${data.recommendations.length} similar player(s)`, 'success');
        } else {
            showToast(data.error || 'Recommendation failed', 'error');
            document.getElementById('recommend-results').innerHTML = `
                <div class="no-results">
                    <i class="fas fa-exclamation-circle"></i>
                    <h3>Player not found</h3>
                    <p>Please check the player name and try again</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Recommendation error:', error);
        showToast('Recommendation failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

function displayRecommendations(sourcePlayer, recommendations) {
    const container = document.getElementById('recommend-results');
    
    container.innerHTML = `
        <div class="results-header">
            <h3>Players Similar to ${sourcePlayer.name}</h3>
            <p class="results-count">${recommendations.length} recommendation(s)</p>
        </div>
        <div class="source-player-card glass">
            <h4 style="margin-bottom: 1rem;"><i class="fas fa-user"></i> Source Player</h4>
            ${createPlayerCard(sourcePlayer, false)}
        </div>
        <div class="player-grid">
            ${recommendations.map(player => createPlayerCard(player, true)).join('')}
        </div>
    `;
}

// Compare players
async function comparePlayers() {
    const player1 = document.getElementById('compare-player-1').value.trim();
    const player2 = document.getElementById('compare-player-2').value.trim();
    const player3 = document.getElementById('compare-player-3').value.trim();
    const player4 = document.getElementById('compare-player-4').value.trim();
    
    const players = [player1, player2, player3, player4].filter(p => p);
    
    if (players.length < 2) {
        showToast('Please enter at least 2 player names', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                gender: currentGender,
                players: players
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayComparison(data.players);
            showToast('Comparison loaded successfully', 'success');
        } else {
            showToast(data.error || 'Comparison failed', 'error');
        }
    } catch (error) {
        console.error('Comparison error:', error);
        showToast('Comparison failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

function displayComparison(playersData) {
    const container = document.getElementById('compare-results');
    
    container.innerHTML = `
        <div class="results-header">
            <h3>Player Comparison</h3>
            <p class="results-count">Comparing ${playersData.length} player(s)</p>
        </div>
        <div class="comparison-container">
            ${playersData.map((data, index) => createComparisonCard(data, index)).join('')}
        </div>
    `;
    
    // Render radar charts
    playersData.forEach((data, index) => {
        renderRadarChart(`radar-${index}`, data.radar);
    });
}

function createComparisonCard(data, index) {
    const player = data.card;
    
    return `
        <div class="comparison-card glass">
            <div class="player-card-header">
                <div class="player-overall" style="color: ${getOverallColor(player.overall)}">
                    ${player.overall}
                </div>
                <div class="player-position">${player.position}</div>
            </div>
            <div class="player-name">${player.name}</div>
            <div class="player-info">
                <div><i class="fas fa-calendar"></i> ${player.age} years old</div>
                <div><i class="fas fa-flag"></i> ${player.nation}</div>
                <div><i class="fas fa-shield-alt"></i> ${player.team}</div>
            </div>
            <div class="radar-container">
                <canvas id="radar-${index}"></canvas>
            </div>
            <div class="player-stats">
                <div class="player-stat">
                    <div class="player-stat-value">${player.pace}</div>
                    <div class="player-stat-label">PAC</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.shooting}</div>
                    <div class="player-stat-label">SHO</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.passing}</div>
                    <div class="player-stat-label">PAS</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.dribbling}</div>
                    <div class="player-stat-label">DRI</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.defending}</div>
                    <div class="player-stat-label">DEF</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.physical}</div>
                    <div class="player-stat-label">PHY</div>
                </div>
            </div>
        </div>
    `;
}

// Create player card HTML
function createPlayerCard(player, showSimilarity = false) {
    return `
        <div class="player-card glass" onclick="openPlayerDetails('${player.name.replace(/'/g, "\\'")}')">
            ${showSimilarity && player.similarity ? `
                <div class="similarity-badge">${player.similarity}% Match</div>
            ` : ''}
            <div class="player-card-header">
                <div class="player-overall" style="color: ${getOverallColor(player.overall)}">
                    ${player.overall}
                </div>
                <div class="player-position">${player.position}</div>
            </div>
            <div class="player-name">${player.name}</div>
            <div class="player-info">
                <div><i class="fas fa-calendar"></i> ${player.age} years old</div>
                <div><i class="fas fa-flag"></i> ${player.nation}</div>
                <div><i class="fas fa-trophy"></i> ${player.league}</div>
                <div><i class="fas fa-shield-alt"></i> ${player.team}</div>
            </div>
            <div class="player-stats">
                <div class="player-stat">
                    <div class="player-stat-value">${player.pace}</div>
                    <div class="player-stat-label">PAC</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.shooting}</div>
                    <div class="player-stat-label">SHO</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.passing}</div>
                    <div class="player-stat-label">PAS</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.dribbling}</div>
                    <div class="player-stat-label">DRI</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.defending}</div>
                    <div class="player-stat-label">DEF</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${player.physical}</div>
                    <div class="player-stat-label">PHY</div>
                </div>
            </div>
        </div>
    `;
}

// Render radar chart
function renderRadarChart(canvasId, radarData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const attributes = radarData.attributes;
    const labels = Object.keys(attributes);
    const values = Object.values(attributes);
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: radarData.name,
                data: values,
                fill: true,
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderColor: 'rgba(102, 126, 234, 1)',
                pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: 'rgba(255, 255, 255, 0.9)',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Utility functions
function getOverallColor(overall) {
    if (overall >= 90) return '#FFD700';
    if (overall >= 85) return '#FF4500';
    if (overall >= 80) return '#32CD32';
    if (overall >= 75) return '#4169E1';
    return '#808080';
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.add('show');
    } else {
        overlay.classList.remove('show');
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Player detail modal
async function openPlayerDetails(playerName) {
    showLoading(true);
    
    try {
        const response = await fetch(`/api/player/${encodeURIComponent(playerName)}?gender=${currentGender}`);
        const data = await response.json();
        
        if (data.success) {
            displayPlayerModal(data.player, data.radar);
        } else {
            showToast('Player details not found', 'error');
        }
    } catch (error) {
        console.error('Error loading player details:', error);
        showToast('Failed to load player details', 'error');
    } finally {
        showLoading(false);
    }
}

function displayPlayerModal(player, radar) {
    const modal = document.getElementById('player-modal');
    const content = document.getElementById('modal-player-content');
    
    content.innerHTML = `
        <div class="modal-player-header">
            <div class="modal-player-name">${player.name}</div>
            <div class="modal-player-info">
                <span style="color: ${getOverallColor(player.overall)}; font-size: 1.5rem; font-weight: 700;">OVR ${player.overall}</span>
                <span>${player.position}</span>
                <span>${player.age} years</span>
                <span><i class="fas fa-flag"></i> ${player.nation}</span>
            </div>
            <div class="modal-player-info" style="margin-top: 0.5rem;">
                <span><i class="fas fa-trophy"></i> ${player.league}</span>
                <span><i class="fas fa-shield-alt"></i> ${player.team}</span>
            </div>
            <div class="modal-player-info" style="margin-top: 0.5rem;">
                <span><i class="fas fa-ruler"></i> ${player.height}</span>
                <span><i class="fas fa-weight"></i> ${player.weight}</span>
                <span><i class="fas fa-shoe-prints"></i> ${player.preferred_foot} foot</span>
                <span><i class="fas fa-star"></i> ${player.weak_foot}★ WF</span>
                <span><i class="fas fa-magic"></i> ${player.skill_moves}★ SM</span>
            </div>
        </div>
        
        <div class="modal-radar-container">
            <canvas id="modal-radar-chart"></canvas>
        </div>
        
        <div class="modal-player-stats">
            <div class="modal-stat-card">
                <div class="modal-stat-value" style="color: ${getStatColor(player.pace)}">${player.pace}</div>
                <div class="modal-stat-label">Pace</div>
            </div>
            <div class="modal-stat-card">
                <div class="modal-stat-value" style="color: ${getStatColor(player.shooting)}">${player.shooting}</div>
                <div class="modal-stat-label">Shooting</div>
            </div>
            <div class="modal-stat-card">
                <div class="modal-stat-value" style="color: ${getStatColor(player.passing)}">${player.passing}</div>
                <div class="modal-stat-label">Passing</div>
            </div>
            <div class="modal-stat-card">
                <div class="modal-stat-value" style="color: ${getStatColor(player.dribbling)}">${player.dribbling}</div>
                <div class="modal-stat-label">Dribbling</div>
            </div>
            <div class="modal-stat-card">
                <div class="modal-stat-value" style="color: ${getStatColor(player.defending)}">${player.defending}</div>
                <div class="modal-stat-label">Defending</div>
            </div>
            <div class="modal-stat-card">
                <div class="modal-stat-value" style="color: ${getStatColor(player.physical)}">${player.physical}</div>
                <div class="modal-stat-label">Physical</div>
            </div>
        </div>
    `;
    
    modal.classList.add('show');
    
    // Render radar chart
    setTimeout(() => {
        renderRadarChart('modal-radar-chart', radar);
    }, 100);
}

function closePlayerModal() {
    const modal = document.getElementById('player-modal');
    modal.classList.remove('show');
}

function getStatColor(value) {
    if (value >= 80) return '#10b981';
    if (value >= 70) return '#3b82f6';
    if (value >= 60) return '#f59e0b';
    return '#ef4444';
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('player-modal');
    if (e.target === modal) {
        closePlayerModal();
    }
});

// Autocomplete functionality
function initializeAutocomplete() {
    const inputs = [
        'search-query',
        'recommend-player',
        'compare-player-1',
        'compare-player-2',
        'compare-player-3',
        'compare-player-4'
    ];
    
    inputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            setupAutocomplete(input, inputId + '-suggestions');
        }
    });
}

function setupAutocomplete(input, suggestionsId) {
    let debounceTimer;
    
    input.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value.trim();
        
        if (query.length < 2) {
            hideSuggestions(suggestionsId);
            return;
        }
        
        debounceTimer = setTimeout(() => {
            fetchSuggestions(query, suggestionsId, input);
        }, 300);
    });
    
    input.addEventListener('blur', function() {
        setTimeout(() => hideSuggestions(suggestionsId), 200);
    });
}

async function fetchSuggestions(query, suggestionsId, inputElement) {
    try {
        const response = await fetch(`/api/autocomplete?gender=${currentGender}&query=${encodeURIComponent(query)}&limit=10`);
        const data = await response.json();
        
        if (data.success && data.suggestions.length > 0) {
            displaySuggestions(data.suggestions, suggestionsId, inputElement);
        } else {
            hideSuggestions(suggestionsId);
        }
    } catch (error) {
        console.error('Autocomplete error:', error);
    }
}

function displaySuggestions(suggestions, suggestionsId, inputElement) {
    const container = document.getElementById(suggestionsId);
    if (!container) return;
    
    container.innerHTML = suggestions.map(name => `
        <div class="autocomplete-suggestion" onclick="selectSuggestion('${name.replace(/'/g, "\\'")}', '${inputElement.id}', '${suggestionsId}')">${name}</div>
    `).join('');
    
    container.classList.add('show');
}

function hideSuggestions(suggestionsId) {
    const container = document.getElementById(suggestionsId);
    if (container) {
        container.classList.remove('show');
    }
}

function selectSuggestion(name, inputId, suggestionsId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.value = name;
    }
    hideSuggestions(suggestionsId);
}

// Keyboard shortcuts
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        if (currentSection === 'search') {
            searchPlayers();
        } else if (currentSection === 'recommend') {
            getRecommendations();
        } else if (currentSection === 'compare') {
            comparePlayers();
        }
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closePlayerModal();
    }
});

