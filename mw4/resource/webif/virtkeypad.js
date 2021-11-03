// entering the host name
var parameters = location.search.substring(1).split("&");
var temp = parameters[0].split("=");
var host = unescape(temp[1]);

function pack_7bit_into8bit(e, t) {
    // console.log('input: ' + e)
    for (var o, a = [], n = 0, i = e.length, r = 0; r < i; ++r) {
        if (o = o << 7 | 127 & e[r], (n += 7) >= 8) {
            var u = o >> n - 8 & 255;
            n -= 8, a.push(u)
        }
    }
    if (t && n > 0) {
        u = o << 8 - n & 255;
        a.push(u)
    }
    // console.log('output: ' + a)
    return a
}
function unpack_8bit_into_7bit(e, t, o) {
    for (var a, n = [], i = 0, r = e.length, u = 0; u < r; ++u) {
        for (a = a << 8 | e[u], i += 8; i >= 7;) {
            var l = a >> i - 7 & 127;
            i -= 7, n.push(l | 128 * o)
        }
    }
    if (t && i > 0) {
        l = a << 7 - i & 127;
        n.push(l | 128 * o)
    }
    return n
}
function virtual_keypad() {
    var e = document.getElementById("virtkp_canvas").getContext("2d"),
        t = document.getElementById("virtkp_cursor"),
        o = [];
    function a() {
        t.style.display = "none"
    }
    function n(t, a, n) {
        // writes the text
        // adding 1px in x and y, because overlapping
        t >= 1 && t <= 16 && a >= 1 && a <= 5 && e.drawImage(o[n], 8 * (t - 1) + 1, 12 * (a - 1) + 1)
    }
    !function() {
        for (var e = 0; e < 256; ++e) {
            var t = new Image;

            // changing the location of the pictures
            t.src = "pic/vk" + e + ".png", o.push(t)
        }
    }();
    var i = {
            key_0: 82,
            key_1: 92,
            key_2: 94,
            key_3: 98,
            key_4: 32,
            key_5: 34,
            key_6: 38,
            key_7: 22,
            key_8: 24,
            key_9: 28,
            key_esc: 84,
            key_enter: 106,
            key_stop: 96,
            key_menu: 88,
            key_plus: 36,
            key_minus: 46,
            key_up: 11,
            key_left: 14,
            key_down: 12,
            key_right: 18
        },
        r = [],
        u = !1;
    function l(o) {
        var i = pack_7bit_into8bit(o, !1);
        //console.log(i)
        if (i.length > 0)
            switch (i[0]) {
            case 1:
                for (var r = i[1], u = i[2], l = i[3], s = 0; s < l; ++s) {
                    var c = i[4 + s];
                    0 !== c && n(r + s, u, c)
                }
                break;
            case 3:
                r = i[1], u = i[2];
                for (var f = e.createImageData(8, 12), d = 0, _ = 0; _ < 12; ++_)
                    for (var g = i[3 + _], p = 0; p < 8; ++p) {
                        var y = 0 != (g & 1 << p);

                        // changing the drawing color from red to blue
                        if (y)
                            f.data[d + 0] = 32, f.data[d + 1] = 144, f.data[d + 2] = 192, f.data[d + 3] = 255, d += 4
                        else
                            f.data[d + 0] = 0, f.data[d + 1] = 0, f.data[d + 2] = 0, f.data[d + 3] = 128, d += 4
                    }
                // one pixel in y
                e.putImageData(f, 8 * (r - 1) + 1 , 12 * (u - 1) + 1);
                break;
            case 2:
                for (r = i[1], u = i[2], f = e.createImageData(8, 8), d = 0, _ = 0; _ < 8; ++_)
                    for (p = 0; p < 8; ++p) {
                        y = 0 != (i[3 + p] & 128 >> _);

                        // changing the drawing color from red to blue
                        if (y)
                            f.data[d + 0] = 32 * y, f.data[d + 1] = 144*y, f.data[d + 2] = 192*y, f.data[d + 3] = 255, d += 4
                        else
                            f.data[d + 0] = 0, f.data[d + 1] = 0, f.data[d + 2] = 0, f.data[d + 3] = 0, d += 4
                    }
                // one pixel in y
                e.putImageData(f, 8 * (r - 1) + 1, 8 * (u - 1) + 1);
                break;
            case 5:
                !function(e, o) {
                    var a = 100 * (e - 1) / 16,
                        n = 1200 * (o - 1) / 64;
                    t.style.left = a + "%", t.style.top = n + "%", t.style.width = "6.25%", t.style.height = "18.75%", t.style.display = ""
                }(r = i[1], u = i[2]);
                break;
            case 6:
                a();
                break;
            }
    }
    function s(e) {
        e[0] >= 10 || 1 == e[0] || 0 == e[0] && l(e.slice(1))
    }
    Object.keys(i).forEach(function(e) {
        $("#" + e).on("touchstart mousedown", function(t) {
            t.preventDefault(), function(e) {
                var t = d(e);
                c.send(t)
            }(i[e])
        }), $("#" + e).on("touchend mouseup", function(t) {
            t.preventDefault(), function(e) {
                var t = _(e);
                c.send(t)
            }(i[e])
        })
    });
    var c = new Websock;
    function f(e) {
        for (var t = e.length, o = 0, a = 0; a < t; ++a)
            o ^= e[a];
        return o < 10 && (o += 10), o
    }
    function d(e) {
        return msg = [2, 6, e], msg.push(f(msg)), msg.push(3), msg
    }
    function _(e) {
        return msg = [2, 5, e], msg.push(f(msg)), msg.push(3), msg
    }
    function g() {
        var e = $(".global-main").width(),
            t = $(".global-main").height(),
            o = e,
            a = 2 * e;
        a > t && (a = t, o = t / 2), $("#virtkeypad").css("height", a + "px"), $("#virtkeypad").css("width", o + "px")
    }
    c.binaryType = "arraybuffer", c.on("message", function(e) {
        !function(e) {
            // console.log(e)
            for (var t = e.length, o = 0; o < t; o++)
                if (2 === e[o])
                    r = [], u = !0;
                else if (3 === e[o]) {
                    if (u = !1, r.length > 1) {
                        var a = r.slice(0, r.length - 1);
                        f([2].concat(a)) === r[r.length - 1] && s(a)
                    }
                } else
                    u && r.push(e[o])
        }(c.rQshiftBytes())
    }), c.on("open", function(e) {}), c.on("error", function(e) {
        console.log("Error")
    }), c.on("close", function(e) {
        for (var t = "                                Connecting...                                   ", o = t.length, i = 0; i < o; ++i) {
            n(1 + (15 & i), 1 + (i >> 4), t.codePointAt(i))
        }
        a(), setTimeout(function() {
            c.open("ws://" + "192.168.2.15" + ":8000/", "binary")
        }, 3e3)
    }), c.open("ws://" + "192.168.2.15" + ":8000/", "binary"), $(window).resize(function() {
        g()
    }), g()
}
$(document).ready(function() {
    virtual_keypad()
});

