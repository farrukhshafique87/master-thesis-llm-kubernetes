// Shared settings for all k6 scripts. Everything that must stay constant
// between experiments lives here (controlled variables).
export const BASE_URL = __ENV.BASE_URL || 'http://localhost:8010';
export const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';          // used in secure runs
export const PROMPT = __ENV.PROMPT || 'Explain Kubernetes in one sentence.';
export const THINK_TIME = parseFloat(__ENV.THINK_TIME || '1');
export const RUN_ID = __ENV.RUN_ID || 'manual';

export function headers() {
  const h = { 'Content-Type': 'application/json' };
  if (AUTH_TOKEN) {
    h['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return { headers: h, tags: { run_id: RUN_ID } };
}
