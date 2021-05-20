window.onload = () => {

    var socket = io();

    socket.on('arduinoread', data => {
        console.log(data.number);
    });

    socket.on('poem', data => {
        console.log(data.poem);
        let poem = document.getElementById("text");
        poem.classList.add("fadeOut");
        poem.innerHTML = data.poem;
        poem.classList.add("fadeIn");
    });

    // document.getElementById("btn").onclick = () => {
    //     socket.emit("buttonclicked", "clicked");
    // };

    const fullscreen = document.getElementById('fullscreen');
    fullscreen.addEventListener("click", openFullscreen);

    document.addEventListener('fullscreenchange', exitHandler);
    document.addEventListener('webkitfullscreenchange', exitHandler);
    document.addEventListener('mozfullscreenchange', exitHandler);
    document.addEventListener('MSFullscreenChange', exitHandler);

    function exitHandler() {
        if (!document.fullscreenElement && !document.webkitIsFullScreen && !document.mozFullScreen && !document.msFullscreenElement) {
            fullscreen.style.display = "block";
            document.body.style.cursor = 'cursor';
        }
    }

    var elem = document.documentElement;

    function openFullscreen() {
        fullscreen.style.display = "none";
        document.body.style.cursor = 'none';
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) {
            /* Safari */
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) {
            /* IE11 */
            elem.msRequestFullscreen();
        }
    }
};