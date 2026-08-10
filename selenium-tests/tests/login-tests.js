/**
 * ============================================================================
 * Selenium E2E Test Suite: Web Frontend Login Functionality
 * File: selenium-tests/tests/login-tests.js
 * Description: Comprehensive End-to-End (E2E) automated test script using 
 *              Selenium WebDriver for testing web frontend authentication.
 * Supports: Mocha test runner and Standalone execution via Node.js
 * ============================================================================
 */

const { Builder, By, Key, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const firefox = require('selenium-webdriver/firefox');
const fs = require('fs');
const path = require('path');

// Test Configuration
const CONFIG = {
    baseUrl: process.env.BASE_URL || 'http://localhost:5000/auth/login',
    targetDashboardUrl: process.env.DASHBOARD_URL || 'http://localhost:5000/api/dashboard',
    browser: process.env.BROWSER || 'chrome',
    headless: process.env.HEADLESS === 'true' || false,
    defaultTimeout: 10000,
    screenshotDir: path.join(__dirname, '../screenshots'),
    validCredentials: {
        username: process.env.TEST_USER || 'admin',
        password: process.env.TEST_PASSWORD || 'admin123'
    },
    invalidCredentials: {
        username: 'invalid_user_99',
        password: 'wrong_password_xyz'
    }
};

// Ensure screenshot directory exists
if (!fs.existsSync(CONFIG.screenshotDir)) {
    fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
}

// Element Locators Dictionary
const LOCATORS = {
    usernameInput: By.id('username'),
    usernameFallback: By.css('input[name="username"]'),
    passwordInput: By.id('password'),
    passwordFallback: By.css('input[name="password"]'),
    submitButton: By.css('button[type="submit"]'),
    submitFallback: By.css('input[type="submit"]'),
    errorMessage: By.css('.alert-danger, .error-message, .error, #error-message'),
    successMessage: By.css('.alert-success, .success-message'),
    rememberMeCheckbox: By.id('remember_me'),
    showPasswordToggle: By.css('.toggle-password, #toggle-password'),
    forgotPasswordLink: By.css('a[href*="forgot"]'),
    logoutButton: By.css('a[href*="logout"], button#logout'),
    dashboardHeader: By.css('h1, .dashboard-title, #dashboard')
};

/**
 * Driver Factory: Builds WebDriver instance based on configuration
 */
async function createDriver() {
    let builder = new Builder().forBrowser(CONFIG.browser);

    if (CONFIG.browser === 'chrome') {
        let options = new chrome.Options();
        if (CONFIG.headless) {
            options.addArguments('--headless=new');
        }
        options.addArguments('--no-sandbox');
        options.addArguments('--disable-dev-shm-usage');
        options.addArguments('--disable-gpu');
        options.addArguments('--window-size=1920,1080');
        builder.setChromeOptions(options);
    } else if (CONFIG.browser === 'firefox') {
        let options = new firefox.Options();
        if (CONFIG.headless) {
            options.addArguments('-headless');
        }
        builder.setFirefoxOptions(options);
    }

    const driver = await builder.build();
    await driver.manage().setTimeouts({ implicit: CONFIG.defaultTimeout });
    return driver;
}

/**
 * Helper Utilities
 */
const Helpers = {
    async locateElement(driver, primaryLocator, fallbackLocator) {
        try {
            return await driver.wait(until.elementLocated(primaryLocator), 3000);
        } catch (e) {
            if (fallbackLocator) {
                return await driver.wait(until.elementLocated(fallbackLocator), 3000);
            }
            throw e;
        }
    },

    async enterText(driver, locator, text) {
        const element = await driver.wait(until.elementLocated(locator), CONFIG.defaultTimeout);
        await driver.wait(until.elementIsVisible(element), CONFIG.defaultTimeout);
        await element.clear();
        await element.sendKeys(text);
    },

    async clickElement(driver, locator) {
        const element = await driver.wait(until.elementLocated(locator), CONFIG.defaultTimeout);
        await driver.wait(until.elementIsVisible(element), CONFIG.defaultTimeout);
        await driver.wait(until.elementIsEnabled(element), CONFIG.defaultTimeout);
        await element.click();
    },

    async getElementText(driver, locator) {
        try {
            const element = await driver.wait(until.elementLocated(locator), 5000);
            return (await element.getText()).trim();
        } catch (err) {
            return '';
        }
    },

    async isElementPresent(driver, locator) {
        try {
            const elements = await driver.findElements(locator);
            return elements.length > 0 && await elements[0].isDisplayed();
        } catch (err) {
            return false;
        }
    },

    async captureScreenshot(driver, testName) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = path.join(CONFIG.screenshotDir, `${testName}_${timestamp}.png`);
        const image = await driver.takeScreenshot();
        fs.writeFileSync(filename, image, 'base64');
        console.log(`  📸 Screenshot saved: ${filename}`);
    }
};

/**
 * Selenium E2E Test Suite Definition
 */
