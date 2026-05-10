// MDRS calculator — reference implementation
// Implements Section 5 of "A Practical Cybersecurity Framework for Legacy Medical Devices"
//
// Two-stage scoring:
//   Stage 1 — weighted composite per equation (1):
//     MDRS_comp = (CIS × 0.35) + (ES × 0.25) + (DCI × 0.20) + (NEF × 0.15) + (CCD × 0.05)
//   Stage 2 — irreversibility-driven tier floor + CCD-driven tier promoter:
//     CIS ≥ 9          → minimum tier HIGH
//     CIS = 7 or 8     → minimum tier MEDIUM
//     CCD ≥ 8          → tier promoted by one level (capped at CRITICAL)

'use strict';

const DEFAULT_WEIGHTS = {
  cis: 0.35,
  es:  0.25,
  dci: 0.20,
  nef: 0.15,
  ccd: 0.05
};

const TIER_ORDER = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

const TIER_ACTIONS = {
  CRITICAL: {
    timeline: 'Immediate / 24 hours',
    text: 'Immediate isolation or shutdown of non-life-critical devices; 24-hour escalation to CISO and CMO; emergency vendor engagement; activate incident response plan.',
    owners: 'For CRITICAL: CISO + CMO + clinical engineering director within 24 hours.',
    timelineInline: '24 hours',
    review: 'Quarterly for CRITICAL devices.'
  },
  HIGH: {
    timeline: '30 days',
    text: 'Remediation within 30 days; compensating controls deployed within 72 hours; weekly monitoring cadence; board-level reporting.',
    owners: 'For HIGH: CISO + clinical engineering director within 72 hours.',
    timelineInline: '30 days',
    review: 'Semi-annually for HIGH devices.'
  },
  MEDIUM: {
    timeline: '90 days',
    text: 'Remediation within 90 days; compensating-control gap analysis; monthly monitoring; include in quarterly security review.',
    owners: 'For MEDIUM: clinical engineering with InfoSec consultation within 1 week.',
    timelineInline: '90 days',
    review: 'Annually for MEDIUM devices.'
  },
  LOW: {
    timeline: '12 months',
    text: 'Annual review cycle; document and accept residual risk per ISO 14971 cl.8 with CISO sign-off; include in next refresh budget cycle.',
    owners: 'For LOW: clinical engineering, with InfoSec annual review.',
    timelineInline: '12 months',
    review: 'Annually for LOW devices.'
  }
};

const HELP_BY_BAND = {
  cis: [
    [9, 10, '9–10: life-sustaining (ventilators, infusion pumps, pacemaker programmers)'],
    [7, 8.5, '7–8: critical monitoring (ICU, surgical, anaesthesia)'],
    [5, 6.5, '5–6: diagnostic imaging (MRI, CT, X-ray, PACS)'],
    [3, 4.5, '3–4: administrative / scheduling'],
    [1, 2.5, '1–2: non-clinical support']
  ],
  es: [
    [9, 10, '9–10: network-accessible with public exploit (Shodan-visible, known CVE with PoC)'],
    [7, 8.5, '7–8: network-accessible without public exploit'],
    [5, 6.5, '5–6: adjacent-network or physical-proximity required'],
    [3, 4.5, '3–4: authenticated local or service-port access'],
    [1, 2.5, '1–2: privileged physical access only']
  ],
  dci: [
    [9, 10, '9–10: single point of failure in critical care unit'],
    [7, 8.5, '7–8: redundancy available but switchover >30 min'],
    [5, 6.5, '5–6: multiple redundant devices; switchover <15 min'],
    [1, 4.5, '1–4: non-critical with manual workaround']
  ],
  nef: [
    [9, 10, '9–10: internet-facing or flat network, OR exposed unprotected service port in shared space'],
    [7, 8.5, '7–8: internal network, no VLAN isolation'],
    [5, 6.5, '5–6: VLAN-isolated with permissive ACLs'],
    [3, 4.5, '3–4: VLAN-isolated with restrictive ACLs and physical-access controls'],
    [1, 2.5, '1–2: air-gapped, attended-only physical access']
  ],
  ccd: [
    [9, 10, '9–10: no compensating controls in place'],
    [7, 8.5, '7–8: partial controls (1–2 STRIDE categories covered)'],
    [5, 6.5, '5–6: controls in 3–4 STRIDE categories'],
    [3, 4.5, '3–4: comprehensive controls, not formally tested'],
    [1, 2.5, '1–2: comprehensive controls, validated annually']
  ]
};

