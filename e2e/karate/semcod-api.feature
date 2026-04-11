Feature: Semcod API E2E Tests
  Test Semcod code health analysis API endpoints using Karate DSL

  Background:
    * url baseUrl
    * configure retry = { count: 3, interval: 1000 }

  Scenario: Health check endpoint
    Given path '/api/health'
    When method get
    Then status 200
    And match response.status == 'ok'
    And match response contains { version: '#string', tools: '#array' }

  Scenario: Domain configuration
    Given path '/api/config/domain'
    When method get
    Then status 200
    And match response contains { domain: '#string' }

  Scenario: Demo authentication
    Given path '/auth/demo'
    When method post
    Then status 200
    And match response contains { session: '#string', user: '#object' }
    * def token = response.session

  Scenario: List marketplace apps
    Given path '/api/apps'
    When method get
    Then status 200
    And match response == '#array'
    And match response[0] contains { name: '#string', version: '#string', pricing: '#string' }

  Scenario: List repositories (authenticated)
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/repos'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200
    And match response == '#array'
    And match response[0] contains { full_name: '#string', name: '#string' }

  Scenario: Start audit (authenticated)
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/audit'
    And header Authorization = 'Bearer ' + token
    And request { repo: 'acme/backend-api' }
    When method post
    Then status 200
    And match response contains { audit_id: '#string', status: '#string' }
    * def auditId = response.audit_id

  Scenario: Get standard metrics (authenticated)
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/metrics/standard'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200

  Scenario: Get repository trend (authenticated)
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/trend/acme/backend-api'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200
    And match response contains { meta: '#object', trend: '#object', points: '#array' }

  Scenario: Get scan diff (authenticated)
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/scan/diff/acme/backend-api'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200
    And match response contains { meta: '#object', delta: '#object', scans: '#object' }

  Scenario: Get badge SVG
    Given path '/badge/acme-backend-api.svg'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'image/svg+xml'

  Scenario: MCP server info
    Given path '/mcp/info'
    When method get
    Then status 200
    And match response contains { name: '#string', version: '#string', protocol_version: '#string' }

  Scenario: List MCP resources
    Given path '/mcp/resources'
    When method get
    Then status 200
    And match response == '#array'
    And match response[0] contains { uri: '#string', name: '#string', mime_type: '#string' }

  Scenario: List MCP tools
    Given path '/mcp/tools'
    When method get
    Then status 200
    And match response == '#array'
    And match response[0] contains { name: '#string', description: '#string', input_schema: '#object' }

  Scenario: Invoke MCP tool (analyze_public_repo)
    Given path '/mcp/tools/invoke'
    And request { 
      name: 'analyze_public_repo',
      arguments: { repo_url: 'https://github.com/acme/backend-api' }
    }
    When method post
    Then status 200
    And match response contains { audit_id: '#string', status: '#string' }

  Scenario: List billing plans
    Given path '/api/billing/plans'
    When method get
    Then status 200
    And match response contains { free: '#object', pro: '#object' }

  Scenario: Get billing status (authenticated)
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/billing/status'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200
    And match response contains { plan: '#string', status: '#string', scans_remaining: '#number' }

  Scenario: List mirrors (authenticated)
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/mirror/list'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200
    And match response == '#array'

  Scenario: List schedules
    Given path '/api/schedules'
    When method get
    Then status 200
    And match response == '#array'

  Scenario: Create schedule (authenticated)
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/schedules'
    And header Authorization = 'Bearer ' + token
    And request { repo: 'acme/backend-api', cron: '0 0 * * *' }
    When method post
    Then status 201
    And match response contains { repo: '#string', next_run: '#string' }

  Scenario: GitHub webhook
    Given path '/webhook/github'
    And request { test: 'data' }
    When method post
    Then status 200
    And match response contains { status: '#string' }

  # ==================== Error Scenarios ====================

  Scenario: Invalid endpoint returns 404
    Given path '/api/invalid-endpoint'
    When method get
    Then status 404

  Scenario: Unauthorized access returns 401
    Given path '/api/repos'
    And header Authorization = 'Bearer invalid_token'
    When method get
    Then status 401

  # ==================== Validation Tests ====================

  Scenario: Audit with missing repo field
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/audit'
    And header Authorization = 'Bearer ' + token
    And request { invalid: 'data' }
    When method post
    Then status 422

  Scenario: Audit with empty repo name
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/audit'
    And header Authorization = 'Bearer ' + token
    And request { repo: '' }
    When method post
    Then status 422

  # ==================== Edge Cases ====================

  Scenario: Trend for non-existent repository
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/trend/nonexistent/repo'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 404

  Scenario: Badge for non-existent repository
    Given path '/badge/nonexistent-repo.svg'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'image/svg+xml'

  Scenario: Schedule with invalid cron expression
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session
    Given path '/api/schedules'
    And header Authorization = 'Bearer ' + token
    And request { repo: 'acme/backend-api', cron: 'invalid' }
    When method post
    Then status 422

  # ==================== Negative Tests ====================

  Scenario: Delete schedule without authentication
    Given path '/api/schedules/acme/backend-api'
    When method delete
    Then status 401

  Scenario: POST without valid JSON
    Given path '/api/audit'
    And request 'invalid json'
    And header Content-Type = 'application/json'
    When method post
    Then status 400

  # ==================== Integration Flow Tests ====================

  Scenario: Complete audit flow - authenticate, list repos, start audit, get trend
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session

    Given path '/api/repos'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200
    * def repo = response[0].full_name

    Given path '/api/audit'
    And header Authorization = 'Bearer ' + token
    And request { repo: '#(repo)' }
    When method post
    Then status 200
    * def auditId = response.audit_id

    Given path '/api/trend/#(repo)'
    And header Authorization = 'Bearer ' + token
    When method get
    Then status 200

  Scenario: MCP tool invocation flow - list tools, invoke, check status
    Given path '/mcp/tools'
    When method get
    Then status 200
    * def toolName = response[0].name

    Given path '/mcp/tools/invoke'
    And request { name: '#(toolName)', arguments: { repo_url: 'https://github.com/acme/backend-api' } }
    When method post
    Then status 200
    * def auditId = response.audit_id

    Given path '/mcp/tools/invoke'
    And request { name: 'get_scan_status', arguments: { audit_id: '#(auditId)' } }
    When method post
    Then status 200

  # ==================== Benchmark Tests ====================

  Scenario: Benchmark summary
    Given path '/api/benchmark/summary'
    When method get
    Then status 200
    And match response contains { total_cases: '#number', pr_conversion_rate: '#number' }

  Scenario: Create benchmark case
    Given path '/api/benchmark/cases'
    And request { case_id: 'BM-KARATE-001', repo: 'acme/backend-api', source_type: 'pr', change_type: 'bugfix', baseline_detected: true, baseline_tools: ['ruff', 'ci'] }
    When method post
    Then status 201
    And match response.case_id == 'BM-KARATE-001'

  Scenario: List benchmark cases
    Given path '/api/benchmark/cases'
    When method get
    Then status 200
    And match response.cases == '#array'

  Scenario: Get specific benchmark case
    Given path '/api/benchmark/cases/BM-KARATE-001'
    When method get
    Then status 200
    And match response.repo == 'acme/backend-api'

  Scenario: Patch benchmark case
    Given path '/api/benchmark/cases/BM-KARATE-001'
    And request { reviewer_verdict: 'go', pr_candidate: true }
    When method patch
    Then status 200
    And match response.reviewer_verdict == 'go'
    And match response.pr_candidate == true

  Scenario: Post benchmark decision
    Given path '/api/benchmark/cases/BM-KARATE-001/decision'
    And request { deployment_model_selected: 'hybrid', pr_candidate: true }
    When method post
    Then status 200
    And match response.deployment_model_selected == 'hybrid'

  Scenario: Post recommendation feedback
    Given path '/api/benchmark/cases/BM-KARATE-001/recommendations/rec123abc/feedback'
    And request { accepted: true, novelty_score: 3, usefulness_score: 2, notes: 'Good recommendation' }
    When method post
    Then status 200
    And match response.accepted == true

  Scenario: Post benchmark event
    Given path '/api/benchmark/cases/BM-KARATE-001/events'
    And request { event_name: 'result_viewed', audit_id: 'abc123' }
    When method post
    Then status 201
    And match response.event_name == 'result_viewed'

  Scenario: List benchmark events
    Given path '/api/benchmark/cases/BM-KARATE-001/events'
    When method get
    Then status 200
    And match response.events == '#array'

  Scenario: List recommendation feedback
    Given path '/api/benchmark/cases/BM-KARATE-001/recommendations/feedback'
    When method get
    Then status 200
    And match response.feedback == '#array'

  Scenario: Export benchmark JSON
    Given path '/api/benchmark/export.json'
    When method get
    Then status 200
    And match response contains { cases: '#array', summary: '#object' }

  Scenario: Export benchmark CSV
    Given path '/api/benchmark/export.csv'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'text/csv'

  # ==================== Benchmark Error Scenarios ====================

  Scenario: Duplicate benchmark case rejection
    Given path '/api/benchmark/cases'
    And request { case_id: 'BM-KARATE-001', repo: 'test' }
    When method post
    Then status 409

  Scenario: Get non-existent benchmark case
    Given path '/api/benchmark/cases/NONEXISTENT'
    When method get
    Then status 404

  Scenario: Patch non-existent benchmark case
    Given path '/api/benchmark/cases/NONEXISTENT'
    And request { reviewer_verdict: 'go' }
    When method patch
    Then status 404

  Scenario: Post decision for non-existent case
    Given path '/api/benchmark/cases/NONEXISTENT/decision'
    And request { pr_candidate: true }
    When method post
    Then status 404

  Scenario: Post feedback for non-existent case
    Given path '/api/benchmark/cases/NONEXISTENT/recommendations/rec123/feedback'
    And request { accepted: true }
    When method post
    Then status 404

  Scenario: Post event for non-existent case
    Given path '/api/benchmark/cases/NONEXISTENT/events'
    And request { event_name: 'test' }
    When method post
    Then status 404

  # ==================== Content-Type Validation ====================

  Scenario: Health endpoint returns JSON content-type
    Given path '/api/health'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'application/json'

  Scenario: Apps endpoint returns JSON content-type
    Given path '/api/apps'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'application/json'

  Scenario: Billing plans endpoint returns JSON content-type
    Given path '/api/billing/plans'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'application/json'

  Scenario: MCP info returns JSON content-type
    Given path '/mcp/info'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'application/json'

  Scenario: Benchmark summary returns JSON content-type
    Given path '/api/benchmark/summary'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'application/json'

  Scenario: Badge SVG returns correct content-type
    Given path '/badge/test-repo.svg'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'image/svg+xml'

  Scenario: Benchmark CSV export returns correct content-type
    Given path '/api/benchmark/export.csv'
    When method get
    Then status 200
    And match responseHeaders['Content-Type'] contains 'text/csv'

  # ==================== Marketplace Install Flow ====================

  Scenario: Marketplace install → status → uninstall flow (authenticated)
    Given path '/auth/demo'
    When method post
    Then status 200
    * def token = response.session

    Given path '/api/install'
    And header Authorization = 'Bearer ' + token
    And request { repo: 'karate-test/repo', provider: 'github', apps: ['audit'] }
    When method post
    Then status 200
    And match response.status == 'installed'

    Given path '/api/apps/status'
    And header Authorization = 'Bearer ' + token
    And param repo = 'karate-test/repo'
    And param provider = 'github'
    When method get
    Then status 200
    And match response.installed == true

  # ==================== Multi-step MCP Flow ====================

  Scenario: MCP end-to-end: list tools → invoke analyze → check status
    Given path '/mcp/tools'
    When method get
    Then status 200
    * def tools = response
    * def analyzeExists = karate.filter(tools, function(x){ return x.name == 'analyze_public_repo' })
    * assert analyzeExists.length > 0

    Given path '/mcp/tools/invoke'
    And request { name: 'analyze_public_repo', arguments: { repo_url: 'https://github.com/acme/backend-api' } }
    When method post
    Then status 200
    * def auditId = response.audit_id

    Given path '/mcp/tools/invoke'
    And request { name: 'get_scan_status', arguments: { audit_id: '#(auditId)' } }
    When method post
    Then status 200
