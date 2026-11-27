'use strict';

var fs = require('fs');

function loadOrders(file, callback) {
  fs.readFile(file, 'utf8', function (err, text) {
    if (err) {
      return callback(err);
    }
    var orders;
    try {
      orders = JSON.parse(text);
    } catch (e) {
      return callback(new Error('Invalid orders file ' + file + ': ' + e.message));
    }
    callback(null, orders);
  });
}

function groupByCustomer(orders) {
  return orders.reduce(function (groups, order) {
    if (!groups.hasOwnProperty(order.customer)) {
      groups[order.customer] = [];
    }
    groups[order.customer].push(order);
    return groups;
  }, {});
}

function newestFirst(orders) {
  var copy = orders.slice();
  copy.sort(function (a, b) {
    return a.placedAt < b.placedAt ? 1 : a.placedAt > b.placedAt ? -1 : 0;
  });
  return copy;
}

function withDiscount(order, percent) {
  var copy = JSON.parse(JSON.stringify(order));
  for (var i = 0; i < copy.lines.length; i++) {
    copy.lines[i].priceCents = Math.round((copy.lines[i].priceCents * (100 - percent)) / 100);
  }
  return copy;
}

function orderTotal(order) {
  var total = 0;
  for (var i = 0; i < order.lines.length; i++) {
    total += order.lines[i].priceCents * order.lines[i].qty;
  }
  return total;
}

module.exports = {
  loadOrders: loadOrders,
  groupByCustomer: groupByCustomer,
  newestFirst: newestFirst,
  withDiscount: withDiscount,
  orderTotal: orderTotal,
};
