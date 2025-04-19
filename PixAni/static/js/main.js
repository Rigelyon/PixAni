document.addEventListener('DOMContentLoaded', function () {
    const decodeImageForm = document.getElementById('decodeImageForm');
    const decodedDataContainer = document.getElementById('decodedData');
    const decodedDataPre = decodedDataContainer.querySelector('pre');

    decodeImageForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(decodeImageForm);

        fetch('/decode_image/', {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    decodedDataPre.textContent = JSON.stringify(data.decoded_data, null, 4);
                    decodedDataContainer.classList.remove('d-none');
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
    });
});
