// Initialize PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.worker.min.js';

document.addEventListener('DOMContentLoaded', function() {
    const reportForm = document.getElementById('reportForm');
    const pdfViewer = document.getElementById('pdfViewer');
    const submitButton = reportForm.querySelector('button[type="submit"]');

    reportForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const fileInput = document.getElementById('dataFile');
        
        if (!fileInput.files[0]) {
            alert('Please select a file first');
            return;
        }

        // Check if it's a CSV file
        if (!fileInput.files[0].name.toLowerCase().endsWith('.csv')) {
            alert('Please upload a CSV file');
            return;
        }

        formData.append('file', fileInput.files[0]);

        try {
            // Disable submit button and show loading
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
            
            pdfViewer.innerHTML = `
                <div class="loading">
                    <div class="spinner-border text-primary loading-spinner" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div class="mt-3">Generating Report...</div>
                </div>`;

            // Generate report
            const response = await fetch('/generate_report', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to generate report');
            }

            // Get the PDF data
            const pdfBlob = await response.blob();
            const pdfUrl = URL.createObjectURL(pdfBlob);

            // Load and display the PDF
            const loadingTask = pdfjsLib.getDocument(pdfUrl);
            const pdf = await loadingTask.promise;

            // Clear the viewer
            pdfViewer.innerHTML = '';

            // Display each page
            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                const page = await pdf.getPage(pageNum);
                const scale = 1.5;
                const viewport = page.getViewport({ scale });

                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.height = viewport.height;
                canvas.width = viewport.width;
                canvas.style.marginBottom = '20px';

                const renderContext = {
                    canvasContext: context,
                    viewport: viewport
                };

                await page.render(renderContext).promise;
                pdfViewer.appendChild(canvas);
            }

        } catch (error) {
            console.error('Error:', error);
            pdfViewer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    ${error.message || 'Failed to generate report. Please try again.'}
                </div>`;
        } finally {
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.innerHTML = 'Generate Report';
        }
    });
});
