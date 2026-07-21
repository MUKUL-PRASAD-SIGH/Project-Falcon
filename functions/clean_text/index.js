const catalyst = require('zcatalyst-sdk-node');

module.exports = (context, basicIO) => {
    const app = catalyst.initialize(context);
    const reqBody = basicIO.getArgument('reqBody') || {};
    
    let text = reqBody.BriefFacts || "";
    
    // Check for non UTF-8 or malformed characters
    try {
        text = decodeURIComponent(escape(text));
        basicIO.write(JSON.stringify({
            status: "success",
            cleanedText: text,
            message: "Text is valid UTF-8."
        }));
    } catch (e) {
        basicIO.write(JSON.stringify({
            status: "error",
            message: "Invalid text encoding. Expected UTF-8."
        }));
    }
    
    context.close();
};
