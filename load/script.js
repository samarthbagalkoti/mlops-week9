import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '2m',
};

export default function () {
  // 80% good requests, 20% slowish, plus occasional error endpoint
  if (Math.random() < 0.05) {
    http.get('http://localhost:8000/error');
  } else {
    const q = Math.random() < 0.2 ? 0.9 : 0.5;
    http.get(`http://localhost:8000/predict?q=${q}`);
  }
  sleep(0.1);
}

