const bgPanel = document.getElementById('bg-panel');
let isStreaming = false;
let isAutoCapture = false;

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
  this.classList.toggle('clicked')
  setTimeout(() => {
    this.classList.toggle('clicked')
  }, 200);
  // Implement clean functionality
  doCleanReqquest()
}

function handleAutoButtonClick() {
  this.classList.toggle('clicked')
  // Implement auto functionality
  isAutoCapture = !isAutoCapture;
  doAutoCaptureRequest(isAutoCapture)
}

function handleCaptureButtonClick() {
  this.classList.toggle('clicked')
  setTimeout(() => {
    this.classList.toggle('clicked')
  }, 200);
  // Implement capture functionality
  doSingleCaptureRequest()
}

function handleStreamButtonClick() {
  this.classList.toggle('clicked')
  console.log("Stream button clicked.....");
  if (isStreaming) stopStreaming() // stop streaming from client first then do request to stop it on server side
  isStreaming = !isStreaming;
  doStreamRequest();
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

function doAutoCaptureRequest(isAutoCapture) {
  fetch('/request_auto_capture', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ auto: isAutoCapture }),
  })
  .catch(error => {
    console.error('Fetch error:', error); // Handle fetch error
  });
}

function doSingleCaptureRequest() {
  fetch('/request_single_capture', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ capture: true }),
  })
  .catch(error => {
    console.error('Fetch error:', error); // Handle fetch error
  });
}

function doStreamRequest() {
  fetch('/request_stream?' + new Date().getTime(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ startStream: isStreaming }),
  })
  .then(response => response.json())
  .then(data => {
    const isStreaming = data.isStreaming; // Access the isStreaming property
    if (isStreaming) {
      console.log("Starting stream...");
      startStreaming();
    } else {
      console.log("Stoped!");
    }
  })
  .catch(error => {
    console.error('Fetch error:', error); // Handle fetch error
  });
}

function doCleanReqquest() {
  fetch('/request_clean', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ clean: true }),
  })
  .then(response => response.json())
  .then(data => print (data))
  .catch(error => {
    console.error('Fetch error:', error); // Handle fetch error
  });
}

function startStreaming() {
  const streamImage = document.getElementById('streamImage');
  streamImage.src = '/stream?' + new Date().getTime();
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
setInterval(() => {
  if (!isStreaming) {
    updateUI();
  }
}, 500);
