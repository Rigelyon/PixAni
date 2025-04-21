document.getElementById('embedBtn').addEventListener('click', function () {
    const formData = new FormData();
    const image = document.getElementById('imageInput').files[0];
    const message = document.getElementById('secretMessage').value;

    if (!image || !message) {
        alert("Gambar dan pesan harus diisi!");
        return;
    }

    formData.append('image', image);
    formData.append('message', message);

    fetch('/encode/', {
        method: 'POST',
        body: formData
    })
    .then(res => res.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        document.getElementById('outputImage').style.display = 'block';
        document.getElementById('outputImage').src = url;
        document.getElementById('extractedMessage').innerText = '';
    });
});

document.getElementById('extractBtn').addEventListener('click', function () {
    const formData = new FormData();
    const image = document.getElementById('imageInput').files[0];

    if (!image) {
        alert("Silakan upload gambar untuk diekstrak.");
        return;
    }

    formData.append('image', image);

    fetch('/decode/', {
        method: 'POST',
        body: formData
    })
    .then(res => res.text())
    .then(message => {
        document.getElementById('extractedMessage').innerText = 'Pesan: ' + message;
        document.getElementById('outputImage').style.display = 'none';
    });
});
