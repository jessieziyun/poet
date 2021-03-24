window.onload = () => {
    
    console.log("Hello world!")
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/arduino');

    var p = io.connect('http://' + document.domain + ':' + location.port + '/test');

    //receive details from server
    socket.on('arduinoread', data => {
        // console.log("Proximity value: " + data.number);
        document.getElementById("arduino").innerHTML = data.number;
    });

    socket.on('poem', data => {
        console.log(data);
    });

    socket.on('my response', data => {
        console.log(data);
    });

    document.getElementById("btn").onclick = () => {
        socket.emit("buttonclicked", "clicked");
    };
};