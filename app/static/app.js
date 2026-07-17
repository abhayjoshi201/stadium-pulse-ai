/**
 * Aura-26 Stadium Pulse Operations Dashboard Client Script.
 * 
 * WHY: Vanilla async JavaScript ensures zero frontend bundle overhead while providing
 * reactive, real-time command center telemetry injection, keyboard shortcuts for accessibility,
 * and structured result rendering with full ARIA live announcements.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const apiStatusBadge = document.getElementById('apiStatusBadge');
    const densitySlider = document.getElementById('densitySlider');
    const densityValue = document.getElementById('densityValue');
    const contextForm = document.getElementById('contextForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const notesInput = document.getElementById('notesInput');
    
    // Output Containers
    const loadingIndicator = document.getElementById('loadingIndicator');
    const emptyState = document.getElementById('emptyState');
    const resultsContainer = document.getElementById('resultsContainer');
    const riskBadge = document.getElementById('riskBadge');
    
    // Result Elements
    const summaryText = document.getElementById('summaryText');
    const probValue = document.getElementById('probValue');
    const riskTextValue = document.getElementById('riskTextValue');
    const rootCauseText = document.getElementById('rootCauseText');
    const signageText = document.getElementById('signageText');
    const directivesList = document.getElementById('directivesList');
    const paScriptText = document.getElementById('paScriptText');
    const paTabs = document.querySelectorAll('.pa-tab');
    
    // State storage for PA scripts
    let currentPaScripts = null;

    // WHY: Immediate health check verification upon load informs controllers of backend status instantly.
    async function checkApiHealth() {
        try {
            const response = await fetch('/api/v1/health');
            if (response.ok) {
                const data = await response.json();
                apiStatusBadge.textContent = data.genai_live_mode ? 'ONLINE (GENAI LIVE)' : 'ONLINE (FALLBACK ENGINE)';
                apiStatusBadge.className = 'status-badge online';
                apiStatusBadge.setAttribute('aria-label', `API Status: ${apiStatusBadge.textContent}`);
            } else {
                throw new Error('Health check non-200');
            }
        } catch (err) {
            apiStatusBadge.textContent = 'API OFFLINE / ERR';
            apiStatusBadge.className = 'status-badge offline';
            apiStatusBadge.setAttribute('aria-label', 'API Status: Offline or Error');
            console.error('API health check failed:', err);
        }
    }

    // Initialize health probe
    checkApiHealth();

    // WHY: Real-time slider feedback allows precise concourse capacity threshold adjustment.
    densitySlider.addEventListener('input', (e) => {
        densityValue.textContent = `${e.target.value}%`;
        densitySlider.setAttribute('aria-valuenow', e.target.value);
    });

    // Keyboard Accessibility: Ctrl+Enter or Cmd+Enter inside form submits instantly
    notesInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            contextForm.dispatchEvent(new Event('submit'));
        }
    });

    // Keyboard Accessibility: Escape key resets view back to empty state for rapid triage
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !resultsContainer.classList.contains('hidden')) {
            resultsContainer.classList.add('hidden');
            emptyState.classList.remove('hidden');
            riskBadge.textContent = 'AWAITING SYNTHESIS';
            riskBadge.className = 'risk-badge risk-low';
            notesInput.focus();
        }
    });

    // PA Tab Switcher Logic with ARIA updates
    paTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            paTabs.forEach(t => {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');
            
            if (currentPaScripts) {
                const lang = tab.getAttribute('data-lang');
                paScriptText.textContent = currentPaScripts[lang] || currentPaScripts.english;
            }
        });
    });

    // Form Submission / GenAI Context Injection
    contextForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Disable button & show loading state
        analyzeBtn.disabled = true;
        emptyState.classList.add('hidden');
        resultsContainer.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        riskBadge.textContent = 'SYNTHESIZING...';
        riskBadge.className = 'risk-badge risk-moderate';
        loadingIndicator.setAttribute('aria-busy', 'true');

        const formData = new FormData(contextForm);
        const payload = {
            stadium_id: 'metlife_stadium_ny_nj',
            zone_id: formData.get('zone_id'),
            user_role: formData.get('user_role'),
            match_phase: formData.get('match_phase'),
            crowd_density_percentage: parseFloat(formData.get('crowd_density_percentage')),
            incident_type: formData.get('incident_type'),
            additional_notes: formData.get('additional_notes') || ''
        };

        try {
            // WHY: Send structured JSON to our FastAPI backend for Pydantic validation & GenAI reasoning.
            const response = await fetch('/api/v1/crowd/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'API request failed');
            }

            const data = await response.json();
            renderResults(data);

        } catch (error) {
            console.error('Synthesis error:', error);
            alert(`Error synthesizing crowd intelligence: ${error.message}`);
            emptyState.classList.remove('hidden');
        } finally {
            loadingIndicator.classList.add('hidden');
            loadingIndicator.setAttribute('aria-busy', 'false');
            analyzeBtn.disabled = false;
        }
    });

    /**
     * Renders the structured GenAI response onto the command center UI.
     * WHY: Clear visual hierarchy and ARIA live announcements ensure immediate comprehension during high-pressure crowd situations.
     */
    function renderResults(data) {
        // Update Risk Badge
        const riskLevel = data.risk_assessment.risk_level.toLowerCase();
        riskBadge.textContent = `RISK: ${data.risk_assessment.risk_level}`;
        riskBadge.className = `risk-badge risk-${riskLevel}`;

        // Populate Summary & Risk Card
        summaryText.textContent = data.summary_for_role;
        probValue.textContent = `${data.risk_assessment.bottleneck_probability}%`;
        riskTextValue.textContent = data.risk_assessment.risk_level;
        rootCauseText.textContent = data.risk_assessment.root_cause_analysis;

        // Populate LED Signage Payload
        signageText.textContent = data.digital_signage_payload;

        // Populate Prioritized Directives
        directivesList.innerHTML = '';
        data.steward_directives.forEach(dir => {
            const li = document.createElement('li');
            li.className = `directive-item priority-${dir.priority}`;
            li.innerHTML = `
                <span class="directive-badge">P${dir.priority}</span>
                <div>
                    <span class="directive-target">${dir.assigned_target}</span>
                    <span class="directive-text">${dir.action_instruction}</span>
                </div>
            `;
            directivesList.appendChild(li);
        });

        // Populate Multilingual PA Scripts
        currentPaScripts = data.pa_broadcast_scripts;
        const activeTab = document.querySelector('.pa-tab.active');
        const activeLang = activeTab ? activeTab.getAttribute('data-lang') : 'english';
        paScriptText.textContent = currentPaScripts[activeLang] || currentPaScripts.english;

        // Reveal results container and focus for screen readers
        resultsContainer.classList.remove('hidden');
        summaryText.focus();
    }
});
