module.exports = RED => {
    const socket = require("../connection").socket;
    const ConnectionHelper = require("../connectionHelper");

	function LanguageRecognize(config) {}
    RED.nodes.registerType("LanguageRecognize", LanguageRecognize);
}