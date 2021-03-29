window.onload = () => {
    
    var socket = io();

    socket.on('arduinoread', data => {
        document.getElementById("arduino").innerHTML = data.number;
    });

    socket.on('poem', data => {
        console.log(data);
        document.getElementById("poem").innerHTML = data.poem;
    });

    socket.on('clickconfirmation', data => {
        console.log(data);
    });

    document.getElementById("btn").onclick = () => {
        socket.emit("buttonclicked", "clicked");
    };
};