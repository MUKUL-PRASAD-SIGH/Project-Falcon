const catalyst = require('zcatalyst-sdk-node');

module.exports = async (context, basicIO) => {
    const app = catalyst.initialize(context);
    const reqBody = basicIO.getArgument('reqBody') || {};
    
    const caseMasterId = reqBody.CaseMasterID;
    
    if (!caseMasterId) {
        basicIO.write(JSON.stringify({
            status: "error",
            message: "Missing CaseMasterID."
        }));
        context.close();
        return;
    }
    
    try {
        const datastore = app.datastore();
        const table = datastore.table('CaseMaster');
        const row = await table.getRow(caseMasterId);
        
        if (row) {
            basicIO.write(JSON.stringify({
                status: "success",
                message: "Valid foreign key."
            }));
        } else {
            basicIO.write(JSON.stringify({
                status: "error",
                message: "Invalid foreign key: CaseMasterID not found."
            }));
        }
    } catch (err) {
        basicIO.write(JSON.stringify({
            status: "error",
            message: "Error querying DataStore.",
            error: err.toString()
        }));
    }
    
    context.close();
};
