let canvas = document.getElementById('sketchpad');
let ctx = canvas.getContext('2d');
let mouse = {x: 0, y: 0};
let draw = false;
let saveButton = document.getElementById('saveButton');

// Set the canvas to white to begin with.
ctx.fillStyle = 'white';
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.fillStyle = 'black';

// Set the "gradient" stroke style
ctx.lineWidth = 20; // Simulate brush size like in MNIST
ctx.lineJoin = 'round';
ctx.lineCap = 'round';
ctx.strokeStyle = 'black';
ctx.shadowColor = 'black';
ctx.shadowBlur = 0; // This value can be adjusted

// Event Listener for Mouse Down
canvas.addEventListener('mousedown', function(e) {
    draw = true;
    updateMousePosition(e);
});

let prevMouse = {x: 0, y: 0}; // Track previous mouse position

// Event Listener for Mouse Move
canvas.addEventListener('mousemove', function(e) {
    updateMousePosition(e);
    if (draw) {
        ctx.beginPath();
        ctx.moveTo(prevMouse.x, prevMouse.y); // Start from previous mouse position
        ctx.lineTo(mouse.x, mouse.y); // Draw line to current mouse position
        ctx.stroke();
    }
    prevMouse = {x: mouse.x, y: mouse.y}; // Update previous mouse position
});

// Event Listener for Mouse Up
canvas.addEventListener('mouseup', function() {
    draw = false;
});

// Update Mouse Position
function updateMousePosition(e) {
    mouse.x = e.pageX - canvas.offsetLeft;
    mouse.y = e.pageY - canvas.offsetTop;
}

// Clear Canvas
let clearButton = document.getElementById('clearButton');

clearButton.addEventListener('click', function() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'black';
});

// Save button
saveButton.addEventListener('click', function() {
    // Convert the drawing on the canvas into a data URL
    let dataUrl = canvas.toDataURL('image/png');

    // Prepare the request
    let request = new Request('/save_image/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: dataUrl })
    });

    // Send the request
    fetch(request)
    .then(response => {
        if (response.status === 200) {
            return response.json();
        } else {
            throw new Error('Something went wrong on the server.');
        }
    })
    .then(responseData => {
        // Handle the response data
        document.getElementById('formattedData').textContent = `Prediction: ${responseData.digit}`;
        
        let imageUrl = responseData.image;
        let predictionImage = document.getElementById('predictionImage');
        predictionImage.src = "/media/transformed_image.png?t=" + new Date().getTime();
        console.log(imageUrl);
    })
    .catch(error => {
        console.error(error);
    });
});