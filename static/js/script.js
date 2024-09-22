const fileNameDisplay = document.getElementById("fileName");
function updateFileName(input) {
  const fileName = input.files.length > 0 ? input.files[0].name : "";
  fileNameDisplay.textContent = fileName
    ? `Selected file: ${fileName}`
    : "No file selected";
}

// SHADOW STUFF

const container = document.getElementById("splash");
const text = document.getElementById("title");

const distance = 30;

function setShadow(e) {
  const width = this.offsetWidth;
  const height = this.offsetHeight;

  let x = e.offsetX;
  let y = e.offsetY;

  if (this !== e.target) {
    x = x + e.target.offsetLeft;
    y = y + e.target.offsetTop;
  }

  const xDistance = Math.round((x / width) * distance - distance / 2);
  const yDistance = Math.round((y / height) * distance - distance / 2);

  text.style.textShadow = `${xDistance}px ${yDistance}px #FFFFFF`;
}

container.addEventListener("mousemove", setShadow);

// Camera and audio recording

const video = document.getElementById("video");
const startCameraButton = document.getElementById("startCamera");
const captureButton = document.getElementById("capture");
const canvas = document.getElementById("canvas");
const cameraImageInput = document.getElementById("cameraImage");
const startRecordingButton = document.getElementById("startRecording");
const stopRecordingButton = document.getElementById("stopRecording");
let mediaRecorder;
let audioChunks = [];

function sendAudioToServer() {
  const audioBlob = new Blob(audioChunks, {
    type: "audio/wav",
  });
  const formData = new FormData();
  formData.append("file", audioBlob, "recording.wav");

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.text()) // We expect a text response (HTML)
    .then((html) => {
      // Inject the HTML response into the resultsContainer
      document.getElementById("resultsContainer").innerHTML = html;
      console.log(
        "New HTML response at:",
        new Date().toLocaleTimeString(),
        "Response: ",
        html
      );
      // Reset the audio chunks
      audioChunks = [];
    })
    .catch((error) => console.error("Error:", error));
}

startCameraButton.addEventListener("click", async () => {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: true,
  });
  video.srcObject = stream;
  video.style.display = "block";
  video.play();
  captureButton.style.display = "block";
});

captureButton.addEventListener("click", () => {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const imageData = canvas.toDataURL("image/png");
  cameraImageInput.value = imageData;
  video.style.display = "none";
  captureButton.style.display = "none";
});

// Audio recording functionality
startRecordingButton.addEventListener("click", async () => {
  console.log("clicked");
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
  });
  mediaRecorder = new MediaRecorder(stream, {
    mimeType: "audio/webm;codecs=opus", // Use a suitable codec
  });
  audioChunks = []; // Reset audio chunks

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, {
      type: "audio/wav",
    });
    audioChunks = [];

    // Convert audioBlob to WAV format before sending
    const reader = new FileReader();
    reader.onloadend = function () {
      const audioArrayBuffer = reader.result;
      // Convert ArrayBuffer to WAV here
      const wavBlob = convertToWav(audioArrayBuffer); // Implement this function
      const formData = new FormData(document.getElementById("mainForm"));
      formData.append("audio", wavBlob, "recording.wav");
      // Send the FormData via POST request
      fetch("/submit", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.blob())
        .then((blob) => {
          console.log("blob", blob);
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "calendar_events.ics";
          document.body.appendChild(a);
          a.click();
          a.remove();
        })
        .catch((error) => console.error("Error:", error));
    };
    reader.readAsArrayBuffer(audioBlob);
  };

  mediaRecorder.start();
  startRecordingButton.style.display = "none";
  stopRecordingButton.style.display = "block";
});

stopRecordingButton.addEventListener("click", () => {
  console.log("stop button clicked");
  mediaRecorder.stop();
  startRecordingButton.style.display = "block";
  stopRecordingButton.style.display = "none";
});

function convertToWav(audioBuffer) {
  // Convert audioBuffer to WAV format using a library like WAVEncoder.js
  // or handle the conversion manually using ArrayBuffer manipulations.

  // Placeholder: Use a library to create a WAV blob from the audio buffer
  const wavBlob = new Blob([audioBuffer], {
    type: "audio/wav",
  });
  return wavBlob;
}
