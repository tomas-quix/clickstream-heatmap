// Function to replace 'heatmap' with 'heatmap-ws' and create WebSocket URL
function createClickstreamWebSocketURL() {
    // Dynamically get the current URL from the window object
    const currentServiceURL = `${window.location.protocol}//${window.location.host}${window.location.pathname}`;
  
    // Assuming the service name is in the subdomain, replace 'heatmap' with 'heatmap-ws'
    const clickstreamURL = currentServiceURL.replace('heatmap', 'heatmap-ws');
  
    // Decide on the WebSocket protocol based on the current protocol (http or https)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
  
    // Construct the WebSocket URL, excluding the 'http:' or 'https:' part from clickstreamURL
    const baseURL = clickstreamURL.substring(clickstreamURL.indexOf('//') + 2);
    const fullWSURL = `${wsProtocol}${baseURL}`;
  
    console.log(baseURL);
    
  return fullWSURL;
  }
  
  const socket = new WebSocket(createClickstreamWebSocketURL());
  
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
  
  // Function to calculate color intensity based on heatmap value, with transparency
  function getColorIntensity(value, maxValue) {
    const intensity = Math.min(1, value / maxValue);
    const redIntensity = Math.floor(intensity * 255);
    return `rgba(${redIntensity},0,0,0.5)`; // Adjust transparency as needed
  }
  
  // Function to draw the heatmap
  function drawHeatmap(heatmapData, gridSize) {
    const tileWidth = canvas.width / gridSize;
    const tileHeight = canvas.height / gridSize;
  
    let maxValue = 0;
    for (let x = 0; x < gridSize; x++) {
      for (let y = 0; y < gridSize; y++) {
        const value = heatmapData[x]?.[y] ?? 0;
        if (value > maxValue) {
          maxValue = value; // Update maxValue if current value is greater
        }
      }
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas for redraw
    for (let x = 0; x < gridSize; x++) {
      for (let y = 0; y < gridSize; y++) {
        const value = heatmapData[x]?.[y] ?? 0;
        ctx.fillStyle = getColorIntensity(value, maxValue);
        ctx.fillRect(x * tileWidth, y * tileHeight, tileWidth, tileHeight);
      }
    }
  }
  
  // Initialize an empty heatmap data structure
  let heatmapData = {};
  let gridSize = 0;
  
  socket.onmessage = function(event) {
    console.log(event);
    const data = JSON.parse(event.data);
  
    if (data["grid-size"] != heatmapData.length) {
      gridSize = data["grid-size"];
      heatmapData = Array.from({ length: gridSize }, () => Array(gridSize).fill(0));
    }
  
    if (data["tile-coordinates"]["x"] !== undefined && data["tile-coordinates"]["y"] !== undefined) {
      const x = data["tile-coordinates"]["x"];
      const y = data["tile-coordinates"]["y"];
      const value = data["value"] ?? 1;
  
      if (!heatmapData[x]) {
        heatmapData[x] = [];
      }
  
      heatmapData[x][y] = (heatmapData[x][y] ?? 0) + value;
  
      drawHeatmap(heatmapData, gridSize);
    }
  };
  
  // Error handling
  socket.onerror = function(error) {
    console.log(error);
  };
  
  // Optionally, handle the WebSocket connection opening
  socket.onopen = function(event) {
    console.log('WebSocket connection established');
    // You can also send messages to the server here if needed
  };