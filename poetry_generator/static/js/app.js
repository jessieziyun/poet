let canvas1 = document.getElementById('canvas1'),
    ctx1 = canvas1.getContext('2d');
let canvas2 = document.getElementById('canvas2'),
    ctx2 = canvas2.getContext('2d');
let w = window.innerWidth,
    h = window.innerHeight;
canvas1.width = w;
canvas1.height = h;
canvas2.width = w;
canvas2.height = h;

let poemContainer = $("#text");

let deg = 1;

window.onload = () => {

    // test background with random colours
    fillGradient(canvas1, ctx1, colours[getRandomInt(0, 10)], colours[getRandomInt(0, 10)], colours[getRandomInt(0, 10)], colours[getRandomInt(0, 10)], colours[getRandomInt(0, 10)]);

    var socket = io();

    socket.on('arduinoread', data => {
        // console.log("arduino", data.number);
    });

    // ON RECEPTION OF NEW POEM
    socket.on('poem', data => {
        console.log(data.poem);
        animate("out");
        setTimeout(() => {
            newPoem(data.poem, deg);
        }, 8000);
    });

    handleFullScreen();
};

function handleFullScreen() {
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
}

// STYLE POEM

function newPoem(poem, degree) {
    let divs = [];
    let yPositions = [];
    splitPoem(poem, divs, yPositions);
    generatePoint(degree, divs, yPositions);
    animate("in");
}

function animate(type) {
    let divIndex, spanIndex, spans;
    console.log("animating " + type);
    let wordDivs = document.getElementsByClassName("word");
    if (wordDivs.length == 0) {
        console.log("no words yet");
        return;
    }

    divIndex = 0
    spanIndex = 0;
    spans = wordDivs[divIndex].childNodes;
    doOne();

    function doOne() {
        let span = $(spans[spanIndex]);
        if (type == "out") {
            span.removeClass("animate-in");
        } 
        if (type == "in") {
            span.removeClass("animate-out");
        }
        span.addClass("animate-" + type);
        next();
    }

    function next() {
        ++spanIndex;
        if (spanIndex < spans.length) {
            setTimeout(doOne, 25);
        } else if (divIndex < wordDivs.length - 1) { 
            ++divIndex;
            spanIndex = 0;
            spans = wordDivs[divIndex].childNodes;
            setTimeout(doOne, 25);
        }
    }
}

function splitPoem(target, poem_divs, y_positions) {
    poemContainer.empty();
    let words = target.split(/(?:\n| )+/);
    poemContainer.css({
        'font-size': 100 / words.length * 0.75 + "vh",
        'line-height': 100 / words.length + "vh"
    });

    for (let i = 0; i < words.length; i++) {
        let wordDiv = document.createElement('div');
        wordDiv.innerHTML = words[i].split("<br>").map(val => {
            return val.replace(/(\S)/g, "<span>$1</span>");
        }).join("<br>");
        wordDiv.classList.add("word");
        poemContainer.append(wordDiv);
        const divY = Math.floor(wordDiv.getBoundingClientRect().top);
        poem_divs.push(wordDiv);
        y_positions.push(divY);
    }
}

function generatePoint(degree, poem_divs, y_positions) {
    let posY = 0;
    let noiseX = w / 3,
        amp = 600, // amplitude
        wl = 150, // wavelength
        a = pseudoRand(),
        b = pseudoRand();
    while (posY < h) {
        if (posY % wl === 0) {
            a = b;
            b = pseudoRand();
            noiseX = w / 3 + a * amp;
        } else {
            noiseX = w / 3 + interpolate(a, b, (posY % wl) / wl) * amp;
        }
        let randX = (Math.random() - 0.5) * 2 * w;
        let posX = randX + (noiseX - randX) * degree;
        let index = y_positions.indexOf(posY);
        if (index !== -1) {
            poem_divs[index].style.marginLeft = posX + "px";
        }
        posY += 1;
    }
}

function pseudoRand() {
    const M = 4294967296,
        A = 1664525,
        C = 1;
    let Z = Math.floor(Math.random() * M);
    Z = (A * Z + C) % M;
    return Z / M - 0.5;
};

function interpolate(pa, pb, px) {
    var ft = px * Math.PI,
        f = (1 - Math.cos(ft)) * 0.5;
    return pa * (1 - f) + pb * f;
}

// COLOUR FIELD BACKGROUND

function getProjectionDistance(a, b, c) {
    const k2 = b.x * b.x - b.x * a.x + b.y * b.y - b.y * a.y;
    const k1 = a.x * a.x - b.x * a.x + a.y * a.y - b.y * a.y;
    const ab2 = (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y);
    const kcom = (c.x * (a.x - b.x) + c.y * (a.y - b.y));
    const d1 = (k1 - kcom) / ab2;
    const d2 = (k2 + kcom) / ab2;
    return {
        d1,
        d2
    };
}

function limit01(value) {
    if (value < 0) {
        return 0;
    }
    if (value > 1) {
        return 1;
    }
    return value;
}

function paddingleft0(v, v_length) {
    while (v.length < v_length) {
        v = '0' + v;
    }
    return v;
}

function getWeightedColorMix(points, ratios) {
    let r = 0;
    let g = 0;
    let b = 0;
    for ([ind, point] of points.entries()) {
        r += Math.round(parseInt(point.c.substring(1, 3), 16) * ratios[ind]);
        g += Math.round(parseInt(point.c.substring(3, 5), 16) * ratios[ind]);
        b += Math.round(parseInt(point.c.substring(5, 7), 16) * ratios[ind]);
    }

    let result = '#' + paddingleft0(r.toString(16), 2) + paddingleft0(g.toString(16), 2) + paddingleft0(b.toString(16), 2);

    return result;
}

function getGeometricColorMix(p, points) {
    let colorRatios = new Array(points.length);
    colorRatios.fill(1);
    for ([ind1, point1] of points.entries()) {
        for ([ind2, point2] of points.entries()) {
            if (ind1 != ind2) {
                d = getProjectionDistance(point1, point2, p);
                colorRatios[ind1] *= limit01(d.d2);
            }
        }
    }
    let totalRatiosSum = 0;
    colorRatios.forEach(c => totalRatiosSum += c);
    colorRatios.forEach((c, i) => colorRatios[i] /= totalRatiosSum);
    c = getWeightedColorMix(points, colorRatios);
    return c;
}

function fillGradient(canvas, ctx, col1, col2, col3, col4, col5) {
    let points = [{
            x: 0,
            y: 0,
            c: col1
        },
        {
            x: w * 0.25,
            y: h,
            c: col2
        },
        {
            x: w * 0.7,
            y: h,
            c: col3
        },
        {
            x: w * 0.6,
            y: h * 0.1,
            c: col4
        },
        {
            x: w,
            y: 0,
            c: col5
        },
    ];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.globalCompositeOperation = 'destination-over';
    let xcs = points.map(p => p.x);
    let ycs = points.map(p => p.y);
    let xmin = Math.min(...xcs);
    let xmax = Math.max(...xcs);
    let ymin = Math.min(...ycs);
    let ymax = Math.max(...ycs);
    let x, y;
    let mixColor;

    for (x = xmin; x < xmax; x++) {
        for (y = ymin; y < ymax; y++) {
            mixColor = getGeometricColorMix({
                x: x,
                y: y
            }, points);
            ctx.fillStyle = mixColor;
            ctx.fillRect(x, y, 1, 1);
        }
    }
}

const colours = ["#000000", "#5c8e5e", "#b8e2c3", "#fff930", "#ffffff", "#fff930", "#ff9077", "#779077", "#d06b44", "#dd95c3", "#4d6249"]

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}