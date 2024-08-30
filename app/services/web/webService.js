const bgPanel = document.getElementById('bg-panel');
let isStreaming = false;

document.addEventListener('DOMContentLoaded', function () {
  // Add event listeners and functionality here
  document.getElementById('btExit').addEventListener('click', handleExitButtonClick);
  document.getElementById('btClean').addEventListener('click', handleCleanButtonClick);
  document.getElementById('btAuto').addEventListener('click', handleAutoButtonClick);
  document.getElementById('btCapture').addEventListener('click', handleCaptureButtonClick);
  document.getElementById('btStream').addEventListener('click', handleStreamButtonClick);
  document.getElementById('btPreview').addEventListener('click', handlePreviewButtonClick);
  document.getElementById('btPrevious').addEventListener('click', handlePreviousButtonClick);
  document.getElementById('btNext').addEventListener('click', handleNextButtonClick);
  document.getElementById('btIdling').addEventListener('click', handleIdlingButtonClick);

  window.addEventListener('beforeunload', stopStreaming);
  const streamImage = document.getElementById('streamImage');
  streamImage.addEventListener('error', handleStreamError);
});

function handleExitButtonClick() {
  // Implement exit functionality
}

function handleCleanButtonClick() {
  // Implement clean functionality
}

function handleAutoButtonClick() {
  // Implement auto functionality
}

function handleCaptureButtonClick() {
  // Implement capture functionality
}

function handleStreamButtonClick() {
  this.classList.toggle('clicked')
  console.log("Stream button clicked.....");
  if (isStreaming) {
    stopStreaming();
  } else {
    doStreamRequest();
  }
  isStreaming = !isStreaming
}

function handlePreviewButtonClick() {
  // Implement preview functionality
}

function handlePreviousButtonClick() {
  // Implement previous functionality
}

function handleNextButtonClick() {
  // Implement next functionality
}

function handleIdlingButtonClick() {
  // Implement idling functionality
}

function updateUI() {
  fetch('/info')
    .then(response => response.text())
    .then(data => {
      // Update UI elements based on the received data
      const lbInfo = document.getElementById('lbInfo');
      lbInfo.innerHTML = data.replace(/\n/g, '<br>');;
    })
    .catch(error => {
      console.error('Fetch error:', error); // Handle fetch error
    });
}

function doStreamRequest() {
  fetch('/request_stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ startStream: !isStreaming }),
  })
    .then(response => response.json())
    .then(data => {
      const isStreaming = data.isStreaming; // Access the isStreaming property
      if (isStreaming) {
        console.log("Starting stream...");
        startStreaming();
      }
    })
    .catch(error => {
      console.error('Fetch error:', error); // Handle fetch error
    });
}

function startStreaming() {
  const streamImage = document.getElementById('streamImage');
  streamImage.src = '/stream'
  streamImage.style.display = 'block'; // Ensure the image is visible
}

function stopStreaming() {
  const streamImage = document.getElementById('streamImage');
  streamImage.src = 'Digime.jpeg'
  streamImage.style.display = 'block'; // Hide the image
}

function handleStreamError() {
  if (isStreaming) {
    console.log("Stream error...");
    isStreaming = false
  }
}  

// Call updateUI every 1000 milliseconds (1 second)
setInterval(updateUI, 500);
