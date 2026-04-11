// Cypress E2E test for GitHub OAuth login simulation
describe('GitHub OAuth Login - Cypress', () => {
  const FRONTEND_URL = Cypress.env('FRONTEND_URL') || 'http://localhost:3000';
  const MOCK_GITHUB_URL = Cypress.env('MOCK_GITHUB_URL') || 'http://localhost:4010';

  beforeEach(() => {
    // Clear cookies and localStorage before each test
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  it('should complete full OAuth login flow', () => {
    // Visit frontend
    cy.visit(FRONTEND_URL);
    
    // Find and click GitHub login button
    cy.get('button:contains("GitHub"), a:contains("GitHub"), [data-testid="github-login"]')
      .first()
      .should('be.visible')
      .click();

    // Should redirect to mock GitHub OAuth page
    cy.url().should('include', '4010');
    cy.url().should('include', 'login/oauth/authorize');

    // Verify mock GitHub login page elements
    cy.get('body').should('contain', 'Mock GitHub Login');
    cy.get('button:has-text("tom-sapletta-com")')
      .should('be.visible')
      .click();

    // Should redirect back to frontend with session
    cy.url().should('match', new RegExp(`^${FRONTEND_URL}/`));
    
    // Verify user is logged in
    cy.get('body').should('contain', 'tom-sapletta-com');
    cy.get('[data-testid="user-name"], text=tom-sapletta-com')
      .should('be.visible');
  });

  it('should handle OAuth flow with explicit waits', () => {
    cy.visit(FRONTEND_URL);
    
    // Wait for page to load completely
    cy.get('#root').should('be.visible');
    
    // Click login button with explicit wait
    cy.get('button:has-text("GitHub"), a:has-text("GitHub")')
      .should('be.visible')
      .and('not.be.disabled')
      .first()
      .click();

    // Wait for redirect to mock GitHub
    cy.url({ timeout: 10000 }).should('include', '4010');
    
    // Verify we're on the mock login page
    cy.get('h2').should('contain', 'Mock GitHub Login');
    
    // Click user button
    cy.get('button:has-text("tom-sapletta-com")')
      .should('be.visible')
      .click();

    // Wait for redirect back to frontend
    cy.url({ timeout: 10000 }).should('match', new RegExp(`^${FRONTEND_URL}/`));
    
    // Check for successful login indicators
    cy.get('body').should('contain.text', 'tom-sapletta-com');
  });

  it('should persist login session across page reloads', () => {
    // Complete login flow first
    cy.visit(FRONTEND_URL);
    cy.get('button:has-text("GitHub"), a:has-text("GitHub")').first().click();
    cy.url().should('include', '4010');
    cy.get('button:has-text("tom-sapletta-com")').click();
    cy.url().should('match', new RegExp(`^${FRONTEND_URL}/`));
    
    // Verify logged in
    cy.get('body').should('contain', 'tom-sapletta-com');
    
    // Reload page
    cy.reload();
    
    // Should still be logged in
    cy.get('body').should('contain', 'tom-sapletta-com');
  });

  it('should handle multiple login attempts', () => {
    // First login
    cy.visit(FRONTEND_URL);
    cy.get('button:has-text("GitHub"), a:has-text("GitHub")').first().click();
    cy.url().should('include', '4010');
    cy.get('button:has-text("tom-sapletta-com")').click();
    cy.url().should('match', new RegExp(`^${FREND_URL}/`));
    
    // Logout if possible (if logout button exists)
    cy.get('button:has-text("Logout"), a:has-text("Logout")')
      .then($logout => {
        if ($logout.length > 0) {
          $logout.first().click();
        }
      });
    
    // Try to login again
    cy.get('button:has-text("GitHub"), a:has-text("GitHub")')
      .first()
      .click();
    cy.url().should('include', '4010');
    cy.get('button:has-text("tom-sapletta-com")').click();
    cy.url().should('match', new RegExp(`^${FRONTEND_URL}/`));
    
    // Should be logged in again
    cy.get('body').should('contain', 'tom-sapletta-com');
  });
});
