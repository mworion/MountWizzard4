"use strict";
var Util = {};
Array.prototype.push8 = function(t) {
    this.push(255 & t)
}, Array.prototype.push16 = function(t) {
    this.push(t >> 8 & 255, 255 & t)
}, Array.prototype.push32 = function(t) {
    this.push(t >> 24 & 255, t >> 16 & 255, t >> 8 & 255, 255 & t)
}, Array.prototype.map || (Array.prototype.map = function(t) {
    var e = this.length;
    if ("function" != typeof t)
        throw new TypeError;
    for (var n = new Array(e), o = arguments[1], i = 0; i < e; i++)
        i in this && (n[i] = t.call(o, this[i], i, this));
    return n
}), window.requestAnimFrame = window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame || function(t) {
    window.setTimeout(t, 1e3 / 60)
}, Util._log_level = "warn", Util.init_logging = function(t) {
    switch (void 0 === t ? t = Util._log_level : Util._log_level = t, void 0 === window.console && (void 0 !== window.opera ? window.console = {
        log: window.opera.postError,
        warn: window.opera.postError,
        error: window.opera.postError
    } : window.console = {
        log: function(t) {},
        warn: function(t) {},
        error: function(t) {}
    }), Util.Debug = Util.Info = Util.Warn = Util.Error = function(t) {}, t) {
    case "debug":
        Util.Debug = function(t) {
            console.log(t)
        };
    case "info":
        Util.Info = function(t) {
            console.log(t)
        };
    case "warn":
        Util.Warn = function(t) {
            console.warn(t)
        };
    case "error":
        Util.Error = function(t) {
            console.error(t)
        };
    case "none":
        break;
    default:
        throw "invalid logging type '" + t + "'"
    }
}, Util.get_logging = function() {
    return Util._log_level
}, Util.init_logging(), Util.conf_default = function(t, e, n, o, i, r, a, l) {
    var c,
        s;
    c = function(e) {
        return r in {
            arr: 1,
            array: 1
        } && void 0 !== e ? t[o][e] : t[o]
    }, s = function(e, n) {
        r in {
            boolean: 1,
            bool: 1
        } ? e = !(!e || e in {
            0: 1,
            no: 1,
            false: 1
        }) : r in {
            integer: 1,
            int: 1
        } ? e = parseInt(e, 10) : "str" === r ? e = String(e) : "func" === r && (e || (e = function() {})), void 0 !== n ? t[o][n] = e : t[o] = e
    }, e[o + "_description"] = l, void 0 === e["get_" + o] && (e["get_" + o] = c), void 0 === e["set_" + o] && (e["set_" + o] = function(e, n) {
        if (i in {
            RO: 1,
            ro: 1
        })
            throw o + " is read-only";
        if (i in {
            WO: 1,
            wo: 1
        } && void 0 !== t[o])
            throw o + " can only be set once";
        s(e, n)
    }), void 0 !== n[o] ? a = n[o] : r in {
        arr: 1,
        array: 1
    } && !(a instanceof Array) && (a = []), s(a)
}, Util.conf_defaults = function(t, e, n, o) {
    var i;
    for (i = 0; i < o.length; i++)
        Util.conf_default(t, e, n, o[i][0], o[i][1], o[i][2], o[i][3], o[i][4])
}, Util.get_include_uri = function() {
    return "undefined" != typeof INCLUDE_URI ? INCLUDE_URI : "include/"
}, Util._loading_scripts = [], Util._pending_scripts = [], Util.load_scripts = function(t) {
    for (var e, n = document.getElementsByTagName("head")[0], o = Util._loading_scripts, i = Util._pending_scripts, r = 0; r < t.length; r++)
        (e = document.createElement("script")).type = "text/javascript", e.src = Util.get_include_uri() + t[r], e.onload = e.onreadystatechange = function(t) {
            for (; o.length > 0 && ("loaded" === o[0].readyState || "complete" === o[0].readyState);) {
                var e = o.shift();
                n.appendChild(e)
            }
            (!this.readyState || Util.Engine.presto && "loaded" === this.readyState || "complete" === this.readyState) && i.indexOf(this) >= 0 && (this.onload = this.onreadystatechange = null, i.splice(i.indexOf(this), 1), 0 === i.length && window.onscriptsload && window.onscriptsload())
        }, Util.Engine.trident ? o.push(e) : (e.async = !1, n.appendChild(e)), i.push(e)
}, Util.getPosition = function(t) {
    var e = 0,
        n = 0;
    if (t.offsetParent)
        do {
            e += t.offsetLeft, n += t.offsetTop, t = t.offsetParent
        } while (t);
    return {
        x: e,
        y: n
    }
}, Util.getEventPosition = function(t, e, n) {
    var o,
        i,
        r,
        a;
    return (o = (o = t || window.event).changedTouches ? o.changedTouches[0] : o.touches ? o.touches[0] : o).pageX || o.pageY ? (i = o.pageX, r = o.pageY) : (o.clientX || o.clientY) && (i = o.clientX + document.body.scrollLeft + document.documentElement.scrollLeft, r = o.clientY + document.body.scrollTop + document.documentElement.scrollTop), a = Util.getPosition(e), void 0 === n && (n = 1), {
        x: (i - a.x) / n,
        y: (r - a.y) / n
    }
}, Util.addEvent = function(t, e, n) {
    if (t.attachEvent)
        return t.attachEvent("on" + e, n);
    if (t.addEventListener)
        return t.addEventListener(e, n, !1), !0;
    throw "Handler could not be attached"
}, Util.removeEvent = function(t, e, n) {
    if (t.detachEvent)
        return t.detachEvent("on" + e, n);
    if (t.removeEventListener)
        return t.removeEventListener(e, n, !1), !0;
    throw "Handler could not be removed"
}, Util.stopEvent = function(t) {
    t.stopPropagation ? t.stopPropagation() : t.cancelBubble = !0, t.preventDefault ? t.preventDefault() : t.returnValue = !1
}, Util.Features = {
    xpath: !!document.evaluate,
    air: !!window.runtime,
    query: !!document.querySelector
}, Util.Engine = {
    presto: !!window.opera,
    trident: !!window.ActiveXObject && (window.XMLHttpRequest ? document.querySelectorAll ? 6 : 5 : 4),
    webkit: function() {
        try {
            return !navigator.taintEnabled && (Util.Features.xpath ? Util.Features.query ? 525 : 420 : 419)
        } catch (t) {
            return !1
        }
    }(),
    gecko: !(!document.getBoxObjectFor && null == window.mozInnerScreenX) && (document.getElementsByClassName ? 19 : 18)
}, Util.Engine.webkit && (Util.Engine.webkit = function(t) {
    var e = new RegExp("WebKit/([0-9.]*) ");
    return t = (navigator.userAgent.match(e) || ["", t])[1], parseFloat(t, 10)
}(Util.Engine.webkit));

