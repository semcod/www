// Comprehensive API validation tests for GitHub OAuth simulation
// Tests all OAuth endpoints and error scenarios

const axios = require('axios');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8003';
const MOCK_GITHUB_URL = process.env.MOCK_GITHUB_URL || 'http://localhost:4010';

describe('OAuth API Validation Tests', () => {
  let authToken = null;
  let testCode = null;

  beforeAll(async () => {
    // Verify all services are running
    try {
      await axios.get(`${FRONTEND_URL}`);
      await axios.get(`${MOCK_GITHUB_URL}/health`);
      await axios.get(`${BACKEND_URL}/api/health`);
    } catch (error) {
      throw new Error('Services not running properly');
    }
  });

  describe('Mock GitHub Server API', () => {
    test('health check returns correct status', async () => {
      const response = await axios.get(`${MOCK_GITHUB_URL}/health`);
      expect(response.status).toBe(200);
      expect(response.data.mode).toBe('github-simulation');
      expect(response.data.users).toContain('tom-sapletta-com');
    });

    test('code registration works', async () => {
      testCode = `test_${Date.now()}`;
      const response = await axios.post(`${MOCK_GITHUB_URL}/api/_sim/issue-code`, {
        code: testCode,
        login: 'tom-sapletta-com',
        state: 'test123'
      });
      expect(response.status).toBe(200);
      expect(response.data.ok).toBe(true);
    });

    test('token exchange with valid code', async () => {
      const response = await axios.post(`${MOCK_GITHUB_URL}/login/oauth/access_token`, {
        client_id: 'Iv1.mock_test_client',
        client_secret: 'mock_secret_for_testing',
        code: testCode
      }, {
        headers: { Accept: 'application/json' }
      });
      
      expect(response.status).toBe(200);
      expect(response.data.access_token).toBeTruthy();
      expect(response.data.access_token).toMatch(/^gho_mock_/);
      expect(response.data.token_type).toBe('bearer');
      
      authToken = response.data.access_token;
    });

    test('token exchange with invalid code fails', async () => {
      try {
        await axios.post(`${MOCK_GITHUB_URL}/login/oauth/access_token`, {
          client_id: 'Iv1.mock_test_client',
          client_secret: 'mock_secret_for_testing',
          code: 'invalid_code_999'
        }, {
          headers: { Accept: 'application/json' }
        });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.response.status).toBe(400);
        expect(error.response.data.error).toBe('bad_verification_code');
      }
    });

    test('user profile with valid token', async () => {
      const response = await axios.get(`${MOCK_GITHUB_URL}/user`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      
      expect(response.status).toBe(200);
      expect(response.data.login).toBe('tom-sapletta-com');
      expect(response.data.name).toBe('Tom Sapletta');
      expect(response.data.id).toBe(5669315);
      expect(response.data.email).toBe('tom@sapletta.com');
    });

    test('user profile with invalid token fails', async () => {
      try {
        await axios.get(`${MOCK_GITHUB_URL}/user`, {
          headers: { Authorization: 'Bearer gho_invalid_token' }
        });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.response.status).toBe(401);
      }
    });

    test('user repositories with valid token', async () => {
      const response = await axios.get(`${MOCK_GITHUB_URL}/user/repos`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      
      expect(response.status).toBe(200);
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThanOrEqual(2);
      
      const repoNames = response.data.map(repo => repo.name);
      expect(repoNames).toContain('semcod');
      expect(repoNames).toContain('letwhisper');
    });

    test('OAuth authorize page returns HTML', async () => {
      const response = await axios.get(`${MOCK_GITHUB_URL}/login/oauth/authorize`, {
        params: {
          client_id: 'Iv1.mock_test_client',
          redirect_uri: `${BACKEND_URL}/auth/callback`,
          scope: 'read:user,repo',
          state: 'test123'
        }
      });
      
      expect(response.status).toBe(200);
      expect(response.headers['content-type']).toContain('text/html');
      expect(response.data).toContain('Mock GitHub Login');
      expect(response.data).toContain('tom-sapletta-com');
    });
  });

  describe('Backend OAuth API', () => {
    test('OAuth start redirects correctly', async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/auth/github`, {
          maxRedirects: 0,
          validateStatus: () => true
        });
        
        expect(response.status).toBe(307);
        expect(response.headers.location).toContain('localhost:4010');
        expect(response.headers.location).toContain('login/oauth/authorize');
      } catch (error) {
        // Axios throws for redirects, check the error response
        expect(error.response.status).toBe(307);
        expect(error.response.headers.location).toContain('localhost:4010');
      }
    });

    test('OAuth callback with valid code', async () => {
      // First register a code with mock server
      const callbackCode = `callback_${Date.now()}`;
      await axios.post(`${MOCK_GITHUB_URL}/api/_sim/issue-code`, {
        code: callbackCode,
        login: 'tom-sapletta-com',
        state: 'test123'
      });

      try {
        const response = await axios.get(`${BACKEND_URL}/auth/callback`, {
          params: { code: callbackCode },
          maxRedirects: 0,
          validateStatus: () => true
        });
        
        expect(response.status).toBe(307);
        expect(response.headers.location).toContain(FRONTEND_URL);
        expect(response.headers.location).toContain('session=');
      } catch (error) {
        expect(error.response.status).toBe(307);
        expect(error.response.headers.location).toContain(FRONTEND_URL);
        expect(error.response.headers.location).toContain('session=');
      }
    });

    test('OAuth callback with invalid code fails', async () => {
      try {
        await axios.get(`${BACKEND_URL}/auth/callback`, {
          params: { code: 'invalid_code_999' }
        });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.response.status).toBe(400);
      }
    });

    test('protected API requires authentication', async () => {
      try {
        await axios.get(`${BACKEND_URL}/api/me`);
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.response.status).toBe(401);
      }
    });
  });

  describe('Session Management', () => {
    let sessionToken = null;

    test('create session via OAuth callback', async () => {
      // Register a new code
      const sessionCode = `session_${Date.now()}`;
      await axios.post(`${MOCK_GITHUB_URL}/api/_sim/issue-code`, {
        code: sessionCode,
        login: 'tom-sapletta-com',
        state: 'test123'
      });

      try {
        const response = await axios.get(`${BACKEND_URL}/auth/callback`, {
          params: { code: sessionCode },
          maxRedirects: 0,
          validateStatus: () => true
        });
        
        // Extract session token from redirect URL
        const location = response.headers.location;
        const sessionMatch = location.match(/session=([^&]+)/);
        expect(sessionMatch).toBeTruthy();
        
        sessionToken = sessionMatch[1];
        expect(sessionToken).toBeTruthy();
      } catch (error) {
        const location = error.response.headers.location;
        const sessionMatch = location.match(/session=([^&]+)/);
        sessionToken = sessionMatch[1];
      }
    });

    test('access protected API with session token', async () => {
      const response = await axios.get(`${BACKEND_URL}/api/me`, {
        headers: { Authorization: `Bearer ${sessionToken}` }
      });
      
      expect(response.status).toBe(200);
      expect(response.data.login).toBe('tom-sapletta-com');
      expect(response.data.name).toBe('Tom Sapletta');
    });

    test('access user repositories with session', async () => {
      const response = await axios.get(`${BACKEND_URL}/api/repos`, {
        headers: { Authorization: `Bearer ${sessionToken}` }
      });
      
      expect(response.status).toBe(200);
      expect(Array.isArray(response.data)).toBe(true);
      
      if (response.data.length > 0) {
        const repoNames = response.data.map(repo => repo.name);
        expect(repoNames).toContain('semcod');
      }
    });
  });

  describe('Error Handling', () => {
    test('handles malformed OAuth requests', async () => {
      try {
        await axios.get(`${BACKEND_URL}/auth/callback`);
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.response.status).toBe(400);
      }
    });

    test('handles invalid session tokens', async () => {
      try {
        await axios.get(`${BACKEND_URL}/api/me`, {
          headers: { Authorization: 'Bearer invalid_session_token' }
        });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.response.status).toBe(401);
      }
    });

    test('mock server handles concurrent requests', async () => {
      const codes = Array.from({ length: 10 }, (_, i) => `concurrent_${Date.now()}_${i}`);
      
      // Register multiple codes concurrently
      const promises = codes.map(code =>
        axios.post(`${MOCK_GITHUB_URL}/api/_sim/issue-code`, {
          code,
          login: 'tom-sapletta-com',
          state: 'test123'
        })
      );
      
      const results = await Promise.all(promises);
      results.forEach(response => {
        expect(response.status).toBe(200);
        expect(response.data.ok).toBe(true);
      });
    });
  });
});
