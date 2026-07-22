const express = require('express');
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const PORT = 5000;
const BUNDLE_DIR = path.join(__dirname, 'bundled');
const RENDERER_VERSION = 'modex-persistent-v1';

// Read pool size from environment variable, default to 8 for parallel execution
const POOL_SIZE = parseInt(process.env.POOL_SIZE || '8', 10);

async function findChromePath() {
  const paths = [
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable'
  ];
  for (const p of paths) {
    if (fs.existsSync(p)) return p;
  }
  throw new Error("Could not find Chromium or Chrome executable on the system");
}

async function launchBrowser() {
  const executablePath = await findChromePath();
  console.log(`Launching headless Chromium from ${executablePath}...`);
  
  const browser = await puppeteer.launch({
    executablePath,
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
    protocolTimeout: 120000,
  });
  return browser;
}

let browser = null;
const tabPool = [];
const queue = [];
let tabReplacements = 0;

async function initTab(index) {
  console.log(`Initializing tab ${index}...`);
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 1 });

  page.on('console', msg => console.log(`PAGE LOG [tab ${index}]:`, msg.text()));
  page.on('pageerror', err => console.error(`PAGE ERROR [tab ${index}]:`, err.message));

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

  // Navigate to local bundle page
  await page.goto(`http://127.0.0.1:${PORT}/index.html?mode=persistent`);

  // Wait until Remotion ready signal is set
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
        const timeout = setTimeout(() => reject(new Error(`Timeout setting frame ${frame} on tab ${index}`)), 5000);
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
  console.log(`Tab ${index} initialized successfully.`);
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

  if (queue.length === 0) {
    tab.free = true;
    return;
  }

  const { req, res } = queue.shift();
  try {
    const { slide_data, slide_index, est_duration, output_path } = req.body;
    console.log(`Processing render request on tab ${tab.index} for slide ${slide_index}...`);

    const tempDir = path.join('/tmp', `modex_render_${Date.now()}_s${slide_index}`);
    fs.mkdirSync(tempDir, { recursive: true });

    // Set dynamic props
    await tab.setProps({
      slides: [slide_data],
      audioUrls: []
    });

    // Capture screenshots frame-by-frame (0 to 71 for 3s at 24fps)
    for (let f = 0; f < 72; f++) {
      await tab.setFrame(f);
      const framePath = path.join(tempDir, `frame_${String(f).padStart(3, '0')}.png`);
      await tab.page.screenshot({
        path: framePath,
        type: 'png',
        omitBackground: false
      });
    }

    // Run FFmpeg to compile screenshots into silent MP4
    const ffmpegArgs = [
      '-y',
      '-framerate', '24',
      '-i', path.join(tempDir, 'frame_%03d.png'),
      '-c:v', 'libx264',
      '-preset', 'ultrafast',
      '-crf', '32',
      '-pix_fmt', 'yuv420p',
      output_path
    ];

    const ffmpeg = spawn('ffmpeg', ffmpegArgs);
    let stderr = '';
    ffmpeg.stderr.on('data', (data) => { stderr += data.toString(); });

    ffmpeg.on('close', (code) => {
      // Clean up frames folder
      fs.rmSync(tempDir, { recursive: true, force: true });

      if (code === 0) {
        console.log(`Successfully rendered slide ${slide_index} to ${output_path}`);
        res.json({
          success: true,
          output_path,
          metrics: {
            slide_index,
            tab_index: tab.index
          }
        });
      } else {
        console.error(`FFmpeg failed for slide ${slide_index}:`, stderr);
        res.status(500).json({ error: `FFmpeg failed with exit code ${code}: ${stderr}` });
      }

      tab.free = true;
      processQueue();
    });

  } catch (error) {
    console.error(`Error rendering slide on tab ${tab.index}:`, error);
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
app.use(express.static(BUNDLE_DIR));

app.post('/render', (req, res) => {
  const { slide_data, slide_index, est_duration, output_path } = req.body;
  if (!slide_data || slide_index === undefined || !output_path) {
    return res.status(400).json({ error: "Missing parameters" });
  }
  queue.push({ req, res });
  processQueue();
});

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
  browser = await launchBrowser();
  
  app.listen(PORT, '127.0.0.1', async () => {
    console.log(`Renderer service serving assets and listening on http://127.0.0.1:${PORT}`);
    
    // Initialize pool of tabs
    const promises = [];
    for (let i = 0; i < POOL_SIZE; i++) {
      tabPool.push({ index: i, free: false }); // mark temporarily busy during init
      promises.push(initTab(i).then(() => {
        tabPool[i].free = true;
      }));
    }
    await Promise.all(promises);
    console.log(`Renderer service successfully initialized with ${POOL_SIZE} tabs!`);
  });
}

process.on('SIGTERM', async () => {
  if (browser) await browser.close();
  process.exit(0);
});

process.on('SIGINT', async () => {
  if (browser) await browser.close();
  process.exit(0);
});

main();
