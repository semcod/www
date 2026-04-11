#!/usr/bin/env node
/**
 * Manual browser testing script for GitHub OAuth simulation
 * Opens different browsers and guides through the OAuth login flow
 */

const { spawn } = require('child_process');
const http = require('http');

const FRONTEND_URL = 'http://localhost:3000';
const MOCK_GITHUB_URL = 'http://localhost:4010';

async function checkServer(url) {
  return new Promise((resolve) => {
    http.get(url, (res) => {
      resolve(res.statusCode === 200);
    }).on('error', () => resolve(false));
  });
}

async function openBrowser(browser, url) {
  const commands = {
    chrome: ['google-chrome', '--new-window', '--disable-web-security', '--disable-features=VizDisplayCompositor'],
    firefox: ['firefox', '--new-window'],
    safari: ['open', '-a', 'Safari'],
    edge: ['microsoft-edge', '--new-window']
  };

  const command = commands[browser.toLowerCase()];
  if (!command) {
    console.error(`Browser ${browser} not supported`);
    return;
  }

  try {
    spawn(command[0], [...command.slice(1), url], { detached: true });
    console.log(`✅ Opened ${browser} at ${url}`);
  } catch (error) {
    console.error(`❌ Failed to open ${browser}:`, error.message);
  }
}

async function runManualTest() {
  console.log('🧪 Manual Browser Testing for GitHub OAuth Simulation');
  console.log('=' .repeat(50));

  // Check if servers are running
  console.log('🔍 Checking server availability...');
  const frontendOk = await checkServer(FRONTEND_URL);
  const mockOk = await checkServer(MOCK_GITHUB_URL);

  if (!frontendOk) {
    console.error('❌ Frontend server not running at', FRONTEND_URL);
    console.log('💡 Start with: docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d');
    return;
  }

  if (!mockOk) {
    console.error('❌ Mock GitHub server not running at', MOCK_GITHUB_URL);
    console.log('💡 Start with: ./run-sim.sh');
    return;
  }

  console.log('✅ Both servers are running!');
  console.log('');

  // Display test instructions
  console.log('📋 Test Instructions:');
  console.log('1. Click "Sign in with GitHub" button');
  console.log('2. You should be redirected to the mock GitHub login page');
  console.log('3. Click the "tom-sapletta-com" user button');
  console.log('4. You should be redirected back to the frontend, logged in');
  console.log('5. Verify you see "tom-sapletta-com" or "Tom Sapletta" on the page');
  console.log('');

  // Test URLs
  console.log('🌐 Test URLs:');
  console.log(`Frontend: ${FRONTEND_URL}`);
  console.log(`Mock GitHub: ${MOCK_GITHUB_URL}/login/oauth/authorize?client_id=test`);
  console.log('');

  // Browser selection
  const availableBrowsers = ['chrome', 'firefox', 'safari', 'edge'];
  console.log('🚀 Available browsers:');
  availableBrowsers.forEach((browser, index) => {
    console.log(`${index + 1}. ${browser}`);
  });

  // Open browsers based on user input or open all
  if (process.argv.length > 2) {
    const selectedBrowser = process.argv[2].toLowerCase();
    if (availableBrowsers.includes(selectedBrowser)) {
      console.log(`\n🌐 Opening ${selectedBrowser}...`);
      await openBrowser(selectedBrowser, FRONTEND_URL);
    } else {
      console.error(`❌ Browser ${selectedBrowser} not available`);
    }
  } else {
    console.log('\n🌐 Opening all available browsers...');
    for (const browser of availableBrowsers) {
      await openBrowser(browser, FRONTEND_URL);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Small delay between browsers
    }
  }

  console.log('\n📝 Manual Testing Checklist:');
  console.log('□ Login button is visible and clickable');
  console.log('□ Redirect to mock GitHub works');
  console.log('□ Mock GitHub login page loads correctly');
  console.log('□ User button is visible and clickable');
  console.log('□ Redirect back to frontend works');
  console.log('□ User is logged in (shows username)');
  console.log('□ Session persists on page reload');
  console.log('□ Logout works (if available)');
  console.log('');

  console.log('🔍 Debugging Tips:');
  console.log('- Open browser DevTools (F12) to check network requests');
  console.log('- Check Console for JavaScript errors');
  console.log('- Verify OAuth flow: /auth/github → mock-github → /auth/callback → frontend');
  console.log('- Check that backend environment variables are correct');
  console.log('');

  console.log('⚡ Quick Commands:');
  console.log('- Check mock server health: curl', MOCK_GITHUB_URL + '/health');
  console.log('- Test OAuth redirect: curl -v "http://localhost:8003/auth/github"');
  console.log('- View backend logs: docker compose logs backend');
  console.log('- Restart services: docker compose restart');
}

// Run the manual test
runManualTest().catch(console.error);