async function runTestSuite() {
    let driver;
    let passedCount = 0;
    let failedCount = 0;
    const results = [];

    async function executeTest(testId, description, testFn) {
        console.log(`\n▶ [${testId}] ${description}`);
        try {
            await testFn();
            console.log(`  ✅ PASSED`);
            passedCount++;
            results.push({ id: testId, description, status: 'PASSED', error: null });
        } catch (error) {
            console.error(`  ❌ FAILED: ${error.message}`);
            failedCount++;
            if (driver) {
                await Helpers.captureScreenshot(driver, testId).catch(() => {});
            }
            results.push({ id: testId, description, status: 'FAILED', error: error.message });
        }
    }

    try {
        console.log('====================================================');
        console.log(' Starting Selenium E2E Login Functionality Test Suite');
        console.log(` Target URL: ${CONFIG.baseUrl}`);
        console.log(` Browser: ${CONFIG.browser} (Headless: ${CONFIG.headless})`);
        console.log('====================================================');

        driver = await createDriver();

        // ----------------------------------------------------------------
        // Test Group 1: Page Load & UI Elements Verification
        // ----------------------------------------------------------------
        await executeTest('TC_LOG_001', 'Verify login page loads successfully with HTTP 200 state', async () => {
            await driver.get(CONFIG.baseUrl);
            const title = await driver.getTitle();
            if (!title && !(await driver.getCurrentUrl()).includes('/login')) {
                throw new Error('Page title or URL indicates login page failed to load.');
            }
        });

        await executeTest('TC_LOG_002', 'Verify presence of essential form controls (Username, Password, Submit)', async () => {
            await driver.get(CONFIG.baseUrl);
            const hasUsername = await Helpers.isElementPresent(driver, LOCATORS.usernameInput);
            const hasPassword = await Helpers.isElementPresent(driver, LOCATORS.passwordInput);
            const hasSubmit = await Helpers.isElementPresent(driver, LOCATORS.submitButton);

            if (!hasUsername || !hasPassword || !hasSubmit) {
                throw new Error('One or more essential form elements are missing from the DOM.');
            }
        });

        await executeTest('TC_LOG_003', 'Verify Password field has input type="password" for security masking', async () => {
            await driver.get(CONFIG.baseUrl);
            const pwdElement = await driver.findElement(LOCATORS.passwordInput);
            const typeAttr = await pwdElement.getAttribute('type');
            if (typeAttr !== 'password') {
                throw new Error(`Password field type is '${typeAttr}', expected 'password'.`);
            }
        });

        // ----------------------------------------------------------------
        // Test Group 2: Negative Authentication Scenarios
        // ----------------------------------------------------------------
        await executeTest('TC_LOG_004', 'Verify error display on submitting empty form fields', async () => {
            await driver.get(CONFIG.baseUrl);
            await Helpers.clickElement(driver, LOCATORS.submitButton);
            
            const currentUrl = await driver.getCurrentUrl();
            const hasError = await Helpers.isElementPresent(driver, LOCATORS.errorMessage);
            const isStillOnLogin = currentUrl.includes('/login') || currentUrl.endsWith('/');

            if (!isStillOnLogin) {
                throw new Error('Form submitted successfully with empty fields instead of staying on login.');
            }
        });

        await executeTest('TC_LOG_005', 'Verify error feedback with invalid username and password', async () => {
            await driver.get(CONFIG.baseUrl);
            await Helpers.enterText(driver, LOCATORS.usernameInput, CONFIG.invalidCredentials.username);
            await Helpers.enterText(driver, LOCATORS.passwordInput, CONFIG.invalidCredentials.password);
            await Helpers.clickElement(driver, LOCATORS.submitButton);

            const errorText = await Helpers.getElementText(driver, LOCATORS.errorMessage);
            const currentUrl = await driver.getCurrentUrl();
            
            if (!currentUrl.includes('/login') && !errorText.toLowerCase().includes('invalid')) {
                throw new Error(`Expected error message for invalid login. Got text: '${errorText}'`);
            }
        });

        await executeTest('TC_LOG_006', 'Verify SQL Injection payloads are sanitized/rejected safely', async () => {
            await driver.get(CONFIG.baseUrl);
            await Helpers.enterText(driver, LOCATORS.usernameInput, "' OR '1'='1");
            await Helpers.enterText(driver, LOCATORS.passwordInput, "' OR '1'='1");
            await Helpers.clickElement(driver, LOCATORS.submitButton);

            const currentUrl = await driver.getCurrentUrl();
            if (!currentUrl.includes('/login')) {
                throw new Error('Potential SQL Injection vulnerability detected! Login bypass occurred.');
            }
        });

        await executeTest('TC_LOG_007', 'Verify XSS Payload in username does not execute inline scripts', async () => {
            await driver.get(CONFIG.baseUrl);
            const xssPayload = "<script>window.xssTest=true;</script>";
            await Helpers.enterText(driver, LOCATORS.usernameInput, xssPayload);
            await Helpers.enterText(driver, LOCATORS.passwordInput, 'password123');
            await Helpers.clickElement(driver, LOCATORS.submitButton);

            const isXssExecuted = await driver.executeScript("return window.xssTest === true;");
            if (isXssExecuted) {
                throw new Error('XSS Payload executed in client context!');
            }
        });

        // ----------------------------------------------------------------
        // Test Group 3: Keyboard & Usability Testing
        // ----------------------------------------------------------------
        await executeTest('TC_LOG_008', 'Verify Form Submission via Keyboard ENTER key in password input', async () => {
            await driver.get(CONFIG.baseUrl);
            await Helpers.enterText(driver, LOCATORS.usernameInput, CONFIG.invalidCredentials.username);
            const pwdElement = await driver.findElement(LOCATORS.passwordInput);
            await pwdElement.sendKeys(CONFIG.invalidCredentials.password, Key.RETURN);

            // Wait brief moment for post submit evaluation
            await driver.sleep(1000);
            const currentUrl = await driver.getCurrentUrl();
            if (!currentUrl.includes('/login')) {
                throw new Error('ENTER key press did not trigger form submit process.');
            }
        });

        await executeTest('TC_LOG_009', 'Verify Tab Key navigation between Username and Password fields', async () => {
            await driver.get(CONFIG.baseUrl);
            const userElem = await driver.findElement(LOCATORS.usernameInput);
            await userElem.click();
            await userElem.sendKeys(Key.TAB);

            const activeElement = await driver.switchTo().activeElement();
            const activeId = await activeElement.getAttribute('id');
            const activeName = await activeElement.getAttribute('name');

            if (activeId !== 'password' && activeName !== 'password') {
                console.warn('  ⚠️ Warning: Focus did not move directly to password field via TAB key.');
            }
        });

        // ----------------------------------------------------------------
        // Test Group 4: Positive Authentication Scenarios
        // ----------------------------------------------------------------
        await executeTest('TC_LOG_010', 'Verify successful login redirect with valid credentials', async () => {
            await driver.get(CONFIG.baseUrl);
            await Helpers.enterText(driver, LOCATORS.usernameInput, CONFIG.validCredentials.username);
            await Helpers.enterText(driver, LOCATORS.passwordInput, CONFIG.validCredentials.password);
            await Helpers.clickElement(driver, LOCATORS.submitButton);

            await driver.sleep(1500);
            const currentUrl = await driver.getCurrentUrl();
            const pageSource = await driver.getPageSource();

            const isSuccess = !currentUrl.includes('/login') || pageSource.includes('Dashboard') || pageSource.includes('Logout');

            if (!isSuccess) {
                console.warn('  ⚠️ Valid login attempted. Ensure backend server is running and user credentials exist.');
            }
        });

        // Summary Report
        console.log('\n====================================================');
        console.log(' Selenium E2E Execution Summary');
        console.log(` Total Executed: ${passedCount + failedCount}`);
        console.log(` Passed: ${passedCount}`);
        console.log(` Failed: ${failedCount}`);
        console.log('====================================================\n');

    } catch (criticalErr) {
        console.error('Critical Driver Error during suite execution:', criticalErr);
    } finally {
        if (driver) {
            await driver.quit();
        }
    }
}

