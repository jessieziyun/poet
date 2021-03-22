window.onload=function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/arduino');

    //receive details from server
    socket.on('arduinoread', data => {
        console.log("Proximity value: " + data.number);
        document.getElementById("arduino").innerHTML = data.number;
    });

};