module.exports = RED => {
    const socket = require("../connection").socket;
    const ConnectionHelper = require("../connectionHelper");
    const EventPubSub = require('node-red-contrib-base/eventPubSub');

    const events = new EventPubSub();

    let lastReset = 0;
    let timeoutId = null;

    function resetNodeState(ch, node) {
        if (lastReset + 100 > Date.now()) {
            return;
        }

        clearTimeout(timeoutId);
        timeoutId = null;
        node.waitingNode = null;

        lastReset = Date.now();
        ch.emit(null, "/robot/waving/stop");
    }

    function timeoutHandler(ch, node) {
        if (node.waitingNode !== null) {
            const output = [null, { payload: RED._(node.type + ".timeoutOutput") }];

            node.status({});
            node.send(output);
            node.waitingNode = null;

            resetNodeState(ch, node);
        }
        timeoutId = null;
    }

    function WaveDetection(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        node.path = "/robot/waving/start";
        node.waitingNode = null;

        const ch = new ConnectionHelper(socket, node);

        node.on("input", msg => {
            node.waitingNode = msg;
            node.status({ fill: "blue", shape: "dot", text: node.type + ".waiting" });

            // wait some time to prevent a race condition with _set_awareness
            setTimeout(() => {
                if (config.timeout !== null && config.timeout > 0 && timeoutId === null) { // timeout === null prevents multiple/non-cancellable timeouts
                    node.timeoutDuration = config.timeout * 1000;
                    timeoutId = setTimeout(timeoutHandler, node.timeoutDuration, ch, node)[Symbol.toPrimitive](); // we don't want to use the node.js setTimeout version (returns object), we only want the ID;
                }
                ch.emit();
            }, 250);
        });

        ch.socket.on("/event/waving/detected", () => {
            if (!node.waitingNode) {
                return;
            }

            clearTimeout(timeoutId);
            timeoutId = null;

            node.send(node.waitingNode);
            node.waitingNode = null;

            node.status({});
        });

        node.on("close", (removed, done) => {
            resetNodeState(ch, node);
            done();
        });

        events.subscribe(EventPubSub.RESET_NODE_STATE, () => {
            resetNodeState(ch, node);
            node.status({});
        });
    }
    RED.nodes.registerType("Wave Detection", WaveDetection);
}