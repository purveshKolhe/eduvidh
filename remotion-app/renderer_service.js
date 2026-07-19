const express = require('express');
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const PORT = 5000;
const BUNDLE_DIR = path.join(__dirname, 'bundled');
const RENDERER_VERSION = 'persistent-cdp-v2';

// Launch Google Chrome headless
async function launchBrowser() {
  console.log("Launching headless Google Chrome...");
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: true,
    args: [
      '--headless',
      '--disable-gpu',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--remote-debugging-port=9222',
      '--window-size=1280,720'
    ],
    // Safety limit for a busy one-core VM; this is not normal render latency.
    protocolTimeout: 120000,
  });
  return browser;
}

let browser = null;
const tabPool = [];
const queue = [];
let tabReplacements = 0;
// Two tabs may prepare separate slides, but one VM core cannot reliably
// rasterize two full-HD screenshot streams through Chrome at the same time.
let screenshotLock = Promise.resolve();

async function captureFramesExclusively(capture) {
  const previous = screenshotLock;
  let release;
  screenshotLock = new Promise((resolve) => { release = resolve; });
  await previous;
  try {
    return await capture();
  } finally {
    release();
  }
}

async function initTab(index) {
  console.log(`Initializing tab ${index}...`);
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 1 });

  page.on('console', msg => console.log(`PAGE LOG [tab ${index}]:`, msg.text()));
  page.on('pageerror', err => console.error(`PAGE ERROR [tab ${index}]:`, err.message));

  // Expose callbacks
  let propsSetResolver = null;
  let frameSetResolver = null;

  await page.exposeFunction('remotion_onPropsSet', () => {
    if (propsSetResolver) {
      propsSetResolver();
      propsSetResolver = null;
    }
  });

  await page.exposeFunction('remotion_onFrameSet', () => {
    if (frameSetResolver) {
      frameSetResolver();
      frameSetResolver = null;
    }
  });

  // Navigate to bundle
  await page.goto(`http://127.0.0.1:${PORT}/index.html?mode=persistent`);

  // Wait until window.remotion_ready is true
  await page.waitForFunction(() => window.remotion_ready === true, { timeout: 30000 });

  tabPool[index] = {
    index,
    page,
    free: true,
    setProps: async (props) => {
      return new Promise(async (resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error(`Timeout setting props on tab ${index}`)), 5000);
        propsSetResolver = () => {
          clearTimeout(timeout);
          resolve();
        };
        try {
          await page.evaluate((p) => window.remotion_setProps(p), props);
        } catch (e) {
          clearTimeout(timeout);
          reject(e);
        }
      });
    },
    setFrame: async (frame) => {
      return new Promise(async (resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error(`Timeout setting frame ${frame} on tab ${index}`)), 2000);
        frameSetResolver = () => {
          clearTimeout(timeout);
          resolve();
        };
        try {
          await page.evaluate((f) => window.remotion_setFrame(f), frame);
        } catch (e) {
          clearTimeout(timeout);
          reject(e);
        }
      });
    }
  };
}

async function getTab() {
  for (const tab of tabPool) {
    if (tab.free) {
      tab.free = false;
      return tab;
    }
  }
  return null;
}

async function processQueue() {
  if (queue.length === 0) return;
  const tab = await getTab();
  if (!tab) return;

  // Another completion may have consumed the last queued request while this
  // async worker was acquiring a tab. Do not crash the renderer in that race.
  if (queue.length === 0) {
    tab.free = true;
    return;
  }

  const { req, res } = queue.shift();
  try {
    const { slide_data, slide_index, output_path } = req.body;
    const renderStartedAt = performance.now();

    const tempDir = path.join('/tmp', `render_${Date.now()}_s${slide_index}`);
    fs.mkdirSync(tempDir, { recursive: true });

    // Remotion's renderer drives Chromium directly. The previous custom CDP
    // screenshot-per-frame loop could deadlock after a few frames on Azure.
    const propsPath = path.join(tempDir, 'props.json');
    fs.writeFileSync(propsPath, JSON.stringify({ slides: [slide_data], audioUrls: [] }));
    const remotionStartedAt = performance.now();
    const remotionArgs = [
      'remotion', 'render', 'bundled', 'EducationalVideo', output_path,
      '--props', propsPath, '--frames=0-71', '--concurrency=1', '--log=error',
    ];
    const remotion = spawn('npx', remotionArgs, { cwd: __dirname });
    let stderr = '';
    remotion.stderr.on('data', (data) => { stderr += data.toString(); });
    remotion.on('close', (code) => {
      fs.rmSync(tempDir, { recursive: true, force: true });
      if (code === 0) {
        res.json({
          success: true,
          renderer_version: 'remotion-cli-v1',
          output_path,
          metrics: {
            tab_index: tab.index,
            remotion_seconds: Number(((performance.now() - remotionStartedAt) / 1000).toFixed(3)),
            total_seconds: Number(((performance.now() - renderStartedAt) / 1000).toFixed(3)),
          },
        });
      } else {
        res.status(500).json({ error: `Remotion failed with exit code ${code}: ${stderr}` });
      }
      tab.free = true;
      processQueue();
    });

  } catch (error) {
    console.error(`Error rendering slide on tab ${tab.index}:`, error);
    // Replace tab if it crashed/timed out
    try {
      tabReplacements++;
      if (tab.page) {
        await tab.page.close().catch(() => {});
        await initTab(tab.index);
      }
    } catch (e) {
      console.error(`Failed to replace crashed tab ${tab.index}:`, e);
    }
    res.status(500).json({ error: error.message });
    tab.free = true;
    processQueue();
  }
}

const app = express();
app.use(express.json());

// Serve static bundled folder
app.use(express.static(BUNDLE_DIR));

app.post('/render', (req, res) => {
  const { slide_data, slide_index, est_duration, output_path } = req.body;
  if (!slide_data || slide_index === undefined || !output_path) {
    return res.status(400).json({ error: "Missing required parameters (slide_data, slide_index, output_path)" });
  }

  queue.push({ req, res });
  processQueue();
});

// Health check / status endpoint
app.get('/status', (req, res) => {
  res.json({
    renderer_version: RENDERER_VERSION,
    pool_size: tabPool.length,
    active_jobs: tabPool.filter(t => !t.free).length,
    queue_length: queue.length,
    tab_replacements: tabReplacements
  });
});

async function main() {
  // Start server
  app.listen(PORT, '127.0.0.1', async () => {
    console.log(`Renderer service serving assets and listening on http://127.0.0.1:${PORT}`);
    // Two slots limit the VM to its intended two local slides. Each slot uses
    // Remotion's native renderer, which owns and cleans up its Chromium run.
    tabPool.push({ index: 0, free: true });
    tabPool.push({ index: 1, free: true });
    console.log("Renderer service successfully initialized!");
  });
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log("SIGTERM received. Cleaning up browser...");
  if (browser) {
    await browser.close();
  }
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log("SIGINT received. Cleaning up browser...");
  if (browser) {
    await browser.close();
  }
  process.exit(0);
});

main();
