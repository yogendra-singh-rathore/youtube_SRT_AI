document.addEventListener('DOMContentLoaded', function () {
    // Accordion functionality for FAQ section (if any)
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

    // Sidebar toggle functionality
    const sidebar = document.getElementById('sidebar');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');

    mobileMenuToggle.addEventListener('click', function () {
        sidebar.classList.toggle('active');
    });
});
