function Websock() {
    "use strict";
    this._websocket = null, this._rQi = 0, this._rQlen = 0, this._rQbufferSize = 4194304, this._rQmax = this._rQbufferSize / 8, this._rQ = null, this._sQbufferSize = 10240, this._sQlen = 0, this._sQ = null, this._eventHandlers = {
        message: function() {},
        open: function() {},
        close: function() {},
        error: function() {}
    }
}
!function() {
    "use strict";
    var t = function() {
        try {
            var t = new Uint8Array([1, 2, 3]);
            return String.fromCharCode.apply(null, t), function(t) {
                return String.fromCharCode.apply(null, t)
            }
        } catch (t) {
            return function(t) {
                return String.fromCharCode.apply(null, Array.prototype.slice.call(t))
            }
        }
    }();
    Websock.prototype = {
        get_sQ: function() {
            return this._sQ
        },
        get_rQ: function() {
            return this._rQ
        },
        get_rQi: function() {
            return this._rQi
        },
        set_rQi: function(t) {
            this._rQi = t
        },
        rQlen: function() {
            return this._rQlen - this._rQi
        },
        rQpeek8: function() {
            return this._rQ[this._rQi]
        },
        rQshift8: function() {
            return this._rQ[this._rQi++]
        },
        rQskip8: function() {
            this._rQi++
        },
        rQskipBytes: function(t) {
            this._rQi += t
        },
        rQshift16: function() {
            return (this._rQ[this._rQi++] << 8) + this._rQ[this._rQi++]
        },
        rQshift32: function() {
            return (this._rQ[this._rQi++] << 24) + (this._rQ[this._rQi++] << 16) + (this._rQ[this._rQi++] << 8) + this._rQ[this._rQi++]
        },
        rQshiftStr: function(e) {
            void 0 === e && (e = this.rQlen());
            var i = new Uint8Array(this._rQ.buffer, this._rQi, e);
            return this._rQi += e, t(i)
        },
        rQshiftBytes: function(t) {
            return void 0 === t && (t = this.rQlen()), this._rQi += t, new Uint8Array(this._rQ.buffer, this._rQi - t, t)
        },
        rQshiftTo: function(t, e) {
            void 0 === e && (e = this.rQlen()), t.set(new Uint8Array(this._rQ.buffer, this._rQi, e)), this._rQi += e
        },
        rQwhole: function() {
            return new Uint8Array(this._rQ.buffer, 0, this._rQlen)
        },
        rQslice: function(t, e) {
            return e ? new Uint8Array(this._rQ.buffer, this._rQi + t, e - t) : new Uint8Array(this._rQ.buffer, this._rQi + t, this._rQlen - this._rQi - t)
        },
        rQwait: function(t, e, i) {
            if (this._rQlen - this._rQi < e) {
                if (i) {
                    if (this._rQi < i)
                        throw new Error("rQwait cannot backup " + i + " bytes");
                    this._rQi -= i
                }
                return !0
            }
            return !1
        },
        flush: function() {
            0 !== this._websocket.bufferedAmount && Util.Debug("bufferedAmount: " + this._websocket.bufferedAmount), this._sQlen > 0 && this._websocket.readyState === WebSocket.OPEN && (this._websocket.send(this._encode_message()), this._sQlen = 0)
        },
        send: function(t) {
            this._sQ.set(t, this._sQlen), this._sQlen += t.length, this.flush()
        },
        send_string: function(t) {
            this.send(t.split("").map(function(t) {
                return t.charCodeAt(0)
            }))
        },
        off: function(t) {
            this._eventHandlers[t] = function() {}
        },
        on: function(t, e) {
            this._eventHandlers[t] = e
        },
        _allocate_buffers: function() {
            this._rQ = new Uint8Array(this._rQbufferSize), this._sQ = new Uint8Array(this._sQbufferSize)
        },
        init: function() {
            this._allocate_buffers(), this._rQi = 0, this._websocket = null
        },
        open: function(t, e) {
            t.match(/^([a-z]+):\/\//)[1];
            this.init(), this._websocket = e ? new WebSocket(t, e) : new WebSocket(t), this._websocket.binaryType = "arraybuffer", this._websocket.onmessage = this._recv_message.bind(this), this._websocket.onopen = function() {
                Util.Debug(">> WebSock.onopen"), this._websocket.protocol && Util.Info("Server choose sub-protocol: " + this._websocket.protocol), this._eventHandlers.open(), Util.Debug("<< WebSock.onopen")
            }.bind(this), this._websocket.onclose = function(t) {
                Util.Debug(">> WebSock.onclose"), this._eventHandlers.close(t), Util.Debug("<< WebSock.onclose")
            }.bind(this), this._websocket.onerror = function(t) {
                Util.Debug(">> WebSock.onerror: " + t), this._eventHandlers.error(t), Util.Debug("<< WebSock.onerror: " + t)
            }.bind(this)
        },
        close: function() {
            this._websocket && (this._websocket.readyState !== WebSocket.OPEN && this._websocket.readyState !== WebSocket.CONNECTING || (Util.Info("Closing WebSocket connection"), this._websocket.close()), this._websocket.onmessage = function(t) {})
        },
        _encode_message: function() {
            return new Uint8Array(this._sQ.buffer, 0, this._sQlen)
        },
        _expand_compact_rQ: function(t) {
            var e = t || this._rQlen - this._rQi > this._rQbufferSize / 2;
            if (e && (t ? this._rQbufferSize = 8 * (this._rQlen - this._rQi + t) : this._rQbufferSize *= 2), this._rQbufferSize > 41943040 && (this._rQbufferSize = 41943040, this._rQbufferSize - this._rQlen - this._rQi < t))
                throw new Exception("Receive Queue buffer exceeded 41943040 bytes, and the new message could not fit");
            if (e) {
                var i = this._rQ.buffer;
                this._rQmax = this._rQbufferSize / 8, this._rQ = new Uint8Array(this._rQbufferSize), this._rQ.set(new Uint8Array(i, this._rQi))
            } else
                this._rQ.set(new Uint8Array(this._rQ.buffer, this._rQi));
            this._rQlen = this._rQlen - this._rQi, this._rQi = 0
        },
        _decode_message: function(t) {
            var e = new Uint8Array(t);
            e.length > this._rQbufferSize - this._rQlen && this._expand_compact_rQ(e.length), this._rQ.set(e, this._rQlen), this._rQlen += e.length
        },
        _recv_message: function(t) {
            try {
                this._decode_message(t.data), this.rQlen() > 0 ? (this._eventHandlers.message(), this._rQlen == this._rQi ? (this._rQlen = 0, this._rQi = 0) : this._rQlen > this._rQmax && this._expand_compact_rQ()) : Util.Debug("Ignoring empty message")
            } catch (t) {
                var e = "";
                t.name && (e += "\n    name: " + t.name + "\n", e += "    message: " + t.message + "\n"), void 0 !== t.description && (e += "    description: " + t.description + "\n"), void 0 !== t.stack && (e += t.stack), e.length > 0 ? Util.Error("recv_message, caught exception: " + e) : Util.Error("recv_message, caught exception: " + t), void 0 !== t.name ? this._eventHandlers.error(t.name + ": " + t.message) : this._eventHandlers.error(t)
            }
        }
    }
}();

