'use strict';

var path = require('path');
var orders = require('./orders');

var file = process.argv[2] || path.join(__dirname, '..', 'data', 'orders.json');

orders.loadOrders(file, function (err, list) {
  if (err) {
    console.error('Cannot build report: ' + err.message);
    process.exit(1);
  }
  var groups = orders.groupByCustomer(list);
  var customers = Object.keys(groups).sort();
  for (var i = 0; i < customers.length; i++) {
    var customerOrders = groups[customers[i]];
    var total = 0;
    customerOrders.forEach(function (order) {
      total += orders.orderTotal(order);
    });
    console.log(customers[i] + ': ' + (total / 100).toFixed(2) + ' EUR (' + customerOrders.length + ' orders)');
  }
});
