// Smoke test: 1 request through the full path. Run before every experiment.
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, PROMPT, headers } from './lib/common.js';

export const options = {
  vus: 1,
  iterations: 1,
  thresholds: { checks: ['rate==1'] },
};

export default function () {
  const res = http.post(`${BASE_URL}/chat`, JSON.stringify({ prompt: PROMPT }), headers());
  check(res, {
    'status is 200': (r) => r.status === 200,
    'has response text': (r) => r.json('response') !== undefined && r.json('response').length > 0,
  });
}
