#!/usr/bin/env node
/**
 * Simple API test runner for GitHub OAuth simulation
 * Tests all OAuth endpoints and validates the complete flow
 */

const axios = require('axios');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8003';
const MOCK_GITHUB_URL = process.env.MOCK_GITHUB_URL || 'http://localhost:4010';

let testResults = {
  passed: 0,
  failed: 0,
  total: 0
};

function assert(condition, message) {
  testResults.total++;
  if (condition) {
    console.log(`✅ ${message}`);
    testResults.passed++;
  } else {
    console.log(`❌ ${message}`);
    testResults.failed++;
  }
}

async function test(name, testFn) {
  console.log(`\n🧪 ${name}`);
  try {
    await testFn();
  } catch (error) {
    console.log(`❌ ${name} - Error: ${error.message}`);
    testResults.failed++;
    testResults.total++;
  }
}

async function checkServer(url) {
  try {
    const response = await axios.get(url);
    return response.status === 200;
  } catch {
    return false;
  }
}

async function runTests() {
  console.log('🚀 GitHub OAuth Simulation - API Test Suite');
  console.log('=' .repeat(50));

  // Check if all services are running
  console.log('🔍 Checking service availability...');
  const frontendOk = await checkServer(FRONTEND_URL);
  const backendOk = await checkServer(`${BACKEND_URL}/api/health`);
  const mockOk = await checkServer(`${MOCK_GITHUB_URL}/health`);

  assert(frontendOk, `Frontend server at ${FRONTEND_URL}`);
  assert(backendOk, `Backend server at ${BACKEND_URL}`);
  assert(mockOk, `Mock GitHub server at ${MOCK_GITHUB_URL}`);

  if (!frontendOk || !backendOk || !mockOk) {
    console.log('\n❌ Some services are not running. Please start them first:');
    console.log('docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d');
    return;
  }

  let authToken = null;
  let sessionToken = null;

  // Test Mock GitHub Server
  await test('Mock GitHub Health Check', async () => {
    const response = await axios.get(`${MOCK_GITHUB_URL}/health`);
    assert(response.status === 200, 'Health check returns 200');
    assert(response.data.mode === 'github-simulation', 'Correct mode');
    assert(response.data.users.includes('tom-sapletta-com'), 'User available');
  });

  await test('Code Registration', async () => {
    const testCode = `test_${Date.now()}`;
    const response = await axios.post(`${MOCK_GITHUB_URL}/api/_sim/issue-code`, {
      code: testCode,
      login: 'tom-sapletta-com',
      state: 'test123'
    });
    assert(response.status === 200, 'Code registration successful');
    assert(response.data.ok === true, 'Registration response ok');
  });

  await test('Token Exchange', async () => {
    const testCode = `token_${Date.now()}`;
    
    // Register code first
    await axios.post(`${MOCK_GITHUB_URL}/api/_sim/issue-code`, {
      code: testCode,
      login: 'tom-sapletta-com',
      state: 'test123'
    });

    // Exchange for token
    const response = await axios.post(`${MOCK_GITHUB_URL}/login/oauth/access_token`, {
      client_id: 'Iv1.mock_test_client',
      client_secret: 'mock_secret_for_testing',
      code: testCode
    }, {
      headers: { Accept: 'application/json' }
    });

    assert(response.status === 200, 'Token exchange successful');
    assert(response.data.access_token, 'Access token returned');
    assert(response.data.access_token.startsWith('gho_mock_'), 'Token format correct');
    assert(response.data.token_type === 'bearer', 'Token type correct');
    
    authToken = response.data.access_token;
  });

  await test('User Profile', async () => {
    const response = await axios.get(`${MOCK_GITHUB_URL}/user`, {
      headers: { Authorization: `Bearer ${authToken}` }
    });

    assert(response.status === 200, 'User profile successful');
    assert(response.data.login === 'tom-sapletta-com', 'Correct login');
    assert(response.data.name === 'Tom Sapletta', 'Correct name');
    assert(response.data.id === 5669315, 'Correct user ID');
  });

  await test('User Repositories', async () => {
    const response = await axios.get(`${MOCK_GITHUB_URL}/user/repos`, {
      headers: { Authorization: `Bearer ${authToken}` }
    });

    assert(response.status === 200, 'Repositories request successful');
    assert(Array.isArray(response.data), 'Returns array');
    assert(response.data.length >= 2, 'Has at least 2 repositories');
    
    const repoNames = response.data.map(repo => repo.name);
    assert(repoNames.includes('semcod'), 'Contains semcod repo');
    assert(repoNames.includes('letwhisper'), 'Contains letwhisper repo');
  });

  // Test Backend OAuth
  await test('Backend OAuth Start', async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/auth/github`, {
        maxRedirects: 0,
        validateStatus: () => true
      });
      
      assert(response.status === 307, 'Returns redirect');
      assert(response.headers.location.includes('localhost:4010'), 'Redirects to mock server');
      assert(response.headers.location.includes('login/oauth/authorize'), 'Correct OAuth endpoint');
    } catch (error) {
      assert(error.response.status === 307, 'Returns redirect (via error)');
      assert(error.response.headers.location.includes('localhost:4010'), 'Redirects to mock server (via error)');
    }
  });

  await test('Backend OAuth Callback', async () => {
    const callbackCode = `callback_${Date.now()}`;
    
    // Register code with mock server
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
      
      assert(response.status === 307, 'Returns redirect');
      assert(response.headers.location.includes(FRONTEND_URL), 'Redirects to frontend');
      assert(response.headers.location.includes('session='), 'Includes session token');
      
      // Extract session token
      const sessionMatch = response.headers.location.match(/session=([^&]+)/);
      assert(sessionMatch, 'Session token found in redirect');
      sessionToken = sessionMatch[1];
    } catch (error) {
      assert(error.response.status === 307, 'Returns redirect (via error)');
      assert(error.response.headers.location.includes(FRONTEND_URL), 'Redirects to frontend (via error)');
      
      const sessionMatch = error.response.headers.location.match(/session=([^&]+)/);
      assert(sessionMatch, 'Session token found in redirect (via error)');
      sessionToken = sessionMatch[1];
    }
  });

  await test('Protected API Access', async () => {
    assert(sessionToken, 'Session token available');
    
    const response = await axios.get(`${BACKEND_URL}/api/me`, {
      headers: { Authorization: `Bearer ${sessionToken}` }
    });

    assert(response.status === 200, 'Protected API accessible');
    assert(response.data.login === 'tom-sapletta-com', 'Correct user data');
  });

  // Test Error Cases
  await test('Invalid Code Error', async () => {
    try {
      await axios.post(`${MOCK_GITHUB_URL}/login/oauth/access_token`, {
        client_id: 'Iv1.mock_test_client',
        client_secret: 'mock_secret_for_testing',
        code: 'invalid_code'
      }, {
        headers: { Accept: 'application/json' }
      });
      assert(false, 'Should have thrown an error');
    } catch (error) {
      assert(error.response.status === 400, 'Returns 400 for invalid code');
      assert(error.response.data.error === 'bad_verification_code', 'Correct error message');
    }
  });

  await test('Invalid Token Error', async () => {
    try {
      await axios.get(`${MOCK_GITHUB_URL}/user`, {
        headers: { Authorization: 'Bearer invalid_token' }
      });
      assert(false, 'Should have thrown an error');
    } catch (error) {
      assert(error.response.status === 401, 'Returns 401 for invalid token');
    }
  });

  await test('Unauthorized API Access', async () => {
    try {
      await axios.get(`${BACKEND_URL}/api/me`);
      assert(false, 'Should have thrown an error');
    } catch (error) {
      assert(error.response.status === 401, 'Returns 401 without auth');
    }
  });

  // Print results
  console.log('\n' + '=' .repeat(50));
  console.log('📊 Test Results Summary');
  console.log('=' .repeat(50));
  console.log(`Total Tests: ${testResults.total}`);
  console.log(`✅ Passed: ${testResults.passed}`);
  console.log(`❌ Failed: ${testResults.failed}`);
  console.log(`Success Rate: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`);

  if (testResults.failed === 0) {
    console.log('\n🎉 All tests passed! The GitHub OAuth simulation is working correctly.');
  } else {
    console.log('\n⚠️  Some tests failed. Please check the configuration and logs.');
  }

  console.log('\n🔗 Quick Links:');
  console.log(`Frontend: ${FRONTEND_URL}`);
  console.log(`Backend: ${BACKEND_URL}`);
  console.log(`Mock GitHub: ${MOCK_GITHUB_URL}`);
}

// Run the tests
runTests().catch(console.error);
