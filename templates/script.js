const video = document.getElementById('video');
const startCameraButton = document.getElementById('startCamera');
const captureButton = document.getElementById('capture');
const canvas = document.getElementById('canvas');
const cameraImageInput = document.getElementById('cameraImage');
const fileNameDisplay = document.getElementById('fileName');

startCameraButton.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.style.display = 'block';
    video.play();
    captureButton.style.display = 'block';
});

captureButton.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const imageData = canvas.toDataURL('image/png');
    cameraImageInput.value = imageData;
    video.style.display = 'none';
    captureButton.style.display = 'none';
});

function updateFileName(input) {
    const fileName = input.files.length > 0 ? input.files[0].name : '';
    fileNameDisplay.textContent = fileName ? `Selected file: ${fileName}` : 'No file selected';
}


// SHADOW STUFF

const container = document.getElementById('splash');
const text = document.getElementById('title');

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

    const xDistance = Math.round(( x / width * distance) - (distance / 2));
    const yDistance = Math.round(( y / height * distance) - (distance / 2));

    text.style.textShadow = `${xDistance}px ${yDistance}px #EB492C`;
}

container.addEventListener('mousemove', setShadow);