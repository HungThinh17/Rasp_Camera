  const bgPanel = document.getElementById('bg-panel');
  let isStreaming = false;

  document.addEventListener('DOMContentLoaded', function() {
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
    console.log("Stream button clicked.....");
      fetch('/handleStream', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ startStream: !isStreaming }),
      })
      .then(response => response.json())
      .then(data => {
          isStreaming = data.isStreaming;
          if (isStreaming) {
              console.log("Starting stream...");
              startStreaming();
          } else {
              console.log("Stopping stream...");
              stopStreaming();
          }
      })
      .catch(error => console.error('Error:', error));
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
      // Implement UI update logic here
  }

  function startStreaming() {
    const streamImage = document.getElementById('streamImage');
    streamImage.src = '/stream';
    streamImage.style.display = 'block';
  }

  function stopStreaming() {
    const streamImage = document.getElementById('streamImage');
    streamImage.src = '';
    streamImage.style.display = 'none';
    bgPanel.style.backgroundImage = "url('Digime.jpeg')";
  }
  // Call updateUI periodically
  setInterval(updateUI, 1000); // Update every second, adjust as needed