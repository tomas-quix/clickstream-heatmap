
function generateGUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
  });
}

const session_id = generateGUID()

// Function to replace 'webshop' with 'clickstream' and create WebSocket URL
function createClickstreamWebSocketURL(session_id) {
  // Dynamically get the current URL from the window object
  const currentServiceURL = `${window.location.protocol}//${window.location.host}${window.location.pathname}`;

  // Assuming the service name is in the subdomain, replace 'webshop' with 'clickstream'
  const clickstreamURL = currentServiceURL.replace('heatmap', 'heatmap-ws');

  // Decide on the WebSocket protocol based on the current protocol (http or https)
  const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';

  // Construct the WebSocket URL, excluding the 'http:' or 'https:' part from clickstreamURL
  const baseURL = clickstreamURL.substring(clickstreamURL.indexOf('//') + 2);
  const fullWSURL = `${wsProtocol}${baseURL}${session_id}`;

  return fullWSURL;
}

const socket = new WebSocket(createClickstreamWebSocketURL(session_id));


// Create a canvas element and overlay it over the page
const canvas = document.createElement('canvas');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
canvas.style.position = 'fixed';
canvas.style.top = '0';
canvas.style.left = '0';
canvas.style.zIndex = '10000'; // Make sure it's on top of other content
canvas.style.pointerEvents = 'none'; // Allows clicking through the canvas
document.body.appendChild(canvas);

const ctx = canvas.getContext('2d');
const tileWidth = canvas.width / 10;
const tileHeight = canvas.height / 10;

// Function to calculate color intensity based on heatmap value, with transparency
function getColorIntensity(value) {
    const maxValue = 4; // This might need to be dynamic based on incoming data
    const intensity = Math.min(1, value / maxValue);
    const redIntensity = Math.floor(intensity * 255);
    return `rgba(${redIntensity},0,0,0.5)`; // Adjust transparency as needed
}

// Function to draw the heatmap
function drawHeatmap(heatmapData) {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas for redraw
    for (let x = 0; x < 10; x++) {
        for (let y = 0; y < 10; y++) {
            const value = heatmapData[x]?.[y] ?? 0;
            ctx.fillStyle = getColorIntensity(value);
            ctx.fillRect(x * tileWidth, y * tileHeight, tileWidth, tileHeight);
        }
    }
}

socket2.onmessage = function(event) {
    console.log(event);
    const data = JSON.parse(event.data);
    // Assuming the incoming message is the heatmap data
    // Adjust this as necessary based on the structure of your WebSocket messages
    drawHeatmap(data["value"]);
};

// Error handling
socket2.onerror = function(error) {
    console.log(error);
};

// Optionally, handle the WebSocket connection opening
socket2.onopen = function(event) {
    console.log('WebSocket connection established');
    // You can also send messages to the server here if needed
};
