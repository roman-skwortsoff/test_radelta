db = db.getSiblingDB("app_logs");

db.createUser({
  user: "usermongodb",
  pwd: "11012017",
  roles: [
    {
      role: "readWrite",
      db: "app_logs"
    }
  ]
});