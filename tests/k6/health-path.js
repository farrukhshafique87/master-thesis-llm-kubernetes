// Overhead-isolation test: hits /health (no LLM inference). Because inference
// takes seconds, small security overhead (mTLS, gateway, policies) would be
// invisible in /chat latency. This path exposes the per-request cost of the
// security layers themselves.
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, headers } from './lib/common.js';

export const options = {
  scenarios: {
    health: {
      executor: 'constant-arrival-rate',
      rate: parseInt(__ENV.RATE || '50'),
      timeUnit: '1s',
      duration: __ENV.DURATION || '2m',
      preAllocatedVUs: 20,
      maxVUs: 100,
    },
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/health`, headers());
  check(res, { 'status is 200': (r) => r.status === 200 });
}