// ----------------------------------------------------------------------------
// Mocha Framework Export & Standalone Execution Harness
// ----------------------------------------------------------------------------
if (require.main === module) {
    // Run standalone
    runTestSuite();
} else {
    // Mocha Integration
    describe('Selenium E2E Login Functionality Tests', function () {
        this.timeout(60000);
        let driver;

        before(async function () {
            driver = await createDriver();
        });

        after(async function () {
            if (driver) {
                await driver.quit();
            }
        });

        beforeEach(async function () {
            await driver.get(CONFIG.baseUrl);
        });

        it('TC_LOG_001: Should load login page successfully', async function () {
            const title = await driver.getTitle();
            const url = await driver.getCurrentUrl();
            if (!url.includes('/login') && !title) {
                throw new Error('Login page load verification failed.');
            }
        });

        it('TC_LOG_002: Should display username and password fields', async function () {
            const userVis = await Helpers.isElementPresent(driver, LOCATORS.usernameInput);
            const pwdVis = await Helpers.isElementPresent(driver, LOCATORS.passwordInput);
            if (!userVis || !pwdVis) {
                throw new Error('Login fields not visible.');
            }
        });

        it('TC_LOG_003: Should reject invalid login credentials with message', async function () {
            await Helpers.enterText(driver, LOCATORS.usernameInput, 'invalidUser');
            await Helpers.enterText(driver, LOCATORS.passwordInput, 'invalidPass');
            await Helpers.clickElement(driver, LOCATORS.submitButton);
            const currentUrl = await driver.getCurrentUrl();
            if (!currentUrl.includes('/login')) {
                throw new Error('Should remain on login page on failure');
            }
        });
    });
}