// ---------- Pure scoring functions (also exported for tests) ----------

function computeComposite(scores, weights) {
  const w = weights || DEFAULT_WEIGHTS;
  return (scores.cis * w.cis) +
         (scores.es  * w.es)  +
         (scores.dci * w.dci) +
         (scores.nef * w.nef) +
         (scores.ccd * w.ccd);
}

function compositeToTier(composite) {
  if (composite >= 8.0) return 'CRITICAL';
  if (composite >= 6.0) return 'HIGH';
  if (composite >= 3.5) return 'MEDIUM';
  return 'LOW';
}

function applyIrreversibilityFloor(tier, cis) {
  if (cis >= 9 && tierRank(tier) < tierRank('HIGH')) return 'HIGH';
  if (cis >= 7 && cis < 9 && tierRank(tier) < tierRank('MEDIUM')) return 'MEDIUM';
  return tier;
}

function applyCCDPromoter(tier, ccd) {
  if (ccd >= 8) {
    const idx = TIER_ORDER.indexOf(tier);
    if (idx < TIER_ORDER.length - 1) return TIER_ORDER[idx + 1];
  }
  return tier;
}

function tierRank(tier) { return TIER_ORDER.indexOf(tier); }

function score(scores, weights) {
  const composite = computeComposite(scores, weights);
  const rounded = Math.round(composite * 1000) / 1000;
  const baseTier = compositeToTier(rounded);
  const afterFloor = applyIrreversibilityFloor(baseTier, scores.cis);
  const finalTier = applyCCDPromoter(afterFloor, scores.ccd);

  const floorActive = afterFloor !== baseTier;
  const promoterActive = finalTier !== afterFloor;

  return {
    composite: rounded,
    baseTier,
    afterFloor,
    finalTier,
    floorActive,
    promoterActive,
    inputs: { ...scores },
    weights: weights || DEFAULT_WEIGHTS
  };
}

function helpFor(dim, value) {
  const bands = HELP_BY_BAND[dim] || [];
  for (const [lo, hi, text] of bands) {
    if (value >= lo && value <= hi) return text;
  }
  return '';
}

// ---------- DOM wiring ----------

