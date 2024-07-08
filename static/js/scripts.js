document.addEventListener('DOMContentLoaded', function () {
    // Function to handle video playback
    const videoPlayer = document.getElementById('my-video');
    if (videoPlayer) {
        videoPlayer.addEventListener('play', function () {
            console.log('Video is playing');
        });
    }

    // Accordion functionality for FAQ section
    var acc = document.getElementsByClassName("accordion");
    var i;

    for (i = 0; i < acc.length; i++) {
        acc[i].addEventListener("click", function () {
            this.classList.toggle("active");
            var panel = this.nextElementSibling;
            if (panel.style.maxHeight) {
                panel.style.maxHeight = null;
            } else {
                panel.style.maxHeight = panel.scrollHeight + "px";
            }
        });
    }
});
