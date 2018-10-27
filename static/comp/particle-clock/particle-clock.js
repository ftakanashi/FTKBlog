/**
 * Created by weiyz18939 on 2018/10/26.
 */

// Utilities
function clamp(n, min, max) {
  return Math.min(max, Math.max(min, n));
}

function lerp(o, t, p) {
  return o + (t - o) * p;
}

function rad(deg) {
  return deg * Math.PI / 180;
}

function pos(x, y, r, deg) {
  return {
    x: (x - r * Math.sin(rad(deg))).toString(),
    y: (y - r * Math.cos(rad(deg))).toString()
  };
}

function stringPos(obj) {
  return obj.x + "," + obj.y;
}

// Easings
function oscillate(t) {
  return Math.sin(rad(180 * t));
}

var c = Snap("#clock"),
  i;

var poly = [];
for (i = 0; i < 12; i++) {
  var p = pos(256, 256, 256, i * 30);
  poly.push(p.x, p.y);
}
c.polygon(poly).addClass("f1");

var seconds = [];
for (i = 0; i < 60; i++) {
  var p = pos(256, 256, 192, i * -6);
  seconds.push({
    l: c.circle(p.x, p.y, i % 5 === 0 ? 8 : 4).addClass("f2"),
    r: 0
  });
}

var minutes = [];
for (i = 0; i < 10; i++) {
  var p = pos(256, 256, 16 * i, 0);
  minutes.push({ l: c.circle(p.x, p.y, i === 0 ? 4 : 4).addClass("f2"), r: 0 });
}

var hours = [];
for (i = 0; i < 5; i++) {
  var p = pos(256, 256, 24 * i, 0);
  hours.push({ l: c.circle(p.x, p.y, 8).addClass("f2"), r: 0 });
}

// Drawing
var delta,
  lastSecond,
  last = new Date();
function draw() {
  var now = new Date();
  delta = (now.getTime() - last.getTime()) / 1000;
  last = now;

  // Get Times
  var h = now.getHours();
  var m = now.getMinutes();
  var s = now.getSeconds();
  var ms = now.getMilliseconds();

  // Progress
  var prog = { ms: ms / 1000 },
    p,
    target;
  prog.s = (s + prog.ms) / 60;
  prog.m = (m + prog.s) / 60;
  prog.h = (h + prog.m) / 12;

  for (i = 0; i < seconds.length; i++) {
    var sec = seconds[i];
    var pp = clamp((prog.s - i * 1 / 60) / (1 / 60), 0, 1);

    if (pp === sec.r) {
      continue;
    }
    p = pos(
      256,
      256,
      192 + 32 * oscillate(pp) * (i % 2 === 0 ? -1 : 1),
      i * -6
    );
    sec.r = pp;

    sec.l.attr({ cx: p.x, cy: p.y });
  }

  var len = minutes.length;
  for (i = 0; i < len; i++) {
    var min = minutes[i];
    target = m + m * 60;
    if (target === 0 && min.r > 300) {
      min.r = -61;
    } // Wrapping
    min.r = lerp(min.r, target, delta * (5 + (len - i) / len * 5));

    p = pos(256, 256, 16 * i, min.r / 60 * -360);
    min.l.attr({ cx: p.x, cy: p.y });
  }

  len = hours.length;
  for (i = 0; i < len; i++) {
    var hou = hours[i];
    var hh = h * 5 + Math.round(m / 12);
    target = hh + hh * 60;
    if (target === 0 && hou.r > 300) {
      hou.r = -61;
    } // Wrapping
    hou.r = lerp(hou.r, target, delta * (5 + (len - i) / len * 5));

    p = pos(256, 256, 24 * i, hou.r / 60 * -360);
    hou.l.attr({ cx: p.x, cy: p.y });
  }

  window.requestAnimationFrame(draw);
}

draw();