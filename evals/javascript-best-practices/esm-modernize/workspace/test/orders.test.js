'use strict';

var test = require('node:test');
var assert = require('assert');
var path = require('path');
var orders = require('../src/orders');

test('loadOrders reads the sample file', function (t, done) {
  orders.loadOrders(path.join(__dirname, '..', 'data', 'orders.json'), function (err, list) {
    assert.ifError(err);
    assert.strictEqual(list.length, 5);
    done();
  });
});

test('orderTotal sums the lines in cents', function () {
  var order = { lines: [{ priceCents: 1250, qty: 2 }, { priceCents: 99, qty: 1 }] };
  assert.strictEqual(orders.orderTotal(order), 2599);
});

test('groupByCustomer groups orders per customer', function () {
  var groups = orders.groupByCustomer([
    { id: 1, customer: 'a@example.com' },
    { id: 2, customer: 'b@example.com' },
    { id: 3, customer: 'a@example.com' },
  ]);
  assert.strictEqual(groups['a@example.com'].length, 2);
  assert.strictEqual(groups['b@example.com'].length, 1);
});
