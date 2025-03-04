import DeviceDetector from "https://cdn.skypack.dev/device-detector-js@2.2.10";
const mpHands = window;
const drawingUtils = window;
const controls = window;
const controls3d = window;

// -------------------
// Configuration values (from config.py)
// -------------------
const RECT_WIDTH_MODE_1 = 300;          // Width of rectangles for Mode 1
const RECT_HEIGHT_MODE_1 = 100;         // Height of rectangles for Mode 1
const SOUND_COOLDOWN = 1.0;             // Sound cooldown in seconds

// Define sound files (using the "C" directory as in your config)
const SOUND_FILES_A = [
  'A4.wav',  // Top-left corner
  'G4.wav',  // Second on left
  'D4.wav',  // Third on left
  'E4.wav',  // Bottom-left corner
  'E3.wav',  // Top-right corner
  'D3.wav',  // Second on right
  'B3.wav',  // Third on right
  'A3.wav',  // Bottom-right corner
].map(s => `./audio/C/${s}`);

// Define string colors for rectangles (using CSS rgb strings)
const STRING_COLORS = [
  'rgb(255,87,34)',    // Deep Orange
  'rgb(255,193,7)',    // Amber
  'rgb(76,175,80)',    // Green
  'rgb(33,150,243)',   // Blue
  'rgb(156,39,176)',   // Purple
  'rgb(0,188,212)',    // Cyan
  'rgb(255,235,59)',   // Yellow
  'rgb(244,67,54)'     // Red
];

// Create an Audio object for each sound file
const audioElements = SOUND_FILES_A.map(file => new Audio(file));
// Array to track last play times (one per rectangle), stored in milliseconds.
let lastPlayedTime = new Array(8).fill(0);

// -------------------
// Device support check
// -------------------
testSupport([{ client: 'Chrome' }]);
function testSupport(supportedDevices) {
  const deviceDetector = new DeviceDetector();
  const detectedDevice = deviceDetector.parse(navigator.userAgent);
  let isSupported = false;
  for (const device of supportedDevices) {
    if (device.client !== undefined) {
      const re = new RegExp(`^${device.client}$`);
      if (!re.test(detectedDevice.client.name)) {
        continue;
      }
    }
    if (device.os !== undefined) {
      const re = new RegExp(`^${device.os}$`);
      if (!re.test(detectedDevice.os.name)) {
        continue;
      }
    }
    isSupported = true;
    break;
  }
  if (!isSupported) {
    alert(`This demo, running on ${detectedDevice.client.name}/${detectedDevice.os.name}, is not well supported at this time, continue at your own risk.`);
  }
}

