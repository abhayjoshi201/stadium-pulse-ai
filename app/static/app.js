/**
 * Stadium Pulse AI Operations Dashboard Client Script.
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
    
    // Mode Switcher Elements
    const tabSingle = document.getElementById('tabSingle');
    const tabBatch = document.getElementById('tabBatch');
    const modeDesc = document.getElementById('modeDesc');
    const batchForm = document.getElementById('batchForm');
    const batchBtn = document.getElementById('batchBtn');
    const csvInput = document.getElementById('csvInput');
    
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

    // Mode Switcher Listeners
    if (tabSingle && tabBatch) {
        tabSingle.addEventListener('click', () => {
            tabSingle.classList.add('active');
            tabSingle.setAttribute('aria-selected', 'true');
            tabBatch.classList.remove('active');
            tabBatch.setAttribute('aria-selected', 'false');
            contextForm.classList.remove('hidden');
            contextForm.setAttribute('aria-hidden', 'false');
            batchForm.classList.add('hidden');
            batchForm.setAttribute('aria-hidden', 'true');
            modeDesc.textContent = "Configure real-time matchday context vectors to drive GenAI reasoning decisions.";
        });
        tabBatch.addEventListener('click', () => {
            tabBatch.classList.add('active');
            tabBatch.setAttribute('aria-selected', 'true');
            tabSingle.classList.remove('active');
            tabSingle.setAttribute('aria-selected', 'false');
            batchForm.classList.remove('hidden');
            batchForm.setAttribute('aria-hidden', 'false');
            contextForm.classList.add('hidden');
            contextForm.setAttribute('aria-hidden', 'true');
            modeDesc.textContent = "Paste or upload high-frequency CSV gate sensor datasets for O(M * log N) batch classification.";
        });
    }

    if (batchForm) {
        batchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            batchBtn.disabled = true;
            emptyState.classList.add('hidden');
            resultsContainer.classList.add('hidden');
            loadingIndicator.classList.remove('hidden');
            riskBadge.textContent = 'BATCH EVALUATING...';
            riskBadge.className = 'risk-badge risk-moderate';

            try {
                const response = await fetch('/api/v1/telemetry/batch-csv-upload', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ csv_payload: csvInput.value })
                });
                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || 'Batch evaluation failed');
                }
                const data = await response.json();
                renderBatchResults(data.batch_evaluation_results);
            } catch (err) {
                alert(`Batch CSV Error: ${err.message}`);
                emptyState.classList.remove('hidden');
            } finally {
                loadingIndicator.classList.add('hidden');
                batchBtn.disabled = false;
            }
        });
    }

    function renderBatchResults(batchData) {
        summaryText.textContent = `[BATCH EVALUATION COMPLETE] Analyzed ${batchData.batch_summary.total_sectors_analyzed} sectors in ${batchData.batch_summary.algorithmic_complexity}. Average density: ${batchData.batch_summary.average_stadium_density} | Critical Bottleneck Zones: ${batchData.batch_summary.critical_bottleneck_zones}.`;
        probValue.textContent = `${batchData.batch_summary.critical_bottleneck_zones} ZONE(S)`;
        riskTextValue.textContent = batchData.batch_summary.critical_bottleneck_zones > 0 ? "CRITICAL BATCH" : "NOMINAL";
        rootCauseText.textContent = `Algorithm: ${batchData.batch_summary.algorithmic_complexity}. Binary search threshold cutoffs evaluated instantaneously across all rows without linear traversal.`;
        signageText.textContent = `⚠️ MULTI-GATE BATCH PROCESSED. ${batchData.batch_summary.critical_bottleneck_zones} CRITICAL ZONES IDENTIFIED FOR PULSE METERING.`;
        
        directivesList.innerHTML = '';
        batchData.sector_evaluations.forEach((evalItem, idx) => {
            const li = document.createElement('li');
            li.className = `directive-item priority-${evalItem.crush_risk_index >= 95 ? 1 : 2}`;
            li.innerHTML = `
                <span class="directive-badge">ROW ${evalItem.row_id}</span>
                <div>
                    <span class="directive-target">${evalItem.zone_id} (${evalItem.raw_density} density | Index: ${evalItem.crush_risk_index})</span>
                    <span class="directive-text">Mode: <strong>${evalItem.recommended_action_mode}</strong> | Overflow: ${evalItem.adjacent_overflow_targets.join(', ')}</span>
                </div>
            `;
            directivesList.appendChild(li);
        });

        paScriptText.textContent = `Batch evaluation completed across ${batchData.batch_summary.total_sectors_analyzed} concourse sectors. Stewards deployed to ${batchData.batch_summary.critical_bottleneck_zones} critical bottleneck zones.`;
        resultsContainer.classList.remove('hidden');
        summaryText.focus();
    }

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
