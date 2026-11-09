/* SuperIntelNex — punktewolke als seitenweites Hintergrund-Bild (WebGL)

   Ein fixer Layer hinter der gesamten Seite. Die Wolke aus feinen
   Lichtpunkten morpht automatisch zwischen drei Szenen (Kugel,
   Galaxie, Lorenz-Attraktor — parametrisch erzeugt, keine externen
   Assets) und reagiert ueberall auf die Maus: sanftes Kippen in
   Mausrichtung + punktuelle Abstoessung (Gauss). Verhalten nach
   yunbay.xyz:
     - Auto-Advance: 2.6 s Morph, dann 4.4 s Pause
     - Rotation mit Traegheit (Lerp 0.12), Auto-Drehung + Maus-Kippen
     - Mausfeld = punktuelle Abstoessung, ueber die ganze Seite
     - prefers-reduced-motion: statisches Bild, keine Schleife
     - ohne WebGL: Layer bleibt leer, die dunkle Seite ist ohne
       die Wolke weiterhin lesbar
*/
(function () {
  "use strict";

  var host = document.querySelector("[data-page-cloud]");
  var canvas = host ? host.querySelector(".page-cloud__canvas") : null;
  if (!host || !canvas) {
    return;
  }

  var gl = canvas.getContext("webgl", { antialias: true, alpha: false });
  if (!gl) {
    return; // Layer zeigt nur den schwarzen Grund
  }
  host.classList.add("is-active");

  var reduced = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isSmall = window.matchMedia &&
    window.matchMedia("(max-width: 640px)").matches;
  var N = isSmall ? 2200 : 3600;

  /* ------------------------------------------------------------ Formen */

  function Kugel() {
    var a = new Float32Array(N * 3);
    var ga = Math.PI * (3 - Math.sqrt(5)); // Golden Angle
    for (var i = 0; i < N; i++) {
      var y = 1 - 2 * (i + 0.5) / N;
      var r = Math.sqrt(Math.max(0, 1 - y * y));
      var th = ga * i;
      var rad = 1.0 * (0.9 + 0.2 * Math.random());
      a[i * 3] = Math.cos(th) * r * rad;
      a[i * 3 + 1] = y * rad;
      a[i * 3 + 2] = Math.sin(th) * r * rad;
    }
    return a;
  }

  function gauss() {
    return (Math.random() + Math.random() + Math.random() - 1.5) * 1.6;
  }

  function Galaxie() {
    var a = new Float32Array(N * 3);
    var arms = 2;
    var twist = 3.6;
    var coreCount = Math.floor(N * 0.18);
    for (var i = 0; i < N; i++) {
      if (i < coreCount) {
        // Kugelhaufen im Kern
        a[i * 3] = gauss() * 0.14;
        a[i * 3 + 1] = gauss() * 0.09;
        a[i * 3 + 2] = gauss() * 0.14;
      } else {
        var r = Math.pow(Math.random(), 0.65) * 1.15;
        var arm = i % arms;
        var ang = arm * Math.PI + r * twist + (Math.random() - 0.5) * 0.35;
        a[i * 3] = Math.cos(ang) * r;
        a[i * 3 + 1] = gauss() * 0.045 * (2 - r);
        a[i * 3 + 2] = Math.sin(ang) * r;
      }
    }
    return a;
  }

  function Lorenz() {
    var sigma = 10, rho = 28, beta = 8 / 3, dt = 0.0045;
    var x = 0.1, y = 0.1, z = 0;
    function step() {
      var dx = sigma * (y - x) * dt;
      var dy = (x * (rho - z) - y) * dt;
      var dz = (x * y - beta * z) * dt;
      x += dx; y += dy; z += dz;
    }
    var warm = 800;
    var i;
    for (i = 0; i < warm; i++) { step(); }
    var raw = [];
    var sub = 3; // jede dritte Integration sampeln
    for (i = 0; i < N; i++) {
      for (var k = 0; k < sub; k++) { step(); }
      raw.push([x, y, z]);
    }
    // Zentrieren und auf Passformat skalieren.
    var cx = 0, cy = 0, cz = 0;
    for (i = 0; i < N; i++) {
      cx += raw[i][0]; cy += raw[i][1]; cz += raw[i][2];
    }
    cx /= N; cy /= N; cz /= N;
    var maxLen = 0;
    var a = new Float32Array(N * 3);
    for (i = 0; i < N; i++) {
      var px = raw[i][0] - cx;
      var py = (raw[i][1] - cy) * 0.7; // Flach gedrueckt: Schmetterling von vorn
      var pz = raw[i][2] - cz;
      var len = Math.sqrt(px * px + py * py + pz * pz);
      if (len > maxLen) { maxLen = len; }
      a[i * 3] = px;
      a[i * 3 + 1] = py;
      a[i * 3 + 2] = pz;
    }
    var s = 1.15 / (maxLen || 1);
    for (i = 0; i < N * 3; i++) { a[i] *= s; }
    return a;
  }

  var shapes = [Kugel(), Galaxie(), Lorenz()];

  /* ---------------------------------------------------------- Shader */

  var VERT = [
    "precision mediump float;",
    "attribute vec3 aFrom;",
    "attribute vec3 aTo;",
    "attribute float aSeed;",
    "uniform float uMorph;",
    "uniform float uTime;",
    "uniform float uAspect;",
    "uniform float uPixelRatio;",
    "uniform float uPointSize;",
    "uniform float uRotationX;",
    "uniform float uRotationY;",
    "uniform vec2 uMouse;",
    "uniform float uMouseStrength;",
    "varying float vAlpha;",
    "mat3 rotY(float a){float c=cos(a);float s=sin(a);",
    "  return mat3(vec3(c,0.0,-s),vec3(0.0,1.0,0.0),vec3(s,0.0,c));}",
    "mat3 rotX(float a){float c=cos(a);float s=sin(a);",
    "  return mat3(vec3(1.0,0.0,0.0),vec3(0.0,c,s),vec3(0.0,-s,c));}",
    "void main(){",
    "  float m = smoothstep(0.0, 1.0, uMorph);",
    "  vec3 p = mix(aFrom, aTo, m);",
    "  p += 0.02 * vec3(",
    "    sin(uTime*0.5 + aSeed*11.0),",
    "    cos(uTime*0.4 + aSeed*7.0),",
    "    sin(uTime*0.6 + aSeed*5.0));",
    "  p = rotY(uRotationY) * (rotX(uRotationX) * p);",
    "  float depth = 3.0 - p.z;",
    "  vec2 pos = vec2(p.x * uAspect, p.y) * 0.85 / depth;",
    "  vec2 d = pos - uMouse;",
    "  float rep = uMouseStrength * exp(-dot(d, d) * 5.5);",
    "  pos += normalize(d + vec2(0.0001)) * rep;",
    "  gl_Position = vec4(pos, 0.0, 1.0);",
    "  float closeness = clamp((4.4 - depth) / 2.4, 0.0, 1.0);",
    "  vAlpha = mix(0.08, 0.85, closeness) * (0.72 + 0.5 * aSeed);",
    "  gl_PointSize = uPointSize * uPixelRatio *",
    "    mix(0.55, 1.35, closeness) * (0.7 + 0.6 * aSeed);",
    "}"
  ].join("\n");

  var FRAG = [
    "precision mediump float;",
    "varying float vAlpha;",
    "void main(){",
    "  vec2 c = gl_PointCoord - 0.5;",
    "  float d = length(c);",
    "  if (d > 0.5) { discard; }",
    "  float a = smoothstep(0.5, 0.12, d) * vAlpha;",
    "  gl_FragColor = vec4(1.0, 1.0, 1.0, a);",
    "}"
  ].join("\n");

  function compile(type, src) {
    var sh = gl.createShader(type);
    gl.shaderSource(sh, src);
    gl.compileShader(sh);
    if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
      throw new Error(gl.getShaderInfoLog(sh) || "Shaderfehler");
    }
    return sh;
  }

  var prog;
  try {
    prog = gl.createProgram();
    gl.attachShader(prog, compile(gl.VERTEX_SHADER, VERT));
    gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FRAG));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
      throw new Error(gl.getProgramInfoLog(prog) || "Linkfehler");
    }
  } catch (err) {
    // Stille Abmeldung: Layer bleibt schwarz, kein Konsolenfehler.
    host.classList.remove("is-active");
    return;
  }
  gl.useProgram(prog);

  /* ------------------------------------------------------------- Daten */

  var u = {};
  ["uMorph", "uTime", "uAspect", "uPixelRatio", "uPointSize", "uRotationX",
   "uRotationY", "uMouse", "uMouseStrength"].forEach(function (name) {
    u[name] = gl.getUniformLocation(prog, name);
  });

  var seed = new Float32Array(N);
  for (var i = 0; i < N; i++) {
    seed[i] = Math.random();
  }

  var bufA = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, bufA);
  gl.bufferData(gl.ARRAY_BUFFER, shapes[0], gl.DYNAMIC_DRAW);
  var bufB = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, bufB);
  gl.bufferData(gl.ARRAY_BUFFER, shapes[0], gl.DYNAMIC_DRAW);
  var bufS = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, bufS);
  gl.bufferData(gl.ARRAY_BUFFER, seed, gl.STATIC_DRAW);

  function bindAttr(buf, name, size) {
    var loc = gl.getAttribLocation(prog, name);
    if (loc < 0) {
      return;
    }
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0);
  }
  bindAttr(bufA, "aFrom", 3);
  bindAttr(bufB, "aTo", 3);
  bindAttr(bufS, "aSeed", 1);

  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE); // additiv: Lichtpunkte
  gl.clearColor(0.01, 0.01, 0.012, 1);
  gl.enable(gl.DEPTH_TEST);
  gl.depthMask(false); // kein Tiefen-Buffer bei additivem Blending

  /* -------------------------------------------------------- Zustand */

  var MORPH = 2.6;  // Sekunden
  var HOLD = 4.4;
  var from = 0, to = 0, phase = "hold", phaseT = 0, time = 0;
  // Sanfte Auto-Drehung: Y wandert dauerhaft, X pendelt leicht.
  var rx = 0.12, ry = -0.35, targetRX = 0.12, targetRY = -0.35;
  var mouseX = 0, mouseY = 0, mouseStr = 0, mouseStrTarget = 0;
  var uAspect = 1, uPixelRatio = 1;

  function advance() {
    from = to;
    to = (to + 1) % shapes.length;
    phase = "morph";
    phaseT = 0;
    gl.bindBuffer(gl.ARRAY_BUFFER, bufA);
    gl.bufferSubData(gl.ARRAY_BUFFER, 0, shapes[from]);
    gl.bindBuffer(gl.ARRAY_BUFFER, bufB);
    gl.bufferSubData(gl.ARRAY_BUFFER, 0, shapes[to]);
  }

  function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  function render() {
    gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
    gl.clear(gl.COLOR_BUFFER_BIT);
    var morph = reduced ? 1 :
      (phase === "morph" ? easeInOutCubic(Math.min(1, phaseT / MORPH)) : 1);
    gl.uniform1f(u.uMorph, morph);
    gl.uniform1f(u.uTime, time);
    gl.uniform1f(u.uAspect, uAspect);
    gl.uniform1f(u.uPixelRatio, uPixelRatio);
    gl.uniform1f(u.uPointSize, 3.2);
    gl.uniform1f(u.uRotationX, rx);
    gl.uniform1f(u.uRotationY, ry);
    gl.uniform2f(u.uMouse, mouseX, mouseY);
    gl.uniform1f(u.uMouseStrength, mouseStr);
    gl.drawArrays(gl.POINTS, 0, N);
  }

  function resize() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    // Layer ist seitenweit fix: Canvas maesst immer das Viewport.
    var w = Math.max(1, Math.round(window.innerWidth * dpr));
    var h = Math.max(1, Math.round(window.innerHeight * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
    uPixelRatio = dpr;
    uAspect = h / w;
    if (reduced) {
      render();
    }
  }
  resize();
  window.addEventListener("resize", resize, { passive: true });

  /* --------------------------------------------- Interaktion (ganze Seite) */

  // Maus-Position ins Canvas-Koordinatensystem (NDC, y nach oben),
  // egal wo auf der Seite die Maus ist.
  function toNDC(clientX, clientY) {
    var nx = (clientX / window.innerWidth) * 2 - 1;
    var ny = 1 - (clientY / window.innerHeight) * 2;
    return [nx, ny];
  }

  document.addEventListener("mousemove", function (e) {
    var p = toNDC(e.clientX, e.clientY);
    mouseX = p[0];
    mouseY = p[1];
    // Sanftes Kippen in Mausrichtung, mit Begrenzung (yunbay-Style).
    targetRY = -0.35 + p[0] * 0.5;
    targetRX = 0.12 - p[1] * 0.5;
    if (targetRX > 0.65) { targetRX = 0.65; }
    if (targetRX < -0.65) { targetRX = -0.65; }
    if (targetRY > 0.65) { targetRY = 0.65; }
    if (targetRY < -0.65) { targetRY = -0.65; }
    mouseStrTarget = reduced ? 0 : 0.32;
  }, { passive: true });

  document.addEventListener("mouseleave", function () {
    mouseStrTarget = 0;
    targetRX = 0.12;
    targetRY = -0.35;
    if (!reduced) {
      mouseX = 0;
      mouseY = 0;
    }
  });

  // Touch: gleiche Reaktivitaet mit dem Finger, ohne zu blockieren.
  document.addEventListener("touchmove", function (e) {
    if (!e.touches || !e.touches[0]) {
      return;
    }
    var p = toNDC(e.touches[0].clientX, e.touches[0].clientY);
    mouseX = p[0];
    mouseY = p[1];
    targetRY = -0.35 + p[0] * 0.5;
    targetRX = 0.12 - p[1] * 0.5;
    if (targetRX > 0.65) { targetRX = 0.65; }
    if (targetRX < -0.65) { targetRX = -0.65; }
    if (targetRY > 0.65) { targetRY = 0.65; }
    if (targetRY < -0.65) { targetRY = -0.65; }
    mouseStrTarget = reduced ? 0 : 0.32;
  }, { passive: true });

  /* --------------------------------------------------- Schleife */

  if (reduced) {
    // Statisches Bild: eine Szene, ohne Auto-Advance, ohne Loop.
    render();
    return;
  }

  var last = performance.now();
  var tick = function (now) {
    var dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    time += dt;

    // Auto-Advance
    phaseT += dt;
    if (phase === "morph" && phaseT >= MORPH) {
      phase = "hold";
      phaseT = 0;
    } else if (phase === "hold" && phaseT >= HOLD) {
      advance();
    }

    // Auto-Drehung: y wandert kontinuierlich, x pendelt sanft.
    targetRY += dt * 0.10;
    targetRX = 0.12 + Math.sin(time * 0.22) * 0.16;
    // Rotation mit Traegheit (Lerp 0.12, yunbay-Style)
    ry += (targetRY - ry) * 0.12;
    rx += (targetRX - rx) * 0.12;

    // Mausfeld sanft an- und abklingen
    mouseStr += (mouseStrTarget - mouseStr) * 0.08;

    render();
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
})();
