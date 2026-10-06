// EXP-01 baseline load: constant virtual users on the full inference path.
// Example:
//   k6 run -e BASE_URL=http://localhost:8010 -e VUS=1 -e DURATION=5m \
//     -e RUN_ID=exp01-r1 --summary-export=results/exp-01-baseline/exp01-r1.json \
//     tests/k6/baseline.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';
import { BASE_URL, PROMPT, THINK_TIME, headers } from './lib/common.js';

const tokensPerSecond = new Trend('llm_tokens_per_second');

export const options = {
  scenarios: {
    baseline: {
      executor: 'constant-vus',
      vus: parseInt(__ENV.VUS || '1'),
      duration: __ENV.DURATION || '5m',
    },
  },
  thresholds: {
    // Acceptance thresholds (NOT results): see research integrity rule 7.
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<30000'],
  },
};

export default function () {
  const res = http.post(`${BASE_URL}/chat`, JSON.stringify({ prompt: PROMPT }), headers());

  const ok = check(res, {
    'status is 200': (r) => r.status === 200,
    'response contains data': (r) => r.body && r.body.length > 0,
  });

  if (ok) {
    const tps = res.json('tokens_per_second');
    if (tps) tokensPerSecond.add(tps);
  }

  sleep(THINK_TIME);
}
