import { test, expect } from '@playwright/test';

test.describe('Mini Kanban Board End-to-End Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the frontend
    await page.goto('/');
  });

  test('opens the frontend at http://localhost:8000', async ({ page }) => {
    // Check that the page loads successfully
    await expect(page).toHaveTitle(/Mini Kanban|Mini Kanban Board/);
    
    // Check that the main content is visible
    await expect(page.locator('h1, h2, .app-title, .main-content')).toBeVisible();
  });

  test('registers a new user', async ({ page }) => {
    // Click on login/register button if present
    const loginButton = page.locator('button:has-text("Login"), button:has-text("Register"), a:has-text("Login"), a:has-text("Register")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
    }

    // Wait for registration form to appear
    await expect(page.locator('input[type="email"], input[placeholder*="email"], input[placeholder*="Email"]')).toBeVisible();
    
    // Fill in registration form
    await page.fill('input[type="email"]', 'testuser@example.com');
    await page.fill('input[type="password"]', 'testpass123');
    await page.fill('input[type="text"], input[placeholder*="name"], input[placeholder*="Name"]', 'Test User');
    
    // Click register button
    await page.click('button:has-text("Register"), button:has-text("Sign Up")');
    
    // Wait for successful registration (redirect or success message)
    await expect(page.locator('.success-message, .welcome-message, .dashboard')).toBeVisible({ timeout: 10000 });
  });

  test('creates a Kanban board', async ({ page }) => {
    // First register a user
    await page.fill('input[type="email"]', 'boarduser@example.com');
    await page.fill('input[type="password"]', 'testpass123');
    await page.fill('input[type="text"], input[placeholder*="name"], input[placeholder*="Name"]', 'Board User');
    await page.click('button:has-text("Register"), button:has-text("Sign Up")');
    
    // Wait for dashboard to load
    await expect(page.locator('.dashboard, .boards-list, .create-board')).toBeVisible({ timeout: 10000 });
    
    // Click create board button
    await page.click('button:has-text("Create Board"), button:has-text("+"), .create-board button');
    
    // Fill in board name
    await page.fill('input[placeholder*="board name"], input[placeholder*="Board Name"]', 'Test Kanban Board');
    
    // Click create button
    await page.click('button:has-text("Create")');
    
    // Wait for board to be created and displayed
    await expect(page.locator('.board, .kanban-board, .board-title')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text="Test Kanban Board"')).toBeVisible();
  });

  test('adds a card to the "To Do" column', async ({ page }) => {
    // Register user and create board (simplified for brevity)
    await page.fill('input[type="email"]', 'carduser@example.com');
    await page.fill('input[type="password"]', 'testpass123');
    await page.fill('input[type="text"], input[placeholder*="name"], input[placeholder*="Name"]', 'Card User');
    await page.click('button:has-text("Register"), button:has-text("Sign Up")');
    
    await page.click('button:has-text("Create Board"), button:has-text("+"), .create-board button');
    await page.fill('input[placeholder*="board name"], input[placeholder*="Board Name"]', 'Card Test Board');
    await page.click('button:has-text("Create")');
    
    // Wait for board to load and check for default columns
    await expect(page.locator('.board, .kanban-board')).toBeVisible({ timeout: 10000 });
    
    // Find "To Do" column
    const todoColumn = page.locator('text="To Do"').locator('..').locator('..'); // Get parent element
    
    // Click "Add card" button in "To Do" column
    const addCardButton = todoColumn.locator('button:has-text("Add card"), button:has-text("+"), .add-card');
    await addCardButton.click();
    
    // Fill in card details
    await page.fill('input[placeholder*="card title"], input[placeholder*="Card Title"], .card-input', 'Test Task');
    await page.click('button:has-text("Add"), button:has-text("Create")');
    
    // Verify card appears in "To Do" column
    await expect(todoColumn.locator('text="Test Task"')).toBeVisible();
  });

  test('drags and drops a card to the "In Progress" column', async ({ page }) => {
    // Register user and create board
    await page.fill('input[type="email"]', 'draguser@example.com');
    await page.fill('input[type="password"]', 'testpass123');
    await page.fill('input[type="text"], input[placeholder*="name"], input[placeholder*="Name"]', 'Drag User');
    await page.click('button:has-text("Register"), button:has-text("Sign Up")');
    
    await page.click('button:has-text("Create Board"), button:has-text("+"), .create-board button');
    await page.fill('input[placeholder*="board name"], input[placeholder*="Board Name"]', 'Drag Test Board');
    await page.click('button:has-text("Create")');
    
    await expect(page.locator('.board, .kanban-board')).toBeVisible({ timeout: 10000 });
    
    // Add a card to "To Do" column
    const todoColumn = page.locator('text="To Do"').locator('..').locator('..');
    const progressColumn = page.locator('text="In Progress"').locator('..').locator('..');
    
    await todoColumn.locator('button:has-text("Add card"), button:has-text("+"), .add-card').click();
    await page.fill('input[placeholder*="card title"], input[placeholder*="Card Title"], .card-input', 'Draggable Task');
    await page.click('button:has-text("Add"), button:has-text("Create")');
    
    // Wait for card to appear
    await expect(todoColumn.locator('text="Draggable Task"')).toBeVisible();
    
    // Drag the card to "In Progress" column
    const card = todoColumn.locator('text="Draggable Task"').locator('..');
    const targetColumn = progressColumn;
    
    // Get the bounding box of the card and target column
    const cardBoundingBox = await card.boundingBox();
    const targetBoundingBox = await targetColumn.boundingBox();
    
    if (cardBoundingBox && targetBoundingBox) {
      // Calculate drop position (middle of target column)
      const dropX = targetBoundingBox.x + targetBoundingBox.width / 2;
      const dropY = targetBoundingBox.y + targetBoundingBox.height / 2;
      
      // Perform drag and drop
      await page.mouse.move(cardBoundingBox.x + cardBoundingBox.width / 2, cardBoundingBox.y + cardBoundingBox.height / 2);
      await page.mouse.down();
      await page.mouse.move(dropX, dropY);
      await page.mouse.up();
      
      // Wait for the drag to complete
      await page.waitForTimeout(1000);
    }
    
    // Verify card is now in "In Progress" column
    await expect(progressColumn.locator('text="Draggable Task"')).toBeVisible();
    
    // Verify card is no longer in "To Do" column
    await expect(todoColumn.locator('text="Draggable Task"')).toBeHidden();
  });

  test('verifies the card state is updated', async ({ page }) => {
    // Register user and create board
    await page.fill('input[type="email"]', 'stateuser@example.com');
    await page.fill('input[type="password"]', 'testpass123');
    await page.fill('input[type="text"], input[placeholder*="name"], input[placeholder*="Name"]', 'State User');
    await page.click('button:has-text("Register"), button:has-text("Sign Up")');
    
    await page.click('button:has-text("Create Board"), button:has-text("+"), .create-board button');
    await page.fill('input[placeholder*="board name"], input[placeholder*="Board Name"]', 'State Test Board');
    await page.click('button:has-text("Create")');
    
    await expect(page.locator('.board, .kanban-board')).toBeVisible({ timeout: 10000 });
    
    // Add multiple cards to different columns
    const todoColumn = page.locator('text="To Do"').locator('..').locator('..');
    const progressColumn = page.locator('text="In Progress"').locator('..').locator('..');
    const doneColumn = page.locator('text="Done"').locator('..').locator('..');
    
    // Add card1 to "To Do"
    await todoColumn.locator('button:has-text("Add card"), button:has-text("+"), .add-card').click();
    await page.fill('input[placeholder*="card title"], input[placeholder*="Card Title"], .card-input', 'Task 1');
    await page.click('button:has-text("Add"), button:has-text("Create")');
    
    // Add card2 to "To Do"
    await todoColumn.locator('button:has-text("Add card"), button:has-text("+"), .add-card').click();
    await page.fill('input[placeholder*="card title"], input[placeholder*="Card Title"], .card-input', 'Task 2');
    await page.click('button:has-text("Add"), button:has-text("Create")');
    
    // Move card1 to "In Progress"
    const card1 = todoColumn.locator('text="Task 1"').locator('..');
    const progressBoundingBox = await progressColumn.boundingBox();
    
    if (progressBoundingBox) {
      await page.mouse.move(await card1.boundingBox()!.x + 50, await card1.boundingBox()!.y + 25);
      await page.mouse.down();
      await page.mouse.move(progressBoundingBox.x + progressBoundingBox.width / 2, progressBoundingBox.y + progressBoundingBox.height / 2);
      await page.mouse.up();
      await page.waitForTimeout(1000);
    }
    
    // Move card1 to "Done"
    const doneBoundingBox = await doneColumn.boundingBox();
    if (doneBoundingBox) {
      const card1InProgress = progressColumn.locator('text="Task 1"').locator('..');
      await page.mouse.move(await card1InProgress.boundingBox()!.x + 50, await card1InProgress.boundingBox()!.y + 25);
      await page.mouse.down();
      await page.mouse.move(doneBoundingBox.x + doneBoundingBox.width / 2, doneBoundingBox.y + doneBoundingBox.height / 2);
      await page.mouse.up();
      await page.waitForTimeout(1000);
    }
    
    // Move card2 to "In Progress"
    const card2 = todoColumn.locator('text="Task 2"').locator('..');
    if (progressBoundingBox) {
      await page.mouse.move(await card2.boundingBox()!.x + 50, await card2.boundingBox()!.y + 25);
      await page.mouse.down();
      await page.mouse.move(progressBoundingBox.x + progressBoundingBox.width / 2, progressBoundingBox.y + progressBoundingBox.height / 2);
      await page.mouse.up();
      await page.waitForTimeout(1000);
    }
    
    // Verify final state
    await expect(todoColumn.locator('text="Task 1"')).toBeHidden();
    await expect(todoColumn.locator('text="Task 2"')).toBeHidden();
    await expect(progressColumn.locator('text="Task 1"')).toBeHidden();
    await expect(progressColumn.locator('text="Task 2"')).toBeVisible();
    await expect(doneColumn.locator('text="Task 1"')).toBeVisible();
    
    // Verify card counts
    const todoCardCount = await todoColumn.locator('.card, .task').count();
    const progressCardCount = await progressColumn.locator('.card, .task').count();
    const doneCardCount = await doneColumn.locator('.card, .task').count();
    
    expect(todoCardCount).toBe(0);
    expect(progressCardCount).toBe(1);
    expect(doneCardCount).toBe(1);
  });

  test('handles authentication flow properly', async ({ page }) => {
    // Test registration
    await page.fill('input[type="email"]', 'authuser@example.com');
    await page.fill('input[type="password"]', 'authpass123');
    await page.fill('input[type="text"], input[placeholder*="name"], input[placeholder*="Name"]', 'Auth User');
    await page.click('button:has-text("Register"), button:has-text("Sign Up")');
    
    // Wait for successful registration
    await expect(page.locator('.dashboard, .boards-list, .welcome-message')).toBeVisible({ timeout: 10000 });
    
    // Test logout
    await page.click('button:has-text("Logout"), .logout-button, .user-menu');
    
    // Verify we're back at login/register screen
    await expect(page.locator('input[type="email"], input[type="password"]')).toBeVisible();
    
    // Test login with same credentials
    await page.fill('input[type="email"]', 'authuser@example.com');
    await page.fill('input[type="password"]', 'authpass123');
    await page.click('button:has-text("Login"), button:has-text("Sign In")');
    
    // Verify we're back in the dashboard
    await expect(page.locator('.dashboard, .boards-list')).toBeVisible({ timeout: 10000 });
  });

  test('handles errors gracefully', async ({ page }) => {
    // Try to register with invalid email
    await page.fill('input[type="email"]', 'invalid-email');
    await page.fill('input[type="password"]', 'testpass123');
    await page.fill('input[type="text"], input[placeholder*="name"], input[placeholder*="Name"]', 'Test User');
    await page.click('button:has-text("Register"), button:has-text("Sign Up")');
    
    // Should show error message
    await expect(page.locator('.error-message, .alert, .notification')).toBeVisible();
    
    // Try to login with non-existent user
    await page.fill('input[type="email"]', 'nonexistent@example.com');
    await page.fill('input[type="password"]', 'wrongpass');
    await page.click('button:has-text("Login"), button:has-text("Sign In")');
    
    // Should show error message
    await expect(page.locator('.error-message, .alert, .notification')).toBeVisible();
  });
});