if (typeof document !== 'undefined') {
  const dims = ['cis', 'es', 'dci', 'nef', 'ccd'];
  let currentMode = 'guided';

  // Guided mode reads from radio buttons; falls back to defaults that won't trigger nonsense
  function readScoresGuided() {
    const out = {};
    let allAnswered = true;
    for (const d of dims) {
      const radios = document.querySelectorAll(`input[name="q-${d}"]:checked`);
      if (radios.length > 0) {
        out[d] = parseFloat(radios[0].value);
      } else {
        out[d] = 5.5; // neutral midpoint until answered
        allAnswered = false;
      }
    }
    out._allAnswered = allAnswered;
    return out;
  }

  function readScoresDirect() {
    return Object.fromEntries(dims.map(d => [d, parseFloat(document.getElementById(d).value)]));
  }

  function readScores() {
    return currentMode === 'guided' ? readScoresGuided() : readScoresDirect();
  }

  function readWeights() {
    return {
      cis: parseFloat(document.getElementById('w-cis').value) || 0,
      es:  parseFloat(document.getElementById('w-es').value)  || 0,
      dci: parseFloat(document.getElementById('w-dci').value) || 0,
      nef: parseFloat(document.getElementById('w-nef').value) || 0,
      ccd: parseFloat(document.getElementById('w-ccd').value) || 0
    };
  }

  function updateOutputs() {
    if (currentMode !== 'direct') return;
    dims.forEach(d => {
      const value = parseFloat(document.getElementById(d).value);
      document.getElementById(`${d}-out`).textContent = value.toFixed(1);
      document.getElementById(`${d}-help`).textContent = helpFor(d, value);
    });
  }

  function updateWeightLabels(w) {
    const cisEl = document.getElementById('weight-cis');
    if (cisEl) cisEl.textContent = (w.cis * 100).toFixed(0) + '%';
    const esEl = document.getElementById('weight-es');
    if (esEl) esEl.textContent = (w.es * 100).toFixed(0) + '%';
    const dciEl = document.getElementById('weight-dci');
    if (dciEl) dciEl.textContent = (w.dci * 100).toFixed(0) + '%';
    const nefEl = document.getElementById('weight-nef');
    if (nefEl) nefEl.textContent = (w.nef * 100).toFixed(0) + '%';
    const ccdEl = document.getElementById('weight-ccd');
    if (ccdEl) ccdEl.textContent = (w.ccd * 100).toFixed(0) + '% + tier promoter';

    const sum = w.cis + w.es + w.dci + w.nef + w.ccd;
    const warning = document.getElementById('weight-warning');
    const sumDisplay = document.getElementById('weight-sum');
    sumDisplay.textContent = sum.toFixed(3);
    if (Math.abs(sum - 1.0) > 0.001) {
      warning.classList.remove('hidden');
    } else {
      warning.classList.add('hidden');
    }
  }

  function recompute() {
    const scores = readScores();
    const weights = readWeights();
    const result = score(scores, weights);

    document.getElementById('result-composite').textContent = result.composite.toFixed(3);

    const tierEl = document.getElementById('result-tier');
    tierEl.textContent = result.finalTier;

    const card = document.getElementById('result-card');
    card.className = 'result-card tier-' + result.finalTier;

    // Score-summary table
    document.getElementById('rs-cis').textContent = scores.cis.toFixed(1);
    document.getElementById('rs-es').textContent  = scores.es.toFixed(1);
    document.getElementById('rs-dci').textContent = scores.dci.toFixed(1);
    document.getElementById('rs-nef').textContent = scores.nef.toFixed(1);
    document.getElementById('rs-ccd').textContent = scores.ccd.toFixed(1);

    // Explainer list
    const explain = document.getElementById('explain-list');
    explain.innerHTML = '';
    const items = [];

    if (currentMode === 'guided' && !scores._allAnswered) {
      items.push(`<span class="not-applied">Awaiting answers — answer all five questions for a final score. Showing partial result with neutral defaults for unanswered dimensions.</span>`);
    }

    items.push(`Composite ${result.composite.toFixed(3)} → base tier <strong>${result.baseTier}</strong> from range mapping.`);

    if (result.floorActive) {
      const reason = scores.cis >= 9
        ? `CIS=${scores.cis} (life-sustaining) imposes minimum tier HIGH`
        : `CIS=${scores.cis} (critical monitoring) imposes minimum tier MEDIUM`;
      items.push(`<span class="applied">Irreversibility floor applied:</span> ${reason} → tier <strong>${result.afterFloor}</strong>.`);
    } else if (scores.cis >= 7) {
      items.push(`<span class="not-applied">Irreversibility floor not active (composite already meets or exceeds the floor).</span>`);
    } else {
      items.push(`<span class="not-applied">Irreversibility floor not applicable (CIS &lt; 7).</span>`);
    }

    if (result.promoterActive) {
      items.push(`<span class="applied">CCD promoter applied:</span> CCD=${scores.ccd} (≥8, no or minimal compensating controls) → tier promoted to <strong>${result.finalTier}</strong>.`);
    } else if (scores.ccd >= 8) {
      items.push(`<span class="not-applied">CCD promoter would apply (CCD ≥ 8) but tier already at CRITICAL ceiling.</span>`);
    } else {
      items.push(`<span class="not-applied">CCD promoter not active (CCD &lt; 8).</span>`);
    }

    items.forEach(html => {
      const li = document.createElement('li');
      li.innerHTML = html;
      explain.appendChild(li);
    });

    // Action card and next-steps owners/timeline/review
    const action = TIER_ACTIONS[result.finalTier];
    document.getElementById('result-action-text').textContent = action.text;
    document.getElementById('result-timeline').textContent = action.timeline;
    const ownersEl = document.getElementById('next-owners');
    if (ownersEl) ownersEl.textContent = action.owners;
    const tinlEl = document.getElementById('next-timeline-inline');
    if (tinlEl) tinlEl.textContent = action.timelineInline;
    const reviewEl = document.getElementById('next-review');
    if (reviewEl) reviewEl.textContent = action.review;

    updateOutputs();
    updateWeightLabels(weights);

    window._lastResult = result;
  }

  function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.mode === mode);
    });
    document.querySelectorAll('.mode-panel').forEach(p => {
      p.classList.toggle('active', p.id === 'mode-' + mode);
    });
    recompute();
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Mode toggle
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', () => setMode(btn.dataset.mode));
    });

    // Direct-mode sliders
    dims.forEach(d => {
      const el = document.getElementById(d);
      if (el) el.addEventListener('input', recompute);
    });

    // Guided-mode radio buttons
    dims.forEach(d => {
      document.querySelectorAll(`input[name="q-${d}"]`).forEach(r => {
        r.addEventListener('change', recompute);
      });
    });

    // Weight inputs
    ['w-cis', 'w-es', 'w-dci', 'w-nef', 'w-ccd'].forEach(id => {
      document.getElementById(id).addEventListener('input', recompute);
    });

    document.getElementById('reset-weights').addEventListener('click', () => {
      document.getElementById('w-cis').value = DEFAULT_WEIGHTS.cis;
      document.getElementById('w-es').value  = DEFAULT_WEIGHTS.es;
      document.getElementById('w-dci').value = DEFAULT_WEIGHTS.dci;
      document.getElementById('w-nef').value = DEFAULT_WEIGHTS.nef;
      document.getElementById('w-ccd').value = DEFAULT_WEIGHTS.ccd;
      recompute();
    });

    // Presets — populate direct-mode sliders, switch to direct mode, and recompute
    document.querySelectorAll('.preset').forEach(btn => {
      btn.addEventListener('click', () => {
        document.getElementById('cis').value = btn.dataset.cis;
        document.getElementById('es').value  = btn.dataset.es;
        document.getElementById('dci').value = btn.dataset.dci;
        document.getElementById('nef').value = btn.dataset.nef;
        document.getElementById('ccd').value = btn.dataset.ccd;
        setMode('direct');
        document.getElementById('calculator').scrollIntoView({ behavior: 'smooth' });
      });
    });

    document.getElementById('export-json').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(window._lastResult, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mdrs-${window._lastResult.finalTier.toLowerCase()}-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });

    document.getElementById('copy-summary').addEventListener('click', () => {
      const r = window._lastResult;
      const summary = [
        `MDRS Score Summary`,
        `------------------`,
        `Inputs: CIS=${r.inputs.cis}, ES=${r.inputs.es}, DCI=${r.inputs.dci}, NEF=${r.inputs.nef}, CCD=${r.inputs.ccd}`,
        `Composite: ${r.composite.toFixed(3)}`,
        `Base tier: ${r.baseTier}`,
        `Irreversibility floor: ${r.floorActive ? 'applied → ' + r.afterFloor : 'not applied'}`,
        `CCD promoter: ${r.promoterActive ? 'applied → ' + r.finalTier : 'not applied'}`,
        `Final tier: ${r.finalTier}`,
        `Action timeline: ${TIER_ACTIONS[r.finalTier].timeline}`
      ].join('\n');
      navigator.clipboard.writeText(summary).then(() => {
        const btn = document.getElementById('copy-summary');
        const orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = orig, 1500);
      });
    });

    recompute();
  });
}

// Export pure functions for Node-based testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    computeComposite,
    compositeToTier,
    applyIrreversibilityFloor,
    applyCCDPromoter,
    score,
    DEFAULT_WEIGHTS,
    TIER_ORDER
  };
}
