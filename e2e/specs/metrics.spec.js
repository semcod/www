import { test, expect } from '@playwright/test';

// Skip API tests in CI - they require running backend on :8000
const skipInCI = process.env.CI ? test.skip : test;

test.describe('Metrics API', () => {
  const baseURL = 'http://localhost:9000';

  skipInCI('GET /api/metrics/standard returns standardized metrics', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/metrics/standard?limit=5`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    
    // Verify response structure
    expect(data).toHaveProperty('meta');
    expect(data).toHaveProperty('scans');
    expect(data.meta).toHaveProperty('generated_at');
    expect(data.meta).toHaveProperty('total_scans');
    expect(data.meta).toHaveProperty('returned_scans');
    expect(Array.isArray(data.scans)).toBe(true);
    
    // If scans exist, verify scan structure
    if (data.scans.length > 0) {
      const scan = data.scans[0];
      expect(scan).toHaveProperty('repository');
      expect(scan).toHaveProperty('platform');
      expect(scan).toHaveProperty('health_score');
      expect(scan).toHaveProperty('grade');
      expect(scan).toHaveProperty('metrics');
      expect(scan).toHaveProperty('scanned_at');
      expect(scan).toHaveProperty('badge_url');
      
      // Verify metrics structure
      expect(scan.metrics).toHaveProperty('files');
      expect(scan.metrics).toHaveProperty('lines_of_code');
      expect(scan.metrics).toHaveProperty('languages');
      expect(scan.metrics).toHaveProperty('complexity');
      expect(scan.metrics).toHaveProperty('duplication');
      expect(scan.metrics).toHaveProperty('quality');
      
      // Verify health_score is a number
      expect(typeof scan.health_score).toBe('number');
      expect(scan.health_score).toBeGreaterThanOrEqual(0);
      expect(scan.health_score).toBeLessThanOrEqual(100);
      
      // Verify grade is valid
      expect(['A+', 'A', 'B+', 'B', 'C', 'D', 'F', '?']).toContain(scan.grade);
    }
  });

  skipInCI('GET /api/metrics/summary returns statistics', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/metrics/summary`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    
    // Verify response structure
    expect(data).toHaveProperty('meta');
    expect(data).toHaveProperty('summary');
    expect(data.meta).toHaveProperty('generated_at');
    expect(data.meta).toHaveProperty('total_scans');
    
    // Verify summary structure
    expect(data.summary).toHaveProperty('avg_health_score');
    expect(data.summary).toHaveProperty('grade_distribution');
    expect(data.summary).toHaveProperty('total_files');
    expect(data.summary).toHaveProperty('total_lines');
    expect(data.summary).toHaveProperty('platform_distribution');
    
    // Verify avg_health_score is a number
    expect(typeof data.summary.avg_health_score).toBe('number');
  });

  skipInCI('GET /api/metrics/repository/{repo} returns specific repo metrics', async ({ request }) => {
    // First, get recent scans to find a valid repo
    const listResponse = await request.get(`${baseURL}/api/metrics/standard?limit=1`);
    const listData = await listResponse.json();
    
    if (listData.scans.length === 0) {
      test.skip();
      return;
    }
    
    const repo = listData.scans[0].repository;
    const response = await request.get(`${baseURL}/api/metrics/repository/${repo}`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    
    // Verify response structure
    expect(data).toHaveProperty('meta');
    expect(data).toHaveProperty('scan');
    expect(data.meta).toHaveProperty('repository');
    expect(data.meta).toHaveProperty('platform');
    expect(data.meta).toHaveProperty('scan_count');
    
    // Verify scan structure
    expect(data.scan).toHaveProperty('health_score');
    expect(data.scan).toHaveProperty('grade');
    expect(data.scan).toHaveProperty('metrics');
    expect(data.scan).toHaveProperty('scanned_at');
    expect(data.scan).toHaveProperty('badge_url');
  });

  skipInCI('GET /api/metrics/repository/{repo} returns 404 for non-existent repo', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/metrics/repository/nonexistent/fake-repo`);
    
    expect(response.status()).toBe(404);
  });

  skipInCI('GET /api/scans/recent returns scan history', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/scans/recent?limit=10`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    
    // Verify response structure
    expect(data).toHaveProperty('scans');
    expect(data).toHaveProperty('total');
    expect(Array.isArray(data.scans)).toBe(true);
    expect(typeof data.total).toBe('number');
  });
});
