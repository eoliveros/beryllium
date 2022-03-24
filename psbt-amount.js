const decodePsbt = require('psbt');
const txHexDecoder = require("raw-transaction-hex-decoder");
const dpsbt = decodePsbt;

module.exports = {
	getUnsignedPSBTAmount : function(psbtString) {
		var returnVal = "";
		try {
			const buffer = Buffer.from(psbtString, 'base64');
			const bufString = buffer.toString('hex');
			const rawTx = dpsbt.decodePsbt({psbt: bufString})["unsigned_transaction"];
			const btcDecodedRawTx = txHexDecoder.decodeRawUTXO(rawTx);
			var txOutputs = btcDecodedRawTx["outs"];
			// remove change address amount from outputs
			var changeOutput = txOutputs.pop();
			var totalSent = 0;
			for(var i=0; i < txOutputs.length; i++) {
				totalSent+=txOutputs[i]["value"];
			};
			returnVal = `${totalSent/100000000}`;
		} catch {
			returnVal = "Please enter a valid psbt value";
		}
		return returnVal;
	},
};