// -------------------
// Set up video and canvas elements
// -------------------
const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const controlsElement = document.getElementsByClassName('control-panel')[0];
const canvasCtx = canvasElement.getContext('2d');
const config = {
  locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/hands@${mpHands.VERSION}/${file}`;
  }
};

// FPS control for display in the control panel.
const fpsControl = new controls.FPS();

// Hide spinner after its transition.
const spinner = document.querySelector('.loading');
spinner.ontransitionend = () => {
  spinner.style.display = 'none';
};

// Landmark grid for 3D view.
const landmarkContainer = document.getElementsByClassName('landmark-grid-container')[0];
const grid = new controls3d.LandmarkGrid(landmarkContainer, {
  connectionColor: 0xCCCCCC,
  definedColors: [
    { name: 'Left', value: 0xffa500 },
    { name: 'Right', value: 0x00ffff }
  ],
  range: 0.2,
  fitToGrid: false,
  labelSuffix: 'm',
  landmarkSize: 2,
  numCellsPerAxis: 4,
  showHidden: false,
  centered: false,
});

// -------------------
// Functions for rectangles and strings (Mode 1 only)
// -------------------

// Returns an array of 8 rectangles for Mode 1.
function getRectanglesMode1(frameWidth, frameHeight) {
  return [
    // Left side (4 rectangles)
    { x: 0, y: 0, w: RECT_WIDTH_MODE_1, h: RECT_HEIGHT_MODE_1 },
    { x: 0, y: RECT_HEIGHT_MODE_1, w: RECT_WIDTH_MODE_1, h: RECT_HEIGHT_MODE_1 },
    { x: 0, y: 2 * RECT_HEIGHT_MODE_1, w: RECT_WIDTH_MODE_1, h: RECT_HEIGHT_MODE_1 },
    { x: 0, y: 3 * RECT_HEIGHT_MODE_1, w: RECT_WIDTH_MODE_1, h: RECT_HEIGHT_MODE_1 },
    // Right side (4 rectangles)
    { x: canvasElement.width - RECT_WIDTH_MODE_1, y: 0, w: RECT_WIDTH_MODE_1, h: RECT_HEIGHT_MODE_1 },
    { x: canvasElement.width - RECT_WIDTH_MODE_1, y: RECT_HEIGHT_MODE_1, w: RECT_WIDTH_MODE_1, h: RECT_HEIGHT_MODE_1 },
    { x: canvasElement.width - RECT_WIDTH_MODE_1, y: 2 * RECT_HEIGHT_MODE_1, w: RECT_WIDTH_MODE_1, h: RECT_HEIGHT_MODE_1 },
    { x: canvasElement.width - RECT_WIDTH_MODE_1, y: 3 * RECT_HEIGHT_MODE_1, w: RECT_WIDTH_MODE_1, h: RECT_HEIGHT_MODE_1 },
  ];
}

// Draws rectangles, centers pitch text, and draws a vertical "string" line.
function drawRectanglesAndStrings(ctx, rectangles, stringColors, soundFiles) {
  ctx.save();
  ctx.font = "48px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (let idx = 0; idx < rectangles.length; idx++) {
    const rect = rectangles[idx];
    // Draw rectangle border.
    ctx.lineWidth = 4;
    ctx.strokeStyle = "green";
    ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);

    // Extract pitch text from the sound file name.
    let fileName = soundFiles[idx].split('/').pop(); // e.g., "A4.wav"
    let pitchText = fileName.split('.')[0]; // e.g., "A4"
    const textX = rect.x + rect.w / 2;
    const textY = rect.y + rect.h / 2;
    ctx.fillStyle = stringColors[idx];
    ctx.fillText(pitchText, textX, textY);

    // Draw the vertical string line.
    ctx.beginPath();
    let lineX = idx < 4 ? (rect.x + rect.w - 3) : (rect.x + 3);
    ctx.moveTo(lineX, rect.y);
    ctx.lineTo(lineX, rect.y + rect.h);
    ctx.lineWidth = 10; // String thickness.
    ctx.strokeStyle = stringColors[idx];
    ctx.stroke();
  }
  ctx.restore();
}

// -------------------
// onResults callback (modified for Mode 1)
// -------------------
function onResults(results) {
  // Hide the spinner.
  document.body.classList.add('loaded');
  // Update the frame rate.
  fpsControl.tick();
  // Draw the overlays.
  canvasCtx.save();
  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
  if (results.multiHandLandmarks && results.multiHandedness) {
    for (let index = 0; index < results.multiHandLandmarks.length; index++) {
      const classification = results.multiHandedness[index];
      const isRightHand = classification.label === 'Right';
      const landmarks = results.multiHandLandmarks[index];
      drawingUtils.drawConnectors(canvasCtx, landmarks, mpHands.HAND_CONNECTIONS, { color: isRightHand ? '#00FF00' : '#FF0000' });
      drawingUtils.drawLandmarks(canvasCtx, landmarks, {
        color: isRightHand ? '#00FF00' : '#FF0000',
        fillColor: isRightHand ? '#FF0000' : '#00FF00',
        radius: (data) => {
          return drawingUtils.lerp(data.from.z, -0.15, 0.1, 10, 1);
        }
      });
    }
  }
  canvasCtx.restore();

  // ---------- Draw rectangles and strings, and check for finger collision ----------
  const rects = getRectanglesMode1(canvasElement.width, canvasElement.height);
  drawRectanglesAndStrings(canvasCtx, rects, STRING_COLORS, SOUND_FILES_A);

  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    const tip = results.multiHandLandmarks[0][8]; // Index finger tip.
    const tipX = tip.x * canvasElement.width;
    const tipY = tip.y * canvasElement.height;
    for (let i = 0; i < rects.length; i++) {
      const rect = rects[i];
      if (tipX >= rect.x && tipX <= rect.x + rect.w &&
          tipY >= rect.y && tipY <= rect.y + rect.h) {
        const currentTime = Date.now();
        if (currentTime - lastPlayedTime[i] > SOUND_COOLDOWN * 1000) {
          // Clone the audio element to allow immediate play.
          const soundClone = audioElements[i].cloneNode();
          soundClone.play();
          lastPlayedTime[i] = currentTime;
        }
      }
    }
  }
  // -----------------------------------------------------------------------------------

  if (results.multiHandWorldLandmarks) {
    // Merge world landmarks and offset connections for the 3D grid.
    const landmarks = results.multiHandWorldLandmarks.reduce((prev, current) => [...prev, ...current], []);
    const colors = [];
    let connections = [];
    for (let loop = 0; loop < results.multiHandWorldLandmarks.length; ++loop) {
      const offset = loop * mpHands.HAND_CONNECTIONS.length;
      const offsetConnections = mpHands.HAND_CONNECTIONS.map((connection) => [connection[0] + offset, connection[1] + offset]);
      connections = connections.concat(offsetConnections);
      const classification = results.multiHandedness[loop];
      colors.push({
        list: offsetConnections.map((unused, i) => i + offset),
        color: classification.label,
      });
    }
    grid.updateLandmarks(landmarks, connections, colors);
  } else {
    grid.updateLandmarks([]);
  }
}

const hands = new mpHands.Hands(config);
hands.onResults(onResults);

// -------------------
// Present control panel for adjusting options.
// -------------------
new controls
  .ControlPanel(controlsElement, {
    selfieMode: true,
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
  })
  .add([
    new controls.StaticText({ title: 'MediaPipe Hands' }),
    fpsControl,
    new controls.Toggle({ title: 'Selfie Mode', field: 'selfieMode' }),
    new controls.SourcePicker({
      onFrame: async (input, size) => {
        const aspect = size.height / size.width;
        let width, height;
        if (window.innerWidth > window.innerHeight) {
          height = window.innerHeight;
          width = height / aspect;
        } else {
          width = window.innerWidth;
          height = width * aspect;
        }
        canvasElement.width = width;
        canvasElement.height = height;
        await hands.send({ image: input });
      },
    }),
    new controls.Slider({
      title: 'Max Number of Hands',
      field: 'maxNumHands',
      range: [1, 4],
      step: 1
    }),
    new controls.Slider({
      title: 'Model Complexity',
      field: 'modelComplexity',
      discrete: ['Lite', 'Full'],
    }),
    new controls.Slider({
      title: 'Min Detection Confidence',
      field: 'minDetectionConfidence',
      range: [0, 1],
      step: 0.01
    }),
    new controls.Slider({
      title: 'Min Tracking Confidence',
      field: 'minTrackingConfidence',
      range: [0, 1],
      step: 0.01
    }),
  ])
  .on(x => {
    const options = x;
    videoElement.classList.toggle('selfie', options.selfieMode);
    hands.setOptions(options);
  });
