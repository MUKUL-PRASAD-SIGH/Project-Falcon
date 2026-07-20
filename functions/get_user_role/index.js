const express = require('express');
const app = express();
const catalyst = require('zcatalyst-sdk-node');

app.use(express.json());

app.all('/', async (req, res) => {
  try {
    const catalystApp = catalyst.initialize(req);
    
    // In Catalyst Advanced I/O, the logged-in user is available in req.user
    // If not, we can resolve it using the auth component
    const user = req.user || (catalystApp.auth && await catalystApp.auth().getCurrentUser(req));
    
    if (!user || !user.user_id) {
      return res.status(401).json({ role: null, error: 'User session not found' });
    }

    const zuid = user.user_id;

    // Query DataStore UserRoles table
    const query = `SELECT Role FROM UserRoles WHERE ZUID = '${zuid}'`;
    const zcqlResult = await catalystApp.zcql().executeZCQLQuery(query);

    if (zcqlResult && zcResultLength(zcqlResult) > 0) {
      // ZCQL returns array of row objects e.g., [{ UserRoles: { Role: 'Admin', ZUID: '...' } }]
      const role = zcqlResult[0].UserRoles.Role;
      return res.status(200).json({ role });
    } else {
      // Fallback role if user has no role defined in DataStore table
      return res.status(200).json({ role: 'Investigator' });
    }
  } catch (err) {
    console.error('[get_user_role] Function execution failed:', err);
    return res.status(500).json({ role: 'Investigator', error: err.message });
  }
});

function zcResultLength(result) {
  return Array.isArray(result) ? result.length : 0;
}

module.exports = app;
