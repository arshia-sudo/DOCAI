// Initialize the QR code scanner after the DOM content is loaded
document.addEventListener("DOMContentLoaded", function() {
    const qrCodeScanner = new Html5QrcodeScanner("qr-reader", {
        fps: 10,  // Set frames per second for the scanning
        qrbox: 250, // Size of the scanning box
        aspectRatio: 1.0, // Aspect ratio of the box
        rememberLastUsedCamera: true, // Keep track of the last used camera
    });

    // Start scanning
    qrCodeScanner.render(onScanSuccess, onScanError);

    // Handle successful QR code scanning
    function onScanSuccess(decodedText, decodedResult) {
        console.log(`QR Code scanned: ${decodedText}`);
        
        // Assuming the QR code contains patient information such as patient ID
        // Redirect to the patient's report page or handle it as required
        window.location.href = `/patient_report/${decodedText}`;
    }

    // Handle errors during scanning
    function onScanError(errorMessage) {
        console.error(`Error scanning QR code: ${errorMessage}`);
    }
});
