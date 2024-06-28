document.addEventListener('DOMContentLoaded', function () {
    // Function to handle video playback
    const videoPlayer = document.getElementById('my-video');
    videoPlayer.addEventListener('play', function () {
        console.log('Video is playing');
    });

    // Other video playback controls can be added as needed
});
